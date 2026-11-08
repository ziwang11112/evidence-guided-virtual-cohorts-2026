"""Whole-cohort Gaussian realization of the reconciled P0 moments."""
import operator

import numpy as np
import pandas as pd


def generate(n, rng, spec):
    """Generate independent P0 rows using only the supplied random generator."""
    if isinstance(n, (bool, np.bool_)):
        raise TypeError("n must be an integer row count")
    n = operator.index(n)
    if n < 0:
        raise ValueError("n must be nonnegative")
    columns = list(spec["columns"])
    if columns != ["Z", "X1", "X2", "Y"]:
        raise ValueError("Unexpected column order")
    mean = np.asarray(spec["predictor_mean"], dtype=float)
    covariance = np.asarray(spec["predictor_covariance"], dtype=float)
    coefficients = np.asarray(spec["outcome_coefficients"], dtype=float)
    dimension = len(columns) - 1
    if mean.shape != (dimension,) or coefficients.shape != (dimension,):
        raise ValueError("Unexpected parameter dimensions")
    if covariance.shape != (dimension, dimension):
        raise ValueError("Unexpected covariance dimensions")
    residual_variance = float(spec["outcome_residual_variance"])
    if not np.isfinite(residual_variance) or residual_variance < 0:
        raise ValueError("Residual variance must be finite and nonnegative")
    factor = np.linalg.cholesky(covariance)
    predictors = rng.standard_normal((n, dimension)) @ factor.T + mean
    residual = rng.standard_normal(n) * np.sqrt(residual_variance)
    outcome = float(spec["outcome_intercept"]) + predictors @ coefficients + residual
    return pd.DataFrame(np.column_stack((predictors, outcome)), columns=columns)
