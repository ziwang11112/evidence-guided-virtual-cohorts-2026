"""Invented declarations test structural scope, references and lifecycle linkage.

The replay backend is mocked. These tests certify neither biological judgments
nor process isolation, and no target outcomes are read.
"""
import copy
import json

import pytest

from cohort_harness import source_replay
from cohort_harness.__main__ import validate_bundle
from cohort_harness.analysis_evidence import (
    DIMENSIONS, summarize_analysis_evidence, validate_analysis_evidence,
)
from cohort_harness.contracts import ContractError
from cohort_harness.demo import make_demo
from cohort_harness.lifecycle import freeze_candidate, read_json, sha256, verify_candidate
from cohort_harness.source_checks import run_source_checks
from test_source_replay import bundle as replay_bundle, fake_backend


def write(path, value):
    path.write_text(json.dumps(value, allow_nan=False, indent=2), encoding="utf-8")


def direct_manifest():
    return {"schema_version": 1, "analyses": [{
        "id": "mean_y", "estimand": {
            "description": "The arithmetic mean of invented y in the stated population.",
            "kind": "mean", "outcome": "y", "exposures": [], "conditioning": [], "adjustment": [],
            "scale": "Arithmetic mean on the original measurement scale", "unit": "y_unit",
            "population": "Invented target-use population", "measurement": "Invented exact y measurements",
            "selection": "All members of the declared population",
        },
        "assessment": "directly_reported", "rationale": "Fixture-only author declaration of a reported mean.",
        "assumption_ids": [], "evidence_links": [{
            "evidence_id": "E1", "relation": "direct_estimand",
            "comparisons": {dimension: "declared_match" for dimension in DIMENSIONS},
            "assumption_ids": [], "rationale": "The invented source reports this mean.",
        }], "gaps": [], "actions": [],
    }]}


def with_gap(manifest, dimension="population"):
    analysis = manifest["analyses"][0]
    analysis["gaps"] = [{
        "id": "G1", "dimension": dimension, "description": "The needed information was not reported.",
        "consequence": "The requested use remains dependent on unverified information.", "assumption_ids": [],
    }]
    analysis["actions"] = [{
        "id": "R1", "gap_ids": ["G1"], "tool": "none", "status": "unavailable",
        "request": "Seek a directly applicable estimate for the requested use.",
        "reason": "This invented task does not permit retrieval.",
    }]
    return manifest


def transported_manifest():
    manifest = with_gap(direct_manifest())
    analysis = manifest["analyses"][0]
    analysis.update(assessment="transported", assumption_ids=["A1"])
    analysis["evidence_links"][0]["comparisons"]["population"] = "declared_difference"
    analysis["evidence_links"][0]["assumption_ids"] = ["A1"]
    analysis["gaps"][0]["assumption_ids"] = ["A1"]
    return manifest


@pytest.fixture
def fixture(tmp_path):
    root = make_demo(tmp_path / "invented")
    candidate = root / "candidates/initial"
    return root, candidate, read_json(root / "task.json"), read_json(candidate / "evidence.json"), read_json(candidate / "model_spec.json")


def test_direct_label_remains_a_declaration_and_no_population_equality_is_asserted(fixture):
    _, _, task, evidence, spec = fixture
    manifest = direct_manifest()
    assert manifest["analyses"][0]["estimand"]["population"] != task["population"]
    report = summarize_analysis_evidence(manifest, task, evidence, spec)
    assert report["contract"] == "structurally_valid"
    assert report["assessment_origin"] == "submitter_declaration"
    assert report["scientific_validity"] == report["joint_distribution_identification"] == "not_assessed"
    assert report["uncertainty_calibration"] == "not_assessed"
    assert report["retrieval_executed"] is False
    assert report["analyses"][0]["declared_assessment"] == "directly_reported"


def test_transport_assumptions_do_not_close_gap(fixture):
    _, _, task, evidence, spec = fixture
    report = summarize_analysis_evidence(transported_manifest(), task, evidence, spec)
    assert report["analyses"][0]["unresolved_gap_ids"] == ["G1"]
    assert report["analyses"][0]["assumption_ids"] == ["A1"]
    assert report["analyses"][0]["unavailable_action_ids"] == ["R1"]


def test_explicit_unassessed_use_and_prior_only_evidence_are_valid(fixture):
    _, _, task, _, spec = fixture
    manifest = with_gap(direct_manifest(), "estimand")
    manifest["analyses"][0].update(assessment="unassessed", evidence_links=[])
    task["information_policy"]["mode"] = "prior_only"
    evidence = {"schema_version": 1, "sources": [], "items": []}
    for provenance in spec["parameter_provenance"].values():
        provenance["evidence_ids"] = []
    validate_analysis_evidence(manifest, task, evidence, spec)


