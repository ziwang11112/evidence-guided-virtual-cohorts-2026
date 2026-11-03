"""Whole-cohort conditional model; scientific values come only from spec.

This module is submitted for controller execution only. It performs no I/O.
"""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort model requires observed=None")
    p = spec["parameters"]
    if p["age_law"] != "discrete_uniform_within_each_band":
        raise ValueError("Unsupported age law")
    if p["dependence_law"] != "mutually_independent_biomarkers_and_demographics":
        raise ValueError("Unsupported dependence law")
    rng = np.random.default_rng(seed)
    d = p["design"]
    age_parts, sex_parts = [], []
    for sex in d["female_values"]:
        for lower, upper in d["age_bands"]:
            age_parts.append(rng.integers(lower, upper + 1, size=d["per_cell"]))
            sex_parts.append(np.full(d["per_cell"], sex, dtype=np.int64))
    age = np.concatenate(age_parts)
    female = np.concatenate(sex_parts)
    n = d["n_rows"]
    if len(age) != n:
        raise ValueError("Design row count does not match cell quotas")
    out = {"row_id": [f"fictional_{i + 1:06d}" for i in range(n)], "age": age, "female": female}
    for name in ("bmi", "glucose", "hba1c"):
        margin = p[name]
        mean, sd = margin["mean"], margin["sd"]
        if margin["family"] == "gamma":
            shape = (mean / sd) ** 2
            scale = sd ** 2 / mean
            values = rng.gamma(shape, scale, size=n)
            valid = np.isfinite(values) & (values > 0)
        elif margin["family"] == "scaled_beta":
            lower, upper = margin["lower"], margin["upper"]
            width = upper - lower
            proportion = (mean - lower) / width
            concentration = proportion * (1 - proportion) / (sd / width) ** 2 - 1
            alpha = proportion * concentration
            beta = (1 - proportion) * concentration
            if alpha <= 0 or beta <= 0:
                raise ValueError("Infeasible beta moment parameters")
            values = lower + width * rng.beta(alpha, beta, size=n)
            valid = np.isfinite(values) & (values > lower) & (values < upper)
        else:
            raise ValueError("Unsupported marginal family")
        if not np.all(valid):
            raise ValueError("Floating-point draw outside open support; no clipping performed")
        out[name] = values
    frame = pd.DataFrame(out, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
    return frame.iloc[rng.permutation(n)].reset_index(drop=True)
