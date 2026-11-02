"""Artificial group-conditional Gaussian completion of supplied moments."""

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Return independent rows; distribution shapes are explicit assumptions."""
    if observed is not None:
        raise ValueError("This whole-cohort construction requires observed=None.")
    p = spec["parameters"]
    if p["x_family"] != "normal" or p["residual_family"] != "normal":
        raise ValueError("The submitted construction implements normal families only.")
    if p["sampling_scheme"] != "iid_rows_independent_latent_draws":
        raise ValueError("Unsupported sampling scheme.")
    if p["uncertainty_mode"] != "fixed_parameters_unquantified_structural_uncertainty":
        raise ValueError("Unsupported uncertainty scheme.")

    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)
    g = rng.binomial(1, p["g_probability"], size=n).astype(np.int64)
    x_mean = np.asarray(p["x_mean_by_g"], dtype=float)[g]
    x_sd = np.asarray(p["x_sd_by_g"], dtype=float)[g]
    intercept = np.asarray(p["y_intercept_by_g"], dtype=float)[g]
    slope = np.asarray(p["y_slope_by_g"], dtype=float)[g]
    residual_sd = np.asarray(p["residual_sd_by_g"], dtype=float)[g]
    x = x_mean + x_sd * rng.standard_normal(n)
    residual = residual_sd * rng.standard_normal(n)
    y = intercept + slope * x + residual
    return pd.DataFrame({
        "row_id": [f"row_{i + 1:06d}" for i in range(n)],
        "g": g,
        "x": x,
        "y": y,
    })
