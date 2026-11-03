import numpy as np
import pandas as pd
from scipy.special import expit, logit, ndtri


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")

    p = spec["parameters"]
    c = p["cohort"]
    rng = np.random.default_rng(seed)
    n = int(c["n_rows"])

    age_support = np.arange(c["age_min"], c["age_max"] + 1, dtype=np.int64)
    age_mass = np.exp(-0.5 * ((age_support - c["age_location"]) / c["age_spread"]) ** 2)
    age_mass = age_mass / age_mass.sum()
    age = rng.choice(age_support, size=n, p=age_mass)
    age_term = (age - c["reference_age"]) / c["age_scale_years"]

    s = p["sex"]
    female_probability = expit(
        logit(s["female_probability_at_reference_age"])
        + s["female_log_odds_per_age_scale"] * age_term
    )
    female = (rng.random(n) < female_probability).astype(np.int64)

    b = p["bmi"]
    bmi_log_sd = (
        b["log_spread_multiplier"]
        * np.log(b["reference_q3"] / b["reference_q1"])
        / (2.0 * ndtri(0.75))
    )
    bmi = np.exp(
        np.log(b["median_at_reference_age_male"])
        + b["log_median_age_linear"] * age_term
        + b["log_median_age_quadratic"] * age_term ** 2
        + b["log_median_female_effect"] * female
        + bmi_log_sd * rng.standard_normal(n)
    )
    bmi_term = bmi - c["reference_bmi"]

    k = p["upper_glycaemia_class"]
    upper_probability = expit(
        logit(k["probability_at_reference_male"])
        + k["log_odds_per_age_scale"] * age_term
        + k["log_odds_per_bmi_unit"] * bmi_term
        + k["female_log_odds_effect"] * female
    )
    component = (rng.random(n) < upper_probability).astype(np.int64)

    rho = np.asarray(p["residual_dependence"]["class_gaussian_correlations"])[component]
    shared = rng.standard_normal(n)
    independent = rng.standard_normal(n)
    hba1c_residual = rho * shared + np.sqrt(1.0 - rho ** 2) * independent

    g = p["glucose"]
    glucose = np.exp(
        np.log(np.asarray(g["class_reference_medians"])[component])
        + g["log_median_per_age_scale"] * age_term
        + g["log_median_per_bmi_unit"] * bmi_term
        + g["log_median_female_effect"] * female
        + np.asarray(g["class_log_sds"])[component] * shared
    )

    h = p["hba1c"]
    hba1c = np.exp(
        np.log(np.asarray(h["class_reference_medians"])[component])
        + h["log_median_per_age_scale"] * age_term
        + h["log_median_per_bmi_unit"] * bmi_term
        + h["log_median_female_effect"] * female
        + np.asarray(h["class_log_sds"])[component] * hba1c_residual
    )

    return pd.DataFrame({
        "row_id": [f"E1_A03_{i + 1:06d}" for i in range(n)],
        "age": age,
        "female": female,
        "bmi": bmi,
        "glucose": glucose,
        "hba1c": hba1c,
    }, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
