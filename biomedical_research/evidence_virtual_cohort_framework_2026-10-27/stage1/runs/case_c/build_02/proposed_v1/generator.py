"""Source-only paired rehearsal under three precommitted dependence assumptions.

Rounded arithmetic marginal moments are plug-in population parameters. Joint
relationships are assumptions, not estimates or validated clinical findings.
There is no file I/O, evidence mutation, sample matching, or seed selection.
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
SCENARIOS = ("target", "stable_shared_trait", "discordant_response")


def _endpoint_latents(rng, n, shared_fraction, loadings=None):
    """Unit-variance normal vector with an explicit shared-factor structure."""
    if loadings is None:
        loadings = np.ones(len(ENDPOINTS))
    shared = rng.standard_normal((n, 1))
    specific = rng.standard_normal((n, len(ENDPOINTS)))
    return (
        np.sqrt(shared_fraction) * shared * loadings
        + np.sqrt(1.0 - shared_fraction) * specific
    )


def _paired_latents(rng, n, context):
    if context == "target":
        # Preserve the parent's numerical construction and random draw order.
        pre = _endpoint_latents(rng, n, 0.25)
        innovation = _endpoint_latents(rng, n, 0.25)
        post = 0.80 * pre + np.sqrt(1.0 - 0.80 ** 2) * innovation
        return pre, post
    if context == "stable_shared_trait":
        # Stable traits explain all cross-endpoint dependence. Visit-specific
        # deviations are independent across visits and endpoints.
        trait = _endpoint_latents(rng, n, 0.3125)
        pre_noise = rng.standard_normal((n, len(ENDPOINTS)))
        post_noise = rng.standard_normal((n, len(ENDPOINTS)))
        pre = np.sqrt(0.80) * trait + np.sqrt(0.20) * pre_noise
        post = np.sqrt(0.80) * trait + np.sqrt(0.20) * post_noise
        return pre, post
    if context == "discordant_response":
        # Independent level and response components. Signs are an unvalidated
        # sensitivity assumption: leptin/body mass versus glucose/triglycerides.
        level = _endpoint_latents(rng, n, 0.25)
        response = _endpoint_latents(rng, n, 0.50, np.array([1.0, 1.0, -1.0, -1.0]))
        pre = np.sqrt(0.70) * level - np.sqrt(0.30) * response
        post = np.sqrt(0.70) * level + np.sqrt(0.30) * response
        return pre, post
    raise ValueError("Unknown scenario; use a declared context")


def _measurement(z, mean, sd, distribution):
    if not np.isfinite(mean) or not np.isfinite(sd) or sd < 0:
        raise ValueError("Source marginal moments must be finite with nonnegative SD")
    if distribution == "normal":
        return mean + sd * z
    if distribution == "lognormal":
        if mean <= 0:
            raise ValueError("Lognormal source means must be positive")
        log_variance = np.log1p((sd / mean) ** 2)
        log_mean = np.log(mean) - 0.5 * log_variance
        return np.exp(log_mean + np.sqrt(log_variance) * z)
    raise ValueError("Unsupported distribution in the evidence packet")


def generate(n, seed, evidence, context="target") -> pd.DataFrame:
    """Generate n persons, preserving scaled complete-pair counts and support.

    Both-null endpoint fields encode unavailable analysis pairs. Last-row
    masking is the schema convention, not an inferred clinical mechanism.
    Gaussian-scale structural constants need not equal observed-scale Pearson
    correlations following lognormal transformations or unequal marginal SDs.
    """
    if context not in SCENARIOS:
        raise ValueError("Unknown scenario; use a declared context")
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer number of persons")
    n = int(n)
    source_n = int(evidence["n_persons"])
    if source_n <= 0:
        raise ValueError("Source person count must be positive")
    rng = np.random.default_rng(seed)
    pre, post = _paired_latents(rng, n, context)
    result = {
        "participant_id": [
            "synthetic_c_" + context + "_" + str(seed) + "_" + str(i + 1).zfill(6)
            for i in range(n)
        ]
    }
    for j, endpoint in enumerate(ENDPOINTS):
        moments = evidence["moments"][endpoint]
        source_pairs = int(moments["n"])
        if source_pairs < 0 or source_pairs > source_n:
            raise ValueError("Source endpoint count must lie within person count")
        n_observed = int(round(source_pairs * n / source_n))
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
