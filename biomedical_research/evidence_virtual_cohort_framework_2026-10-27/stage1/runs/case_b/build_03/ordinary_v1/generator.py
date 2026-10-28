"""Positive paired synthetic rehearsal data from supplied marginal moments.

The joint distribution is a declared assumption, not recovered evidence.  The
reported marginal moments parameterize population distributions; random cohort
moments are not forced to equal the reconstruction inputs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


ENDPOINTS = ("leptin", "body_mass", "glucose", "triglycerides")
COLUMNS = ["participant_id"] + [
    f"{endpoint}_{visit}" for endpoint in ENDPOINTS for visit in ("pre", "post")
]


def generate(n, seed, evidence, context="target") -> pd.DataFrame:
    """Draw n persons using one locally seeded Gaussian-factor copula.

    Lognormal marginal means/SDs equal the rounded packet values in expectation
    (SD denotes the population distribution parameter). Latent normal
    correlations are 0.90 within endpoint over visits and 0.20 between endpoints
    at any visits. These correlations are assumptions on the log scale; raw
    correlations and change correlations differ and are not calibration inputs.
    """
    if context != "target":
        raise ValueError("Only the declared target scenario is supported")
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer person count")
    n = int(n)
    packet_n = int(evidence["n_persons"])
    if packet_n <= 0:
        raise ValueError("Packet person count must be positive")
    rng = np.random.default_rng(seed)
    data = {
        "participant_id": [f"syn_b03_{seed}_{i + 1:06d}" for i in range(n)]
    }
    # Variance partition: 0.20 stable common person factor, 0.70 stable
    # endpoint-specific person factor, 0.10 independent visit fluctuation.
    common_person = rng.standard_normal(n)
    for endpoint in ENDPOINTS:
        summary = evidence["moments"][endpoint]
        endpoint_person = rng.standard_normal(n)
        stable = np.sqrt(0.20) * common_person + np.sqrt(0.70) * endpoint_person
        n_complete = int(round(float(summary["n"]) * n / packet_n))
        if not 0 <= n_complete <= n:
            raise ValueError("Invalid scaled complete-pair count")
        observed = np.ones(n, dtype=bool)
        if n_complete < n:
            observed[:] = False
            observed[rng.permutation(n)[:n_complete]] = True
        for visit in ("pre", "post"):
            mean = float(summary[f"{visit}_mean"])
            sd = float(summary[f"{visit}_sd"])
            if not np.isfinite(mean) or not np.isfinite(sd) or mean <= 0 or sd < 0:
                raise ValueError("Positive finite means and nonnegative SDs required")
            sigma_squared = np.log1p((sd / mean) ** 2)
            log_mean = np.log(mean) - 0.5 * sigma_squared
            latent = stable + np.sqrt(0.10) * rng.standard_normal(n)
            values = np.exp(log_mean + np.sqrt(sigma_squared) * latent)
            values[~observed] = np.nan
            data[f"{endpoint}_{visit}"] = values
    return pd.DataFrame(data, columns=COLUMNS)
