"""Whole-cohort constructor; finite parameter arithmetic precedes random draws.

This module performs no input/output. Scientific numbers live in model_spec.json.
Source reproduction and target validity must be assessed outside this module.
"""

import numpy as np
import pandas as pd
from scipy.special import ndtr
from scipy.stats import beta, gamma


def _lognormal_parameters(mean, variance):
    log_variance = np.log1p(variance / (mean * mean))
    return np.log(mean) - 0.5 * log_variance, np.sqrt(log_variance)


def _sex_moments(mean, sd, female_minus_male, female_fraction):
    means = np.array([
        mean - female_fraction * female_minus_male,
        mean + (1.0 - female_fraction) * female_minus_male,
    ])
    variance = sd * sd - female_fraction * (1.0 - female_fraction) * female_minus_male ** 2
    if variance <= 0.0 or np.any(means <= 0.0):
        raise ValueError("Incompatible mixture moments")
    return means, variance


def _bounded_beta_parameters(mean, variance, lower, upper):
    fraction = (mean - lower) / (upper - lower)
    concentration = fraction * (1.0 - fraction) * (upper - lower) ** 2 / variance - 1.0
    if np.any(fraction <= 0.0) or np.any(fraction >= 1.0) or np.any(concentration <= 0.0):
        raise ValueError("Incompatible bounded-beta moments")
    return fraction * concentration, (1.0 - fraction) * concentration


def _prepare_age(config, female_fraction):
    family = config["family"]
    result = dict(config)
    if family == "bounded_beta":
        means, variance = _sex_moments(config["mean"], config["sd"], config["female_minus_male"], female_fraction)
        result["alpha"], result["beta"] = _bounded_beta_parameters(means, variance, config["lower"], config["upper"])
    elif family == "bin_beta":
        probabilities = np.asarray(config["counts"], dtype=float) / config["denominator"]
        lower = np.asarray(config["lower"], dtype=float)
        upper = np.asarray(config["upper"], dtype=float)
        means = np.asarray(config["within_means_prefix"] + [0.0], dtype=float)
        means[-1] = (config["mean"] - np.dot(probabilities[:-1], means[:-1])) / probabilities[-1]
        between = np.dot(probabilities, (means - config["mean"]) ** 2)
        within_variance = config["sd"] ** 2 - between
        fraction = (means - lower) / (upper - lower)
        concentration = np.dot(probabilities, (means - lower) * (upper - means)) / within_variance - 1.0
        if within_variance <= 0.0 or concentration <= 0.0 or np.any(fraction <= 0.0) or np.any(fraction >= 1.0):
            raise ValueError("Incompatible age-bin moments")
        result.update(probabilities=probabilities, alpha=fraction * concentration, beta=(1.0 - fraction) * concentration)
    elif family == "shifted_gamma":
        means = np.array([
            config["excess_mean"] - female_fraction * config["female_minus_male"],
            config["excess_mean"] + (1.0 - female_fraction) * config["female_minus_male"],
        ])
        result["shape"] = means ** 2 / config["within_sd"] ** 2
        result["scale"] = config["within_sd"] ** 2 / means
    else:
        raise ValueError("Unknown age family")
    return result


def _age_quantile(uniform, female, config, epsilon):
    if config["family"] == "bounded_beta":
        index = female.astype(int)
        return config["lower"] + (config["upper"] - config["lower"]) * beta.ppf(uniform, config["alpha"][index], config["beta"][index])
    if config["family"] == "shifted_gamma":
        index = female.astype(int)
        return config["lower"] + gamma.ppf(uniform, config["shape"][index], scale=config["scale"][index])
    cumulative = np.cumsum(config["probabilities"])
    cumulative[-1] = 1.0
    group = np.searchsorted(cumulative, uniform, side="right")
    previous = np.r_[0.0, cumulative[:-1]]
    local = np.clip((uniform - previous[group]) / config["probabilities"][group], epsilon, 1.0 - epsilon)
    lower = np.asarray(config["lower"], dtype=float)[group]
    upper = np.asarray(config["upper"], dtype=float)[group]
    value = lower + (upper - lower) * beta.ppf(local, config["alpha"][group], config["beta"][group])
    # Preserve declared half-open bins when inverse-CDF rounding reaches an endpoint.
    return np.minimum(value, np.nextafter(upper, lower))


def _prepare_bmi(config, female_fraction):
    result = dict(config)
    if config["family"] == "sex_lognormal":
        means, variance = _sex_moments(config["mean"], config["sd"], config["female_minus_male"], female_fraction)
        result["log_mean"], result["log_sd"] = _lognormal_parameters(means, variance)
    elif config["family"] == "category_mixture":
        probabilities = np.asarray(config["counts"], dtype=float) / config["denominator"]
        difference = np.asarray(config["female_minus_male_probabilities"], dtype=float)
        result["probabilities"] = np.vstack([
            probabilities - female_fraction * difference,
            probabilities + (1.0 - female_fraction) * difference,
        ])
        if np.any(result["probabilities"] <= 0.0):
            raise ValueError("Incompatible BMI category probabilities")
    else:
        raise ValueError("Unknown BMI family")
    return result


