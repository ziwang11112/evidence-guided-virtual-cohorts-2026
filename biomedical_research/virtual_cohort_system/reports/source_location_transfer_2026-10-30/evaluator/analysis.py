"""M11 descriptive point estimators. No outcome access or generator execution."""
from __future__ import annotations

import numpy as np
import pandas as pd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vectors(y, w):
    y, w = np.asarray(y, dtype=float), np.asarray(w, dtype=float)
    require(y.ndim == w.ndim == 1 and len(y) == len(w) > 0, "Invalid vector dimensions")
    require(np.isfinite(y).all() and np.isfinite(w).all(), "Nonfinite values")
    require((w > 0).all(), "Weights must be positive")
    # Rescaling preserves the estimand and prevents accumulation overflow.
    w = w / w.max()
    require(np.isfinite(w.sum()) and w.sum() > 0, "Invalid total weight")
    return y, w


def weighted_quantile(y, w, probability):
    require(np.isfinite(probability) and 0 <= probability <= 1, "Invalid quantile")
    y, w = vectors(y, w)
    values, inverse = np.unique(y, return_inverse=True)
    mass = np.bincount(inverse, weights=w, minlength=len(values))
    cumulative = np.cumsum(mass)
    index = np.searchsorted(cumulative, probability * cumulative[-1], side="left")
    return float(values[min(int(index), len(values) - 1)])


def weighted_mean(y, w):
    y, w = vectors(y, w)
    result = float(np.dot(y, w / w.sum()))
    require(np.isfinite(result), "Nonfinite weighted mean")
    return result


def require_aligned(frame, ids, columns):
    require(list(frame.columns) == columns, "Aligned table column mismatch")
    require(frame.row_id.notna().all() and frame.row_id.is_unique, "Invalid aligned IDs")
    require(np.array_equal(frame.row_id.to_numpy(), np.asarray(ids)), "Row ID order mismatch")


def points(observed, outcome, weight):
    require(isinstance(observed, pd.DataFrame), "Observed must be a table")
    y, w = vectors(outcome, weight)
    require(len(observed) == len(y), "Row length mismatch")
    require(list(observed.columns) == ["row_id", "age_years", "sex", "bmi_kg_m2"], "Visible column contract")
    require(observed.row_id.notna().all() and observed.row_id.is_unique, "Invalid IDs")
    require(observed.sex.isin(["male", "female"]).all(), "Invalid sex")
    age = observed.age_years.to_numpy(dtype=float)
    bmi = observed.bmi_kg_m2.to_numpy(dtype=float)
    require(np.isfinite(age).all() and np.isfinite(bmi).all(), "Nonfinite covariates")
    require(((age >= 20) & (age <= 79) & (age == np.floor(age))).all(), "Age outside protocol")
    require((bmi > 0).all(), "Nonpositive BMI")
    result = {}
    for sex in ["male", "female"]:
        take = observed.sex.eq(sex).to_numpy()
        if take.any():
            result[f"median_{sex}"] = weighted_quantile(y[take], w[take], .5)
        else:
            result[f"median_{sex}"] = None
        for lo, hi in [(20,39),(40,59),(60,79)]:
            cell = take & (age >= lo) & (age <= hi)
            name = f"mean_{sex}_{lo}_{hi}"
            result[name] = weighted_mean(y[cell], w[cell]) if cell.any() else None
            result[name + "_n"] = int(cell.sum())
    result["q90_all"] = weighted_quantile(y, w, .9)
    result["mean_all"] = weighted_mean(y, w)
    x = np.column_stack([np.ones(len(y)), age/10, bmi/5, observed.sex.eq("female").astype(float)])
    xw, yw = x*np.sqrt(w)[:,None], y*np.sqrt(w)
    if np.linalg.matrix_rank(xw) == x.shape[1]:
        beta = np.linalg.lstsq(xw, yw, rcond=None)[0]
        require(np.isfinite(beta).all(), "Nonfinite WLS estimates")
        for name, value in zip(["intercept","age_per_10y","bmi_per_5","female_offset"], beta):
            result[name] = float(value)
    else:
        result.update({name: None for name in ["intercept","age_per_10y","bmi_per_5","female_offset"]})
    return result


def errors(reference, generated):
    primary = ["median_male", "median_female"]
    reuse = [f"mean_{s}_{lo}_{hi}" for s in ["male","female"] for lo,hi in [(20,39),(40,59),(60,79)]]
    def error(k):
        return None if reference[k] is None or generated[k] is None else abs(generated[k] - reference[k])
    p, r = [error(k) for k in primary], [error(k) for k in reuse]
    return {
        "sex_median_mae": None if any(v is None for v in p) else float(np.mean(p)),
        "age_sex_cell_mean_mae": None if any(v is None for v in r) else float(np.mean(r)),
        "q90_absolute_error": error("q90_all"),
        "age_slope_absolute_error": error("age_per_10y"),
        "bmi_slope_absolute_error": error("bmi_per_5"),
    }


def preservation(initial, revised, tolerance=1e-10):
    result={}
    for key in ["age_per_10y", "bmi_per_5"]:
        a,b=initial[key],revised[key]
        delta=None if a is None or b is None else float(b-a)
        if delta is not None:
            require(np.isfinite(delta),"Nonfinite preservation delta")
        result[key+"_change"]=delta
        result[key+"_preserved"]=None if delta is None else abs(delta)<=tolerance
    return result
