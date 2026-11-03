"""One complete cohort per invocation; no hidden cohorts, fitting, files or network."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)
    a = p["age_distribution"]
    support = np.arange(a["minimum"], a["maximum"] + 1, dtype=int)
    weights = np.exp(-0.5 * ((support - a["center"]) / a["scale"]) ** 2)
    age = rng.choice(support, size=n, p=weights / weights.sum())
    s = p["female_distribution"]
    logit_f = np.log(s["reference_probability"] / (1 - s["reference_probability"])) + s["log_odds_per_year"] * (age - s["age_center"])
    female = (rng.random(n) < 1 / (1 + np.exp(-logit_f))).astype(int)
    b = p["bmi_distribution"]
    age_b = age - b["age_center"]
    mean_b = b["reference_mean"] + b["age_linear"] * age_b + b["age_quadratic"] * age_b ** 2 + b["female_mean_shift"] * (female - b["female_center"])
    bmi = mean_b * np.exp(b["log_sd"] * rng.standard_normal(n) - 0.5 * b["log_sd"] ** 2)
    d = p["glycemic_state"]
    logit_d = np.log(d["reference_probability"] / (1 - d["reference_probability"])) + d["log_odds_per_year"] * (age - d["age_center"]) + d["log_odds_per_bmi"] * (bmi - d["bmi_center"]) + d["female_log_odds_shift"] * (female - d["female_center"])
    state = (rng.random(n) < 1 / (1 + np.exp(-logit_d))).astype(int)
    z_g = rng.standard_normal(n)
    z_independent = rng.standard_normal(n)
    rho = np.asarray(p["conditional_log_error_correlation"])[state]
    z_h = rho * z_g + np.sqrt(1 - rho ** 2) * z_independent
    results = []
    for name, z in (("glucose_distribution", z_g), ("hba1c_distribution", z_h)):
        settings = p[name]
        mean = np.asarray(settings["reference_means"])[state] + settings["age_mean_slope"] * (age - settings["age_center"]) + settings["bmi_mean_slope"] * (bmi - settings["bmi_center"]) + settings["female_mean_shift"] * (female - settings["female_center"])
        cv = np.asarray(settings["conditional_cv"])[state]
        sigma = np.sqrt(np.log1p(cv ** 2))
        results.append(mean * np.exp(sigma * z - 0.5 * sigma ** 2))
    return pd.DataFrame({"row_id": [f"SYN_{i + 1:05d}" for i in range(n)], "age": age, "female": female, "bmi": bmi, "glucose": results[0], "hba1c": results[1]}, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
