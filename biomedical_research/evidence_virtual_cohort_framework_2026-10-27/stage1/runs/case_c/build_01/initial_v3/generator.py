"""Source-only paired synthetic cohort; dependence parameters are assumptions.

The arithmetic source moments parameterize population marginals, so finite
synthetic samples fluctuate around them. No paired or change summaries are fit.
"""

import numpy as np
import pandas as pd


ENDPOINTS = ("leptin_log10", "body_mass", "glucose", "triglycerides")
COLUMNS = ["participant_id"] + [
    endpoint + "_" + visit
    for endpoint in ENDPOINTS
    for visit in ("pre", "post")
]


def generate(n, seed, evidence, context="target"):
    """Return n persons with paired endpoints and scaled complete-pair counts.

    Latent variance fractions: shared stable person 0.20, stable endpoint 0.50,
    shared visit 0.05, endpoint-visit residual 0.25. These imply latent same-
    endpoint pre/post correlation 0.70, cross-endpoint same-visit correlation
    0.25 and cross-endpoint opposite-visit correlation 0.20. They are modeling
    choices, not estimates. Nonlinear marginals alter observed correlations.
    """
    if context != "target":
        raise ValueError("Only the declared target context is supported")
    if not isinstance(n, (int, np.integer)) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a nonnegative integer number of persons")
    n = int(n)
    rng = np.random.default_rng(seed)
    stable_person = rng.standard_normal((n, 1, 1))
    stable_endpoint = rng.standard_normal((n, len(ENDPOINTS), 1))
    shared_visit = rng.standard_normal((n, 1, 2))
    residual = rng.standard_normal((n, len(ENDPOINTS), 2))
    z = (
        np.sqrt(0.20) * stable_person
        + np.sqrt(0.50) * stable_endpoint
        + np.sqrt(0.05) * shared_visit
        + np.sqrt(0.25) * residual
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
            if sd < 0:
                raise ValueError("SD must be nonnegative")
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
            # Trailing both-null fields encode unavailable analysis pairs.
            # Their common row placement is a schema convention, not inferred
            # native missingness or an estimated missing-data mechanism.
            values[observed:] = np.nan
            data[endpoint + "_" + visit] = values
    return pd.DataFrame(data, columns=COLUMNS)
