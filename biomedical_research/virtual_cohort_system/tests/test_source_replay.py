"""Invented data and mocked execution: these tests do not establish isolation."""
from __future__ import annotations

import copy
import json
import shutil

import pandas as pd
import pytest

from cohort_harness import execution, source_replay as replay
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate


PROGRAM = """def generate(observed, spec, seed):
    out = observed.copy()
    p = spec['parameters']
    out['y'] = p['intercept'] + p['slope'] * out['x']
    return out
"""


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def bundle(tmp_path, *, edit=None, direct=False):
    root = make_demo(tmp_path / "bundle")
    candidate = root / "candidates/initial"
    if not direct:
        (candidate / "generated.csv").unlink()
        (candidate / "generator.py").write_text(PROGRAM)
    source = candidate / "source_covariates.csv"
    pd.DataFrame({"sample_id": ["source_0", "source_1", "source_2", "source_3"],
                  "x": [0, 0, 3, 5]}).to_csv(source, index=False)
    checks = read_json(candidate / "source_checks.json")["checks"]
    checks = [{k: v for k, v in check.items() if k != "table"} for check in checks]
    plan = {"schema_version": 1, "contexts": [{
        "id": "declared", "population": "Four invented source-context rows",
        "reason": "Operator and execution linkage test only", "assumption_ids": ["A1"],
        "measurement": {"mode": "identity", "description": "Same invented x and y units"},
        "input": {"path": source.name, "sha256": sha256(source), "origin": "declared_source_covariates"},
        "checks": [{**check, "status": "approximate"} for check in checks],
    }]}
    if edit:
        edit(plan, source)
    write(candidate / "source_replay.json", plan)
    freeze_candidate(root, candidate)
    return root, candidate


def fake_backend(monkeypatch, *, returncode=0):
    monkeypatch.setattr(execution, "_runtime_manifest", lambda _: {"mocked": True})
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        task = read_json(cwd / "input/task.json")
        observed = execution.read_table(cwd / "input/observed.csv", task)
        spec = read_json(cwd / "input/model_spec.json")["parameters"]
        observed.assign(y=spec["intercept"] + spec["slope"] * observed.x).to_csv(
            cwd / "output/generated.csv", index=False)
        write(cwd / "output/worker_report.json", {"status": "completed" if returncode == 0 else "failed",
                                                  "generator_started": True})
        stdout_path.write_text("Mocked execution; not an isolation test")
        stderr_path.write_text("")
        return {"returncode": returncode, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(execution, "_capture", capture)


def test_replay_uses_same_spec_generator_and_only_declared_context(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    before = {p.name: sha256(p) for p in (root / "task.json", candidate / "freeze.json", candidate / "model_spec.json")}
    fake_backend(monkeypatch)
    report = replay.run_source_replay(root, candidate, "one", 17)
    assert report["status"] == "success"
    context = report["contexts"][0]
    assert context["generation_link_verified"] is True
    assert context["checks"][0]["value"] == 5
    assert context["checks"][0]["difference"] == -2  # A discrepancy is diagnostic, not execution failure.
    assert context["checks"][1]["value"] == pytest.approx(2)
    child = root / "source_replays/one" / context["child_bundle"]
    assert read_json(child / "task.json")["n_rows"] == 4
    assert read_json(child / "task.json")["budget"] == read_json(root / "task.json")["budget"]
    assert read_json(child / "task.json")["information_policy"] == read_json(root / "task.json")["information_policy"]
    assert sha256(child / "candidates/source/generator.py") == sha256(candidate / "generator.py")
    assert sha256(child / "candidates/source/model_spec.json") == sha256(candidate / "model_spec.json")
    assert before == {p.name: sha256(p) for p in (root / "task.json", candidate / "freeze.json", candidate / "model_spec.json")}
    assert replay.verify_source_replay(root, "one", candidate=candidate) == report
    verify_candidate(root, candidate)


def test_all_implemented_numeric_statistics_reuse_execution_output(tmp_path, monkeypatch):
    def edit(plan, source):
        context = plan["contexts"][0]
        for kind in ("sd", "correlation"):
            original = copy.deepcopy(context["checks"][0])
            original.update(id=kind, evidence_id=kind)
            original["operator"].update(kind=kind)
            if kind == "correlation":
                original["operator"].pop("column")
                original["operator"].update(x="x", y="y", unit="1")
            context["checks"].append(original)
        evidence_path = source.parent / "evidence.json"
        evidence = read_json(evidence_path)
        base = evidence["items"][0]
        evidence["items"].extend([{**base, "id": "sd", "kind": "sd", "estimate": 1},
                                  {**base, "id": "correlation", "kind": "correlation", "variables": ["x", "y"],
                                   "unit": "1", "estimate": 1}])
        write(evidence_path, evidence)
    root, candidate = bundle(tmp_path, edit=edit)
    fake_backend(monkeypatch)
    result = replay.run_source_replay(root, candidate, "statistics", 2)
    checks = result["contexts"][0]["checks"]
    assert checks[2]["value"] == pytest.approx(pd.Series([1, 1, 7, 11]).std())
    assert checks[3]["value"] == pytest.approx(1)
    assert len({check["generated_sha256"] for check in checks}) == 1


@pytest.mark.parametrize("mutation", ["outcome", "path", "hash", "assumption", "computed_bridge", "mapping"])
def test_invalid_declared_context_rejected_before_execution(tmp_path, monkeypatch, mutation):
    def edit(plan, source):
        context = plan["contexts"][0]
        if mutation == "outcome":
            frame = pd.read_csv(source).assign(y=99)
            frame.to_csv(source, index=False)
            context["input"]["sha256"] = sha256(source)
        elif mutation == "path":
            context["input"]["path"] = "../../observed.csv"
        elif mutation == "hash":
            context["input"]["sha256"] = "0" * 64
        elif mutation == "assumption":
            context["assumption_ids"] = ["not_recorded"]
        elif mutation == "computed_bridge":
            context["checks"][0]["status"] = "computed"
        else:
            context["measurement"]["mode"] = "automatic_conversion"
    root, candidate = bundle(tmp_path, edit=edit)
    monkeypatch.setattr(execution, "run_candidate", lambda *a, **kw: pytest.fail("must not execute invalid context"))
    with pytest.raises(ValueError):
        replay.run_source_replay(root, candidate, "invalid", 3)
    assert not (root / "source_replays/invalid").exists()


def test_direct_table_cannot_claim_replay(tmp_path):
    root, candidate = bundle(tmp_path, direct=True)
    with pytest.raises(ValueError, match="frozen generator"):
        replay.run_source_replay(root, candidate, "direct", 1)


def test_failed_execution_has_no_verified_feedback(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch, returncode=1)
    report = replay.run_source_replay(root, candidate, "failed", 1)
    assert report["status"] == "failed"
    assert report["contexts"][0]["generation_link_verified"] is False
    assert report["contexts"][0]["checks"] == []
    assert replay.verify_source_replay(root, "failed") == report


@pytest.mark.parametrize("artifact", ["output/generated.csv", "input/model_spec.json", "input/observed.csv"])
def test_changed_execution_artifacts_rejected(tmp_path, monkeypatch, artifact):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch)
    replay.run_source_replay(root, candidate, "tamper", 4)
    path = root / "source_replays/tamper/contexts/declared/bundle/executions/replay" / artifact
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="hash changed"):
        replay.verify_source_replay(root, "tamper")


