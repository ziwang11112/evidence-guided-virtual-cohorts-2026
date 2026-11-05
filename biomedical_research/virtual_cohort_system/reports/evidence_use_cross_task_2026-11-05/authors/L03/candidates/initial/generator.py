"""L03 reviewed finite-moment law; no I/O, fitting, clipping or row rejection."""
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort construction requires observed=None")
    p = specification["parameters"]
    if p["age_biomarker_conditional_independence"] is not True:
        raise ValueError("This reviewed law requires conditional age independence")
    n = int(p["n_rows"])
    names = list(p["biomarker_order"])
    if names != ["bmi", "total_cholesterol", "hdl_cholesterol"]:
        raise ValueError("Unexpected biomarker order")
    rng = np.random.default_rng(seed)
    female_probability = float(p["female_probability"])
    female = rng.random(n) < female_probability
    sex = np.where(female, "F", "M")

    # A separate uniform vector gives independence of age and biomarkers given sex.
    age_spec = p["age"]
    probs = np.asarray(age_spec["probabilities"], dtype=float)
    u = rng.random(n)
    age = np.empty(n, dtype=float)
    for label in ["M", "F"]:
        selected = sex == label
        q = np.asarray(age_spec["knots"][label], dtype=float)
        us = u[selected]
        value = np.interp(us, probs, q)
        tail = us > probs[-2]
        v = (us[tail] - probs[-2]) / (probs[-1] - probs[-2])
        value[tail] = q[-2] + (q[-1] - q[-2]) * (1.0 - np.power(1.0-v, float(age_spec["upper_tail_power"])))
        age[selected] = value

    means = np.array([p["marginal_moments"][v]["mean"] for v in names], dtype=float)
    sds = np.array([p["marginal_moments"][v]["sd"] for v in names], dtype=float)
    ratios = np.array([p["female_to_male_geometric_ratios"][v] for v in names], dtype=float)
    a1 = (1.0-female_probability) + female_probability * ratios
    a2 = (1.0-female_probability) + female_probability * ratios**2
    log_variance = np.log((1.0+(sds/means)**2) * a1**2/a2)
    if not np.all(log_variance > 0):
        raise ValueError("Reviewed moment decomposition requires positive log variance")
    location = np.log(means) - np.log(a1) - log_variance/2.0
    sex_shift = np.log(ratios)
    rank = p["copula_spearman"]
    latent = np.eye(3)
    for i, j, key in [(0, 1, "bmi_tc"), (0, 2, "bmi_hdl"), (1, 2, "tc_hdl")]:
        latent[i, j] = latent[j, i] = 2.0*np.sin(np.pi*float(rank[key])/6.0)
    factor = np.linalg.cholesky(latent)
    z = rng.standard_normal((n, 3)) @ factor.T
    values = np.exp(location + female[:, None]*sex_shift + z*np.sqrt(log_variance))
    return pd.DataFrame({
        "id": [f"L03_{i+1:06d}" for i in range(n)],
        "age": age,
        "sex": sex,
        "bmi": values[:, 0],
        "total_cholesterol": values[:, 1],
        "hdl_cholesterol": values[:, 2],
    })