@pytest.mark.parametrize("mutation", ["unknown_evidence", "duplicate_link", "unknown_assumption",
    "unknown_source", "excluded_source", "unknown_gap", "duplicate_analysis", "unknown_variable"])
def test_cross_record_reference_attacks_reject(fixture, mutation):
    _, _, task, evidence, spec = fixture
    manifest = transported_manifest()
    analysis = manifest["analyses"][0]
    if mutation == "unknown_evidence":
        analysis["evidence_links"][0]["evidence_id"] = "unregistered_estimate"
    elif mutation == "duplicate_link":
        analysis["evidence_links"].append(copy.deepcopy(analysis["evidence_links"][0]))
    elif mutation == "unknown_assumption":
        analysis["assumption_ids"].append("unrecorded")
    elif mutation == "unknown_source":
        evidence["items"][0]["source_id"] = "absent_source"
    elif mutation == "excluded_source":
        task["information_policy"]["excluded_cohorts"] = ["INVENTED-DEMO"]
    elif mutation == "unknown_gap":
        analysis["actions"][0]["gap_ids"] = ["nonexistent_gap"]
    elif mutation == "duplicate_analysis":
        manifest["analyses"].append(copy.deepcopy(analysis))
    else:
        analysis["estimand"]["outcome"] = "hidden_outcome"
    with pytest.raises(ContractError):
        validate_analysis_evidence(manifest, task, evidence, spec)


@pytest.mark.parametrize("mutation", ["no_links", "partial_no_links", "unassessed_no_gap", "missing_action",
    "missing_bridge", "hidden_difference", "direct_with_gap", "wrong_variable", "wrong_adjustment", "wrong_unit"])
def test_empty_coverage_and_contradictory_declarations_reject(fixture, mutation):
    _, _, task, evidence, spec = fixture
    manifest = direct_manifest()
    analysis = manifest["analyses"][0]
    if mutation in {"no_links", "partial_no_links"}:
        analysis["evidence_links"] = []
        if mutation == "partial_no_links":
            with_gap(manifest)
            analysis["assessment"] = "partial"
    elif mutation == "unassessed_no_gap":
        analysis.update(assessment="unassessed", evidence_links=[])
    elif mutation == "missing_action":
        manifest = transported_manifest()
        manifest["analyses"][0]["actions"] = []
    elif mutation == "missing_bridge":
        manifest = transported_manifest()
        manifest["analyses"][0]["evidence_links"][0]["assumption_ids"] = []
    elif mutation == "hidden_difference":
        manifest = transported_manifest()
        manifest["analyses"][0]["evidence_links"][0]["comparisons"]["measurement"] = "unknown"
    elif mutation == "direct_with_gap":
        with_gap(manifest)
    elif mutation == "wrong_variable":
        analysis["estimand"]["outcome"] = "x"
    elif mutation == "wrong_adjustment":
        analysis["estimand"]["adjustment"] = ["x"]
    else:
        analysis["estimand"]["unit"] = "different_unit"
    with pytest.raises(ContractError):
        validate_analysis_evidence(manifest, task, evidence, spec)


def test_uncertainty_sd_cannot_substitute_for_an_sd_evidence_estimate(fixture):
    _, _, task, evidence, spec = fixture
    evidence["items"][0]["uncertainty"] = {"kind": "sd", "value": 9}
    manifest = direct_manifest()
    manifest["analyses"][0]["estimand"]["kind"] = "sd"
    with pytest.raises(ContractError, match="different statistic"):
        validate_analysis_evidence(manifest, task, evidence, spec)


@pytest.mark.parametrize("difference", ["rank", "quantile", "other_name"])
def test_statistic_definitions_cannot_be_relabelled(fixture, difference):
    _, _, task, evidence, spec = fixture
    manifest = direct_manifest()
    request, item = manifest["analyses"][0]["estimand"], evidence["items"][0]
    if difference == "rank":
        item.update(kind="correlation", variables=["x", "y"], unit="1", estimate=0.5)
        request.update(kind="spearman_correlation", exposures=["x"], unit="1")
    elif difference == "quantile":
        item.update(kind="quantile", q=0.25, method="linear")
        request.update(kind="quantile", q=0.75, method="linear")
    else:
        item.update(kind="reported_other", statistic_name="hazard ratio")
        request.update(kind="reported_other", statistic_name="odds ratio")
    with pytest.raises(ContractError, match="different statistic"):
        validate_analysis_evidence(manifest, task, evidence, spec)


