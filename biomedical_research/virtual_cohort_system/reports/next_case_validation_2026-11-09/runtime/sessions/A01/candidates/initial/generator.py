import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation expects observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = p["n_rows"]
    decade = rng.choice(len(p["age_decade_starts"]), size=n, p=p["age_decade_probabilities"])
    age = np.asarray(p["age_decade_starts"])[decade] + rng.integers(p["age_decade_width"], size=n)
    female = (rng.random(n) < np.asarray(p["female_probabilities"])[decade]).astype(int)
    bm = (p["bmi_mean_at40_male"] + p["bmi_age_slope"]*(age-p["bmi_age_center"])
          + p["bmi_postknot_slope_change"]*np.maximum(age-p["bmi_decline_knot"],0)
          + p["bmi_female_difference"]*female)
    excess = bm-p["bmi_floor"]
    shape = (excess/p["bmi_conditional_sd"])**2
    scale = p["bmi_conditional_sd"]**2/excess
    bmi = np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_passes"]):
        if pending.size == 0:
            break
        draw = p["bmi_floor"] + rng.gamma(shape[pending], scale[pending])
        good = np.isfinite(draw) & (draw <= p["bmi_maximum"])
        bmi[pending[good]] = draw[good]
        pending = pending[~good]
    if pending.size:
        raise RuntimeError("BMI rejection limit reached")
    ax = age-p["bp_age_center"]
    bx = bmi-p["bp_bmi_center"]
    ms = (p["sbp_intercept"] + p["sbp_age_slope"]*ax + p["sbp_bmi_slope"]*bx
          + female*(p["sbp_female_difference_at50"]+p["sbp_female_age_interaction"]*ax))
    md = (p["dbp_intercept"] + p["dbp_age_slope_before"]*(np.minimum(age,p["dbp_age_knot"])-p["bp_age_center"])
          + p["dbp_age_slope_after"]*np.maximum(age-p["dbp_age_knot"],0)
          + p["dbp_female_difference"]*female + p["dbp_bmi_slope"]*bx)
    ss = p["sbp_residual_sd_at20"]+p["sbp_residual_sd_age_slope"]*(age-p["residual_age_center"])
    sd = p["dbp_residual_sd_at20"]+p["dbp_residual_sd_age_slope"]*(age-p["residual_age_center"])
    rho = p["residual_correlation"]
    sbp, dbp = np.empty(n), np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_passes"]):
        if pending.size == 0:
            break
        z = rng.standard_normal((2, pending.size))
        s = ms[pending]+ss[pending]*z[0]
        d = md[pending]+sd[pending]*(rho*z[0]+np.sqrt(1-rho*rho)*z[1])
        good = (np.isfinite(s) & np.isfinite(d) & (s >= p["sbp_limits"][0])
                & (s <= p["sbp_limits"][1]) & (d >= p["dbp_limits"][0])
                & (d <= p["dbp_limits"][1]) & (s > d))
        sbp[pending[good]], dbp[pending[good]] = s[good], d[good]
        pending = pending[~good]
    if pending.size:
        raise RuntimeError("BP rejection limit reached")
    return pd.DataFrame({"row_id":np.arange(1,n+1), "age":age, "female":female,
                         "bmi":bmi, "sbp":sbp, "dbp":dbp})
