"""Prior-only artificial cohort; no observed rows or external information."""

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Return one IID cohort conditional on the fixed declared assumptions."""
    if observed is not None:
        raise ValueError("This whole-cohort model requires observed=None")
    p = spec["parameters"]
    if p["distribution_family"] != "bivariate_normal":
        raise ValueError("Unsupported distribution family")
    if p["parameter_uncertainty"] != "fixed_scenario":
        raise ValueError("Only the declared fixed scenario is implemented")
    n = int(p["n_rows"])
    probability = float(p["probability_g1"])
    if n <= 0 or not 0.0 <= probability <= 1.0:
        raise ValueError("Invalid cohort size or group probability")
    rng = np.random.default_rng(seed)
    g = rng.binomial(1, probability, size=n).astype(np.int64)
    mu_x = np.asarray(p["x_mean_by_g"], dtype=float)[g]
    mu_y = np.asarray(p["y_mean_by_g"], dtype=float)[g]
    sd_x = np.asarray(p["x_sd_by_g"], dtype=float)[g]
    sd_y = np.asarray(p["y_sd_by_g"], dtype=float)[g]
    rho = np.asarray(p["xy_correlation_by_g"], dtype=float)[g]
    if np.any(sd_x <= 0) or np.any(sd_y <= 0) or np.any(np.abs(rho) >= 1):
        raise ValueError("Invalid conditional dispersion or correlation")
    innovations = rng.standard_normal((n, 2))
    x = mu_x + sd_x * innovations[:, 0]
    y = mu_y + sd_y * (
        rho * innovations[:, 0] + np.sqrt(1.0 - rho * rho) * innovations[:, 1]
    )
    return pd.DataFrame({
        "row_id": ["row_" + str(i + 1) for i in range(n)],
        "g": g,
        "x": x,
        "y": y,
    }, columns=["row_id", "g", "x", "y"])
