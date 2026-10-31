"""Artificial metadata + mocked bridge only: no program or cohort execution."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

import run_source_calibration as adapter
from cohort_harness import calibration_budget as budget, execution, lifecycle
from cohort_harness.lifecycle import read_json


@pytest.fixture
def tmp_path(tmp_path_factory, request):
    path = tmp_path_factory.getbasetemp() / hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:6]
    path.mkdir()
    return path


def rewrite(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


@pytest.fixture
def case(tmp_path):
    # The old metadata-only artificial builder is trusted engineering code. It
    # writes inert program text; its program is replaced with an import sentinel.
    path = adapter.BRIDGE_PATH.with_name("prepare_artificial_source_contexts.py")
    loader = importlib.util.spec_from_file_location("artificial_metadata_fixture", path)
    fixture = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(fixture)
    root = fixture.prepare(tmp_path / "b", freeze=False)
    candidate = root / "candidates/initial"
    spec = read_json(candidate / "model_spec.json")
    for context in spec["parameters"]["contexts"].values():
        context["n_rows"] = 6000
    task = read_json(root / "task.json")
    task["n_rows"] = 6000
    rewrite(root / "task.json", task)
    rewrite(candidate / "model_spec.json", spec)
    constraints, weights = [], []
    for identifier in ("source_a", "source_b"):
        folder = candidate / "source_contexts" / identifier
        task = read_json(folder / "task.json")
        task["n_rows"] = 6000
        rewrite(folder / "task.json", task)
        recipe = read_json(folder / "whole_cohort_feedback.json")
        recipe["checks"] = [{**copy.deepcopy(recipe["checks"][0]), "id": "mean_%02d" % i} for i in range(10)]
        rewrite(folder / "whole_cohort_feedback.json", recipe)
        for check in recipe["checks"]:
            constraints.append({"context_id": identifier, "check_id": check["id"], "scale": 1,
                                "scale_reason": "Explicit artificial engineering unit; not a source SE."})
            weights.append({"context_id": identifier, "check_id": check["id"], "weight": 1,
                            "weight_reason": "Equal artificial check importance."})
    (candidate / "generator.py").write_text(
        'raise RuntimeError("SUBMITTED PROGRAM MUST NEVER BE IMPORTED")\n'
        'def generate(observed, specification, seed):\n    raise RuntimeError("NO REAL COHORT")\n', encoding="utf-8")
    lifecycle.freeze_candidate(root, candidate)
    plan = {"schema_version": 1, "parameters": [{"name": "step", "lower": 0, "upper": 3, "step": 1}],
            "constraints": constraints, "fit_seeds": [19101], "replay_seeds": [19111, 19123],
            "optimizer": {"method": "bounded_coordinate_search", "max_trials": 3, "shrink": 0.5,
                          "min_step_fraction": 0.01, "target_loss": 0},
            "execution": {"timeout_seconds": 30, "memory_mb": 1024, "output_bytes": 20000000, "log_bytes": 100000},
            "noncomputable": "infeasible"}
    criteria = {"schema_version": 1, "scope": "source_only",
                "parameter_roles": [{"name": "step", "role": "source_parameter", "rationale": "Artificial scalar."}],
                "check_weights": weights, "scientific_requirements": ["No scientific conclusion from this fixture."]}
    return root, plan, criteria


def release(root, plan, criteria, session="s"):
    validation = adapter.validate_calibration(root, "initial", plan, criteria)
    return {"schema_version": 1, "kind": "root_source_calibration_release", "decision": "release",
            "session_id": session, "binding": validation["binding"],
            "authorized_restricted_parameters": validation["required_restricted_authorizations"],
            "reason": "Artificial metadata/mock test only, never a scientific execution release."}


def mocked_bridge(monkeypatch, *, failed_steps=(), crash=False, no_fit_feasible=False):
    calls = []
    def expected(bundle, destination):
        intent = read_json(destination / "intent.json")
        step = read_json(bundle / "candidates/t/model_spec.json")["parameters"]["step"]
        seed = intent["limits"]["seed"]
        rows = []
        for identifier in intent["contexts"]:
            recipe = read_json(bundle / "candidates/t/source_contexts" / identifier / "whole_cohort_feedback.json")
            fail = step in failed_steps or (no_fit_feasible and seed == 19101)
            checks = [{"id": c["id"], "status": "approximate", "reported_value": 0,
                       "calculation": {"value": step - 2 if seed == 19101 else 100 * step},
                       "operator": c["operator"]} for c in recipe["checks"]]
            rows.append({"id": identifier, "feedback": None if fail else {"checks": checks}})
        return {"contexts": rows, "status": "failed" if any(r["feedback"] is None for r in rows) else "success"}
    def execute(bundle, destination, *, candidate=None):
        adapter.bridge.verify_preparation(bundle, destination, candidate=candidate)
        calls.append((Path(bundle), read_json(destination / "intent.json")["limits"]["seed"]))
        # Every replay must begin after the immutable selection artifact exists.
        if calls[-1][1] != 19101:
            assert (destination.parent.parent / "selection.json").is_file()
        if crash:
            raise RuntimeError("Artificial interrupted bridge")
        result = expected(bundle, destination)
        execution._write(destination / "report.json", result)
        return result
    def verify(bundle, destination, *, candidate=None):
        adapter.bridge.verify_preparation(bundle, destination, candidate=candidate)
        report = read_json(destination / "report.json")
        assert report == expected(bundle, destination)
        return report
    monkeypatch.setattr(adapter.bridge, "execute_source_contexts", execute)
    monkeypatch.setattr(adapter.bridge, "verify_source_contexts", verify)
    return calls


def run(case, monkeypatch, **mock_options):
    root, plan, criteria = case
    calls = mocked_bridge(monkeypatch, **mock_options)
    budget.create_budget(root, adapter._reservation(plan))
    result = adapter.run_calibration(root, "initial", "s", plan, criteria, release(root, plan, criteria))
    return result, calls


def test_fit_and_disjoint_baseline_selected_replay_are_frozen(case, monkeypatch):
    result, calls = run(case, monkeypatch)
    root, plan, criteria = case
    assert result["selected_trial"] == 1
    assert result["trials"][0]["parameters"] == {"step": 1}
    assert result["trials"][1]["parameters"] == {"step": 2}
    assert result["trials"][1]["fit"]["loss"] == 0
    # Mock replay deliberately makes selected worse: it must not affect choice.
    assert result["replay"]["1"][0]["score"]["loss"] > result["replay"]["0"][0]["score"]["loss"]
    assert [s for _, s in calls] == [19101, 19101, 19111, 19123, 19111, 19123]
    assert result["usage"]["executions"] == 12
    assert adapter.verify_calibration(root, "s") == result
    assert budget.get_budget(root)["reserved"]["executions"] == 14
    assert not list(root.rglob("*.csv"))
    original = read_json(root / "candidates/initial/model_spec.json")
    fitted = read_json(root / "source_calibration/s/t0001/bundle/candidates/t/model_spec.json")
    assert fitted["parameter_provenance"]["step"]["derivation"].startswith("Calibrated numerical trial 1")
    assert all(fitted["parameter_provenance"]["step"][k] == original["parameter_provenance"]["step"][k]
               for k in ("evidence_ids", "assumption_ids"))
    fitted["parameters"]["step"] = original["parameters"]["step"]
    fitted["parameter_provenance"]["step"]["derivation"] = original["parameter_provenance"]["step"]["derivation"]
    assert fitted == original
    baseline = root / "source_calibration/s/t0000/bundle/candidates/t"
    assert read_json(baseline / "model_spec.json") == original
    assert read_json(baseline / "calibration_trial.json")["value_origin"] == "unchanged_baseline"
    fitted_root = root / "source_calibration/s/t0001/bundle"
    note = read_json(fitted_root / "candidates/t/calibration_trial.json")
    assert note["trial_index"] == 1 and note["parameter_values"] == {"step": 2}
    assert note["parent_binding"] == result["binding"]
    with pytest.raises(ValueError, match="Numerical trials cannot parent"):
        adapter.validate_calibration(fitted_root, "t", plan, criteria)
    with pytest.raises(ValueError, match="already exists"):
        adapter.run_calibration(root, "initial", "s", plan, criteria, release(root, plan, criteria))
    with pytest.raises(ValueError, match="already has a session"):
        adapter.run_calibration(root, "initial", "again", plan, criteria, release(root, plan, criteria, "again"))


def test_baseline_selected_replays_reused_and_trial_cap_inclusive(case, monkeypatch):
    root, plan, criteria = case
    plan["optimizer"]["max_trials"] = 1
    result, calls = run(case, monkeypatch)
    assert len(result["trials"]) == 1 and result["selected_trial"] == 0
    assert result["stop_reason"] == "max_trials"
    assert set(result["replay"]) == {"0"}
    assert [s for _, s in calls] == [19101, 19111, 19123]
    assert result["usage"]["executions"] == 6
    assert budget.get_budget(root)["reserved"]["executions"] == 10


def test_failed_trial_preserved_and_does_not_win(case, monkeypatch):
    result, calls = run(case, monkeypatch, failed_steps=(2,))
    assert len(result["trials"]) == 3
    assert result["selected_trial"] == 0
    assert result["trials"][1]["fit"]["feasible"] is False
    assert result["trials"][1]["fit"]["loss"] is None
    assert len(result["trials"][1]["fit"]["constraints"]) == 20
    assert all(c["status"] == "unavailable" for c in result["trials"][1]["fit"]["constraints"])


def test_no_feasible_fit_still_replays_baseline(case, monkeypatch):
    result, calls = run(case, monkeypatch, no_fit_feasible=True)
    assert result["status"] == "no_feasible_trial" and result["selected_trial"] is None
    assert set(result["replay"]) == {"0"}
    assert [s for _, s in calls][-2:] == [19111, 19123]


def test_interruption_keeps_pending_reservation_and_cannot_resume(case, monkeypatch):
    root, plan, criteria = case
    mocked_bridge(monkeypatch, crash=True)
    budget.create_budget(root, adapter._reservation(plan))
    grant = release(root, plan, criteria)
    with pytest.raises(RuntimeError, match="interrupted"):
        adapter.run_calibration(root, "initial", "s", plan, criteria, grant)
    session = root / "source_calibration/s"
    assert (session / "failure.json").is_file() and (session / "t0000/fit/preparation.json").is_file()
    assert budget.get_budget(root)["pending"] == "s"
    with pytest.raises(ValueError, match="interrupted"):
        adapter.verify_calibration(root, "s")
    with pytest.raises(ValueError, match="already exists"):
        adapter.run_calibration(root, "initial", "s", plan, criteria, grant)
    assert not list(root.rglob("*.csv"))


@pytest.mark.parametrize("mutation", [
    lambda p, c: p.update(fit_seeds=[19111]),
    lambda p, c: p.update(replay_seeds=[19101, 19123]),
    lambda p, c: p["optimizer"].update(max_trials=41),
    lambda p, c: p["parameters"][0].update(name="contexts"),
    lambda p, c: p["constraints"].pop(),
    lambda p, c: p["constraints"][0].update(scale=0),
    lambda p, c: p["constraints"][0].update(scale_reason=""),
    lambda p, c: c["check_weights"].pop(),
    lambda p, c: c["check_weights"][0].update(weight=0),
    lambda p, c: c["parameter_roles"][0].update(name="other"),
])
def test_invalid_plans_fail_without_side_effects(case, mutation):
    root, plan, criteria = case
    before = adapter.bridge._inventory(root)
    mutation(plan, criteria)
    with pytest.raises((ValueError, KeyError, TypeError)):
        adapter.validate_calibration(root, "initial", plan, criteria)
    assert adapter.bridge._inventory(root) == before


def test_release_must_bind_plan_task_candidate_and_script(case):
    root, plan, criteria = case
    grant = release(root, plan, criteria)
    grant["binding"]["adapter_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="binding differs"):
        adapter.run_calibration(root, "initial", "s", plan, criteria, grant)
    assert not (root / "source_calibration").exists()
    assert not (root / "calibration_budget").exists()


def test_restricted_role_requires_explicit_root_names(case):
    root, plan, criteria = case
    criteria["parameter_roles"][0]["role"] = "context"
    grant = release(root, plan, criteria)
    assert grant["authorized_restricted_parameters"] == ["step"]
    grant["authorized_restricted_parameters"] = []
    with pytest.raises(ValueError, match="explicitly authorize"):
        adapter.run_calibration(root, "initial", "s", plan, criteria, grant)


def test_weighted_objective_not_unweighted_or_source_se_inferred(case):
    _, plan, criteria = case
    criteria["check_weights"][0]["weight"] = 2
    contexts = []
    for identifier in ("source_a", "source_b"):
        checks = [{"id": "mean_%02d" % i, "status": "approximate", "reported_value": 10,
                   "calculation": {"value": 10 + (2 if identifier == "source_a" and i == 0 else 1)}} for i in range(10)]
        contexts.append({"id": identifier, "feedback": {"checks": checks}})
    score = adapter._score({"contexts": contexts}, plan, criteria, 19101)
    assert score["loss"] == pytest.approx((2 * 4 + 19) / 21)
    assert len(score["constraints"]) == 20
    contexts[0]["feedback"]["checks"][0]["status"] = "not_computable"
    assert adapter._score({"contexts": contexts}, plan, criteria, 19101)["loss"] is None


@pytest.mark.parametrize("path", ["selection.json", "t0000/trial.json", "t0001/bundle/candidates/t/generator.py",
                                   "t0001/bundle/candidates/t/calibration_trial.json"])
def test_tampering_is_rejected(case, monkeypatch, path):
    run(case, monkeypatch)
    root, _, _ = case
    with (root / "source_calibration/s" / path).open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValueError, match="inventory/hash"):
        adapter.verify_calibration(root, "s")
