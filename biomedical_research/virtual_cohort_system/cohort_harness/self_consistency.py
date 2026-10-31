"""Deterministic, aggregate-only diagnostics for an Agent-authored direct table.

The declarative construction is data, never executable code. Numerical agreement
with it does not establish scientific validity or prove how a table was authored.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import platform
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from . import contracts
from .contracts import ContractError, exact_keys, number, require, string_list, validate_output, validate_task


SCHEMA_VERSION = 1
MAX_EXPRESSION_DEPTH = 32
MAX_EXPRESSION_NODES = 1024
MAX_ABS_EXPONENT = 8
MAX_JOINT_GROUPS = 4096
QUANTILES = (0.0, 0.01, 0.05, 0.5, 0.95, 0.99, 1.0)


def _key(value: Any) -> tuple[str, Any]:
    if isinstance(value, str):
        return ("string", value)
    number(value, "lookup category key")
    return ("number", value)


def validate_self_consistency_spec(task: dict, spec: dict) -> None:
    """Validate strict V1 expressions without executing any supplied program."""
    validate_task(task)
    require(task["mode"] == "enrichment", "Self-consistency V1 supports enrichment tasks only")
    exact_keys(spec, {"schema_version", "interpretation", "outcome", "numeric_predictors",
                      "group_by", "conditional_mean"}, {"conditional_sd"}, where="self-consistency spec")
    require(type(spec["schema_version"]) is int and spec["schema_version"] == SCHEMA_VERSION,
            "self-consistency schema_version must be 1")
    require(spec["interpretation"] in ("conditional_moments", "working_guides"),
            "interpretation must be conditional_moments or working_guides")
    columns = {c["name"]: c for c in task["columns"]}
    require(isinstance(spec["outcome"], str) and spec["outcome"] in columns,
            "outcome must name a task column")
    outcome = columns[spec["outcome"]]
    require(outcome["role"] == "generated" and outcome["kind"] in ("number", "integer"),
            "outcome must be a generated numeric column")
    string_list(spec["numeric_predictors"], "numeric_predictors")
    string_list(spec["group_by"], "group_by")
    for name in spec["numeric_predictors"]:
        require(name in columns and columns[name]["role"] == "observed"
                and columns[name]["kind"] in ("number", "integer"),
                "numeric_predictors must name observed numeric columns only")
    for name in spec["group_by"]:
        require(name in columns and columns[name]["role"] == "observed"
                and columns[name]["kind"] == "category",
                "group_by must name observed categorical columns only")
    require(math.prod(len(columns[name]["categories"]) for name in spec["group_by"]) <= MAX_JOINT_GROUPS,
            "group_by Cartesian product exceeds 4096 declared groups")
    node_count = 0

    def visit(expr: Any, depth: int) -> None:
        nonlocal node_count
        node_count += 1
        require(node_count <= MAX_EXPRESSION_NODES and depth <= MAX_EXPRESSION_DEPTH,
                "Expression exceeds depth or node budget")
        require(isinstance(expr, dict), "Expressions must be JSON objects")
        if set(expr) == {"const"}:
            number(expr["const"], "expression constant")
        elif set(expr) == {"column"}:
            require(isinstance(expr["column"], str) and expr["column"] in spec["numeric_predictors"],
                    "Expression column must be a declared observed numeric predictor")
        elif set(expr) == {"lookup"}:
            lookup = expr["lookup"]
            exact_keys(lookup, {"column", "values"}, where="lookup")
            name = lookup["column"]
            require(isinstance(name, str) and name in columns and columns[name]["role"] == "observed"
                    and columns[name]["kind"] == "category", "Lookup requires an observed categorical column")
            require(isinstance(lookup["values"], list), "lookup.values must be a list")
            keys = []
            for entry in lookup["values"]:
                exact_keys(entry, {"key", "value"}, where="lookup entry")
                keys.append(_key(entry["key"]))
                number(entry["value"], "lookup value")
            require(len(keys) == len(set(keys)), "Duplicate lookup category")
            require(set(keys) == {_key(v) for v in columns[name]["categories"]},
                    "Lookup must cover exactly every task-declared category; no fallback is allowed")
        elif expr.get("op") == "pow":
            exact_keys(expr, {"op", "base", "exponent"}, where="power expression")
            number(expr["exponent"], "power exponent")
            require(abs(expr["exponent"]) <= MAX_ABS_EXPONENT, "Power exponent outside [-8, 8]")
            visit(expr["base"], depth + 1)
        else:
            exact_keys(expr, {"op", "args"}, where="binary expression")
            require(expr["op"] in ("add", "sub", "mul", "div", "min", "max"),
                    "Unsupported expression operator")
            require(isinstance(expr["args"], list) and len(expr["args"]) == 2,
                    "Binary expression requires exactly two args")
            for arg in expr["args"]:
                visit(arg, depth + 1)

    visit(spec["conditional_mean"], 0)
    if "conditional_sd" in spec:
        visit(spec["conditional_sd"], 0)


def _strict_json(raw: bytes, label: str) -> dict:
    def object_pairs(pairs: list) -> dict:
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key in {label}")
            result[key] = value
        return result

    def reject_constant(_: str) -> None:
        raise ContractError(f"Nonfinite JSON constant in {label}")

    try:
        result = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=object_pairs,
                            parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ContractError(f"Invalid JSON in {label}") from error
    require(isinstance(result, dict), f"{label} must be a JSON object")
    return result


def _csv_table(raw: bytes, columns: list[dict], task: dict, label: str) -> tuple[pd.DataFrame, list[list[str]]]:
    try:
        rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True))
    except (UnicodeError, csv.Error) as error:
        raise ContractError(f"Invalid CSV in {label}") from error
    require(bool(rows), f"{label} is empty")
    names = [c["name"] for c in columns]
    require(rows[0] == names, f"{label} columns/order do not match task")
    require(len(rows) - 1 == task["n_rows"], f"{label} row count does not match task")
    require(all(len(row) == len(names) for row in rows[1:]), f"{label} has ragged rows")
    parsed: dict[str, list] = {}
    for j, column in enumerate(columns):
        name = column["name"]
        category_map = {}
        if column["kind"] == "category":
            for category in column["categories"]:
                token = str(category)
                require(token != "" and token not in category_map,
                        "CSV categories must have distinct nonempty textual representations")
                category_map[token] = category
        values = []
        for row in rows[1:]:
            token = row[j]
            if token == "" and column["nullable"]:
                value = None
            elif column["kind"] in ("number", "integer"):
                try:
                    decimal = Decimal(token)
                    value = float(decimal)
                except (ValueError, InvalidOperation, OverflowError) as error:
                    raise ContractError(f"Invalid numeric cell in {label}.{name}") from error
                require(math.isfinite(value), f"Nonfinite numeric cell in {label}.{name}")
                require(decimal == 0 or value != 0, f"Numeric underflow in {label}.{name}")
                if column["kind"] == "integer":
                    require(decimal == decimal.to_integral_value(), f"Noninteger cell in {label}.{name}")
                    value = int(decimal)
            elif column["kind"] == "category":
                require(token in category_map, f"Unknown category in {label}.{name}")
                value = category_map[token]
            else:
                require(token != "", f"Blank nonnullable cell in {label}.{name}")
                value = token
            values.append(value)
        # Object dtype avoids pandas converting typed categories or identifiers.
        parsed[name] = pd.Series(values, dtype=object)
    return pd.DataFrame(parsed, columns=names), rows[1:]


def _evaluate(expr: dict, observed: pd.DataFrame) -> np.ndarray:
    if "const" in expr:
        result = np.full(len(observed), float(expr["const"]), dtype=float)
    elif "column" in expr:
        result = observed[expr["column"]].to_numpy(dtype=float)
    elif "lookup" in expr:
        lookup = expr["lookup"]
        values = {_key(entry["key"]): float(entry["value"]) for entry in lookup["values"]}
        require(not observed[lookup["column"]].isna().any(), "Missing values in lookup column")
        result = np.array([values[_key(value)] for value in observed[lookup["column"]]], dtype=float)
    else:
        with np.errstate(all="ignore"):
            if expr["op"] == "pow":
                result = np.power(_evaluate(expr["base"], observed), expr["exponent"])
            else:
                left, right = (_evaluate(arg, observed) for arg in expr["args"])
                operations = {"add": np.add, "sub": np.subtract, "mul": np.multiply,
                              "div": np.divide, "min": np.minimum, "max": np.maximum}
                result = operations[expr["op"]](left, right)
    require(bool(np.isfinite(result).all()), "Expression produced missing or nonfinite values")
    return result


def _summary(values: np.ndarray) -> dict:
    n = len(values)
    result: dict[str, Any] = {"n": n, "finite_count": int(np.isfinite(values).sum()),
                              "all_finite": bool(np.isfinite(values).all())}
    if n == 0:
        return {**result, "status": "empty_group", "mean": None, "sample_sd": None,
                "sample_sd_status": "undefined_n_lt_2", "rmse_from_zero": None, "quantiles": None}
    scale = float(np.max(np.abs(values))) or 1.0
    scaled = values / scale
    sd = None
    sd_status = "undefined_n_lt_2"
    if n >= 2:
        with np.errstate(over="ignore"):
            sd = float(np.std(scaled, ddof=1) * scale)
        sd_status = "computed" if math.isfinite(sd) else "numeric_overflow"
        if not math.isfinite(sd):
            sd = None
    return {**result, "status": "computed", "mean": float(np.mean(scaled) * scale),
            "sample_sd": sd, "sample_sd_status": sd_status,
            "rmse_from_zero": float(np.sqrt(np.mean(scaled ** 2)) * scale),
            "quantiles": {str(q): float(np.quantile(scaled, q, method="linear") * scale) for q in QUANTILES}}


def _correlation(left: np.ndarray, right: np.ndarray) -> dict:
    if len(left) < 2:
        return {"status": "undefined_n_lt_2", "value": None}
    if np.all(left == left[0]) or np.all(right == right[0]):
        return {"status": "undefined_constant_vector", "value": None}
    a = left / (float(np.max(np.abs(left))) or 1.0)
    b = right / (float(np.max(np.abs(right))) or 1.0)
    a, b = a - a.mean(), b - b.mean()
    norm_a, norm_b = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if norm_a == 0 or norm_b == 0:
        return {"status": "numerically_unresolved", "value": None}
    value = float(np.dot(a / norm_a, b / norm_b))
    return {"status": "computed", "value": max(-1.0, min(1.0, value))}


def _associations(residual: np.ndarray, observed: pd.DataFrame, predictors: list[str]) -> dict:
    result = {}
    ranks = pd.Series(residual).rank(method="average").to_numpy(dtype=float)
    for name in predictors:
        x = observed[name].to_numpy(dtype=float)
        result[name] = {"n": len(x), "pearson": _correlation(residual, x),
                        "spearman_average_ranks": _correlation(ranks, pd.Series(x).rank(method="average").to_numpy())}
    return result


def _rank_status(observed: pd.DataFrame, predictors: list[str]) -> dict:
    vectors = [np.ones(len(observed))]
    constants = []
    for name in predictors:
        x = observed[name].to_numpy(dtype=float)
        if np.all(x == x[0]):
            constants.append(name)
            vectors.append(np.zeros(len(x)))
        else:
            scaled = x / (float(np.max(np.abs(x))) or 1.0)
            centered = scaled - np.mean(scaled)
            vectors.append(centered / (float(np.max(np.abs(centered))) or 1.0))
    design = np.column_stack(vectors)
    singular = np.linalg.svd(design, compute_uv=False)
    tolerance = float(singular.max() * max(design.shape) * np.finfo(float).eps)
    rank = int(np.count_nonzero(singular > tolerance))
    return {"status": "full_column_rank" if rank == design.shape[1] else "rank_deficient",
            "columns": ["(intercept)", *predictors], "n_rows": len(observed),
            "n_columns": design.shape[1], "rank": rank, "tolerance": tolerance,
            "constant_predictors": constants,
            "method": "SVD of intercept and centered, max-absolute-scaled declared numeric predictors"}


def _diagnostics(task: dict, observed: pd.DataFrame, generated: pd.DataFrame, spec: dict) -> dict:
    for name in spec["numeric_predictors"] + spec["group_by"]:
        require(not observed[name].isna().any(), "Declared diagnostic columns cannot contain missing values")
    y = generated[spec["outcome"]].to_numpy(dtype=float)
    mu = _evaluate(spec["conditional_mean"], observed)
    with np.errstate(all="ignore"):
        residual = y - mu
    require(bool(np.isfinite(residual).all()), "Nonfinite deviation from conditional mean/location guide")
    vectors = {"outcome": y, "conditional_mean_or_location_guide": mu, "residual": residual}
    if "conditional_sd" in spec:
        sd = _evaluate(spec["conditional_sd"], observed)
        require(bool((sd > 0).all()), "conditional_sd must be strictly positive in every row")
        with np.errstate(all="ignore"):
            z = residual / sd
        require(bool(np.isfinite(z).all()), "Nonfinite standardized deviation")
        vectors["conditional_sd_or_scale_guide"] = sd
        vectors["standardized_residual"] = z
    groups = {}
    columns = {c["name"]: c for c in task["columns"]}
    for name in spec["group_by"]:
        groups[name] = []
        for category in columns[name]["categories"]:
            mask = observed[name].map(lambda v: _key(v) == _key(category)).to_numpy(dtype=bool)
            groups[name].append({"category": category, "n": int(mask.sum()),
                                 "summaries": {key: _summary(value[mask]) for key, value in vectors.items()}})
    joint_entries = []
    if spec["group_by"]:
        category_sets = [columns[name]["categories"] for name in spec["group_by"]]
        for combination in itertools.product(*category_sets):
            mask = np.ones(len(observed), dtype=bool)
            categories = dict(zip(spec["group_by"], combination))
            for name, category in categories.items():
                mask &= observed[name].map(lambda v: _key(v) == _key(category)).to_numpy(dtype=bool)
            joint_entries.append({"categories": categories, "n": int(mask.sum()),
                                  "summaries": {key: _summary(value[mask]) for key, value in vectors.items()}})
    empty_joint_groups = sum(entry["n"] == 0 for entry in joint_entries)
    _, multiplicities = np.unique(y, return_counts=True)
    result = {
        "overall": {key: _summary(value) for key, value in vectors.items()},
        "groups": groups,
        "joint_groups": {"status": "computed" if spec["group_by"] else "not_requested",
                         "columns": spec["group_by"], "declared_group_count": len(joint_entries),
                         "observed_group_count": len(joint_entries) - empty_joint_groups,
                         "empty_group_count": empty_joint_groups, "groups": joint_entries},
        "residual_predictor_associations": _associations(residual, observed, spec["numeric_predictors"]),
        "predictor_design": _rank_status(observed, spec["numeric_predictors"]),
        "duplicate_outcome_values": {"unique_count": len(multiplicities),
                                     "repeated_value_count": int(np.count_nonzero(multiplicities > 1)),
                                     "extra_occurrence_count": int(len(y) - len(multiplicities)),
                                     "largest_multiplicity": int(multiplicities.max())},
    }
    if "standardized_residual" in vectors:
        z = vectors["standardized_residual"]
        result["standardized_residual_predictor_associations"] = _associations(z, observed, spec["numeric_predictors"])
        result["absolute_standardized_tail_counts"] = {str(limit): int(np.count_nonzero(np.abs(z) > limit))
                                                       for limit in (1, 2, 3)}
    return result


def run_self_consistency(task_path: str | Path, observed_path: str | Path, generated_path: str | Path,
                         spec_path: str | Path, output_path: str | Path) -> dict:
    """Read exact input bytes, validate, calculate, and exclusively create a report.

    Existing outputs are never overwritten. No candidate code is loaded, no table
    is created or altered, and all table-derived report values are aggregates.
    """
    paths = {"task": Path(task_path), "observed": Path(observed_path),
             "generated": Path(generated_path), "spec": Path(spec_path)}
    require(not Path(output_path).exists(), "Output already exists; choose a new report path")
    raw = {key: path.read_bytes() for key, path in paths.items()}
    task, spec = _strict_json(raw["task"], "task"), _strict_json(raw["spec"], "spec")
    validate_self_consistency_spec(task, spec)
    observed_columns = [column for column in task["columns"] if column["role"] != "generated"]
    observed, observed_rows = _csv_table(raw["observed"], observed_columns, task, "observed")
    generated, generated_rows = _csv_table(raw["generated"], task["columns"], task, "generated")
    validate_output(observed, generated, task)
    full_names = [column["name"] for column in task["columns"]]
    for j, column in enumerate(observed_columns):
        k = full_names.index(column["name"])
        require(all(left[j] == right[k] for left, right in zip(observed_rows, generated_rows)),
                f"Observed CSV cell representation changed: {column['name']}")
    report = {
        "schema_version": SCHEMA_VERSION, "kind": "direct_table_self_consistency",
        "task_id": task["task_id"], "outcome": spec["outcome"], "interpretation": spec["interpretation"],
        "status": "computed", "table_contract": "valid", "observed_preservation": "exact_decoded_csv_cells",
        "scientific_validity": "not_assessed", "authorship_or_prior_commitment": "not_verified",
        "notes": ["Diagnostics are descriptive finite-sample quantities, not validity tests or tuning targets.",
                  "Residual means, spread, correlations and tails are not required to equal population moments.",
                  "Working guides do not assert conditional expected values or conditional standard deviations.",
                  "Hashes bind the supplied bytes; they do not prove source quality, authorship or chronology."],
        "bindings": {key: {"sha256": hashlib.sha256(value).hexdigest(), "bytes": len(value)} for key, value in raw.items()},
        "implementation": {"self_consistency_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                           "contracts_sha256": hashlib.sha256(Path(contracts.__file__).read_bytes()).hexdigest(),
                           "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
        "diagnostics": _diagnostics(task, observed, generated, spec),
    }
    encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
    with Path(output_path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("task", "observed", "generated", "spec", "output"):
        parser.add_argument(f"--{flag}", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = run_self_consistency(args.task, args.observed, args.generated, args.spec, args.output)
    except (ContractError, OSError, ValueError, OverflowError, TypeError, KeyError, np.linalg.LinAlgError) as error:
        print(f"self-consistency rejected: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "output": str(args.output),
                      "scientific_validity": report["scientific_validity"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
