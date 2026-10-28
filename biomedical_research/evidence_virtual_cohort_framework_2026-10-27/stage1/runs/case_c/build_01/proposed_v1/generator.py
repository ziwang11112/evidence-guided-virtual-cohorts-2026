"""Three precommitted source-compatible dependence completions.

Marginal means and SDs parameterize distributions, rather than being fit to
each sample. Dependence fractions are sensitivity assumptions, not estimates.
The examined scenarios are not an exhaustive uncertainty set.
"""

import numpy as np
import pandas as pd


ENDPOINTS = ("leptin_log10", "body_mass", "glucose", "triglycerides")
COLUMNS = ["participant_id"] + [
    endpoint + "_" + visit
    for endpoint in ENDPOINTS
    for visit in ("pre", "post")
]

# Variance shares: stable person, stable endpoint, shared visit, residual.
# Each sums to one and therefore preserves standard-normal latent marginals.
STRUCTURES = {
    "target": (0.20, 0.50, 0.05, 0.25),
    "persistent_endpoint_specific": (0.20, 0.70, 0.00, 0.10),
    "shared_visit_variation": (0.15, 0.20, 0.45, 0.20),
}


def generate(n, seed, evidence, context="target"):
    """Generate n paired persons under the declared scenario context.

    Latent within-endpoint correlations are 0.70, 0.90 and 0.35 in committed
    order. Corresponding standardized latent change correlations are 1/6,
    0 and 9/13. These are construction properties, not observed correlations;
    unequal visit scales and nonlinear transforms change raw-scale results.
    """
    if context not in STRUCTURES:
        raise ValueError("Unknown declared scenario context")
    if not isinstance(n, (int, np.integer)) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a nonnegative integer number of persons")
    n = int(n)
    rng = np.random.default_rng(seed)
    stable_person = rng.standard_normal((n, 1, 1))
    stable_endpoint = rng.standard_normal((n, len(ENDPOINTS), 1))
    shared_visit = rng.standard_normal((n, 1, 2))
    residual = rng.standard_normal((n, len(ENDPOINTS), 2))
    person_share, endpoint_share, visit_share, residual_share = STRUCTURES[context]
    z = (
        np.sqrt(person_share) * stable_person
        + np.sqrt(endpoint_share) * stable_endpoint
        + np.sqrt(visit_share) * shared_visit
        + np.sqrt(residual_share) * residual
    )
    data = {"participant_id": ["SYN_C_" + str(i + 1).zfill(6) for i in range(n)]}
    original_n = int(evidence["n_persons"])
    if original_n <= 0:
        raise ValueError("Evidence n_persons must be positive")
    for j, endpoint in enumerate(ENDPOINTS):
        moment = evidence["moments"][endpoint]
        observed = int(round(int(moment["n"]) * n / original_n))
        if not 0 <= observed <= n:
            raise ValueError("Endpoint complete-pair count exceeds person count")
        for t, visit in enumerate(("pre", "post")):
            mean = float(moment[visit + "_mean"])
            sd = float(moment[visit + "_sd"])
            if not np.isfinite(mean) or not np.isfinite(sd) or sd < 0:
                raise ValueError("Moments must be finite and SD nonnegative")
            if moment["distribution"] == "normal":
                values = mean + sd * z[:, j, t]
            elif moment["distribution"] == "lognormal":
                if mean <= 0:
                    raise ValueError("Lognormal mean must be positive")
                log_variance = np.log1p((sd / mean) ** 2)
                log_mean = np.log(mean) - 0.5 * log_variance
                values = np.exp(log_mean + np.sqrt(log_variance) * z[:, j, t])
            else:
                raise ValueError("Unsupported source marginal distribution")
            # Trailing paired nulls encode unavailable complete analysis pairs.
            # Co-placement is required by schema, not inferred missingness.
            values[observed:] = np.nan
            data[endpoint + "_" + visit] = values
    return pd.DataFrame(data, columns=COLUMNS)
