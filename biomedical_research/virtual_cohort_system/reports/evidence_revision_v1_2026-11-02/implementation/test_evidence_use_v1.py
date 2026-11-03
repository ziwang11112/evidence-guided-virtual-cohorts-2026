"""Invented metadata only: no real source files, rows, or generator execution."""
from copy import deepcopy
import json

import pytest

from evidence_use_v1 import assess_evidence_use, canonical_json_sha256


def declaration():
    evidence = {
        "schema_version": 1,
        "sources": [{"id": "S1", "identifier": "synthetic source", "population": "invented adults",
                     "measurement": "invented assay", "cohort_ids": ["invented cohort"],
                     "artifacts": [{"path": "synthetic.txt", "sha256": "a" * 64}]}],
        "items": [{"id": "E1", "source_id": "S1", "locator": "invented table 1",
                   "variables": ["x", "y"], "kind": "correlation", "estimate": 0.2,
                   "unit": "1", "uncertainty": {"kind": "not_reported"}, "adjustment": [],
                   "selection": "invented eligibility", "applicability": "unknown transfer"},
                  {"id": "E2", "source_id": "S1", "locator": "invented unit guidance",
                   "variables": [], "kind": "contextual", "estimate": None, "unit": "",
                   "uncertainty": {"kind": "not_reported"}, "adjustment": [],
                   "selection": "invented eligibility", "applicability": "context only"}],
    }
    spec = {
        "parameters": {"shared": {"association": 0.1}, "contexts": {"source": {"offset": 0.0}}},
        "assumptions": [{"id": "A1", "description": "Joint source distribution is assumed."}],
        "parameter_provenance": {
            "shared": {"evidence_ids": ["E1"], "assumption_ids": ["A1"], "derivation": "declared choice"},
            "contexts": {"evidence_ids": [], "assumption_ids": ["A1"], "derivation": "source context assumption"}},
    }
    records = []
    for item in evidence["items"]:
        records.append({"evidence_id": item["id"], "role": "unused",
                        "source_reference": {"source_id": "S1",
                                             "source_sha256": canonical_json_sha256(evidence["sources"][0]),
                                             "item_sha256": canonical_json_sha256(item)},
                        "context_id": None, "check_ids": [], "parameter_names": [],
                        "structure_names": [], "code_references": [], "assumption_ids": [],
                        "gaps": [], "rationale": "No supported numerical role is claimed.",
                        "source_comparison": "not_applicable"})
    records[0].update(role="qualified_numerical_comparison", context_id="source",
                      check_ids=["source_pearson"], parameter_names=["shared"],
                      code_references=[{"path": "generator.py", "symbol": "sample_source"}],
                      assumption_ids=["A1"], source_comparison="qualified",
                      gaps=[{"id": "G1", "dimension": "joint_distribution",
                             "description": "Source joint covariate law is unavailable.",
                             "assumption_ids": ["A1"]}])
    return {"schema_version": 1, "evidence_sha256": canonical_json_sha256(evidence),
            "items": records}, evidence, spec


def test_qualified_report_never_certifies_execution_or_source_fidelity():
    manifest, evidence, spec = declaration()
    originals = deepcopy((manifest, evidence, spec))
    report = assess_evidence_use(manifest, evidence, spec, recipe_check_ids=["source_pearson"])
    assert report["declaration_valid"] is True
    assert report["recipe_check_membership_verified"] is True
    assert report["scope"] == "declarations_and_references_only"
    assert report["executed_uptake"] == report["source_fidelity"] == "not_verified"
    assert report["verification_needed"]
    assert all(row["executed_uptake"] == row["source_fidelity"] == "not_verified" for row in report["items"])
    assert json.loads(json.dumps(report, allow_nan=False)) == report
    assert (manifest, evidence, spec) == originals


