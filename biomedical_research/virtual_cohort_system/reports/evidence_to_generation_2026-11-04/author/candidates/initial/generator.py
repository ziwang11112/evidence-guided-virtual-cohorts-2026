"""Whole-cohort sampler. All scientific settings are in model_spec.json."""
import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("whole-cohort input must be None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["n_rows"])
    female = rng.binomial(1, p["female_probability"], size=n)
    age = np.empty(n, dtype=np.int64)
    bmi = np.empty(n, dtype=float)
    glucose = np.empty(n, dtype=float)
    hba1c = np.empty(n, dtype=float)
    for sex in ("male", "female"):
        model = p["sex_models"][sex]
        indices = np.flatnonzero(female == model["female"])
        R = np.asarray(model["latent_correlation"], dtype=float)
        # A Cholesky failure is an error, never repaired by changing the model.
        z = rng.standard_normal((len(indices), 4)) @ np.linalg.cholesky(R).T
        bins = np.asarray(model["age"]["latent_thresholds_finite"], dtype=float)
        values = np.asarray(model["age"]["values"], dtype=np.int64)
        age[indices] = values[np.searchsorted(bins, z[:, 0], side="right")]
        for k, out, column in ((1, bmi, "bmi"), (2, glucose, "glucose"), (3, hba1c, "hba1c")):
            law = model[column]
            out[indices] = law["floor"] + np.exp(law["log_mu"] + law["log_sd"] * z[:, k])
    digits = int(p["rounding_digits"])
    return pd.DataFrame({
        "person_id": [p["row_id_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": age,
        "female": female,
        "bmi": np.round(bmi, digits),
        "hba1c": np.round(hba1c, digits),
        "glucose": np.round(glucose, digits),
    })
