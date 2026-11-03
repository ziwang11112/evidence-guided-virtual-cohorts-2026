"""A01 direct eligible-population generator. No individual input or I/O."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    context_id = p["active_context"]
    descriptor = p["contexts"][context_id]
    x = descriptor["inputs"]
    n = descriptor["n_rows"]
    innovation = p["innovations"]
    rng = np.random.default_rng(seed)
    age = rng.integers(x["age_lower"], x["age_upper"] + 1, n)
    female = rng.binomial(1, x["female_probability"], n)
    latent = {}
    for name in p["construction"]["innovation_order"]:
        if x["innovation_family"] == "uniform":
            latent[name] = rng.uniform(innovation["uniform_lower"], innovation["uniform_upper"], n)
        elif x["innovation_family"] == "gamma":
            latent[name] = rng.gamma(innovation["gamma_shape"], innovation["gamma_scale"], n) - innovation["gamma_center"]
        else:
            raise ValueError("Unknown innovation family")
    bmi = x["bmi_location"] + x["bmi_sd"] * latent["X"]
    glucose = (x["glucose_location"]
               + p["glucose_on_bmi"] * x["bmi_sd"] * latent["X"]
               + x["glucose_independent_scale"] * latent["Z"])
    hba1c = (x["hba1c_location"]
             + p["hba1c_on_glucose"] * (glucose - x["glucose_location"])
             + x["residual_scale"] * latent["E"])
    frame = pd.DataFrame({
        "row_id": [f"{context_id}_{seed}_{i}" for i in range(n)],
        "age": age, "female": female,
        "bmi": bmi, "glucose": glucose, "hba1c": hba1c,
    })
    if not np.isfinite(frame[["age", "female", "bmi", "glucose", "hba1c"]].to_numpy()).all():
        raise FloatingPointError("Nonfinite generated value; no repair")
    d = p["required_domains"][context_id]
    if not ((age >= d["age_lower"]) & (age <= d["age_upper"])).all():
        raise ValueError("Age-domain failure; no repair")
    if not np.isin(female, [0, 1]).all():
        raise ValueError("Membership-domain failure; no repair")
    for name in d["positive_columns"]:
        if not (frame[name] > 0).all():
            raise FloatingPointError("Positivity failure; no repair")
    if d["glucose_upper_exclusive"] is not None and not (glucose < d["glucose_upper_exclusive"]).all():
        raise ValueError("Glucose eligibility failure; no repair")
    if d["hba1c_lower_inclusive"] is not None and not (hba1c >= d["hba1c_lower_inclusive"]).all():
        raise ValueError("Native IFCC-domain failure; no repair")
    return frame
