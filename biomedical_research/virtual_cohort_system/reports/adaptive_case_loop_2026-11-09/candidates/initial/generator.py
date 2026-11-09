"""Whole-cohort scenario. Execute only through the isolated adapter."""
import math

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This generator requires whole-cohort mode")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = p["n_rows"]
    female = rng.random(n) < p["female_probability"]
    z = rng.standard_normal((n, 4))
    age_probability = np.asarray([0.5 * (1 + math.erf(float(a) / math.sqrt(2))) for a in z[:, 0]])
    age = np.empty(n, dtype=float)
    bmi = np.empty(n)
    tc_anchor = np.empty(n)
    hdl_anchor = np.empty(n)
    rho = p["age_bmi_latent_correlation"]
    bmi_z = rho * z[:, 0] + math.sqrt(1 - rho * rho) * z[:, 1]
    for code, mask in (("F", female), ("M", ~female)):
        age[mask] = np.interp(age_probability[mask], p["age_probabilities"],
                              p["age_quantiles"][code])
        m = p["margins"][code]
        bmi[mask] = np.exp(math.log(m["bmi_geometric_mean"]) + m["bmi_log_sd"] * bmi_z[mask])
        tc_anchor[mask] = m["tc_arithmetic_anchor"]
        hdl_anchor[mask] = m["hdl_arithmetic_anchor"]
    tc_mean = (tc_anchor + p["tc_bmi_working_slope"] * (bmi - p["reference_bmi"])
               + p["tc_age_working_slope"] * (age - p["reference_age"]))
    age_group = np.searchsorted(p["hdl_age_cutpoints"], age, side="right")
    bmi_group = np.searchsorted(p["hdl_bmi_cutpoints"], bmi, side="right")
    hdl_mean = (hdl_anchor + np.asarray(p["hdl_age_effects"])[age_group] - p["hdl_age_center"]
                + np.asarray(p["hdl_bmi_effects"])[bmi_group])
    if np.any(tc_mean <= 0) or np.any(hdl_mean <= 0):
        raise ValueError("The declared conditional mean became nonpositive")
    rho_e = p["residual_latent_correlation"]
    hdl_z = rho_e * z[:, 2] + math.sqrt(1 - rho_e * rho_e) * z[:, 3]
    tc_sigma, hdl_sigma = p["lipid_residual_log_sd"]
    tc = tc_mean * np.exp(tc_sigma * z[:, 2] - 0.5 * tc_sigma**2)
    hdl = hdl_mean * np.exp(hdl_sigma * hdl_z - 0.5 * hdl_sigma**2)
    return pd.DataFrame({
        "id": [f"virtual_{seed}_{i:05d}" for i in range(1, n + 1)],
        "age": age,
        "sex": np.where(female, "F", "M"),
        "bmi": bmi,
        "total_cholesterol": tc,
        "hdl_cholesterol": hdl,
    })
