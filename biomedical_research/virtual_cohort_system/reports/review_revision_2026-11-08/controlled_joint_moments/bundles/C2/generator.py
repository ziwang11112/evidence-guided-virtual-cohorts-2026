"""Stochastic whole-cohort law for the artificial P0 population.

The specification fixes scientific moments and coefficients. Rows are independent
samples; no finite-sample centering or rescaling is imposed.
"""
import numpy as np
import pandas as pd


def generate(n, rng, spec):
    """Return n iid rows with columns Z, X1, X2, Y using the supplied RNG."""
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    predictor_columns = spec["predictor_columns"]
    columns = spec["columns"]
    mean = np.asarray(spec["predictor_mean"], dtype=float)
    covariance = np.asarray(spec["predictor_covariance"], dtype=float)
    coefficients = np.asarray(spec["outcome_coefficients"], dtype=float)
    residual_variance = float(spec["outcome_residual_variance"])
    dimension = len(predictor_columns)
    if mean.shape != (dimension,) or coefficients.shape != (dimension,):
        raise ValueError("Invalid predictor parameter dimensions")
    if covariance.shape != (dimension, dimension) or residual_variance < 0:
        raise ValueError("Invalid covariance or residual variance")
    factor = np.linalg.cholesky(covariance)
    innovations = rng.standard_normal(size=(n, dimension + 1))
    predictors = mean + innovations[:, :dimension] @ factor.T
    outcome = (float(spec["outcome_intercept"])
               + predictors @ coefficients
               + np.sqrt(residual_variance) * innovations[:, dimension])
    return pd.DataFrame(np.column_stack((predictors, outcome)), columns=columns)
