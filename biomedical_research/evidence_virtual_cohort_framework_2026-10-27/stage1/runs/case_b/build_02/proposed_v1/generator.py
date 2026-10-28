"""Three precommitted A0 reconstructions with unidentified joint dependence.

The supplied marginal moments are reconstruction inputs, not validation.
Contexts differ in assumptions about persistence and common visit deviations.
No reserved paired result is used or calibrated.
"""

import numpy as np
import pandas as pd
from scipy.optimize import brentq


_ENDPOINTS = ("leptin", "body_mass", "glucose", "triglycerides")
_COLUMNS = ["participant_id"] + [
    endpoint + "_" + visit
    for endpoint in _ENDPOINTS for visit in ("pre", "post")
]
_SCENARIOS = {
    "target": {
        "persistence": (0.75, 0.995, 0.75, 0.75),
        "shared_innovation_fraction": 0.0,
    },
    "labile_response": {
        "persistence": (0.35, 0.98, 0.35, 0.35),
        "shared_innovation_fraction": 0.0,
    },
    "shared_response": {
        "persistence": (0.75, 0.995, 0.75, 0.75),
        "shared_innovation_fraction": 0.70,
    },
}
_SHARED_STABLE_VARIANCE = 0.20


def _positive_moment_reconstruction(z, mean, sd):
    """Positive monotone reconstruction of raw-scale sample mean and SD."""
    count = len(z)
    if count == 0:
        return np.empty(0, dtype=float)
    if not np.isfinite(mean) or not np.isfinite(sd) or mean <= 0 or sd < 0:
        raise ValueError("Finite positive means and nonnegative SDs required")
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
    for _ in range(64):
        if residual(high) >= 0:
            break
        high *= 2.0
    else:
        raise ValueError("Positive marginal dispersion could not be bracketed")
    scale = brentq(residual, 0.0, high, xtol=1e-13, rtol=1e-13)
    weights = np.exp(scale * centered)
    return float(mean) * weights / np.mean(weights)


def generate(n, seed, evidence, context="target"):
    """Return n synthetic persons in schema order, using only a local RNG.

    Complete-pair counts scale with n. For an observed count of one only the
    mean is reconstructable; zero observed pairs produce missing values.
    Scenario coefficients describe latent normals, not raw-scale correlations.
    """
    if context not in _SCENARIOS:
        raise ValueError("Unknown declared scenario context: " + str(context))
    if isinstance(n, (bool, np.bool_)) or int(n) != n or n < 0:
        raise ValueError("n must be a nonnegative integer")
    n = int(n)
    source_n = int(evidence["n_persons"])
    if source_n <= 0:
        raise ValueError("Source person count must be positive")
    config = _SCENARIOS[context]
    shared_fraction = config["shared_innovation_fraction"]
    rng = np.random.default_rng(seed)
    common_stable = rng.normal(size=n)
    # The target draw order reproduces the parent measurement construction.
    common_visit = rng.normal(size=(2, n)) if shared_fraction else None
    data = {"participant_id": [
        f"syn_{context}_{seed}_{i+1:06d}" for i in range(n)
    ]}
    for endpoint, persistence in zip(_ENDPOINTS, config["persistence"]):
        moments = evidence["moments"][endpoint]
        observed_n = int(round(int(moments["n"]) * n / source_n))
        if not 0 <= observed_n <= n:
            raise ValueError("Source complete-pair count outside person count")
        observed = rng.permutation(n)[:observed_n]
        stable = rng.normal(size=n)
        stable_part = (
            np.sqrt(_SHARED_STABLE_VARIANCE) * common_stable
            + np.sqrt(persistence - _SHARED_STABLE_VARIANCE) * stable
        )
        for visit_index, visit in enumerate(("pre", "post")):
            innovation = rng.normal(size=n)
            if shared_fraction:
                innovation = (
                    np.sqrt(shared_fraction) * common_visit[visit_index]
                    + np.sqrt(1.0 - shared_fraction) * innovation
                )
            latent = stable_part + np.sqrt(1.0 - persistence) * innovation
            values = np.full(n, np.nan, dtype=float)
            values[observed] = _positive_moment_reconstruction(
                latent[observed], moments[visit + "_mean"], moments[visit + "_sd"]
            )
            data[endpoint + "_" + visit] = values
    return pd.DataFrame(data, columns=_COLUMNS)
