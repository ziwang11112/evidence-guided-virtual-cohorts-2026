import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["n_rows"])
    a = p["age"]
    age = a["minimum"] + (a["maximum"] - a["minimum"]) * rng.beta(a["alpha"], a["beta"], n)
    female = (rng.random(n) < p["female_probability"]).astype(int)
    coords = p["coordinates"]
    x = (age - coords["age_center"]) / coords["age_scale"]
    b = p["bmi"]
    bmi_mean = b["mean_intercept"] + b["age_linear"]*x + b["age_quadratic"]*x*x + b["female"]*female
    log_sd = np.sqrt(np.log1p(b["cv"]**2))
    log_mean = np.log(bmi_mean) - log_sd**2/2
    bmi = np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rounds"]):
        if pending.size == 0:
            break
        draw = rng.lognormal(log_mean[pending], log_sd)
        valid = np.isfinite(draw) & (draw >= b["minimum"]) & (draw <= b["maximum"])
        bmi[pending[valid]] = draw[valid]
        pending = pending[~valid]
    if pending.size:
        raise RuntimeError("BMI rejection limit exceeded")
    def location(q):
        return q["intercept"]+q["age_linear"]*x+q["age_quadratic"]*x*x+(q["female"]+q["age_female"]*x)*female
    mu_s = location(p["sbp_location"])+p["bmi_sbp_per_unit"]*(bmi-coords["bmi_center"])
    mu_d = location(p["dbp_location"])+p["bmi_dbp_per_unit"]*(bmi-coords["bmi_center"])
    r = p["residual"]
    sd_s = r["sbp_base_sd"]+r["sbp_age_increment"]*np.maximum(age-r["sbp_age_threshold"],0)
    sd_d = r["dbp_base_sd"]+r["dbp_age_increment"]*np.maximum(age-r["dbp_age_threshold"],0)
    rho = r["correlation"]
    sbp, dbp = np.empty(n), np.empty(n)
    pending = np.arange(n)
    support = p["bp_support"]
    for _ in range(p["max_rounds"]):
        if pending.size == 0:
            break
        z = rng.standard_normal((pending.size,2))
        s = mu_s[pending]+sd_s[pending]*z[:,0]
        d = mu_d[pending]+sd_d[pending]*(rho*z[:,0]+np.sqrt(1-rho*rho)*z[:,1])
        valid = (np.isfinite(s)&np.isfinite(d)&(s>=support["sbp_min"])&(s<=support["sbp_max"])
                 &(d>=support["dbp_min"])&(d<=support["dbp_max"])&((s-d)>support["minimum_pulse_pressure"]))
        sbp[pending[valid]], dbp[pending[valid]] = s[valid], d[valid]
        pending = pending[~valid]
    if pending.size:
        raise RuntimeError("BP rejection limit exceeded")
    return pd.DataFrame({"row_id":np.arange(1,n+1,dtype=int),"age":age,"female":female,"bmi":bmi,"sbp":sbp,"dbp":dbp})
