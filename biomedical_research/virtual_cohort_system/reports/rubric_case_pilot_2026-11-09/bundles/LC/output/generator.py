"""Fictional LC cohort under the law documented in model_spec.json.

Only definitions/imports run at import time. No output-fitting or seed selection.
"""

import math

import numpy as np
import pandas as pd


def _log_age_mgf(coefficient, shape, scale):
    """Log MGF of Gamma(shape, scale) centered at its mean."""
    return -shape * scale * coefficient - shape * math.log1p(-scale * coefficient)


def _log_sex_mgf(coefficient, probability_f):
    return math.log((1.0 - probability_f) + probability_f * math.exp(coefficient))


def generate(observed, specification, seed):
    """Return exactly the task's 3,000 fictional, complete rows in mmol/L."""
    if observed is not None:
        raise ValueError("This whole-cohort construction requires observed=None.")

    contract = specification["contract"]
    n = int(contract["n_rows"])
    if n != 3000:
        raise ValueError("This submitted task requires exactly 3000 rows.")
    parameters = specification["parameters"]
    rng = np.random.default_rng(seed)

    p_f = float(parameters["sex"]["probability_F"])
    female = rng.random(n) < p_f
    age_parameters = parameters["age"]
    shape = float(age_parameters["gamma_shape"])
    scale = float(age_parameters["gamma_scale_years"])
    age_minimum = float(age_parameters["minimum_years"])
    age = age_minimum + rng.gamma(shape, scale, size=n)
    age_centered = age - (age_minimum + shape * scale)

    rank_parameters = parameters["copula"]["assumed_conditional_spearman"]
    r_b_tc = 2.0 * math.sin(math.pi * float(rank_parameters["bmi_tc"]) / 6.0)
    r_b_hdl = 2.0 * math.sin(math.pi * float(rank_parameters["bmi_hdl"]) / 6.0)
    r_tc_hdl = 2.0 * math.sin(math.pi * float(rank_parameters["tc_hdl"]) / 6.0)
    correlation = np.array([
        [1.0, r_b_tc, r_b_hdl],
        [r_b_tc, 1.0, r_tc_hdl],
        [r_b_hdl, r_tc_hdl, 1.0],
    ])
    latent = rng.standard_normal((n, 3)) @ np.linalg.cholesky(correlation).T

    bmi_parameters = parameters["bmi"]
    bmi_mean = np.where(female, bmi_parameters["F"]["arithmetic_mean"],
                        bmi_parameters["M"]["arithmetic_mean"])
    bmi_sd = np.where(female, bmi_parameters["F"]["individual_sd"],
                      bmi_parameters["M"]["individual_sd"])
    bmi_log_variance = np.log1p((bmi_sd / bmi_mean) ** 2)
    bmi = np.exp(np.log(bmi_mean) - 0.5 * bmi_log_variance
                 + np.sqrt(bmi_log_variance) * latent[:, 0])

    lipids = {}
    for latent_column, name in enumerate(
        ("total_cholesterol", "hdl_cholesterol"), start=1
    ):
        settings = parameters["lipids"][name]
        marginal_mean = float(settings["arithmetic_mean_mmol_L"])
        marginal_sd = float(settings["individual_sd_mmol_L"])
        age_coefficient = float(settings["assumed_log_age_coefficient_per_year"])
        female_log_ratio = math.log(
            float(settings["sex_geometric_mean_anchors"]["F"])
            / float(settings["sex_geometric_mean_anchors"]["M"])
        )
        log_age_first = _log_age_mgf(age_coefficient, shape, scale)
        log_age_second = _log_age_mgf(2.0 * age_coefficient, shape, scale)
        log_sex_first = _log_sex_mgf(female_log_ratio, p_f)
        log_sex_second = _log_sex_mgf(2.0 * female_log_ratio, p_f)
        normal_log_variance = (
            math.log1p((marginal_sd / marginal_mean) ** 2)
            - (log_age_second - 2.0 * log_age_first)
            - (log_sex_second - 2.0 * log_sex_first)
        )
        if normal_log_variance <= 0.0:
            raise ValueError("Covariate effects exhaust the specified marginal variance.")
        log_intercept = (
            math.log(marginal_mean) - log_age_first - log_sex_first
            - 0.5 * normal_log_variance
        )
        lipids[name] = np.exp(
            log_intercept + age_coefficient * age_centered
            + female_log_ratio * female + math.sqrt(normal_log_variance) * latent[:, latent_column]
        )

    result = pd.DataFrame({
        "id": [contract["identifier_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": age,
        "sex": np.where(female, "F", "M"),
        "bmi": bmi,
        "total_cholesterol": lipids["total_cholesterol"],
        "hdl_cholesterol": lipids["hdl_cholesterol"],
    }, columns=contract["ordered_columns"])
    return result
