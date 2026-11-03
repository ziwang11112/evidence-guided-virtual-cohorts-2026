"""Invented metadata fixtures plus explicitly permitted retained metadata only."""
import copy
import json
from pathlib import Path
import sys

import pytest

import qualified_author_preflight as preflight

WORKSPACE = preflight.PROJECT.parents[1]


@pytest.fixture
def payload():
    columns = [
        {"name": "age", "kind": "integer", "unit": "year", "role": "generated"},
        {"name": "female", "kind": "integer", "unit": "1", "role": "generated", "minimum": 0, "maximum": 1},
        {"name": "bmi", "kind": "number", "unit": "kg/m^2", "role": "generated"},
        {"name": "glucose", "kind": "number", "unit": "mmol/L", "role": "generated"},
        {"name": "hba1c", "kind": "number", "unit": "%", "role": "generated"},
    ]
    contexts, items = {}, []
    for context_id, kind in [("J", "ols_coefficient"), ("B", "correlation"), ("M", "spearman_correlation")]:
        source_id, evidence_id = "invented-source-" + context_id, "invented-evidence-" + context_id
        operator = {"kind": kind, "unit": "1", "selection": [], "missing_policy": "error"}
        variables, adjustment = ["glucose", "hba1c"], []
        mapping = {"kind": "identity"}
        aliases = []
        if context_id == "J":
            operator.update(outcome="HbA1c_IFCC", predictors=["age", "female", "bmi"], term="bmi", include_intercept=True, unit="mmol/mol/(kg/m^2)")
            variables, adjustment = ["HbA1c_IFCC", "bmi"], ["age", "female"]
            mapping = {"kind": "hba1c_ngsp_to_ifcc", "input_column": "HbA1c_percent", "output_column": "HbA1c_IFCC",
                       "ngsp_percent_per_ifcc": 0.1, "ngsp_percent_intercept": 2, "unit_evidence_id": "invented-unit",
                       "assumption_ids": ["invented-assumption"]}
            aliases = [{"source_name": "HbA1c_percent", "generated_name": "hba1c", "assumption_ids": ["invented-assumption"]}]
        else:
            operator.update(x="glucose", y="hba1c")
        item = {"id": evidence_id, "source_id": source_id, "kind": kind, "unit": operator["unit"], "variables": variables,
                "adjustment": adjustment, "estimate": 0.2}
        items.append(item)
        check_id = "invented-check-" + context_id
        check = {"id": "qualified-" + context_id, "evidence_id": evidence_id, "semantic_check_id": check_id,
                 "operator": operator, "measurement_mapping": mapping,
                 "source_relation": {"kind": "same_reported_functional_under_declared_assumptions", "assumed_weights": "equal",
                                     "assumption_ids": ["invented-assumption"], "unresolved_original_details": ["invented unknown weights"],
                                     "reason": "Invented metadata test; no source study or approval."}}
        contexts[context_id] = {"schema_version": 1, "bindings": {}, "context_role": "source", "context_id": context_id,
                               "population": "invented " + context_id, "measurement": "invented measurement",
                               "source_ids": [source_id], "assumption_ids": ["invented-assumption"], "column_aliases": aliases,
                               "checks": [check]}
    items.append({"id": "invented-unit", "kind": "contextual", "variables": ["HbA1c_percent", "HbA1c_IFCC"]})
    spec = {"assumptions": [{"id": "invented-assumption"}], "parameters": {"contexts": {
        key: {"population": value["population"], "measurement": value["measurement"]} for key, value in contexts.items()}}}
    return [{"columns": columns}, {"items": items}, spec, {"schema_version": 1, "contexts": contexts}]


def j(payload):
    return payload[-1]["contexts"]["J"]


def check(payload):
    return j(payload)["checks"][0]


def test_valid_metadata_is_immutable_and_not_approval(payload):
    original = copy.deepcopy(payload)
    report = preflight.preflight_metadata(*payload)
    assert report["status"] == "metadata_checks_passed"
    assert report["counts"] == {"contexts_visited": 3, "checks_visited": 3, "checks_passed": 3,
                                "checks_failed": 0, "checks_blocked": 0, "findings": 0}
    assert report["scientific_validity"] == report["lifecycle_approval"] == "not_assessed"
    assert payload == original


