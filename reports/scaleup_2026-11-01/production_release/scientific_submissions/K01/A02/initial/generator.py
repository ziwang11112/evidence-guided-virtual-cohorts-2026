"""Whole-cohort candidate; parameter derivations precede random generation.

No fitting, sample calibration, external inputs, or execution at import time.
"""

import math

import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri
from scipy.stats import beta, gamma


def _interior(probability):
    """Handle floating-point CDF endpoints, not a scientific tail cutoff."""
    return np.clip(probability, np.nextafter(0.0, 1.0), np.nextafter(1.0, 0.0))


def _beta_shapes(mean, variance, lower, upper):
    width = upper - lower
    q = (mean - lower) / width
    v = variance / (width * width)
    concentration = q * (1.0 - q) / v - 1.0
    if not (0.0 < q < 1.0 and concentration > 0.0):
        raise ValueError("Infeasible specified beta moments")
    return q * concentration, (1.0 - q) * concentration


def _lognormal_parameters(mean, sd):
    variance_log = math.log1p((sd / mean) ** 2)
    return math.log(mean) - variance_log / 2.0, math.sqrt(variance_log)


def _mixture_rank(score, female_probability, sex_shift):
    """CDF of a two-location, unit-variance Gaussian mixture."""
    p = female_probability
    return _interior(
        (1.0 - p) * ndtr(score + sex_shift * p)
        + p * ndtr(score - sex_shift * (1.0 - p))
    )


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    parameters = specification["parameters"]
    context_id = parameters["active_context"]
    context = parameters["contexts"][context_id]
    inputs = context["inputs"]
    n = context["n_rows"]
    if n != 5000:
        raise ValueError("This prospective schedule requires exactly 5000 rows")

    # All parameter arithmetic below is finite and independent of generated rows.
    female = inputs["female_composition"]
    p_female = female["numerator"] / female["denominator"]
    age_spec = inputs["age_distribution"]
    if age_spec["family"] == "bounded_beta":
        age_alpha, age_beta = _beta_shapes(
            age_spec["mean"], age_spec["sd"] ** 2,
            age_spec["lower"], age_spec["upper"]
        )
    elif age_spec["family"] == "category_moment_beta":
        age_weights = np.asarray(age_spec["counts"], dtype=float) / age_spec["denominator"]
        age_lower = np.asarray(age_spec["lower"], dtype=float)
        age_upper = np.asarray(age_spec["upper"], dtype=float)
        midpoints = (age_lower + age_upper) / 2.0
        center = float(np.sum(age_weights * midpoints))
        between_midpoint_variance = float(np.sum(age_weights * (midpoints - center) ** 2))
        within_variance = age_spec["within_bin_sd"] ** 2
        dilation = math.sqrt((age_spec["sd"] ** 2 - within_variance) / between_midpoint_variance)
        age_conditional_means = age_spec["mean"] + dilation * (midpoints - center)
        age_shapes = [
            _beta_shapes(float(m), within_variance, float(lo), float(hi))
            for m, lo, hi in zip(age_conditional_means, age_lower, age_upper)
        ]
        age_cumulative = np.cumsum(age_weights)
        age_cumulative[-1] = 1.0
        age_previous = np.r_[0.0, age_cumulative[:-1]]
    elif age_spec["family"] != "shifted_gamma":
        raise ValueError("Unknown age family")

    bmi_spec = inputs["bmi_distribution"]
    if bmi_spec["family"] == "lognormal":
        bmi_log_mean, bmi_log_sd = _lognormal_parameters(bmi_spec["mean"], bmi_spec["sd"])
    elif bmi_spec["family"] == "category_quantiles":
        bmi_weights = np.asarray(bmi_spec["counts"], dtype=float) / bmi_spec["denominator"]
        bmi_cumulative = np.cumsum(bmi_weights)
        bmi_cumulative[-1] = 1.0
        bmi_previous = np.r_[0.0, bmi_cumulative[:-1]]
    else:
        raise ValueError("Unknown BMI family")
    glucose_spec = inputs["glucose_distribution"]
    glucose_log_mean, glucose_log_sd = _lognormal_parameters(glucose_spec["mean"], glucose_spec["sd"])
    measurement = inputs["measurement"]
    error_log_sd = math.sqrt(math.log1p(measurement["multiplicative_error_cv"] ** 2))
    joint = parameters["joint_structure"]
    rho = joint["age_bmi_loading"]
    age_loading = joint["glucose_age_loading"]
    bmi_male = joint["glucose_bmi_residual_loading_male"]
    bmi_female = joint["glucose_bmi_residual_loading_female"]
    bmi_residual_scale = math.sqrt(1.0 - rho ** 2)
    glucose_residual_male = math.sqrt(1.0 - age_loading ** 2 - bmi_male ** 2)
    glucose_residual_female = math.sqrt(1.0 - age_loading ** 2 - bmi_female ** 2)

    # Random generation begins only after the above parameter derivation.
    rng = np.random.default_rng(seed)
    is_female = rng.random(n) < p_female
    sex = np.where(is_female, "F", "M")
    centered_sex = is_female.astype(float) - p_female
    latent_age, residual_bmi, residual_glucose = rng.standard_normal((3, n))
    age_rank = _interior(ndtr(latent_age))
    if age_spec["family"] == "bounded_beta":
        age = age_spec["lower"] + (age_spec["upper"] - age_spec["lower"]) * beta.ppf(age_rank, age_alpha, age_beta)
    elif age_spec["family"] == "category_moment_beta":
        age_group = np.searchsorted(age_cumulative, age_rank, side="right")
        age = np.empty(n, dtype=float)
        for k, (a, b) in enumerate(age_shapes):
            in_group = age_group == k
            conditional_rank = _interior((age_rank[in_group] - age_previous[k]) / age_weights[k])
            age[in_group] = age_lower[k] + (age_upper[k] - age_lower[k]) * beta.ppf(conditional_rank, a, b)
    else:
        age = age_spec["lower"] + gamma.ppf(age_rank, a=age_spec["shape"], scale=age_spec["scale"])

    shifts = inputs["sex_shifts"]
    bmi_score = rho * latent_age + bmi_residual_scale * residual_bmi + shifts["bmi"] * centered_sex
    bmi_rank = _mixture_rank(bmi_score, p_female, shifts["bmi"])
    if bmi_spec["family"] == "lognormal":
        bmi = np.exp(bmi_log_mean + bmi_log_sd * ndtri(bmi_rank))
    else:
        bmi_group = np.searchsorted(bmi_cumulative, bmi_rank, side="right")
        bmi = np.empty(n, dtype=float)
        for k in range(3):
            in_group = bmi_group == k
            conditional_rank = _interior((bmi_rank[in_group] - bmi_previous[k]) / bmi_weights[k])
            if k == 0:
                bmi[in_group] = bmi_spec["underweight_upper"] * conditional_rank ** (1.0 / bmi_spec["underweight_power"])
            elif k == 1:
                bmi[in_group] = bmi_spec["normal_lower"] + (bmi_spec["normal_upper"] - bmi_spec["normal_lower"]) * beta.ppf(
                    conditional_rank, bmi_spec["normal_alpha"], bmi_spec["normal_beta"]
                )
            else:
                bmi[in_group] = bmi_spec["high_lower"] + gamma.ppf(
                    conditional_rank, a=bmi_spec["high_shape"], scale=bmi_spec["high_scale"]
                )

    glucose_bmi_loading = np.where(is_female, bmi_female, bmi_male)
    glucose_residual_scale = np.where(is_female, glucose_residual_female, glucose_residual_male)
    glucose_score = (
        age_loading * latent_age + glucose_bmi_loading * residual_bmi
        + glucose_residual_scale * residual_glucose + shifts["glucose"] * centered_sex
    )
    glucose_rank = _mixture_rank(glucose_score, p_female, shifts["glucose"])
    baseline_glucose = np.exp(glucose_log_mean + glucose_log_sd * ndtri(glucose_rank))
    recorded_sum = np.zeros(n, dtype=float)
    for _ in range(measurement["replicate_count"]):
        fed = rng.random(n) < measurement["feeding_probability"]
        meal = rng.gamma(measurement["meal_shape"], measurement["meal_scale"], n) * fed
        error = np.exp(error_log_sd * rng.standard_normal(n) - error_log_sd ** 2 / 2.0)
        recorded_sum += measurement["scale_factor"] * (baseline_glucose + meal) * error
    glucose = recorded_sum / measurement["replicate_count"]

    # Fail the complete output; never drop, repair, or replace individual rows.
    if not (np.isfinite(age).all() and np.isfinite(bmi).all() and np.isfinite(glucose).all()):
        raise ValueError("Nonfinite generated clinical value")
    age_minimum = age_spec["lower"] if np.isscalar(age_spec["lower"]) else min(age_spec["lower"])
    if not ((bmi > 0.0).all() and (glucose > 0.0).all() and (age >= age_minimum).all()):
        raise ValueError("Generated value violates context support")
    if age_spec["family"] == "bounded_beta" and not (age <= age_spec["upper"]).all():
        raise ValueError("Age exceeds bounded source context")
    if age_spec["family"] == "category_moment_beta" and not (age <= max(age_spec["upper"])).all():
        raise ValueError("Age exceeds bounded source context")
    identifiers = [f"{context_id}:{i + 1:05d}" for i in range(n)]
    return pd.DataFrame({"id": identifiers, "age": age, "sex": sex, "bmi": bmi, "glucose": glucose}, columns=parameters["numerics"]["ordered_columns"])
