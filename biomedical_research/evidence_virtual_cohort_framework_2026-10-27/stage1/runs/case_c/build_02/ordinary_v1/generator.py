"""Source-only paired cohort rehearsal with assumed Gaussian-copula dependence.

The source arithmetic means and sample SDs are plug-in population parameters.
The joint covariance is a working assumption, not identified by the packet.
No realization is selected or rescaled to match reserved outcomes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


ENDPOINTS = ("leptin_log10", "body_mass", "glucose", "triglycerides")
COLUMNS = ["participant_id"] + [
    endpoint + "_" + visit
    for endpoint in ENDPOINTS
    for visit in ("pre", "post")
]

# A single declared scenario: these constants are assumptions, not estimates.
TEMPORAL_CORRELATION = 0.80
CROSS_ENDPOINT_CORRELATION = 0.25


def _endpoint_latents(rng, n):
    """Unit variance endpoint normals with exchangeable correlation 0.25."""
    shared = rng.standard_normal((n, 1))
    specific = rng.standard_normal((n, len(ENDPOINTS)))
    return (
        np.sqrt(CROSS_ENDPOINT_CORRELATION) * shared
        + np.sqrt(1.0 - CROSS_ENDPOINT_CORRELATION) * specific
    )


def _measurement(z, mean, sd, distribution):
    if distribution == "normal":
        return mean + sd * z
    if distribution == "lognormal":
        if mean <= 0 or sd < 0:
            raise ValueError("Lognormal source moments require positive mean and nonnegative SD")
        log_variance = np.log1p((sd / mean) ** 2)
        log_mean = np.log(mean) - 0.5 * log_variance
        return np.exp(log_mean + np.sqrt(log_variance) * z)
    raise ValueError("Unsupported distribution in the evidence packet")


def generate(n, seed, evidence, context="target") -> pd.DataFrame:
    """Generate n synthetic persons with the exact scaled analysis-pair counts.

    Dependence is separable on the normal-copula scale: pre/post correlation
    0.80 within endpoints, contemporaneous cross-endpoint correlation 0.25,
    and cross-endpoint/cross-visit correlation 0.20. Transforming lognormal
    endpoints makes their Pearson correlations differ from these constants.
    Rows missing an analysis pair are a deterministic representation convention;
    the final rows do not encode severity or a native missing-data mechanism.
    """
    if context != "target":
        raise ValueError("Only the declared target scenario is supported")
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer number of persons")
    n = int(n)
    source_n = int(evidence["n_persons"])
    if source_n <= 0:
        raise ValueError("Source person count must be positive")

    rng = np.random.default_rng(seed)
    pre = _endpoint_latents(rng, n)
    innovation = _endpoint_latents(rng, n)
    post = (
        TEMPORAL_CORRELATION * pre
        + np.sqrt(1.0 - TEMPORAL_CORRELATION ** 2) * innovation
    )

    result = {
        "participant_id": ["synthetic_c_" + str(seed) + "_" + str(i + 1).zfill(6) for i in range(n)]
    }
    for j, endpoint in enumerate(ENDPOINTS):
        moments = evidence["moments"][endpoint]
        n_observed = int(round(int(moments["n"]) * n / source_n))
        if n_observed < 0 or n_observed > n:
            raise ValueError("Source endpoint count must lie within person count")
        for visit, latent in (("pre", pre), ("post", post)):
            values = _measurement(
                latent[:, j],
                float(moments[visit + "_mean"]),
                float(moments[visit + "_sd"]),
                moments["distribution"],
            )
            values[n_observed:] = np.nan
            result[endpoint + "_" + visit] = values
    return pd.DataFrame(result, columns=COLUMNS)