def test_all_contexts_and_exact_finding_locations(payload):
    for context in payload[-1]["contexts"].values():
        context["bindings"] = {"task_sha256": ""}
    check(payload)["measurement_mapping"]["input_column"] = "hba1c"
    report = preflight.preflight_metadata(*payload)
    assert report["counts"]["contexts_visited"] == 3
    assert report["counts"]["checks_visited"] == 3
    assert [row["json_pointer"] for row in report["findings"]] == [
        "/contexts/J/bindings", "/contexts/J/checks/0/measurement_mapping", "/contexts/B/bindings", "/contexts/M/bindings"]
    assert all(row["source_path"] == "memory:qualified_plan_v1.json" for row in report["findings"])


@pytest.mark.parametrize("mutation", ["chain", "collision", "unknown_assumption"])
def test_alias_failures_block_only_dependent_checks(payload, mutation):
    alias = j(payload)["column_aliases"][0]
    if mutation == "chain":
        j(payload)["column_aliases"].append({**alias, "source_name": "second", "generated_name": "HbA1c_percent"})
    elif mutation == "collision":
        alias["source_name"] = "age"
    else:
        alias["assumption_ids"] = ["absent"]
    report = preflight.preflight_metadata(*payload)
    assert report["findings"][0]["code"] == "column_aliases"
    assert report["counts"]["checks_blocked"] == 1
    assert report["counts"]["checks_passed"] == 2


@pytest.mark.parametrize("field,value", [("input_column", "hba1c"), ("unit_evidence_id", "absent"),
                                          ("ngsp_percent_per_ifcc", 0), ("ngsp_percent_intercept", float("nan")),
                                          ("kind", "invented_conversion")])
def test_mapping_contract_rejections(payload, field, value):
    check(payload)["measurement_mapping"][field] = value
    report = preflight.preflight_metadata(*payload)
    assert report["findings"][0]["code"] == "measurement_mapping"
    assert report["counts"]["checks_passed"] == 2


@pytest.mark.parametrize("field,value", [("include_intercept", False), ("unit", "1"), ("missing_policy", "complete_cases")])
def test_operator_contract_rejections(payload, field, value):
    check(payload)["operator"][field] = value
    report = preflight.preflight_metadata(*payload)
    assert report["findings"][0]["code"] == "operator_contract"


def test_shared_generated_operand_origin_is_rejected(payload):
    declaration = payload[-1]["contexts"]["B"]
    declaration["column_aliases"] = [{"source_name": "same_glucose", "generated_name": "glucose", "assumption_ids": ["invented-assumption"]}]
    declaration["checks"][0]["operator"]["y"] = "same_glucose"
    payload[1]["items"][1]["variables"] = ["glucose", "same_glucose"]
    report = preflight.preflight_metadata(*payload)
    assert any("same generated column" in row["message"] for row in report["findings"])


def test_null_operator_and_relation_do_not_claim_computability(payload):
    check(payload).update(operator=None, source_relation=None, measurement_mapping={"kind": "identity"})
    report = preflight.preflight_metadata(*payload)
    assert report["status"] == "metadata_checks_passed"
    assert "available" not in json.dumps(report)


@pytest.mark.parametrize("mutation", ["target_label", "wrong_id", "bad_context_shape"])
def test_context_shape_rejections_continue(payload, mutation):
    if mutation == "target_label":
        j(payload)["context_role"] = "target"
    elif mutation == "wrong_id":
        j(payload)["context_id"] = "wrong"
    elif mutation == "bad_context_shape":
        del j(payload)["measurement"]
    report = preflight.preflight_metadata(*payload)
    assert report["status"] == "failed"
    assert report["contexts"][-1]["context_id"] == "M"
    assert report["contexts"][-1]["status"] == "metadata_checks_passed"


def test_bad_supporting_metadata_has_its_own_file_location(payload):
    payload[0]["columns"].append(copy.deepcopy(payload[0]["columns"][0]))
    report = preflight.preflight_metadata(*payload)
    finding = report["findings"][0]
    assert finding["source_path"] == "memory:task.json"
    assert finding["json_pointer"] == "/columns"


def test_empty_contexts_do_not_pass_without_checks(payload):
    payload[-1]["contexts"] = {}
    report = preflight.preflight_metadata(*payload)
    assert report["status"] == "failed"
    assert report["counts"]["checks_visited"] == 0
    assert report["findings"][0]["code"] == "input_structure"
    assert "nonempty" in report["findings"][0]["message"]


