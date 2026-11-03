import numpy as np
import pandas as pd
from scipy.special import expit


def generate(observed, spec, seed):
    """Draw the single declared whole-cohort law without external state or I/O."""
    if observed is not None:
        raise ValueError("This whole-cohort generator requires observed=None.")

    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["design"]["n_rows"])
    a = p["age_distribution"]
    c = p["centering"]
    f = p["female_distribution"]
    b = p["bmi_distribution"]
    g = p["central_glycemia"]
    e = p["elevated_component"]

    lower = np.asarray(a["stratum_lower"], dtype=np.int64)
    upper = np.asarray(a["stratum_upper"], dtype=np.int64)
    stratum = rng.choice(len(lower), size=n, p=a["stratum_probability"])
    age = rng.integers(lower[stratum], upper[stratum] + 1)
    age_coordinate = (age - c["age_reference"]) / c["age_scale"]

    female_probability = expit(
        f["logit_intercept"] + f["logit_age_per_decade"] * age_coordinate
    )
    female = rng.binomial(1, female_probability, size=n).astype(np.int64)
    female_coordinate = female - c["female_reference"]

    bmi = np.exp(
        np.log(b["reference_median"])
        + b["log_age_linear"] * age_coordinate
        + b["log_age_quadratic"] * age_coordinate ** 2
        + b["log_female_difference"] * female_coordinate
        + b["log_residual_sd"] * rng.standard_normal(n)
    )
    bmi_coordinate = (bmi - c["bmi_reference"]) / c["bmi_scale"]

    elevated_probability = expit(
        e["logit_intercept"]
        + e["logit_age"] * age_coordinate
        + e["logit_bmi"] * bmi_coordinate
        + e["logit_male"] * (1 - female)
    )
    elevated = rng.binomial(1, elevated_probability, size=n)
    severity = rng.gamma(
        shape=e["severity_gamma_shape"],
        scale=e["severity_gamma_scale"],
        size=n,
    )

    shared_normal = rng.standard_normal(n)
    independent_normal = rng.standard_normal(n)
    rho = g["log_residual_correlation"]
    hba1c_normal = rho * shared_normal + np.sqrt(1 - rho ** 2) * independent_normal

    glucose = np.exp(
        np.log(g["glucose_reference_median"])
        + g["glucose_log_age"] * age_coordinate
        + g["glucose_log_bmi"] * bmi_coordinate
        + g["glucose_log_female"] * female_coordinate
        + g["glucose_log_residual_sd"] * shared_normal
        + elevated * (e["glucose_log_offset"] + e["glucose_severity_loading"] * severity)
    )
    hba1c = np.exp(
        np.log(g["hba1c_reference_median"])
        + g["hba1c_log_age"] * age_coordinate
        + g["hba1c_log_bmi"] * bmi_coordinate
        + g["hba1c_log_female"] * female_coordinate
        + g["hba1c_log_residual_sd"] * hba1c_normal
        + elevated * (e["hba1c_log_offset"] + e["hba1c_severity_loading"] * severity)
    )

    return pd.DataFrame(
        {
            "row_id": [f"E1_A02_{i + 1:06d}" for i in range(n)],
            "age": age.astype(np.int64),
            "female": female,
            "bmi": bmi,
            "glucose": glucose,
            "hba1c": hba1c,
        },
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"],
    )
