"""Invented fixture: conditional gamma sampling with observed cells preserved.

This module has no file or network operations. It performs no sampling at import.
"""

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Return a new table; only y is generated, using settings in model_spec."""
    if not isinstance(observed, pd.DataFrame):
        raise TypeError("observed must be a pandas DataFrame")
    if list(observed.columns) != ["record_id", "x", "group"]:
        raise ValueError("observed columns must be record_id, x, group")
    if observed["record_id"].isna().any() or not observed["record_id"].map(lambda v: isinstance(v, str)).all():
        raise ValueError("record_id values must be non-null strings")
    if not observed["record_id"].is_unique:
        raise ValueError("record_id values must be unique")
    x = observed["x"].to_numpy(dtype=float)
    group = observed["group"].to_numpy(dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(group).all():
        raise ValueError("observed numeric values must be finite")
    if np.any((x < 0.0) | (x > 2.0)) or not np.isin(group, [0.0, 1.0]).all():
        raise ValueError("observed values fall outside the fixture domain")

    settings = spec["parameters"]
    if settings["distribution_family"] != "gamma":
        raise ValueError("this program implements only the declared gamma family")
    intercept = float(settings["group0_mean_intercept"])
    slope = float(settings["group0_mean_slope"])
    group1_ratio = float(settings["group1_mean_multiplier"])
    cv = float(settings["individual_coefficient_of_variation"])
    if not np.isfinite([intercept, slope, group1_ratio, cv]).all() or cv <= 0.0:
        raise ValueError("scientific settings must be finite with positive CV")
    mean = (intercept + slope * x) * np.where(group == 1.0, group1_ratio, 1.0)
    if not np.isfinite(mean).all() or np.any(mean <= 0.0):
        raise ValueError("conditional arithmetic means must be positive and finite")
    shape = 1.0 / (cv * cv)
    scale = mean / shape
    rng = np.random.default_rng(seed)
    y = rng.gamma(shape=shape, scale=scale)
    if not np.isfinite(y).all() or np.any(y <= 0.0):
        raise ValueError("gamma sampler returned a nonpositive or nonfinite value")
    result = observed.copy(deep=True)
    result["y"] = y
    return result