def test_wrong_candidate_cannot_reuse_linked_feedback(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    other = root / "candidates/other"
    shutil.copytree(candidate, other)
    (other / "freeze.json").unlink()
    freeze_candidate(root, other)
    fake_backend(monkeypatch)
    replay.run_source_replay(root, candidate, "one", 1)
    with pytest.raises(ValueError, match="wrong candidate"):
        replay.verify_source_replay(root, "one", candidate=other)


def test_recomputed_feedback_rejects_changed_numbers(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch)
    result = replay.run_source_replay(root, candidate, "one", 1)
    result["contexts"][0]["checks"][0]["value"] = 100
    write(root / "source_replays/one/replay.json", result)
    with pytest.raises(ValueError, match="recomputed"):
        replay.verify_source_replay(root, "one")


def test_changed_child_model_cannot_pass_even_with_valid_child_freeze(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch)
    original = replay._make_child
    def altered(*args):
        original(*args)
        child = args[-1]
        child_candidate = child / "candidates/source"
        spec = read_json(child_candidate / "model_spec.json")
        spec["parameters"]["slope"] = 99
        write(child_candidate / "model_spec.json", spec)
        (child_candidate / "freeze.json").unlink()
        freeze_candidate(child, child_candidate)
    monkeypatch.setattr(replay, "_make_child", altered)
    with pytest.raises(ValueError, match="differ from parent"):
        replay.run_source_replay(root, candidate, "wrong_model", 1)
    assert not (root / "source_replays/wrong_model/replay.json").exists()


def test_replay_id_is_append_only_and_does_not_traverse(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    fake_backend(monkeypatch)
    replay.run_source_replay(root, candidate, "one", 1)
    for name in ("one", "../escape", "x/y"):
        with pytest.raises(ValueError):
            replay.run_source_replay(root, candidate, name, 1)


def test_registry_appends_do_not_change_original_replay_snapshot(tmp_path, monkeypatch):
    root, candidate = bundle(tmp_path)
    artifact = root / "sources/later.txt"
    artifact.write_text("Later approved invented source")
    registry = read_json(root / "registry.json")
    registry["artifacts"].append({"source_id": "later", "path": "sources/later.txt", "sha256": sha256(artifact),
                                  "origin": "fixture", "screening": "approved"})
    write(root / "registry.json", registry)
    fake_backend(monkeypatch)
    result = replay.run_source_replay(root, candidate, "snapshot", 1)
    child = root / "source_replays/snapshot" / result["contexts"][0]["child_bundle"]
    assert len(read_json(child / "registry.json")["artifacts"]) == 1
    assert not (child / "sources/later.txt").exists()
