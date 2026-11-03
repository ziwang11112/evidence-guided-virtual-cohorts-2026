"""Bounded E0 completion scenario; no file/network access or individual inputs."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = spec["parameters"]
    d, ref = p["design"], p["source_reference"]
    b, g, h = p["bmi"], p["glucose"], p["hba1c"]
    rng = np.random.default_rng(seed)
    ages, sexes = [], []
    for female in d["female_values"]:
        for lo, hi in d["age_bands"]:
            ages.append(rng.integers(lo, hi + 1, size=d["n_per_cell"]))
            sexes.append(np.full(d["n_per_cell"], female, dtype=int))
    age = np.concatenate(ages)
    female = np.concatenate(sexes)
    n = len(age)
    if n != d["n_rows"]:
        raise ValueError("Design count does not match specification")
    width = b["upper"] - b["lower"]
    mean_fraction = (b["mean"] - b["lower"]) / width
    variance_fraction = (b["sd"] / width) ** 2
    concentration = mean_fraction * (1 - mean_fraction) / variance_fraction - 1
    bmi = b["lower"] + width * rng.beta(mean_fraction * concentration,
        (1 - mean_fraction) * concentration, size=n)
    z_bmi = (bmi - b["mean"]) / b["sd"]
    radius = np.sqrt(6 * p["residual_law"]["variance"])
    z_glucose = rng.triangular(-radius, 0, radius, size=n)
    z_hba1c = rng.triangular(-radius, 0, radius, size=n)
    glucose_residual_sd = np.sqrt(g["source_sd"] ** 2
        - (g["age_per_year"] * ref["age_sd"]) ** 2
        - g["bmi_standardized_loading"] ** 2)
    hba1c_residual_sd = np.sqrt(h["source_sd"] ** 2
        - (h["age_per_year"] * ref["age_sd"]) ** 2
        - h["bmi_standardized_loading"] ** 2
        - h["shared_glucose_factor_loading"] ** 2)
    age_centered = age - ref["age_mean"]
    glucose = (g["reference_mean"] + g["age_per_year"] * age_centered
        + g["bmi_standardized_loading"] * z_bmi + glucose_residual_sd * z_glucose)
    hba1c = (h["reference_mean"] + h["age_per_year"] * age_centered
        + h["bmi_standardized_loading"] * z_bmi
        + h["shared_glucose_factor_loading"] * z_glucose + hba1c_residual_sd * z_hba1c)
    order = rng.permutation(n)
    frame = pd.DataFrame({
        "row_id": [p["output"]["row_id_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": age[order], "female": female[order], "bmi": bmi[order],
        "glucose": glucose[order], "hba1c": hba1c[order],
    })
    return frame[p["output"]["columns"]]
