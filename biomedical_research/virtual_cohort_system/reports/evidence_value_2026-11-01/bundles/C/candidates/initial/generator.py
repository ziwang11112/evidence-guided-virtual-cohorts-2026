"""Artificial moment-constrained cohort; Gaussian families are assumptions."""

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Return one iid whole cohort using only the specification and supplied seed."""
    if observed is not None:
        raise ValueError("This whole-cohort candidate requires observed=None")
    p = spec["parameters"]
    if p["x_family"] != "normal" or p["residual_family"] != "normal":
        raise ValueError("This candidate implements the declared normal families")
    if p["dependence_model"] != "independent_standard_innovations_given_group":
        raise ValueError("Unsupported dependence model")
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)
    g = rng.binomial(1, p["group_probability"], size=n).astype(np.int64)
    x_mean = np.asarray(p["x_group_mean"], dtype=float)[g]
    x_sd = np.asarray(p["x_group_sd"], dtype=float)[g]
    intercept = np.asarray(p["y_group_intercept"], dtype=float)[g]
    slope = np.asarray(p["y_group_slope"], dtype=float)[g]
    residual_sd = np.asarray(p["y_group_residual_sd"], dtype=float)[g]
    x = x_mean + x_sd * rng.standard_normal(n)
    y = intercept + slope * x + residual_sd * rng.standard_normal(n)
    row_ids = [p["row_id_prefix"] + str(i + 1) for i in range(n)]
    return pd.DataFrame({"row_id": row_ids, "g": g, "x": x, "y": y})
