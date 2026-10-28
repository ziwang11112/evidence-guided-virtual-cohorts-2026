"""Literature-anchored stochastic HDL model; no target HDL information is used."""
import numpy as np
import pandas as pd


def conditional_moments(observed: pd.DataFrame, evidence: dict):
    p = evidence["parameters"]
    bmi = observed["bmi"].to_numpy(dtype=float)
    age = observed["age"].to_numpy(dtype=float)
    sex = observed["sex"].to_numpy()
    knots = np.asarray(p["bmi_anchor_kg_m2"], dtype=float)
    age_effect = np.interp(age, p["age_knots_years"], p["age_effect_mg_dl"])
    age_effect = age_effect - p["age_center_mg_dl"]
    means = np.empty(len(observed), dtype=float)
    sds = np.empty(len(observed), dtype=float)
    for code in (1, 2):
        selected = sex == code
        key = str(code)
        m = np.asarray(p["mean_hdl_by_sex"][key], dtype=float)
        s = np.asarray(p["sd_hdl_by_sex"][key], dtype=float)
        b = bmi[selected]
        location = np.interp(b, knots, m)
        upper = b > knots[-1]
        floor = p["tail_asymptote_by_sex"][key]
        location[upper] = floor + (m[-1] - floor) * np.exp(
            -p["tail_decay_per_bmi"] * (b[upper] - knots[-1])
        )
        means[selected] = location + age_effect[selected]
        sds[selected] = np.interp(b, knots, s)
    return means, sds


def generate(observed: pd.DataFrame, evidence: dict, seed: int) -> pd.DataFrame:
    """Return one positive HDL draw, preserving observed values and row order."""
    required = ["row_id", "bmi", "age", "sex"]
    if not all(c in observed.columns for c in required):
        raise ValueError("Missing required observed column")
    if not observed["sex"].isin([1, 2]).all():
        raise ValueError("Sex must use codes 1 and 2")
    values = observed[["bmi", "age"]].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("BMI and age must be finite and positive")
    mean, sd = conditional_moments(observed, evidence)
    if (mean <= 0).any() or (sd <= 0).any():
        raise ValueError("Specification implies invalid conditional moments")
    log_variance = np.log1p((sd / mean) ** 2)
    log_location = np.log(mean) - log_variance / 2
    rng = np.random.default_rng(seed)
    out = observed.loc[:, required].copy(deep=True)
    out["hdl"] = rng.lognormal(log_location, np.sqrt(log_variance))
    return out
