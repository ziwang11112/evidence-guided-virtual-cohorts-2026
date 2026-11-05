"""Synthetic metadata/opaque bytes only; no generator or clinical data execution."""
import copy
import hashlib
import json

import pytest

from cohort_harness.contracts import ContractError
from cohort_harness.evidence_use_v1 import validate_evidence_use
from test_evidence_actions_v1 import routing_inputs


def encoded(value):
    return json.dumps(value, allow_nan=False).encode("utf-8")


def bind(fixture, role, value):
    manifest, artifacts = fixture
    path = manifest["bindings"][role]["path"]
    artifacts[path] = value if isinstance(value, bytes) else encoded(value)
    manifest["bindings"][role]["sha256"] = hashlib.sha256(artifacts[path]).hexdigest()


def obj(fixture, role):
    manifest, artifacts = fixture
    return json.loads(artifacts[manifest["bindings"][role]["path"]])


def run(fixture, required=None):
    return validate_evidence_use(*fixture, required_analysis_ids=required or ["mean_y"])


@pytest.fixture
def use_fixture(routing_inputs):
    analysis, _, task, evidence, spec, _ = copy.deepcopy(routing_inputs)
    check_bytes = b"Synthetic source-only check result; never a biomedical validation."
    checks = {"scope": "fixture_only", "records": [
        {"name": "source_review", "status": "fail", "detail": "An invented discrepancy was retained."}],
        "artifacts": [{"path": "checks/source_review.txt", "sha256": hashlib.sha256(check_bytes).hexdigest()}]}
    role_objects = {"task": task, "evidence": evidence, "model_spec": spec, "analysis_evidence": analysis,
                    "checks": checks, "generator": b"opaque initial generator bytes, never executed"}
    manifest = {"schema_version": 1, "bindings": {}, "decisions": [{
        "id": "D1", "analysis_id": "mean_y", "choice": "relationship", "evidence_ids": ["E1"],
        "parameter_paths": ["/parameters/invented_parameter"], "assumption_ids": ["A1"],
        "check_names": ["source_review"], "check_artifact_paths": ["checks/source_review.txt"]}]}
    artifacts = {"candidates/new/checks/source_review.txt": check_bytes}
    fixture = manifest, artifacts
    for role, value in role_objects.items():
        path = "task.json" if role == "task" else "candidates/new/" + (
            "generator.py" if role == "generator" else role + ".json")
        manifest["bindings"][role] = {"path": path, "sha256": "0" * 64}
        bind(fixture, role, value)
    return fixture


def revision(fixture, *, update=True):
    manifest, artifacts = fixture
    for role in ("evidence", "model_spec", "generator"):
        value = artifacts[manifest["bindings"][role]["path"]]
        baseline_role = "baseline_" + role
        path = "candidates/old/" + ("generator.py" if role == "generator" else role + ".json")
        manifest["bindings"][baseline_role] = {"path": path, "sha256": "0" * 64}
        bind(fixture, baseline_role, value)
    if update:
        spec = obj(fixture, "model_spec")
        spec["parameters"]["invented_parameter"] = 8
        bind(fixture, "model_spec", spec)
    return fixture


def test_initial_binds_use_without_claiming_change_or_scientific_success(use_fixture):
    before = copy.deepcopy(use_fixture)
    result = run(use_fixture)
    assert result == run(use_fixture)
    assert use_fixture == before
    assert result["mode"] == "initial"
    assert result["parameter_status"] == "initial_values_bound"
    assert result["changed_parameter_paths"] is result["generator_bytes_changed"] is None
    assert result["decisions"][0]["check_statuses"] == {"source_review": "fail"}
    assert result["decisions"][0]["unresolved_gap_ids"] == ["G1"]
    assert result["scientific_validity"] == result["generator_parameter_use"] == "not_assessed"
    assert result["data_quality_gain"] == "not_tested"
    assert result["check_execution"] == "not_verified"


