"""Fictional Gaussian whole-cohort generator; no clinical interpretation."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Draw i.i.d. rows from the fully declared Gaussian scenario."""
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    if p["joint_family"] != "multivariate_gaussian":
        raise ValueError("Unsupported declared joint family")
    if p["sampling_design"] != "independent_identically_distributed":
        raise ValueError("Unsupported declared sampling design")
    variables = p["variables"]
    n = p["n_rows"]
    means = np.asarray(p["means"], dtype=float)
    sds = np.asarray(p["standard_deviations"], dtype=float)
    correlation = np.asarray(p["correlation_matrix"], dtype=float)
    covariance = correlation * np.outer(sds, sds)
    factor = np.linalg.cholesky(covariance)
    rng = np.random.default_rng(seed)
    independent = rng.standard_normal((n, len(variables)))
    values = independent @ factor.T + means
    frame = pd.DataFrame(values, columns=variables)
    identifier = p["identifier"]
    frame.insert(0, identifier["column"],
                 [identifier["prefix"] + str(i + 1) for i in range(n)])
    return frame
