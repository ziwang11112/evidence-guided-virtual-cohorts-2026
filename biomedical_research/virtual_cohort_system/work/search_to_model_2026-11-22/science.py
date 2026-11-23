"""Independently score paired OCT and ultrasound central corneal thickness measurements."""
import numpy as np
import pandas as pd


THRESHOLD_UM = 20.0
EQUALITY_TOLERANCE_UM = 1e-10
QUANTILES = (0.05, 0.25, 0.50, 0.75, 0.95)


def evaluate(frame, oct_col, us_col):
    """Evaluate matched measurements in micrometers; caller verifies units and eye pairing.

    Means, sample SDs, correlation, quantiles and threshold rates use the same
    complete pairs. Report observed nonpositive readings even on incomplete rows.
    Undefined statistics are None, suitable for strict JSON serialization.
    """
    if oct_col == us_col or not frame.columns.is_unique:
        raise ValueError("Require distinct measurement columns and unique headers")
    for col in (oct_col, us_col):
        if not isinstance(col, str) or not col or col not in frame:
            raise ValueError("A submitted measurement column is absent")
        if col.casefold() in ("id", "row_id") or col.casefold().startswith("diagnostic_"):
            raise ValueError("Identifiers and author diagnostics cannot represent instrument measurements")
        dtype = frame[col].dtype
        if (not pd.api.types.is_numeric_dtype(dtype) or pd.api.types.is_bool_dtype(dtype)
                or pd.api.types.is_complex_dtype(dtype)):
            raise ValueError(f"Expected a real numeric measurement column: {col}")
    raw = frame[[oct_col, us_col]].to_numpy(dtype=float, na_value=np.nan)
    if np.isinf(raw).any():
        raise ValueError("Infinite thickness in input")
    complete = ~np.isnan(raw).any(axis=1)
    oct_values, us_values = raw[complete].T
    n = len(oct_values)
    delta = oct_values - us_values
    absolute = np.abs(delta)
    ties = np.isclose(absolute, THRESHOLD_UM, rtol=0, atol=EQUALITY_TOLERANCE_UM)
    exceed = int(np.sum((absolute > THRESHOLD_UM) & ~ties))
    quantities = {"oct": oct_values, "us": us_values, "difference": delta, "absolute_difference": absolute}
    quantiles = {
        name: dict(zip(("p05", "p25", "p50", "p75", "p95"), np.quantile(values, QUANTILES).tolist()))
        for name, values in quantities.items() if n
    }
    varies = n >= 2 and np.ptp(oct_values) > 0 and np.ptp(us_values) > 0
    return {
        "column_mapping": {"oct": oct_col, "us": us_col}, "unit": "um",
        "n_input": len(frame), "n_complete": n, "n_incomplete": len(frame) - n,
        "fraction_missing": (len(frame) - n) / len(frame) if len(frame) else None,
        "oct_missing_n": int(np.isnan(raw[:, 0]).sum()), "us_missing_n": int(np.isnan(raw[:, 1]).sum()),
        "oct_nonpositive_n": int((raw[:, 0] <= 0).sum()), "us_nonpositive_n": int((raw[:, 1] <= 0).sum()),
        "either_nonpositive_n": int((raw <= 0).any(axis=1).sum()),
        "oct_mean_um": float(oct_values.mean()) if n else None,
        "us_mean_um": float(us_values.mean()) if n else None,
        "oct_sd_um": float(oct_values.std(ddof=1)) if n >= 2 else None,
        "us_sd_um": float(us_values.std(ddof=1)) if n >= 2 else None,
        "pearson_r": float(np.corrcoef(oct_values, us_values)[0, 1]) if varies else None,
        "mean_difference_um": float(delta.mean()) if n else None,
        "difference_sd_um": float(delta.std(ddof=1)) if n >= 2 else None,
        "mean_absolute_difference_um": float(absolute.mean()) if n else None,
        "abs_gt20_n": exceed, "abs_gt20_fraction": exceed / n if n else None,
        "abs_gt20_pct": 100 * exceed / n if n else None, "abs_equal20_n": int(ties.sum()),
        "threshold_um": THRESHOLD_UM, "equality_tolerance_um": EQUALITY_TOLERANCE_UM,
        "sample_quantiles_um": quantiles,
    }
