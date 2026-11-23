"""Independent row-level replay of the Gólczewski et al. lung development case.

Canonical inputs are sex (F or M), fev1_l and fvc_l. The caller verifies the
agent's mapping before using this evaluator. Only aggregate output is returned.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


# Original article, Tables 1 and 2. Table 2's first column is unadjusted.
FIELDS = ("fev1_mean_l", "fev1_sd_l", "fvc_mean_l", "fvc_sd_l",
          "pearson_r", "ols_slope", "ols_intercept_l", "r_squared_pct")
PRECISION = dict(zip(FIELDS, (.1, .1, .1, .1, .01, .01, .01, .1)))
SOURCE = {
    "F": dict(zip(FIELDS, (2.4, .7, 3.1, .8, .96, .84, -.23, 92.0))),
    "M": dict(zip(FIELDS, (3.4, 1.0, 4.5, 1.2, .96, .84, -.36, 93.1))),
}
SOURCE_N = {"F": 1625, "M": 1120}


def rounding_replay(value, center, step):
    inside = None if value is None else bool(center - step / 2 <= value < center + step / 2)
    return {"rows": value, "source": center, "printed_step": step,
            "difference": None if value is None else value - center,
            "inside_printed_rounding_bin": inside}


def summarize_group(x, y, reference):
    n = len(x)
    xbar, ybar = float(x.mean()), float(y.mean())
    x0, y0 = x - xbar, y - ybar
    intercept, slope, r, r_squared = None, None, None, None
    if n > 1 and y.max() > y.min():
        design = np.column_stack([np.ones(n), y])
        intercept, slope = np.linalg.lstsq(design, x, rcond=None)[0].tolist()
        if x.max() > x.min():
            r = float(np.corrcoef(x, y)[0, 1])
            sse = np.square(x0 - slope * y0).sum()
            r_squared = float(100 * (1 - sse / np.square(x0).sum()))
    sd_x = float(x.std(ddof=1)) if n > 1 else None
    sd_y = float(y.std(ddof=1)) if n > 1 else None
    values = dict(zip(FIELDS, (xbar, sd_x, ybar, sd_y, r, slope, intercept, r_squared)))
    replay = {k: rounding_replay(v, reference[k], PRECISION[k]) for k, v in values.items()}
    ratios = x / y
    return {
        "n": n, "threshold_count": int((ratios < .70).sum()),
        "equal_to_threshold_count": int((ratios == .70).sum()),
        "threshold_pct": float(100 * (ratios < .70).mean()),
        "within_0_005_of_cutoff_pct": float(100 * (np.abs(ratios - .70) <= .005).mean()),
        "fev1_exceeding_fvc": int((x > y).sum()),
        "source_replay": replay, "sd_denominator": "n-1",
        "sd_l_population_convention": {"fev1": float(x.std()), "fvc": float(y.std())},
    }


def evaluate(frame):
    if not {"sex", "fev1_l", "fvc_l"} <= set(frame.columns):
        raise ValueError("Expected sex, fev1_l and fvc_l using the reviewed units")
    group = frame["sex"]
    values = frame[["fev1_l", "fvc_l"]].apply(pd.to_numeric, errors="coerce")
    finite = np.isfinite(values.to_numpy()).all(axis=1)
    positive = (values.to_numpy() > 0).all(axis=1)
    recognized = group.isin(SOURCE)
    counts = {s: int((group == s).sum()) for s in SOURCE}
    result = {
        "n_rows": len(frame), "source_n_by_sex": SOURCE_N, "generated_n_by_sex": counts,
        "unknown_or_missing_sex": int((~recognized).sum()), "rows_with_nonfinite_volume": int((~finite).sum()),
        "rows_with_nonpositive_finite_volume": int((finite & ~positive).sum()),
        "source_threshold_prevalence": None,
    }
    if not (len(frame) and recognized.all() and finite.all() and positive.all() and min(counts.values()) > 0):
        result["status"] = "invalid_input_no_row_substitution"
        return result
    strata = {}
    for sex, ref in SOURCE.items():
        x, y = values.loc[group == sex].to_numpy().T
        strata[sex] = summarize_group(x, y, ref)
    num = sum(c["source_replay"]["fev1_mean_l"]["rows"] for c in strata.values())
    den = sum(c["source_replay"]["fvc_mean_l"]["rows"] for c in strata.values())
    k = len(strata)
    replay_fail = [f"{sex}.{key}" for sex, info in strata.items()
                   for key, value in info["source_replay"].items()
                   if value["inside_printed_rounding_bin"] is not True]
    a = sum(ref["fev1_mean_l"] for ref in SOURCE.values())
    b = sum(ref["fvc_mean_l"] for ref in SOURCE.values())
    half_sum = k * PRECISION["fev1_mean_l"] / 2
    assert PRECISION["fev1_mean_l"] == PRECISION["fvc_mean_l"]
    result.update({
        "status": "computed", "sex": strata, "source_replay_outside_or_undefined": replay_fail,
        "source_replay_inside_count": len(strata) * len(FIELDS) - len(replay_fail),
        "nonphysical_rows_fev1_exceeding_fvc": sum(c["fev1_exceeding_fvc"] for c in strata.values()),
        "equal_sex_threshold_pct": sum(c["threshold_pct"] for c in strata.values()) / k,
        "equal_sex_ratio_of_means_pct": 100 * num / den,
        "source_ratio_from_printed_means_pct": 100 * a / b,
        "outer_interval_from_table1_rounding_alone_pct": [100 * (a-half_sum) / (b+half_sum),
                                                          100 * (a+half_sum) / (b-half_sum)],
    })
    assert math.isfinite(result["equal_sex_ratio_of_means_pct"])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical_table", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(pd.read_csv(args.canonical_table, float_precision="round_trip"))
    text = json.dumps(result, indent=2, allow_nan=False)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf8")
    else:
        print(text)
