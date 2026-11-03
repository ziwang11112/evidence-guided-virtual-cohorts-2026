"""Fictional selected whole cohort. Scientific settings are supplied in spec."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = spec["parameters"]
    if p["dependence"] != "independent_product":
        raise ValueError("Unsupported dependence law")
    if p["age_law"] != "discrete_uniform_within_fixed_cells":
        raise ValueError("Unsupported age law")
    if p["endpoint_policy"] != "nearest_float_strictly_inside":
        raise ValueError("Unsupported endpoint policy")
    d = p["design"]
    rng = np.random.default_rng(seed)
    count = d["rows_per_cell"]
    ages, sexes = [], []
    for sex in d["sex_values"]:
        for lower, upper in d["age_bands"]:
            ages.append(rng.integers(lower, upper + 1, size=count))
            sexes.append(np.full(count, sex, dtype=int))
    age = np.concatenate(ages)
    female = np.concatenate(sexes)
    n = len(age)
    if n != d["n_rows"]:
        raise ValueError("Demographic design does not match row count")

    def positive_marginal(settings):
        if settings["family"] != "lognormal":
            raise ValueError("Unsupported positive marginal")
        mean, sd = settings["arithmetic_mean"], settings["individual_sd"]
        sigma2 = np.log1p((sd / mean) ** 2)
        mu = np.log(mean) - sigma2 / 2
        return rng.lognormal(mean=mu, sigma=np.sqrt(sigma2), size=n)

    bmi = positive_marginal(p["bmi"])
    g = p["glucose"]
    if g["family"] != "scaled_beta":
        raise ValueError("Unsupported glucose marginal")
    lower, upper = g["lower"], g["upper"]
    width = upper - lower
    prob = (g["arithmetic_mean"] - lower) / width
    variance = (g["individual_sd"] / width) ** 2
    concentration = prob * (1 - prob) / variance - 1
    glucose = lower + width * rng.beta(prob * concentration, (1 - prob) * concentration, size=n)
    glucose = np.clip(glucose, np.nextafter(lower, upper), np.nextafter(upper, lower))
    hba1c = positive_marginal(p["hba1c"])
    row_ids = [d["row_id_prefix"] + str(index + 1) for index in range(n)]
    frame = pd.DataFrame({"row_id":row_ids, "age":age, "female":female,
                          "bmi":bmi, "glucose":glucose, "hba1c":hba1c})
    return frame.loc[:, d["columns"]]
