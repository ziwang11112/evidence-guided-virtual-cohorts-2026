"""Source-marginal synthetic rehearsal under three declared dependence models.

Positive lognormal marginals reproduce the supplied arithmetic moments as
population parameters. Finite-cohort moments fluctuate. All dependence weights
are sensitivity assumptions, not recovered joint evidence.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


ENDPOINTS = ("leptin", "body_mass", "glucose", "triglycerides")
COLUMNS = ["participant_id"] + [
    f"{endpoint}_{visit}" for endpoint in ENDPOINTS for visit in ("pre", "post")
]
# Common stable person, endpoint stable person, common visit, endpoint visit.
# Each row sums to one, providing a positive-semidefinite normal factor model.
STRUCTURES = {
    "target": (0.20, 0.70, 0.00, 0.10),
    "moderate_individual": (0.20, 0.30, 0.00, 0.50),
    "moderate_shared": (0.20, 0.30, 0.35, 0.15),
}


def generate(n, seed, evidence, context="target") -> pd.DataFrame:
    """Draw n paired persons with local random state and exact observed counts.

    target preserves the parent structure: latent pre/post correlation 0.90,
    cross-endpoint correlation 0.20 at all visits.
    moderate_individual uses latent pre/post correlation 0.50 and retains 0.20
    cross-endpoint correlation at all visits.
    moderate_shared also uses pre/post correlation 0.50, but same-visit
    cross-endpoint correlation is 0.55 versus 0.20 across visits. Its common
    visit factors induce coordinated change heterogeneity. These correlations
    apply to standardized latent normals, not directly to raw outcomes.
    """
    if context not in STRUCTURES:
        raise ValueError("context must identify a declared scenario")
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer person count")
    n = int(n)
    packet_n = int(evidence["n_persons"])
    if packet_n <= 0:
        raise ValueError("Packet person count must be positive")
    common_weight, endpoint_weight, shared_weight, residual_weight = STRUCTURES[context]
    rng = np.random.default_rng(seed)
    data = {
        "participant_id": [f"syn_b03pv1_{context}_{seed}_{i + 1:06d}" for i in range(n)]
    }
    common_person = rng.standard_normal(n)
    # Avoid extra draws in target, preserving the parent's seeded measurements.
    common_visits = (
        rng.standard_normal((2, n)) if shared_weight > 0.0 else np.zeros((2, n))
    )
    for endpoint in ENDPOINTS:
        summary = evidence["moments"][endpoint]
        endpoint_person = rng.standard_normal(n)
        stable = np.sqrt(common_weight) * common_person + np.sqrt(endpoint_weight) * endpoint_person
        n_complete = int(round(float(summary["n"]) * n / packet_n))
        if not 0 <= n_complete <= n:
            raise ValueError("Invalid scaled complete-pair count")
        observed = np.ones(n, dtype=bool)
        if n_complete < n:
            observed[:] = False
            observed[rng.permutation(n)[:n_complete]] = True
        for visit_index, visit in enumerate(("pre", "post")):
            mean = float(summary[f"{visit}_mean"])
            sd = float(summary[f"{visit}_sd"])
            if not np.isfinite(mean) or not np.isfinite(sd) or mean <= 0 or sd < 0:
                raise ValueError("Positive finite means and nonnegative SDs required")
            sigma_squared = np.log1p((sd / mean) ** 2)
            log_mean = np.log(mean) - 0.5 * sigma_squared
            latent = (
                stable
                + np.sqrt(shared_weight) * common_visits[visit_index]
                + np.sqrt(residual_weight) * rng.standard_normal(n)
            )
            values = np.exp(log_mean + np.sqrt(sigma_squared) * latent)
            values[~observed] = np.nan
            data[f"{endpoint}_{visit}"] = values
    return pd.DataFrame(data, columns=COLUMNS)
