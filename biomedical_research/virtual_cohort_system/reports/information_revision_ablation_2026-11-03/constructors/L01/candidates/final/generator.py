"""Assumption-dependent whole-cohort construction; only generate produces rows."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    d = p["design"]
    n = d["n_rows"]
    a = p["age_distribution"]
    age_values = np.arange(d["age_min"], d["age_max"] + 1)
    age_weights = np.exp(-0.5 * ((age_values - a["location"]) / a["scale"]) ** 2)
    age = rng.choice(age_values, n, p=age_weights / age_weights.sum())
    age_c = age - p["centering"]["age"]
    f = p["female_distribution"]
    female_logit = np.log(f["probability_at_center"] / (1.0 - f["probability_at_center"])) + f["age_logit_slope"] * age_c
    female = rng.binomial(1, 1.0 / (1.0 + np.exp(-female_logit)), n)
    female_c = female - p["centering"]["female"]
    b = p["bmi_distribution"]
    bmi = np.exp(np.log(b["mean_at_center"]) + b["age_quadratic_log"] * age_c ** 2 + b["female_log_effect"] * female_c - 0.5 * b["log_sd"] ** 2 + b["log_sd"] * rng.normal(size=n))
    center = p["centering"]
    bmi_c = center["bmi_covariate_scale"] * np.tanh((bmi - center["bmi"]) / center["bmi_covariate_scale"])
    j = p["joint_glycemia"]
    z_glucose = rng.normal(size=n)
    z_hba1c = j["core_normal_correlation"] * z_glucose + np.sqrt(1.0 - j["core_normal_correlation"] ** 2) * rng.normal(size=n)
    g = p["core_glucose"]
    h = p["core_hba1c"]
    glucose = np.exp(np.log(g["mean_at_center"]) + g["age_log_slope"] * age_c + g["bmi_log_slope"] * bmi_c + g["female_log_effect"] * female_c - 0.5 * g["log_sd"] ** 2 + g["log_sd"] * z_glucose)
    hba1c = np.exp(np.log(h["mean_at_center"]) + h["age_log_slope"] * age_c + h["bmi_log_slope"] * bmi_c + h["female_log_effect"] * female_c - 0.5 * h["log_sd"] ** 2 + h["log_sd"] * z_hba1c)
    t = p["glycemic_subgroup"]
    subgroup_logit = np.log(t["probability_at_center"] / (1.0 - t["probability_at_center"])) + t["age_logit_slope"] * age_c + t["bmi_logit_slope"] * bmi_c + t["female_logit_effect"] * female_c
    subgroup = rng.binomial(1, 1.0 / (1.0 + np.exp(-subgroup_logit)), n)
    common_excess = rng.gamma(j["shared_gamma_shape"], 1.0, n)
    glucose_excess = common_excess + rng.gamma(j["individual_gamma_shape"], 1.0, n)
    hba1c_excess = common_excess + rng.gamma(j["individual_gamma_shape"], 1.0, n)
    glucose = glucose + subgroup * t["glucose_increment_per_gamma_unit"] * glucose_excess
    hba1c = hba1c + subgroup * t["hba1c_increment_per_gamma_unit"] * hba1c_excess
    return pd.DataFrame({
        "row_id": [d["id_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": age.astype(int), "female": female.astype(int),
        "bmi": bmi, "glucose": glucose, "hba1c": hba1c,
    }, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
