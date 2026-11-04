"""Published HRS conditional-model reconstruction; no participant records.

The synchronous entry point uses only its specification and random seed.
Construction checks never imported or executed this module.
"""
import math
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    design = p["cohort_design"]
    n = int(design["n_subjects"])
    times = np.asarray(design["visit_times"], dtype=int)
    m = len(times)
    rng = np.random.default_rng(seed)

    # One draw per synthetic subject from the reported joint demographic cells.
    cells = p["demographic_model"]["cells"]
    weights = np.asarray([c["count"] for c in cells], dtype=float)
    chosen = rng.choice(len(cells), size=n, p=weights / weights.sum())
    sex = np.asarray([cells[j]["sex"] for j in chosen])
    race = np.asarray([cells[j]["race"] for j in chosen])
    bins = np.asarray([cells[j]["age_bin"] for j in chosen], dtype=int)
    age_model = p["age_model"]
    bounds = np.asarray(age_model["bin_bounds"], dtype=float)
    baseline_age = rng.uniform(bounds[bins, 0], bounds[bins, 1])
    baseline_age60 = (baseline_age - age_model["center_years"]) / age_model["scale_years"]
    base = {
        "intercept": np.ones(n),
        "baseline_age60": baseline_age60,
        "sex_male": (sex == "male").astype(float),
        "race_black": (race == "black").astype(float),
    }

    cses_model = p["cses_model"]
    cses_x = np.column_stack([base[t] for t in cses_model["terms"]])
    cses = cses_x @ np.asarray(cses_model["coefficients"]) + rng.normal(
        0.0, cses_model["residual_sd"], size=n
    )
    base["cses"] = cses

    education_model = p["education_model"]
    educ_x = np.column_stack([base[t] for t in education_model["terms"]])
    logits = educ_x @ np.asarray(education_model["coefficients"]).T
    logits = logits - np.max(logits, axis=1, keepdims=True)
    probs = np.exp(logits)
    probs = probs / probs.sum(axis=1, keepdims=True)
    cumulative = np.cumsum(probs, axis=1)
    cumulative[:, -1] = 1.0
    educ_index = (rng.random(n)[:, None] >= cumulative).sum(axis=1)
    educ = np.asarray(education_model["levels"])[educ_index]
    base["educ_HS"] = (educ == "HS").astype(float)
    base["educ_LessThanHS"] = (educ == "LessThanHS").astype(float)

    hba_model = p["hba1c_model"]
    hba_x = np.column_stack([base[t] for t in hba_model["terms"]])
    mu = np.exp(hba_x @ np.asarray(hba_model["coefficients"]))
    phi = hba_model["dispersion"]
    hba1c = rng.gamma(shape=1.0 / phi, scale=mu * phi)

    # Covariates are baseline attributes, repeated at every scheduled visit.
    visit_time = np.tile(times, n)
    age = np.repeat(baseline_age, m) + visit_time
    age60 = (age - age_model["center_years"]) / age_model["scale_years"]
    memory_model = p["memory_model"]
    centered_hba = hba1c - memory_model["hba1c_knot"]
    base["U65"] = np.minimum(centered_hba, 0.0)
    base["O65"] = np.maximum(centered_hba, 0.0)
    long_features = {k: np.repeat(v, m) for k, v in base.items()}
    long_features["age60"] = age60
    for term in memory_model["interaction_covariates"]:
        long_features["age60:" + term] = age60 * long_features[term]
    memory_x = np.column_stack([long_features[t] for t in memory_model["terms"]])
    fixed_mean = memory_x @ np.asarray(memory_model["coefficients"])

    # This standard-normal transform realizes the specified 2x2 covariance.
    z = rng.standard_normal((n, 2))
    rho = memory_model["random_effect_correlation"]
    b0 = math.sqrt(memory_model["random_intercept_variance"]) * z[:, 0]
    b1 = math.sqrt(memory_model["random_slope_variance"]) * (
        rho * z[:, 0] + math.sqrt(1.0 - rho * rho) * z[:, 1]
    )
    residual = rng.normal(0.0, math.sqrt(memory_model["residual_variance"]), size=n*m)
    mem_s = fixed_mean + np.repeat(b0, m) + age60 * np.repeat(b1, m) + residual

    subjects = np.asarray([design["identifier_prefix"] + str(i + 1).zfill(5) for i in range(n)])
    subject_id = np.repeat(subjects, m)
    visit_id = [s + "_v" + str(j) for s in subjects for j in range(m)]
    return pd.DataFrame({
        "id": visit_id,
        "subject_id": subject_id,
        "visit_time": visit_time,
        "baseline_age": np.repeat(baseline_age, m),
        "age": age,
        "age60": age60,
        "sex": np.repeat(sex, m),
        "race": np.repeat(race, m),
        "educ": np.repeat(educ, m),
        "cses": np.repeat(cses, m),
        "hba1c": np.repeat(hba1c, m),
        "mem_s": mem_s,
    })
