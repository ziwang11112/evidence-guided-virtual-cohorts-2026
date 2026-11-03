"""One fixed, assumption-dependent whole-cohort probability law.

This module has no execution entry point, file access, calibration or diagnostics.
"""

import numpy as np
import pandas as pd
from scipy.special import expit, logit


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")

    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = p["n_rows"]

    age_p = p["age"]
    support = np.arange(age_p["minimum"], age_p["maximum"] + 1, dtype=np.int64)
    age_mass = np.exp(-0.5 * ((support - age_p["kernel_center"]) / age_p["kernel_sd"]) ** 2)
    age_mass = age_mass / age_mass.sum()
    age = rng.choice(support, size=n, p=age_mass)
    a = (age - age_p["kernel_center"]) / age_p["regression_scale"]

    female_p = p["female"]
    female_probability = expit(
        logit(female_p["probability_at_age_center"])
        + female_p["log_odds_per_age_scale"] * a
    )
    female = rng.binomial(1, female_probability, size=n).astype(np.int64)
    f = female - female_p["probability_at_age_center"]

    bmi_p = p["bmi"]
    log_bmi = (
        np.log(bmi_p["median_at_reference"])
        + bmi_p["age_linear_log_shift"] * a
        + bmi_p["age_quadratic_log_shift"] * a ** 2
        + bmi_p["female_log_shift"] * f
        + bmi_p["log_sd"] * rng.standard_normal(n)
    )
    bmi = np.exp(log_bmi)
    b = (bmi - bmi_p["glycemic_center"]) / bmi_p["glycemic_scale"]

    state_p = p["high_glycemia_state"]
    state_probability = expit(
        logit(state_p["probability_at_reference"])
        + state_p["age_log_odds"] * a
        + state_p["bmi_log_odds"] * b
        + state_p["female_log_odds"] * f
    )
    state = rng.binomial(1, state_probability, size=n)

    dep_p = p["residual_dependence"]
    rho = dep_p["latent_transport_multiplier"] * 2.0 * np.sin(
        np.pi * dep_p["source_rank_anchor"] / 6.0
    )
    glucose_error = rng.standard_normal(n)
    hba1c_error = (
        rho * glucose_error
        + np.sqrt(1.0 - rho ** 2) * rng.standard_normal(n)
    )

    glucose_p = p["glucose"]
    glucose_median = np.asarray(glucose_p["median_by_state"], dtype=float)[state]
    glucose_log_sd = np.asarray(glucose_p["log_sd_by_state"], dtype=float)[state]
    glucose = np.exp(
        np.log(glucose_median)
        + glucose_p["age_log_shift"] * a
        + glucose_p["bmi_log_shift"] * b
        + glucose_p["female_log_shift"] * f
        + glucose_log_sd * glucose_error
    )

    hba1c_p = p["hba1c"]
    hba1c_median = np.asarray(hba1c_p["median_by_state"], dtype=float)[state]
    hba1c_log_sd = np.asarray(hba1c_p["log_sd_by_state"], dtype=float)[state]
    hba1c = np.exp(
        np.log(hba1c_median)
        + hba1c_p["age_log_shift"] * a
        + hba1c_p["bmi_log_shift"] * b
        + hba1c_p["female_log_shift"] * f
        + hba1c_log_sd * hba1c_error
    )

    return pd.DataFrame(
        {
            "row_id": [f"synthetic_{i + 1:05d}" for i in range(n)],
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": glucose,
            "hba1c": hba1c,
        },
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"],
    )
