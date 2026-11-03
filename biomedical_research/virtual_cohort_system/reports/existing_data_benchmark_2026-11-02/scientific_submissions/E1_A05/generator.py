import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Return the declared complete-cohort scenario; perform no external I/O."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")

    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["cohort"]["n_rows"])

    a = p["age"]
    age_support = np.arange(a["minimum"], a["maximum"] + 1, dtype=np.int64)
    age_weights = np.exp(-0.5 * ((age_support - a["kernel_center"]) / a["kernel_scale"]) ** 2)
    age = rng.choice(age_support, size=n, p=age_weights / age_weights.sum())
    age_score = (age - a["reference"]) / a["decade"]

    f = p["female"]
    female_reference = f["reference_probability"]
    female_log_odds = np.log(female_reference / (1.0 - female_reference))
    female_log_odds = female_log_odds + f["age_log_odds_per_decade"] * age_score
    female_probability = 1.0 / (1.0 + np.exp(-female_log_odds))
    female = rng.binomial(1, female_probability, size=n).astype(np.int64)
    female_score = female - female_reference

    b = p["bmi"]
    bmi_log_location = (
        np.log(b["reference_median"])
        + b["age_log_slope_per_decade"] * age_score
        + b["age_log_quadratic_per_decade_squared"] * age_score ** 2
        + b["female_log_shift"] * female_score
    )
    bmi = np.exp(bmi_log_location + b["log_residual_sd"] * rng.standard_normal(n))
    bmi_score = np.log(bmi / b["reference_median"]) / b["risk_log_scale"]

    d = p["glycemic_state"]
    state_reference = d["reference_probability"]
    state_log_odds = (
        np.log(state_reference / (1.0 - state_reference))
        + d["age_log_odds_per_decade"] * age_score
        + d["bmi_score_log_odds"] * bmi_score
        + d["female_log_odds"] * female_score
    )
    state_probability = 1.0 / (1.0 + np.exp(-state_log_odds))
    state = rng.binomial(1, state_probability, size=n)

    shared_fraction = p["residual_dependence"]["shared_variance_fraction"]
    shared_residual = rng.standard_normal(n)
    glucose_residual = (
        np.sqrt(shared_fraction) * shared_residual
        + np.sqrt(1.0 - shared_fraction) * rng.standard_normal(n)
    )
    hba1c_residual = (
        np.sqrt(shared_fraction) * shared_residual
        + np.sqrt(1.0 - shared_fraction) * rng.standard_normal(n)
    )

    g = p["glucose_body"]
    glucose = np.exp(
        np.log(g["reference_median"])
        + g["age_log_slope_per_decade"] * age_score
        + g["bmi_score_log_slope"] * bmi_score
        + g["female_log_shift"] * female_score
        + g["log_residual_sd"] * glucose_residual
    )

    h = p["hba1c_body"]
    hba1c = np.exp(
        np.log(h["reference_median"])
        + h["age_log_slope_per_decade"] * age_score
        + h["bmi_score_log_slope"] * bmi_score
        + h["female_log_shift"] * female_score
        + h["log_residual_sd"] * hba1c_residual
    )

    t = p["glycemic_tail"]
    severity = np.exp(t["shared_log_sd"] * rng.standard_normal(n))
    glucose = glucose + (
        state * t["glucose_increment_mmol_L"] * severity
        * np.exp(t["glucose_log_noise_sd"] * rng.standard_normal(n))
    )
    hba1c = hba1c + (
        state * t["hba1c_increment_percent"] * severity
        * np.exp(t["hba1c_log_noise_sd"] * rng.standard_normal(n))
    )

    return pd.DataFrame({
        "row_id": [f"synthetic_{i + 1:06d}" for i in range(n)],
        "age": age,
        "female": female,
        "bmi": bmi,
        "glucose": glucose,
        "hba1c": hba1c,
    }, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
