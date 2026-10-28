"""Compute declared source statistics without importing Agent-written code.

Submitted tables are *not* certified to have come from the generator. This
milestone checks statistical operators and content binding, not execution or
target validity. No expected biological relationship is encoded here.
"""
from __future__ import annotations

import hashlib
import csv
import math
import sys
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd

from .contracts import validate_evidence, validate_spec
from .lifecycle import read_json


class NotComputable(ValueError):
    """A valid operator cannot be estimated from the supplied rows."""


def require(ok, message):
    if not ok:
        raise ValueError(message)


def exact_keys(obj, required, optional=()):
    require(isinstance(obj, dict), "Expected an object")
    require(set(required) <= obj.keys(), "Missing fields: " + str(set(required) - obj.keys()))
    require(obj.keys() <= set(required) | set(optional), "Unexpected fields: " + str(obj.keys() - set(required) - set(optional)))


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def bound_file(root, relative):
    root = Path(root).resolve()
    require(isinstance(relative, str) and relative and "\\" not in relative and ":" not in relative,
            "Use a portable relative path")
    rel = PurePosixPath(relative)
    require(not rel.is_absolute() and all(x not in (".", "..") for x in rel.parts), "Unsafe relative path")
    path = root.joinpath(*rel.parts)
    for ancestor in [path, *path.parents]:
        if ancestor == root:
            break
        require(not ancestor.is_symlink() and not (hasattr(ancestor, "is_junction") and ancestor.is_junction()),
                "Linked source-table path rejected")
    require(path.resolve().is_relative_to(root) and path.is_file(), "Source table must be inside candidate")
    return path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def condition(frame, spec):
    exact_keys(spec, ("column", "op", "value"))
    column, op, value = spec["column"], spec["op"], spec["value"]
    require(column in frame.columns, "Unknown filter column: " + str(column))
    require(op in {"eq", "ne", "lt", "le", "gt", "ge", "in"}, "Unsupported filter operation")
    series = frame[column]
    if op == "in":
        require(isinstance(value, list) and value, "in filter requires nonempty values")
        mask = series.isin(value)
    else:
        require(not isinstance(value, (dict, list)) and value is not None, "Filter requires a scalar")
        if isinstance(value, (int, float)):
            require(finite(value), "Nonfinite filter value")
        methods = {"eq": "eq", "ne": "ne", "lt": "lt", "le": "le", "gt": "gt", "ge": "ge"}
        mask = getattr(series, methods[op])(value)
    return mask.fillna(False) & series.notna()


