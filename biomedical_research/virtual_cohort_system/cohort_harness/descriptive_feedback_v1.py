"""Assumption-labelled descriptive diagnostics on verified whole-cohort output.

This additive interface never upgrades strict semantic feedback, reconstructs a
source population, executes a generator, or reads a target reference. A number,
a source-definition match, and population applicability are separate judgments.
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

from . import contracts, execution, semantic_feedback_v1 as strict
from . import source_checks, whole_cohort_feedback as legacy
from .contracts import exact_keys, require, string_list, text
from .lifecycle import _bundle, _path, read_json, read_table, sha256, verify_candidate

FILE = "descriptive_feedback_v1.json"
PLAN = FILE
FOLDER = "descriptive_feedback_v1"
KINDS = {"mean", "sd", "geometric_mean", "median", "quantile", "correlation", "spearman_correlation"}


def _surrogate(operator):
    # Reuse existing declarative validation, without altering the old operator.
    return {**operator, "kind": "mean"} if operator["kind"] == "geometric_mean" else operator


def _signature(operator):
    require(isinstance(operator, dict) and operator.get("kind") in KINDS,
            "Unsupported descriptive operator; categorical contrasts and OLS are not implemented")
    signature = json.loads(strict._signature(_surrogate(operator)))
    signature["kind"] = operator["kind"]
    return json.dumps(signature, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _conventions(operator):
    kind = operator["kind"] if operator else None
    return {"weighting": "equal", "sd_ddof": 1 if kind == "sd" else None,
            "quantile_method": "linear" if kind in {"median", "quantile"} else None,
            "spearman_ties": "average" if kind == "spearman_correlation" else None}


def _validate_conventions(conventions, operator):
    exact_keys(conventions, {"weighting", "sd_ddof", "quantile_method", "spearman_ties"},
               where="descriptive conventions")
    require(type(conventions["sd_ddof"]) in {int, type(None)}, "SD ddof cannot be Boolean")
    require(conventions == _conventions(operator), "Conventions must describe the implemented calculation")


def _evidence_mismatches(item, operator):
    """Compare machine-readable definitions; never guess from a narrative label."""
    reasons = []
    kind = item["kind"]
    if kind == "reported_other" and item.get("statistic_name") == "geometric_mean":
        kind = "geometric_mean"
    if operator["kind"] != kind:
        reasons.append("Evidence/calculation statistic kind mismatch: " + kind + " versus " + operator["kind"])
    if operator["unit"] != item["unit"]:
        reasons.append("Evidence/calculation statistic unit mismatch")
    primary = ({operator["x"], operator["y"]} if operator["kind"] in {"correlation", "spearman_correlation"}
               else {operator["column"]})
    if primary != set(item["variables"]):
        reasons.append("Evidence/calculation variable-role mismatch")
    if item["adjustment"]:
        reasons.append("Adjusted source statistic cannot be replaced by a marginal descriptive statistic")
    if kind == operator["kind"] == "quantile" and operator["q"] != item["q"]:
        reasons.append("Evidence/calculation quantile probability mismatch")
    if kind == operator["kind"] and kind in {"median", "quantile"}:
        if item["method"] not in {"not_reported", operator["method"]}:
            reasons.append("Evidence/calculation quantile method mismatch")
    return reasons


def _definition(check, item, columns):
    source, operator = check["source_definition"], check["operator"]
    exact_keys(source, {"definition_status", "source_operator", "weights", "transform",
                        "source_variable_units", "reason"}, {"conventions"}, where="source definition")
    require(source["definition_status"] in {"specified", "not_reported", "unsupported"},
            "Unknown source definition status")
    require(source["weights"] in {"none", "weighted", "not_reported"}, "Unknown source weighting")
    require(source["transform"] in {"identity", "nonidentity", "not_reported"}, "Unknown source transform")
    text(source["reason"], "source definition reason")
    units = source["source_variable_units"]
    require(isinstance(units, dict), "Source variable units must be a mapping")
    declared = source["source_operator"]
    mismatches, assumptions = [], []
    if source["definition_status"] == "specified":
        _signature(declared)
        names = strict._variables(_surrogate(declared))
        require(set(units) == names, "Source units must cover every source operand including selection")
        for unit in units.values():
            text(unit, "source variable unit")
        # Unit mismatches are visible scientific mismatches, not hidden by an assumption.
        try:
            strict._measurement(source, _surrogate(declared), columns)
            strict._task_operator(_surrogate(declared), columns)
        except ValueError as error:
            mismatches.append(str(error))
        mismatches.extend("Declared source: " + reason for reason in _evidence_mismatches(item, declared))
        if operator and _signature(declared) != _signature(operator):
            mismatches.append("Declared source/calculation operator mismatch (definition, selection or missingness)")
    else:
        require(declared is None and not units, "Unresolved source definition requires null operator and empty units")
        assumptions.append("Source operational conventions are " + source["definition_status"])
    if operator:
        mismatches.extend(_evidence_mismatches(item, operator))
    if source["weights"] == "weighted":
        mismatches.append("Weighted source estimator versus equal-weight descriptive calculation")
    elif source["weights"] == "not_reported":
        assumptions.append("Source weighting not reported; equal weights assumed for the diagnostic")
    if source["transform"] == "nonidentity":
        mismatches.append("Nonidentity source measurement has no implemented conversion")
    elif source["transform"] == "not_reported":
        assumptions.append("Source measurement mapping not reported; identity mapping assumed")
    if operator and operator["kind"] in {"median", "quantile"} and item.get("method") == "not_reported":
        assumptions.append("Source quantile interpolation not reported; linear interpolation assumed")
    if "conventions" in source:
        require(declared is not None, "Declared source conventions require a specified source operator")
        exact_keys(source["conventions"], set(_conventions(declared)), where="source conventions")
        require(type(source["conventions"]["sd_ddof"]) in {int, type(None)}, "Source SD ddof cannot be Boolean")
        if source["conventions"] != _conventions(declared):
            mismatches.append("Source calculation conventions differ from implemented conventions")
    elif operator and operator["kind"] in {"sd", "spearman_correlation"}:
        assumptions.append("Source SD degrees of freedom or rank-tie convention not explicitly bound")
    status = ("known_mismatch" if mismatches else "unsupported" if operator is None else
              "assumed_convention" if assumptions else "matched_declared")
    return {"status": status, "mismatches": mismatches, "assumptions": assumptions,
            "source_authenticity": "not_certified"}


def _preflight(root, directory):
    task = read_json(root / "task.json")
    contracts.validate_task(task)
    require(task["mode"] == "whole_cohort", "Descriptive feedback supports whole_cohort only")
    require(not _path(root, "observed.csv", file=False).exists(), "Observed input is forbidden")
    columns = {column["name"]: column for column in task["columns"]}
    evidence_document = read_json(directory / "evidence.json")
    evidence_ids = contracts.validate_evidence(evidence_document, task)
    spec = read_json(directory / "model_spec.json")
    contracts.validate_spec(spec, evidence_ids)
    assumptions = {item["id"] for item in spec["assumptions"]}
    evidence = {item["id"]: item for item in evidence_document["items"]}
    plan = read_json(_path(directory, FILE))
    exact_keys(plan, {"schema_version", "evidence_sha256", "checks"}, where=FILE)
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Invalid descriptive version")
    require(plan["evidence_sha256"] == sha256(directory / "evidence.json"), "Descriptive evidence hash mismatch")
    require(isinstance(plan["checks"], list) and bool(plan["checks"]), "Descriptive checks must be nonempty")
    ids, gates = set(), []
    for check in plan["checks"]:
        exact_keys(check, {"id", "evidence_id", "source_locator", "operator", "conventions", "source_definition",
                           "assumption_ids", "applicability", "reason"}, where="descriptive check")
        key = execution._name(check["id"])
        require(key.casefold() not in ids, "Duplicate descriptive check ID")
        ids.add(key.casefold())
        require(check["evidence_id"] in evidence, "Unknown descriptive evidence ID")
        item = evidence[check["evidence_id"]]
        require(check["source_locator"] == item["locator"], "Descriptive source locator mismatch")
        string_list(check["assumption_ids"], "descriptive assumptions", nonempty=True)
        require(set(check["assumption_ids"]) <= assumptions, "Unknown descriptive assumption")
        text(check["reason"], "descriptive reason")
        exact_keys(check["applicability"], {"status", "reason"}, where="descriptive applicability")
        require(check["applicability"]["status"] in {"explicit_transfer_assumption", "unsupported_target_claim"},
                "Source population is not replayed; applicability cannot be certified")
        text(check["applicability"]["reason"], "applicability reason")
        operator = check["operator"]
        if operator is not None:
            _signature(operator)
            strict._task_operator(_surrogate(operator), columns)
            calculation_units = {name: columns[name]["unit"] for name in strict._variables(_surrogate(operator))}
            strict._measurement({"source_variable_units": calculation_units, "transform": "identity"},
                                _surrogate(operator), columns)
        _validate_conventions(check["conventions"], operator)
        gates.append({"id": key, "evidence_id": item["id"],
                      "calculation_status": "ready" if operator else "not_requested",
                      "source_definition_match": _definition(check, item, columns),
                      "applicability": check["applicability"]})
    return task, plan, evidence, gates


def preflight(bundle, candidate):
    """Validate declarations only; no individual table or numerical calculation."""
    root = _bundle(bundle)
    directory, relative = legacy._resolve_candidate(root, candidate)
    _, _, _, gates = _preflight(root, directory)
    return {"schema_version": 1, "scope": "assumption_labelled_descriptive_source_feedback",
            "candidate": relative, "source_population_replayed": False, "checks": gates}


def apply_operator(frame, operator):
    """Use frozen core arithmetic plus an equal-weight positive geometric mean."""
    _signature(operator)
    if operator["kind"] != "geometric_mean":
        return source_checks.apply_operator(frame, operator)
    require(isinstance(frame, pd.DataFrame) and frame.columns.is_unique, "Expected unique-column table")
    selected = frame.copy(deep=False)
    for predicate in operator["selection"]:
        selected = selected.loc[source_checks.condition(selected, predicate)]
    column = operator["column"]
    require(column in selected.columns, "Unknown geometric-mean variable")
    missing = selected[column].isna()
    if operator["missing_policy"] == "error" and missing.any():
        raise source_checks.NotComputable("Missing geometric-mean values under error policy")
    used = selected.loc[~missing, column]
    if used.empty:
        raise source_checks.NotComputable("No complete selected rows")
    require(pd.api.types.is_numeric_dtype(used) and not pd.api.types.is_bool_dtype(used), "Numeric values required")
    values = used.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise source_checks.NotComputable("Geometric mean requires finite strictly positive values; no dropping or shifting")
    value = float(np.exp(np.log(values).mean()))
    if not source_checks.finite(value):
        raise source_checks.NotComputable("Nonfinite geometric mean")
    return {"value": value, "n_input": len(frame), "n_selected": len(selected), "n_used": len(used),
            "n_missing_dropped": int(missing.sum()), "unit": operator["unit"]}


def _uncertainty(item):
    original = item["uncertainty"]
    absent = {"kind": "not_reported"}
    return {"estimator_uncertainty": original if original["kind"] in {"se", "ci"} else absent,
            "unresolved_source_dispersion": original if original["kind"] == "sd" else absent,
            "monte_carlo_uncertainty": {"status": "not_estimated"}}


def _compute(root, directory, relative, run_id, feedback_id):
    frozen = verify_candidate(root, directory)
    require(relative + "/" + FILE in frozen["candidate_files"], "Descriptive plan must be frozen")
    task, plan, evidence, gates = _preflight(root, directory)
    receipt = execution.verify_execution(root, execution._name(run_id))
    require(receipt["candidate"] == relative, "Execution belongs to a different candidate")
    require(receipt["status"] == "success", "Descriptive feedback requires successful verified execution")
    require(receipt["route"] == frozen["route"], "Execution route mismatch")
    output = _path(root, f"executions/{run_id}/output/generated.csv")
    frame = read_table(output, task, output=True)
    records = []
    for check, gate in zip(plan["checks"], gates):
        item = evidence[check["evidence_id"]]
        row = {**gate, "source_id": item["source_id"], "source_locator": item["locator"],
               "operator": check["operator"], "conventions": check["conventions"],
               "source_definition": check["source_definition"], "assumption_ids": sorted(set(check["assumption_ids"])),
               "reason": check["reason"], "source_selection": item["selection"],
               "source_applicability": item["applicability"], "reported_value": item["estimate"],
               "reported_uncertainty": item["uncertainty"], **_uncertainty(item),
               "calculation": None, "difference": None, "unavailable_reason": None,
               "difference_interpretation": "descriptive_raw_difference_only_no_fit_or_validity_claim",
               "strict_feedback_promoted": False}
        if check["operator"] is None:
            row.update(calculation_status="cannot_compute", unavailable_reason=check["reason"])
        else:
            try:
                row["calculation"] = apply_operator(frame, check["operator"])
                row["calculation_status"] = "computed"
                if gate["source_definition_match"]["status"] in {"matched_declared", "assumed_convention"}:
                    difference = row["calculation"]["value"] - item["estimate"]
                    require(source_checks.finite(difference), "Nonfinite descriptive difference")
                    row["difference"] = difference
            except (ValueError, FloatingPointError) as error:
                row.update(calculation_status="cannot_compute", calculation=None, difference=None,
                           unavailable_reason=str(error))
        records.append(row)
    return {"schema_version": 1, "kind": "descriptive_whole_cohort_feedback_v1", "feedback_id": feedback_id,
            "candidate": relative, "run_id": run_id, "status": "complete", "route": frozen["route"],
            "output_link_verified": True, "generator_execution_recorded": receipt["generator_executed"],
            "agent_authorship_verified": False, "agent_isolation": "not_provided",
            "scientific_validity": "not_assessed", "source_context_validity": "not_certified",
            "source_population_replayed": False, "population": task["population"],
            "bindings": {"task_sha256": sha256(root / "task.json"),
                         "candidate_freeze_sha256": sha256(directory / "freeze.json"),
                         "plan_sha256": sha256(directory / FILE), "evidence_sha256": sha256(directory / "evidence.json"),
                         "model_spec_sha256": sha256(directory / "model_spec.json"),
                         "execution_receipt_sha256": sha256(root / f"executions/{run_id}/execution.json"),
                         "generated_table_sha256": sha256(output)},
            "engine_sha256": {**legacy._engine(), Path(strict.__file__).name: sha256(strict.__file__),
                              Path(__file__).name: sha256(__file__)},
            "calculator_runtime": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
            "checks": records, "n_computable": sum(row["calculation_status"] == "computed" for row in records),
            "n_not_computable": sum(row["calculation_status"] == "cannot_compute" for row in records),
            "n_known_mismatch": sum(row["source_definition_match"]["status"] == "known_mismatch" for row in records),
            "limitations": ["These calculations do not replace or upgrade separately retained strict semantic feedback.",
                            "No source population, selection variables, weights or assay conversion are reconstructed.",
                            "Matched declared definitions do not certify extraction or source applicability.",
                            "Source precision, individual dispersion, Monte Carlo and transport uncertainty are not pooled.",
                            "Overlapping checks or source populations are not independent validations.",
                            "No target reference, patient input, parameter fitting or generator execution is used by this collector.",
                            "Hash commitments are not signatures against host-side alteration."]}


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
    require([path.name for path in folder.iterdir()] == ["feedback.json"], "Feedback artifact set changed")
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


collect = collect_feedback
verify = verify_feedback


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "collect", "verify"))
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--candidate")
    parser.add_argument("--run-id")
    parser.add_argument("--feedback-id")
    args = parser.parse_args(argv)
    try:
        if args.action == "preflight":
            require(args.candidate, "preflight requires candidate")
            result = preflight(args.bundle, args.candidate)
        elif args.action == "collect":
            require(args.candidate and args.run_id and args.feedback_id, "collect requires candidate, run and feedback IDs")
            result = collect(args.bundle, args.candidate, args.run_id, args.feedback_id)
        else:
            require(args.feedback_id, "verify requires feedback ID")
            result = verify(args.bundle, args.feedback_id, candidate=args.candidate, run_id=args.run_id)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({"status": "error", "type": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