def _bmi_quantile(normal, female, config, epsilon):
    index = female.astype(int)
    if config["family"] == "sex_lognormal":
        return np.exp(config["log_mean"][index] + config["log_sd"][index] * normal)
    uniform = np.clip(ndtr(normal), epsilon, 1.0 - epsilon)
    value = np.empty(len(normal), dtype=float)
    for sex_index in (0, 1):
        selected = index == sex_index
        probabilities = config["probabilities"][sex_index]
        cumulative = np.cumsum(probabilities)
        cumulative[-1] = 1.0
        group = np.searchsorted(cumulative, uniform[selected], side="right")
        previous = np.r_[0.0, cumulative[:-1]]
        local = np.clip((uniform[selected] - previous[group]) / probabilities[group], epsilon, 1.0 - epsilon)
        values = np.empty(len(local), dtype=float)
        under = group == 0
        normal_weight = group == 1
        over = group == 2
        values[under] = config["underweight_lower"] + (config["underweight_upper"] - config["underweight_lower"]) * local[under]
        values[normal_weight] = config["normal_lower"] + (config["normal_upper"] - config["normal_lower"]) * local[normal_weight]
        values[over] = config["overweight_lower"] + gamma.ppf(local[over], config["overweight_shape"], scale=config["overweight_scale"])
        value[selected] = values
    return value


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    parameters = specification["parameters"]
    context_id = parameters["active_context"]
    context = parameters["contexts"][context_id]
    inputs = context["inputs"]
    n_rows = int(context["n_rows"])
    if n_rows != 5000 or not isinstance(context["population"], str) or not isinstance(context["measurement"], str):
        raise ValueError("Unexpected context descriptor")
    settings = parameters["shared_settings"]
    epsilon = settings["cdf_epsilon"]

    # All finite parameter derivations occur before random generation.
    sex_config = inputs["sex_distribution"]
    female_probability = sex_config["numerator"] / sex_config["denominator"]
    n_female = int(np.floor(n_rows * female_probability + 0.5))
    if not 0 < n_female < n_rows:
        raise ValueError("Both sexes must be represented")
    female_fraction = n_female / n_rows
    age_config = _prepare_age(inputs["age_distribution"], female_fraction)
    bmi_config = _prepare_bmi(inputs["bmi_distribution"], female_fraction)
    glucose_config = inputs["glucose_baseline"]
    glucose_means, glucose_variance = _sex_moments(glucose_config["mean"], glucose_config["sd"], settings["glucose_female_minus_male"], female_fraction)
    glucose_log_mean, glucose_log_sd = _lognormal_parameters(glucose_means, glucose_variance)
    age_bmi = inputs["dependence"]["age_bmi_latent_correlation"]
    age_loading = settings["glucose_age_latent_loading"]
    bmi_loadings = np.asarray(settings["glucose_bmi_residual_loadings_male_female"], dtype=float)
    glucose_residual = np.sqrt(1.0 - age_loading ** 2 - bmi_loadings ** 2)
    feeding = inputs["feeding"]
    meal = settings["meal_increment"]
    meal_shape = (meal["mean"] / meal["sd"]) ** 2
    meal_scale = meal["sd"] ** 2 / meal["mean"]
    measurement = inputs["measurement_model"]
    measurement_log_sd = np.sqrt(np.log1p(measurement["multiplicative_cv"] ** 2))
    repetitions = int(measurement["repetitions"])

    rng = np.random.default_rng(seed)
    female = np.arange(n_rows) < n_female
    rng.shuffle(female)
    sex_index = female.astype(int)
    independent = rng.standard_normal((n_rows, 3))
    age_latent = independent[:, 0]
    bmi_residual = independent[:, 1]
    bmi_latent = age_bmi * age_latent + np.sqrt(1.0 - age_bmi ** 2) * bmi_residual
    glucose_latent = age_loading * age_latent + bmi_loadings[sex_index] * bmi_residual + glucose_residual[sex_index] * independent[:, 2]
    age_uniform = np.clip(ndtr(age_latent), epsilon, 1.0 - epsilon)
    age = _age_quantile(age_uniform, female, age_config, epsilon)
    bmi = _bmi_quantile(bmi_latent, female, bmi_config, epsilon)
    glucose_baseline = np.exp(glucose_log_mean[sex_index] + glucose_log_sd[sex_index] * glucose_latent)
    glucose = np.zeros(n_rows, dtype=float)
    for _ in range(repetitions):
        fed = rng.random(n_rows) < feeding["nonfasting_probability"]
        meal_increment = rng.gamma(meal_shape, meal_scale, n_rows)
        multiplier = np.exp(measurement_log_sd * rng.standard_normal(n_rows) - 0.5 * measurement_log_sd ** 2)
        glucose += (glucose_baseline + fed * meal_increment) * multiplier
    glucose /= repetitions

    return pd.DataFrame({
        "id": [f"{context_id}-{i + 1:05d}" for i in range(n_rows)],
        "age": age,
        "sex": np.where(female, "F", "M"),
        "bmi": bmi,
        "glucose": glucose,
    }, columns=settings["columns"])
