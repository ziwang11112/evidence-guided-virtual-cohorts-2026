"""Evidence-informed scenario; executed only by the supplied isolated harness."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    n = int(p["n_rows"])
    rng = np.random.default_rng(seed)
    a = p["age_model"]
    ages = np.arange(a["minimum"], a["maximum"] + 1, dtype=np.int64)
    weights = np.exp(-0.5 * ((ages - a["location"]) / a["scale"]) ** 2)
    age = rng.choice(ages, size=n, p=weights / weights.sum())
    da = age - a["location"]
    s = p["sex_model"]
    eta_s = np.log(s["reference_probability"] / (1-s["reference_probability"])) + s["age_logodds"] * da
    female = (rng.random(n) < 1 / (1 + np.exp(-eta_s))).astype(np.int64)
    df = female - s["reference_probability"]
    b = p["bmi_model"]
    knot = b["age_knot"]
    age_bmi = b["age_below_log_slope"] * (np.minimum(age, knot) - min(a["location"], knot))
    age_bmi += b["age_above_log_slope"] * (np.maximum(age-knot, 0) - max(a["location"]-knot, 0))
    log_bmi_centered = age_bmi + b["female_log_shift"] * df + b["log_sd"] * rng.standard_normal(n)
    bmi = b["reference_median"] * np.exp(log_bmi_centered)
    t = p["tail_model"]
    eta_t = np.log(t["reference_probability"] / (1-t["reference_probability"]))
    eta_t = eta_t + t["age_logodds"] * da + t["log_bmi_logodds"] * log_bmi_centered + t["female_logodds"] * df
    # Stable expit; no rejection sampling, clipping or supplementary cohort.
    tail_probability = np.exp(-np.logaddexp(0, -eta_t))
    component = (rng.random(n) < tail_probability).astype(np.int64)
    m = p["biomarker_model"]
    zg = rng.standard_normal(n)
    independent_h = rng.standard_normal(n)
    rho = m["residual_correlation"]
    zh = rho * zg + np.sqrt(1-rho*rho) * independent_h
    glucose = np.exp(np.log(np.asarray(m["glucose_medians"])[component])
        + m["glucose_age_log_slope"] * da
        + m["glucose_log_bmi_slope"] * log_bmi_centered
        + m["glucose_female_log_shift"] * df
        + np.asarray(m["glucose_log_sds"])[component] * zg)
    hba1c = np.exp(np.log(np.asarray(m["hba1c_medians"])[component])
        + m["hba1c_age_log_slope"] * da
        + m["hba1c_log_bmi_slope"] * log_bmi_centered
        + m["hba1c_female_log_shift"] * df
        + np.asarray(m["hba1c_log_sds"])[component] * zh)
    return pd.DataFrame({"row_id": [f"L03_{i+1:05d}" for i in range(n)],
        "age": age, "female": female, "bmi": bmi, "glucose": glucose, "hba1c": hba1c},
        columns=["row_id", "age", "female", "bmi", "glucose", "hba1c"])
