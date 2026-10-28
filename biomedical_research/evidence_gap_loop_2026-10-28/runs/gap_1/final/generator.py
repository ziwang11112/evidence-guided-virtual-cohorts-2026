"""Assumption-based virtual HDL generator; never an observed patient measurement."""

import numpy as np
import pandas as pd


def generate(observed: pd.DataFrame, evidence: dict, seed: int) -> pd.DataFrame:
    """Generate positive HDL in mg/dL, preserving predictors and row order."""
    p = evidence["parameters"]
    out = observed.loc[:, ["row_id", "bmi", "age", "sex"]].copy(deep=True)
    bmi = out["bmi"].to_numpy(dtype=float)
    age = out["age"].to_numpy(dtype=float)
    female = out["sex"].to_numpy() == 2
    slope = np.where(female, p["bmi_log_slopes_by_sex"]["female"],
                     p["bmi_log_slopes_by_sex"]["male"])
    base = np.where(female, p["conditional_means_at_reference_by_sex"]["female"],
                    p["conditional_means_at_reference_by_sex"]["male"])
    sigma = np.where(female, p["residual_log_sd_by_sex"]["female"],
                     p["residual_log_sd_by_sex"]["male"])
    log_age_values = np.log(np.asarray(p["age_relative_means"], dtype=float))
    age_term = np.interp(age, p["age_knots_years"], log_age_values)
    age_center = np.interp(p["age_reference"], p["age_knots_years"], log_age_values)
    log_mean = np.log(base) + slope * (bmi - p["bmi_reference"]) + age_term - age_center
    rng = np.random.default_rng(seed)
    out["hdl"] = rng.lognormal(log_mean - sigma * sigma / 2, sigma)
    return out
