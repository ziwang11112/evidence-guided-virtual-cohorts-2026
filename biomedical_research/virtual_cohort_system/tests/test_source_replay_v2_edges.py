"""Invented adapter edge cases; mocked backends never execute candidate code."""
from __future__ import annotations

import copy

import pytest

from cohort_harness import execution, source_replay_v2 as replay
from cohort_harness.contracts import ContractError
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate
from examples.m12_source_domain import build_fixture, write
from test_source_replay import fake_backend


def test_output_bound_failure(tmp_path, monkeypatch):
    def edit(plan, source, task):
        # Input support is valid, but the mocked generator's final y=21 exceeds
        # this source output bound while remaining inside the model domain.
        plan["contexts"][0]["columns"][2]["maximum"] = 20

    root, candidate = build_fixture(tmp_path / "bundle", edit=edit)
    parent_hash = sha256(candidate / "freeze.json")
    fake_backend(monkeypatch)
    report = replay.run_source_replay(root, candidate, "bounds", 23)
    context = report["contexts"][0]
    child = root / "source_replays_v2/bounds" / context["child_bundle"]
    receipt = execution.verify_execution(child, "replay")

    assert report["status"] == context["status"] == receipt["status"] == "failed"
    assert receipt["generator_executed"] is True
    assert "above maximum in y" in receipt["error"]["message"]
    assert context["generation_link_verified"] is False
    assert context["checks"] == []
    assert "generated_sha256" not in context
    output = child / "executions/replay/output/generated.csv"
    assert execution.read_table(output, read_json(child / "task.json"), output=True).y.max() == 21
    assert sha256(candidate / "freeze.json") == parent_hash
    assert replay.verify_source_replay(root, "bounds") == report


def test_unavailable_runtime(tmp_path, monkeypatch):
    root, candidate = build_fixture(tmp_path / "bundle")

    def unavailable(runtime):
        raise ContractError("Invented unavailable runtime; no local execution fallback")

    def forbidden_capture(*args, **kwargs):
        pytest.fail("Unavailable runtime must not launch any candidate process")

    monkeypatch.setattr(execution, "_runtime_manifest", unavailable)
    monkeypatch.setattr(execution, "_capture", forbidden_capture)
    report = replay.run_source_replay(root, candidate, "unavailable", 23)
    context = report["contexts"][0]
    child = root / "source_replays_v2/unavailable" / context["child_bundle"]
    receipt = execution.verify_execution(child, "replay")

    assert report["status"] == context["status"] == receipt["status"] == "failed"
    assert receipt["generator_executed"] is False
    assert receipt["process"] is None
    assert "unavailable runtime" in receipt["error"]["message"]
    assert context["generation_link_verified"] is False
    assert context["checks"] == []
    assert not (child / "executions/replay/launch.json").exists()
    assert not (child / "executions/replay/output/generated.csv").exists()
    assert replay.verify_source_replay(root, "unavailable") == report


@pytest.mark.parametrize("invalid", ["operator", "support"])
def test_invalid_second_context(tmp_path, monkeypatch, invalid):
    def edit(plan, source, task):
        second = copy.deepcopy(plan["contexts"][0])
        second["id"] = "second"
        if invalid == "operator":
            second["checks"][0]["operator"]["missing_policy"] = "guess"
        else:
            second["columns"][1]["maximum"] = 13
        plan["contexts"].append(second)

    root, candidate = build_fixture(tmp_path / "bundle", edit=edit)
    calls = []

    def forbidden_execution(*args, **kwargs):
        calls.append((args, kwargs))
        pytest.fail("Every context must validate before the first execution")

    monkeypatch.setattr(execution, "run_candidate", forbidden_execution)
    with pytest.raises(ValueError, match="missing policy|outside the model domain"):
        replay.run_source_replay(root, candidate, "invalid", 23)
    assert calls == []
    assert not (root / "source_replays_v2/invalid").exists()


def test_casefold_context_collision(tmp_path, monkeypatch):
    def edit(plan, source, task):
        second = copy.deepcopy(plan["contexts"][0])
        second["id"] = second["id"].upper()
        plan["contexts"].append(second)

    root, candidate = build_fixture(tmp_path / "bundle", edit=edit)
    calls = []

    def forbidden_execution(*args, **kwargs):
        calls.append((args, kwargs))
        pytest.fail("Context directories must not collide on Windows")

    monkeypatch.setattr(execution, "run_candidate", forbidden_execution)
    with pytest.raises(ValueError, match="Duplicate source context"):
        replay.run_source_replay(root, candidate, "collision", 23)
    assert calls == []
    assert not (root / "source_replays_v2/collision").exists()


@pytest.mark.parametrize("where", ["selection", "event"])
def test_filter_type_preflight(tmp_path, monkeypatch, where):
    def edit(plan, source, task):
        check = plan["contexts"][0]["checks"][0]
        incompatible = {"column": "sample_id", "op": "lt", "value": 1}
        if where == "selection":
            check["operator"]["selection"] = [incompatible]
        else:
            evidence_path = source.parent / "evidence.json"
            evidence = read_json(evidence_path)
            item = copy.deepcopy(evidence["items"][0])
            item.update(id="event_type", kind="proportion", variables=["sample_id"],
                        adjustment=[], unit="1", estimate=0.5)
            evidence["items"].append(item)
            write(evidence_path, evidence)
            check["evidence_id"] = "event_type"
            check["operator"] = {"kind": "proportion", "unit": "1", "selection": [],
                                 "missing_policy": "error", "event": incompatible}

    root, candidate = build_fixture(tmp_path / "bundle", edit=edit)

    def forbidden_execution(*args, **kwargs):
        pytest.fail("String-versus-number ordering must be rejected before execution")

    monkeypatch.setattr(execution, "run_candidate", forbidden_execution)
    with pytest.raises((ValueError, TypeError)):
        replay.run_source_replay(root, candidate, "filter_type", 23)
    assert not (root / "source_replays_v2/filter_type").exists()


@pytest.mark.parametrize("changed", ["generator.py", "model_spec.json"])
def test_refrozen_child_identity(tmp_path, monkeypatch, changed):
    root, candidate = build_fixture(tmp_path / "bundle")
    original_make_child = replay.legacy._make_child
    parent_hash = sha256(candidate / "freeze.json")

    def change_and_refreeze(*args):
        original_make_child(*args)
        child = args[-1]
        copied = child / "candidates/source"
        if changed == "generator.py":
            program = (copied / changed).read_text(encoding="utf-8")
            assert "p['intercept'] +" in program
            (copied / changed).write_text(program.replace("p['intercept'] +", "2 * p['intercept'] +"),
                                         encoding="utf-8")
        else:
            spec = read_json(copied / changed)
            spec["parameters"]["intercept"] = 2
            write(copied / changed, spec)
        (copied / "freeze.json").unlink()  # Only this newly constructed synthetic child.
        freeze_candidate(child, copied)
        verify_candidate(child, copied)

    monkeypatch.setattr(replay.legacy, "_make_child", change_and_refreeze)
    fake_backend(monkeypatch)
    with pytest.raises(ValueError, match="differ from parent"):
        replay.run_source_replay(root, candidate, "identity", 23)

    replay_dir = root / "source_replays_v2/identity"
    child = replay_dir / "contexts/wider_source/bundle"
    assert sha256(child / "candidates/source" / changed) != sha256(candidate / changed)
    assert execution.verify_execution(child, "replay")["status"] == "success"
    assert (replay_dir / "intent.json").is_file()
    assert not (replay_dir / "replay.json").exists()
    assert sha256(candidate / "freeze.json") == parent_hash
    verify_candidate(root, candidate)
