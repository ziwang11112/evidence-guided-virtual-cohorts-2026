"""Whole-cohort construction; no fitting, external input, or execution at authoring."""

import numpy as np
import pandas as pd
from scipy.special import ndtr
from scipy.stats import beta as beta_distribution
from scipy.stats import gamma as gamma_distribution


def _open_probability(value):
    """Protect inverse CDFs from floating-point endpoints, not clinical tails."""
    return np.clip(value, np.nextafter(0.0, 1.0), np.nextafter(1.0, 0.0))


def _lognormal_parameters(mean, sd):
    variance = np.log1p((float(sd) / float(mean)) ** 2)
    return np.log(float(mean)) - variance / 2.0, np.sqrt(variance)


def _prepare_age(settings):
    family = settings["family"]
    if family == "bounded_beta_moments":
        lower = float(settings["lower"])
        width = float(settings["upper"]) - lower
        mean = (float(settings["mean"]) - lower) / width
        variance = (float(settings["sd"]) / width) ** 2
        concentration = mean * (1.0 - mean) / variance - 1.0
        if not (0.0 < mean < 1.0 and concentration > 0.0):
            raise ValueError("Incompatible bounded beta moments")
        return {"family": family, "lower": lower, "width": width,
                "alpha": mean * concentration,
                "beta": (1.0 - mean) * concentration}
    if family == "binned_beta_moments":
        counts = np.asarray(settings["counts"], dtype=float)
        probability = counts / float(settings["denominator"])
        lower = np.asarray(settings["lower"], dtype=float)
        width = np.asarray(settings["upper"], dtype=float) - lower
        mean = float(settings["mean"])
        sd = float(settings["sd"])
        concentration = float(settings["within_bin_concentration"])
        index = np.arange(len(probability), dtype=float)
        mean_width = np.sum(probability * width)
        r = (mean - np.sum(probability * lower)) / mean_width
        s = index - np.sum(probability * width * index) / mean_width
        # q_j = r + b*s_j preserves the reported mean for every b.
        # E[U_j^2]=(k*q_j^2+q_j)/(k+1) for U_j~Beta(k*q_j,k*(1-q_j)).
        # Equating E[age^2] to mean^2+sd^2 gives one quadratic in b.
        coefficient_a = np.sum(probability * width**2 * concentration * s**2
                               / (concentration + 1.0))
        coefficient_b = np.sum(probability * (
            2.0 * lower * width * s
            + width**2 * (2.0 * concentration * r + 1.0) * s
            / (concentration + 1.0)))
        coefficient_c = np.sum(probability * (
            lower**2 + 2.0 * lower * width * r
            + width**2 * (concentration * r**2 + r)
            / (concentration + 1.0))) - mean**2 - sd**2
        discriminant = coefficient_b**2 - 4.0 * coefficient_a * coefficient_c
        if coefficient_a <= 0.0 or discriminant < 0.0:
            raise ValueError("Incompatible binned age moment equation")
        # Prespecified positive-square-root branch, not a search or optimizer.
        b = (-coefficient_b + np.sqrt(discriminant)) / (2.0 * coefficient_a)
        q = r + b * s
        if np.any(q <= 0.0) or np.any(q >= 1.0):
            raise ValueError("Binned beta shapes are not positive")
        cumulative = np.cumsum(probability)
        cumulative[-1] = 1.0  # Exact exhaustiveness; floating-point accumulation only.
        return {"family": family, "probability": probability,
                "cumulative": cumulative, "lower": lower,
                "width": width, "alpha": concentration * q,
                "beta": concentration * (1.0 - q)}
    if family == "shifted_gamma":
        return {"family": family, "lower": float(settings["lower"]),
                "shape": float(settings["shape"]), "scale": float(settings["scale"])}
    raise ValueError("Unknown age distribution")


def _draw_age(probability, prepared):
    family = prepared["family"]
    if family == "bounded_beta_moments":
        return prepared["lower"] + prepared["width"] * beta_distribution.ppf(
            probability, prepared["alpha"], prepared["beta"])
    if family == "shifted_gamma":
        return prepared["lower"] + gamma_distribution.ppf(
            probability, a=prepared["shape"], scale=prepared["scale"])
    category = np.searchsorted(prepared["cumulative"], probability, side="right")
    previous = np.concatenate(([0.0], prepared["cumulative"][:-1]))
    within = _open_probability((probability - previous[category])
                               / prepared["probability"][category])
    return prepared["lower"][category] + prepared["width"][category] * beta_distribution.ppf(
        within, prepared["alpha"][category], prepared["beta"][category])


def _prepare_bmi(settings):
    if settings["family"] == "lognormal_moments":
        return {"lognormal": _lognormal_parameters(settings["mean"], settings["sd"])}
    weights = np.asarray(settings["counts"], dtype=float) / float(settings["denominator"])
    cumulative = np.cumsum(weights)
    cumulative[-1] = 1.0
    return {"weights": weights, "cumulative": cumulative,
            "previous": np.concatenate(([0.0], cumulative[:-1]))}


