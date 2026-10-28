"""Source-conditioned synthetic rehearsal cohort; no learned joint findings.

The supplied marginal summaries determine the one-dimensional distributions.
All copula and missingness dependence parameters are working assumptions.
Stratified quantiles condition each observed margin on its source summary,
so this is a reconstruction generator rather than an unconditional sample.
"""

import numpy as np
import pandas as pd
from scipy import stats


_VARIABLES = ("weight_kg", "pfs", "gng", "dd100", "dd1000")
_MONTHS = (0, 3, 6, 9, 12)


def _quantiles(variable, month, mean, sd, probabilities):
    """Moment-parameterized margins with their declared measurement support."""
    if sd <= 0:
        values = np.full(len(probabilities), mean, dtype=float)
    elif variable == "weight_kg":
        sigma = np.sqrt(np.log1p((sd / mean) ** 2))
        scale = np.exp(np.log(mean) - 0.5 * sigma ** 2)
        if month == 0:
            # Eligibility is a baseline restriction only.
            upper_probability = stats.lognorm.cdf(180.0, s=sigma, scale=scale)
            probabilities = probabilities * upper_probability
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
        # A total average of fifteen integer items has a 1/15 lattice.
        values = np.clip(np.round(values * 15.0) / 15.0, 1.0, 5.0)
    return np.asarray(values, dtype=float)


def generate(n, seed, evidence, context="target"):
    """Return n new synthetic persons with five visits in schema column order.

    There is one committed scenario. Counts scale by nearest-integer rounding.
    No file access, evidence mutation, or changes to the global RNG occur.
    """
    if context != "target":
        raise ValueError("The only declared context is target")
    if isinstance(n, bool) or int(n) != n or n < 0:
        raise ValueError("n must be a nonnegative integer number of persons")
    n = int(n)
    rng = np.random.default_rng(seed)
    summaries = {(item["variable"], int(item["month"])): item
                 for item in evidence["marginal_summaries"]}
    source_n = int(evidence["n_persons"])

    # Four independent scientific domains: weight, PFS, No-Go, discounting.
    # The two reward magnitudes share one domain, without linking to weight.
    person_factors = rng.normal(size=(n, 5))
    person_factors[:, 4] = (0.70 * person_factors[:, 3]
                            + np.sqrt(1.0 - 0.70 ** 2) * person_factors[:, 4])
    occasion_factors = rng.normal(size=(n, 5, 5))
    occasion_factors[:, :, 4] = (
        0.50 * occasion_factors[:, :, 3]
        + np.sqrt(1.0 - 0.50 ** 2) * occasion_factors[:, :, 4])
    repeatability = np.array([0.94, 0.60, 0.50, 0.65, 0.65])
    latent = (np.sqrt(repeatability)[None, None, :] * person_factors[:, None, :]
              + np.sqrt(1.0 - repeatability)[None, None, :] * occasion_factors)

    # Outcome-independent missingness, with persistent and shared-visit causes.
    retention = rng.normal(size=(n, 1, 1))
    visit_attendance = rng.normal(size=(n, 5, 1))
    endpoint_availability = rng.normal(size=(n, 5, 5))
    missing_score = (np.sqrt(0.60) * retention
                     + np.sqrt(0.30) * visit_attendance
                     + np.sqrt(0.10) * endpoint_availability)
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
            # One local-RNG uniform draw per stratum retains marginal variety
            # while avoiding needless source-moment drift in a small cohort.
            probabilities = (np.arange(observed_n) + rng.uniform(
                1e-6, 1.0 - 1e-6, size=observed_n)) / observed_n
            values[ordered, visit_index, variable_index] = _quantiles(
                variable, month, float(summary["mean"]), float(summary["sd"]),
                probabilities)

    # New synthetic identifiers never encode or reuse a source individual.
    result = {"person_id": np.repeat(np.arange(1, n + 1, dtype=np.int64), 5),
              "month": np.tile(np.array(_MONTHS, dtype=np.int64), n)}
    for index, variable in enumerate(_VARIABLES):
        result[variable] = values[:, :, index].reshape(-1)
    return pd.DataFrame(result, columns=["person_id", "month", *_VARIABLES])
