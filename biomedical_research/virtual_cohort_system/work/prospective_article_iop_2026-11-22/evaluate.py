"""Recompute the two registered IOP analyses on paired eye-level measurements."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ABS_TOL_MMHG = 1e-10
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_SEED = 20261122


def strict_over_three(difference):
    at_three = np.isclose(difference, 3.0, rtol=0.0, atol=ABS_TOL_MMHG)
    return (difference > 3.0) & ~at_three, at_three


def bootstrap_intervals(pascal, goldmann):
    """Paired participant resampling, percentile limits, primary endpoints and means."""
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    difference = pascal - goldmann
    above, _ = strict_over_three(difference)
    draws = np.empty((BOOTSTRAP_REPLICATES, 4))
    for b in range(BOOTSTRAP_REPLICATES):
        idx = rng.integers(len(difference), size=len(difference))
        draws[b] = [np.mean(pascal[idx]), np.mean(goldmann[idx]),
                    np.mean(difference[idx]), 100 * np.mean(above[idx])]
    bounds = np.quantile(draws, [0.025, 0.975], axis=0).T
    keys = ("pascal_mean_mmhg", "goldmann_mean_mmhg", "mean_difference_mmhg",
            "signed_gt_3_pct")
    return {"resamples": BOOTSTRAP_REPLICATES, "seed": BOOTSTRAP_SEED,
            "unit": "paired participant", "method": "percentile, numpy linear quantile",
            "interval_95": dict(zip(keys, bounds.tolist()))}


def evaluate(frame, pascal_column, goldmann_column, *, measured=False, id_column=None):
    if pascal_column == goldmann_column:
        raise ValueError("Two distinct measurement columns are required")
    if not frame.columns.is_unique:
        raise ValueError("The input must have unique column labels")
    values = frame[[pascal_column, goldmann_column]].apply(pd.to_numeric, errors="raise")
    complete = values.notna().all(axis=1)
    if id_column:
        ids = frame.loc[complete, id_column]
        if ids.isna().any() or ids.duplicated().any():
            raise ValueError("Expected one complete left-eye pair per participant identifier")
    paired = values.loc[complete].to_numpy(dtype=float)
    if len(paired) < 2 or not np.isfinite(paired).all():
        raise ValueError("Need at least two complete finite paired measurements")
    pascal, goldmann = paired.T
    n = len(pascal)
    difference = pascal - goldmann
    above, ties = strict_over_three(difference)
    abs_difference = np.abs(difference)
    extreme = (abs_difference > 4.0) | np.isclose(abs_difference, 4.0, atol=ABS_TOL_MMHG,
                                                 rtol=0.0)
    high = int(np.sum(extreme & (difference > 0)))
    low = int(np.sum(extreme & (difference < 0)))
    varying = np.ptp(pascal) > 0 and np.ptp(goldmann) > 0
    correlation = float(np.corrcoef(pascal, goldmann)[0, 1]) if varying else None
    output = {
        "columns": {"pascal": pascal_column, "goldmann": goldmann_column},
        "n_input": len(frame), "n_complete": n, "n_incomplete": len(frame) - n,
        "comparison_abs_tolerance_mmhg": ABS_TOL_MMHG,
        "pascal_mean_mmhg": float(pascal.mean()), "goldmann_mean_mmhg": float(goldmann.mean()),
        "pascal_sd_mmhg": float(pascal.std(ddof=1)), "goldmann_sd_mmhg": float(goldmann.std(ddof=1)),
        "pearson_r": correlation, "mean_difference_mmhg": float(difference.mean()),
        "difference_sd_mmhg": float(difference.std(ddof=1)),
        "signed_gt_3_n": int(above.sum()), "signed_gt_3_pct": float(100 * above.mean()),
        "signed_equal_3_n": int(ties.sum()), "signed_equal_3_pct": float(100 * ties.mean()),
        "abs_ge_4_n": high + low, "abs_ge_4_pct": float(100 * extreme.mean()),
        "among_abs_ge_4_pascal_higher_n": high, "among_abs_ge_4_goldmann_higher_n": low,
        "positive_pressure_check": {
            "pascal_nonpositive_n": int(np.sum(pascal <= 0)),
            "goldmann_nonpositive_n": int(np.sum(goldmann <= 0)),
            "either_nonpositive_n": int(np.sum((pascal <= 0) | (goldmann <= 0))),
            "pascal_min_max_mmhg": [float(pascal.min()), float(pascal.max())],
            "goldmann_min_max_mmhg": [float(goldmann.min()), float(goldmann.max())],
        },
    }
    if measured:
        output["paired_bootstrap"] = bootstrap_intervals(pascal, goldmann)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path, help="One row per participant, values in mmHg")
    parser.add_argument("--columns", nargs=2, required=True, metavar=("PASCAL", "GOLDMANN"))
    parser.add_argument("--id-column")
    parser.add_argument("--measured", action="store_true", help="Add paired bootstrap intervals")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    frame = pd.read_csv(args.table, float_precision="round_trip")
    report = evaluate(frame, *args.columns, measured=args.measured, id_column=args.id_column)
    report["input_sha256"] = hashlib.sha256(args.table.read_bytes()).hexdigest()
    result = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        print(result, end="")
    elif args.output.exists():
        if args.output.read_text(encoding="utf-8") != result:
            parser.error("An existing output differs; supply a new path")
    else:
        args.output.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
