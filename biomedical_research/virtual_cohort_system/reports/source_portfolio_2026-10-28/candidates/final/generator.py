"""Frozen scientific settings reside in model_spec.json. No I/O or target fitting."""
import numpy as np

def generate(observed, spec, seed):
    p = spec["parameters"]
    c = p["column_map"]
    result = observed.copy(deep=True)
    male = observed[c["sex"]].to_numpy() == c["male_code"]
    bmi = observed[c["bmi"]].to_numpy(dtype=float)
    ar = p["age_response"]
    age = np.clip(observed[c["age"]].to_numpy(dtype=float), ar["minimum"], ar["maximum"])
    br = p["bmi_response"]
    excess = np.maximum(bmi - br["bend_at"], 0.0)
    effective_bmi = np.minimum(bmi, br["bend_at"]) + br["bend_scale"] * np.log1p(excess / br["bend_scale"])
    anchor = np.where(male, p["mean_anchor"]["male"], p["mean_anchor"]["female"])
    bmi_ref = np.where(male, p["bmi_reference"]["male"], p["bmi_reference"]["female"])
    female_age = ar["female_amplitude"] * (1.0 / (1.0 + np.exp(-(age-ar["female_midpoint"])/ar["female_width"])) - ar["female_center"])
    male_age = ar["male_slope"] * (age-ar["male_reference"])
    bmi_slope = np.where(male, br["slope_male"], br["slope_female"])
    linear_mean = anchor + bmi_slope * (effective_bmi-bmi_ref) + np.where(male, male_age, female_age)
    pos = p["positive_mean"]
    conditional_mean = pos["floor"] + pos["softness"] * np.logaddexp(0.0, (linear_mean-pos["floor"])/pos["softness"])
    sigma = np.where(male, p["residual_log_sd"]["male"], p["residual_log_sd"]["female"])
    z = np.random.default_rng(seed).standard_normal(len(observed))
    result[c["outcome"]] = conditional_mean * np.exp(sigma*z - 0.5*sigma*sigma)
    return result
