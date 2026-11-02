"""Whole-cohort scenario; finite inline derivations precede random generation."""

import math

import numpy as np
import pandas as pd
from scipy.special import betaincinv, gammaincinv, ndtr, ndtri


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    parameters = specification["parameters"]
    context_id = parameters["active_context"]
    context = parameters["contexts"][context_id]
    if not context["population"] or not context["measurement"]:
        raise ValueError("A complete declared context is required")
    n = int(context["n_rows"])
    if n != 5000:
        raise ValueError("The committed cohort size is 5000")
    inputs = context["inputs"]
    shared = parameters["shared_model"]
    age_spec = inputs["age_distribution"]
    bmi_spec = inputs["bmi_distribution"]
    dependence = inputs["dependence"]
    glucose_spec = inputs["glucose_baseline"]
    measurement = inputs["measurement_model"]

    # Finite population composition is fixed at the nearest integer allocation.
    sex_spec = inputs["sex_composition"]
    requested_p = sex_spec["female_numerator"] / sex_spec["denominator"]
    n_female = int(math.floor(n * requested_p + 0.5))
    if not 0 < n_female < n:
        raise ValueError("Both sex categories must be supported")
    p_female = n_female / n

    # All source-dependent arithmetic occurs before random sampling.
    age_family = age_spec["family"]
    if age_family == "bounded_beta_moments":
        age_lower, age_upper = age_spec["bounds"]
        age_width = age_upper - age_lower
        age_fraction_mean = (age_spec["mean"] - age_lower) / age_width
        age_fraction_var = (age_spec["sd"] / age_width) ** 2
        age_concentration = age_fraction_mean * (1 - age_fraction_mean) / age_fraction_var - 1
        age_alpha = age_fraction_mean * age_concentration
        age_beta = (1 - age_fraction_mean) * age_concentration
        if min(age_alpha, age_beta) <= 0:
            raise ValueError("Incompatible bounded age moments")
    elif age_family == "binned_beta_moments":
        counts = np.asarray(age_spec["counts"], dtype=float)
        weights = counts / age_spec["denominator"]
        lower = np.asarray(age_spec["lower"], dtype=float)
        upper = np.asarray(age_spec["upper"], dtype=float)
        width = upper - lower
        concentration = age_spec["endpoint_bin_concentration"]
        # Middle bins are uniform. Endpoint bins use Beta(k*m,k*(1-m)).
        middle_mean = np.sum(weights[1:3] * (lower[1:3] + width[1:3] / 2))
        middle_second = np.sum(weights[1:3] * (lower[1:3] ** 2 + lower[1:3] * width[1:3] + width[1:3] ** 2 / 3))
        first, last = 0, 3
        affine_a = (age_spec["mean"] - middle_mean - weights[first] * lower[first] - weights[last] * lower[last]) / (weights[last] * width[last])
        affine_b = -weights[first] * width[first] / (weights[last] * width[last])
        linear = 2 * lower * width + width ** 2 / (concentration + 1)
        quadratic = width ** 2 * concentration / (concentration + 1)
        qa = weights[first] * quadratic[first] + weights[last] * quadratic[last] * affine_b ** 2
        qb = weights[first] * linear[first] + weights[last] * (linear[last] * affine_b + 2 * quadratic[last] * affine_a * affine_b)
        qc = middle_second + weights[first] * lower[first] ** 2 + weights[last] * (lower[last] ** 2 + linear[last] * affine_a + quadratic[last] * affine_a ** 2) - (age_spec["mean"] ** 2 + age_spec["sd"] ** 2)
        discriminant = qb ** 2 - 4 * qa * qc
        if discriminant <= 0:
            raise ValueError("Incompatible binned age moments")
        first_mean = (-qb - math.sqrt(discriminant)) / (2 * qa)
        last_mean = affine_a + affine_b * first_mean
        if not (0 < first_mean < 1 and 0 < last_mean < 1):
            raise ValueError("Endpoint-bin beta means are infeasible")
        bin_alpha = np.array([concentration * first_mean, 1.0, 1.0, concentration * last_mean])
        bin_beta = np.array([concentration * (1 - first_mean), 1.0, 1.0, concentration * (1 - last_mean)])
        cumulative = np.cumsum(weights)
        cumulative[-1] = 1.0  # Exact total mass; prevent a floating-point end-bin overflow.
        preceding = np.concatenate(([0.0], cumulative[:-1]))
    elif age_family != "shifted_gamma":
        raise ValueError("Unrecognized declared age family")

    if bmi_spec["family"] == "lognormal_moments":
        bmi_log_variance = math.log1p((bmi_spec["sd"] / bmi_spec["mean"]) ** 2)
        bmi_log_sd = math.sqrt(bmi_log_variance)
        bmi_log_mean = math.log(bmi_spec["mean"]) - bmi_log_variance / 2
    elif bmi_spec["family"] == "category_quantile":
        bmi_weights = np.asarray(bmi_spec["counts"], dtype=float) / bmi_spec["denominator"]
        bmi_cut1 = bmi_weights[0]
        bmi_cut2 = bmi_weights[0] + bmi_weights[1]
    else:
        raise ValueError("Unrecognized declared BMI family")

    female_log_shift = shared["glucose_female_log_shift"]
    mixture_m1 = (1 - p_female) * math.exp(-female_log_shift * p_female) + p_female * math.exp(female_log_shift * (1 - p_female))
    mixture_m2 = (1 - p_female) * math.exp(-2 * female_log_shift * p_female) + p_female * math.exp(2 * female_log_shift * (1 - p_female))
    glucose_log_variance = math.log1p((glucose_spec["sd"] / glucose_spec["mean"]) ** 2) - math.log(mixture_m2 / mixture_m1 ** 2)
    if glucose_log_variance <= 0:
        raise ValueError("Glucose variance insufficient for the declared sex shift")
    glucose_log_sd = math.sqrt(glucose_log_variance)
    glucose_log_mean = math.log(glucose_spec["mean"]) - math.log(mixture_m1) - glucose_log_variance / 2
    bmi_age_rho = dependence["bmi_age_latent_correlation"]
    bmi_body_loading = math.sqrt(1 - bmi_age_rho ** 2)
    glucose_age_loading = shared["glucose_age_loading"]
    glucose_body_f = shared["glucose_body_loading_female"]
    glucose_body_m = shared["glucose_body_loading_male"]
    glucose_residual_f = math.sqrt(1 - glucose_age_loading ** 2 - glucose_body_f ** 2)
    glucose_residual_m = math.sqrt(1 - glucose_age_loading ** 2 - glucose_body_m ** 2)
    cdf_lower = np.nextafter(0.0, 1.0)
    cdf_upper = np.nextafter(1.0, 0.0)

    rng = np.random.default_rng(seed)
    female = rng.permutation(np.arange(n) < n_female)
    centered_sex = female.astype(float) - p_female
    z_age, z_body, z_glucose = rng.standard_normal((3, n))
    u_age = np.clip(ndtr(z_age), cdf_lower, cdf_upper)
    if age_family == "bounded_beta_moments":
        age = age_lower + age_width * betaincinv(age_alpha, age_beta, u_age)
    elif age_family == "binned_beta_moments":
        age_bin = np.searchsorted(cumulative, u_age, side="right")
        fraction = np.clip((u_age - preceding[age_bin]) / weights[age_bin], cdf_lower, cdf_upper)
        age = lower[age_bin] + width[age_bin] * betaincinv(bin_alpha[age_bin], bin_beta[age_bin], fraction)
    else:
        age = age_spec["minimum"] + age_spec["scale"] * gammaincinv(age_spec["shape"], u_age)

    # The analytic mixture CDF preserves BMI marginals while permitting sex shifts.
    bmi_shift = dependence["bmi_female_latent_shift"]
    z_bmi = bmi_age_rho * z_age + bmi_body_loading * z_body + bmi_shift * centered_sex
    u_bmi = (1 - p_female) * ndtr(z_bmi + bmi_shift * p_female) + p_female * ndtr(z_bmi - bmi_shift * (1 - p_female))
    u_bmi = np.clip(u_bmi, cdf_lower, cdf_upper)
    if bmi_spec["family"] == "lognormal_moments":
        bmi = np.exp(bmi_log_mean + bmi_log_sd * ndtri(u_bmi))
    else:
        bmi = np.empty(n, dtype=float)
        low = u_bmi < bmi_cut1
        middle = (u_bmi >= bmi_cut1) & (u_bmi < bmi_cut2)
        high = u_bmi >= bmi_cut2
        bmi[low] = bmi_spec["underweight_upper"] * (u_bmi[low] / bmi_cut1) ** (1 / bmi_spec["underweight_power"])
        bmi[middle] = bmi_spec["normal_lower"] + (bmi_spec["normal_upper"] - bmi_spec["normal_lower"]) * (u_bmi[middle] - bmi_cut1) / bmi_weights[1]
        high_fraction = np.clip((u_bmi[high] - bmi_cut2) / bmi_weights[2], cdf_lower, cdf_upper)
        bmi[high] = bmi_spec["overweight_lower"] - bmi_spec["overweight_excess_scale"] * np.log1p(-high_fraction)

    body_loading = np.where(female, glucose_body_f, glucose_body_m)
    residual_loading = np.where(female, glucose_residual_f, glucose_residual_m)
    glucose_rank = glucose_age_loading * z_age + body_loading * z_body + residual_loading * z_glucose
    persistent_glucose = np.exp(glucose_log_mean + glucose_log_sd * glucose_rank + female_log_shift * centered_sex)
    meal_reference = measurement["meal_probability_at_reference"]
    if meal_reference == 0:
        meal_probability = np.zeros(n)
    else:
        meal_logit = math.log(meal_reference / (1 - meal_reference)) + shared["meal_age_logit_loading"] * z_age + shared["meal_body_logit_loading"] * z_body + shared["meal_female_logit_loading"] * centered_sex
        meal_probability = 1 / (1 + np.exp(-meal_logit))
    glucose = np.zeros(n)
    for _ in range(measurement["replicate_count"]):
        fed = rng.random(n) < meal_probability
        meal_log = fed * (measurement["meal_log_increment"] + measurement["meal_log_sd"] * rng.standard_normal(n))
        device_sd = measurement["device_log_sd"]
        device_log = device_sd * rng.standard_normal(n) - device_sd ** 2 / 2
        glucose += persistent_glucose * np.exp(meal_log + device_log)
    glucose /= measurement["replicate_count"]

    if not (np.all(np.isfinite(age)) and np.all(np.isfinite(bmi)) and np.all(np.isfinite(glucose)) and np.all(bmi > 0) and np.all(glucose > 0)):
        raise ValueError("Invalid whole cohort; no filtering or repair is permitted")
    frame = pd.DataFrame({
        "id": [f"{context_id}:{int(seed)}:{index + 1:05d}" for index in range(n)],
        "age": age,
        "sex": np.where(female, "F", "M"),
        "bmi": bmi,
        "glucose": glucose,
    }, columns=parameters["output_columns"])
    return frame
