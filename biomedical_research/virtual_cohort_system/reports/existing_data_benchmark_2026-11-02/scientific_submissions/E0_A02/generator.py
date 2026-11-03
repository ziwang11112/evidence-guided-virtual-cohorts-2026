import numpy as np
import pandas as pd
from scipy.special import expit


def generate(observed, spec, seed):
    """Sample the single declared law without external input or output."""
    if observed is not None:
        raise ValueError("This whole-cohort model requires observed=None.")

    p = spec["parameters"]
    n = int(p["cohort"]["n_rows"])
    rng = np.random.default_rng(seed)

    d = p["demographics"]
    age_grid = np.arange(
        int(d["age_minimum"]), int(d["age_maximum"]) + 1, dtype=np.int64
    )
    age_mass = np.exp(
        -0.5 * ((age_grid - d["age_kernel_location"]) / d["age_kernel_scale"]) ** 2
    )
    age = rng.choice(age_grid, size=n, p=age_mass / age_mass.sum())
    age_centered = (age - d["age_reference"]) / d["age_unit"]
    female_reference = d["female_reference_probability"]
    female_probability = expit(
        np.log(female_reference / (1.0 - female_reference))
        + d["female_age_log_odds"] * age_centered
    )
    female = rng.binomial(1, female_probability, size=n).astype(np.int64)
    female_centered = female - female_reference

    b = p["bmi"]
    bmi = np.exp(
        np.log(b["reference_median"])
        + b["age_log_shift"] * age_centered
        + b["age_squared_log_shift"] * age_centered ** 2
        + b["female_log_shift"] * female_centered
        + b["log_residual_sd"] * rng.standard_normal(n)
    )
    bmi_driver = b["driver_saturation"] * np.tanh(
        (bmi - b["driver_reference"])
        / (b["driver_scale"] * b["driver_saturation"])
    )

    s = p["glycemic_state"]
    high_reference = s["reference_high_probability"]
    high_probability = expit(
        np.log(high_reference / (1.0 - high_reference))
        + s["age_log_odds"] * age_centered
        + s["bmi_log_odds"] * bmi_driver
        + s["female_log_odds"] * female_centered
    )
    state = (rng.random(n) < high_probability).astype(np.int64)

    shared_normal = rng.standard_normal(n)
    outcomes = {}
    for field in ("glucose", "hba1c"):
        m = p[field]
        medians = np.asarray(m["component_medians"], dtype=float)
        log_sd = np.asarray(m["component_log_residual_sd"], dtype=float)
        loading = m["shared_normal_loading"]
        residual = (
            loading * shared_normal
            + np.sqrt(1.0 - loading ** 2) * rng.standard_normal(n)
        )
        outcomes[field] = np.exp(
            np.log(medians[state])
            + m["age_log_shift"] * age_centered
            + m["bmi_log_shift"] * bmi_driver
            + m["female_log_shift"] * female_centered
            + log_sd[state] * residual
        )

    return pd.DataFrame(
        {
            "row_id": [f"synthetic_{i + 1:04d}" for i in range(n)],
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": outcomes["glucose"],
            "hba1c": outcomes["hba1c"],
        },
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"],
    )
