import numpy as np
import pandas as pd
from scipy.special import expit, ndtri


def generate(observed, spec, seed):
    """Draw the declared whole-cohort law without reading or writing artifacts."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    design = p["design"]
    n = int(design["n_rows"])
    age_settings = p["age_distribution"]
    refs = p["reference_scales"]

    age_grid = np.arange(design["age_min"], design["age_max"] + 1, dtype=np.int64)
    age_weights = np.exp(-0.5 * ((age_grid - age_settings["kernel_center_years"])
                                / age_settings["kernel_scale_years"]) ** 2)
    age = rng.choice(age_grid, size=n, p=age_weights / age_weights.sum())
    age_unit = (age - refs["age_years"]) / refs["age_unit_years"]

    sex_settings = p["female_distribution"]
    sex_p = sex_settings["reference_probability"]
    sex_logit = np.log(sex_p / (1.0 - sex_p))
    female = rng.binomial(1, expit(sex_logit + sex_settings["age_log_odds_per_unit"]
                                  * age_unit), size=n).astype(np.int64)
    sex_centered = female - refs["female_center"]

    b = p["bmi_distribution"]
    bmi_log_sd = np.log(b["dispersion_anchor_q3_kg_m2"]
                        / b["dispersion_anchor_q1_kg_m2"]) / (2.0 * ndtri(0.75))
    bmi = b["reference_median_kg_m2"] * np.exp(
        b["age_log_location_per_unit"] * age_unit
        + b["age_squared_log_location"] * age_unit ** 2
        + b["female_log_location"] * sex_centered
        + bmi_log_sd * rng.standard_normal(n)
    )
    bmi_unit = np.log(bmi / refs["bmi_kg_m2"]) / np.log1p(
        refs["bmi_unit_kg_m2"] / refs["bmi_kg_m2"]
    )

    t = p["elevated_tail"]
    tail_p = t["reference_probability"]
    tail_logit = np.log(tail_p / (1.0 - tail_p))
    tail_probability = expit(tail_logit
                             + t["age_log_odds_per_unit"] * age_unit
                             + t["bmi_log_odds_per_unit"] * bmi_unit
                             + t["female_log_odds"] * sex_centered)
    elevated = rng.binomial(1, tail_probability, size=n)
    severity = elevated * rng.gamma(t["severity_gamma_shape"],
                                    t["severity_gamma_scale"], size=n)
    shared = rng.standard_normal(n)

    g = p["serum_glucose"]
    g_loading = g["shared_normal_loading"]
    g_error = g_loading * shared + np.sqrt(1.0 - g_loading ** 2) * rng.standard_normal(n)
    glucose = g["reference_core_median_mmol_L"] * np.exp(
        g["age_log_location_per_unit"] * age_unit
        + g["bmi_log_location_per_unit"] * bmi_unit
        + g["female_log_location"] * sex_centered
        + g["core_log_sd"] * g_error
    ) + g["tail_increment_mmol_L_per_severity"] * severity

    h = p["hba1c_percent"]
    h_loading = h["shared_normal_loading"]
    h_error = h_loading * shared + np.sqrt(1.0 - h_loading ** 2) * rng.standard_normal(n)
    hba1c = h["reference_core_median_percent"] * np.exp(
        h["age_log_location_per_unit"] * age_unit
        + h["bmi_log_location_per_unit"] * bmi_unit
        + h["female_log_location"] * sex_centered
        + h["core_log_sd"] * h_error
    ) + h["tail_increment_percent_per_severity"] * severity

    return pd.DataFrame({
        "row_id": [f"R{i + 1:06d}" for i in range(n)],
        "age": age,
        "female": female,
        "bmi": bmi,
        "glucose": glucose,
        "hba1c": hba1c,
    }, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
