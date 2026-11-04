"""Generated-only scientific diagnostics for the two live integration requests.

No reference files, prior effects, generator imports or model calls occur here.
HC3-t intervals condition on a particular synthetic law and draw.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

REQUESTS = {
    "A": {"predictors": ["bmi", "age", "female"], "primary": "bmi"},
    "B": {"predictors": ["bmi", "glucose", "age", "female"], "primary": "bmi"},
}
UNITS = {"age": "year", "female": "1", "bmi": "kg/m^2", "glucose": "mmol/L", "hba1c": "%"}
INTERVAL_MEANING = "HC3-t 95% conditional synthetic-draw interval; not source, structural, transport or patient uncertainty."


def analyze_generated(frame: pd.DataFrame, request_id: str) -> dict:
    if request_id not in REQUESTS:
        raise ValueError("Unknown request")
    predictors = REQUESTS[request_id]["predictors"]
    variables = ["age", "female", "bmi", "hba1c"] + (["glucose"] if request_id == "B" else [])
    if not frame.columns.is_unique or not set(variables) <= set(frame):
        raise ValueError("Missing or duplicate scientific columns")
    values = frame[variables].apply(pd.to_numeric, errors="raise").astype(float)
    quality = {
        "nonfinite": {v: int((~np.isfinite(values[v])).sum()) for v in variables},
        "out_of_age_scope": int((~values["age"].between(35, 74)).sum()),
        "invalid_female": int((~values["female"].isin([0, 1])).sum()),
        "nonpositive_bmi": int((values["bmi"] <= 0).sum()),
        "nonpositive_glycemia": {v: int((values[v] <= 0).sum()) for v in variables if v in ("hba1c", "glucose")},
    }
    invalid = any(quality["nonfinite"].values()) or quality["out_of_age_scope"] or quality["invalid_female"] or quality["nonpositive_bmi"] or any(quality["nonpositive_glycemia"].values())
    result = {"request_id": request_id, "n": len(frame), "quality": quality,
              "status": "withheld" if invalid else "complete", "coefficients": {},
              "marginal": {}, "relationships": {}, "interval_meaning": INTERVAL_MEANING,
              "reference_read": False}
    if invalid or len(frame) < 100:
        result["status"] = "withheld"
        result["reason"] = "invalid_or_nonpositive_measurements_no_row_deletion" if invalid else "insufficient_n"
        return result
    for v in variables:
        s = values[v]
        q = s.quantile([.1, .5, .9], interpolation="linear")
        result["marginal"][v] = {"mean": float(s.mean()), "sd": float(s.std(ddof=1)),
                                 "q10": float(q.iloc[0]), "median": float(q.iloc[1]),
                                 "q90": float(q.iloc[2]), "unit": UNITS[v]}
    for x in ["bmi"] + (["glucose"] if request_id == "B" else []):
        if len(values) > 1 and values[x].nunique() > 1 and values["hba1c"].nunique() > 1:
            result["relationships"][x + "_hba1c"] = {
                "pearson": float(stats.pearsonr(values[x], values["hba1c"]).statistic),
                "spearman": float(stats.spearmanr(values[x], values["hba1c"]).statistic)}
        else:
            result["relationships"][x + "_hba1c"] = {"pearson": None, "spearman": None, "reason": "constant_or_insufficient_pair"}
    terms = ["const"] + predictors
    x = np.column_stack([np.ones(len(values)), values[predictors].to_numpy()])
    n, k = x.shape
    rank = int(np.linalg.matrix_rank(x))
    condition = float(np.linalg.cond(x))
    result["design"] = {"predictors": predictors, "intercept": True, "rank": rank,
                        "columns": k, "condition_number": condition if np.isfinite(condition) else None}
    if n < 100 or rank != k or n <= k:
        result["status"] = "regression_unavailable"
        result["reason"] = "insufficient_n_or_rank"
        return result
    y = values["hba1c"].to_numpy()
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    pinv = np.linalg.pinv(x)
    residual = y - x @ beta
    leverage = np.sum(x * pinv.T, axis=1)
    valid_hc3 = bool(np.all(1 - leverage > np.finfo(float).eps))
    if valid_hc3:
        weights = (residual / (1 - leverage)) ** 2
        covariance = (pinv * weights) @ pinv.T
        variances = np.diag(covariance)
        valid_hc3 = bool(np.isfinite(variances).all() and (variances >= 0).all())
    if valid_hc3:
        standard_errors = np.sqrt(variances)
        half_width = stats.t.ppf(.975, n - k) * standard_errors
    for position, term in enumerate(terms):
        coef = float(beta[position])
        se = float(standard_errors[position]) if valid_hc3 else float("nan")
        lo = coef - float(half_width[position]) if valid_hc3 else float("nan")
        hi = coef + float(half_width[position]) if valid_hc3 else float("nan")
        available = np.isfinite([coef, se, lo, hi]).all()
        result["coefficients"][term] = {
            "value": coef if np.isfinite(coef) else None,
            "standard_error": se if np.isfinite(se) else None,
            "lower": lo if available else None, "upper": hi if available else None,
            "interval_status": "available" if available else "unavailable",
            "unit": "%" if term == "const" else "%/" + UNITS[term],
            "role": "primary" if term == "bmi" else "intercept" if term == "const" else "secondary",
            "sign": "positive" if coef > 0 else "negative" if coef < 0 else "zero",
            "interval_direction": ("positive" if lo > 0 else "negative" if hi < 0 else "inconclusive") if available else "unavailable",
        }
    return result


def diagnose_csv(path, request_id):
    frame = pd.read_csv(path, dtype={"person_id": "string"}, float_precision="round_trip")
    return analyze_generated(frame, request_id)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--request-id", choices=tuple(REQUESTS), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    result = diagnose_csv(args.csv, args.request_id)
    output = Path(args.output)
    with output.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2, allow_nan=False); f.write("\n")
    print(json.dumps({"status": result["status"], "n": result["n"], "request_id": args.request_id, "reference_read": False}))


if __name__ == "__main__":
    main()