def test_pairwise_evidence_cannot_automatically_identify_joint_distribution(fixture):
    _, _, task, evidence, spec = fixture
    evidence["items"][0].update(kind="correlation", variables=["x", "y"], unit="1", estimate=0.5)
    manifest = with_gap(direct_manifest(), "joint_distribution")
    analysis = manifest["analyses"][0]
    analysis["estimand"].update(kind="reported_other", statistic_name="joint upper-tail probability", unit="1")
    analysis["assessment"] = "partial"
    link = analysis["evidence_links"][0]
    link["relation"] = "component"
    link["comparisons"]["estimand"] = "declared_difference"
    report = summarize_analysis_evidence(manifest, task, evidence, spec)
    assert report["joint_distribution_identification"] == "not_assessed"
    assert report["analyses"][0]["unresolved_gap_ids"] == ["G1"]
    analysis["assessment"] = "directly_reported"
    with pytest.raises(ContractError):
        validate_analysis_evidence(manifest, task, evidence, spec)


def test_overlapping_sources_are_visible_without_independence_or_confidence(fixture):
    _, _, task, evidence, spec = fixture
    source = copy.deepcopy(evidence["sources"][0])
    source.update(id="S2", cohort_ids=[" INVENTED-DEMO "])
    evidence["sources"].append(source)
    evidence["items"].append({**evidence["items"][0], "id": "E3", "source_id": "S2"})
    manifest = direct_manifest()
    manifest["analyses"][0]["evidence_links"].append({**copy.deepcopy(manifest["analyses"][0]["evidence_links"][0]), "evidence_id": "E3"})
    report = summarize_analysis_evidence(manifest, task, evidence, spec)
    assert report["analyses"][0]["shared_declared_cohorts"] == {"invented-demo": ["S1", "S2"]}
    assert "confidence" not in report and "independent_source_count" not in report["analyses"][0]


def test_permitted_plan_does_not_execute_or_reserve_retrieval(fixture):
    _, _, task, evidence, spec = fixture
    manifest = transported_manifest()
    task["information_policy"]["allowed_tools"] = ["literature.search"]
    task["budget"]["source_queries"] = 1
    manifest["analyses"][0]["actions"][0].update(tool="literature.search", status="planned", request="invented population arithmetic mean y")
    before = copy.deepcopy((task, evidence, spec))
    report = summarize_analysis_evidence(manifest, task, evidence, spec)
    assert report["retrieval_executed"] is False
    assert report["analyses"][0]["planned_action_ids"] == ["R1"]
    assert (task, evidence, spec) == before
    task["budget"]["source_queries"] = 0
    with pytest.raises(ContractError, match="zero task budget"):
        validate_analysis_evidence(manifest, task, evidence, spec)
    task["budget"]["source_queries"] = 1
    task["information_policy"]["allowed_tools"] = []
    with pytest.raises(ContractError, match="not permitted"):
        validate_analysis_evidence(manifest, task, evidence, spec)


@pytest.mark.parametrize("mutation", ["confidence", "identification", "executed", "schema_bool", "nested", "unknown_key"])
def test_overclaims_and_malformed_fields_reject(fixture, mutation):
    _, _, task, evidence, spec = fixture
    manifest = transported_manifest()
    analysis = manifest["analyses"][0]
    if mutation == "confidence":
        analysis["confidence"] = 0.99
    elif mutation == "identification":
        manifest["joint_distribution_identified"] = True
    elif mutation == "executed":
        analysis["actions"][0]["status"] = "completed"
    elif mutation == "schema_bool":
        manifest["schema_version"] = True
    elif mutation == "nested":
        analysis["evidence_links"][0]["comparisons"] = []
    else:
        analysis["estimand"]["approved_by_validator"] = True
    with pytest.raises(ContractError):
        validate_analysis_evidence(manifest, task, evidence, spec)


def test_cli_validation_and_direct_freeze_reject_same_invalid_sidecar(fixture):
    root, candidate, *_ = fixture
    manifest = direct_manifest()
    manifest["analyses"][0]["evidence_links"][0]["evidence_id"] = "missing"
    write(candidate / "analysis_evidence.json", manifest)
    with pytest.raises(ContractError, match="Unknown linked evidence"):
        validate_bundle(root, candidate)
    with pytest.raises(ContractError, match="Unknown linked evidence"):
        freeze_candidate(root, candidate)
    assert not (candidate / "freeze.json").exists()


