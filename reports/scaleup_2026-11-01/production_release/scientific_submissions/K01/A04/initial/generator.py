"""Unexecuted whole-cohort construction; all scientific choices are in the spec."""

import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri
from scipy.stats import beta as beta_distribution
from scipy.stats import gamma as gamma_distribution


def _lognormal_parameters(mean, sd):
    variance = np.log1p((float(sd) / float(mean)) ** 2)
    return np.log(float(mean)) - variance / 2.0, np.sqrt(variance)


def _prepare_age(settings):
    """Finite source arithmetic, before any random numbers; never sample fitting."""
    kind = settings["family"]
    result = dict(settings)
    if kind == "bounded_beta":
        width = settings["maximum"] - settings["minimum"]
        m = (settings["mean"] - settings["minimum"]) / width
        v = (settings["sd"] / width) ** 2
        concentration = m * (1.0 - m) / v - 1.0
        result["alpha"] = m * concentration
        result["beta"] = (1.0 - m) * concentration
        if min(result["alpha"], result["beta"]) <= 0:
            raise ValueError("Incompatible bounded-beta moments")
    elif kind == "grouped_beta_mixture":
        counts = np.asarray(settings["counts"], dtype=float)
        probabilities = counts / float(settings["denominator"])
        lower = np.asarray(settings["lower"], dtype=float)
        width = np.asarray(settings["upper"], dtype=float) - lower
        alpha = np.asarray(settings["prototype_alpha"], dtype=float)
        beta = np.asarray(settings["prototype_beta"], dtype=float)
        fractions = alpha / (alpha + beta)
        fraction_variances = alpha * beta / ((alpha + beta) ** 2 * (alpha + beta + 1.0))
        component_means = lower[None, :] + width[None, :] * fractions
        means = component_means @ probabilities
        second_moments = (component_means ** 2 + width[None, :] ** 2 * fraction_variances) @ probabilities
        matrix = np.vstack((np.ones(len(means)), means, second_moments))
        moments = np.array([1.0, settings["mean"], settings["mean"] ** 2 + settings["sd"] ** 2])
        weights = np.linalg.solve(matrix, moments)
        if not np.all(np.isfinite(weights)) or np.any(weights < 0.0) or np.any(weights > 1.0):
            raise ValueError("Source age moments outside the declared prototype mixture")
        result["probabilities"] = probabilities
        result["prototype_weights"] = weights
    elif kind != "shifted_gamma":
        raise ValueError("Unknown age family")
    return result


def _mixture_rank_tails(z, shift, female, female_probability):
    """Probability integral transform of a two-normal location mixture."""
    value = z + float(shift) * female
    p = float(female_probability)
    lower = (1.0 - p) * ndtr(value) + p * ndtr(value - shift)
    upper = (1.0 - p) * ndtr(-value) + p * ndtr(shift - value)
    return lower, upper


def _normal_quantile(lower, upper):
    result = np.empty_like(lower)
    left = lower <= 0.5
    result[left] = ndtri(lower[left])
    result[~left] = -ndtri(upper[~left])
    return result


def _beta_quantile(lower, upper, alpha, beta):
    a = np.broadcast_to(np.asarray(alpha), lower.shape)
    b = np.broadcast_to(np.asarray(beta), lower.shape)
    result = np.empty_like(lower)
    left = lower <= 0.5
    result[left] = beta_distribution.ppf(lower[left], a[left], b[left])
    result[~left] = beta_distribution.isf(upper[~left], a[~left], b[~left])
    return result


def _gamma_quantile(lower, upper, shape, scale):
    result = np.empty_like(lower)
    left = lower <= 0.5
    result[left] = gamma_distribution.ppf(lower[left], a=shape, scale=scale)
    result[~left] = gamma_distribution.isf(upper[~left], a=shape, scale=scale)
    return result


