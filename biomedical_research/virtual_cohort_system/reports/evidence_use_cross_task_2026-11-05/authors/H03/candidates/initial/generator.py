"""Reviewed H03 bounded joint law; execution is reserved for the supplied adapter."""
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    """Generate the authorized whole cohort from the supplied scientific specification."""
    if observed is not None:
        raise ValueError("H03 is a whole-cohort task without observed rows")
    p = specification["parameters"]
    design, bmi_p, glucose_p, hba1c_p = (p[k] for k in ("design", "bmi", "glucose", "hba1c"))
    bands = design["age_bands"]
    n_cell = design["rows_per_cell"]
    n_bands = len(bands)
    age_mean = sum((lo + hi) / 2 for lo, hi in bands) / n_bands
    age_variance = sum(((hi - lo + 1) ** 2 - 1) / 12 + ((lo + hi) / 2 - age_mean) ** 2
                       for lo, hi in bands) / n_bands
    female_mean, female_variance = 0.5, 0.25

    b_mean, b_sd = bmi_p["mean"], bmi_p["sd"]
    b_low, b_high = bmi_p["lower"], bmi_p["upper"]
    b_var = b_sd ** 2
    b_prob = (b_mean - b_low) / (b_high - b_low)
    b_concentration = (b_mean - b_low) * (b_high - b_mean) / b_var - 1
    b_alpha, b_beta = b_prob * b_concentration, (1 - b_prob) * b_concentration

    g_mean, g_var, g_upper = glucose_p["mean"], glucose_p["sd"] ** 2, glucose_p["upper"]
    ga, gb, gf = (glucose_p[k] for k in ("age_slope", "bmi_slope", "female_slope"))
    g_mean_var = ga ** 2 * age_variance + gb ** 2 * b_var + gf ** 2 * female_variance
    g_residual_var = g_var - g_mean_var
    g_concentration = (g_mean * (g_upper - g_mean) - g_mean_var) / g_residual_var - 1

    ref_lo, ref_hi = hba1c_p["reference_age_range"]
    ref_age = (ref_lo + ref_hi) / 2
    ref_age_var = ((ref_hi - ref_lo + 1) ** 2 - 1) / 12
    g_ref_mean = g_mean + ga * (ref_age - age_mean)
    g_ref_mean_var = ga ** 2 * ref_age_var + gb ** 2 * b_var + gf ** 2 * female_variance
    g_ref_residual_var = (g_ref_mean * (g_upper - g_ref_mean) - g_ref_mean_var) / (g_concentration + 1)
    h_ref_mean = hba1c_p["reference_mean"]
    h_ref_var = ((hba1c_p["reference_upper_quantile"] - h_ref_mean) / hba1c_p["normal_quantile_z"]) ** 2
    ha, hb_total, hf_total = (hba1c_p[k] for k in ("age_slope", "bmi_total_slope", "female_total_slope"))
    rho = hba1c_p["marginal_glucose_correlation"]

    def moment_components(c):
        v_mu = ((ha + c * ga) ** 2 * age_variance + hb_total ** 2 * b_var
                + hf_total ** 2 * female_variance + c ** 2 * g_residual_var)
        v_mu_ref = ((ha + c * ga) ** 2 * ref_age_var + hb_total ** 2 * b_var
                    + hf_total ** 2 * female_variance + c ** 2 * g_ref_residual_var)
        residual = h_ref_var - v_mu_ref
        covariance = (ha * ga * age_variance + hb_total * gb * b_var
                      + hf_total * gf * female_variance
                      + c * (g_var - gb ** 2 * b_var - gf ** 2 * female_variance))
        return residual + v_mu, covariance, residual

    v0 = moment_components(0)[0]
    v1 = (moment_components(1)[0] - moment_components(-1)[0]) / 2
    v2 = (moment_components(1)[0] + moment_components(-1)[0]) / 2 - v0
    c0 = moment_components(0)[1]
    c1 = moment_components(1)[1] - c0
    qa = c1 ** 2 - rho ** 2 * g_var * v2
    qb = 2 * c0 * c1 - rho ** 2 * g_var * v1
    qc = c0 ** 2 - rho ** 2 * g_var * v0
    discriminant = qb ** 2 - 4 * qa * qc
    if qa == 0 or discriminant < 0:
        raise ValueError("Incompatible proposed moment equations")
    roots = [(-qb - np.sqrt(discriminant)) / (2 * qa),
             (-qb + np.sqrt(discriminant)) / (2 * qa)]
    admissible = []
    for c in roots:
        variance, covariance, residual = moment_components(c)
        if variance > 0 and residual > 0 and abs(covariance / np.sqrt(g_var * variance) - rho) < 1e-10:
            admissible.append(c)
    if len(admissible) != 1:
        raise ValueError("Signed correlation equation does not identify one admissible root")
    hg = admissible[0]
    h_residual_var = moment_components(hg)[2]
    hb, hf = hb_total - hg * gb, hf_total - hg * gf
    if min(b_alpha, b_beta, g_concentration, h_residual_var) <= 0:
        raise ValueError("Nonpositive distribution parameter")

    rng = np.random.default_rng(seed)
    age_parts, female_parts = [], []
    for female_value in (0, 1):
        for lo, hi in bands:
            age_parts.append(rng.integers(lo, hi + 1, size=n_cell))
            female_parts.append(np.full(n_cell, female_value, dtype=np.int64))
    age = np.concatenate(age_parts)
    female = np.concatenate(female_parts)
    n = len(age)
    bmi = b_low + (b_high - b_low) * rng.beta(b_alpha, b_beta, size=n)
    mg = g_mean + ga * (age - age_mean) + gb * (bmi - b_mean) + gf * (female - female_mean)
    gp = mg / g_upper
    if np.any((gp <= 0) | (gp >= 1)):
        raise ValueError("Conditional glucose mean outside percentage support")
    glucose = g_upper * rng.beta(gp * g_concentration, (1 - gp) * g_concentration)
    glucose = np.clip(glucose, np.nextafter(0.0, 1.0), np.nextafter(g_upper, 0.0))
    mh = (h_ref_mean + ha * (age - ref_age) + hb * (bmi - b_mean)
          + hf * (female - female_mean) + hg * (glucose - g_ref_mean))
    h_upper = hba1c_p["upper"]
    hp = mh / h_upper
    h_concentration = mh * (h_upper - mh) / h_residual_var - 1
    if np.any((hp <= 0) | (hp >= 1) | (h_concentration <= 0)):
        raise ValueError("Invalid conditional HbA1c beta parameters")
    hba1c = h_upper * rng.beta(hp * h_concentration, (1 - hp) * h_concentration)
    hba1c = np.clip(hba1c, np.nextafter(0.0, 1.0), np.nextafter(h_upper, 0.0))
    return pd.DataFrame({
        "row_id": [f"H03-{i + 1:06d}" for i in range(n)],
        "age": age, "female": female, "bmi": bmi, "glucose": glucose, "hba1c": hba1c,
    })
