"""Portable conditional DXA body-fat construction; no context/identifier lookup."""
import numpy as np


def generate(observed, spec, seed):
    p = spec["parameters"]
    output = observed.copy(deep=True)
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    male = observed["male"].to_numpy(dtype=float)
    asian = observed["asian"].to_numpy(dtype=float)
    g = p["gallagher_coefficients"]
    t = p["thai_coefficients"]
    gallagher_location = (g["intercept"] + g["inv_bmi"] / bmi + g["male"] * male
        + g["age"] * age + g["asian_inv_bmi"] * asian / bmi
        + g["asian_age"] * asian * age + g["male_inv_bmi"] * male / bmi
        + g["male_age"] * male * age)
    thai_location = t["intercept"] + t["bmi"] * bmi + t["age"] * age + t["male"] * male
    weight = p["asian_blend"] * asian
    location = ((1.0 - weight) * gallagher_location + weight * thai_location
        + p["level_shift"] + p["male_shift"] * male)
    mean = np.clip(location, p["mean_floor"], p["mean_ceiling"])
    sd = p["residual_base_sd"] * p["residual_scale"] * np.where(male == 1, 1.0, p["female_sd_ratio"])
    variance = np.minimum(sd * sd, p["variance_fraction_cap"] * mean * (100.0 - mean))
    concentration = mean * (100.0 - mean) / variance - 1.0
    alpha = (mean / 100.0) * concentration
    beta = (1.0 - mean / 100.0) * concentration
    output["bodyfat"] = 100.0 * np.random.default_rng(seed).beta(alpha, beta)
    return output
