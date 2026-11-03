"""Whole-cohort generator; execution is reserved for the isolated controller."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    n = p["n_rows"]
    rng = np.random.default_rng(seed)
    data = {
        "row_id": [p["row_id_prefix"] + str(i + 1).zfill(4) for i in range(n)],
        "age": rng.integers(p["age_min"], p["age_max"] + 1, size=n),
        "female": rng.binomial(1, p["female_probability"], size=n),
    }
    shared = rng.standard_normal(n)
    for name in p["continuous_order"]:
        marginal = p["marginals"][name]
        mean = marginal["mean"]
        sd = marginal["individual_sd"]
        loading = marginal["factor_loading"]
        sigma2 = np.log1p((sd / mean) ** 2)
        mu = np.log(mean) - sigma2 / 2.0
        z = loading * shared + np.sqrt(1.0 - loading ** 2) * rng.standard_normal(n)
        with np.errstate(over="raise", under="raise", invalid="raise"):
            data[name] = np.exp(mu + np.sqrt(sigma2) * z)
    return pd.DataFrame(data, columns=p["output_columns"])
