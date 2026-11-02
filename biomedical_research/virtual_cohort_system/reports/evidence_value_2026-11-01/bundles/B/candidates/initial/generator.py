"""Artificial whole-cohort moment completion; no individual data are read."""

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Return an IID target draw under the explicitly assumed Gaussian law."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)
    g = rng.binomial(1, p["target_g_probability"], size=n)
    x_mean = np.asarray(p["x_group_mean"], dtype=float)
    x_sd = np.asarray(p["x_group_sd"], dtype=float)
    intercept = np.asarray(p["y_group_intercept"], dtype=float)
    slope = np.asarray(p["y_group_x_slope"], dtype=float)
    residual_sd = np.asarray(p["y_group_residual_sd"], dtype=float)
    x = x_mean[g] + x_sd[g] * rng.standard_normal(n)
    y = intercept[g] + slope[g] * x + residual_sd[g] * rng.standard_normal(n)
    row_id = [p["identifier_prefix"] + str(i + 1) for i in range(n)]
    return pd.DataFrame({"row_id": row_id, "g": g, "x": x, "y": y})
