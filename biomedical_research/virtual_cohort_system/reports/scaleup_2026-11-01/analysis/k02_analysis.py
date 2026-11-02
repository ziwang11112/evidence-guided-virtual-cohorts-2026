"""Prospective K02 arithmetic on explicit in-memory tables; no data access.

This module is not a custodian/access gate or a case release. The caller must
supply an authorized canonical DataFrame. All three estimands remain visible.
"""
from __future__ import annotations

import math
from typing import Literal

import numpy as np
import pandas as pd

COLUMNS = ("age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol")
NUMERIC = ("age", "bmi", "total_cholesterol", "hdl_cholesterol")
IDS = ("K02-HDL-BMI", "K02-TC-BMI", "K02-LIPID-RESIDUAL")
OUTCOMES = {"K02-HDL-BMI": "hdl_cholesterol", "K02-TC-BMI": "total_cholesterol"}
EPS = np.finfo(float).eps
Z95 = 1.959963984540054


def _interval(reason):
    return {"status": "unavailable", "reason": reason, "lower": None,
            "upper": None, "standard_error": None,
            "kind": "HC3_normal_assumption_conditional_sensitivity_not_design_CI"}


def _endpoint(key, n=0, reason="not_evaluated"):
    return {"status": "unavailable", "estimate": None, "reason": reason, "n": n,
            "unit": "1" if key == IDS[2] else "mg/dL per 5 kg/m^2",
            "interval": _interval("residual_interval_not_implemented" if key == IDS[2] else reason)}


def _stop(result, status, reason):
    result["status"] = status
    result["reason"] = reason
    for key in IDS:
        result["estimands"][key] = _endpoint(key, result["selection"]["eligible_rows"], reason)
    return result


def _finish(result):
    states = [x["status"] == "computed" for x in result["estimands"].values()]
    result["status"] = "complete" if all(states) else ("partial" if any(states) else "unavailable")
    return result


