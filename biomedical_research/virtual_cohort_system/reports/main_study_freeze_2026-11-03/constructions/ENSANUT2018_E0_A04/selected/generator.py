"""Independent marginal completion, conditional on the specified eligibility design.
Only the controller may execute this program. Scientific constants live in spec.
"""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    design = p["design"]
    rng = np.random.default_rng(seed)
    ages, sexes = [], []
    for female in design["female_values"]:
        for lower, upper in design["age_bands"]:
            ages.append(rng.integers(lower, upper + 1, size=design["rows_per_cell"]))
            sexes.append(np.full(design["rows_per_cell"], female, dtype=np.int64))
    age = np.concatenate(ages)
    female = np.concatenate(sexes)
    n = len(age)
    if n != design["n_rows"]:
        raise ValueError("Inconsistent design row count")
    values = {}
    for name in ("bmi", "hba1c"):
        marginal = p[name]
        shape = (marginal["mean"] / marginal["sd"]) ** 2
        scale = marginal["sd"] ** 2 / marginal["mean"]
        values[name] = rng.gamma(shape, scale, size=n)
    glucose = p["glucose"]
    width = glucose["upper"] - glucose["lower"]
    fraction = (glucose["mean"] - glucose["lower"]) / width
    concentration = fraction * (1 - fraction) / (glucose["sd"] / width) ** 2 - 1
    alpha = fraction * concentration
    beta = (1 - fraction) * concentration
    values["glucose"] = glucose["lower"] + width * rng.beta(alpha, beta, size=n)
    for name, vector in values.items():
        if not np.all(np.isfinite(vector)) or not np.all(vector > 0):
            raise FloatingPointError("Numerical support violation: " + name)
    if not np.all(values["glucose"] < glucose["upper"]):
        raise FloatingPointError("Numerical strict glucose upper-bound violation")
    order = rng.permutation(n)
    frame = pd.DataFrame({
        "row_id": [design["row_id_prefix"] + str(index + 1).zfill(4) for index in range(n)],
        "age": age[order],
        "female": female[order],
        "bmi": values["bmi"][order],
        "glucose": values["glucose"][order],
        "hba1c": values["hba1c"][order],
    })
    return frame[p["output_columns"]]
