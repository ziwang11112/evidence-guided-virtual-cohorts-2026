"""Whole-cohort Gaussian completion of the exact P0 population moments."""
import numpy as np
import pandas as pd


def generate(n, rng, spec):
    """Return iid rows in Z, X1, X2, Y order using the supplied RNG only."""
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    columns = list(spec["columns"])
    if columns != ["Z", "X1", "X2", "Y"]:
        raise ValueError("Expected columns Z, X1, X2, Y in that order")
    predictor_count = len(columns) - 1
    mean = np.asarray(spec["predictor_mean"], dtype=float)
    covariance = np.asarray(spec["predictor_covariance"], dtype=float)
    coefficients = np.asarray(spec["outcome_coefficients"], dtype=float)
    intercept = float(spec["outcome_intercept"])
    residual_sd = float(spec["residual_sd"])
    if mean.shape != (predictor_count,) or coefficients.shape != (predictor_count,):
        raise ValueError("Predictor mean and coefficient shapes must match the schema")
    if covariance.shape != (predictor_count, predictor_count):
        raise ValueError("Predictor covariance shape must match the schema")
    if not all(np.isfinite(a).all() for a in (mean, covariance, coefficients)):
        raise ValueError("Model arrays must contain finite numeric values")
    if not np.isfinite(intercept) or not np.isfinite(residual_sd) or residual_sd <= 0:
        raise ValueError("Intercept must be finite and residual SD positive")
    if not np.array_equal(covariance, covariance.T):
        raise ValueError("Predictor covariance must be symmetric")
    factor = np.linalg.cholesky(covariance)
    innovations = rng.standard_normal(size=(int(n), len(columns)))
    predictors = mean + innovations[:, :predictor_count] @ factor.T
    outcome = intercept + predictors @ coefficients + residual_sd * innovations[:, predictor_count]
    return pd.DataFrame(np.column_stack((predictors, outcome)), columns=columns)
