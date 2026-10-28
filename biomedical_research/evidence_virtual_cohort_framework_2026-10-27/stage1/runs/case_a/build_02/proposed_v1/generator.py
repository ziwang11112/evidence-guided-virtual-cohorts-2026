"""Source-conditioned rehearsal cohorts with three unresolved joint structures.

All marginal families and copula parameters are assumptions. Marginal inputs
are reconstruction targets, not independently validated empirical findings.
"""

import numpy as np
import pandas as pd
from scipy import stats


_VARIABLES = ("weight_kg", "pfs", "gng", "dd100", "dd1000")
_MONTHS = (0, 3, 6, 9, 12)
_CONTEXTS = ("target", "shared_trait", "state_selection")


def _quantiles(variable, month, mean, sd, probabilities):
    """The parent's supported marginal family, conditional on observed counts."""
    if sd <= 0:
        values = np.full(len(probabilities), mean, dtype=float)
    elif variable == "weight_kg":
        sigma = np.sqrt(np.log1p((sd / mean) ** 2))
        scale = np.exp(np.log(mean) - 0.5 * sigma ** 2)
        if month == 0:
            probabilities = probabilities * stats.lognorm.cdf(
                180.0, s=sigma, scale=scale)
        values = stats.lognorm.ppf(probabilities, s=sigma, scale=scale)
    elif variable == "gng":
        variance = sd ** 2
        if variance > mean:
            shape = mean ** 2 / (variance - mean)
            probability = mean / variance
            upper_probability = stats.nbinom.cdf(512, shape, probability)
            values = stats.nbinom.ppf(probabilities * upper_probability,
                                     shape, probability)
        else:
            upper_probability = stats.poisson.cdf(512, mean)
            values = stats.poisson.ppf(probabilities * upper_probability, mean)
    else:
        lower, width = (1.0, 4.0) if variable == "pfs" else (0.0, 1.0)
        normalized_mean = (mean - lower) / width
        normalized_variance = (sd / width) ** 2
        concentration = (normalized_mean * (1.0 - normalized_mean)
                         / normalized_variance - 1.0)
        if concentration <= 0:
            raise ValueError("Source moments incompatible with beta support")
        alpha = normalized_mean * concentration
        beta = (1.0 - normalized_mean) * concentration
        values = lower + width * stats.beta.ppf(probabilities, alpha, beta)
    if variable == "pfs":
        values = np.clip(np.round(values * 15.0) / 15.0, 1.0, 5.0)
    return np.asarray(values, dtype=float)


def _domain_correlation(discount_correlation):
    correlation = np.eye(5)
    correlation[3, 4] = correlation[4, 3] = discount_correlation
    return correlation


def _shared_correlation(base, loadings):
    """A shared factor plus correlated residuals guarantees positive variance."""
    residual = np.sqrt(1.0 - loadings ** 2)
    return (np.outer(loadings, loadings)
            + residual[:, None] * base * residual[None, :])


def generate(n, seed, evidence, context="target"):
    """Generate n synthetic persons; context selects a committed assumption."""
    if context not in _CONTEXTS:
        raise ValueError("Unknown scenario context")
    if isinstance(n, bool) or int(n) != n or n < 0:
        raise ValueError("n must be a nonnegative integer number of persons")
    n = int(n)
    rng = np.random.default_rng(seed)
    summaries = {(item["variable"], int(item["month"])): item
                 for item in evidence["marginal_summaries"]}
    source_n = int(evidence["n_persons"])

    person_correlation = _domain_correlation(0.70)
    occasion_correlation = _domain_correlation(0.50)
    repeatability = np.array([0.94, 0.60, 0.50, 0.65, 0.65])
    loadings = np.array([0.45, 0.65, 0.45, -0.45, -0.45])
    occasion_ar = 0.0
    selection_loading = 0.0
    if context == "shared_trait":
        person_correlation = _shared_correlation(person_correlation, loadings)
    elif context == "state_selection":
        occasion_correlation = _shared_correlation(occasion_correlation, loadings)
        repeatability = np.array([0.75, 0.30, 0.25, 0.35, 0.35])
        occasion_ar = 0.40
        selection_loading = 0.45

    # Identical RNG array sizes across contexts keep marginal draws paired.
    person_factors = (rng.normal(size=(n, 5))
                      @ np.linalg.cholesky(person_correlation).T)
    occasion_factors = (rng.normal(size=(n, 5, 5))
                        @ np.linalg.cholesky(occasion_correlation).T)
    for visit_index in range(1, 5):
        occasion_factors[:, visit_index, :] = (
            occasion_ar * occasion_factors[:, visit_index - 1, :]
            + np.sqrt(1.0 - occasion_ar ** 2)
            * occasion_factors[:, visit_index, :])
    latent = (np.sqrt(repeatability)[None, None, :] * person_factors[:, None, :]
              + np.sqrt(1.0 - repeatability)[None, None, :] * occasion_factors)

    retention = rng.normal(size=(n, 1, 1))
    visit_attendance = rng.normal(size=(n, 5, 1))
    endpoint_availability = rng.normal(size=(n, 5, 5))
    missing_score = (np.sqrt(0.60) * retention
                     + np.sqrt(0.30) * visit_attendance
                     + np.sqrt(0.10) * endpoint_availability)
    if selection_loading:
        # Only baseline behavioral ranks affect later observation propensity.
        # Higher PFS/No-Go and lower AUC increase missing-score ranks.
        a = np.sqrt(repeatability)
        b = np.sqrt(1.0 - repeatability)
        baseline_covariance = (
            a[:, None] * person_correlation * a[None, :]
            + b[:, None] * occasion_correlation * b[None, :])
        contrast = np.array([0.0, 1.0, 1.0, -1.0, -1.0])
        baseline_score = (latent[:, 0, :] @ contrast
                          / np.sqrt(contrast @ baseline_covariance @ contrast))
        missing_score = (np.sqrt(1.0 - selection_loading ** 2) * missing_score
                         + selection_loading * baseline_score[:, None, None])

    values = np.full((n, 5, 5), np.nan, dtype=float)
    for visit_index, month in enumerate(_MONTHS):
        for variable_index, variable in enumerate(_VARIABLES):
            summary = summaries[(variable, month)]
            observed_n = int(round(summary["n_observed"] * n / source_n))
            if observed_n == 0:
                continue
            observed = np.argsort(missing_score[:, visit_index, variable_index],
                                  kind="stable")[:observed_n]
            ordered = observed[np.argsort(latent[observed, visit_index, variable_index],
                                          kind="stable")]
            probabilities = (np.arange(observed_n) + rng.uniform(
                1e-6, 1.0 - 1e-6, size=observed_n)) / observed_n
            values[ordered, visit_index, variable_index] = _quantiles(
                variable, month, float(summary["mean"]), float(summary["sd"]),
                probabilities)

    result = {"person_id": np.repeat(np.arange(1, n + 1, dtype=np.int64), 5),
              "month": np.tile(np.array(_MONTHS, dtype=np.int64), n)}
    for index, variable in enumerate(_VARIABLES):
        result[variable] = values[:, :, index].reshape(-1)
    return pd.DataFrame(result, columns=["person_id", "month", *_VARIABLES])
