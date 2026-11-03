import numpy as np
import pandas as pd
from scipy.special import expit, logit, ndtr, ndtri


def generate(observed, spec, seed):
    """Draw one complete cohort from the single declared conditional law."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")

    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)

    pa = p["age"]
    age_support = np.arange(pa["minimum"], pa["maximum"] + 1, dtype=np.int64)
    age_mass = ndtr((age_support + 0.5 - pa["normal_location"]) / pa["normal_scale"])
    age_mass -= ndtr((age_support - 0.5 - pa["normal_location"]) / pa["normal_scale"])
    age_mass = age_mass / age_mass.sum()
    age = rng.choice(age_support, size=n, p=age_mass)
    age_unit = (age - pa["reference"]) / pa["unit_scale"]

    pf = p["female"]
    female_probability = expit(
        logit(pf["reference_probability"]) + pf["age_log_odds_effect"] * age_unit
    )
    female = (rng.random(n) < female_probability).astype(np.int64)
    female_centered = female - pf["reference_probability"]

    pb = p["bmi"]
    bmi_log_sd = np.log(
        pb["dispersion_quartile_upper"] / pb["dispersion_quartile_lower"]
    ) / (2.0 * ndtri(0.75))
    bmi_log_median = (
        np.log(pb["reference_median"])
        + pb["age_log_effect"] * age_unit
        + pb["age_squared_log_effect"] * age_unit**2
        + pb["female_log_effect"] * female_centered
    )
    bmi = np.exp(bmi_log_median + bmi_log_sd * rng.standard_normal(n))
    bmi_unit = (bmi - pb["reference"]) / pb["unit_scale"]

    pe = p["elevated_glycaemia"]
    elevated_probability = expit(
        logit(pe["reference_probability"])
        + pe["age_log_odds_effect"] * age_unit
        + pe["bmi_log_odds_effect"] * bmi_unit
        + pe["female_log_odds_effect"] * female_centered
    )
    component = (rng.random(n) < elevated_probability).astype(np.int64)

    shared = rng.standard_normal(n)
    pc = p["shared_glycaemia"]
    g_loading = pc["glucose_loading"]
    h_loading = pc["hba1c_loading"]
    g_residual = g_loading * shared + np.sqrt(1.0 - g_loading**2) * rng.standard_normal(n)
    h_residual = h_loading * shared + np.sqrt(1.0 - h_loading**2) * rng.standard_normal(n)

    pg = p["glucose"]
    glucose_log_median = (
        np.log(np.asarray(pg["component_medians"], dtype=float)[component])
        + pg["age_log_effect"] * age_unit
        + pg["bmi_log_effect"] * bmi_unit
        + pg["female_log_effect"] * female_centered
    )
    glucose = np.exp(
        glucose_log_median
        + np.asarray(pg["component_log_sd"], dtype=float)[component] * g_residual
    )

    ph = p["hba1c"]
    hba1c_log_median = (
        np.log(np.asarray(ph["component_medians"], dtype=float)[component])
        + ph["age_log_effect"] * age_unit
        + ph["bmi_log_effect"] * bmi_unit
        + ph["female_log_effect"] * female_centered
    )
    hba1c = np.exp(
        hba1c_log_median
        + np.asarray(ph["component_log_sd"], dtype=float)[component] * h_residual
    )

    return pd.DataFrame(
        {
            "row_id": [f"synthetic_{i + 1:06d}" for i in range(n)],
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": glucose,
            "hba1c": hba1c,
        },
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"],
    )
