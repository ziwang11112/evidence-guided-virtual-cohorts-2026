import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = p["n_rows"]
    a = p["age_distribution"]
    age = a["low"] + a["width"] * rng.beta(a["alpha"], a["beta"], n)
    f = p["female_probability"]
    female = rng.binomial(1, f["at50"] + f["per_year"] * (age-50.0), n)
    b = p["bmi_distribution"]
    bmi_mean = b["mean_at50_male"] + b["per_year"]*(age-50.0) + b["female_difference"]*female + b["late_quadratic"]*np.maximum(age-b["late_knot"],0.0)**2
    positive_mean = bmi_mean-b["shift"]
    shape = positive_mean**2/b["sd"]**2
    scale = b["sd"]**2/positive_mean
    bmi = np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_rounds"]):
        if pending.size == 0:
            break
        draw = b["shift"] + rng.gamma(shape[pending], scale[pending])
        ok = (draw < b["upper"]) & np.isfinite(draw)
        bmi[pending[ok]] = draw[ok]
        pending = pending[~ok]
    if pending.size:
        raise RuntimeError("BMI rejection limit exceeded")
    s = p["sbp_location"]
    d = p["dbp_location"]
    mu_s = s["intercept"] + s["age_linear"]*(age-s["age_center"]) + s["hinge_slope"]*np.maximum(age-s["hinge_knot"],0.0) + (s["female_at50"]+s["female_age_slope"]*(age-s["age_center"]))*female + p["bmi_sbp_slope"]*(bmi-s["bmi_center"])
    mu_d = d["intercept"] + d["age_linear"]*(age-d["age_center"]) + d["hinge_slope"]*np.maximum(age-d["hinge_knot"],0.0) + d["female"]*female + p["bmi_dbp_slope"]*(bmi-d["bmi_center"])
    r = p["residual_distribution"]
    sd_s = r["sbp_sd_base"] + r["sbp_sd_slope"]*np.maximum(age-r["sbp_sd_knot"],0.0)
    sd_d = r["dbp_sd_base"] + r["dbp_sd_slope"]*np.maximum(age-r["dbp_sd_knot"],0.0)
    lim = p["selection"]
    sbp, dbp = np.empty(n), np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_rounds"]):
        if pending.size == 0:
            break
        k = pending.size
        z = rng.normal(size=(k,2))
        mixing = np.sqrt((r["df"]-2.0)/rng.chisquare(r["df"], k))
        es = z[:,0]*mixing
        ed = (r["rho"]*z[:,0]+np.sqrt(1.0-r["rho"]**2)*z[:,1])*mixing
        ds = mu_s[pending]+sd_s[pending]*es
        dd = mu_d[pending]+sd_d[pending]*ed
        ok = np.isfinite(ds) & np.isfinite(dd) & (ds>=lim["sbp_min"]) & (ds<=lim["sbp_max"]) & (dd>=lim["dbp_min"]) & (dd<=lim["dbp_max"])
        if lim["positive_pulse_pressure"]:
            ok = ok & (ds>dd)
        sbp[pending[ok]], dbp[pending[ok]] = ds[ok], dd[ok]
        pending = pending[~ok]
    if pending.size:
        raise RuntimeError("BP rejection limit exceeded")
    return pd.DataFrame({"row_id":np.arange(1,n+1),"age":age,"female":female,"bmi":bmi,"sbp":sbp,"dbp":dbp},columns=["row_id","age","female","bmi","sbp","dbp"])
