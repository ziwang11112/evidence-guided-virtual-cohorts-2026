"""Whole-cohort Gaussian copula; execution is reserved for the controller.

Scientific settings and marginal transformations are specified in model_spec.
There is no participant input, parameter fitting, rejection, or source replay.
"""
import math

import numpy as np
import pandas as pd


def _normal_cdf(z):
    flat = np.asarray(z, dtype=float).ravel()
    result = np.fromiter(
        (0.5 * math.erfc(-float(value) / math.sqrt(2.0)) for value in flat),
        dtype=float, count=flat.size,
    )
    return result.reshape(np.shape(z))


def _marginal(z, definition):
    family = definition["family"]
    if family == "lognormal":
        return np.exp(definition["log_mean"] + definition["log_sd"] * z)
    if family == "uniform":
        return definition["low"] + (definition["high"] - definition["low"]) * _normal_cdf(z)
    if family == "discrete_uniform":
        count = definition["high"] - definition["low"] + 1
        # The final-bin guard only handles CDF rounding to exactly 1.0.
        bins = np.minimum(count - 1, np.floor(count * _normal_cdf(z))).astype(np.int64)
        return definition["low"] + bins
    raise ValueError("Unrecognized marginal family")


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort construction requires observed=None")
    parameters = spec["parameters"]
    law = parameters["target_law"]
    n = parameters["n_rows"]
    rng = np.random.default_rng(seed)
    correlation = np.asarray(law["latent_correlation"], dtype=float)
    cholesky = np.linalg.cholesky(correlation)
    z = rng.standard_normal((n, len(law["variables"]))) @ cholesky.T
    values = {
        name: _marginal(z[:, index], law["marginals"][name])
        for index, name in enumerate(law["variables"])
    }
    female = rng.binomial(1, law["female_probability"], size=n).astype(np.int64)
    frame = pd.DataFrame({
        "row_id": [parameters["row_prefix"] + str(index + 1) for index in range(n)],
        "age": values["age"].astype(np.int64),
        "female": female,
        "bmi": values["bmi"],
        "glucose": values["glucose"],
        "hba1c": values["hba1c"],
    })
    # A numerical failure is explicit; no rows are dropped or regenerated.
    if not np.isfinite(frame[["age", "female", "bmi", "glucose", "hba1c"]].to_numpy()).all():
        raise FloatingPointError("Nonfinite arithmetic; no clipping or resampling allowed")
    if not (frame[["bmi", "glucose", "hba1c"]] > 0).to_numpy().all():
        raise FloatingPointError("Nonpositive numerical output")
    return frame
