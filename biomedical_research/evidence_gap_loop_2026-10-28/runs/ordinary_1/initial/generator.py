"""External aggregate-evidence HDL generator; no target outcome fitting."""

import numpy as np
import pandas as pd


def generate(observed: pd.DataFrame, evidence: dict, seed: int) -> pd.DataFrame:
    """Return observed fields unchanged and a locally seeded positive HDL draw.

    The evidence argument is model_spec.json, containing a parameters mapping.
    The function does not read files, fit to the supplied cohort, or mutate input.
    """
    p = evidence["parameters"]
    required = ["row_id", "bmi", "age", "sex"]
    if not all(column in observed.columns for column in required):
        raise ValueError("Missing required observed column")
    result = observed.loc[:, required].copy(deep=True)
    bmi = observed["bmi"].to_numpy(dtype=float)
    age = observed["age"].to_numpy(dtype=float)
    sex = observed["sex"].to_numpy()
    if not (np.isfinite(bmi).all() and np.isfinite(age).all()):
        raise ValueError("Observed BMI and age must be finite")
    if not ((bmi > 0).all() and np.isin(sex, [1, 2]).all()):
        raise ValueError("BMI must be positive and sex must be 1 or 2")

    bmi_knots = np.asarray(p["bmi_knots"], dtype=float)
    age_knots = np.asarray(p["age_knots"], dtype=float)
    age_effects = np.asarray(p["age_contrasts"], dtype=float)
    age_counts = np.asarray(p["source_age_counts_by_bmi"], dtype=float)
    age_center = (age_counts @ age_effects) / age_counts.sum(axis=1)
    age_effect = np.interp(age, age_knots, age_effects)
    mean = np.empty(len(result), dtype=float)
    log_variance = np.empty(len(result), dtype=float)
    for code, label in ((1, "male"), (2, "female")):
        selected = sex == code
        source_mean = np.asarray(p["source_hdl_means"][label], dtype=float)
        source_n = np.asarray(p["source_cell_counts"][label], dtype=float)
        source_se = np.asarray(p["source_mean_standard_errors"][label], dtype=float)
        source_sd = source_se * np.sqrt(source_n)
        # Convert arithmetic mean and SD to the exact lognormal variance.
        anchor_log_variance = np.log1p((source_sd / source_mean) ** 2)
        centered_means = source_mean - age_center
        mean[selected] = np.interp(bmi[selected], bmi_knots, centered_means)
        mean[selected] += age_effect[selected]
        # A separately declared longitudinal-to-cross-sectional tail bridge.
        excess = np.maximum(bmi[selected] - bmi_knots[-1], 0)
        mean[selected] *= np.exp(p["tail_log_slopes"][label] * excess)
        log_variance[selected] = np.interp(
            bmi[selected], bmi_knots, anchor_log_variance
        )
    if not (np.isfinite(mean).all() and (mean > 0).all()):
        raise ValueError("Model conditional mean is not finite and positive")
    rng = np.random.default_rng(seed)
    standard_normal = rng.standard_normal(len(result))
    result["hdl"] = np.exp(
        np.log(mean) - log_variance / 2
        + np.sqrt(log_variance) * standard_normal
    )
    return result
