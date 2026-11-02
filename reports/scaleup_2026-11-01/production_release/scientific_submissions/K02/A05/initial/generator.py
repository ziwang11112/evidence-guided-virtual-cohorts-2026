"""Whole-cohort construction; no fitting, external inputs, or sample tuning."""

import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri
from scipy.stats import gamma


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("This construction requires observed=None.")
    parameters = specification["parameters"]
    context_id = parameters["active_context"]
    context = parameters["contexts"][context_id]
    inputs = context["inputs"]
    n = int(context["n_rows"])
    if n != 5000:
        raise ValueError("Every context requires exactly 5000 rows.")

    # All model-specific algebra precedes generation. Published CIs and sample
    # counts are not used as participant SDs, fitting weights, or tolerances.
    anchors = parameters["reported_anchors"]
    resolved = {}
    for sex in ("M", "F"):
        selected = [
            (anchors[anchor_id], float(weight))
            for anchor_id, weight in zip(inputs["anchor_ids"], inputs["anchor_weights"])
            if anchors[anchor_id]["sex"] == sex
        ]
        if not selected:
            continue
        weights = np.asarray([weight for _, weight in selected], dtype=float)
        if np.any(weights <= 0):
            raise ValueError("Anchor weights must be positive.")
        weights = weights / np.sum(weights)
        bmi_log_centres = []
        tc_log_centres = []
        hdl_log_centres = []
        hdl_log_variances = []
        for anchor, _ in selected:
            log_g = np.log(float(anchor["hdl_geometric_mean"]))
            probability = float(anchor["low_hdl_percentage"]) / 100.0
            sigma = (
                np.log(float(anchor["low_hdl_strict_threshold"])) - log_g
            ) / ndtri(probability)
            if not np.isfinite(sigma) or sigma <= 0:
                raise ValueError("Declared HDL lognormal inversion is undefined.")
            bmi_log_centres.append(np.log(float(anchor["bmi_geometric_mean"])))
            tc_log_centres.append(np.log(float(anchor["tc_geometric_mean"])))
            hdl_log_centres.append(log_g)
            hdl_log_variances.append(sigma * sigma)
        resolved[sex] = {
            "bmi_mu": float(np.dot(weights, bmi_log_centres)),
            "tc_mu": float(np.dot(weights, tc_log_centres)),
            "hdl_mu": float(np.dot(weights, hdl_log_centres)),
            "hdl_sigma": float(inputs["hdl_dispersion_multiplier"])
            * np.sqrt(float(np.dot(weights, hdl_log_variances))),
        }

    loadings = parameters["dependence_loadings"]
    bmi_age = float(loadings["bmi_age"])
    hdl_weights = np.asarray(loadings["hdl_age_adiposity_shared"], dtype=float)
    tc_weights = np.asarray(loadings["tc_age_adiposity_shared"], dtype=float)
    bmi_residual = np.sqrt(1.0 - bmi_age * bmi_age)
    hdl_residual = np.sqrt(1.0 - np.dot(hdl_weights, hdl_weights))
    tc_residual = np.sqrt(1.0 - np.dot(tc_weights, tc_weights))
    age_config = parameters["age_distribution"]

    rng = np.random.default_rng(int(seed) % (2 ** 64))
    sex_values = np.where(rng.random(n) < float(inputs["sex_probability_f"]), "F", "M")
    latent = rng.standard_normal((n, 5))
    age_z, adiposity_z, shared_z, hdl_z, tc_z = latent.T
    bmi_z = bmi_age * age_z + bmi_residual * adiposity_z
    common = np.column_stack((age_z, adiposity_z, shared_z))
    hdl_z = common @ hdl_weights + hdl_residual * hdl_z
    tc_z = common @ tc_weights + tc_residual * tc_z

    # The probability clamp only avoids floating-point CDF endpoints. It does
    # not delete, winsorize, or select clinical records.
    age_probability = np.clip(ndtr(age_z), np.nextafter(0.0, 1.0), np.nextafter(1.0, 0.0))
    age = float(age_config["minimum"]) + gamma.ppf(
        age_probability,
        a=float(age_config["shape"]),
        scale=float(age_config["scale_years"]),
    )
    bmi = np.empty(n, dtype=float)
    total_cholesterol = np.empty(n, dtype=float)
    hdl_cholesterol = np.empty(n, dtype=float)
    measurement_sd = float(inputs["extra_lipid_measurement_log_sd"])
    measurement_error = rng.standard_normal((n, 2)) * measurement_sd
    for sex, law in resolved.items():
        rows = sex_values == sex
        bmi[rows] = np.exp(law["bmi_mu"] + float(inputs["bmi_log_sd"]) * bmi_z[rows])
        total_cholesterol[rows] = np.exp(
            law["tc_mu"] + float(inputs["tc_log_sd"]) * tc_z[rows] + measurement_error[rows, 0]
        )
        hdl_cholesterol[rows] = np.exp(
            law["hdl_mu"] + law["hdl_sigma"] * hdl_z[rows] + measurement_error[rows, 1]
        )
    if any(sex not in resolved for sex in np.unique(sex_values)):
        raise ValueError("No declared marginal anchors for an emitted sex category.")

    result = pd.DataFrame({
        "id": [f"{context_id}:{int(seed)}:{row:05d}" for row in range(n)],
        "age": age,
        "sex": sex_values,
        "bmi": bmi,
        "total_cholesterol": total_cholesterol,
        "hdl_cholesterol": hdl_cholesterol,
    }, columns=parameters["output_schema"]["columns"])
    values = result[["age", "bmi", "total_cholesterol", "hdl_cholesterol"]].to_numpy()
    if not np.isfinite(values).all() or np.any(values[:, 1:] <= 0) or np.any(age < 18):
        raise ValueError("Generated table violates the finite adult positive-value contract.")
    return result