def _group_ranks(lower, upper, probabilities):
    cumulative = np.cumsum(probabilities)
    cumulative[-1] = 1.0
    group = np.searchsorted(cumulative, lower, side="right")
    group = np.minimum(group, len(probabilities) - 1)
    prior = np.concatenate(([0.0], cumulative[:-1]))
    local_lower = (lower - prior[group]) / probabilities[group]
    local_upper = (upper - (1.0 - cumulative[group])) / probabilities[group]
    # These bounds concern floating-point probability subtraction only, not rows
    # or clinical values; both tails are retained to avoid a target-age cutoff.
    return group, np.clip(local_lower, 0.0, 1.0), np.clip(local_upper, 0.0, 1.0)


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    parameters = specification["parameters"]
    context_id = parameters["active_context"]
    descriptor = parameters["contexts"][context_id]
    if not isinstance(descriptor["population"], str) or not isinstance(descriptor["measurement"], str):
        raise TypeError("Context descriptors must contain copied text")
    n = int(descriptor["n_rows"])
    if n != 5000:
        raise ValueError("This declared schedule requires exactly 5000 rows")
    inputs = descriptor["inputs"]
    age_parameters = _prepare_age(inputs["age"])
    bmi_parameters = inputs["bmi"]
    if bmi_parameters["family"] == "lognormal":
        bmi_location, bmi_scale = _lognormal_parameters(bmi_parameters["mean"], bmi_parameters["sd"])
    elif bmi_parameters["family"] == "category_quantiles":
        bmi_probabilities = np.asarray(bmi_parameters["counts"], dtype=float) / bmi_parameters["denominator"]
    else:
        raise ValueError("Unknown BMI family")
    glucose_location, glucose_scale = _lognormal_parameters(inputs["glucose_baseline"]["mean"], inputs["glucose_baseline"]["sd"])
    p_female = float(inputs["female_probability"])
    joint = parameters["joint_copula"]
    rho = float(joint["age_bmi_correlation"])
    a = float(joint["glucose_age_loading"])
    loadings = np.array([joint["glucose_bmi_loading_male"], joint["glucose_bmi_loading_female"]], dtype=float)
    residual_variances = 1.0 - a ** 2 - loadings ** 2 - 2.0 * a * loadings * rho
    if not 0.0 < p_female < 1.0 or np.any(residual_variances <= 0.0):
        raise ValueError("Invalid declared copula or sex composition")
    feeding = inputs["feeding"]
    measurement = inputs["poc_measurement"]
    meal_shape = (feeding["increment_mean"] / feeding["increment_sd"]) ** 2
    meal_scale = feeding["increment_sd"] ** 2 / feeding["increment_mean"]
    measurement_log_variance = np.log1p(measurement["cv"] ** 2)
    measurement_log_location = np.log(measurement["multiplier"]) - measurement_log_variance / 2.0
    repeat_count = int(measurement["repeat_count"])
    if repeat_count < 1:
        raise ValueError("Invalid measurement repeat count")

    # All distribution parameters above were fixed or deterministically derived
    # from the specification before this first random draw.
    rng = np.random.default_rng(seed)
    female_count = int(np.floor(n * p_female + rng.random()))
    female = np.zeros(n, dtype=int)
    female[:female_count] = 1
    rng.shuffle(female)
    independent = rng.standard_normal((3, n))
    z_age = independent[0]
    z_bmi = rho * z_age + np.sqrt(1.0 - rho ** 2) * independent[1]
    b = loadings[female]
    z_glucose = a * z_age + b * z_bmi + np.sqrt(residual_variances[female]) * independent[2]
    shifts = inputs["sex_rank_shifts"]
    age_lower, age_upper = _mixture_rank_tails(z_age, shifts["age"], female, p_female)
    bmi_lower, bmi_upper = _mixture_rank_tails(z_bmi, shifts["bmi"], female, p_female)
    glucose_lower, glucose_upper = _mixture_rank_tails(z_glucose, shifts["glucose"], female, p_female)

    age_family = age_parameters["family"]
    if age_family == "bounded_beta":
        age = age_parameters["minimum"] + (age_parameters["maximum"] - age_parameters["minimum"]) * _beta_quantile(age_lower, age_upper, age_parameters["alpha"], age_parameters["beta"])
    elif age_family == "shifted_gamma":
        age = age_parameters["minimum"] + _gamma_quantile(age_lower, age_upper, age_parameters["shape"], age_parameters["scale"])
    else:
        group, lower, upper = _group_ranks(age_lower, age_upper, age_parameters["probabilities"])
        prototype = rng.choice(len(age_parameters["prototype_weights"]), size=n, p=age_parameters["prototype_weights"])
        alpha = np.asarray(age_parameters["prototype_alpha"])[prototype, group]
        beta = np.asarray(age_parameters["prototype_beta"])[prototype, group]
        bounds_lower = np.asarray(age_parameters["lower"])[group]
        bounds_upper = np.asarray(age_parameters["upper"])[group]
        age = bounds_lower + (bounds_upper - bounds_lower) * _beta_quantile(lower, upper, alpha, beta)

    if bmi_parameters["family"] == "lognormal":
        bmi = np.exp(bmi_location + bmi_scale * _normal_quantile(bmi_lower, bmi_upper))
    else:
        group, lower, upper = _group_ranks(bmi_lower, bmi_upper, bmi_probabilities)
        bmi = np.empty(n, dtype=float)
        for category in (0, 1):
            selected = group == category
            values = _beta_quantile(lower[selected], upper[selected], bmi_parameters["within_beta_alpha"], bmi_parameters["within_beta_beta"])
            lo = bmi_parameters["lower"][category]
            hi = bmi_parameters["upper"][category]
            bmi[selected] = lo + (hi - lo) * values
        selected = group == 2
        bmi[selected] = bmi_parameters["upper_tail_origin"] + _gamma_quantile(lower[selected], upper[selected], bmi_parameters["upper_tail_shape"], bmi_parameters["upper_tail_scale"])

    basal_glucose = np.exp(glucose_location + glucose_scale * _normal_quantile(glucose_lower, glucose_upper))
    glucose = np.zeros(n, dtype=float)
    for _ in range(repeat_count):
        fed = rng.random(n) < feeding["probability"]
        increment = rng.gamma(meal_shape, meal_scale, size=n) * fed
        instrument_factor = np.exp(measurement_log_location + np.sqrt(measurement_log_variance) * rng.standard_normal(n))
        glucose += (basal_glucose + increment) * instrument_factor / repeat_count

    values = np.column_stack((age, bmi, glucose))
    if not np.all(np.isfinite(values)) or np.any(bmi <= 0.0) or np.any(glucose <= 0.0):
        raise ValueError("Invalid clinical values; entire output rejected")
    if np.any(age < inputs["age"]["minimum"]):
        raise ValueError("Age below context eligibility; entire output rejected")
    if inputs["age"]["maximum"] is not None and np.any(age > inputs["age"]["maximum"]):
        raise ValueError("Age above context eligibility; entire output rejected")
    return pd.DataFrame({
        "id": [context_id + ":" + str(i + 1).zfill(6) for i in range(n)],
        "age": age,
        "sex": np.where(female == 1, "F", "M"),
        "bmi": bmi,
        "glucose": glucose,
    }, columns=["id", "age", "sex", "bmi", "glucose"])