def _draw_bmi(probability, score, settings, prepared):
    if settings["family"] == "lognormal_moments":
        location, scale = prepared["lognormal"]
        return np.exp(location + scale * score)
    category = np.searchsorted(prepared["cumulative"], probability, side="right")
    within = _open_probability((probability - prepared["previous"][category])
                               / prepared["weights"][category])
    bmi = np.empty(len(probability), dtype=float)
    for j in (0, 1):
        selected = category == j
        component = settings["components"][j]
        bmi[selected] = float(component["lower"]) + (
            float(component["upper"]) - float(component["lower"])
        ) * beta_distribution.ppf(within[selected], component["alpha"], component["beta"])
    selected = category == 2
    component = settings["components"][2]
    bmi[selected] = float(component["lower"]) + gamma_distribution.ppf(
        within[selected], a=component["shape"], scale=component["scale"])
    return bmi


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("This is a whole-cohort generator with no observed individuals")
    parameters = specification["parameters"]
    active_context = parameters["active_context"]
    context = parameters["contexts"][active_context]
    inputs = context["inputs"]
    structure = parameters["structure"]
    n = int(context["n_rows"])
    if n != 5000:
        raise ValueError("The released contract requires exactly 5000 rows")
    if not isinstance(context["population"], str) or not isinstance(context["measurement"], str):
        raise ValueError("Context descriptors must be declared strings")

    # All moment algebra precedes random generation. No generated sample is fitted.
    prepared_age = _prepare_age(inputs["age_distribution"])
    bmi_settings = inputs["bmi_distribution"]
    prepared_bmi = _prepare_bmi(bmi_settings)
    reference = inputs["glucose_reference_moments"]
    glucose_location, glucose_scale = _lognormal_parameters(reference["mean"], reference["sd"])
    measurement = inputs["measurement_process"]
    error_variance = np.log1p(float(measurement["extra_multiplicative_cv"]) ** 2)
    error_scale = np.sqrt(error_variance)
    meal_cv = float(measurement["meal_increment_cv"])
    meal_shape = 1.0 / meal_cv**2
    meal_scale = float(measurement["meal_increment_mean"]) * meal_cv**2

    loadings = structure["copula"]
    age_sex = float(loadings["age_sex"])
    age_residual = np.sqrt(1.0 - age_sex**2)
    bmi_sex = float(loadings["bmi_sex"])
    bmi_age = float(loadings["bmi_age_innovation"])
    bmi_residual = np.sqrt(1.0 - bmi_sex**2 - bmi_age**2)
    glucose_sex = float(loadings["glucose_sex"])
    glucose_age = np.asarray(loadings["glucose_age_innovation_by_sex_M_F"], dtype=float)
    glucose_bmi = np.asarray(loadings["glucose_bmi_innovation_by_sex_M_F"], dtype=float)
    glucose_residual = np.sqrt(1.0 - glucose_sex**2 - glucose_age**2 - glucose_bmi**2)

    rng = np.random.default_rng(seed)
    sex_score, age_innovation, bmi_innovation, glucose_innovation = rng.standard_normal((4, n))
    female = ndtr(sex_score) > (1.0 - float(inputs["female_probability"]))
    sex_index = female.astype(int)
    sex = np.where(female, "F", "M")
    age_score = age_sex * sex_score + age_residual * age_innovation
    bmi_score = bmi_sex * sex_score + bmi_age * age_innovation + bmi_residual * bmi_innovation
    glucose_score = (glucose_sex * sex_score
                     + glucose_age[sex_index] * age_innovation
                     + glucose_bmi[sex_index] * bmi_innovation
                     + glucose_residual[sex_index] * glucose_innovation)
    age = _draw_age(_open_probability(ndtr(age_score)), prepared_age)
    bmi = _draw_bmi(_open_probability(ndtr(bmi_score)), bmi_score, bmi_settings, prepared_bmi)
    reference_glucose = np.exp(glucose_location + glucose_scale * glucose_score)

    baseline_fed_probability = float(measurement["fed_reference_probability"])
    if baseline_fed_probability == 0.0:
        fed_probability = np.zeros(n, dtype=float)
    else:
        feeding = structure["feeding_log_odds_loadings"]
        linear_predictor = (np.log(baseline_fed_probability / (1.0 - baseline_fed_probability))
                            + float(feeding["age_score"]) * age_score
                            + float(feeding["bmi_score"]) * bmi_score
                            + float(feeding["sex_score"]) * sex_score)
        fed_probability = 1.0 / (1.0 + np.exp(-linear_predictor))
    glucose_sum = np.zeros(n, dtype=float)
    repetitions = int(measurement["repetitions"])
    for _ in range(repetitions):
        fed = rng.random(n) < fed_probability
        meal = rng.gamma(shape=meal_shape, scale=meal_scale, size=n)
        extra_error = np.exp(-error_variance / 2.0 + error_scale * rng.standard_normal(n))
        glucose_sum += (reference_glucose + fed * meal) * extra_error
    glucose = float(measurement["calibration_scale"]) * glucose_sum / repetitions

    numeric = np.column_stack((age, bmi, glucose))
    if not np.isfinite(numeric).all() or np.any(bmi <= 0.0) or np.any(glucose <= 0.0):
        raise ValueError("Invalid whole cohort; no row filtering or repair is permitted")
    age_rule = inputs["age_distribution"]
    lower = float(age_rule["eligibility_lower"])
    upper = age_rule["eligibility_upper"]
    if np.any(age < lower) or (upper is not None and np.any(age > float(upper))):
        raise ValueError("Invalid context age support; no row filtering is permitted")
    ids = [f"{active_context}:{seed}:{i + 1:05d}" for i in range(n)]
    return pd.DataFrame({"id": ids, "age": age, "sex": sex, "bmi": bmi, "glucose": glucose},
                        columns=["id", "age", "sex", "bmi", "glucose"])