def apply_operator(frame, operator):
    """Return value and row accounting; invalid inputs fail rather than drop silently."""
    require(isinstance(frame, pd.DataFrame) and frame.columns.is_unique, "Expected table with unique columns")
    exact_keys(operator, ("kind", "unit", "selection", "missing_policy"),
               ("column", "x", "y", "outcome", "predictors", "term", "include_intercept", "event"))
    kind = operator["kind"]
    require(kind in {"mean", "sd", "correlation", "ols_coefficient", "proportion"}, "Operator not implemented")
    require(isinstance(operator["unit"], str) and operator["unit"].strip(), "Unit label required")
    require(operator["missing_policy"] in {"error", "complete_cases"}, "Explicit missing policy required")
    require(isinstance(operator["selection"], list), "Selection must be a list")
    base_fields = {"kind", "unit", "selection", "missing_policy"}
    fields = {"mean": {"column"}, "sd": {"column"}, "correlation": {"x", "y"},
              "ols_coefficient": {"outcome", "predictors", "term", "include_intercept"}, "proportion": {"event"}}[kind]
    require(set(operator) == base_fields | fields, "Operator fields do not match its kind")
    selected = frame.copy(deep=False)
    for selection in operator["selection"]:
        selected = selected.loc[condition(selected, selection)]
    if kind in {"mean", "sd"}:
        columns = [operator["column"]]
    elif kind == "correlation":
        columns = [operator["x"], operator["y"]]
        require(columns[0] != columns[1], "Correlation requires distinct variables")
    elif kind == "ols_coefficient":
        predictors = operator["predictors"]
        require(isinstance(predictors, list) and predictors and len(set(predictors)) == len(predictors),
                "OLS needs distinct predictors")
        require(type(operator["include_intercept"]) is bool, "include_intercept must be boolean")
        require(operator["outcome"] not in predictors and "intercept" not in predictors,
                "OLS outcome/intercept cannot be a predictor")
        columns = [operator["outcome"], *predictors]
    else:
        exact_keys(operator["event"], ("column", "op", "value"))
        columns = [operator["event"]["column"]]
        require(operator["unit"] in {"1", "%"}, "Proportion unit must be 1 or %")
    require(all(isinstance(c, str) and c in selected.columns for c in columns), "Unknown operator variable")
    missing = selected[columns].isna().any(axis=1)
    if operator["missing_policy"] == "error":
        require(not missing.any(), "Missing operator values; no implicit complete-case deletion")
    used = selected.loc[~missing]
    if used.empty:
        raise NotComputable("No complete selected rows")
    if kind != "proportion":
        require(all(pd.api.types.is_numeric_dtype(used[c]) and not pd.api.types.is_bool_dtype(used[c]) for c in columns),
                "Numeric columns required; no implicit encoding")
        require(np.isfinite(used[columns].to_numpy(dtype=float)).all(), "Nonfinite numeric source values")
    else:
        for col in columns:
            if pd.api.types.is_numeric_dtype(used[col]):
                require(np.isfinite(used[col].to_numpy(dtype=float)).all(), "Nonfinite event values")
    if kind == "mean":
        value = float(used[columns[0]].mean())
    elif kind == "sd":
        if len(used) < 2:
            raise NotComputable("Sample SD requires at least two rows")
        value = float(used[columns[0]].std(ddof=1))
    elif kind == "correlation":
        if len(used) < 2 or any(used[c].std(ddof=1) == 0 for c in columns):
            raise NotComputable("Pearson correlation requires nonconstant variables")
        value = float(np.corrcoef(used[columns].to_numpy(dtype=float), rowvar=False)[0, 1])
    elif kind == "ols_coefficient":
        matrix = used[operator["predictors"]].to_numpy(dtype=float)
        terms = list(operator["predictors"])
        if operator["include_intercept"]:
            matrix = np.column_stack([np.ones(len(used)), matrix])
            terms = ["intercept", *terms]
        require(operator["term"] in terms, "Unknown OLS coefficient term")
        if len(used) <= matrix.shape[1] or np.linalg.matrix_rank(matrix) != matrix.shape[1]:
            raise NotComputable("OLS requires residual degrees of freedom and full rank")
        beta = np.linalg.lstsq(matrix, used[operator["outcome"]].to_numpy(dtype=float), rcond=None)[0]
        value = float(beta[terms.index(operator["term"])])
    else:
        value = float(condition(used, operator["event"]).mean())
        if operator["unit"] == "%":
            value *= 100
    require(finite(value), "Operator returned nonfinite value")
    return {"value": value, "n_input": len(frame), "n_selected": len(selected), "n_used": len(used),
            "n_missing_dropped": int(missing.sum()), "unit": operator["unit"]}


