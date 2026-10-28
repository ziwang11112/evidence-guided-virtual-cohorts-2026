"""One source-only repeated-measures population model.

Marginal moments are reconstruction inputs. All copula and attendance
parameters below are working assumptions, not estimates from the packet.
There is no filesystem access, global RNG mutation, or evidence mutation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, special, stats


_VISITS = (0, 3, 6, 9, 12)
_OUTCOMES = ("weight_kg", "pfs", "gng", "dd100", "dd1000")
_COLUMNS = ("person_id", "month") + _OUTCOMES


def _weight_parameters(mean, sd, upper=None):
    """Lognormal moment parameters, accounting for enrollment truncation."""
    sigma = np.sqrt(np.log1p((sd / mean) ** 2))
    mu = np.log(mean) - 0.5 * sigma ** 2
    if upper is None:
        return mu, sigma, 1.0

    log_upper = np.log(upper)

    def residual(theta):
        loc, scale = theta[0], np.exp(theta[1])
        log_den = special.log_ndtr((log_upper - loc) / scale)
        moments = [np.exp(k * loc + 0.5 * k * k * scale * scale
                          + special.log_ndtr((log_upper - loc - k * scale * scale) / scale)
                          - log_den) for k in (1, 2)]
        variance = max(moments[1] - moments[0] ** 2, 1e-12)
        return [(moments[0] - mean) / mean,
                (np.sqrt(variance) - sd) / sd]

    result = optimize.least_squares(residual, [mu, np.log(sigma)],
                                    xtol=1e-12, ftol=1e-12, gtol=1e-12)
    if not result.success or np.max(np.abs(residual(result.x))) > 1e-7:
        raise ValueError("Could not match baseline truncated lognormal moments")
    mu, sigma = result.x[0], np.exp(result.x[1])
    return mu, sigma, special.ndtr((log_upper - mu) / sigma)


def _marginal_quantiles(variable, month, uniform, mean, sd):
    if variable == "weight_kg":
        upper = 180.0 if month == 0 else None
        mu, sigma, truncation_cdf = _weight_parameters(mean, sd, upper)
        values = np.exp(mu + sigma * special.ndtri(uniform * truncation_cdf))
        return np.minimum(values, upper) if upper is not None else values
    if variable == "gng":
        # Overdispersed errors. Conditioning on the known task maximum
        # enforces support; moment change from this far-tail truncation is tiny.
        variance = sd * sd
        if variance <= mean:
            cdf_upper = stats.poisson.cdf(512, mean)
            return stats.poisson.ppf(uniform * cdf_upper, mean)
        shape = mean * mean / (variance - mean)
        success = shape / (shape + mean)
        cdf_upper = stats.nbinom.cdf(512, shape, success)
        return stats.nbinom.ppf(uniform * cdf_upper, shape, success)
    lower, upper = (1.0, 5.0) if variable == "pfs" else (0.0, 1.0)
    scaled_mean = (mean - lower) / (upper - lower)
    scaled_variance = (sd / (upper - lower)) ** 2
    precision = scaled_mean * (1.0 - scaled_mean) / scaled_variance - 1.0
    if not 0.0 < scaled_mean < 1.0 or precision <= 0.0:
        raise ValueError("Marginal moments incompatible with beta support")
    return lower + (upper - lower) * stats.beta.ppf(
        uniform, scaled_mean * precision, (1.0 - scaled_mean) * precision)


def generate(n, seed, evidence, context="target"):
    """Return n new persons at five visits, with exact scaled source counts."""
    if context != "target":
        raise ValueError("Only the committed target scenario is declared")
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer number of persons")
    rng = np.random.default_rng(seed)
    source_n = int(evidence["n_persons"])
    summaries = {(int(m["month"]), m["variable"]): m
                 for m in evidence["marginal_summaries"]}
    if set(summaries) != {(month, variable) for month in _VISITS for variable in _OUTCOMES}:
        raise ValueError("Require the declared five-visit marginal packet")

    # Separate domains are uncoupled in this selected completion of unknown
    # covariance. Both discounting amounts share a stable discounting factor.
    person_factors = rng.standard_normal((n, len(_OUTCOMES)))
    discounting_factor = rng.standard_normal(n)
    residual = rng.standard_normal((n, len(_VISITS), len(_OUTCOMES)))
    latent = np.empty_like(residual)
    for j, variable in enumerate(_OUTCOMES):
        if variable in ("dd100", "dd1000"):
            latent[:, :, j] = (np.sqrt(0.30) * discounting_factor[:, None]
                               + np.sqrt(0.30) * person_factors[:, j, None]
                               + np.sqrt(0.40) * residual[:, :, j])
        else:
            persistence = 0.90 if variable == "weight_kg" else 0.60
            latent[:, :, j] = (np.sqrt(persistence) * person_factors[:, j, None]
                               + np.sqrt(1.0 - persistence) * residual[:, :, j])
    uniforms = np.clip(special.ndtr(latent), 1e-12, 1.0 - 1e-12)

    # Correlated attendance, independent of every outcome factor. Exact rank
    # counts condition MCAR masks on the supplied per-visit denominators.
    retention_person = rng.standard_normal((n, 1, 1))
    retention_visit = rng.standard_normal((n, len(_VISITS), 1))
    retention_endpoint = rng.standard_normal((n, len(_VISITS), len(_OUTCOMES)))
    attendance = (np.sqrt(0.60) * retention_person
                  + np.sqrt(0.30) * retention_visit
                  + np.sqrt(0.10) * retention_endpoint)
    values = np.empty((n, len(_VISITS), len(_OUTCOMES)))
    for t, month in enumerate(_VISITS):
        for j, variable in enumerate(_OUTCOMES):
            summary = summaries[(month, variable)]
            observed_n = int(round(int(summary["n_observed"]) * n / source_n))
            values[:, t, j] = _marginal_quantiles(
                variable, month, uniforms[:, t, j],
                float(summary["mean"]), float(summary["sd"]))
            absent = np.argsort(attendance[:, t, j], kind="stable")[observed_n:]
            values[absent, t, j] = np.nan

    # Synthetic identifiers contain no source-person linkage.
    result = pd.DataFrame({"person_id": np.repeat(np.arange(1, n + 1), len(_VISITS)),
                           "month": np.tile(np.asarray(_VISITS), n)})
    for j, variable in enumerate(_OUTCOMES):
        result[variable] = values[:, :, j].reshape(-1)
    return result.loc[:, list(_COLUMNS)]