def test_no_numerical_constraints_are_forced():
    manifest, evidence, spec = declaration()
    record = manifest["items"][0]
    record.update(role="qualitative_context", context_id=None, check_ids=[], source_comparison="not_applicable")
    report = assess_evidence_use(manifest, evidence, spec)
    assert report["declaration_valid"]
    assert [row["declared_role"] for row in report["items"]] == ["qualitative_context", "unused"]
    assert report["recipe_check_membership_verified"] is False


def test_strict_declaration_still_needs_external_verification():
    manifest, evidence, spec = declaration()
    manifest["items"][0].update(role="numerical_constraint", assumption_ids=[], gaps=[],
                                source_comparison="declared_strict")
    report = assess_evidence_use(manifest, evidence, spec)
    assert report["declaration_valid"]
    assert report["source_fidelity"] == "not_verified"


def test_structure_only_numeric_use_can_name_a_global_code_symbol():
    manifest, evidence, spec = declaration()
    manifest["items"][0].update(parameter_names=[], structure_names=["sample_source"])
    report = assess_evidence_use(manifest, evidence, spec)
    assert report["items"][0]["structure_names"] == ["sample_source"]


def test_each_item_has_independent_parameter_and_code_references():
    manifest, evidence, spec = declaration()
    manifest["items"][1].update(role="qualitative_context", parameter_names=["contexts"],
                                code_references=[{"path": "mapping.py", "symbol": "convert_units"}])
    report = assess_evidence_use(manifest, evidence, spec)
    assert report["items"][0]["parameter_names"] == ["shared"]
    assert report["items"][1]["parameter_names"] == ["contexts"]


@pytest.mark.parametrize("field,value,message", [
    ("parameter_names", ["shared", "shared"], "Duplicate parameter names"),
    ("parameter_names", ["shared.association"], "Unknown parameter names"),
    ("assumption_ids", ["A1", "A1"], "Duplicate assumption IDs"),
    ("assumption_ids", ["A_missing"], "Unknown assumption IDs"),
    ("assumption_ids", [], "Unknown gap assumption IDs"),
    ("check_ids", ["source_pearson", "source_pearson"], "Duplicate check IDs"),
    ("check_ids", [], "requires check IDs"),
    ("code_references", [], "requires code references"),
    ("code_references", [{"path": "g.py", "symbol": "s"}] * 2, "Duplicate code reference"),
    ("parameter_names", [], "requires parameter or structure"),
    ("structure_names", ["unknown_symbol"], "Unknown structure names"),
    ("context_id", None, "numeric context ID"),
    ("rationale", " ", "rationale must be nonempty"),
    ("source_comparison", "declared_strict", "cannot claim strict source replay"),
    ("role", "verified_numerical_uptake", "Unknown evidence-use role"),
])
def test_invalid_numeric_declarations(field, value, message):
    manifest, evidence, spec = declaration()
    manifest["items"][0][field] = value
    with pytest.raises(ValueError, match=message):
        assess_evidence_use(manifest, evidence, spec)


def test_qualified_comparison_requires_assumptions_even_without_gap_records():
    manifest, evidence, spec = declaration()
    manifest["items"][0].update(assumption_ids=[], gaps=[])
    with pytest.raises(ValueError, match="Qualified use requires explicit assumptions"):
        assess_evidence_use(manifest, evidence, spec)


@pytest.mark.parametrize("keep_assumptions", [False, True])
def test_strict_comparison_cannot_hide_gaps_or_assumptions(keep_assumptions):
    manifest, evidence, spec = declaration()
    record = manifest["items"][0]
    record.update(role="numerical_constraint", source_comparison="declared_strict")
    if keep_assumptions:
        record["gaps"] = []
    else:
        record["assumption_ids"] = []
        record["gaps"][0]["assumption_ids"] = []
    with pytest.raises(ValueError, match="Strict source comparison cannot hide"):
        assess_evidence_use(manifest, evidence, spec)


@pytest.mark.parametrize("change,message", [("missing", "Missing admitted"),
                                            ("duplicate", "Duplicate evidence-use ID"),
                                            ("unknown", "Unknown evidence-use ID")])
