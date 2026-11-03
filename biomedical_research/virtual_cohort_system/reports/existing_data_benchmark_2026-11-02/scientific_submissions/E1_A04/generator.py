import numpy as np
import pandas as pd
from scipy.special import expit


def generate(observed, spec, seed):
    """Draw the single declared whole-cohort model, without input/output access."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")

    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["n_rows"])
    ap = p["age"]
    fp = p["female"]
    bp = p["bmi"]
    sp = p["high_glycemia"]
    gp = p["glucose"]
    hp = p["hba1c"]
    rp = p["residual_dependence"]

    age_support = np.arange(ap["minimum"], ap["maximum"] + 1, dtype=np.int64)
    age_weight = np.exp(-0.5 * ((age_support - ap["location"]) / ap["scale"]) ** 2)
    age = rng.choice(age_support, size=n, p=age_weight / age_weight.sum())
    age_decades = (age - ap["location"]) / ap["effect_unit_years"]

    female_reference = fp["reference_probability"]
    female_logit = np.log(female_reference / (1.0 - female_reference))
    female_probability = expit(female_logit + fp["log_odds_age_effect"] * age_decades)
    female = (rng.random(n) < female_probability).astype(np.int64)
    female_centered = female - female_reference

    bmi_log_median = (
        np.log(bp["reference_median"])
        + bp["log_age_effect"] * age_decades
        + bp["log_age_squared_effect"] * age_decades ** 2
        + bp["log_female_effect"] * female_centered
    )
    bmi = np.exp(bmi_log_median + bp["log_sd"] * rng.standard_normal(n))
    bmi_contrast = (bmi - bp["effect_center"]) / bp["effect_unit"]

    state_reference = sp["reference_probability"]
    state_logit = (
        np.log(state_reference / (1.0 - state_reference))
        + sp["log_odds_age_effect"] * age_decades
        + sp["log_odds_bmi_effect"] * bmi_contrast
        + sp["log_odds_female_effect"] * female_centered
    )
    high_state = (rng.random(n) < expit(state_logit)).astype(np.int64)

    glucose_log_median = (
        np.log(gp["reference_median"])
        + gp["log_age_effect"] * age_decades
        + gp["log_bmi_effect"] * bmi_contrast
        + gp["log_female_effect"] * female_centered
        + high_state * np.log(gp["high_state_median_multiplier"])
    )
    hba1c_log_median = (
        np.log(hp["reference_median"])
        + hp["log_age_effect"] * age_decades
        + hp["log_bmi_effect"] * bmi_contrast
        + hp["log_female_effect"] * female_centered
        + high_state * np.log(hp["high_state_median_multiplier"])
    )
    glucose_log_sd = np.where(high_state == 1, gp["high_state_log_sd"], gp["ordinary_log_sd"])
    hba1c_log_sd = np.where(high_state == 1, hp["high_state_log_sd"], hp["ordinary_log_sd"])
    residual_correlation = np.where(
        high_state == 1,
        rp["high_state_log_scale_correlation"],
        rp["ordinary_log_scale_correlation"],
    )
    glucose_residual = rng.standard_normal(n)
    hba1c_residual = (
        residual_correlation * glucose_residual
        + np.sqrt(1.0 - residual_correlation ** 2) * rng.standard_normal(n)
    )
    glucose = np.exp(glucose_log_median + glucose_log_sd * glucose_residual)
    hba1c = np.exp(hba1c_log_median + hba1c_log_sd * hba1c_residual)

    return pd.DataFrame(
        {
            "row_id": ["E1_A04-" + str(i + 1).zfill(6) for i in range(n)],
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": glucose,
            "hba1c": hba1c,
        },
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"],
    )
