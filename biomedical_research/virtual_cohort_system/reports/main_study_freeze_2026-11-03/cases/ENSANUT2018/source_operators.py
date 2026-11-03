"""Analytic source projection operator; no files, sampling or target calibration.

An author must independently derive the moments of its declared SOURCE law.
This helper verifies mathematical admissibility and computes the corresponding
population linear projection. It cannot establish that the supplied moments
belong to the submitted generator, reconstruct the original survey estimator,
or identify unreported covariance/transport assumptions.
"""
from __future__ import annotations

import numpy as np

OPERATIONS = {
    "J_T2_bmi_slope_task_derived": ("lifelines", "hba1c", "bmi", ("age", "female")),
    "J_T2_glucose_slope_task_derived": ("lifelines", "hba1c", "glucose", ("age", "female")),
    "P_NHANES_age_slope": ("pani", "hba1c", "age", ("female", "bmi", "glucose")),
}


def source_projection(operation_id, *, source_context, variables, mean, covariance):
    """Return the slope of one separately specified source-population projection.

    Means and covariances use age years, female0/1, BMI kg/m^2, glucose mg/dL,
    HbA1c percentage points. Source selection must already be represented in
    these moments; target quota-weighted moments cannot substitute. Pani is a
    qualified population projection, not exact complex-survey reconstruction.
    """
    if operation_id not in OPERATIONS:
        raise ValueError("unknown admitted relational operation")
    expected_context, outcome, predictor, adjustment = OPERATIONS[operation_id]
    if source_context != expected_context:
        raise ValueError("source context differs from the operation")
    variables = tuple(variables)
    if len(variables) != len(set(variables)):
        raise ValueError("duplicate moment variables")
    required = (outcome, predictor, *adjustment)
    if not set(required) <= set(variables):
        raise ValueError("missing projection variable")
    mu = np.asarray(mean, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    n = len(variables)
    if mu.shape != (n,) or cov.shape != (n, n):
        raise ValueError("moment dimensions differ")
    if not (np.isfinite(mu).all() and np.isfinite(cov).all()):
        raise ValueError("finite moments required")
    scale = max(1.0, float(np.max(np.abs(cov))))
    tol = 100 * np.finfo(float).eps * max(1, n) * scale
    if not np.allclose(cov, cov.T, rtol=0, atol=tol):
        raise ValueError("covariance must be symmetric")
    cov = (cov + cov.T) / 2
    if np.linalg.eigvalsh(cov).min() < -tol:
        raise ValueError("covariance must be positive semidefinite")
    xs = [variables.index(x) for x in (predictor, *adjustment)]
    yi = variables.index(outcome)
    xx = cov[np.ix_(xs, xs)]
    if np.linalg.eigvalsh(xx).min() <= tol:
        raise ValueError("predictor covariance is singular or ill-conditioned")
    beta = np.linalg.solve(xx, cov[xs, yi])
    return {
        "operation_id": operation_id,
        "source_context": source_context,
        "status": "qualified_analytic_population_projection",
        "value": float(beta[0]),
        "intercept": float(mu[yi] - mu[xs] @ beta),
        "coefficients": dict(zip((predictor, *adjustment), map(float, beta))),
        "assumption_warning": "Caller-supplied source moments require an independently checked derivation from the frozen generator; no source survey or transport certification.",
    }
