"""Whole-cohort construction; finite parameter derivations precede sampling."""
import numpy as np
import pandas as pd
from scipy.special import ndtri, log_ndtr


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = specification["parameters"]
    context_id = p["active_context"]
    context = p["contexts"][context_id]
    n = int(context["n_rows"])
    if n != 5000:
        raise ValueError("Every declared context requires 5000 rows")
    inputs = context["inputs"]
    order = p["profile_order"]
    anchors = [p["source_anchors"][cid] for cid in order]

    # Finite deterministic equations only; no fitting or random trials.
    bmi_mu = np.log(np.asarray([a["bmi_geometric_mean"] for a in anchors], dtype=float))
    tc_mu = np.log(np.asarray([a["tc_geometric_mean"] for a in anchors], dtype=float))
    hdl_mu = np.log(np.asarray([a["hdl_geometric_mean"] for a in anchors], dtype=float))
    cut = np.asarray([a["low_hdl_threshold"] for a in anchors], dtype=float)
    prevalence = np.asarray([a["low_hdl_percent"] for a in anchors], dtype=float) / 100.0
    hdl_sigma = (np.log(cut) - hdl_mu) / ndtri(prevalence)
    if not np.all(np.isfinite(hdl_sigma) & (hdl_sigma > 0.0)):
        raise ValueError("The declared lognormal HDL inversion has no positive finite solution")
    weights = np.asarray(inputs["profile_weights"], dtype=float)
    if len(weights) != len(order) or np.any(weights < 0.0) or weights.sum() <= 0.0:
        raise ValueError("Invalid declared profile weights")
    probabilities = weights / weights.sum()
    f = p["factor_settings"]
    b_a = float(f["bmi_age_loading"])
    h_a = float(f["hdl_age_loading"])
    h_b = float(f["hdl_bmi_residual_loading"])
    t_a = float(f["tc_age_loading"])
    t_b = float(f["tc_bmi_residual_loading"])
    t_h = float(f["tc_hdl_residual_loading"])
    b_b = np.sqrt(1.0 - b_a ** 2)
    h_h = np.sqrt(1.0 - h_a ** 2 - h_b ** 2)
    t_t = np.sqrt(1.0 - t_a ** 2 - t_b ** 2 - t_h ** 2)
    r = float(p["measurement_settings"]["log_error_correlation"])
    e_h = np.sqrt(1.0 - r ** 2)
    measurement_sd = np.asarray(inputs["measurement_log_sd"], dtype=float)
    measurement_offset = np.asarray(inputs["measurement_log_offset"], dtype=float)
    if p["measurement_settings"]["analyte_order"] != ["total_cholesterol", "hdl_cholesterol"]:
        raise ValueError("Measurement order must be TC then HDL")

    rng = np.random.default_rng(seed)
    profile = rng.choice(len(order), size=n, p=probabilities)
    sex = np.where(rng.random(n) < float(inputs["recorded_f_probability"]), "F", "M")
    z = rng.standard_normal((n, 6))
    a, b, h, t, e1, e2 = z.T
    age = float(p["age_settings"]["minimum"]) - float(p["age_settings"]["excess_mean"]) * log_ndtr(-a)
    b_score = b_a * a + b_b * b
    h_score = h_a * a + h_b * b + h_h * h
    t_score = t_a * a + t_b * b + t_h * h + t_t * t
    bmi = np.exp(bmi_mu[profile] + float(p["marginal_settings"]["bmi_log_sd"]) * b_score)
    tc = np.exp(tc_mu[profile] + float(p["marginal_settings"]["tc_log_sd"]) * t_score
                + measurement_offset[0] + measurement_sd[0] * e1)
    hdl = np.exp(hdl_mu[profile] + hdl_sigma[profile] * h_score
                 + measurement_offset[1] + measurement_sd[1] * (r * e1 + e_h * e2))
    clinical = np.column_stack([age, bmi, tc, hdl])
    if not np.all(np.isfinite(clinical)) or np.any(clinical[:, 1:] <= 0.0):
        raise ValueError("Nonfinite or nonpositive clinical values; no filtering is permitted")
    frame = pd.DataFrame({
        "id": [f"{context_id}-{i:05d}" for i in range(n)],
        "age": age,
        "sex": sex,
        "bmi": bmi,
        "total_cholesterol": tc,
        "hdl_cholesterol": hdl,
    })
    return frame.loc[:, p["output_columns"]]
