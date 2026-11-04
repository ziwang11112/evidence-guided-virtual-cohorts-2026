"""Request A whole-cohort generator; scientific parameters are in model_spec.json.
The generative order is a statistical factorization, not a causal graph.
"""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation expects observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)
    age = rng.integers(int(p["age_min"]), int(p["age_max"]) + 1, size=n)
    female = rng.binomial(1, p["female_probability"], size=n)
    age_c = age - p["age_center"]
    pr = p["stratum_reference_probability"]
    log_odds = np.log(pr / (1.0 - pr)) + p["stratum_age_logodds"] * age_c
    stratum = rng.binomial(1, 1.0 / (1.0 + np.exp(-log_odds)), size=n)
    bmi_mean = (p["bmi_male_reference_mean"] + p["bmi_female_mean_shift"] * female
                + p["bmi_age_slope"] * age_c + p["bmi_stratum_mean_shift"] * stratum)
    bmi_var_log = np.log1p((p["bmi_conditional_sd"] / bmi_mean) ** 2)
    bmi = rng.lognormal(np.log(bmi_mean) - 0.5 * bmi_var_log, np.sqrt(bmi_var_log))
    hba_mean = (p["hba1c_lower_reference_mean"] + p["hba1c_age_slope"] * age_c
                + p["hba1c_bmi_slope"] * (bmi - p["hba1c_bmi_center"])
                + p["hba1c_female_shift"] * female
                + p["hba1c_stratum_mean_shift"] * stratum)
    hba_sd = np.where(stratum == 1, p["hba1c_upper_sd"], p["hba1c_lower_sd"])
    excess = hba_mean - p["hba1c_floor"]
    if np.any(bmi_mean <= 0) or np.any(excess <= 0):
        raise ValueError("Scientific specification implies invalid conditional mean")
    hba1c = p["hba1c_floor"] + rng.gamma((excess / hba_sd) ** 2, hba_sd ** 2 / excess)
    return pd.DataFrame({"person_id": [f"A{i+1:05d}" for i in range(n)],
                         "age": age, "female": female, "bmi": bmi, "hba1c": hba1c})
