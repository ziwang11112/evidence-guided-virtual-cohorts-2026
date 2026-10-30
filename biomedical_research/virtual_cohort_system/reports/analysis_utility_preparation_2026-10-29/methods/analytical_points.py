"""Point-estimate protocol for two enrichment tasks; importing reads no data.

This module does not estimate survey variance or synthetic uncertainty. It is
not an authorized hidden-reference release command. Inputs must be supplied by
the evaluator after its release gate. The same function evaluates real and
generated outcomes. Scientific relations are estimated, never prescribed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class Nonestimable(ValueError):
    pass


def normalize_visible(frame: pd.DataFrame, case: str) -> pd.DataFrame:
    """Explicit adapter for actual task schemas; never accept hidden/proxy columns."""
    required = ["row_id", "age_years", "sex", "bmi_kg_m2"]
    if case == "nhanes_insulin":
        required.append("fasting_glucose_mg_dl")
    elif case != "pns_hba1c":
        raise ValueError("Unknown task")
    if list(frame.columns) != required or frame.row_id.isna().any() or not frame.row_id.is_unique:
        raise ValueError("Unexpected visible schema or invalid IDs")
    if not frame.sex.isin(["male", "female"]).all():
        raise ValueError("Unexpected sex label")
    result = frame.rename(columns={"age_years":"age", "bmi_kg_m2":"bmi",
                                   "fasting_glucose_mg_dl":"glucose_mg_dl"}).set_index("row_id").copy()
    result["sex"] = result.sex.map({"male":1, "female":2})
    return result


def wls_point(X, y, w):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    if X.ndim != 2 or y.ndim != 1 or w.ndim != 1 or not len(y) == len(w) == len(X):
        raise ValueError("Incompatible input dimensions")
    if not (np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(w).all()):
        raise ValueError("Nonfinite analysis input")
    if (w <= 0).any():
        raise ValueError("Weights must be positive")
    if len(y) <= X.shape[1] or np.linalg.matrix_rank(X) < X.shape[1]:
        raise Nonestimable("Insufficient rows or rank-deficient analysis")
    scaled = np.sqrt(w / w.mean())
    return np.linalg.lstsq(X * scaled[:, None], y * scaled, rcond=None)[0]


def _point(value, unit, n, **extra):
    value = float(value)
    if not np.isfinite(value):
        raise ValueError("Nonfinite analytical result")
    return dict(status="estimated", estimate=value, unit=unit, n=int(n),
                point_direction="positive" if value > 0 else "negative" if value < 0 else "zero",
                uncertainty="not_estimated", **extra)


def evaluate_points(observed: pd.DataFrame, outcome: pd.Series, weights: pd.Series, case: str):
    """Arguments must have the same unique record-ID index; no positional joins."""
    if case not in {"nhanes_insulin", "pns_hba1c"}:
        raise ValueError("Unknown task")
    if not observed.index.is_unique or observed.index.hasnans:
        raise ValueError("Observed record IDs must be unique and nonmissing")
    if not observed.index.equals(outcome.index) or not observed.index.equals(weights.index):
        raise ValueError("Outcome/weight index must exactly match observed record IDs and order")
    required = ["age", "sex", "bmi"] + (["glucose_mg_dl"] if case == "nhanes_insulin" else [])
    if not set(required).issubset(observed.columns):
        raise ValueError("Missing observed analysis columns")
    z = observed[required].to_numpy(dtype=float)
    y = outcome.to_numpy(dtype=float)
    w = weights.to_numpy(dtype=float)
    if len(y) == 0 or not (np.isfinite(z).all() and np.isfinite(y).all() and np.isfinite(w).all()):
        raise ValueError("Empty or nonfinite input")
    if (w <= 0).any() or (observed.bmi <= 0).any():
        raise ValueError("Nonpositive weights or BMI")
    if case == "nhanes_insulin" and (y <= 0).any():
        raise ValueError("Nonpositive insulin cannot enter the declared log analysis")
    if not observed.sex.isin([1, 2]).all() or not observed.age.between(20, 79).all():
        raise ValueError("Unexpected age or sex coding")
    age = observed.age.to_numpy(dtype=float)
    bmi = observed.bmi.to_numpy(dtype=float)
    A, B = (age - 50) / 10, (bmi - 25) / 5
    F = (observed.sex.to_numpy() == 2).astype(float)
    base = np.column_stack([np.ones(len(y)), A, B, F])
    transformed = np.log(y) if case == "nhanes_insulin" else y.copy()
    unit = "natural_log_insulin_uU_mL" if case == "nhanes_insulin" else "HbA1c_percentage_points"
    if case == "nhanes_insulin":
        glucose = observed.glucose_mg_dl.to_numpy(dtype=float)
        if (glucose <= 0).any():
            raise ValueError("Nonpositive fasting glucose")
        base = np.column_stack([base, np.log(glucose / 100)])
    models = {"adjusted": base, "bmi_curve": np.column_stack([base, B * B]),
              "sex_bmi": np.column_stack([base, F * B])}
    definitions = {
        "adjusted_age_per10": ("adjusted", 1, 1., "primary"),
        "adjusted_bmi_per5": ("adjusted", 2, 1., "primary"),
        "bmi_curvature_second_difference": ("bmi_curve", -1, 2., "primary"),
        "female_minus_male_bmi_slope_per5": ("sex_bmi", -1, 1., "primary"),
        "adjusted_female_minus_male": ("adjusted", 3, 1., "secondary"),
    }
    fitted, failures = {}, {}
    for name, X in models.items():
        try:
            fitted[name] = wls_point(X, transformed, w)
        except Nonestimable as error:
            failures[name] = str(error)
    results = {}
    for name, (model, term, scale, tier) in definitions.items():
        if model in failures:
            results[name] = dict(status="nonestimable", reason=failures[model], tier=tier, n=len(y))
        else:
            results[name] = _point(scale * fitted[model][term], unit, len(y), tier=tier)
    results["weighted_arithmetic_mean"] = _point(np.average(y, weights=w),
        "insulin_uU_mL" if case == "nhanes_insulin" else "HbA1c_percent", len(y), tier="diagnostic")
    if case == "nhanes_insulin":
        # HOMA1 approximation, not HOMA2 and not an independent measured endpoint.
        homa = y * glucose / 405.0
        results["derived_homa1_ir_mean"] = _point(np.average(homa, weights=w), "HOMA1_IR", len(y),
            tier="derived_use_demonstration", independent_biological_validation=False)
    for low, high in [(20, 40), (40, 60), (60, 80)]:
        for sex in [1, 2]:
            for group, lower, upper in [("lt25", 0., 25.), ("25lt30", 25., 30.), ("ge30", 30., np.inf)]:
                mask = (age >= low) & (age < high) & (observed.sex.to_numpy() == sex) & (bmi >= lower) & (bmi < upper)
                key = f"cell_age{low}_{high-1}_sex{sex}_bmi{group}_mean"
                n = int(mask.sum())
                results[key] = (_point(np.average(y[mask], weights=w[mask]),
                    "insulin_uU_mL" if case == "nhanes_insulin" else "HbA1c_percent", n,
                    tier="secondary_cell", sparse_n_lt30=n < 30) if n else
                    dict(status="nonestimable", reason="Empty prespecified cell", n=0, tier="secondary_cell"))
    return results
