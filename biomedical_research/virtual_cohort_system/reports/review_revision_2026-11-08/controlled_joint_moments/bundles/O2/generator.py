"""Whole-cohort Gaussian construction from the supplied population moments."""

import numpy as np
import pandas as pd


def generate(n, rng, spec):
    """Return n iid rows; rng is the controller-supplied NumPy Generator."""
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer")

    predictors = spec["predictor_columns"]
    means = np.asarray(spec["predictor_means"], dtype=float)
    covariance = np.asarray(spec["predictor_covariance"], dtype=float)
    coefficients = np.asarray(spec["outcome_coefficients"], dtype=float)
    factor = np.linalg.cholesky(covariance)
    x = rng.standard_normal((n, len(predictors))) @ factor.T + means
    error = rng.standard_normal(n) * np.sqrt(spec["outcome_residual_variance"])
    y = spec["outcome_intercept"] + x @ coefficients + error
    return pd.DataFrame(np.column_stack((x, y)), columns=spec["columns"])
