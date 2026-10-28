"""Case-independent schema checks and study observation operators.

These operators fail on undefined statistics rather than silently replacing them
with zero. They do not infer statistical compatibility, transportability, or
evidence independence; those are separate, explicit research decisions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from numbers import Integral, Real
import operator

import numpy as np
import pandas as pd


def _frame(raw) -> pd.DataFrame:
    try:
        frame = raw.copy(deep=True) if isinstance(raw, pd.DataFrame) else pd.DataFrame(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("Input cannot be converted to a data frame") from exc
    if not frame.columns.is_unique:
        raise ValueError("Duplicate column names are not allowed")
    return frame


def _number(value, label: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite number")
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return value


def _numeric(frame: pd.DataFrame, name: str) -> np.ndarray:
    if name not in frame.columns:
        raise ValueError(f"Missing column: {name}")
    try:
        values = pd.to_numeric(frame[name], errors="raise").to_numpy(dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"Column {name} must be numeric") from exc
    if not np.isfinite(values).all():
        raise ValueError(f"Column {name} contains missing or nonfinite values")
    return values


def validate_frame(raw, n: int, schema: dict) -> pd.DataFrame:
    """Validate required columns and return a copy, preserving extra columns.

    Numeric strings may be converted to numbers. Bounds are checked after that
    conversion; ``exclusive_minimum`` is a numeric threshold, not a boolean.
    Category columns cannot be missing even when no allowed values are supplied.
    """
    if isinstance(n, bool) or not isinstance(n, Integral) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if not isinstance(schema, Mapping):
        raise ValueError("schema must be a column-to-rule mapping")
    frame = _frame(raw)
    if len(frame) != n:
        raise ValueError(f"Expected {n} rows, received {len(frame)}")
    for name, rule in schema.items():
        if name not in frame.columns:
            raise ValueError(f"Missing required column: {name}")
        if not isinstance(rule, Mapping):
            raise ValueError(f"Invalid schema rule for {name}")
        if rule.get("type") == "number":
            values = _numeric(frame, name)
            for bound, op in (("minimum", np.greater_equal), ("maximum", np.less_equal),
                              ("exclusive_minimum", np.greater)):
                if bound in rule:
                    threshold = _number(rule[bound], f"{name}.{bound}")
                    if not op(values, threshold).all():
                        raise ValueError(f"Column {name} violates {bound}={threshold}")
            frame[name] = values
        elif rule.get("type") == "category":
            if frame[name].isna().any():
                raise ValueError(f"Category column {name} contains missing values")
            if "values" in rule and not frame[name].isin(rule["values"]).all():
                raise ValueError(f"Category column {name} contains an unsupported value")
        else:
            raise ValueError(f"Unsupported schema type for {name}: {rule.get('type')}")
    return frame


_FILTER_OPS = {"lt": operator.lt, "le": operator.le, "gt": operator.gt,
               "ge": operator.ge, "eq": operator.eq, "ne": operator.ne}


def _mask(frame: pd.DataFrame, filters: list) -> np.ndarray:
    if not isinstance(filters, (list, tuple)):
        raise ValueError("Filters must be a list of column/op/value objects")
    mask = np.ones(len(frame), dtype=bool)
    for item in filters:
        if not isinstance(item, Mapping):
            raise ValueError("Each filter must be an object")
        name, op = item.get("column"), item.get("op")
        if name not in frame.columns or op not in _FILTER_OPS or "value" not in item:
            raise ValueError(f"Invalid filter: {item}")
        if frame[name].isna().any():
            raise ValueError(f"Filter column {name} contains missing values")
        try:
            result = _FILTER_OPS[op](frame[name], item["value"])
            if result.isna().any():
                raise ValueError("Filter result is undefined")
            mask &= result.to_numpy(dtype=bool)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Cannot apply filter to {name}") from exc
    return mask


def observe(frame, spec: dict) -> float:
    """Compute one declared statistic, optionally within an AND-filtered subset.

    Univariate statistics use ``column``. Paired statistics use ``x`` and ``y``.
    Probability is the fraction satisfying all ``filters`` within ``where``.
    SD uses ddof=1; residual SD uses sqrt(SSE/(n-2)) after intercept OLS.
    """
    data = _frame(frame)
    if not isinstance(spec, Mapping):
        raise ValueError("Observation specification must be an object")
    if "where" in spec:
        data = data.loc[_mask(data, spec["where"])]
    if len(data) == 0:
        raise ValueError("Cannot observe an empty analysis subset")
    kind = spec.get("kind")
    if kind == "probability":
        if "filters" not in spec:
            raise ValueError("Probability requires filters (an empty list denotes all rows)")
        result = float(_mask(data, spec["filters"]).mean())
    elif kind in {"mean", "sd", "quantile"}:
        values = _numeric(data, spec.get("column"))
        if kind == "mean":
            result = float(np.mean(values))
        elif kind == "sd":
            if len(values) < 2:
                raise ValueError("Sample SD requires at least two rows")
            result = float(np.std(values, ddof=1))
        else:
            q = _number(spec.get("q"), "q")
            if not 0 <= q <= 1:
                raise ValueError("q must lie in [0, 1]")
            result = float(np.quantile(values, q))
    elif kind in {"correlation", "ols_slope", "ols_intercept", "residual_sd"}:
        x, y = _numeric(data, spec.get("x")), _numeric(data, spec.get("y"))
        if len(x) < 2:
            raise ValueError("Paired statistic requires at least two rows")
        xc, yc = x - np.mean(x), y - np.mean(y)
        xx, yy = float(xc @ xc), float(yc @ yc)
        if xx <= 0 or not np.isfinite(xx):
            raise ValueError("Undefined statistic: predictor is constant or ill-conditioned")
        xy = float(xc @ yc)
        if kind == "correlation":
            if yy <= 0 or not np.isfinite(yy):
                raise ValueError("Undefined correlation: response is constant or ill-conditioned")
            result = float(xy / np.sqrt(xx) / np.sqrt(yy))
        else:
            slope = xy / xx
            if kind == "ols_slope":
                result = float(slope)
            elif kind == "ols_intercept":
                result = float(np.mean(y) - slope * np.mean(x))
            else:
                if len(x) < 3:
                    raise ValueError("Residual SD requires at least three rows")
                residual = yc - slope * xc
                result = float(np.sqrt((residual @ residual) / (len(x) - 2)))
    else:
        raise ValueError(f"Unsupported observation kind: {kind}")
    if not np.isfinite(result):
        raise ValueError(f"Observation {kind} is nonfinite")
    return result


def derive(frame, recipes: list) -> pd.DataFrame:
    """Add declared transformations in order, validating numeric domains.

    ``difference`` is left-right; ``percent_change`` is 100*(left/right-1);
    ``log_ratio`` is log(left/right), requiring positive left and right values.
    Existing columns cannot be overwritten accidentally.
    """
    data = _frame(frame)
    if not isinstance(recipes, (list, tuple)):
        raise ValueError("recipes must be a list")
    for recipe in recipes:
        if not isinstance(recipe, Mapping):
            raise ValueError("Each derivation must be an object")
        name, kind = recipe.get("name"), recipe.get("kind")
        if not isinstance(name, str) or not name or name in data.columns:
            raise ValueError(f"Invalid or existing derived column name: {name}")
        left = _numeric(data, recipe.get("left"))
        right = _numeric(data, recipe.get("right"))
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            if kind == "difference":
                values = left - right
            elif kind == "percent_change":
                if np.any(right == 0):
                    raise ValueError("Percent change has a zero divisor")
                values = 100 * (left / right - 1)
            elif kind == "log_ratio":
                if np.any(left <= 0) or np.any(right <= 0):
                    raise ValueError("Log ratio requires positive operands")
                values = np.log(left) - np.log(right)
            else:
                raise ValueError(f"Unsupported derivation kind: {kind}")
        if not np.isfinite(values).all():
            raise ValueError(f"Derived column {name} contains nonfinite values")
        data[name] = values
    return data


def compare_invariants(parent, current, columns: Sequence[str]) -> dict:
    """Compare seeded generated rows positionally with exact value equality.

    This only checks declared output invariants. It does not establish shared
    random draws or participant correspondence; the caller must enforce those.
    """
    before, after = _frame(parent), _frame(current)
    if isinstance(columns, str) or not isinstance(columns, Sequence):
        raise ValueError("columns must be a sequence of column names")
    if len(set(columns)) != len(columns):
        raise ValueError("Invariant columns must be unique")
    result = {"parent_rows": len(before), "current_rows": len(after), "columns": {}}
    if len(before) != len(after):
        result.update(status="not_testable", equal_rows=None, reason="row_count_mismatch")
        result["columns"] = {name: {"status": "not_testable", "equal_rows": None,
                                     "reason": "row_count_mismatch"} for name in columns}
        return result
    same_rows = np.ones(len(before), dtype=bool)
    for name in columns:
        if name not in before.columns or name not in after.columns:
            result["columns"][name] = {"status": "fail", "equal_rows": 0,
                                       "mismatched_rows": len(before), "reason": "missing_column"}
            same_rows[:] = False
            continue
        left, right = before[name].reset_index(drop=True), after[name].reset_index(drop=True)
        equal = ((left == right) | (left.isna() & right.isna())).fillna(False).to_numpy(dtype=bool)
        count = int(equal.sum())
        result["columns"][name] = {"status": "pass" if equal.all() else "fail",
                                   "equal_rows": count, "mismatched_rows": len(equal) - count}
        same_rows &= equal
    passed = all(item["status"] == "pass" for item in result["columns"].values())
    result.update(status="pass" if passed else "fail", equal_rows=int(same_rows.sum()))
    return result
