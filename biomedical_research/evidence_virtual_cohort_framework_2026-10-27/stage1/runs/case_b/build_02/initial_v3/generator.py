"""Positive, paired A0 reconstruction; dependence is explicitly assumed.

Marginal sample means/SDs are reconstruction constraints, not validation.
The stable common factor and endpoint persistence are modeling choices whose
values are not identified by the packet. No reserved analysis is calibrated.
"""

import numpy as np
import pandas as pd
from scipy.optimize import brentq


_ENDPOINTS = ("leptin", "body_mass", "glucose", "triglycerides")
_PERSISTENCE = {"leptin": 0.75, "body_mass": 0.995,
                "glucose": 0.75, "triglycerides": 0.75}
_SHARED_STABLE_VARIANCE = 0.20


def _positive_moment_reconstruction(z, mean, sd):
    """Monotone exponential transform with exact finite-sample moments.

    A root is solved for dispersion, then positive weights are rescaled to the
    source arithmetic mean. This preserves the latent rank ordering, not its
    Pearson correlation. n=1 cannot have an estimable sample SD.
    """
    count = len(z)
    if count == 0:
        return np.empty(0, dtype=float)
    if mean <= 0 or sd < 0:
        raise ValueError("Positive means and nonnegative SDs are required")
    if count == 1 or sd == 0:
        return np.full(count, float(mean))
    cv = float(sd) / float(mean)
    if cv >= np.sqrt(count):
        raise ValueError("Requested sample moments exceed positive support")
    centered = np.asarray(z, dtype=float) - np.max(z)
    spread = float(np.std(centered, ddof=1))
    if not np.isfinite(spread) or spread <= 0:
        raise ValueError("Latent draws must be finite and nonconstant")
    centered = centered / spread

    def residual(scale):
        weights = np.exp(scale * centered)
        return float(np.std(weights, ddof=1) / np.mean(weights) - cv)

    high = 1.0
    while residual(high) < 0:
        high *= 2.0
    scale = brentq(residual, 0.0, high, xtol=1e-13, rtol=1e-13)
    weights = np.exp(scale * centered)
    return float(mean) * weights / np.mean(weights)


def generate(n, seed, evidence, context="target"):
    """Return n synthetic persons; no external state, I/O, or evidence writes."""
    if context != "target":
        raise ValueError("The sole declared context is 'target'")
    if isinstance(n, (bool, np.bool_)) or int(n) != n or n < 0:
        raise ValueError("n must be a nonnegative integer")
    n = int(n)
    source_n = int(evidence["n_persons"])
    if source_n <= 0:
        raise ValueError("Source person count must be positive")
    rng = np.random.default_rng(seed)
    common = rng.normal(size=n)
    # Fresh synthetic keys contain no linkage to source identities.
    data = {"participant_id": [f"syn_{seed}_{i+1:06d}" for i in range(n)]}
    for endpoint in _ENDPOINTS:
        moments = evidence["moments"][endpoint]
        observed_n = int(round(int(moments["n"]) * n / source_n))
        if not 0 <= observed_n <= n:
            raise ValueError("Source complete-pair count outside person count")
        # One random pair mask per endpoint; in this packet all pairs observed.
        observed = rng.permutation(n)[:observed_n]
        stable = rng.normal(size=n)
        persistence = _PERSISTENCE[endpoint]
        stable_part = (
            np.sqrt(_SHARED_STABLE_VARIANCE) * common
            + np.sqrt(persistence - _SHARED_STABLE_VARIANCE) * stable
        )
        for visit in ("pre", "post"):
            latent = stable_part + np.sqrt(1.0 - persistence) * rng.normal(size=n)
            values = np.full(n, np.nan, dtype=float)
            values[observed] = _positive_moment_reconstruction(
                latent[observed], moments[visit + "_mean"], moments[visit + "_sd"]
            )
            data[endpoint + "_" + visit] = values
    return pd.DataFrame(data, columns=["participant_id"] + [
        endpoint + "_" + visit
        for endpoint in _ENDPOINTS for visit in ("pre", "post")
    ])