def analyze_frame(frame: pd.DataFrame, *, role: Literal["reference", "generated"]) -> dict:
    """Analyze canonical columns without loading files or returning row-level data.

    role is mandatory. Only reference mode emits HC3 sensitivity intervals and
    evaluation-only sample-SD denominators. Fixed eligibility exclusions are
    counted, including overlap; unknown codes/schema errors fail the invocation.
    Raw NA strings and unit/code mapping belong to a separate preparation layer.
    """
    if role not in {"reference", "generated"}:
        raise ValueError("An explicit reference or generated role is required")
    result = {
        "specification": "k02_analysis_spec.v0", "release_status": "prospective_not_released",
        "role": role, "status": "unavailable", "reason": None,
        "selection": {"input_rows": len(frame) if isinstance(frame, pd.DataFrame) else None,
                      "eligible_rows": 0, "excluded_rows": None,
                      "reason_counts_overlap": {}},
        "design": None,
        "estimands": {key: _endpoint(key) for key in IDS},
        "metric_denominators": {},
        "inference_scope": "empirical_sample; unavailable clustering; no population/design or transport coverage",
        "file_access_performed": False,
    }
    if not isinstance(frame, pd.DataFrame):
        return _stop(result, "invalid_input", "DataFrame_required")
    if not frame.columns.is_unique or not set(COLUMNS) <= set(frame.columns):
        return _stop(result, "invalid_input", "missing_or_duplicate_columns")
    for col in NUMERIC:
        dtype = frame[col].dtype
        if (not pd.api.types.is_numeric_dtype(dtype)
                or pd.api.types.is_bool_dtype(dtype)
                or pd.api.types.is_complex_dtype(dtype)):
            return _stop(result, "invalid_input", "canonical_real_numeric_column_required:" + col)
    try:
        numeric = frame.loc[:, list(NUMERIC)].to_numpy(dtype=float, na_value=np.nan)
        sex_missing = frame["sex"].isna().to_numpy()
        recognized = frame["sex"].isin(["F", "M"]).to_numpy()
        sex_f = frame["sex"].eq("F").fillna(False).to_numpy(dtype=bool)
    except (TypeError, ValueError, OverflowError):
        return _stop(result, "invalid_input", "canonical_column_conversion_failed")
    if np.any(~sex_missing & ~recognized):
        return _stop(result, "invalid_input", "unknown_nonmissing_sex_token")
    age, bmi, tc, hdl = numeric.T
    reasons = {
        "missing_numeric": np.isnan(numeric).any(axis=1),
        "infinite_numeric": np.isinf(numeric).any(axis=1),
        "missing_sex": sex_missing,
        "age_below_18": np.isfinite(age) & (age < 18),
        "nonpositive_bmi": np.isfinite(bmi) & (bmi <= 0),
        "nonpositive_total_cholesterol": np.isfinite(tc) & (tc <= 0),
        "nonpositive_hdl_cholesterol": np.isfinite(hdl) & (hdl <= 0),
    }
    excluded = np.logical_or.reduce(list(reasons.values()))
    keep = ~excluded
    n = int(keep.sum())
    result["selection"].update(
        eligible_rows=n, excluded_rows=int(excluded.sum()),
        reason_counts_overlap={k: int(v.sum()) for k, v in reasons.items()})
    ys = {"total_cholesterol": tc[keep], "hdl_cholesterol": hdl[keep]}
    if role == "reference":
        for name, y in ys.items():
            with np.errstate(over="ignore", invalid="ignore"):
                sd = float(np.std(y, ddof=1)) if n > 1 else math.nan
            ok = math.isfinite(sd) and sd > 0
            result["metric_denominators"][name] = {
                "status": "computed" if ok else "unavailable",
                "sample_sd": sd if ok else None, "ddof": 1, "n": n,
                "unit": "mg/dL", "role": "evaluation_only_not_builder_input",
                "reason": None if ok else "insufficient_or_zero_or_nonfinite_sample_SD"}
    if n <= 4:
        return _stop(result, "unavailable", "insufficient_rows_for_four_column_design")
    x = np.column_stack((np.ones(n), (age[keep] - 50) / 10,
                         sex_f[keep].astype(float), (bmi[keep] - 25) / 5))
    try:
        u, singular, vt = np.linalg.svd(x, full_matrices=False)
        tol = max(x.shape) * EPS * singular[0]
        rank = int((singular > tol).sum())
        result["design"] = {"n": n, "columns": 4, "rank": rank,
                            "rank_tolerance": float(tol),
                            "coordinates": ["intercept", "age10", "sex_F", "bmi5"],
                            "weights": "none"}
        if rank < 4:
            return _stop(result, "unavailable", "rank_deficient_design")
        pinv = (vt.T / singular) @ u.T
        leverage = np.sum(u * u, axis=1)
    except np.linalg.LinAlgError:
        return _stop(result, "unavailable", "design_decomposition_failed")
    residuals = {}
    for key, name in OUTCOMES.items():
        y = ys[name]
        endpoint = _endpoint(key, n)
        result["estimands"][key] = endpoint
        if np.ptp(y) == 0:
            endpoint["reason"] = "constant_response"
            endpoint["interval"] = _interval("constant_response")
            continue
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            beta = pinv @ y
            residual = y - x @ beta
        if not np.isfinite(beta).all() or not np.isfinite(residual).all():
            endpoint["reason"] = "nonfinite_OLS_arithmetic"
            endpoint["interval"] = _interval(endpoint["reason"])
            continue
        endpoint.update(status="computed", estimate=float(beta[3]), reason=None)
        y_norm = float(np.linalg.norm(y))
        residual_norm = float(np.linalg.norm(residual))
        resolution = 16 * EPS * max(x.shape) * max(y_norm, np.finfo(float).tiny)
        usable = (math.isfinite(residual_norm) and math.isfinite(resolution)
                  and residual_norm > resolution)
        if usable:
            residuals[name] = residual
        if role == "generated":
            endpoint["interval"] = _interval("generated_table_no_inferential_precision")
        elif not usable:
            endpoint["interval"] = _interval("residual_variation_below_numerical_resolution")
        elif np.any(1 - leverage <= 64 * EPS):
            endpoint["interval"] = _interval("HC3_unit_or_near_unit_leverage")
        else:
            with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                influence = pinv[3] * residual / (1 - leverage)
                variance = float(influence @ influence)
                se = math.sqrt(variance) if variance >= 0 else math.nan
                lower, upper = float(beta[3] - Z95 * se), float(beta[3] + Z95 * se)
            if all(math.isfinite(v) for v in (variance, se, lower, upper)):
                endpoint["interval"] = {
                    "status": "available", "reason": None, "lower": lower, "upper": upper,
                    "standard_error": se, "normal_multiplier": Z95, "nominal_level": 0.95,
                    "kind": "HC3_normal_assumption_conditional_sensitivity_not_design_CI"}
            else:
                endpoint["interval"] = _interval("nonfinite_HC3_arithmetic")
    correlation = _endpoint(IDS[2], n, "unavailable_or_degenerate_residuals")
    result["estimands"][IDS[2]] = correlation
    if len(residuals) == 2:
        a = residuals["total_cholesterol"] - np.mean(residuals["total_cholesterol"])
        b = residuals["hdl_cholesterol"] - np.mean(residuals["hdl_cholesterol"])
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            value = float((a / np.linalg.norm(a)) @ (b / np.linalg.norm(b)))
        if math.isfinite(value) and abs(value) <= 1 + 256 * EPS:
            correlation.update(status="computed", estimate=float(np.clip(value, -1, 1)), reason=None)
        else:
            correlation["reason"] = "nonfinite_or_out_of_range_residual_correlation"
    return _finish(result)
