"""Finite, unweighted source statistics on declared numerical measurements.

Each operation declares the expected units of all columns it reads. Unit names
are literal. Submit a measured column already expressed in the intended units.
No scientific code from an author is imported or evaluated.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[3]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
from cohort_harness import source_checks


class ReplayError(ValueError):
    """Operator invalid, incompatible with the schema, or undefined on these rows."""


FIELDS = {
    "mean": {"y"}, "geometric_mean": {"y"}, "sd": {"y", "ddof"},
    "pearson": {"x", "y"}, "spearman": {"x", "y"},
    "ols_slope": {"x", "y"}, "ols_intercept": {"x", "y"},
    "r_squared": {"x", "y", "scale"},
    "count": set(), "proportion": {"event"}, "percentage": {"event"},
    "odds_ratio": {"exposure", "outcome"},
}


def require(ok, message):
    if not ok:
        raise ReplayError(message)


def result_unit(op):
    """Canonical result unit for a structurally valid operator."""
    kind = op["kind"]
    if kind in {"mean", "geometric_mean", "sd", "ols_intercept"}:
        return op["units"][op["y"]]
    if kind == "ols_slope":
        y, x = (op["units"][op[key]] for key in ("y", "x"))
        return "1" if y == x else f"{y}/{x}"
    if kind == "count":
        return "count"
    if kind == "percentage" or (kind == "r_squared" and op["scale"] == "percent"):
        return "%"
    return "1"


def _predicate(predicate):
    require(isinstance(predicate, dict) and set(predicate) == {"column", "cmp", "value"},
            "Predicate requires column, cmp and value")
    require(isinstance(predicate["column"], str) and predicate["column"], "Invalid predicate column")
    require(isinstance(predicate["cmp"], str) and predicate["cmp"] in {"eq", "ne", "lt", "le", "gt", "ge"},
            "Unsupported predicate comparison")
    require(source_checks.finite(predicate["value"]), "Predicate threshold must be a finite number")
    return {"column": predicate["column"], "op": predicate["cmp"], "value": predicate["value"]}


def _finite_column(frame, name):
    s = frame[name]
    require(pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)
            and not pd.api.types.is_complex_dtype(s), "Column must contain real numeric measurements")
    require(not s.isna().any() and np.isfinite(s.to_numpy(dtype=float)).all(),
            "Column contains missing or nonfinite values")


def _compute(frame, schema, op):
    require(isinstance(frame, pd.DataFrame) and frame.columns.is_unique, "Expected a table with unique columns")
    require(isinstance(schema, dict) and isinstance(op, dict), "Expected a column-unit map and operator")
    require("weight" not in op and "weights" not in op and "weight_column" not in op,
            "Weighted operators are not supported")
    kind = op.get("kind")
    require(isinstance(kind, str) and kind in FIELDS, "Unsupported operator kind")
    fields = FIELDS[kind] | {"kind", "units"}
    require(fields <= op.keys() <= fields | {"where"}, "Operator fields differ from the declared kind")
    require(isinstance(op["units"], dict), "Expected units for every referenced column")
    where = op.get("where", [])
    require(isinstance(where, list), "where must be a list of AND predicates")
    filters = [_predicate(predicate) for predicate in where]
    events = {k: _predicate(op[k]) for k in ("event", "exposure", "outcome") if k in op}
    referenced = {p["column"] for p in [*filters, *events.values()]}
    for key in ("x", "y"):
        if key in op:
            require(isinstance(op[key], str) and op[key], "Operator column must be named")
            referenced.add(op[key])
    require(referenced == op["units"].keys(), "Unit declarations must cover exactly the referenced columns")
    for name in referenced:
        require(name in schema and name in frame.columns, f"Column absent from declared or delivered schema: {name}")
        require(isinstance(op["units"][name], str) and op["units"][name].strip() and
                op["units"][name] == schema[name], f"Declared unit differs from delivered schema: {name}")
    if "x" in op:
        require(op["x"] != op["y"], "Predictor and outcome must be distinct columns")
    if kind == "sd":
        require(type(op["ddof"]) is int and op["ddof"] in (0, 1), "ddof must be 0 or 1")
    if kind == "r_squared":
        require(op["scale"] in ("fraction", "percent"), "R-squared requires scale fraction or percent")

    mask = np.ones(len(frame), dtype=bool)
    for predicate in filters:
        _finite_column(frame, predicate["column"])
        mask &= source_checks.condition(frame, predicate).to_numpy(dtype=bool)
    selected = frame.loc[mask]
    n = len(selected)
    if kind == "count":
        return float(n), n
    require(n > 0, "No rows after conditioning")
    for name in referenced:
        _finite_column(selected, name)
    if kind == "geometric_mean":
        values = selected[op["y"]].to_numpy(dtype=float)
        require((values > 0).all(), "Geometric mean requires positive values")
        return float(np.exp(np.log(values).mean())), n
    if kind == "sd" and op["ddof"] == 0:
        return float(selected[op["y"]].std(ddof=0)), n
    if kind in ("ols_slope", "ols_intercept") and n == 2:
        # Two distinct predictor values determine a descriptive line exactly.
        # The older inferential OLS interface also requires residual degrees of freedom.
        x1, x2 = selected[op["x"]].to_numpy(dtype=float)
        y1, y2 = selected[op["y"]].to_numpy(dtype=float)
        require(x1 != x2, "OLS requires distinct predictor values")
        slope = (y2 - y1) / (x2 - x1)
        return float(slope if kind == "ols_slope" else y1 - slope * x1), n
    if kind == "odds_ratio":
        exposure = source_checks.condition(selected, events["exposure"]).to_numpy(dtype=bool)
        outcome = source_checks.condition(selected, events["outcome"]).to_numpy(dtype=bool)
        a, b = int((exposure & outcome).sum()), int((exposure & ~outcome).sum())
        c, d = int((~exposure & outcome).sum()), int((~exposure & ~outcome).sum())
        require(b * c > 0, "Crude odds ratio has zero denominator; no continuity correction")
        return a * d / (b * c), n

    native = {"selection": [], "missing_policy": "error", "unit": result_unit(op)}
    if kind in ("mean", "sd"):
        native.update(kind=kind, column=op["y"])
    elif kind in ("proportion", "percentage"):
        native.update(kind="proportion", event=events["event"])
    elif kind in ("ols_slope", "ols_intercept"):
        native.update(kind="ols_coefficient", outcome=op["y"], predictors=[op["x"]],
                      term=op["x"] if kind == "ols_slope" else "intercept", include_intercept=True)
    else:
        native.update(kind="spearman_correlation" if kind == "spearman" else "correlation",
                      x=op["x"], y=op["y"], unit="1")
    value = source_checks.apply_operator(selected, native)["value"]
    if kind == "r_squared":
        value = value ** 2 * (100.0 if op["scale"] == "percent" else 1.0)
    return value, n


def compute(frame, schema, op):
    """Return (estimate, number of qualifying rows), raising ReplayError on failure."""
    try:
        value, n = _compute(frame, schema, op)
        require(np.isfinite(value), "Nonfinite statistic")
        return float(value), n
    except ReplayError:
        raise
    except (ValueError, TypeError, KeyError, ArithmeticError, np.linalg.LinAlgError) as exc:
        raise ReplayError(str(exc)) from exc
