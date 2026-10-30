import numpy as np

def generate(observed, spec, seed):
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    out = observed.copy(deep=True)
    bmi = np.clip(out["bmi_kg_m2"].to_numpy(dtype=float), *p["bmi_bounds"])
    g = out["fasting_glucose_mg_dl"].to_numpy(dtype=float)
    low, knee, upper = p["glucose_knots"]
    gc = np.clip(g, low, upper)
    gx = np.minimum(gc, knee) + p["glucose_tail_weight"] * p["glucose_tail_scale"] * (1 - np.exp(-np.maximum(gc-knee, 0)/p["glucose_tail_scale"]))
    female = (out["sex"].to_numpy() == "female").astype(float)
    mu = np.log(p["reference_insulin_mean"]) - 0.5*p["total_log_variance"]
    mu = mu + p["bmi_log_coefficient"]*(np.log(bmi)-p["log_bmi_center"])
    mu = mu + p["glucose_coefficient"]*(gx-p["glucose_center"])
    mu = mu + p["age_coefficient"]*(out["age_years"].to_numpy(dtype=float)-p["age_center"])
    mu = mu + p["female_log_shift"]*(female-p["female_center"])
    out["fasting_insulin_uU_ml"] = np.exp(mu+rng.normal(0, p["residual_log_sd"], len(out)))
    return out
