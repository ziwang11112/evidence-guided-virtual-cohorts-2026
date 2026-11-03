"""Whole-cohort generator. Execute only through the supplied isolated backend."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort mode requires observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)
    pair = rng.choice(4, size=n, p=np.asarray(p["mixture_indicator_probabilities"], dtype=float))
    epsilon = rng.standard_normal((n, 5))
    z = np.empty((n, 5), dtype=float)
    for component in range(4):
        selected = pair == component
        z[selected] = epsilon[selected] @ np.asarray(p["component_latent_cholesky"][component], dtype=float).T
    age_spec = p["age_distribution"]
    age = np.asarray(age_spec["values"], dtype=int)[np.searchsorted(
        np.asarray(age_spec["latent_normal_edges"], dtype=float), z[:, 0], side="right")]
    female = (z[:, 1] <= p["female_latent_threshold"]).astype(int)
    bmi = np.exp(p["bmi_lognormal"]["log_mean"] + p["bmi_lognormal"]["log_sd"]*z[:, 2])
    g_component = pair // 2
    h_component = pair % 2
    gp, hp = p["glucose_mixture"], p["hba1c_mixture"]
    glucose = np.exp(np.asarray(gp["log_means"])[g_component] + np.asarray(gp["log_sds"])[g_component]*z[:, 3])
    hba1c = np.exp(np.asarray(hp["log_means"])[h_component] + np.asarray(hp["log_sds"])[h_component]*z[:, 4])
    return pd.DataFrame({"row_id": [f"R01_{seed}_{i+1:06d}" for i in range(n)],
                         "age": age, "female": female, "bmi": bmi,
                         "glucose": glucose, "hba1c": hba1c},
                        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
