"""K01 prospective descriptive projections; explicit in-memory inputs only."""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

IDS = ("K01-GLUCOSE-BMI", "K01-GLUCOSE-AGE", "K01-SEX-BMI")
NUMERIC = ("age", "bmi", "glucose")
EPS = np.finfo(float).eps
Z95 = 1.959963984540054


def _interval(reason):
    return {"status": "unavailable", "reason": reason, "lower": None, "upper": None,
            "standard_error": None,
            "kind": "HC3_normal_assumption_conditional_sensitivity_not_design_CI"}


def _endpoint(key, n=0, reason="not_evaluated"):
    unit = "mmol/L per 10 years" if key == IDS[1] else "mmol/L per 5 kg/m^2"
    return {"status": "unavailable", "estimate": None, "reason": reason,
            "n": n, "unit": unit, "interval": _interval(reason)}


def _stop(result, status, reason):
    result.update(status=status, reason=reason)
    result["estimands"] = {k: _endpoint(k, result["selection"]["eligible_rows"], reason) for k in IDS}
    return result


def analyze_frame(frame: pd.DataFrame, *, role: str) -> dict:
    """Use one common frame. Generated invalid rows reject the whole invocation.

    The caller must separately authenticate the task/execution and whole-table
    context guard. Reference mode alone applies fixed eligibility and emits an
    evaluation-only SD/working intervals. No file load or target access exists.
    """
    if role not in {"reference", "generated"}:
        raise ValueError("Explicit reference/generated role required")
    result = {
        "specification": "k01_analysis_spec.v1", "release_status": "prospective_not_released",
        "role": role, "status": "unavailable", "reason": None,
        "selection": {"input_rows": len(frame) if isinstance(frame, pd.DataFrame) else None,
                      "eligible_rows": 0, "excluded_rows": None, "reason_counts_overlap": {}},
        "designs": {}, "estimands": {k: _endpoint(k) for k in IDS},
        "metric_denominators": {}, "file_access_performed": False,
        "inference_scope": "finite_recorded_sample_projection_not_causal_or_population_inference",
    }
    if not isinstance(frame, pd.DataFrame):
        return _stop(result, "invalid_input", "DataFrame_required")
    if not frame.columns.is_unique or not set((*NUMERIC, "sex")) <= set(frame.columns):
        return _stop(result, "invalid_input", "missing_or_duplicate_columns")
    for col in NUMERIC:
        dtype = frame[col].dtype
        if (not pd.api.types.is_numeric_dtype(dtype) or pd.api.types.is_bool_dtype(dtype)
                or pd.api.types.is_complex_dtype(dtype)):
            return _stop(result, "invalid_input", "canonical_real_numeric_required:" + col)
    try:
        values = frame.loc[:, list(NUMERIC)].to_numpy(dtype=float, na_value=np.nan)
        missing_sex = frame["sex"].isna().to_numpy()
        recognized = frame["sex"].isin(["F", "M"]).to_numpy()
        female = frame["sex"].eq("F").fillna(False).to_numpy(dtype=bool)
    except (TypeError, ValueError, OverflowError):
        return _stop(result, "invalid_input", "canonical_conversion_failed")
    if np.any(~missing_sex & ~recognized):
        return _stop(result, "invalid_input", "unknown_nonmissing_sex_token")
    age, bmi, glucose = values.T
    reasons = {
        "missing_numeric": np.isnan(values).any(axis=1),
        "infinite_numeric": np.isinf(values).any(axis=1),
        "missing_sex": missing_sex,
        "age_below_40": np.isfinite(age) & (age < 40),
        "nonpositive_bmi": np.isfinite(bmi) & (bmi <= 0),
        "nonpositive_glucose": np.isfinite(glucose) & (glucose <= 0),
    }
    excluded = np.logical_or.reduce(list(reasons.values()))
    n = int((~excluded).sum())
    result["selection"].update(eligible_rows=n, excluded_rows=int(excluded.sum()),
        reason_counts_overlap={k: int(v.sum()) for k, v in reasons.items()})
    if role == "generated" and excluded.any():
        return _stop(result, "invalid_input", "generated_rows_must_all_be_eligible_no_filtering")
    keep = ~excluded
    y = glucose[keep]
    if role == "reference":
        with np.errstate(over="ignore", invalid="ignore"):
            sd = float(np.std(y, ddof=1)) if n > 1 else math.nan
        ok = math.isfinite(sd) and sd > 0
        result["metric_denominators"]["glucose"] = {
            "status": "computed" if ok else "unavailable", "sample_sd": sd if ok else None,
            "ddof": 1, "n": n, "unit": "mmol/L", "role": "evaluation_only_not_builder_input",
            "reason": None if ok else "insufficient_or_zero_or_nonfinite_sample_SD"}
    if n <= 5:
        return _stop(result, "unavailable", "require_n_greater_than_five")
    s = female[keep].astype(float)
    if np.unique(s).size != 2:
        return _stop(result, "unavailable", "both_sexes_required")
    a, b = (age[keep] - 50) / 10, (bmi[keep] - 25) / 5
    matrices = {"base": np.column_stack((np.ones(n), a, s, b)),
                "interaction": np.column_stack((np.ones(n), a, s, b, s*b))}
    decompositions = {}
    for name, x in matrices.items():
        try:
            u, singular, vt = np.linalg.svd(x, full_matrices=False)
            tol = max(x.shape) * EPS * singular[0]
            rank = int((singular > tol).sum())
            result["designs"][name] = {"n": n, "columns": x.shape[1], "rank": rank,
                "rank_tolerance": float(tol), "weights": "none"}
            if rank != x.shape[1]:
                return _stop(result, "unavailable", "rank_deficient_" + name + "_design")
            decompositions[name] = ((vt.T / singular) @ u.T, np.sum(u*u, axis=1))
        except np.linalg.LinAlgError:
            return _stop(result, "unavailable", "design_decomposition_failed")
    if np.ptp(y) == 0:
        return _stop(result, "unavailable", "constant_response")
    fits = {}
    for name, x in matrices.items():
        pinv, leverage = decompositions[name]
        with np.errstate(over="ignore", invalid="ignore"):
            beta = pinv @ y
            residual = y - x @ beta
        if not np.isfinite(beta).all() or not np.isfinite(residual).all():
            return _stop(result, "unavailable", "nonfinite_OLS_arithmetic")
        fits[name] = (beta, residual, pinv, leverage, x)
    for key, name, term in [(IDS[0], "base", 3), (IDS[1], "base", 1), (IDS[2], "interaction", 4)]:
        beta, residual, pinv, leverage, x = fits[name]
        ep = _endpoint(key, n)
        ep.update(status="computed", estimate=float(beta[term]), reason=None)
        result["estimands"][key] = ep
        if role == "generated":
            ep["interval"] = _interval("generated_table_no_inferential_precision")
            continue
        residual_norm = float(np.linalg.norm(residual))
        resolution = 16 * EPS * max(x.shape) * max(float(np.linalg.norm(y)), np.finfo(float).tiny)
        if not math.isfinite(resolution) or not math.isfinite(residual_norm) or residual_norm <= resolution:
            ep["interval"] = _interval("residual_variation_below_numerical_resolution")
        elif np.any(1-leverage <= 64*EPS):
            ep["interval"] = _interval("HC3_unit_or_near_unit_leverage")
        else:
            with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                influence = pinv[term]*residual/(1-leverage)
                variance = float(influence @ influence)
                se = math.sqrt(variance) if variance >= 0 else math.nan
                lower, upper = float(beta[term]-Z95*se), float(beta[term]+Z95*se)
            if all(math.isfinite(v) for v in (variance, se, lower, upper)):
                ep["interval"] = {"status": "available", "reason": None, "lower": lower,
                    "upper": upper, "standard_error": se, "normal_multiplier": Z95,
                    "nominal_level": 0.95, "kind": "HC3_normal_assumption_conditional_sensitivity_not_design_CI"}
            else:
                ep["interval"] = _interval("nonfinite_HC3_arithmetic")
    result["status"] = "complete"
    return result
