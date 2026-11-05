"""Approved L02 scenario; execution only through the controller adapter."""
import math
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = specification["parameters"]
    n = int(p["row_count"])
    rng = np.random.default_rng(seed)
    sex = np.where(rng.random(n) < p["female_probability"], "F", "M")
    correlation = np.asarray(p["latent_correlation"], dtype=float)
    factor = np.linalg.cholesky(correlation)
    latent_order = p["latent_order"]
    z = rng.standard_normal((n, len(latent_order))) @ factor.T
    age_z = z[:, latent_order.index("age")]
    u = np.fromiter((0.5 * math.erfc(-float(v) / math.sqrt(2.0)) for v in age_z), dtype=float, count=n)
    ages = np.empty(n, dtype=float)
    for label in ("M", "F"):
        mask = sex == label
        ages[mask] = np.interp(u[mask], p["age_probabilities"], p["age_knots"][label])
    result = {
        "id": [p["id_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": ages,
        "sex": sex,
    }
    for variable, by_sex in p["margins"].items():
        values = np.empty(n, dtype=float)
        index = latent_order.index(variable)
        for label in ("M", "F"):
            mask = sex == label
            settings = by_sex[label]
            values[mask] = settings["geometric_mean"] * np.exp(settings["log_sd"] * z[mask, index])
        result[variable] = values
    return pd.DataFrame(result, columns=p["output_columns"])
