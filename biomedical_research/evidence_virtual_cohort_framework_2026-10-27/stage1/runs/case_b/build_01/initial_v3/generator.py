"""Source-conditioned positive paired cohorts; no external data or I/O.

Marginal sample moments are construction constraints, not validation evidence.
The latent dependence parameters below are assumptions, not packet estimates.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import brentq


ENDPOINTS = ("leptin", "body_mass", "glucose", "triglycerides")
LATENT_PERSISTENCE = {
    "leptin": 0.80,
    "body_mass": 0.98,
    "glucose": 0.80,
    "triglycerides": 0.80,
}


def _positive_moment_projection(scores, mean, sd):
    """Monotone exponential projection to the supplied arithmetic moments.

    This conditions the synthetic cohort on rounded source sample moments.
    It is not a claim that independently sampled cohorts have fixed moments.
    """
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
        # Clipping protects strictly positive support against numerical underflow.
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
    """Return n synthetic people in the declared paired-wide schema.

    Each endpoint has correlated Gaussian pre/post scores. Endpoints have
    independent score pairs. A monotone positive transform conditions each
    observed margin on its supplied mean and sample SD. Correlations on the
    raw scale are neither specified by the packet nor forced by this program.
    """
    if context != "target":
        raise ValueError("Only the declared target scenario is supported")
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError("n must be a nonnegative integer number of people")
    n = int(n)
    rng = np.random.default_rng(seed)
    reference_n = int(evidence["n_persons"])
    if reference_n <= 0:
        raise ValueError("evidence n_persons must be positive")
    data = {"participant_id": [f"synthetic_{i + 1:06d}" for i in range(n)]}

    for endpoint in ENDPOINTS:
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
        rho = LATENT_PERSISTENCE[endpoint]
        post = rho * base + np.sqrt(1.0 - rho * rho) * innovation
        for visit, scores in (("pre", base), ("post", post)):
            values = np.full(n, np.nan, dtype=float)
            values[rows] = _positive_moment_projection(
                scores, float(m[visit + "_mean"]), float(m[visit + "_sd"])
            )
            data[endpoint + "_" + visit] = values
    return pd.DataFrame(data)
