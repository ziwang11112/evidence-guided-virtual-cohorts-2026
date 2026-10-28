"""Three source-compatible joint structures; all association choices are assumptions.

Each observed visit margin uses randomized stratified quantiles assigned by
Gaussian random-intercept ranks. This is conditional cohort reconstruction,
not an iid sampling model or a claim to recover source patient trajectories.
"""
import numpy as np
import pandas as pd
from scipy import stats

_COLUMNS = ["person_id", "month", "weight_kg", "pfs", "gng", "dd100", "dd1000"]
_VISITS = [0, 3, 6, 9, 12]
_SCENARIOS = ("target", "shared_trait", "shared_state")
# Signed shared-factor loadings are sensitivity assumptions, not estimates.
_LOADINGS = {"weight_kg": 0.65, "pfs": 0.70, "gng": 0.65,
             "dd100": -0.75, "dd1000": -0.75}
# Working latent-normal persistent variance fractions; not estimated from packet.
_PERSISTENCE = {"weight_kg": 0.85, "pfs": 0.60, "gng": 0.45,
                "dd100": 0.60, "dd1000": 0.60}


def _margin_quantiles(variable, month, u, mean, sd):
    """Moment-parameterized distributions before count/granularity constraints."""
    if variable == "weight_kg":
        log_var = np.log1p((sd / mean) ** 2)
        shape = np.sqrt(log_var)
        scale = np.exp(np.log(mean) - 0.5 * log_var)
        # Enrollment eligibility is baseline-only. Truncation slightly changes
        # the moment fit; no additional follow-up weight cap is assumed.
        if month == 0:
            u = u * stats.lognorm.cdf(180.0, s=shape, scale=scale)
        return stats.lognorm.ppf(u, s=shape, scale=scale)
    if variable == "gng":
        variance = sd ** 2
        if variance > mean:
            shape = mean ** 2 / (variance - mean)
            probability = shape / (shape + mean)
            # Upper support is the declared measurement bound.
            u = u * stats.nbinom.cdf(512, shape, probability)
            return stats.nbinom.ppf(u, shape, probability)
        u = u * stats.poisson.cdf(512, mean)
        return stats.poisson.ppf(u, mean)
    lower, upper = (1.0, 5.0) if variable == "pfs" else (0.0, 1.0)
    center = (mean - lower) / (upper - lower)
    variance = (sd / (upper - lower)) ** 2
    concentration = center * (1.0 - center) / variance - 1.0
    if not 0.0 < center < 1.0 or concentration <= 0:
        raise ValueError("Source moments are incompatible with a beta margin")
    out = lower + (upper - lower) * stats.beta.ppf(
        u, center * concentration, (1.0 - center) * concentration)
    if variable == "pfs":
        # Fifteen 1--5 items yield increments of 1/15 for complete total averages.
        out = np.round(15.0 * out) / 15.0
    return np.clip(out, lower, upper)


def generate(n, seed, evidence, context="target"):
    """Return n synthetic persons with five visits and declared outcome columns."""
    if context not in _SCENARIOS:
        raise ValueError("Unknown committed scenario")
    if isinstance(n, bool) or int(n) != n or n < 1:
        raise ValueError("n must be a positive integer number of persons")
    n = int(n)
    rng = np.random.default_rng(seed)
    source_n = int(evidence["n_persons"])
    summaries = {(int(m["month"]), m["variable"]): m
                 for m in evidence["marginal_summaries"]}
    rows = {"person_id": np.repeat(np.arange(1, n + 1, dtype=np.int64), 5),
            "month": np.tile(np.asarray(_VISITS, dtype=np.int64), n)}

    # The target path preserves the parent RNG order exactly. Alternative
    # scenarios introduce a factor only at the specified covariance level.
    common_person = rng.standard_normal(n) if context == "shared_trait" else None
    common_visit = rng.standard_normal((n, 5)) if context == "shared_state" else None

    # A shared persistent availability propensity and shared visit shock create
    # overlap of missing masks, with independent endpoint-specific deviations.
    # All are independent of the outcome processes: a working MCAR assumption.
    availability_person = rng.standard_normal(n)
    availability_visit = rng.standard_normal((n, 5))

    for variable in _COLUMNS[2:]:
        persistent = rng.standard_normal(n)
        visit_noise = rng.standard_normal((n, 5))
        loading = _LOADINGS[variable]
        if context == "shared_trait":
            persistent = (loading * common_person
                          + np.sqrt(1.0 - loading ** 2) * persistent)
        elif context == "shared_state":
            visit_noise = (loading * common_visit
                           + np.sqrt(1.0 - loading ** 2) * visit_noise)
        fraction = _PERSISTENCE[variable]
        latent = (np.sqrt(fraction) * persistent[:, None]
                  + np.sqrt(1.0 - fraction) * visit_noise)
        availability_endpoint = rng.standard_normal((n, 5))
        availability = (np.sqrt(0.50) * availability_person[:, None]
                        + np.sqrt(0.30) * availability_visit
                        + np.sqrt(0.20) * availability_endpoint)
        values = np.full((n, 5), np.nan)
        for j, month in enumerate(_VISITS):
            summary = summaries[(month, variable)]
            observed_count = int(round(summary["n_observed"] * n / source_n))
            observed_count = min(n, max(0, observed_count))
            if observed_count == 0:
                continue
            observed = np.argsort(availability[:, j], kind="mergesort")[-observed_count:]
            ordered = observed[np.argsort(latent[observed, j], kind="mergesort")]
            # Randomized stratification stabilizes supplied marginal moments
            # without using any joint source data or conditioning on targets.
            u = (np.arange(observed_count) + rng.random(observed_count)) / observed_count
            u = np.clip(u, np.finfo(float).eps, 1.0 - np.finfo(float).eps)
            values[ordered, j] = _margin_quantiles(
                variable, month, u, float(summary["mean"]), float(summary["sd"]))
        rows[variable] = values.reshape(-1)
    return pd.DataFrame(rows, columns=_COLUMNS)

