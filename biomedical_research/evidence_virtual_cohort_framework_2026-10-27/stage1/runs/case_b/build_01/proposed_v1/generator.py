"""Positive paired reconstruction with three precommitted dependence scenarios.

Supplied marginal sample moments are construction inputs, not validation.
Latent dependence parameters are explicit unestimated assumptions.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import brentq


ENDPOINTS = ("leptin", "body_mass", "glucose", "triglycerides")
SCENARIOS = {
    "target": {
        "persistence": (0.80, 0.98, 0.80, 0.80),
        "shared_innovation_fraction": 0.0,
    },
    "reduced_persistence": {
        "persistence": (0.40, 0.90, 0.40, 0.40),
        "shared_innovation_fraction": 0.0,
    },
    "shared_response": {
        "persistence": (0.80, 0.98, 0.80, 0.80),
        "shared_innovation_fraction": 0.75,
    },
}


def _positive_moment_projection(scores, mean, sd):
    """Condition a positive realized margin on arithmetic mean and sample SD."""
    k = len(scores)
    if k == 0:
        return np.empty(0, dtype=float)
    if not np.isfinite(mean) or mean <= 0 or not np.isfinite(sd) or sd < 0:
        raise ValueError("Require a positive finite mean and nonnegative finite SD")
    if k == 1 or sd == 0:
        return np.full(k, mean, dtype=float)
    cv = sd / mean
    if cv >= np.sqrt(k):
        raise ValueError("Requested moments are infeasible for k positive observations")
    z = np.asarray(scores, dtype=float)
    z = (z - z.mean()) / z.std(ddof=1)
    centered_at_max = z - z.max()

    def weights(shape):
        return np.exp(np.maximum(shape * centered_at_max, -700.0))

    def objective(shape):
        w = weights(shape)
        return w.std(ddof=1) / w.mean() - cv

    upper = 1.0
    while objective(upper) < 0:
        upper *= 2.0
        if not np.isfinite(upper):
            raise ValueError("Could not bracket the marginal shape parameter")
    shape = brentq(objective, 0.0, upper, xtol=1e-13, rtol=1e-13)
    w = weights(shape)
    return mean * w / w.mean()


def generate(n, seed, evidence, context="target"):
    """Return n people in packet column order, without external I/O.

    Baseline endpoint scores are independent in all three scenarios. Post
    scores combine baseline persistence with either independent innovations
    or a positive shared person-level response factor. Marginal projection
    changes raw-scale covariances; latent values are not fitted correlations.
    """
    if context not in SCENARIOS:
        raise ValueError("Unsupported scenario context")
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer number of people")
    n = int(n)
    rng = np.random.default_rng(seed)
    reference_n = int(evidence["n_persons"])
    if reference_n <= 0:
        raise ValueError("evidence n_persons must be positive")
    configuration = SCENARIOS[context]
    fraction = configuration["shared_innovation_fraction"]
    # No extra draw for independent structures: target preserves parent draws.
    shared = rng.standard_normal(n) if fraction > 0 else None
    data = {"participant_id": [f"synthetic_{i + 1:06d}" for i in range(n)]}

    for index, endpoint in enumerate(ENDPOINTS):
        m = evidence["moments"][endpoint]
        observed = int(round(int(m["n"]) * n / reference_n))
        if observed < 0 or observed > n:
            raise ValueError("Invalid scaled complete-pair count")
        if observed == n:
            rows = np.arange(n)
        else:
            rows = np.sort(rng.choice(n, size=observed, replace=False))
        base = rng.standard_normal(observed)
        innovation = rng.standard_normal(observed)
        if shared is not None:
            innovation = (np.sqrt(fraction) * shared[rows]
                          + np.sqrt(1.0 - fraction) * innovation)
        rho = configuration["persistence"][index]
        post = rho * base + np.sqrt(1.0 - rho * rho) * innovation
        for visit, scores in (("pre", base), ("post", post)):
            values = np.full(n, np.nan, dtype=float)
            values[rows] = _positive_moment_projection(
                scores, float(m[visit + "_mean"]), float(m[visit + "_sd"])
            )
            data[endpoint + "_" + visit] = values
    return pd.DataFrame(data)
