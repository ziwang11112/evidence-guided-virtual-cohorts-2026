"""Synthetic paired cohorts with explicitly unidentified dependence scenarios.

Rounded supplied moments are population plug-ins, not independently validated
targets. Scenario frequency is computational allocation, not probability.
"""

import numpy as np
import pandas as pd


ENDPOINTS = ("leptin_log10", "body_mass", "glucose", "triglycerides")

# Shared stable, endpoint stable, shared visit and residual variance shares.
# Each row sums to one. All parameters and loading signs are assumptions.
SCENARIOS = {
    "target": (0.15, 0.50, 0.10, 0.25, (1.0, 1.0, 1.0, 1.0)),
    "stable_endpoint_specific": (0.15, 0.70, 0.00, 0.15, (1.0, 1.0, 1.0, 1.0)),
    "mixed_visit_response": (0.15, 0.20, 0.30, 0.35, (-1.0, 1.0, 1.0, 1.0)),
}


def generate(n, seed, evidence, context="target"):
    """Return n synthetic people, with schema-defined trailing unavailable pairs."""
    if context not in SCENARIOS:
        raise ValueError("Unknown declared scenario")
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer number of persons")
    n = int(n)
    rng = np.random.default_rng(seed)
    common, stable, visit, noise, signs = SCENARIOS[context]

    # Independent factors yield a valid positive semidefinite covariance without
    # fitting any unidentified covariance to marginal evidence.
    shared_stable = rng.standard_normal((n, 1, 1))
    endpoint_stable = rng.standard_normal((n, len(ENDPOINTS), 1))
    shared_visit = rng.standard_normal((n, 1, 2))
    residual = rng.standard_normal((n, len(ENDPOINTS), 2))
    latent = (
        np.sqrt(common) * shared_stable
        + np.sqrt(stable) * endpoint_stable
        + np.sqrt(visit) * np.asarray(signs)[None, :, None] * shared_visit
        + np.sqrt(noise) * residual
    )

    data = {
        "participant_id": [f"synthetic_{context}_{seed}_{i + 1:06d}" for i in range(n)]
    }
    base_n = int(evidence["n_persons"])
    for j, endpoint in enumerate(ENDPOINTS):
        marginal = evidence["moments"][endpoint]
        observed = int(round(int(marginal["n"]) * n / base_n))
        for t, time in enumerate(("pre", "post")):
            mean = float(marginal[time + "_mean"])
            sd = float(marginal[time + "_sd"])
            z = latent[:, j, t]
            if marginal["distribution"] == "normal":
                values = mean + sd * z
            elif marginal["distribution"] == "lognormal":
                log_variance = np.log1p((sd / mean) ** 2)
                log_mean = np.log(mean) - 0.5 * log_variance
                values = np.exp(log_mean + np.sqrt(log_variance) * z)
            else:
                raise ValueError("Unsupported source marginal distribution")
            # Both-null fields mean an unavailable complete analysis pair.
            # Shared trailing gaps satisfy the schema, not native missingness.
            values[observed:] = np.nan
            data[endpoint + "_" + time] = values
    return pd.DataFrame(data)
