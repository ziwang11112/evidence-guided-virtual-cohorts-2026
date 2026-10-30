import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    p = spec["parameters"]
    out = observed.copy(deep=True)
    age = observed["age_years"].to_numpy(dtype=float)
    bmi = observed["bmi_kg_m2"].to_numpy(dtype=float)
    glucose = observed["fasting_glucose_mg_dl"].to_numpy(dtype=float)
    bt = p["high_bmi_extension"]["threshold_kg_m2"]
    bs = p["high_bmi_extension"]["scale_kg_m2"]
    gt = p["high_glucose_extension"]["threshold_mg_dl"]
    gs = p["high_glucose_extension"]["scale_mg_dl"]
    bmi_effect = np.minimum(bmi, bt) + bs * np.log1p(np.maximum(bmi - bt, 0.0) / bs)
    glucose_effect = np.minimum(glucose, gt) + gs * np.log1p(np.maximum(glucose - gt, 0.0) / gs)
    ref = p["reference"]
    beta = p["beta_age_bmi_glucose"]
    log_mu = (p["log_intercept"] + beta[0] * (age - ref["age_years"])
              + beta[1] * (bmi_effect - ref["bmi_kg_m2"])
              + beta[2] * (glucose_effect - ref["fasting_glucose_mg_dl"])
              + p["male_log_shift"] * (observed["sex"].to_numpy() == "male"))
    rng = np.random.default_rng(seed)
    out["fasting_insulin_uU_ml"] = np.exp(log_mu + rng.normal(0.0, p["log_residual_sd"], len(out)))
    return out
