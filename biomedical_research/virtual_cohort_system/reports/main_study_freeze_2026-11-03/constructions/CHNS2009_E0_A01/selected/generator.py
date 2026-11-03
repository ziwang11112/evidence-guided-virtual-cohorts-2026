"""An all-generated, assumption-dependent product-marginal cohort.

The scientific constants are in model_spec.json. Importing is unnecessary for
validation. Only the coordinator's isolated adapter may call generate.
"""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = spec["parameters"]
    if (p["continuous_family"] != "independent_lognormal"
            or p["age_family"] != "discrete_uniform_inclusive"
            or p["female_family"] != "bernoulli"
            or p["joint_law"] != "product_of_five_marginals"):
        raise ValueError("Unsupported declared probability law")
    n = p["n_rows"]
    rng = np.random.default_rng(seed)
    values = {
        "row_id": [p["row_id_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": rng.integers(p["age_min"], p["age_max"] + 1, size=n),
        "female": rng.binomial(1, p["female_probability"], size=n),
    }
    for column in ("bmi", "glucose", "hba1c"):
        margin = p["marginals"][column]
        mean = margin["mean"]
        sd = margin["individual_sd"]
        if mean <= 0 or sd <= 0:
            raise ValueError("Lognormal moments require positive mean and SD")
        sigma2 = np.log1p((sd / mean) ** 2)
        mu = np.log(mean) - sigma2 / 2
        draw = rng.lognormal(mu, np.sqrt(sigma2), size=n)
        if not np.isfinite(draw).all() or not (draw > 0).all():
            raise ValueError("Nonfinite/nonpositive numerical output; no clipping or redraw")
        values[column] = draw
    return pd.DataFrame(values, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
