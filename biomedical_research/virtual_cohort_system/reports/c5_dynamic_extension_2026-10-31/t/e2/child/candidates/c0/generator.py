"""Append x3 conditionally while preserving every supplied old cell."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    p = spec["parameters"]
    if not isinstance(observed, pd.DataFrame):
        raise ValueError("Enrichment requires a pandas observed table")
    if list(observed.columns) != p["preserved_columns"] or len(observed) != p["n_rows"]:
        raise ValueError("Observed shape or column order differs from specification")
    if p["distribution"] != "gaussian_conditional" or p["random_generator"] != "PCG64":
        raise ValueError("Unsupported distribution or random generator")
    fixed_values = observed.loc[:, p["conditioning_variables"]].to_numpy(dtype=float)
    center = np.asarray(p["conditioning_mean"], dtype=float)
    slopes = np.asarray(p["conditional_slopes"], dtype=float)
    conditional_mean = p["outcome_mean"] + (fixed_values - center) @ slopes
    residual_variance = p["conditional_residual_variance"]
    if residual_variance <= 0:
        raise ValueError("Conditional residual variance must be positive")
    rng = np.random.Generator(np.random.PCG64(seed))
    residual = np.sqrt(residual_variance) * rng.standard_normal(p["n_rows"])
    output = observed.copy(deep=True)
    output[p["generated_variable"]] = conditional_mean + residual
    return output
