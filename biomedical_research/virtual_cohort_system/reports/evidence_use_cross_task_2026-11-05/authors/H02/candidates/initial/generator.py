"""Reviewed H02 bounded conditional joint law; controller-only execution."""

import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("H02 whole-cohort construction requires observed=None")
    p = specification["parameters"]
    rng = np.random.default_rng(seed)
    ages = []
    females = []
    for female in p["female_levels"]:
        for lower, upper in p["age_bands"]:
            ages.append(rng.integers(lower, upper + 1, size=p["rows_per_cell"]))
            females.append(np.full(p["rows_per_cell"], female, dtype=int))
    age = np.concatenate(ages)
    female = np.concatenate(females)
    n = len(age)
    bmi = p["bmi_lower"] + (p["bmi_upper"] - p["bmi_lower"]) * rng.beta(
        p["bmi_alpha"], p["bmi_beta"], size=n
    )
    glucose_mean = (
        p["glucose_center"]
        + p["glucose_age_coefficient"] * (age - p["age_center"])
        + p["glucose_female_coefficient"] * female
        + p["glucose_bmi_coefficient"] * (bmi - p["bmi_center"])
    )
    glucose_width = p["glucose_upper"] - p["glucose_lower"]
    glucose_fraction = (glucose_mean - p["glucose_lower"]) / glucose_width
    if np.any((glucose_fraction <= 0) | (glucose_fraction >= 1)):
        raise ValueError("Conditional glucose mean is outside its beta support")
    glucose = p["glucose_lower"] + glucose_width * rng.beta(
        p["glucose_precision"] * glucose_fraction,
        p["glucose_precision"] * (1 - glucose_fraction),
    )
    # Floating-point endpoint protection only; no statistical tail clipping.
    glucose = np.minimum(
        glucose, np.nextafter(p["glucose_upper"], p["glucose_lower"])
    )
    hba1c_mean = (
        p["hba1c_intercept"]
        + p["hba1c_age_coefficient"] * (age - p["age_center"])
        + p["hba1c_bmi_coefficient"] * (bmi - p["bmi_center"])
        + p["hba1c_female_coefficient"] * female
        + p["hba1c_glucose_coefficient"] * (glucose - p["glucose_center"])
    )
    residual_alpha = p["hba1c_residual_alpha"]
    residual_beta = p["hba1c_residual_beta"]
    residual_shape_sum = residual_alpha + residual_beta
    residual_mean = residual_alpha / residual_shape_sum
    residual_sd = np.sqrt(
        residual_alpha * residual_beta
        / (residual_shape_sum ** 2 * (residual_shape_sum + 1))
    )
    residual = (
        rng.beta(residual_alpha, residual_beta, size=n) - residual_mean
    ) / residual_sd
    hba1c = hba1c_mean + p["hba1c_residual_sd"] * residual
    return pd.DataFrame(
        {
            "row_id": [f"H02-{i + 1:05d}" for i in range(n)],
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": glucose,
            "hba1c": hba1c,
        }
    )