def test_exact_coverage_of_admitted_evidence(change, message):
    manifest, evidence, spec = declaration()
    if change == "missing":
        manifest["items"].pop()
    elif change == "duplicate":
        manifest["items"].append(deepcopy(manifest["items"][0]))
    else:
        manifest["items"][1]["evidence_id"] = "not_admitted"
    with pytest.raises(ValueError, match=message):
        assess_evidence_use(manifest, evidence, spec)


@pytest.mark.parametrize("field", ["source_sha256", "item_sha256"])
def test_exact_metadata_binding_cannot_be_replaced(field):
    manifest, evidence, spec = declaration()
    manifest["items"][0]["source_reference"][field] = "b" * 64
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        assess_evidence_use(manifest, evidence, spec)


def test_changing_source_selection_requires_a_new_canonical_commitment():
    manifest, evidence, spec = declaration()
    evidence["items"][0]["selection"] = "different selection"
    with pytest.raises(ValueError, match="canonical evidence SHA-256 mismatch"):
        assess_evidence_use(manifest, evidence, spec)


def test_recipe_membership_does_not_accept_unknown_checks():
    manifest, evidence, spec = declaration()
    with pytest.raises(ValueError, match="Unknown check IDs"):
        assess_evidence_use(manifest, evidence, spec, recipe_check_ids=["different_check"])


def test_recipe_check_list_rejects_duplicate_references():
    manifest, evidence, spec = declaration()
    with pytest.raises(ValueError, match="Duplicate recipe check IDs"):
        assess_evidence_use(manifest, evidence, spec, recipe_check_ids=["source_pearson"] * 2)


def test_checks_cannot_be_bound_to_two_evidence_items():
    manifest, evidence, spec = declaration()
    manifest["items"][1]["check_ids"] = ["source_pearson"]
    with pytest.raises(ValueError, match="Duplicate check reference across evidence items"):
        assess_evidence_use(manifest, evidence, spec)


def test_context_only_source_cannot_be_promoted_to_a_numeric_constraint():
    manifest, evidence, spec = declaration()
    numeric = deepcopy(manifest["items"][0])
    numeric.update(evidence_id="E2", source_reference=manifest["items"][1]["source_reference"],
                   check_ids=["invented_numeric_check"])
    manifest["items"][1] = numeric
    with pytest.raises(ValueError, match="requires a numerical evidence estimate"):
        assess_evidence_use(manifest, evidence, spec)


def test_unused_record_cannot_claim_parameter_influence():
    manifest, evidence, spec = declaration()
    manifest["items"][1]["parameter_names"] = ["contexts"]
    with pytest.raises(ValueError, match="Unused evidence cannot claim model influence"):
        assess_evidence_use(manifest, evidence, spec)


def test_gap_assumptions_must_be_local_and_declared():
    manifest, evidence, spec = declaration()
    manifest["items"][0]["gaps"][0]["assumption_ids"] = ["A_missing"]
    with pytest.raises(ValueError, match="Unknown gap assumption IDs"):
        assess_evidence_use(manifest, evidence, spec)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), {1: "bad key"}, (1, 2)])
def test_hash_input_rejects_non_json_or_nonfinite_values(value):
    with pytest.raises(ValueError):
        canonical_json_sha256(value)


def test_canonical_hash_is_not_raw_file_hash():
    assert canonical_json_sha256({"a": 1, "b": 2}) == canonical_json_sha256({"b": 2, "a": 1})


def test_malformed_input_is_value_error_and_cannot_inject_execution_claims():
    manifest, evidence, spec = declaration()
    manifest["items"][0]["executed_uptake"] = True
    with pytest.raises(ValueError, match="unknown fields"):
        assess_evidence_use(manifest, evidence, spec)
    with pytest.raises(ValueError):
        assess_evidence_use([], evidence, spec)