def test_revision_validates_real_change_without_upgrading_code_or_science(use_fixture):
    result = run(revision(use_fixture))
    assert result["changed_parameter_paths"] == ["/parameters/invented_parameter"]
    assert result["parameter_status"] == "changed"
    assert result["specification_bytes_changed"] is True
    assert result["generator_bytes_changed"] is False


@pytest.mark.parametrize("role", ["task", "evidence", "model_spec", "analysis_evidence", "checks", "generator"])
def test_any_stale_binding_fails(use_fixture, role):
    manifest, artifacts = use_fixture
    artifacts[manifest["bindings"][role]["path"]] += b" "
    with pytest.raises(ContractError, match="hash mismatch"):
        run(use_fixture)


def test_check_artifact_bytes_are_verified(use_fixture):
    use_fixture[1]["candidates/new/checks/source_review.txt"] = b"changed result"
    with pytest.raises(ContractError, match="hash mismatch"):
        run(use_fixture)


@pytest.mark.parametrize("attack", ["wrong_path", "unaccounted", "retain_changed", "check_only_changed"])
def test_changed_path_claims_must_match_specification(use_fixture, attack):
    revision(use_fixture)
    decision = use_fixture[0]["decisions"][0]
    if attack == "wrong_path":
        decision["parameter_paths"] = ["/parameters/nonexistent"]
    elif attack == "unaccounted":
        spec = obj(use_fixture, "model_spec")
        spec["parameters"]["extra"] = 3
        spec["parameter_provenance"]["extra"] = copy.deepcopy(spec["parameter_provenance"]["invented_parameter"])
        bind(use_fixture, "model_spec", spec)
    elif attack == "retain_changed":
        decision["choice"] = "retain_assumption"
    elif attack == "check_only_changed":
        decision.update(choice="check_only", parameter_paths=[])
    with pytest.raises(ContractError):
        run(use_fixture)


def test_parameter_retention_does_not_hide_changed_generator_or_provenance(use_fixture):
    revision(use_fixture, update=False)
    use_fixture[0]["decisions"][0]["choice"] = "retain_assumption"
    bind(use_fixture, "generator", b"different opaque generator bytes")
    spec = obj(use_fixture, "model_spec")
    spec["parameter_provenance"]["invented_parameter"]["derivation"] = "Re-reviewed, retained assumption."
    bind(use_fixture, "model_spec", spec)
    result = run(use_fixture)
    assert result["parameter_status"] == "unchanged"
    assert result["generator_bytes_changed"] is result["specification_bytes_changed"] is True


@pytest.mark.parametrize("dimension", ["population", "scale"])
@pytest.mark.parametrize("where", ["gap", "link", "decision", "provenance"])
def test_unmarked_transport_or_unit_bridge_cannot_support_parameter_use(use_fixture, dimension, where):
    analysis = obj(use_fixture, "analysis_evidence")
    use = analysis["analyses"][0]
    use["assessment"] = "partial"  # existing contract permits partial with unmarked bridges
    use["evidence_links"][0]["comparisons"]["population"] = "declared_match"
    use["evidence_links"][0]["comparisons"][dimension] = "unknown"
    use["gaps"][0]["dimension"] = dimension
    if where == "gap":
        use["gaps"][0]["assumption_ids"] = []
    elif where == "link":
        use["evidence_links"][0]["assumption_ids"] = []
    elif where == "decision":
        use_fixture[0]["decisions"][0]["assumption_ids"] = []
    else:
        spec = obj(use_fixture, "model_spec")
        spec["parameter_provenance"]["invented_parameter"]["assumption_ids"] = []
        bind(use_fixture, "model_spec", spec)
    bind(use_fixture, "analysis_evidence", analysis)
    with pytest.raises(ContractError):
        run(use_fixture)


def test_check_only_retains_unknown_unit_gap_without_inventing_bridge(use_fixture):
    analysis = obj(use_fixture, "analysis_evidence")
    use = analysis["analyses"][0]
    use["assessment"] = "partial"
    use["evidence_links"][0]["assumption_ids"] = []
    use["gaps"][0]["assumption_ids"] = []
    bind(use_fixture, "analysis_evidence", analysis)
    use_fixture[0]["decisions"][0].update(choice="check_only", parameter_paths=[], assumption_ids=[])
    assert run(use_fixture)["decisions"][0]["choice"] == "check_only"


