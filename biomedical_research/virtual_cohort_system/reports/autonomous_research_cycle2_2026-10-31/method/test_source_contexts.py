"""Metadata-only tests; no submitted program is imported or generated table made."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from cohort_harness import execution
from cohort_harness.contracts import ContractError
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate
import prepare_artificial_source_contexts as fixture
import run_source_contexts as bridge


@pytest.fixture
def tmp_path(tmp_path_factory, request):
    # Keep retained fixtures within method/ without exceeding legacy Windows
    # MAX_PATH when the bridge nests a second frozen candidate.
    destination = tmp_path_factory.getbasetemp() / hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:6]
    destination.mkdir()
    return destination


def rewrite(path, mutate):
    value = read_json(path)
    mutate(value)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def parent(tmp_path, mutate=None):
    root = fixture.prepare(tmp_path / "parent", freeze=False)
    if mutate:
        mutate(root, root / "candidates/initial")
    freeze_candidate(root, "candidates/initial")
    return root


def prepared(tmp_path):
    root = parent(tmp_path)
    destination = tmp_path / "bridge"
    result = bridge.prepare_source_contexts(root, "initial", destination, 19)
    return root, destination, result


def test_preparation_preserves_all_science_and_no_tables(tmp_path):
    root = parent(tmp_path)
    original = bridge._inventory(root)
    destination = tmp_path / "bridge"
    result = bridge.prepare_source_contexts(root, "initial", destination, 19)
    original_spec = read_json(root / "candidates/initial/model_spec.json")
    for record in result["contexts"]:
        child_root = destination / record["bundle"]
        child_spec = read_json(child_root / "candidates/source/model_spec.json")
        assert child_spec["parameters"]["active_context"] == record["id"]
        child_spec["parameters"]["active_context"] = original_spec["parameters"]["active_context"]
        assert bridge._canonical(child_spec) == bridge._canonical(original_spec)
        descriptor = original_spec["parameters"]["contexts"][record["id"]]
        task = read_json(child_root / "task.json")
        assert task["n_rows"] == descriptor["n_rows"]
        assert task["columns"][1]["minimum"] > 2  # source support is outside target support
        assert task["population"] == descriptor["population"]
        verify_candidate(child_root, "candidates/source")
    assert bridge._inventory(root) == original
    assert not list(tmp_path.rglob("*.csv"))
    assert bridge.verify_preparation(root, destination, candidate="initial") == result


@pytest.mark.parametrize("relative,mutation", [
    ("model_spec.json", lambda x: x["parameters"].update(active_context="unknown")),
    ("model_spec.json", lambda x: x["parameters"]["contexts"].update(SOURCE_A=copy.deepcopy(x["parameters"]["contexts"]["source_a"]))),
    ("model_spec.json", lambda x: x["parameters"]["contexts"]["target_design"].update(n_rows=4)),
    ("model_spec.json", lambda x: x["parameters"]["contexts"]["source_a"].update(n_rows=0)),
    ("model_spec.json", lambda x: x["parameters"]["contexts"]["source_a"].update(inputs=[])),
    ("model_spec.json", lambda x: x["parameters"]["contexts"]["source_a"]["columns"][1].update(maximum=31)),
    ("model_spec.json", lambda x: x["parameters"]["contexts"]["source_a"]["columns"][1].pop("maximum")),
    ("model_spec.json", lambda x: x["parameters"]["contexts"]["source_a"]["columns"][1].update(unit="changed")),
    ("source_context_plan.json", lambda x: x.update(schema_version=True)),
    ("source_context_plan.json", lambda x: x["contexts"][0].update(id="target_design")),
    ("source_context_plan.json", lambda x: x["contexts"].append(copy.deepcopy(x["contexts"][0]))),
    ("source_context_plan.json", lambda x: x["contexts"][0].update(task_path="../task.json")),
    ("source_context_plan.json", lambda x: x["model_domain"].update(assumption_ids=["unknown"])),
    ("source_context_plan.json", lambda x: x["model_domain"]["columns"][1].update(unit="changed")),
    ("source_contexts/source_a/task.json", lambda x: x.update(n_rows=5)),
    ("source_contexts/source_a/task.json", lambda x: x.update(task_id="unapproved")),
    ("source_contexts/source_a/task.json", lambda x: x["information_policy"].update(excluded_cohorts=[])),
    ("source_contexts/source_a/whole_cohort_feedback.json", lambda x: x.update(population="wrong")),
    ("source_contexts/source_a/whole_cohort_feedback.json", lambda x: x.update(assumption_ids=[])),
    ("source_contexts/source_a/whole_cohort_feedback.json", lambda x: x["checks"][0]["operator"].update(column="absent")),
    ("source_contexts/source_a/whole_cohort_feedback.json", lambda x: x["checks"][0]["operator"].update(unapproved=True)),
    ("source_contexts/source_a/whole_cohort_feedback.json", lambda x: x["checks"].append(copy.deepcopy(x["checks"][0]))),
])
def test_invalid_plan_rejected_before_preparation(tmp_path, relative, mutation):
    root = parent(tmp_path, lambda root, candidate: rewrite(candidate / relative, mutation))
    with pytest.raises((ValueError, KeyError, TypeError)):
        bridge.prepare_source_contexts(root, "initial", tmp_path / "rejected", 19)
    assert not (tmp_path / "rejected").exists()
    assert not list(tmp_path.rglob("*.csv"))


@pytest.mark.parametrize("relative", ["model_spec.json", "generator.py", "source_context_plan.json", "evidence.json"])
def test_changed_parent_fails(tmp_path, relative):
    root, destination, _ = prepared(tmp_path)
    with (root / "candidates/initial" / relative).open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValueError):
        bridge.verify_preparation(root, destination)


@pytest.mark.parametrize("relative", ["candidates/source/model_spec.json", "candidates/source/generator.py", "task.json", "registry.json", "sources/artificial_aggregates.txt"])
def test_changed_child_fails(tmp_path, relative):
    root, destination, _ = prepared(tmp_path)
    with (destination / "contexts/source_a/bundle" / relative).open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValueError):
        bridge.verify_preparation(root, destination)


def test_refreezing_cannot_hide_shared_science_change(tmp_path):
    root, destination, _ = prepared(tmp_path)
    child_root = destination / "contexts/source_a/bundle"
    child = child_root / "candidates/source"
    (child / "freeze.json").rename(destination / "retained_original_child_freeze.json")
    rewrite(child / "model_spec.json", lambda x: x["parameters"].update(step=2))
    freeze_candidate(child_root, child)
    with pytest.raises(ValueError, match="differs beyond active_context"):
        bridge.verify_preparation(root, destination)


def test_extra_artifact_and_reused_destination_rejected(tmp_path):
    root, destination, _ = prepared(tmp_path)
    with pytest.raises(ValueError, match="already exists"):
        bridge.prepare_source_contexts(root, "initial", destination, 19)
    (destination / "unapproved.txt").write_text("extra", encoding="utf-8")
    with pytest.raises(ValueError):
        bridge.verify_preparation(root, destination)


def test_undeclared_context_runtime_artifact_rejected(tmp_path):
    root, destination, _ = prepared(tmp_path)
    extra = destination / "contexts/extra/bundle/executions/unapproved/file.txt"
    extra.parent.mkdir(parents=True)
    extra.write_text("not a permitted dynamic artifact", encoding="utf-8")
    with pytest.raises(ValueError, match="context directory"):
        bridge.verify_preparation(root, destination)


def test_selector_numeric_type_identity_is_strict():
    assert bridge._digest({"value": True}) != bridge._digest({"value": 1})
    assert bridge._digest({"value": 1.0}) != bridge._digest({"value": 1})


def test_added_observed_table_is_rejected_without_reading_it(tmp_path):
    root, destination, _ = prepared(tmp_path)
    # Empty sentinel, not an individual table.
    (destination / "contexts/source_a/bundle/observed.csv").touch()
    with pytest.raises(ValueError, match="observed.csv"):
        bridge.verify_preparation(root, destination)


def test_candidate_table_artifact_rejected(tmp_path):
    root = parent(tmp_path, lambda root, candidate: (candidate / "source_covariates.csv").touch())
    with pytest.raises(ValueError, match="individual-table"):
        bridge.prepare_source_contexts(root, "initial", tmp_path / "bridge", 19)


def test_failed_runtime_retained_without_generation_or_fallback(tmp_path, monkeypatch):
    root, destination, _ = prepared(tmp_path)
    calls = []
    def unavailable(runtime):
        calls.append(runtime)
        raise ContractError("Invented runtime unavailable: no local execution fallback")
    def forbidden(*args, **kwargs):
        pytest.fail("Execution backend must not be invoked after runtime inspection failure")
    monkeypatch.setattr(execution, "_runtime_manifest", unavailable)
    monkeypatch.setattr(execution, "_capture", forbidden)
    result = bridge.execute_source_contexts(root, destination)
    assert len(calls) == 2
    assert result["status"] == "failed"
    assert all(not r["generation_link_verified"] and r["feedback"] is None for r in result["contexts"])
    assert all(not p.read_bytes() for p in destination.rglob("generated.csv"))
    assert bridge.verify_source_contexts(root, destination) == result
    with pytest.raises(ValueError, match="already exists"):
        bridge.execute_source_contexts(root, destination)
    rewrite(destination / "report.json", lambda x: x.update(status="success"))
    with pytest.raises(ValueError, match="report"):
        bridge.verify_source_contexts(root, destination)


def test_runtime_configuration_cannot_enable_host_execution(tmp_path):
    root = parent(tmp_path)
    with pytest.raises(ValueError, match="Only the inspected"):
        bridge.prepare_source_contexts(root, "initial", tmp_path / "bridge", 19, runtime={**execution.DEFAULT_RUNTIME, "backend": "local"})
    assert not (tmp_path / "bridge").exists()


def test_output_cannot_modify_frozen_candidate(tmp_path):
    root = parent(tmp_path)
    with pytest.raises(ValueError, match="inside frozen"):
        bridge.prepare_source_contexts(root, "initial", root / "candidates/initial/output", 19)


def test_unknown_expected_candidate_rejected(tmp_path):
    root, destination, _ = prepared(tmp_path)
    with pytest.raises(ValueError):
        bridge.verify_preparation(root, destination, candidate="other")


def test_statistic_not_computable_remains_declared(tmp_path):
    def mutate(root, candidate):
        rewrite(candidate / "source_contexts/source_a/whole_cohort_feedback.json",
                lambda x: x["checks"][0].update(status="not_computable", operator=None, reason="Deliberately unsupported artificial statistic"))
    root = parent(tmp_path, mutate)
    result = bridge.prepare_source_contexts(root, "initial", tmp_path / "bridge", 19)
    assert result["status"] == "prepared"
    assert not list(tmp_path.rglob("*.csv"))
