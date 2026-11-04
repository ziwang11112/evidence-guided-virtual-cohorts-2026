"""C02 reviewed whole-cohort law; invoked only by the isolated adapter."""

import math

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort program requires observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)

    # Latent order is age, log BMI, and log shifted glucose.
    correlation = np.asarray(p["latent_correlation"], dtype=float)
    latent = rng.standard_normal((n, 3)) @ np.linalg.cholesky(correlation).T
    normal_cdf = np.fromiter(
        (0.5 * math.erfc(-float(z) / math.sqrt(2.0)) for z in latent[:, 0]),
        dtype=float,
        count=n,
    )
    age_settings = p["age"]
    category_count = age_settings["maximum"] - age_settings["minimum"] + 1
    # Guard numerical CDF endpoints only; this is not clinical clipping.
    category = np.floor(category_count * normal_cdf).astype(np.int64)
    category = np.minimum(np.maximum(category, 0), category_count - 1)
    age = age_settings["minimum"] + category
    female = rng.binomial(1, p["female_probability"], size=n).astype(np.int64)

    b = p["bmi"]
    bmi = b["mean"] * np.exp(b["log_sd"] * latent[:, 1] - 0.5 * b["log_sd"] ** 2)
    g = p["glucose"]
    glucose = g["shift"] + (g["mean"] - g["shift"]) * np.exp(
        g["log_sd"] * latent[:, 2] - 0.5 * g["log_sd"] ** 2
    )
    h = p["hba1c"]
    residual = rng.uniform(-p["residual_half_width"], p["residual_half_width"], size=n)
    hba1c = (
        h["mean"]
        + p["coefficient_glucose"] * (glucose - g["mean"])
        + p["coefficient_age"] * (age - age_settings["mean"])
        + p["coefficient_female"] * (female - p["female_probability"])
        + p["coefficient_direct_bmi"] * (bmi - b["mean"])
        + residual
    )
    frame = pd.DataFrame({
        "row_id": [f"{p['row_id_prefix']}-{seed}-{i + 1:05d}" for i in range(n)],
        "age": age,
        "female": female,
        "bmi": bmi,
        "glucose": glucose,
        "hba1c": hba1c,
    })
    return frame[p["output_columns"]]
