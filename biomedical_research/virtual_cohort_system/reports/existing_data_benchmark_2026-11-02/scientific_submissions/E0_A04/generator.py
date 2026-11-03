import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """One fixed, assumption-dependent whole-cohort law; no external inputs."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")

    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["n_rows"])

    a = p["age"]
    age_u = rng.beta(a["beta_alpha"], a["beta_beta"], size=n)
    age = (
        a["minimum"]
        + np.floor((a["maximum"] - a["minimum"] + 1) * age_u)
    ).astype(np.int64)
    age = np.minimum(age, a["maximum"])
    age_x = (age - a["reference"]) / a["decade_scale"]

    f = p["female"]
    female_eta = f["intercept_logit"] + f["age_decade_slope"] * age_x
    female_prob = np.exp(-np.logaddexp(0.0, -female_eta))
    female = (rng.random(n) < female_prob).astype(np.int64)
    female_x = female - f["effect_center"]

    b = p["bmi"]
    bmi_log_median = (
        np.log(b["reference_median"])
        + b["age_decade_log_shift"] * age_x
        + b["age_decade_squared_log_shift"] * age_x ** 2
        + b["female_log_shift"] * female_x
    )
    bmi = np.exp(bmi_log_median + b["residual_log_sd"] * rng.standard_normal(n))
    bmi_x = (bmi - b["glycemic_reference"]) / b["glycemic_scale"]

    s = p["glycemic_state"]
    state_eta = (
        s["intercept_logit"]
        + s["age_decade_log_odds"] * age_x
        + s["bmi_scaled_log_odds"] * bmi_x
        + s["female_log_odds"] * female_x
    )
    state_prob = np.exp(-np.logaddexp(0.0, -state_eta))
    state = (rng.random(n) < state_prob).astype(np.int64)
    shared_factor = rng.standard_normal(n)

    laboratories = {}
    for field in ("glucose", "hba1c"):
        q = p[field]
        log_median = (
            np.log(q["baseline_median"])
            + q["state_log_shift"] * state
            + q["age_decade_log_shift"] * age_x
            + q["bmi_scaled_log_shift"] * bmi_x
            + q["female_log_shift"] * female_x
        )
        log_sd = np.asarray(q["residual_log_sd_by_state"], dtype=float)[state]
        loading = np.asarray(q["shared_factor_loading_by_state"], dtype=float)[state]
        residual = (
            loading * shared_factor
            + np.sqrt(1.0 - loading ** 2) * rng.standard_normal(n)
        )
        laboratories[field] = np.exp(log_median + log_sd * residual)

    return pd.DataFrame(
        {
            "row_id": ["synthetic_" + str(i + 1).zfill(6) for i in range(n)],
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": laboratories["glucose"],
            "hba1c": laboratories["hba1c"],
        },
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"],
    )
