"""Whole-cohort candidate; execution is reserved for the isolated controller."""
import numpy as np
import pandas as pd


def _standardized_beta(rng, shapes, count):
    a, b = shapes
    mean = a / (a + b)
    variance = a * b / ((a + b) ** 2 * (a + b + 1))
    return (rng.beta(a, b, count) - mean) / np.sqrt(variance)


def _conditional_outcomes(age, u, v, w, parameters):
    """Same conditional law used in the source-moment derivation."""
    m = parameters["margins"]
    c = parameters["coefficients"]
    rho = parameters["latent"]["bmi_glucose_correlation"]
    bmi = m["bmi_mean"] + m["bmi_sd"] * u
    glucose = m["glucose_mean"] + m["glucose_sd"] * (rho * u + np.sqrt(1 - rho ** 2) * v)
    hba1c = (m["hba1c_mean"] + c["age"] * (age - m["age_center"])
             + c["bmi"] * (bmi - m["bmi_mean"])
             + c["glucose"] * (glucose - m["glucose_mean"])
             + c["residual_sd"] * w)
    return bmi, glucose, hba1c


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort model requires observed=None")
    p = spec["parameters"]
    d = p["design"]
    rng = np.random.default_rng(seed)
    age_parts, sex_parts = [], []
    for female in d["female_values"]:
        for lower, upper in d["age_bands"]:
            age_parts.append(rng.integers(lower, upper + 1, size=d["rows_per_cell"]))
            sex_parts.append(np.full(d["rows_per_cell"], female, dtype=int))
    age = np.concatenate(age_parts)
    female = np.concatenate(sex_parts)
    count = len(age)
    u = _standardized_beta(rng, p["latent"]["bmi_beta"], count)
    v = _standardized_beta(rng, p["latent"]["glucose_beta"], count)
    w = _standardized_beta(rng, p["latent"]["hba1c_beta"], count)
    bmi, glucose, hba1c = _conditional_outcomes(age, u, v, w, p)
    return pd.DataFrame({
        "row_id": ["ENSANUT2018_E1_A01_" + str(i + 1).zfill(4) for i in range(count)],
        "age": age, "female": female, "bmi": bmi, "glucose": glucose, "hba1c": hba1c,
    })
