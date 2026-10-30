"""Invented fixtures; fake backend tests do not establish actual isolation."""
import copy

import pytest

from cohort_harness import execution, source_replay_v2 as replay
from cohort_harness.lifecycle import read_json, sha256, verify_candidate
from examples.m12_source_domain import build_fixture, write
from test_source_replay import fake_backend


def test_independent_source_runs_unchanged_generator_and_verifies(tmp_path, monkeypatch):
    root, candidate = build_fixture(tmp_path / "bundle")
    target_hash = sha256(root / "task.json")
    parent_hash = sha256(candidate / "freeze.json")
    fake_backend(monkeypatch)
    report = replay.run_source_replay(root, candidate, "one", 17)
    assert report["status"] == "success"
    assert [c["value"] for c in report["contexts"][0]["checks"]] == pytest.approx([18, 2])
    child = root / "source_replays_v2/one/contexts/wider_source/bundle"
    source_task = read_json(child / "task.json")
    assert source_task["columns"][1]["maximum"] == 10
    assert source_task["columns"][2]["maximum"] == 30
    assert read_json(root / "task.json")["columns"][1]["maximum"] == 6
    assert sha256(root / "task.json") == target_hash
    assert sha256(candidate / "freeze.json") == parent_hash
    for name in ("generator.py", "model_spec.json"):
        assert sha256(candidate / name) == sha256(child / "candidates/source" / name)
    assert replay.verify_source_replay(root, "one", candidate=candidate) == report
    verify_candidate(root, candidate)


@pytest.mark.parametrize("mutation", ["outcome", "outside_model", "unit", "measurement", "assumption", "field",
                                     "missing_policy", "selection", "term"])
def test_invalid_context_rejected_before_execution(tmp_path, monkeypatch, mutation):
    def edit(plan, source, task):
        context = plan["contexts"][0]
        if mutation == "outcome":
            source.write_text("sample_id,x,y\ns,9,19\n")
            context["input"]["sha256"] = sha256(source)
        elif mutation == "outside_model":
            context["columns"][1]["maximum"] = 13
        elif mutation == "unit":
            context["columns"][1]["unit"] = "different_unit"
        elif mutation == "measurement":
            context["measurement"]["mode"] = "guessed_conversion"
        elif mutation == "assumption":
            plan["model_domain"]["assumption_ids"] = ["unknown"]
        elif mutation == "field":
            context["silently_ignored"] = True
        elif mutation == "missing_policy":
            context["checks"][0]["operator"]["missing_policy"] = "guess"
        elif mutation == "selection":
            context["checks"][0]["operator"]["selection"] = [{"column": "unknown", "op": "eq", "value": 1}]
        else:
            context["checks"][1]["operator"]["term"] = "unknown"
    root, candidate = build_fixture(tmp_path / "bundle", edit=edit)
    monkeypatch.setattr(execution, "run_candidate", lambda *a, **kw: pytest.fail("must reject before execution"))
    with pytest.raises(ValueError):
        replay.run_source_replay(root, candidate, "bad", 1)
    assert not (root / "source_replays_v2/bad").exists()


def test_failed_execution_preserved_without_verified_checks(tmp_path, monkeypatch):
    root, candidate = build_fixture(tmp_path / "bundle")
    fake_backend(monkeypatch, returncode=1)
    report = replay.run_source_replay(root, candidate, "failed", 1)
    assert report["status"] == "failed"
    assert report["contexts"][0]["generation_link_verified"] is False
    assert report["contexts"][0]["checks"] == []
    assert replay.verify_source_replay(root, "failed") == report


@pytest.mark.parametrize("path", ["task.json", "executions/replay/output/generated.csv",
                                 "executions/replay/input/model_spec.json"])
def test_child_artifact_tampering_is_rejected(tmp_path, monkeypatch, path):
    root, candidate = build_fixture(tmp_path / "bundle")
    fake_backend(monkeypatch)
    replay.run_source_replay(root, candidate, "one", 1)
    artifact = root / "source_replays_v2/one/contexts/wider_source/bundle" / path
    artifact.write_bytes(artifact.read_bytes() + b"\n")
    with pytest.raises(ValueError):
        replay.verify_source_replay(root, "one")


def test_recomputed_feedback_and_engine_identity_checked(tmp_path, monkeypatch):
    root, candidate = build_fixture(tmp_path / "bundle")
    fake_backend(monkeypatch)
    report = replay.run_source_replay(root, candidate, "one", 1)
    path = root / "source_replays_v2/one/replay.json"
    changed = copy.deepcopy(report)
    changed["contexts"][0]["checks"][0]["value"] = 999
    write(path, changed)
    with pytest.raises(ValueError, match="Feedback"):
        replay.verify_source_replay(root, "one")
    changed = copy.deepcopy(report)
    changed["engines"]["source_replay_v2"] = "0" * 64
    write(path, changed)
    with pytest.raises(ValueError, match="engine"):
        replay.verify_source_replay(root, "one")


def test_source_csv_uses_source_category_types(tmp_path):
    import pandas as pd
    source = tmp_path / "covariates.csv"
    source.write_text("id,group\ns0,2\ns1,2\n")
    target = {"schema_version": 1, "task_id": "category-fixture", "mode": "enrichment",
        "population": "invented target", "row_id": "id", "n_rows": 2,
        "columns": [{"name": "id", "kind": "string", "role": "identifier", "unit": "id", "nullable": False},
                    {"name": "group", "kind": "category", "role": "observed", "unit": "code", "nullable": False,
                     "categories": [1]},
                    {"name": "y", "kind": "number", "role": "generated", "unit": "y", "nullable": False}],
        "information_policy": {"mode": "prior_only", "excluded_cohorts": [], "allowed_tools": []},
        "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    columns = copy.deepcopy(target["columns"])
    columns[1]["categories"] = ["2"]
    context = {"population": "invented source", "columns": columns,
        "input": {"path": source.name, "sha256": sha256(source)}}
    _, frame = replay._source_frame(tmp_path, context, target, 10000)
    assert frame.group.tolist() == ["2", "2"]
    assert pd.api.types.is_string_dtype(frame.group)
