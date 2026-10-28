"""Fictional conditional lognormal candidate; execution belongs to the harness."""

import numpy as np


def generate(observed, spec, seed):
    """Preserve observed cells and append a nonnegative conditional outcome."""
    p = spec["parameters"]
    if p["family"] != "lognormal":
        raise ValueError("This candidate implements the declared lognormal family only")
    if p["interpolation"] != "linear_mean_constant_cv":
        raise ValueError("Unsupported interpolation assumption")
    if p["residual_dependence"] != "conditional_iid":
        raise ValueError("Unsupported residual dependence assumption")
    if observed is None or list(observed.columns) != ["record_id", "x", "group"]:
        raise ValueError("Expected enrichment covariates in task order")
    x = observed["x"].to_numpy(dtype=float)
    group = observed["group"].to_numpy(dtype=float)
    mean_y = (p["mean_intercept"] + p["mean_slope"] * x) * (
        p["group_multiplier"] ** group
    )
    cv = p["conditional_cv"]
    if cv <= 0 or not np.all(mean_y > 0):
        raise ValueError("Positive conditional means and coefficient of variation required")
    log_variance = np.log1p(cv * cv)
    log_location = np.log(mean_y) - log_variance / 2
    rng = np.random.default_rng(seed)
    result = observed.copy(deep=True)
    result["y"] = rng.lognormal(
        mean=log_location, sigma=np.sqrt(log_variance), size=len(observed)
    )
    return result
