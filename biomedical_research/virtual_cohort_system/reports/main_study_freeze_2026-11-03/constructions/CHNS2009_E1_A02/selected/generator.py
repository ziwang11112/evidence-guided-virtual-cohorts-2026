"""Author CHNS2009_E1_A02; submitted only, never locally imported or executed.

All scientific settings are supplied through model_spec.json. A standardized
gamma BMI innovation and bounded glucose/HbA1c innovations describe ordinary
variation; a Bernoulli-gamma component allows an upper metabolic tail.
"""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort construction requires observed=None")
    p = spec["parameters"]
    c = p["target_context"]
    d = p["shared_structure"]
    rng = np.random.default_rng(seed)
    n = p["n_rows"]
    age = rng.integers(c["age_min"], c["age_max"] + 1, size=n)
    female = rng.binomial(1, c["female_probability"], size=n)
    age_centered = age - c["age_mean"]
    female_centered = female - c["female_probability"]
    z = rng.uniform(-np.sqrt(3.0), np.sqrt(3.0), size=(n, 2))
    bmi_shape = c["bmi_gamma_shape"]
    bmi_innovation = (rng.gamma(bmi_shape, 1.0, size=n) - bmi_shape) / np.sqrt(bmi_shape)
    upper = rng.binomial(1, c["upper_probability"], size=n)
    excess = upper * rng.gamma(c["upper_gamma_shape"], c["upper_gamma_scale"], size=n)
    bmi = (c["bmi_center"] + d["bmi_age"] * age_centered
           + d["bmi_female"] * female_centered + c["bmi_residual_sd"] * bmi_innovation)
    glucose = (c["glucose_center"] + d["glucose_age"] * age_centered
               + d["glucose_female"] * female_centered
               + c["glucose_residual_sd"] * (d["residual_bmi_glucose_correlation"] * bmi_innovation
                  + np.sqrt(1.0 - d["residual_bmi_glucose_correlation"] ** 2) * z[:, 0])
               + excess)
    hba1c = (c["hba1c_center"] + d["hba1c_age_direct"] * age_centered
             + d["hba1c_female_direct"] * female_centered
             + d["hba1c_bmi_joint"] * (bmi - c["bmi_center"])
             + d["hba1c_glucose_joint"] * (glucose - c["glucose_center"])
             + d["hba1c_upper_extra"] * excess + c["hba1c_residual_sd"] * z[:, 1])
    return pd.DataFrame({
        "row_id": [f"{p['row_prefix']}{i + 1:06d}" for i in range(n)],
        "age": age, "female": female, "bmi": bmi,
        "glucose": glucose, "hba1c": hba1c,
    })
