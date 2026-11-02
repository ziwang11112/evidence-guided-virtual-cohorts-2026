"""Whole-cohort scenario model; no observed participant inputs are used."""

import numpy as np
import pandas as pd
from scipy.special import expit, ndtri


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")
    parameters = specification["parameters"]
    context_id = parameters["active_context"]
    context = parameters["contexts"][context_id]
    if not isinstance(context["population"], str) or not context["population"]:
        raise ValueError("A declared population is required.")
    if not isinstance(context["measurement"], str) or not context["measurement"]:
        raise ValueError("A declared measurement description is required.")
    n = int(context["n_rows"])
    if n != 5000:
        raise ValueError("Every scheduled context requires 5000 rows.")
    inputs = context["inputs"]

    # Finite deterministic equations, completed before drawing any random values.
    # This is a log-moment projection of declared anchor distributions, not a fit.
    prepared = {}
    for sex_code, profile in inputs["sex_profiles"].items():
        anchors = profile["anchors"]
        weights = np.asarray(profile["weights"], dtype=float)
        weights = weights / weights.sum()
        log_centres = np.asarray([
            [np.log(a["bmi_geometric_mean"]),
             np.log(a["total_cholesterol_geometric_mean"]),
             np.log(a["hdl_cholesterol_geometric_mean"])]
            for a in anchors
        ], dtype=float)
        hdl_sd = np.asarray([
            (np.log(a["hdl_low_threshold"]) - np.log(a["hdl_cholesterol_geometric_mean"]))
            / ndtri(a["hdl_low_percent"] / 100.0)
            for a in anchors
        ], dtype=float)
        if np.any(hdl_sd <= 0.0) or not np.all(np.isfinite(hdl_sd)):
            raise ValueError("The declared HDL anchors do not define positive log dispersion.")
        centre = np.sum(weights[:, None] * log_centres, axis=0)
        component_variance = np.asarray([
            [parameters["base_log_sd"]["bmi"] ** 2,
             parameters["base_log_sd"]["total_cholesterol"] ** 2,
             s ** 2]
            for s in hdl_sd
        ], dtype=float)
        variance = np.sum(
            weights[:, None] * (component_variance + (log_centres - centre) ** 2),
            axis=0,
        )
        prepared[sex_code] = (centre, np.sqrt(variance))

    f = parameters["factor_loadings"]
    ba = f["bmi_age"]
    ha = f["hdl_age"]
    hb = f["hdl_bmi_innovation"]
    ta = f["total_cholesterol_age"]
    tb = f["total_cholesterol_bmi_innovation"]
    th = f["total_cholesterol_hdl_innovation"]
    bmi_remainder = np.sqrt(1.0 - ba ** 2)
    hdl_remainder = np.sqrt(1.0 - ha ** 2 - hb ** 2)
    tc_remainder = np.sqrt(1.0 - ta ** 2 - tb ** 2 - th ** 2)
    extra_sd = np.asarray([
        inputs["extra_log_error_sd"]["bmi"],
        inputs["extra_log_error_sd"]["total_cholesterol"],
        inputs["extra_log_error_sd"]["hdl_cholesterol"],
    ], dtype=float)

    rng = np.random.default_rng(seed)
    sex = np.where(rng.random(n) < inputs["sex_probability_f"], "F", "M")
    independent = rng.standard_normal((n, 4))
    age_factor = independent[:, 0]
    bmi_factor = ba * age_factor + bmi_remainder * independent[:, 1]
    hdl_factor = ha * age_factor + hb * independent[:, 1] + hdl_remainder * independent[:, 2]
    tc_factor = (
        ta * age_factor + tb * independent[:, 1] + th * independent[:, 2]
        + tc_remainder * independent[:, 3]
    )
    age_model = parameters["age_model"]
    age = age_model["lower"] + (age_model["upper"] - age_model["lower"]) * expit(
        age_model["logit_location"] + age_model["logit_scale"] * age_factor
    )
    factors = np.column_stack((bmi_factor, tc_factor, hdl_factor))
    extra_error = rng.standard_normal((n, 3)) * extra_sd
    clinical = np.empty((n, 3), dtype=float)
    for sex_code, (centre, log_sd) in prepared.items():
        selected = sex == sex_code
        clinical[selected] = np.exp(centre + factors[selected] * log_sd + extra_error[selected])
    if not np.all(np.isfinite(clinical)) or np.any(clinical <= 0.0):
        raise ValueError("Numerical generation failed; rows are never filtered or replaced.")
    return pd.DataFrame({
        "id": [f"{context_id}-{i + 1:05d}" for i in range(n)],
        "age": age,
        "sex": sex,
        "bmi": clinical[:, 0],
        "total_cholesterol": clinical[:, 1],
        "hdl_cholesterol": clinical[:, 2],
    }, columns=parameters["output_columns"])
