"""Whole-cohort finite age/sex mixture; execution belongs to the controller."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    n = p["n_rows"]
    ages = np.arange(p["age_min"], p["age_max"] + 1)
    age_center = ages.mean()
    scaled_ages = (ages - age_center) / p["age_effect_unit_years"]
    female_p = p["female_probability"]
    a = np.asarray(p["log_age_effects"], dtype=float)
    b = np.asarray(p["log_female_effects"], dtype=float)
    means = np.asarray(p["biomarker_means"], dtype=float)
    sds = np.asarray(p["biomarker_sds"], dtype=float)
    loadings = np.asarray(p["residual_factor_loadings"], dtype=float)

    def demographic_mgf(order):
        am = np.mean(np.exp(order * scaled_ages[:, None] * a), axis=0)
        fm = ((1 - female_p) * np.exp(-order * female_p * b)
              + female_p * np.exp(order * (1 - female_p) * b))
        return am * fm

    m1, m2 = demographic_mgf(1), demographic_mgf(2)
    log_variances = np.log1p((sds / means) ** 2) - np.log(m2 / m1 ** 2)
    if np.any(log_variances <= 0) or np.any(np.abs(loadings) >= 1):
        raise ValueError("Specification has invalid residual covariance")
    intercepts = np.log(means) - np.log(m1) - log_variances / 2
    rng = np.random.default_rng(seed)
    age = rng.integers(p["age_min"], p["age_max"] + 1, size=n)
    female = rng.binomial(1, female_p, size=n)
    common = rng.standard_normal((n, 1))
    individual = rng.standard_normal((n, len(means)))
    residual = np.sqrt(log_variances) * (
        common * loadings + individual * np.sqrt(1 - loadings ** 2)
    )
    log_values = (
        intercepts + (age[:, None] - age_center) / p["age_effect_unit_years"] * a
        + (female[:, None] - female_p) * b + residual
    )
    values = np.exp(log_values)
    result = pd.DataFrame({
        "row_id": [p["row_id_prefix"] + str(i + 1).zfill(p["row_id_width"]) for i in range(n)],
        "age": age,
        "female": female,
    })
    for j, name in enumerate(p["biomarker_order"]):
        result[name] = values[:, j]
    return result[p["output_columns"]]