@pytest.mark.parametrize("choice", ["relationship", "dispersion"])
@pytest.mark.parametrize("value", [True, {"nested": 2}, "2"])
def test_numerical_use_requires_actual_numeric_parameter(use_fixture, choice, value):
    spec = obj(use_fixture, "model_spec")
    spec["parameters"]["invented_parameter"] = value
    bind(use_fixture, "model_spec", spec)
    use_fixture[0]["decisions"][0]["choice"] = choice
    with pytest.raises(ContractError, match="must be a number"):
        run(use_fixture)


def test_new_nuisance_parameter_need_not_be_mapped_in_initial_mode(use_fixture):
    spec = obj(use_fixture, "model_spec")
    spec["parameters"]["nuisance"] = "synthetic"
    spec["parameter_provenance"]["nuisance"] = {
        "evidence_ids": [], "assumption_ids": ["A1"], "derivation": "Fixture-only nuisance setting."}
    bind(use_fixture, "model_spec", spec)
    assert run(use_fixture)["mode"] == "initial"


@pytest.mark.parametrize("attack", ["missing_analysis", "missing_decision", "unknown_check", "unknown_artifact", "unknown_evidence", "partial_baseline"])
def test_reference_and_coverage_failures_reject(use_fixture, attack):
    decision = use_fixture[0]["decisions"][0]
    required = ["mean_y"]
    if attack == "missing_analysis":
        required.append("unlisted")
    elif attack == "missing_decision":
        use_fixture[0]["decisions"] = []
    elif attack == "unknown_check":
        decision["check_names"] = ["invented_missing_check"]
    elif attack == "unknown_artifact":
        decision["check_artifact_paths"] = ["absent.txt"]
    elif attack == "unknown_evidence":
        decision["evidence_ids"] = ["absent"]
    else:
        use_fixture[0]["bindings"]["baseline_model_spec"] = use_fixture[0]["bindings"]["model_spec"]
    with pytest.raises(ContractError):
        run(use_fixture, required)


@pytest.mark.parametrize("raw", [b'{"parameters":{},"parameters":{}}', b'{"parameters":{"p":NaN}}'])
def test_bound_json_still_rejects_duplicate_keys_and_nonfinite_constants(use_fixture, raw):
    bind(use_fixture, "model_spec", raw)
    with pytest.raises(ContractError):
        run(use_fixture)


def test_declaration_cannot_be_used_as_auxiliary_check_result(use_fixture):
    checks = obj(use_fixture, "checks")
    checks["artifacts"][0]["path"] = "evidence_use_v1.json"
    bind(use_fixture, "checks", checks)
    with pytest.raises(ContractError, match="auxiliary result"):
        run(use_fixture)


@pytest.mark.parametrize("operation", ["nested_add", "nested_remove", "list_edit", "list_resize", "escaped_key"])
def test_scenario_revision_tracks_exact_structural_change(use_fixture, operation):
    spec = obj(use_fixture, "model_spec")
    spec["parameters"]["invented_parameter"] = {"a": [1, 2], "b": 3, "a/b~c": 4}
    bind(use_fixture, "model_spec", spec)
    revision(use_fixture, update=False)
    if operation == "nested_add":
        spec["parameters"]["invented_parameter"]["new"] = "alternative"
        path = "/parameters/invented_parameter/new"
    elif operation == "nested_remove":
        del spec["parameters"]["invented_parameter"]["b"]
        path = "/parameters/invented_parameter/b"
    elif operation == "list_edit":
        spec["parameters"]["invented_parameter"]["a"][1] = 5
        path = "/parameters/invented_parameter/a/1"
    elif operation == "list_resize":
        spec["parameters"]["invented_parameter"]["a"].append(5)
        path = "/parameters/invented_parameter/a"
    else:
        spec["parameters"]["invented_parameter"]["a/b~c"] = 5
        path = "/parameters/invented_parameter/a~1b~0c"
    bind(use_fixture, "model_spec", spec)
    use_fixture[0]["decisions"][0].update(choice="scenario", parameter_paths=[path])
    assert run(use_fixture)["changed_parameter_paths"] == [path]
    if operation != "list_resize":
        use_fixture[0]["decisions"][0]["parameter_paths"] = ["/parameters/invented_parameter"]
        with pytest.raises(ContractError, match="exact changed"):
            run(use_fixture)


