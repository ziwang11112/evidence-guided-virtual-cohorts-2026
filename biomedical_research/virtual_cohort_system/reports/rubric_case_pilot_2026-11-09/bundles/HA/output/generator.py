"""HA whole-cohort construction. No observations or external state are used."""

import numpy as np
import pandas as pd


def _truncated_lognormal(rng, count, mean_before_truncation, cv, lower, upper):
    log_variance = np.log1p(cv * cv)
    log_mean = np.log(mean_before_truncation) - log_variance / 2.0
    log_sd = np.sqrt(log_variance)
    result = np.empty(count, dtype=float)
    pending = np.arange(count)
    while pending.size:
        proposal = rng.lognormal(log_mean, log_sd, size=pending.size)
        keep = np.isfinite(proposal) & (proposal >= lower) & (proposal < upper)
        result[pending[keep]] = proposal[keep]
        pending = pending[~keep]
    return result


def _truncated_normal(rng, location, sd, lower, upper):
    result = np.empty(location.size, dtype=float)
    pending = np.arange(location.size)
    while pending.size:
        proposal = rng.normal(location[pending], sd, size=pending.size)
        keep = np.isfinite(proposal) & (proposal >= lower) & (proposal < upper)
        result[pending[keep]] = proposal[keep]
        pending = pending[~keep]
    return result


def _truncated_student(rng, location, sd_before_truncation, df, lower, upper):
    scale = sd_before_truncation * np.sqrt((df - 2.0) / df)
    result = np.empty(location.size, dtype=float)
    pending = np.arange(location.size)
    while pending.size:
        proposal = location[pending] + scale * rng.standard_t(df, size=pending.size)
        keep = np.isfinite(proposal) & (proposal >= lower) & (proposal < upper)
        result[pending[keep]] = proposal[keep]
        pending = pending[~keep]
    return result


def generate(observed, specification, seed):
    """Return the selected-population joint draw under the supplied specification."""
    if observed is not None:
        raise ValueError("HA is a whole-cohort task; observed must be None")
    rng = np.random.default_rng(seed)
    design = specification["design"]
    p = specification["parameters"]
    age_parts = []
    sex_parts = []
    for sex in design["female_values"]:
        for lower_age, upper_age in design["age_bands_inclusive"]:
            count = design["rows_per_cell"]
            age_parts.append(rng.integers(lower_age, upper_age + 1, size=count))
            sex_parts.append(np.full(count, sex, dtype=np.int64))
    age = np.concatenate(age_parts)
    female = np.concatenate(sex_parts)
    n = age.size
    if n != design["n_rows"]:
        raise ValueError("Cell sizes do not match the declared row count")

    b = p["bmi"]
    bmi = _truncated_lognormal(
        rng, n, b["mean_before_truncation"], b["cv_before_truncation"],
        b["lower_inclusive"], b["upper_exclusive"]
    )
    g = p["glucose"]
    glucose_location = (
        g["reference_location"]
        + g["age_per_year"] * (age - p["reference_age"])
        + g["male_minus_female"] * (p["reference_female"] - female)
        + g["bmi_per_unit"] * (bmi - p["reference_bmi"])
    )
    glucose = _truncated_normal(
        rng, glucose_location, g["sd_before_truncation"],
        g["lower_inclusive"], g["upper_exclusive"]
    )
    h = p["hba1c"]
    hba1c_location = (
        h["reference_location"]
        + h["age_per_year"] * (age - p["reference_age"])
        + h["female_minus_male"] * female
        + h["bmi_per_unit_conditional"] * (bmi - p["reference_bmi"])
        + h["glucose_per_mgdl"] * (glucose - p["reference_glucose"])
    )
    hba1c = _truncated_student(
        rng, hba1c_location, h["residual_sd_before_truncation"],
        h["residual_df"], h["lower_inclusive"], h["upper_exclusive"]
    )
    result = pd.DataFrame(
        {
            "row_id": [f"{design['row_id_prefix']}-{i + 1:04d}" for i in range(n)],
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": glucose,
            "hba1c": hba1c,
        },
        columns=design["ordered_columns"],
    )
    return result.iloc[rng.permutation(n)].reset_index(drop=True)
