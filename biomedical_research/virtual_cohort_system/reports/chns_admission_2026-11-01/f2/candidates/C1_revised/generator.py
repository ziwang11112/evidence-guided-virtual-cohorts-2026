"""C1 initial conditional lognormal whole-cohort model.

Scientific settings and distribution/dependence assumptions are in model_spec.json.
This module performs no I/O and is not executed during candidate authoring.
"""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Return complete fictional rows using only the specification and seed."""
    if observed is not None:
        raise ValueError("This model implements whole_cohort mode with observed=None")
    p = spec["parameters"]
    if p["model_structure"]["family"] != "conditional_lognormal_v1":
        raise ValueError("Unsupported model family")
    n = p["n_rows"]
    rng = np.random.Generator(np.random.PCG64(seed))
    age = rng.integers(p["age_minimum"], p["age_maximum"] + 1, size=n)
    female = rng.binomial(1, p["female_probability"], size=n)
    female_centered = female - p["female_probability"]
    age_centered = age - p["age_reference"]
    bmi = p["bmi_median"] * np.exp(
        p["bmi_log_sd"] * rng.standard_normal(n)
        + p["bmi_female_log_shift"] * female_centered
    )
    bmi_centered = bmi - p["bmi_reference"]
    glucose = p["glucose_median_reference"] * np.exp(
        p["glucose_log_age_coefficient"] * age_centered
        + p["glucose_log_bmi_coefficient"] * bmi_centered
        + p["glucose_female_log_shift"] * female_centered
        + p["glucose_residual_log_sd"] * rng.standard_normal(n)
    )
    hba1c = p["hba1c_median_reference"] * np.exp(
        p["hba1c_log_age_coefficient"] * age_centered
        + p["hba1c_log_bmi_coefficient"] * bmi_centered
        + p["hba1c_female_log_shift"] * female_centered
        + p["hba1c_glucose_elasticity"] * np.log(
            glucose / p["glucose_median_reference"]
        )
        + p["hba1c_residual_log_sd"] * rng.standard_normal(n)
    )
    continuous = np.column_stack((bmi, glucose, hba1c))
    if not np.isfinite(continuous).all() or not (continuous > 0).all():
        raise ValueError("Nonfinite or nonpositive model output; no clipping is permitted")
    rows = pd.DataFrame({
        "row_id": [p["row_id_prefix"] + str(index + 1) for index in range(n)],
        "age": age,
        "female": female,
        "bmi": bmi,
        "glucose": glucose,
        "hba1c": hba1c,
    })
    return rows.loc[:, p["column_order"]]