def test_noncomputable_retention_records_remain_noncomputable(use_fixture):
    checks = obj(use_fixture, "checks")
    checks["records"][0]["status"] = "not_computable"
    checks["artifacts"] = []
    bind(use_fixture, "checks", checks)
    use_fixture[0]["decisions"][0].update(choice="retain_assumption", check_artifact_paths=[])
    assert run(use_fixture)["decisions"][0]["check_statuses"] == {"source_review": "not_computable"}


@pytest.mark.parametrize("choice", ["relationship", "dispersion", "retain_assumption"])
def test_unchanged_direct_evidence_use_needs_no_invented_assumption(use_fixture, choice):
    analysis = obj(use_fixture, "analysis_evidence")
    use = analysis["analyses"][0]
    use.update(assessment="directly_reported", assumption_ids=[], gaps=[], actions=[])
    use["evidence_links"][0]["comparisons"]["population"] = "declared_match"
    use["evidence_links"][0]["assumption_ids"] = []
    bind(use_fixture, "analysis_evidence", analysis)
    spec = obj(use_fixture, "model_spec")
    spec["assumptions"] = []
    spec["parameter_provenance"]["invented_parameter"]["assumption_ids"] = []
    bind(use_fixture, "model_spec", spec)
    revision(use_fixture, update=False)
    use_fixture[0]["decisions"][0].update(choice=choice, assumption_ids=[])
    report = run(use_fixture)
    assert report["parameter_status"] == "unchanged"
    assert report["decisions"][0]["support_origin"] == "evidence_only"
    assert report["decisions"][0]["parameter_effects"] == {"/parameters/invented_parameter": "unchanged"}


def test_shared_parameter_can_support_multiple_required_analyses(use_fixture):
    revision(use_fixture)
    analysis = obj(use_fixture, "analysis_evidence")
    analysis["analyses"].append({**copy.deepcopy(analysis["analyses"][0]), "id": "second_use"})
    bind(use_fixture, "analysis_evidence", analysis)
    use_fixture[0]["decisions"].append({**copy.deepcopy(use_fixture[0]["decisions"][0]),
                                      "id": "D2", "analysis_id": "second_use"})
    report = run(use_fixture, ["mean_y", "second_use"])
    assert report["changed_parameter_paths"] == ["/parameters/invented_parameter"]
    assert all(decision["parameter_effects"] == {"/parameters/invented_parameter": "changed"}
               for decision in report["decisions"])


@pytest.mark.parametrize("choice", ["relationship", "dispersion", "scenario"])
def test_assumption_only_update_is_explicit_without_fabricating_evidence(use_fixture, choice):
    revision(use_fixture)
    spec = obj(use_fixture, "model_spec")
    spec["parameter_provenance"]["invented_parameter"]["evidence_ids"] = []
    bind(use_fixture, "model_spec", spec)
    use_fixture[0]["decisions"][0].update(choice=choice, evidence_ids=[])
    report = run(use_fixture)
    assert report["parameter_status"] == "changed"
    assert report["decisions"][0]["support_origin"] == "assumption_only"


def test_revision_baseline_case_alias_of_current_candidate_is_rejected(use_fixture):
    revision(use_fixture)
    for role in ("baseline_evidence", "baseline_model_spec", "baseline_generator"):
        manifest, artifacts = use_fixture
        old = manifest["bindings"][role]["path"]
        new = old.replace("candidates/old", "CANDIDATES/NEW")
        manifest["bindings"][role]["path"] = new
        artifacts[new] = artifacts.pop(old)
    with pytest.raises(ContractError, match="distinct paths"):
        run(use_fixture)