@pytest.mark.parametrize("author,candidate,bindings", [("A01", "initial", 3), ("A01", "initial_interface", 0), ("A02", "initial_interface", 0)])
def test_readonly_retained_submission_regression(author, candidate, bindings):
    bundle = WORKSPACE / "evcDP" / author
    metadata, paths, before = preflight.load_metadata(bundle, candidate)
    original = copy.deepcopy(metadata)
    report = preflight.preflight_metadata(*metadata, source_paths=paths)
    assert report["status"] == "failed"
    assert report["counts"]["contexts_visited"] == 3
    assert report["counts"]["checks_visited"] == 4
    assert sum(row["code"] == "authored_bindings" for row in report["findings"]) == bindings
    assert sum(row["code"] == "measurement_mapping" for row in report["findings"]) == 2
    assert len(report["findings"]) == bindings + 2
    assert metadata == original
    assert {path: preflight.digest(path) for path in before} == before


@pytest.mark.parametrize("author", ["A01", "A02"])
def test_hypothetical_in_memory_native_alias_matches_released_pure_validator(author):
    metadata, paths, before = preflight.load_metadata(WORKSPACE / "evcDP" / author, "initial_interface")
    original = copy.deepcopy(metadata)
    task, evidence, spec, _ = metadata
    declaration = j(metadata)
    known = {assumption["id"] for assumption in spec["assumptions"]}
    items = {item["id"]: item for item in evidence["items"]}
    columns = {column["name"]: column for column in task["columns"]}
    alias_columns, _ = preflight.qualified._alias_contract(declaration["column_aliases"], columns, known)
    for current in declaration["checks"]:
        with pytest.raises(preflight.contracts.ContractError, match="two HbA1c representations"):
            preflight.qualified._mapping_contract(current["measurement_mapping"], current["operator"], alias_columns, items, known)
    hypothetical = copy.deepcopy(metadata)
    correction = j(hypothetical)
    correction["column_aliases"].append({"source_name": "HbA1c_percent", "generated_name": "hba1c",
                                          "assumption_ids": correction["checks"][0]["measurement_mapping"]["assumption_ids"][:]})
    for current in correction["checks"]:
        current["measurement_mapping"]["input_column"] = "HbA1c_percent"
    report = preflight.preflight_metadata(*hypothetical, source_paths=paths)
    assert report["status"] == "metadata_checks_passed"
    assert report["counts"]["checks_passed"] == 4
    alias_columns, _ = preflight.qualified._alias_contract(correction["column_aliases"], columns, known)
    for current in correction["checks"]:
        mapped = preflight.qualified._mapping_contract(current["measurement_mapping"], current["operator"], alias_columns, items, known)
        preflight.qualified._operator_contract(current["operator"], items[current["evidence_id"]], mapped)
    assert metadata == original
    assert {path: preflight.digest(path) for path in before} == before


def test_no_lifecycle_numerical_or_generator_access(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Metadata preflight reached a forbidden lifecycle/numerical operation")
    for name in ("_prepare", "_calculate", "compute_qualified_feedback", "read_table", "verify_candidate"):
        monkeypatch.setattr(preflight.qualified, name, forbidden)
    monkeypatch.setattr(preflight.semantic, "preflight", forbidden)
    monkeypatch.setattr(preflight.qualified.source_checks, "apply_operator", forbidden)
    reads = []
    original_read = Path.read_bytes
    def observed_read(path):
        reads.append(path.resolve())
        return original_read(path)
    monkeypatch.setattr(Path, "read_bytes", observed_read)
    modules = set(sys.modules)
    report = preflight.preflight(WORKSPACE / "evcDP/A01", "initial_interface")
    allowed = set(map(Path, report["input_sha256"])) | set(map(Path, report["dependency_sha256"]))
    assert set(reads) == allowed
    assert not any(path.name in {"generator.py", "freeze.json"} or path.suffix == ".csv" for path in reads)
    assert not any("generator" in name.lower() for name in set(sys.modules) - modules)


def test_cli_rejection_exit_and_path_traversal(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["preflight", "--bundle", str(WORKSPACE / "evcDP/A01"), "--candidate", "initial_interface"])
    assert preflight.main() == 1
    assert json.loads(capsys.readouterr().out)["counts"]["findings"] == 2
    with pytest.raises(preflight.contracts.ContractError, match="not a path"):
        preflight.load_metadata(WORKSPACE / "evcDP/A01", "../initial")