def test_freeze_rejects_known_source_with_unregistered_artifact(fixture):
    root, candidate, _, evidence, _ = fixture
    write(candidate / "analysis_evidence.json", direct_manifest())
    evidence["sources"][0]["artifacts"][0]["sha256"] = "a" * 64
    write(candidate / "evidence.json", evidence)
    with pytest.raises(ContractError, match="not registered"):
        freeze_candidate(root, candidate)


def test_sidecar_directory_cannot_bypass_direct_freeze(fixture):
    root, candidate, *_ = fixture
    (candidate / "analysis_evidence.json").mkdir()
    with pytest.raises(ContractError):
        validate_bundle(root, candidate)
    with pytest.raises(ContractError, match="regular file"):
        freeze_candidate(root, candidate)


def test_declaration_sidecar_cannot_be_substituted_for_a_check_result(fixture):
    root, candidate, *_ = fixture
    sidecar = candidate / "analysis_evidence.json"
    write(sidecar, direct_manifest())
    checks = read_json(candidate / "checks.json")
    checks["artifacts"] = [{"path": sidecar.name, "sha256": sha256(sidecar)}]
    write(candidate / "checks.json", checks)
    with pytest.raises(ContractError, match="auxiliary result file"):
        freeze_candidate(root, candidate)


def test_optional_sidecar_legacy_behavior_and_freeze_immutability(fixture):
    root, candidate, *_ = fixture
    assert validate_bundle(root, candidate)["contract"] == "valid"
    manifest = direct_manifest()
    write(candidate / "analysis_evidence.json", manifest)
    assert validate_bundle(root, candidate)["scientific_validity"] == "not_assessed"
    receipt = freeze_candidate(root, candidate)
    assert "candidates/initial/analysis_evidence.json" in receipt["commitments"]
    verify_candidate(root, candidate)
    manifest["analyses"][0]["rationale"] = "Changed but still structurally valid declaration."
    write(candidate / "analysis_evidence.json", manifest)
    with pytest.raises(ContractError, match="commitments changed"):
        verify_candidate(root, candidate)


def test_legacy_candidate_without_sidecar_still_freezes(fixture):
    root, candidate, *_ = fixture
    freeze_candidate(root, candidate)
    verify_candidate(root, candidate)


@pytest.mark.parametrize("text", ['{"schema_version":1,"schema_version":1,"analyses":[]}',
                                 '{"schema_version":1,"analyses":NaN}'])
def test_sidecar_uses_strict_json_loading(fixture, text):
    root, candidate, *_ = fixture
    (candidate / "analysis_evidence.json").write_text(text, encoding="utf-8")
    with pytest.raises(ContractError):
        validate_bundle(root, candidate)
    with pytest.raises(ContractError):
        freeze_candidate(root, candidate)


def test_source_check_success_does_not_change_gap_summary(fixture):
    root, candidate, task, evidence, spec = fixture
    manifest = transported_manifest()
    before = summarize_analysis_evidence(manifest, task, evidence, spec)
    checks = run_source_checks(root, candidate)
    assert all(abs(check["difference"]) < 1e-12 for check in checks["checks"])
    assert summarize_analysis_evidence(manifest, task, evidence, spec) == before


def test_source_replay_copies_target_use_map_without_reinterpreting_population(tmp_path, monkeypatch):
    manifest = transported_manifest()
    def attach(_plan, source):
        write(source.parent / "analysis_evidence.json", manifest)
    root, candidate = replay_bundle(tmp_path, edit=attach)
    fake_backend(monkeypatch)
    report = source_replay.run_source_replay(root, candidate, "analysis_map", 17)
    assert report["status"] == "success"
    child = root / "source_replays/analysis_map" / report["contexts"][0]["child_bundle"]
    assert read_json(child / "task.json")["population"] != read_json(root / "task.json")["population"]
    assert sha256(child / "candidates/source/analysis_evidence.json") == sha256(candidate / "analysis_evidence.json")
    assert source_replay.verify_source_replay(root, "analysis_map", candidate=candidate) == report
    copied = read_json(child / "candidates/source/analysis_evidence.json")
    summary = summarize_analysis_evidence(copied, read_json(child / "task.json"),
                                         read_json(candidate / "evidence.json"), read_json(candidate / "model_spec.json"))
    assert summary["scientific_validity"] == "not_assessed"
    assert summary["analyses"][0]["unresolved_gap_ids"] == ["G1"]
