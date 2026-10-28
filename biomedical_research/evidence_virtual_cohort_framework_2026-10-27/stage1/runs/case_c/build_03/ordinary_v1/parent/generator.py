"""Source-only synthetic paired cohort; dependence is an explicit assumption.

Marginal parameters use the packet's rounded arithmetic means and sample SDs
as population-moment plug-in estimates. Realized samples fluctuate around them.
No joint parameter is estimated from the supplied marginals.
"""

import numpy as np
import pandas as pd


ENDPOINTS = ("leptin_log10", "body_mass", "glucose", "triglycerides")


def generate(n, seed, evidence, context="target"):
    """Return n synthetic people using local random state and fixed final-row gaps."""
    if context != "target":
        raise ValueError("Only the declared target scenario is available")
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer number of persons")
    n = int(n)
    rng = np.random.default_rng(seed)

    # Unidentified but fixed construction assumptions, selected before diagnostics:
    # 0.15 shared stable + 0.50 endpoint stable + 0.10 shared visit + 0.25 residual.
    # Each latent measurement has variance one; its within-endpoint pre/post
    # correlation is 0.65. Other-endpoint correlations are 0.25 at the same visit
    # and 0.15 across visits. These are NOT supplied empirical estimates.
    shared_stable = rng.standard_normal((n, 1, 1))
    endpoint_stable = rng.standard_normal((n, len(ENDPOINTS), 1))
    shared_visit = rng.standard_normal((n, 1, 2))
    residual = rng.standard_normal((n, len(ENDPOINTS), 2))
    latent = (
        np.sqrt(0.15) * shared_stable
        + np.sqrt(0.50) * endpoint_stable
        + np.sqrt(0.10) * shared_visit
        + np.sqrt(0.25) * residual
    )

    data = {"participant_id": [f"synthetic_{seed}_{i + 1:06d}" for i in range(n)]}
    base_n = int(evidence["n_persons"])
    for j, endpoint in enumerate(ENDPOINTS):
        marginal = evidence["moments"][endpoint]
        observed = int(round(int(marginal["n"]) * n / base_n))
        for t, visit in enumerate(("pre", "post")):
            mean = float(marginal[visit + "_mean"])
            sd = float(marginal[visit + "_sd"])
            z = latent[:, j, t]
            if marginal["distribution"] == "normal":
                values = mean + sd * z
            elif marginal["distribution"] == "lognormal":
                log_variance = np.log1p((sd / mean) ** 2)
                log_mean = np.log(mean) - 0.5 * log_variance
                values = np.exp(log_mean + np.sqrt(log_variance) * z)
            else:
                raise ValueError("Unsupported source marginal distribution")
            # Both-null cells denote an unavailable complete analysis pair.
            # Shared trailing gaps implement the schema, not native missingness.
            values[observed:] = np.nan
            data[endpoint + "_" + visit] = values
    return pd.DataFrame(data)
