"""Versioned semantic gate for whole-cohort source feedback.

Checks consistency with declared source semantics, not correctness of extraction
or population transport. Legacy collectors and frozen receipts are unchanged.
No generator is executed. Unsupported source estimators produce no discrepancy.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd

from . import contracts, execution, source_checks, whole_cohort_feedback as legacy
from .contracts import exact_keys, require, text
from .lifecycle import _bundle, _path, read_json, read_table, sha256, verify_candidate
from .source_checks import NotComputable, apply_operator, finite

FILE = "source_semantics_v1.json"
FOLDER = "semantic_feedback_v1"
_KINDS = {
    "mean": {"column"}, "sd": {"column"}, "median": {"column", "method"},
    "quantile": {"column", "q", "method"}, "correlation": {"x", "y"},
    "spearman_correlation": {"x", "y"},
    "ols_coefficient": {"outcome", "predictors", "term", "include_intercept"},
    "proportion": {"event"},
}


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _predicate(spec):
    exact_keys(spec, {"column", "op", "value"}, where="semantic predicate")
    text(spec["column"], "predicate column")
    require(spec["op"] in {"eq", "ne", "lt", "le", "gt", "ge", "in"}, "Unsupported semantic predicate")
    value = spec["value"]
    values = value if spec["op"] == "in" else [value]
    require(isinstance(values, list) and bool(values), "Predicate requires values")
    require(all(type(v) in {str, int, float} and (type(v) not in {int, float} or finite(v))
                for v in values), "Predicate values must be finite typed scalars")
    # Task contracts have no Boolean type; never coerce True into numeric 1.
    encoded = sorted({_json(v) for v in values}) if spec["op"] == "in" else _json(value)
    return (spec["column"], spec["op"], encoded)


def _signature(operator):
    require(isinstance(operator, dict), "Source operator must be an object")
    kind = operator.get("kind")
    require(kind in _KINDS, "Source operator kind unsupported")
    exact_keys(operator, {"kind", "unit", "selection", "missing_policy"} | _KINDS[kind],
               where="semantic operator")
    text(operator["unit"], "semantic unit")
    require(operator["missing_policy"] in {"error", "complete_cases"}, "Missing policy must be explicit")
    require(isinstance(operator["selection"], list), "Selection must be a conjunction list")
    normalized = dict(operator)
    normalized["selection"] = sorted(_json(_predicate(p)) for p in operator["selection"])
    if kind in {"mean", "sd", "median", "quantile"}:
        text(operator["column"], "source variable")
    elif kind in {"correlation", "spearman_correlation"}:
        for key in ("x", "y"):
            text(operator[key], "source correlation variable")
        require(operator["x"] != operator["y"], "Correlation requires distinct variables")
        normalized["x"], normalized["y"] = sorted((operator["x"], operator["y"]))
    elif kind == "ols_coefficient":
        predictors = operator["predictors"]
        contracts.string_list(predictors, "source predictors", nonempty=True)
        require(len(set(predictors)) == len(predictors), "Duplicate source predictors")
        text(operator["outcome"], "source outcome")
        text(operator["term"], "source coefficient")
        require(operator["outcome"] not in predictors and "intercept" not in predictors,
                "Invalid source outcome/predictor roles")
        require(operator["term"] in predictors, "v1 supports non-intercept source coefficients only")
        require(type(operator["include_intercept"]) is bool, "Source intercept must be Boolean")
        normalized["predictors"] = sorted(predictors)
    else:
        normalized["event"] = _predicate(operator["event"])
        require(operator["unit"] in {"1", "%"}, "Invalid proportion unit")
    if kind in {"median", "quantile"}:
        require(operator["method"] == "linear", "Unsupported source quantile convention")
    if kind == "quantile":
        require(finite(operator["q"]) and 0 <= operator["q"] <= 1, "Invalid source quantile probability")
    if kind in {"correlation", "spearman_correlation"}:
        require(operator["unit"] == "1", "Correlation unit must be 1")
    return _json(normalized)


def _variables(operator):
    """All operands, including selection and denominator predicates."""
    names = {p["column"] for p in operator["selection"]}
    kind = operator["kind"]
    if kind in {"mean", "sd", "median", "quantile"}:
        names.add(operator["column"])
    elif kind in {"correlation", "spearman_correlation"}:
        names.update((operator["x"], operator["y"]))
    elif kind == "ols_coefficient":
        names.update([operator["outcome"], *operator["predictors"]])
    else:
        names.add(operator["event"]["column"])
    return names


def _measurement(binding, operator, task_columns):
    units = binding["source_variable_units"]
    require(isinstance(units, dict), "Source variable units must be an explicit mapping")
    if operator is None:
        require(not units, "Unresolved source operator must have empty variable units")
        return
    names = _variables(operator)
    require(names <= set(task_columns), "Source operator references unknown task columns")
    require(set(units) == names, "Source variable units must cover all operands including selection")
    for name, unit in units.items():
        text(unit, "source variable unit")
        if binding["transform"] == "identity":
            require(unit == task_columns[name]["unit"], "Source/task variable unit mismatch under identity")
    kind = operator["kind"]
    if kind in {"mean", "sd", "median", "quantile"}:
        require(operator["unit"] == units[operator["column"]], "Source statistic/variable unit mismatch")
    elif kind == "ols_coefficient":
        numerator, denominator = units[operator["outcome"]], units[operator["term"]]
        allowed = {numerator + "/" + denominator}
        if denominator == "1":
            allowed.add(numerator)
        if numerator == denominator:
            allowed.add("1")
        require(operator["unit"] in allowed, "v1 supports only explicit per-unit unstandardized OLS coefficients")


def _task_operator(operator, columns):
    """Reject known operand/type mismatches without inspecting table values."""
    require(_variables(operator) <= set(columns), "Recipe references unknown task columns")
    def numeric(column):
        return column["kind"] in {"number", "integer"} or (
            column["kind"] == "category" and all(type(v) in {int, float} for v in column["categories"]))
    predicates = list(operator["selection"])
    if operator["kind"] == "proportion":
        predicates.append(operator["event"])
    for predicate in predicates:
        column = columns[predicate["column"]]
        values = predicate["value"] if predicate["op"] == "in" else [predicate["value"]]
        allowed = {int, float} if numeric(column) else {str}
        require(all(type(v) in allowed for v in values), "Predicate/task column type mismatch under identity")
    if operator["kind"] != "proportion":
        # Filter-only columns need not be numeric, but all statistical operands must be.
        operands = _variables({**operator, "selection": []})
        require(all(numeric(columns[name]) for name in operands), "Statistic requires numeric task operands")


def _bind_evidence(item, operator):
    require(operator["kind"] == item["kind"], "Source estimand/evidence kind mismatch")
    require(operator["unit"] == item["unit"], "Source estimand/evidence unit mismatch")
    source_checks.check_statistic_definition(item, operator, approximate=True)
    kind = operator["kind"]
    if kind == "ols_coefficient":
        primary = {operator["outcome"], operator["term"]}
        adjustment = set(operator["predictors"]) - {operator["term"]}
        require(adjustment == set(item["adjustment"]), "Source estimand/evidence adjustment mismatch")
    else:
        require(not item["adjustment"], "Adjusted non-regression statistic is unsupported")
        if kind in {"mean", "sd", "median", "quantile"}:
            primary = {operator["column"]}
        elif kind in {"correlation", "spearman_correlation"}:
            primary = {operator["x"], operator["y"]}
        else:
            primary = {operator["event"]["column"]}
    require(primary == set(item["variables"]), "Source estimand/evidence variable-role mismatch")


def _uncertainty(binding, item):
    n = binding["source_n"]
    require(isinstance(n, dict), "Source n must be an object")
    if n.get("status") == "not_reported":
        exact_keys(n, {"status"}, where="source n")
    else:
        exact_keys(n, {"status", "value", "scope"}, where="source n")
        require(n["status"] == "reported" and type(n["value"]) is int and n["value"] > 0,
                "Source n must be a positive integer")
        text(n["scope"], "source n analysis population")
    original, role = item["uncertainty"], binding["uncertainty_role"]
    kind = original["kind"]
    allowed = {"not_reported": {"not_reported"}, "se": {"estimate"}, "ci": {"estimate"},
               "sd": {"individual_dispersion", "unresolved"}}
    require(role in allowed[kind], "Source uncertainty role cannot reinterpret SD as estimator precision")
    missing = {"kind": "not_reported"}
    return {
        "estimator_uncertainty": original if role == "estimate" else dict(missing),
        "individual_dispersion": original if role == "individual_dispersion" else dict(missing),
        "unresolved_source_uncertainty": original if role == "unresolved" else dict(missing),
        "monte_carlo_uncertainty": {"status": "not_estimated"},
    }


def _preflight(root, directory):
    task = read_json(root / "task.json")
    contracts.validate_task(task)
    require(task["mode"] == "whole_cohort", "Semantic feedback supports whole_cohort only")
    task_columns = {column["name"]: column for column in task["columns"]}
    evidence_document = read_json(directory / "evidence.json")
    evidence_ids = contracts.validate_evidence(evidence_document, task)
    contracts.validate_spec(read_json(directory / "model_spec.json"), evidence_ids)
    plan, evidence = legacy._read_plan(directory, task)  # Structural validation only, no arithmetic.
    sidecar = read_json(_path(directory, FILE))
    exact_keys(sidecar, {"schema_version", "evidence_sha256", "recipe_sha256", "bindings"}, where=FILE)
    require(type(sidecar["schema_version"]) is int and sidecar["schema_version"] == 1, "Invalid semantic version")
    require(sidecar["evidence_sha256"] == sha256(directory / "evidence.json"), "Semantic evidence hash mismatch")
    require(sidecar["recipe_sha256"] == sha256(directory / legacy.PLAN), "Semantic recipe hash mismatch")
    require(isinstance(sidecar["bindings"], list), "Semantic bindings must be a list")
    bindings = {}
    for binding in sidecar["bindings"]:
        exact_keys(binding, {"check_id", "evidence_id", "source_locator", "definition_status", "source_operator",
                            "weights", "transform", "source_variable_units", "source_n", "uncertainty_role", "reason"}, where="semantic binding")
        execution._name(binding["check_id"])
        require(binding["check_id"] not in bindings, "Duplicate semantic binding")
        text(binding["reason"], "semantic reason")
        require(binding["weights"] in {"none", "weighted", "not_reported"}, "Unknown weighting declaration")
        require(binding["transform"] in {"identity", "nonidentity", "not_reported"}, "Unknown transform declaration")
        bindings[binding["check_id"]] = binding
    require(set(bindings) == {check["id"] for check in plan["checks"]}, "Semantic bindings must cover every check exactly")
    gates = []
    for check in plan["checks"]:
        binding = bindings[check["id"]]
        item = evidence[check["evidence_id"]]
        require(binding["evidence_id"] == check["evidence_id"], "Semantic evidence ID mismatch")
        require(binding["source_locator"] == item["locator"], "Semantic source locator mismatch")
        uncertainty = _uncertainty(binding, item)
        definition = binding["definition_status"]
        require(definition in {"specified", "not_reported", "unsupported"}, "Unknown definition status")
        unavailable = []
        if check["operator"] is not None:
            _signature(check["operator"])
            _task_operator(check["operator"], task_columns)
        if definition != "specified":
            require(binding["source_operator"] is None, "Unresolved source definition must have null operator")
            _measurement(binding, None, task_columns)
            unavailable.append("Source definition " + definition + ": " + binding["reason"])
        else:
            declared = binding["source_operator"]
            signature = _signature(declared)
            _measurement(binding, declared, task_columns)
            _bind_evidence(item, declared)
            if check["operator"] is not None:
                require(signature == _signature(check["operator"]),
                        "Source/operator semantic mismatch (roles, coefficient, adjustment, selection, denominator or definition)")
            if item["kind"] in {"median", "quantile"} and item["method"] == "not_reported":
                unavailable.append("Source quantile interpolation not reported")
        if binding["weights"] != "none":
            unavailable.append("Weighted or unknown source estimator is not implemented")
        if binding["transform"] != "identity":
            unavailable.append("Nonidentity or unknown source transform is not implemented")
        if check["status"] == "not_computable":
            unavailable.append(check["reason"])
        gates.append({"id": check["id"], "evidence_id": item["id"], "semantics": binding,
                      "semantic_status": "unavailable" if unavailable else "matched_declared",
                      "unavailable_reason": "; ".join(unavailable) if unavailable else None, **uncertainty})
    return task, plan, evidence, gates


def preflight(bundle, candidate):
    """Check the sidecar/recipe before freezing; never reads individual tables."""
    root = _bundle(bundle)
    directory, relative = legacy._resolve_candidate(root, candidate)
    _, _, _, gates = _preflight(root, directory)
    return {"schema_version": 1, "scope": "declared_source_semantics_only", "candidate": relative,
            "checks": gates, "source_authenticity": "not_certified", "source_applicability": "not_certified"}


def _compute(root, directory, relative, run_id, feedback_id):
    frozen = verify_candidate(root, directory)
    require(relative + "/" + FILE in frozen["candidate_files"], "Semantic sidecar must be frozen")
    # Validate the complete recipe before calling ANY numerical source operator.
    task, plan, evidence, gates = _preflight(root, directory)
    receipt = execution.verify_execution(root, execution._name(run_id))
    require(receipt["candidate"] == relative, "Execution belongs to a different candidate")
    require(receipt["status"] == "success", "Feedback requires a successful verified execution")
    require(receipt["route"] == frozen["route"], "Execution route mismatch")
    output = _path(root, f"executions/{run_id}/output/generated.csv")
    frame = read_table(output, task, output=True)
    records = []
    for check, gate in zip(plan["checks"], gates):
        item = evidence[check["evidence_id"]]
        row = {**gate, "source_id": item["source_id"], "declared_status": check["status"],
               "status": check["status"], "operator": check["operator"], "reason": check["reason"],
               "assumption_ids": sorted(set(plan["assumption_ids"]) | set(check["assumption_ids"])),
               "reported_value": item["estimate"], "reported_uncertainty": item["uncertainty"],
               "calculation": None, "difference": None, "difference_interpretation": "unstandardized_raw_discrepancy_only"}
        if gate["semantic_status"] == "unavailable":
            row["status"] = "not_computable"
        else:
            try:
                row["calculation"] = apply_operator(frame, check["operator"])
                row["difference"] = row["calculation"]["value"] - item["estimate"]
                require(finite(row["difference"]), "Feedback difference is nonfinite")
            except NotComputable as error:
                row.update(status="not_computable", unavailable_reason=str(error))
        records.append(row)
    return {
        "schema_version": 1, "kind": "semantic_whole_cohort_feedback_v1", "feedback_id": feedback_id,
        "candidate": relative, "run_id": run_id, "status": "complete", "route": frozen["route"],
        "output_link_verified": True, "generator_execution_recorded": receipt["generator_executed"],
        "agent_authorship_verified": False, "agent_isolation": "not_provided", "scientific_validity": "not_assessed",
        "source_context_validity": "not_certified", "population": task["population"], "measurement": plan["measurement"],
        "bindings": {"task_sha256": sha256(root / "task.json"), "candidate_freeze_sha256": sha256(directory / "freeze.json"),
                     "recipe_sha256": sha256(directory / legacy.PLAN), "evidence_sha256": sha256(directory / "evidence.json"),
                     "semantics_sha256": sha256(directory / FILE), "model_spec_sha256": sha256(directory / "model_spec.json"),
                     "execution_receipt_sha256": sha256(root / f"executions/{run_id}/execution.json"),
                     "generated_table_sha256": sha256(output)},
        "engine_sha256": {**legacy._engine(), Path(__file__).name: sha256(__file__)},
        "calculator_runtime": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
        "checks": records, "n_computable": sum(r["calculation"] is not None for r in records),
        "n_not_computable": sum(r["status"] == "not_computable" for r in records),
        "limitations": ["Bindings test declared semantics, not faithful extraction or source applicability.",
                        "No source-population reconstruction, weighting, measurement conversion or generator execution occurs.",
                        "Source precision, individual variation, Monte Carlo and transport uncertainty are not pooled.",
                        "Legacy entrypoints remain unchanged; new controllers must explicitly use v1 without fallback.",
                        "Hash commitments are not signatures against host-side alteration."],
    }


def collect_feedback(bundle, candidate, run_id, feedback_id):
    root = _bundle(bundle)
    directory, relative = legacy._resolve_candidate(root, candidate)
    feedback_id = execution._name(feedback_id)
    destination = _path(root, f"{FOLDER}/{feedback_id}", file=False)
    require(not destination.exists(), "Feedback ID already exists")
    report = _compute(root, directory, relative, run_id, feedback_id)
    report["created_utc"] = datetime.now(timezone.utc).isoformat()
    destination.parent.mkdir(exist_ok=True)
    destination.mkdir()
    execution._write(destination / "feedback.json", report)
    return verify_feedback(root, feedback_id, candidate=relative, run_id=run_id)


def verify_feedback(bundle, feedback_id, *, candidate=None, run_id=None):
    root = _bundle(bundle)
    feedback_id = execution._name(feedback_id)
    folder = _path(root, f"{FOLDER}/{feedback_id}", file=False)
    require([p.name for p in folder.iterdir()] == ["feedback.json"], "Feedback artifact set changed")
    report = read_json(_path(folder, "feedback.json"))
    directory, relative = legacy._resolve_candidate(root, report["candidate"])
    if candidate is not None:
        require(legacy._resolve_candidate(root, candidate)[1] == relative, "Wrong feedback candidate")
    if run_id is not None:
        require(report["run_id"] == execution._name(run_id), "Wrong feedback execution")
    text(report.get("created_utc"), "feedback timestamp")
    expected = _compute(root, directory, relative, report["run_id"], feedback_id)
    expected["created_utc"] = report["created_utc"]
    require(report == expected, "Feedback report changed or no longer matches recomputed diagnostics")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "collect", "verify"))
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--feedback-id")
    args = parser.parse_args(argv)
    try:
        if args.action == "preflight":
            result = preflight(args.bundle, args.candidate)
        else:
            require(args.run_id and args.feedback_id, "collect/verify require run and feedback IDs")
            if args.action == "collect":
                result = collect_feedback(args.bundle, args.candidate, args.run_id, args.feedback_id)
            else:
                result = verify_feedback(args.bundle, args.feedback_id, candidate=args.candidate, run_id=args.run_id)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({"status": "error", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