def run_source_checks(bundle, candidate):
    """Evaluate source_checks.json; does not write files or execute a generator."""
    bundle, candidate = Path(bundle).resolve(), Path(candidate).resolve()
    require(candidate.is_relative_to(bundle / "candidates"), "Candidate outside bundle/candidates")
    read = read_json
    plan = read(candidate / "source_checks.json")
    evidence, spec = read(candidate / "evidence.json"), read(candidate / "model_spec.json")
    evidence_ids = validate_evidence(evidence, read(bundle / "task.json"))
    validate_spec(spec, evidence_ids)
    exact_keys(plan, ("schema_version", "checks"))
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1 and isinstance(plan["checks"], list),
            "Invalid source-check plan")
    evidence_by_id = {e["id"]: e for e in evidence["items"]}
    assumptions = {a["id"] for a in spec["assumptions"]}
    records, used_ids = [], set()
    for check in plan["checks"]:
        exact_keys(check, ("id", "evidence_id", "status", "table", "operator", "assumption_ids", "reason"))
        require(isinstance(check["id"], str) and check["id"] and check["id"] not in used_ids, "Duplicate/invalid check ID")
        used_ids.add(check["id"])
        require(check["evidence_id"] in evidence_by_id, "Unknown source-check evidence ID")
        require(check["status"] in {"computed", "approximate", "not_computable"}, "Invalid source-check status")
        require(isinstance(check["reason"], str) and check["reason"].strip(), "Check context/reason required")
        require(isinstance(check["assumption_ids"], list) and set(check["assumption_ids"]) <= assumptions,
                "Unknown check assumption")
        if check["status"] == "approximate":
            require(check["assumption_ids"], "Approximate source replay must name its assumptions")
        if check["status"] == "computed":
            require(not check["assumption_ids"], "Checks relying on bridge assumptions must be approximate")
        record = {k: check[k] for k in ("id", "evidence_id", "status", "assumption_ids", "reason")}
        if check["status"] == "not_computable":
            require(check["table"] is None and check["operator"] is None, "Not-computable checks must not claim execution")
            records.append(record)
            continue
        table = check["table"]
        exact_keys(table, ("path", "sha256", "origin"))
        require(table["origin"] in {"fixture", "agent_supplied_simulation"}, "Unknown simulated-table origin")
        path = bound_file(candidate, table["path"])
        require(sha(path) == table["sha256"], "Source-table hash mismatch")
        item = evidence_by_id[check["evidence_id"]]
        require(check["operator"]["kind"] == item["kind"], "Source/operator statistic-kind mismatch")
        require(check["operator"]["unit"] == item["unit"], "Source/operator unit-label mismatch")
        require(finite(item["estimate"]), "Numeric source estimate required")
        operator = check["operator"]
        kind = operator["kind"]
        if kind in {"mean", "sd"}:
            used_variables = {operator.get("column")}
        elif kind == "correlation":
            used_variables = {operator.get("x"), operator.get("y")}
        elif kind == "proportion":
            used_variables = {operator.get("event", {}).get("column")}
        elif kind == "ols_coefficient":
            used_variables = {operator.get("outcome"), *operator.get("predictors", [])}
        else:
            raise ValueError("Source statistic has no implemented operator; mark not_computable")
        expected_variables = set(item["variables"]) | set(item["adjustment"])
        aligned = used_variables == expected_variables
        if kind == "ols_coefficient":
            aligned = aligned and set(item["adjustment"]) <= set(operator["predictors"])
        require(aligned or (check["status"] == "approximate" and check["assumption_ids"]),
                "Source/operator variable or adjustment mismatch; explicit approximation required")
        record.update(table={**table}, operator=check["operator"], reported_value=item["estimate"],
                      generation_link_verified=False, variable_set_matches_source=aligned,
                      evidence_mapping_check="variable_set_and_unit_labels_only")
        try:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                header = next(csv.reader(stream), [])
            require(header and len(set(header)) == len(header), "Source table has empty/duplicate header")
            summary = apply_operator(pd.read_csv(path, keep_default_na=False, na_values=[""]), check["operator"])
            record.update(summary, difference=summary["value"] - item["estimate"])
        except NotComputable as exc:
            record.update(status="not_computable", computation_error=str(exc))
        records.append(record)
    return {"schema_version": 1, "scope": "source_statistic_diagnostics_only", "checks": records,
            "engine_sha256": sha(__file__),
            "runtime": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__},
            "inputs": {n: sha(candidate / n) for n in ("source_checks.json", "evidence.json", "model_spec.json")},
            "limitations": ["Source-table generation has not been independently executed or verified.",
                            "Unit labels and declared study context require substantive review.",
                            "No target validation, automatic fit pass, or calibrated inference is implied."]}
