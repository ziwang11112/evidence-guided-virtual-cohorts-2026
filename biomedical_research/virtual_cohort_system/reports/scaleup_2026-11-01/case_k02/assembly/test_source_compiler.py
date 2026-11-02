"""Changed, explicitly invented packet fixtures; no actual fit/check/sample.

Real contract/semantic/declaration validators run on temporary metadata only.
Test-only assumption/review records never enter the actual compilation.
"""
import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "operators"))
import source_compiler as compiler
import execution_feedback as supplement
from cohort_harness import contracts, execution, lifecycle, semantic_feedback_v1 as semantic


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")


def compile_packet(packet, task):
    blob = encoded(packet)
    return compiler.compile_source_packet(blob, task, expected_packet_sha256=hashlib.sha256(blob).hexdigest())


@pytest.fixture
def fixture(monkeypatch):
    packet = json.loads((HERE.parent / "request/sources/greiner_source_packet.json").read_text(encoding="utf-8-sig"))
    task = json.loads((HERE.parent / "request/task_template.json").read_text(encoding="utf-8-sig"))
    packet["provenance"]["title"] = "Invented changed packet for compiler tests, not source evidence"
    for record in packet["constraint_candidates"]:
        record["provenance"]["locator"] = "Invented fixture " + record["id"]
        if record["reported_statistic"] == "geometric_mean": record["value"] = 2.0
        elif record["reported_statistic"] == "proportion": record["value"] = 25.0
        else: record["value"] = 20.0
        record["reported_text"] = str(record["value"])
        if record["uncertainty"]["kind"] == "confidence_interval":
            record["uncertainty"].update(lower=record["value"] - 0.1, upper=record["value"] + 0.1, reported_text="Invented interval")
    for record in packet["contextual_regressions"]:
        record["reported_estimate"] = 0.0
        record["reported_ci95"] = [-0.1, 0.1]
        record["provenance"]["locator"] = "Invented context regression " + record["id"]
    def forbidden(*args, **kwargs):
        pytest.fail("No generator, process, network or source statistic allowed")
    for owner, name in [(execution, "run_candidate"), (semantic, "collect_feedback"), (semantic.legacy, "collect_feedback"),
                        (supplement, "collect_feedback"), (subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")]:
        monkeypatch.setattr(owner, name, forbidden)
    return packet, task


def test_original_percentage_ci_and_issues_preserved_normalized_once(fixture):
    packet, task = fixture
    original = copy.deepcopy(packet)
    result = compile_packet(packet, task)
    assert packet == original
    assert len(result["evidence"]["items"]) == 60
    evidence = {x["id"]: x for x in result["evidence"]["items"]}
    for row in result["s01_normalized_constraints"]:
        p = row["low_hdl_proportion"]
        assert p["value"] == 0.25 and p["unit"] == "1"
        item = evidence[p["evidence_id"]]
        assert item["estimate"] == 25 and item["unit"] == "%"
        assert item["uncertainty"] == {"kind": "ci", "low": 24.9, "high": 25.1, "level": 0.95}
    for record in result["s01_normalization_records"]:
        assert record["original_record"]["value"] == 25
        assert record["derivation"]["times_applied"] == 1
        assert record["original_record_sha256"] == compiler.digest(record["original_record"])
        assert record["normalized_record_sha256"] == compiler.digest(record["normalized_record"])
    assert result["source_issues"] == packet["issues"]
    assert result["counts"]["activated_checks"] == result["counts"]["fitted_models"] == 0
    assert sum(d["disposition"] == "potential_direct_supplemental_descriptive_diagnostic" for d in result["dispositions"]) == 24
    assert sum(d["disposition"] == "unavailable_derived_non_hdl_not_task_column" for d in result["dispositions"]) == 6


def test_all_original_records_and_regression_roles_are_retained(fixture):
    packet, task = fixture
    result = compile_packet(packet, task)
    by_id = {r["id"]: r for r in packet["constraint_candidates"] + packet["contextual_regressions"]}
    for identifier, record in result["record_provenance"].items():
        assert record["original_record"] == by_id[identifier]
        assert record["original_record_sha256"] == compiler.digest(by_id[identifier])
    regression = next(x for x in result["evidence"]["items"] if x["id"].startswith("greiner_table3"))
    assert regression["kind"] == "reported_other" and regression["statistic_name"] == "regression_coefficient_unresolved_scale"
    assert regression["unit"] == "unresolved_regression_scale"
    assert all(t["assumption_ids"] == [] and t["supplement"]["context_review"] is None for t in result["source_context_templates"])
    assert all(c["proxy"] is None for t in result["source_context_templates"] for c in t["supplement"]["checks"])


def test_hash_commitment_and_duplicate_keys_reject(fixture):
    packet, task = fixture
    blob = encoded(packet)
    with pytest.raises(ValueError, match="commitment"):
        compiler.compile_source_packet(blob, task, expected_packet_sha256="0" * 64)
    duplicate = b'{"schema_version":1,"schema_version":2}'
    with pytest.raises(ValueError, match="Duplicate"):
        compiler.compile_source_packet(duplicate, task, expected_packet_sha256=hashlib.sha256(duplicate).hexdigest())


def test_missing_uncertainty_is_not_relabelled_as_ci(fixture):
    packet, task = fixture
    packet["constraint_candidates"][0]["uncertainty"] = {"kind": "not_reported", "role": "not_reported"}
    result = compile_packet(packet, task)
    context = result["source_context_templates"][0]
    assert context["semantics"]["bindings"][0]["uncertainty_role"] == "not_reported"
    assert context["supplement"]["checks"][0]["source"]["uncertainty_role"] == "not_reported"


@pytest.mark.parametrize("mutation", ["weights", "ci_to_sd", "fraction_relabel", "threshold_boundary", "event_denominator", "table_n", "quantile_activation", "regression_activation", "context_id", "source_unit", "analyte_id", "regression_doi"])
def test_semantic_changes_fail_before_any_output(fixture, mutation):
    packet, task = fixture
    first = packet["constraint_candidates"][0]
    proportion = next(r for r in packet["constraint_candidates"] if r["reported_statistic"] == "proportion")
    if mutation == "weights": first["admission"]["source_weighting"] = "none"
    elif mutation == "ci_to_sd": first["uncertainty"]["is_individual_dispersion"] = True
    elif mutation == "fraction_relabel": proportion["unit"] = "1"
    elif mutation == "threshold_boundary": proportion["operator"]["comparison"] = "le"
    elif mutation == "event_denominator": proportion["denominator"]["event_conditioned"] = True
    elif mutation == "table_n": first["denominator"]["reported_group_n"] = 5000
    elif mutation == "quantile_activation": packet["operator_definitions"]["reported_age_quantile"]["executable_recipe"] = {}
    elif mutation == "regression_activation": packet["contextual_regressions"][0]["numerical_calibration_allowed"] = True
    elif mutation == "context_id": first["population_ref"] = "uganda_women"
    elif mutation == "analyte_id":
        first["variable"] = first["operator"]["column"] = "hdl_cholesterol"
        first["unit"] = first["uncertainty"]["unit"] = "mmol/L"
        first["denominator"]["source_table"] = 2
    elif mutation == "regression_doi": packet["contextual_regressions"][0]["provenance"]["source_doi"] = "invented:different-source"
    else: task["columns"][4]["unit"] = "mg/dL"
    with pytest.raises(ValueError):
        compile_packet(packet, task)


def _write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def _review(value):
    return {"decision": "approved", "independent": True, "reviewer_id": "invented-fixture-reviewer", "producer_id": "invented-fixture-producer",
            "reviewed_utc": "2026-11-02T00:00:00Z", "reason": "Invented metadata validator fixture only", "approved_sha256": value}


def test_real_semantic_and_supplement_declaration_preflights_on_invented_metadata(fixture, tmp_path):
    packet, task = fixture
    result = compile_packet(packet, task)
    templates = compiler.bind_context_assumptions(result, {c: ["invented-context-assumption"] for c in compiler.CONTEXTS})
    for template in templates:
        root = tmp_path / template["id"]
        candidate = root / "candidates/invented"
        candidate.mkdir(parents=True)
        child_task = copy.deepcopy(task)
        child_task["population"] = template["recipe"]["population"]
        child_task["n_rows"] = 3
        _write(root / "task.json", child_task)
        _write(candidate / "evidence.json", result["evidence"])
        _write(candidate / "model_spec.json", {"parameters": {}, "parameter_provenance": {}, "assumptions": [{"id": "invented-context-assumption", "description": "Invented test context only"}]})
        _write(candidate / "whole_cohort_feedback.json", template["recipe"])
        sidecar = template["semantics"]
        sidecar.update(evidence_sha256=lifecycle.sha256(candidate / "evidence.json"), recipe_sha256=lifecycle.sha256(candidate / "whole_cohort_feedback.json"))
        _write(candidate / semantic.FILE, sidecar)
        gates = semantic.preflight(root, "invented")
        assert len(gates["checks"]) == 4 and all(c["semantic_status"] == "unavailable" for c in gates["checks"])
        declaration = template["supplement"]
        declaration.update(task_sha256=lifecycle.sha256(root / "task.json"), evidence_sha256=lifecycle.sha256(candidate / "evidence.json"),
                           model_spec_sha256=lifecycle.sha256(candidate / "model_spec.json"), semantics_sha256=lifecycle.sha256(candidate / semantic.FILE))
        declaration["context_review"] = _review(supplement.declaration_digest(declaration))
        _write(candidate / supplement.FILE, declaration)
        supplement._declaration(root, candidate, {"candidate_files": ["candidates/invented/" + supplement.FILE]}, "candidates/invented", child_task, gates)
        assert all(c["source"]["weights"] == "not_reported" and c["proxy"] is None for c in declaration["checks"])
    assert not list(tmp_path.rglob("freeze.json")) and not list(tmp_path.rglob("*.csv"))


def test_normalized_view_matches_exact_reference_input_contract_without_fit(fixture, monkeypatch):
    sys.path.insert(0, str(HERE.parent / "implementation"))
    import statistical_reference
    def forbidden(*args, **kwargs):
        pytest.fail("No source fit or sampling authorized")
    monkeypatch.setattr(statistical_reference, "fit_reference", forbidden)
    monkeypatch.setattr(statistical_reference, "sample", forbidden)
    result = compile_packet(*fixture)
    assert statistical_reference._validate_constraints(result["s01_normalized_constraints"]) == result["s01_normalized_constraints"]
