"""Whole-cohort joint scenario; all scientific inputs are in model_spec.json.

Only finite closed-form source derivations precede sampling. This module has
no file/network access, calibration loop, trial table, or optimizer.
"""

import numpy as np
import pandas as pd
from scipy.special import betaincinv, ndtr, ndtri


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    parameters = specification["parameters"]
    context_id = parameters["active_context"]
    descriptor = parameters["contexts"][context_id]
    inputs = descriptor["inputs"]
    n_rows = int(descriptor["n_rows"])
    if n_rows != 5000:
        raise ValueError("The released context requires exactly 5000 rows")
    if not descriptor["population"] or not descriptor["measurement"]:
        raise ValueError("A population and measurement descriptor is required")

    # Finite deterministic derivation from the reported geometric means and
    # strict low-HDL prevalence; no confidence interval enters a dispersion.
    anchor_moments = {}
    for anchor_id, anchor in parameters["source_anchors"].items():
        means = np.log(np.array([
            anchor["bmi_geometric_mean"],
            anchor["tc_geometric_mean"],
            anchor["hdl_geometric_mean"],
        ], dtype=float))
        probability = anchor["low_hdl_percentage"] / 100.0
        hdl_sd = (np.log(anchor["low_hdl_cutoff"]) - means[2]) / ndtri(probability)
        sds = np.array([
            anchor["assumed_bmi_log_sd"],
            anchor["assumed_tc_log_sd"],
            hdl_sd,
        ], dtype=float)
        if not np.all(np.isfinite(sds)) or not np.all(sds > 0.0):
            raise ValueError("Source anchors do not identify positive log SDs")
        anchor_moments[anchor_id] = (means, sds)

    # Reference pooling matches the first two LOG-scale marginal moments.
    # It is an explicit target-transport scenario, not a population estimate.
    sex_moments = {}
    for sex_code in parameters["sex_codes"]:
        weight_map = inputs["reference_weights_by_sex"][sex_code]
        anchor_ids = list(weight_map)
        weights = np.array([weight_map[key] for key in anchor_ids], dtype=float)
        if np.any(weights < 0.0) or not np.sum(weights) > 0.0:
            raise ValueError("Reference weights must be nonnegative and nonempty")
        weights = weights / np.sum(weights)
        locations = np.vstack([anchor_moments[key][0] for key in anchor_ids])
        dispersions = np.vstack([anchor_moments[key][1] for key in anchor_ids])
        location = np.sum(weights[:, None] * locations, axis=0)
        variance = np.sum(
            weights[:, None] * (dispersions ** 2 + (locations - location) ** 2),
            axis=0,
        )
        shifts = np.array(inputs["log_location_shift_by_sex"][sex_code], dtype=float)
        extra_sd = np.array(inputs["extra_log_sd_by_sex"][sex_code], dtype=float)
        sex_moments[sex_code] = (location + shifts, np.sqrt(variance), extra_sd)

    # Triangular factors provide a positive-definite Gaussian copula by
    # construction. Loading magnitudes/signs are declared assumptions.
    loading = parameters["copula_loadings"]
    bmi_age = float(loading["bmi_age"])
    hdl_age = float(loading["hdl_age"])
    hdl_bmi_innovation = float(loading["hdl_bmi_innovation"])
    tc_age = float(loading["tc_age"])
    tc_bmi_innovation = float(loading["tc_bmi_innovation"])
    tc_hdl_innovation = float(loading["tc_hdl_innovation"])
    bmi_residual = np.sqrt(1.0 - bmi_age ** 2)
    hdl_residual = np.sqrt(1.0 - hdl_age ** 2 - hdl_bmi_innovation ** 2)
    tc_residual = np.sqrt(
        1.0 - tc_age ** 2 - tc_bmi_innovation ** 2 - tc_hdl_innovation ** 2
    )
    if not np.all(np.isfinite([bmi_residual, hdl_residual, tc_residual])):
        raise ValueError("Invalid factor loadings")

    # Derivation is complete before the first random call.
    rng = np.random.default_rng(seed)
    sex = np.where(rng.random(n_rows) < inputs["female_probability"], "F", "M")
    innovations = rng.standard_normal((n_rows, 7))
    age_score, bmi_innovation, hdl_innovation, tc_innovation = innovations[:, :4].T
    bmi_score = bmi_age * age_score + bmi_residual * bmi_innovation
    hdl_score = (
        hdl_age * age_score
        + hdl_bmi_innovation * bmi_innovation
        + hdl_residual * hdl_innovation
    )
    tc_score = (
        tc_age * age_score
        + tc_bmi_innovation * bmi_innovation
        + tc_hdl_innovation * hdl_innovation
        + tc_residual * tc_innovation
    )
    scores = np.column_stack((bmi_score, tc_score, hdl_score))
    age = np.empty(n_rows, dtype=float)
    clinical = np.empty((n_rows, 3), dtype=float)
    lower, upper = parameters["age_support_years"]
    for sex_code in parameters["sex_codes"]:
        selected = sex == sex_code
        shape_a, shape_b = inputs["age_beta_shapes_by_sex"][sex_code]
        age[selected] = lower + (upper - lower) * betaincinv(
            shape_a, shape_b, ndtr(age_score[selected])
        )
        location, sd, extra_sd = sex_moments[sex_code]
        clinical[selected, :] = np.exp(
            location + scores[selected, :] * sd
            + innovations[selected, 4:7] * extra_sd
        )

    if not np.all(np.isfinite(age)) or not np.all(age >= lower):
        raise ValueError("Age contract failed; no output rows have been filtered")
    if not np.all(np.isfinite(clinical)) or not np.all(clinical > 0.0):
        raise ValueError("Clinical contract failed; no output rows have been filtered")
    return pd.DataFrame({
        "id": [f"{context_id}-{index + 1:05d}" for index in range(n_rows)],
        "age": age,
        "sex": sex,
        "bmi": clinical[:, 0],
        "total_cholesterol": clinical[:, 1],
        "hdl_cholesterol": clinical[:, 2],
    }, columns=parameters["ordered_columns"])
