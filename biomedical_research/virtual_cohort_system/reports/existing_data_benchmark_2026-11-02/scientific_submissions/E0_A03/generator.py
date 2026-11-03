"""One declared whole-cohort law; construction does not execute this program."""

import numpy as np
import pandas as pd
from scipy.special import expit, ndtri


def generate(observed, spec, seed):
    """Return synthetic rows from the submitted fixed scientific specification."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")

    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["n_rows"])
    ref = p["references"]

    age_spec = p["age"]
    age_support = np.arange(
        int(age_spec["minimum"]), int(age_spec["maximum"]) + 1, dtype=np.int64
    )
    age_kernel = np.exp(
        -0.5
        * ((age_support - age_spec["kernel_location_years"])
           / age_spec["kernel_scale_years"]) ** 2
    )
    age = rng.choice(age_support, size=n, p=age_kernel / age_kernel.sum())
    a = (age - ref["age_years"]) / ref["age_scale_years"]

    sex_spec = p["female"]
    female_ref_p = sex_spec["probability_at_reference_age"]
    female_probability = expit(
        np.log(female_ref_p / (1.0 - female_ref_p))
        + sex_spec["log_odds_per_age_scale"] * a
    )
    female = (rng.random(n) < female_probability).astype(np.int64)
    f = female - ref["female_center"]

    bmi_spec = p["bmi"]
    bmi_reference_median = (
        bmi_spec["source_median_kg_m2"]
        + bmi_spec["reference_median_transport_shift_kg_m2"]
    )
    bmi_log_sd = (
        np.log(bmi_spec["source_q3_kg_m2"] / bmi_spec["source_q1_kg_m2"])
        / (2.0 * ndtri(0.75))
    )
    bmi_log_median = (
        np.log(bmi_reference_median)
        + bmi_spec["log_median_age_linear"] * a
        + bmi_spec["log_median_age_quadratic"] * a * a
        + bmi_spec["log_median_female"] * f
    )
    bmi = np.exp(bmi_log_median + bmi_log_sd * rng.standard_normal(n))
    b = (bmi - ref["bmi_kg_m2"]) / ref["bmi_scale_kg_m2"]

    state_spec = p["glycemic_state"]
    state_ref_p = state_spec["elevated_probability_at_reference"]
    state_probability = expit(
        np.log(state_ref_p / (1.0 - state_ref_p))
        + state_spec["log_odds_per_age_scale"] * a
        + state_spec["log_odds_per_bmi_scale"] * b
        + state_spec["log_odds_female"] * f
    )
    state = (rng.random(n) < state_probability).astype(np.int64)

    g_spec = p["glucose"]
    h_spec = p["hba1c"]
    g_medians = np.asarray(g_spec["state_reference_medians_mmol_L"], dtype=float)
    h_medians = np.asarray(h_spec["state_reference_medians_percent"], dtype=float)
    g_log_sds = np.asarray(g_spec["state_log_sds"], dtype=float)
    h_log_sds = np.asarray(h_spec["state_log_sds"], dtype=float)
    rho = np.asarray(
        p["residual_correlation"]["state_log_glucose_log_hba1c_correlations"],
        dtype=float,
    )[state]

    shared_innovation = rng.standard_normal(n)
    hba1c_innovation = rng.standard_normal(n)
    g_log_median = (
        np.log(g_medians[state])
        + g_spec["log_median_per_age_scale"] * a
        + g_spec["log_median_per_bmi_scale"] * b
        + g_spec["log_median_female"] * f
    )
    h_log_median = (
        np.log(h_medians[state])
        + h_spec["log_median_per_age_scale"] * a
        + h_spec["log_median_per_bmi_scale"] * b
        + h_spec["log_median_female"] * f
    )
    glucose = np.exp(g_log_median + g_log_sds[state] * shared_innovation)
    hba1c = np.exp(
        h_log_median
        + h_log_sds[state]
        * (rho * shared_innovation
           + np.sqrt(1.0 - rho * rho) * hba1c_innovation)
    )

    return pd.DataFrame(
        {
            "row_id": [f"E0_A03_{i + 1:04d}" for i in range(n)],
            "age": age,
            "female": female,
            "bmi": bmi,
            "glucose": glucose,
            "hba1c": hba1c,
        },
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"],
    )
