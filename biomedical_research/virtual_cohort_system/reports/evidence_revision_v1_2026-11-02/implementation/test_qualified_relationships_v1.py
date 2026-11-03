"""Invented arrays and mocked process boundary; real freeze/receipt/v1 verification.

No submitted generator, WSL process, network, clinical rows or source study runs.
Receipt fixtures are invented. Compatibility tests read only existing E1 evidence
definitions and the canonical task schema, then use explicitly artificial arrays.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import socket
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent))
import qualified_relationships_v1 as qualified
from cohort_harness import execution, lifecycle, semantic_feedback_v1 as semantic


def invented_review(declaration):
    return {"decision": "approved", "independent": True, "reviewer_id": "invented-test-reviewer",
            "producer_id": "invented-test-producer", "reviewed_utc": "2026-11-02T00:00:00Z",
            "reason": "Artificial test approval only, not source interpretation approval",
            "approved_sha256": qualified.declaration_digest(declaration)}


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build(tmp_path, monkeypatch, *, frame_edit=None, role="source", generated_names=False):
    root = tmp_path / "invented"
    candidate = root / "candidates/context"
    candidate.mkdir(parents=True)
    (root / "sources").mkdir()
    artifact = root / "sources/invented.txt"
    artifact.write_text("All quantities and HbA1c conversion constants are invented for adapter tests.\n", encoding="utf-8")
    artifact_hash = lifecycle.sha256(artifact)
    task = {"schema_version": 1, "task_id": "invented-source-relationships", "mode": "whole_cohort",
            "population": "Invented eligible source population", "row_id": "id", "n_rows": 8,
            "columns": [{"name": "id", "kind": "string", "unit": "1", "role": "identifier", "nullable": False}],
            "information_policy": {"mode": "published_evidence", "excluded_cohorts": ["forbidden-target"], "allowed_tools": []},
            "budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0}}
    for name, unit in [("age", "year"), ("x", "kg/m^2"), ("z", "mmol/L"), ("HbA1c_percent", "%")]:
        task["columns"].append({"name": name, "kind": "number", "unit": unit, "role": "generated", "nullable": False})
    task["columns"].append({"name": "gender_binary", "kind": "category", "categories": [0, 1], "unit": "1", "role": "generated", "nullable": False})
    renames = {"x": "generated_x", "z": "generated_z", "gender_binary": "female", "HbA1c_percent": "hba1c"} if generated_names else {}
    for column in task["columns"]:
        column["name"] = renames.get(column["name"], column["name"])
        if generated_names and column["name"] == "female":
            column.pop("categories")
            column.update(kind="integer", minimum=0, maximum=1)
    source = {"id": "invented-source", "identifier": "invented:relationships", "population": task["population"],
              "measurement": "Invented measurement and explicitly fictional unit equation",
              "cohort_ids": ["invented-source"], "artifacts": [{"path": "sources/invented.txt", "sha256": artifact_hash}]}
    operators = []
    for term, unit in [("x", "mmol/mol/(kg/m^2)"), ("z", "mmol/mol/(mmol/L)")]:
        operators.append({"kind": "ols_coefficient", "outcome": "HbA1c_IFCC", "predictors": ["age", "gender_binary", term],
                          "term": term, "include_intercept": True, "unit": unit, "selection": [], "missing_policy": "error"})
    for kind in ("correlation", "spearman_correlation"):
        operators.append({"kind": kind, "x": "x", "y": "HbA1c_percent", "unit": "1", "selection": [], "missing_policy": "error"})
    items, checks, bindings, qualified_checks = [], [], [], []
    estimates = [4.0, 5.0, 4 / math.sqrt(47.25), 24 / math.sqrt(1344)]
    for index, (operator, estimate) in enumerate(zip(operators, estimates)):
        identifier = "relationship-" + str(index)
        ols = operator["kind"] == "ols_coefficient"
        item = {"id": identifier, "source_id": source["id"], "locator": "Invented functional " + str(index),
                "variables": [operator["outcome"], operator["term"]] if ols else [operator["x"], operator["y"]],
                "kind": operator["kind"], "estimate": estimate, "unit": operator["unit"],
                "uncertainty": {"kind": "not_reported"}, "adjustment": ["age", "gender_binary"] if ols else [],
                "selection": "Entire invented source table", "applicability": "Invented arithmetic fixture only"}
        items.append(item)
        checks.append({"id": identifier, "evidence_id": identifier, "status": "not_computable", "operator": None,
                       "assumption_ids": ["fixture"], "reason": "Original estimator conventions are unresolved"})
        bindings.append({"check_id": identifier, "evidence_id": identifier, "source_locator": item["locator"],
                         "definition_status": "not_reported", "source_operator": None, "weights": "not_reported",
                         "transform": "identity", "source_variable_units": {}, "source_n": {"status": "not_reported"},
                         "uncertainty_role": "not_reported", "reason": "Unknown original conventions preserved"})
        mapping = {"kind": "hba1c_ngsp_to_ifcc", "input_column": "HbA1c_percent", "output_column": "HbA1c_IFCC",
                   "ngsp_percent_per_ifcc": 2.0, "ngsp_percent_intercept": 10.0, "unit_evidence_id": "invented-units",
                   "assumption_ids": ["fixture"]} if ols else {"kind": "identity"}
        qualified_checks.append({"id": "qualified-" + str(index), "evidence_id": identifier, "semantic_check_id": identifier,
                                 "operator": operator, "measurement_mapping": mapping,
                                 "source_relation": {"kind": "same_reported_functional_under_declared_assumptions", "assumed_weights": "equal",
                                                     "assumption_ids": ["fixture"], "unresolved_original_details": ["original weights and preprocessing"],
                                                     "reason": "Invented equal-weight complete-value comparison"}})
    items.append({"id": "invented-units", "source_id": source["id"], "locator": "Invented unit equation",
                  "variables": ["HbA1c_percent", "HbA1c_IFCC"], "kind": "contextual", "estimate": None, "unit": "",
                  "uncertainty": {"kind": "not_reported"}, "adjustment": [], "selection": "Unit guidance only",
                  "applicability": "Invented equation percent = 2 IFCC + 10; not a clinical conversion"})
    evidence = {"schema_version": 1, "sources": [source], "items": items}
    spec = {"parameters": {"active_context": "invented-source", "contexts": {"invented-source": {
                "population": task["population"], "measurement": source["measurement"], "n_rows": 8, "inputs": {}}}},
            "assumptions": [{"id": "fixture", "description": "All context and equation values are invented"}],
            "parameter_provenance": {key: {"evidence_ids": [], "assumption_ids": ["fixture"], "derivation": "Invented test"}
                                     for key in ("active_context", "contexts")}}
    recipe = {"schema_version": 1, "population": task["population"], "measurement": {"mode": "identity", "description": source["measurement"]},
              "assumption_ids": ["fixture"], "checks": checks}
    plan = {"contexts": [{"id": "invented-source", "role": role, "source_ids": [source["id"]]}]}
    for path, data in [(root / "task.json", task), (root / "registry.json", {"artifacts": [{"source_id": source["id"], "path": "sources/invented.txt",
                       "sha256": artifact_hash, "origin": "fixture", "screening": "approved"}]}),
                       (candidate / "evidence.json", evidence), (candidate / "model_spec.json", spec),
                       (candidate / qualified.BRIDGE_PLAN, plan), (candidate / semantic.legacy.PLAN, recipe),
                       (candidate / "checks.json", {"scope": "fixture_only", "records": [{"name": "fixture", "status": "not_computable", "detail": "No real execution"}], "artifacts": []})]:
        write(path, data)
    sidecar = {"schema_version": 1, "evidence_sha256": lifecycle.sha256(candidate / "evidence.json"),
               "recipe_sha256": lifecycle.sha256(candidate / semantic.legacy.PLAN), "bindings": bindings}
    write(candidate / semantic.FILE, sidecar)
    (candidate / "generator.py").write_text("def generate(observed, spec, seed):\n    raise RuntimeError('This invented generator must never run')\n", encoding="utf-8")
    (candidate / "decision.md").write_text("Invented source fixture, not biomedical evidence.\n", encoding="utf-8")
    lifecycle.freeze_candidate(root, candidate)
    frame = pd.DataFrame({"id": ["invented-" + str(index) for index in range(8)], "age": [29] * 4 + [31] * 4,
                          "x": [1, -1] * 4, "z": [1, 1, -1, -1, -1, -1, 1, 1], "gender_binary": [0, 0, 1, 1] * 2})
    native = 20 + 2 * (frame.age - 30) + 3 * frame.gender_binary + 4 * frame.x + 5 * frame.z
    frame["HbA1c_percent"] = 2 * native + 10
    frame = frame.rename(columns=renames)
    frame = frame[[column["name"] for column in task["columns"]]]
    if frame_edit:
        frame_edit(frame)
    for owner, name in [(subprocess, "run"), (subprocess, "Popen"), (socket, "create_connection")]:
        monkeypatch.setattr(owner, name, lambda *args, **kwargs: pytest.fail("Real process/network forbidden in invented tests"))
    monkeypatch.setattr(execution, "_runtime_manifest", lambda runtime: {"fixture": "No runtime inspected"})
    def capture(command, cwd, timeout, limit, stdout_path, stderr_path):
        frame.to_csv(cwd / "output/generated.csv", index=False)
        write(cwd / "output/worker_report.json", {"status": "completed", "generator_started": True})
        stdout_path.write_text("Invented process boundary, no generator executed\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return {"returncode": 0, "host_timeout": False, "logs": {}}
    monkeypatch.setattr(execution, "_capture", capture)
    execution.run_candidate(root, "candidates/context", "invented-run", 17)
    semantic.collect_feedback(root, "context", "invented-run", "invented-strict")
    paths = {"task_sha256": root / "task.json", "candidate_freeze_sha256": candidate / "freeze.json",
             "evidence_sha256": candidate / "evidence.json", "model_spec_sha256": candidate / "model_spec.json",
             "semantics_sha256": candidate / semantic.FILE, "bridge_plan_sha256": candidate / qualified.BRIDGE_PLAN}
    declaration = {"schema_version": 1, "bindings": {key: lifecycle.sha256(path) for key, path in paths.items()},
                   "context_role": "source", "context_id": "invented-source", "population": task["population"],
                   "measurement": source["measurement"], "source_ids": [source["id"]], "assumption_ids": ["fixture"],
                   "column_aliases": [{"source_name": source_name, "generated_name": generated_name, "assumption_ids": ["fixture"]}
                                      for source_name, generated_name in renames.items()],
                   "checks": qualified_checks}
    return root, declaration


def compute(root, declaration, review=None):
    return qualified.compute_qualified_feedback(root, "context", "invented-run", "invented-strict", declaration,
                                                invented_review(declaration) if review is None else review)


def test_actual_receipts_native_separate_slopes_pearson_spearman_and_no_writes(tmp_path, monkeypatch):
    root, declaration = build(tmp_path, monkeypatch)
    before = {path.relative_to(root).as_posix(): lifecycle.sha256(path) for path in root.rglob("*") if path.is_file()}
    report = compute(root, declaration)
    assert report["n_available"] == 4 and report["exact_source_check_allowed"] is False
    assert [row["calculation"]["value"] for row in report["checks"]] == pytest.approx([4, 5, 4 / math.sqrt(47.25), 24 / math.sqrt(1344)])
    assert all(abs(row["raw_difference"]) < 1e-10 for row in report["checks"])
    assert all(row["original_source_weights"] == "not_reported" and row["strict_result"]["difference"] is None for row in report["checks"])
    assert report["checks"][2]["calculation"]["value"] != report["checks"][3]["calculation"]["value"]
    assert before == {path.relative_to(root).as_posix(): lifecycle.sha256(path) for path in root.rglob("*") if path.is_file()}


@pytest.mark.parametrize("mutation", ["weights", "joint", "no_intercept", "selection", "missing", "unit", "wrong_source", "wrong_context", "target_label", "bad_mapping", "bad_unit_evidence", "stale_hash", "true_schema"])
def test_rejects_changed_semantics_or_scope_before_qualified_arithmetic(tmp_path, monkeypatch, mutation):
    root, declaration = build(tmp_path, monkeypatch)
    check = declaration["checks"][0]
    if mutation == "weights": check["source_relation"]["assumed_weights"] = "unknown"
    elif mutation == "joint": check["operator"]["predictors"].append("z")
    elif mutation == "no_intercept": check["operator"]["include_intercept"] = False
    elif mutation == "selection": check["operator"]["selection"] = [{"column": "x", "op": "gt", "value": 0}]
    elif mutation == "missing": check["operator"]["missing_policy"] = "complete_cases"
    elif mutation == "unit": check["operator"]["unit"] = "%/kg/m^2"
    elif mutation == "wrong_source": declaration["source_ids"] = ["different-source"]
    elif mutation == "wrong_context": declaration["context_id"] = "other-context"
    elif mutation == "target_label": declaration["context_role"] = "target"
    elif mutation == "bad_mapping": check["measurement_mapping"]["kind"] = "arbitrary_affine"
    elif mutation == "bad_unit_evidence": check["measurement_mapping"]["unit_evidence_id"] = "relationship-0"
    elif mutation == "stale_hash": declaration["bindings"]["evidence_sha256"] = "0" * 64
    else: declaration["schema_version"] = True
    monkeypatch.setattr(qualified, "_calculate", lambda *args: pytest.fail("Rejected declaration reached arithmetic"))
    with pytest.raises(ValueError): compute(root, declaration)


def test_target_cannot_be_relabelled_as_source(tmp_path, monkeypatch):
    root, declaration = build(tmp_path, monkeypatch, role="target")
    with pytest.raises(ValueError, match="Target context"):
        compute(root, declaration)


@pytest.mark.parametrize("missing", ["relation", "operator"])
def test_unavailable_details_stay_unavailable(tmp_path, monkeypatch, missing):
    root, declaration = build(tmp_path, monkeypatch)
    if missing == "relation":
        declaration["checks"][0]["source_relation"] = None
    else:
        declaration["checks"][0]["operator"] = None
        declaration["checks"][0]["measurement_mapping"] = {"kind": "identity"}
    row = compute(root, declaration)["checks"][0]
    assert row["status"] == "unavailable" and row["calculation"] is None and row["raw_difference"] is None


@pytest.mark.parametrize("edit", [lambda frame: frame.__setitem__("x", 1), lambda frame: frame.__setitem__("gender_binary", 0)])
def test_degenerate_source_values_report_unavailable_without_repair(tmp_path, monkeypatch, edit):
    root, declaration = build(tmp_path, monkeypatch, frame_edit=edit)
    row = compute(root, declaration)["checks"][0]
    assert row["status"] == "unavailable" and row["raw_difference"] is None


def test_binary_nuisance_relabelling_preserves_focal_slopes(tmp_path, monkeypatch):
    root, declaration = build(tmp_path, monkeypatch, frame_edit=lambda frame: frame.__setitem__("gender_binary", 1 - frame.gender_binary))
    report = compute(root, declaration)
    assert [row["calculation"]["value"] for row in report["checks"][:2]] == pytest.approx([4, 5])


def test_finite_extreme_values_fail_only_affected_checks(tmp_path, monkeypatch):
    def extreme_focal(frame):
        frame["x"] = frame["x"] * 1e308
    root, declaration = build(tmp_path, monkeypatch, frame_edit=extreme_focal)
    with np.errstate(over="ignore", invalid="ignore"):
        report = compute(root, declaration)
    assert report["checks"][1]["calculation"]["value"] == pytest.approx(5)
    assert report["checks"][3]["calculation"]["value"] == pytest.approx(24 / math.sqrt(1344))
    row = report["checks"][2]
    assert row["status"] == "unavailable" and row["raw_difference"] is None
    assert "nonfinite" in row["unavailable_reason"]


@pytest.mark.parametrize("tamper", ["output", "strict", "candidate", "review", "self_review"])
def test_tampered_retained_artifacts_or_review_rejected(tmp_path, monkeypatch, tamper):
    root, declaration = build(tmp_path, monkeypatch)
    review = invented_review(declaration)
    if tamper == "review": review["approved_sha256"] = "0" * 64
    elif tamper == "self_review": review["reviewer_id"] = "  INVENTED-TEST-PRODUCER  "
    elif tamper == "output":
        with (root / "executions/invented-run/output/generated.csv").open("a", encoding="utf-8") as stream: stream.write("\n")
    elif tamper == "candidate":
        with (root / "candidates/context/generator.py").open("a", encoding="utf-8") as stream: stream.write("# changed\n")
    else:
        path = root / semantic.FOLDER / "invented-strict/feedback.json"
        value = lifecycle.read_json(path)
        value["schema_version"] = True
        write(path, value)
    with pytest.raises(ValueError): compute(root, declaration, review)


def test_real_verification_entrypoints_are_required(tmp_path, monkeypatch):
    root, declaration = build(tmp_path, monkeypatch)
    execution_calls, semantic_calls = [], []
    original_execution, original_semantic = execution.verify_execution, semantic.verify_feedback
    def checked_execution(*args, **kwargs):
        execution_calls.append(True)
        return original_execution(*args, **kwargs)
    def checked_semantic(*args, **kwargs):
        semantic_calls.append(True)
        return original_semantic(*args, **kwargs)
    monkeypatch.setattr(execution, "verify_execution", checked_execution)
    monkeypatch.setattr(semantic, "verify_feedback", checked_semantic)
    compute(root, declaration)
    assert execution_calls and semantic_calls


def test_aliases_and_explicit_binary_integer_work_through_real_receipts(tmp_path, monkeypatch):
    root, declaration = build(tmp_path, monkeypatch, generated_names=True)
    before = {path.relative_to(root).as_posix(): lifecycle.sha256(path) for path in root.rglob("*") if path.is_file()}
    report = compute(root, declaration)
    assert report["n_available"] == 4
    assert [row["calculation"]["value"] for row in report["checks"]] == pytest.approx([4, 5, 4 / math.sqrt(47.25), 24 / math.sqrt(1344)])
    assert report["declaration"]["column_aliases"] == declaration["column_aliases"]
    assert before == {path.relative_to(root).as_posix(): lifecycle.sha256(path) for path in root.rglob("*") if path.is_file()}


@pytest.mark.parametrize("mutation", ["overwrite", "duplicate", "chain", "unknown", "nonnumeric", "no_assumption", "extra_unit", "shared_operand"])
def test_aliases_reject_ambiguous_or_unreviewed_views(tmp_path, monkeypatch, mutation):
    root, declaration = build(tmp_path, monkeypatch, generated_names=True)
    aliases = declaration["column_aliases"]
    if mutation == "overwrite": aliases[0]["source_name"] = "age"
    elif mutation == "duplicate": aliases.append(copy.deepcopy(aliases[0]))
    elif mutation == "chain": aliases[1]["generated_name"] = aliases[0]["source_name"]
    elif mutation == "unknown": aliases[0]["generated_name"] = "missing"
    elif mutation == "nonnumeric": aliases[0]["generated_name"] = "id"
    elif mutation == "no_assumption": aliases[0]["assumption_ids"] = []
    elif mutation == "extra_unit": aliases[0]["unit"] = "new_unit"
    else:
        declaration["checks"] = [declaration["checks"][2]]
        aliases[0]["generated_name"] = "hba1c"
    monkeypatch.setattr(qualified, "_calculate", lambda *args: pytest.fail("Rejected aliases reached arithmetic"))
    with pytest.raises(ValueError): compute(root, declaration)


def test_binary_integer_alias_still_requires_both_observed_groups(tmp_path, monkeypatch):
    root, declaration = build(tmp_path, monkeypatch, generated_names=True, frame_edit=lambda frame: frame.__setitem__("female", 0))
    report = compute(root, declaration)
    assert all(row["status"] == "unavailable" and "both declared" in row["unavailable_reason"] for row in report["checks"][:2])
    assert all(row["status"] == "available" for row in report["checks"][2:])


def test_alias_change_requires_new_independent_review(tmp_path, monkeypatch):
    root, declaration = build(tmp_path, monkeypatch, generated_names=True)
    review = invented_review(declaration)
    declaration["column_aliases"][0]["generated_name"] = "generated_z"
    with pytest.raises(ValueError, match="review commitment"):
        compute(root, declaration, review)


def test_existing_e1_definitions_and_canonical_schema_on_artificial_arrays():
    project = Path(__file__).resolve().parents[3]
    implementation = project / "work/existing_data_benchmark_2026-11-02/implementation"
    if not implementation.is_dir():
        implementation = project / "reports/existing_data_benchmark_2026-11-02/implementation"
    task_path = implementation / "task.json"
    evidence_path = implementation / "compiled/E1/evidence.json"
    before = [lifecycle.sha256(path) for path in (task_path, evidence_path)]
    task, evidence = lifecycle.read_json(task_path), lifecycle.read_json(evidence_path)
    items = {item["id"]: item for item in evidence["items"]}
    original_columns = {column["name"]: column for column in task["columns"]}
    aliases = [{"source_name": source, "generated_name": generated, "assumption_ids": ["synthetic-compatibility"]}
               for source, generated in [("gender_binary", "female"), ("BMI", "bmi"), ("FPG", "glucose"),
                                         ("FSG", "glucose"), ("HbA1c_percent", "hba1c")]]
    columns, origins = qualified._alias_contract(aliases, original_columns, {"synthetic-compatibility"})
    for alias in aliases:
        original = original_columns[alias["generated_name"]]
        assert columns[alias["source_name"]] == {**original, "name": alias["source_name"]}
    assert origins["FPG"] == origins["FSG"] == "glucose"
    assert qualified._binary_column(columns["gender_binary"])
    assert not qualified._binary_column({**columns["gender_binary"], "maximum": 2})
    assert not qualified._binary_column({**columns["gender_binary"], "kind": "number"})
    # Eight arbitrary rows: no participant data and no source generator call.
    frame = pd.DataFrame({"row_id": ["artificial-" + str(index) for index in range(8)], "age": [49] * 4 + [51] * 4,
                          "female": [0, 0, 1, 1] * 2, "bmi": [26, 24] * 4, "glucose": [6, 6, 4, 4, 4, 4, 6, 6]})
    native = 50 + 2 * (frame.age - 50) + 3 * frame.female + 4 * (frame.bmi - 25) + 5 * (frame.glucose - 5)
    frame["hba1c"] = 0.09148 * native + 2.152
    view = frame.assign(**{alias["source_name"]: frame[alias["generated_name"]] for alias in aliases})
    calculated = []
    for evidence_id in ("R_JANSEN_BMI", "R_JANSEN_FPG", "R_BAO_PEARSON", "R_MIND_SPEARMAN"):
        item = items[evidence_id]
        if item["kind"] == "ols_coefficient":
            term = "BMI" if evidence_id == "R_JANSEN_BMI" else "FPG"
            operator = {"kind": "ols_coefficient", "outcome": "HbA1c_IFCC", "predictors": ["age", "gender_binary", term],
                        "term": term, "include_intercept": True, "unit": item["unit"], "selection": [], "missing_policy": "error"}
            mapping = {"kind": "hba1c_ngsp_to_ifcc", "input_column": "HbA1c_percent", "output_column": "HbA1c_IFCC",
                       "ngsp_percent_per_ifcc": 0.09148, "ngsp_percent_intercept": 2.152,
                       "unit_evidence_id": "U_NGSP_SCALE", "assumption_ids": ["synthetic-compatibility"]}
        else:
            operator = {"kind": item["kind"], "x": "FPG" if evidence_id == "R_BAO_PEARSON" else "FSG",
                        "y": "HbA1c_percent", "unit": item["unit"], "selection": [], "missing_policy": "error"}
            mapping = {"kind": "identity"}
        mapped_columns = qualified._mapping_contract(mapping, operator, columns, items, {"synthetic-compatibility"})
        qualified._operator_contract(operator, item, mapped_columns)
        calculated.append(qualified._calculate(view, {"operator": operator, "measurement_mapping": mapping}, columns)["value"])
    assert calculated == pytest.approx([4, 5, 5 / math.sqrt(47.25), 24 / math.sqrt(1344)])
    assert "HbA1c_IFCC" not in frame and "HbA1c_IFCC" not in view
    assert list(frame.columns) == [column["name"] for column in task["columns"]]
    assert [lifecycle.sha256(path) for path in (task_path, evidence_path)] == before
