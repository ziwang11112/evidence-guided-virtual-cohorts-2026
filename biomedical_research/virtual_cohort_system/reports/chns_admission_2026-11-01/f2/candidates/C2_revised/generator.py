"""C2 evidence-contextual whole-cohort scenario; execution is controller-owned.

All scientific settings are in model_spec.json. The two mixture components are
distributional devices, not diagnoses. No source processing is replayed.
"""

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Return the complete fictional task table using the submitted scenario."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)

    age_fraction = rng.beta(p["age_beta_alpha"], p["age_beta_beta"], size=n)
    age = np.floor(
        p["age_min"] + (p["age_max"] - p["age_min"] + 1) * age_fraction
    ).astype(np.int64)
    age = np.clip(age, p["age_min"], p["age_max"])
    female = rng.binomial(1, p["female_probability"], size=n).astype(np.int64)
    age_centered = age - p["age_reference"]
    female_centered = female - p["female_reference"]

    bmi_log_location = (
        np.log(p["bmi_reference_median"])
        + p["bmi_age_log_quadratic"] * np.square(age_centered)
        + p["bmi_female_log_shift"] * female_centered
    )
    bmi = np.exp(bmi_log_location + p["bmi_log_sd"] * rng.standard_normal(n))
    bmi_centered = bmi - p["bmi_reference"]

    probability_reference = p["elevated_probability_reference"]
    log_odds = (
        np.log(probability_reference / (1.0 - probability_reference))
        + p["elevated_age_logodds_slope"] * age_centered
        + p["elevated_bmi_logodds_slope"] * bmi_centered
        + p["elevated_female_logodds_slope"] * female_centered
    )
    probability = np.exp(-np.logaddexp(0.0, -log_odds))
    component = (rng.random(n) < probability).astype(np.int64)

    glucose_location = (
        np.log(np.asarray(p["glucose_reference_medians"])[component])
        + p["glucose_age_log_slope"] * age_centered
        + p["glucose_bmi_log_slope"] * bmi_centered
        + p["glucose_female_log_slope"] * female_centered
    )
    hba1c_location = (
        np.log(np.asarray(p["hba1c_reference_medians"])[component])
        + p["hba1c_age_log_slope"] * age_centered
        + p["hba1c_bmi_log_slope"] * bmi_centered
        + p["hba1c_female_log_slope"] * female_centered
    )
    glucose_z = rng.standard_normal(n)
    independent_hba1c_z = rng.standard_normal(n)
    rho = np.asarray(p["glycemic_residual_correlations"])[component]
    hba1c_z = rho * glucose_z + np.sqrt(1.0 - np.square(rho)) * independent_hba1c_z
    glucose = np.exp(
        glucose_location + np.asarray(p["glucose_log_sds"])[component] * glucose_z
    )
    hba1c = np.exp(
        hba1c_location + np.asarray(p["hba1c_log_sds"])[component] * hba1c_z
    )

    width = int(p["row_id_digits"])
    identifiers = [p["row_id_prefix"] + str(i + 1).zfill(width) for i in range(n)]
    return pd.DataFrame(
        {
            "row_id": identifiers,
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": glucose,
            "hba1c": hba1c,
        },
        columns=p["column_order"],
    )
