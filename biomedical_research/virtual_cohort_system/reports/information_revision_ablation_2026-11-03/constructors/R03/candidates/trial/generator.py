"""Five-variable whole-cohort generator; execute only in the supplied backend."""
import numpy as np
import pandas as pd
from scipy.special import ndtr


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("This whole-cohort model requires observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)

    # Label order is (glucose narrow, HbA1c narrow), (narrow,broad),
    # (broad,narrow), (broad,broad). These are mixture labels, not diagnoses.
    labels = rng.choice(4, size=n, p=np.asarray(p["glycemic_label_probabilities"]))
    z = np.empty((n, 4), dtype=float)
    for broad in (False, True):
        selected = (labels != 0) if broad else (labels == 0)
        correlation = p["latent_correlation_broad"] if broad else p["latent_correlation_narrow"]
        factor = np.linalg.cholesky(np.asarray(correlation, dtype=float))
        z[selected, :] = rng.standard_normal((int(selected.sum()), 4)) @ factor.T

    age_cdf = np.cumsum(np.asarray(p["age_probabilities"], dtype=float))
    age_cdf[-1] = 1.0
    age = np.asarray(p["age_values"], dtype=int)[np.searchsorted(age_cdf, ndtr(z[:, 0]), side="left")]
    female = rng.binomial(1, p["female_probability"], size=n).astype(int)
    bmi = np.exp(p["bmi_log_mean"] + p["bmi_log_sd"] * z[:, 1])
    glucose_broad = labels // 2
    hba1c_broad = labels % 2
    glucose = np.exp(np.asarray(p["glucose_log_means"])[glucose_broad]
                     + np.asarray(p["glucose_log_sds"])[glucose_broad] * z[:, 2])
    hba1c = np.exp(np.asarray(p["hba1c_log_means"])[hba1c_broad]
                   + np.asarray(p["hba1c_log_sds"])[hba1c_broad] * z[:, 3])
    return pd.DataFrame({
        "row_id": ["SYN_R03_" + str(i + 1).zfill(6) for i in range(n)],
        "age": age,
        "female": female,
        "bmi": bmi,
        "glucose": glucose,
        "hba1c": hba1c,
    }, columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
