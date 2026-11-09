import numpy as np
import pandas as pd


def _lognormal_parameters(arithmetic_mean, arithmetic_sd):
    variance = np.log1p((arithmetic_sd / arithmetic_mean) ** 2)
    return np.log(arithmetic_mean) - variance / 2.0, np.sqrt(variance)


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("This construction requires observed=None.")
    n = int(specification["n_rows"])
    if n != 3000:
        raise ValueError("The submitted construction requires 3000 rows.")
    p = specification["parameters"]
    rng = np.random.default_rng(seed)

    female = rng.random(n) < p["sex"]["probability_F"]
    u_age = rng.random(n)
    age_p = p["age"]
    age = np.where(
        female,
        np.interp(u_age, age_p["quantile_probabilities"], age_p["quantile_values_F"]),
        np.interp(u_age, age_p["quantile_probabilities"], age_p["quantile_values_M"]),
    )
    age_scaled = (age - age_p["effect_center_years"]) / age_p["effect_scale_years"]

    # This is an explicitly assumed conditional copula, not fitted OLS effects.
    dep = p["dependence"]
    rho = 2.0 * np.sin(np.pi * np.asarray(dep["reference_spearman"], dtype=float) / 6.0)
    r_b_t, r_b_h, r_t_h = rho
    correlation = np.array([
        [1.0, r_b_t, r_b_h],
        [r_b_t, 1.0, r_t_h],
        [r_b_h, r_t_h, 1.0],
    ])
    latent = rng.standard_normal((n, 3)) @ np.linalg.cholesky(correlation).T
    latent = np.clip(latent, -dep["latent_cap_sd"], dep["latent_cap_sd"])

    bmi_p = p["bmi"]
    mu_m, sigma_m = _lognormal_parameters(bmi_p["M"]["mean"], bmi_p["M"]["sd"])
    mu_f, sigma_f = _lognormal_parameters(bmi_p["F"]["mean"], bmi_p["F"]["sd"])
    log_bmi = (np.where(female, mu_f, mu_m)
               + np.where(female, sigma_f, sigma_m) * latent[:, 0]
               + bmi_p["log_change_per_age_scale"] * age_scaled)

    lipid_values = {}
    for column, latent_index in (("total_cholesterol", 1), ("hdl_cholesterol", 2)):
        lp = p[column]
        mu, sigma = _lognormal_parameters(lp["reference_mean"], lp["reference_sd"])
        sex_log_ratio = np.log(lp["female_reference_geometric_mean"]
                               / lp["male_reference_geometric_mean"])
        log_value = (mu + sigma * latent[:, latent_index]
                     + lp["log_change_per_age_scale"] * age_scaled
                     + (female.astype(float) - lp["sex_effect_center"]) * sex_log_ratio)
        lipid_values[column] = np.exp(log_value)

    data = {
        "id": [specification["identifier_prefix"] + f"{i + 1:06d}" for i in range(n)],
        "age": age,
        "sex": np.where(female, "F", "M"),
        "bmi": np.exp(log_bmi),
        "total_cholesterol": lipid_values["total_cholesterol"],
        "hdl_cholesterol": lipid_values["hdl_cholesterol"],
    }
    return pd.DataFrame(data, columns=specification["ordered_columns"])
