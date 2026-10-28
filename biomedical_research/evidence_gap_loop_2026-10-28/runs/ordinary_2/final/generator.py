"""Externally anchored stochastic HDL model; no target HDL fitting or access."""

import numpy as np
import pandas as pd


def generate(observed: pd.DataFrame, evidence: dict, seed: int) -> pd.DataFrame:
    """Generate HDL in mg/dL, preserving input values and row order.

    `evidence` is the model specification containing the parameters dictionary.
    All source-to-parameter bridges are documented in model_spec.json.
    """
    cols = ["row_id", "bmi", "age", "sex"]
    if not set(cols).issubset(observed.columns):
        raise ValueError("Required observed columns are missing")
    out = observed.loc[:, cols].copy(deep=True)
    bmi = observed["bmi"].to_numpy(dtype=float)
    age = observed["age"].to_numpy(dtype=float)
    sex = observed["sex"].to_numpy(dtype=float)
    if not (np.isfinite(bmi).all() and np.isfinite(age).all()
            and np.isfinite(sex).all() and (bmi > 0).all()
            and np.isin(sex, [1, 2]).all()):
        raise ValueError("Invalid observed predictors")
    p = evidence["parameters"]
    male = sex == 1

    def by_sex(name):
        return np.where(male, p[name]["1"], p[name]["2"])

    mean = by_sex("reference_hdl_mean_mgdl")
    sd = by_sex("reference_hdl_sd_mgdl")
    bmi_mean = by_sex("reference_bmi_mean")
    bmi_sd = by_sex("reference_bmi_sd")
    age_slope = by_sex("log_hdl_age_slope_per_year")
    # Gaussian-copula identity; 2, pi and 6 are mathematical constants.
    rho = 2 * np.sin(np.pi * p["partial_spearman_bmi_hdl"] / 6)
    marginal_log_variance = np.log1p((sd / mean) ** 2)
    after_age_variance = marginal_log_variance - (
        age_slope * p["reference_age_sd_years"]
    ) ** 2
    if (after_age_variance <= 0).any() or abs(rho) >= 1:
        raise ValueError("The specification implies a nonpositive residual variance")
    bmi_slope = rho * np.sqrt(after_age_variance) / bmi_sd
    residual_log_sd = np.sqrt((1 - rho ** 2) * after_age_variance)
    log_location = (
        np.log(mean) - marginal_log_variance / 2
        + bmi_slope * (bmi - bmi_mean)
        + age_slope * (age - p["reference_age_mean_years"])
    )
    rng = np.random.default_rng(seed)
    out["hdl"] = np.exp(log_location + residual_log_sd * rng.standard_normal(len(out)))
    if not (np.isfinite(out["hdl"]).all() and (out["hdl"] > 0).all()):
        raise ValueError("HDL numerical overflow or underflow outside supported predictor range")
    return out
