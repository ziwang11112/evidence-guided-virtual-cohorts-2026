"""K02/A01 whole-cohort construction; no external data access or fitting."""

from math import log, sqrt

import numpy as np
import pandas as pd
from scipy.special import expit, ndtri


def generate(observed, specification, seed):
    """Return the complete declared cohort, in canonical units, from one seed."""
    if observed is not None:
        raise ValueError("This whole-cohort construction requires observed=None.")
    parameters = specification["parameters"]
    context_id = parameters["active_context"]
    descriptor = parameters["contexts"][context_id]
    n = int(descriptor["n_rows"])
    inputs = descriptor["inputs"]
    if n != 5000:
        raise ValueError("The released whole-cohort context requires 5000 rows.")

    # All finite deterministic parameter equations precede every random draw.
    # Reported confidence intervals and source sample sizes never enter these.
    profiles = {}
    for code, plan in inputs["anchor_plan"].items():
        total_weight = sum(entry["weight"] for entry in plan)
        if total_weight <= 0:
            raise ValueError("Anchor weights must have a positive total.")
        mu_bmi = 0.0
        mu_tc = 0.0
        mu_hdl = 0.0
        sigma_hdl = 0.0
        for entry in plan:
            anchor = parameters["source_anchors"][entry["context_id"]]
            if anchor["sex_code"] != code or entry["weight"] < 0:
                raise ValueError("Anchor code or weight is inconsistent.")
            weight = entry["weight"] / total_weight
            source_mu_hdl = log(anchor["hdl_geometric_mean"])
            quantile = float(ndtri(anchor["low_hdl_percent"] / 100.0))
            if quantile == 0.0:
                raise ValueError("The declared HDL scale equation is singular.")
            source_sigma_hdl = (
                log(anchor["hdl_threshold"]) - source_mu_hdl
            ) / quantile
            if not np.isfinite(source_sigma_hdl) or source_sigma_hdl <= 0.0:
                raise ValueError("The declared HDL anchors give no positive scale.")
            mu_bmi += weight * log(anchor["bmi_geometric_mean"])
            mu_tc += weight * log(anchor["tc_geometric_mean"])
            mu_hdl += weight * source_mu_hdl
            sigma_hdl += weight * source_sigma_hdl
        profiles[code] = (mu_bmi, mu_tc, mu_hdl, sigma_hdl)

    loading = parameters["factor_loadings"]
    b_age = loading["age_to_bmi"]
    h_age = loading["age_to_hdl"]
    h_bmi = loading["bmi_specific_to_hdl"]
    t_age = loading["age_to_tc"]
    t_bmi = loading["bmi_specific_to_tc"]
    t_hdl = loading["hdl_specific_to_tc"]
    b_residual = sqrt(1.0 - b_age * b_age)
    h_residual = sqrt(1.0 - h_age * h_age - h_bmi * h_bmi)
    t_residual = sqrt(
        1.0 - t_age * t_age - t_bmi * t_bmi - t_hdl * t_hdl
    )
    p_f = inputs["sex_probability_f"]
    if not 0.0 <= p_f <= 1.0:
        raise ValueError("Invalid declared code probability.")
    needed_codes = (["F"] if p_f > 0.0 else []) + (["M"] if p_f < 1.0 else [])
    if set(profiles) != set(needed_codes):
        raise ValueError("The profile plan does not cover the declared codes.")
    age_model = parameters["age_model"]
    age_span = age_model["upper_support"] - age_model["minimum"]
    tc_extra = inputs["additional_measurement_log_sd"]["total_cholesterol"]
    hdl_extra = inputs["additional_measurement_log_sd"]["hdl_cholesterol"]
    tc_shift = inputs["lipid_log_location_shift"]["total_cholesterol"]
    hdl_shift = inputs["lipid_log_location_shift"]["hdl_cholesterol"]

    # Individual variation starts here; no statistic is fit to these draws.
    rng = np.random.default_rng(seed)
    sex = np.where(rng.random(n) < p_f, "F", "M")
    factors = rng.standard_normal((n, 6))
    a, b, h, c, tc_error, hdl_error = factors.T
    age = age_model["minimum"] + age_span * expit(
        age_model["logit_location"] + age_model["logit_scale"] * a
    )
    z_bmi = b_age * a + b_residual * b
    z_hdl = h_age * a + h_bmi * b + h_residual * h
    z_tc = t_age * a + t_bmi * b + t_hdl * h + t_residual * c
    bmi = np.empty(n, dtype=float)
    total_cholesterol = np.empty(n, dtype=float)
    hdl_cholesterol = np.empty(n, dtype=float)
    for code, profile in profiles.items():
        selected = sex == code
        mu_bmi, mu_tc, mu_hdl, sigma_hdl = profile
        bmi[selected] = np.exp(
            mu_bmi + parameters["bmi_log_sd_by_code"][code] * z_bmi[selected]
        )
        total_cholesterol[selected] = np.exp(
            mu_tc + parameters["tc_log_sd_by_code"][code] * z_tc[selected]
            + tc_shift + tc_extra * tc_error[selected]
        )
        hdl_cholesterol[selected] = np.exp(
            mu_hdl + sigma_hdl * z_hdl[selected]
            + hdl_shift + hdl_extra * hdl_error[selected]
        )

    # Check the complete table rather than clipping, rejecting or dropping rows.
    clinical = np.column_stack((age, bmi, total_cholesterol, hdl_cholesterol))
    if not np.isfinite(clinical).all():
        raise ValueError("A complete finite cohort was not produced.")
    if not (age >= 18.0).all() or not (clinical[:, 1:] > 0.0).all():
        raise ValueError("The cohort violates the adult or positivity contract.")
    return pd.DataFrame({
        "id": [f"{context_id}:{seed}:{i + 1:05d}" for i in range(n)],
        "age": age,
        "sex": sex,
        "bmi": bmi,
        "total_cholesterol": total_cholesterol,
        "hdl_cholesterol": hdl_cholesterol,
    }, columns=[
        "id", "age", "sex", "bmi", "total_cholesterol", "hdl_cholesterol"
    ])
