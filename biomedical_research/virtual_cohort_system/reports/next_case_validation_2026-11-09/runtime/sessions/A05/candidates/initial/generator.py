"""A05 assumption-explicit joint BP generator; no external inputs or side effects."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = p["n_rows"]
    lo, hi = p["age_limits"]
    age = lo + (hi - lo) * rng.beta(*p["age_beta"], size=n)
    a = (age - p["age_center"]) / p["age_scale"]
    logit = p["female_logit"][0] + p["female_logit"][1] * a
    female = rng.binomial(1, 1 / (1 + np.exp(-logit)), size=n)
    c = p["bmi_log_median"]
    log_median = c[0] + c[1] * a + c[2] * a * a + c[3] * female
    bmi = np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_rounds"]):
        if len(pending) == 0:
            break
        proposal = np.exp(log_median[pending] + p["bmi_log_sd"] * rng.normal(size=len(pending)))
        good = (proposal >= p["bmi_limits"][0]) & (proposal <= p["bmi_limits"][1])
        bmi[pending[good]] = proposal[good]
        pending = pending[~good]
    if len(pending):
        raise RuntimeError("BMI conditional rejection exhausted")
    x = bmi - p["bmi_center"]
    cs, cd = p["sbp_location"], p["dbp_location"]
    mu_s = cs[0] + cs[1] * a + cs[2] * a * a + cs[3] * female + p["bmi_slopes_per1"][0] * x
    mu_d = cd[0] + cd[1] * a + cd[2] * a * a + cd[3] * female + p["bmi_slopes_per1"][1] * x
    sd_s = p["sbp_residual_scale"][0] + p["sbp_residual_scale"][1] * (age - lo)
    rho = p["conditional_residual_rho"]
    orthogonal_scale = np.sqrt(1 - rho * rho)
    sbp, dbp = np.empty(n), np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_rounds"]):
        if len(pending) == 0:
            break
        z = rng.normal(size=(len(pending), 2))
        s = mu_s[pending] + sd_s[pending] * z[:, 0]
        d = mu_d[pending] + p["dbp_residual_sd"] * (rho * z[:, 0] + orthogonal_scale * z[:, 1])
        good = (s >= p["sbp_limits"][0]) & (s <= p["sbp_limits"][1]) & (d >= p["dbp_limits"][0]) & (d <= p["dbp_limits"][1])
        if p["require_sbp_above_dbp"]:
            good &= s > d
        sbp[pending[good]], dbp[pending[good]] = s[good], d[good]
        pending = pending[~good]
    if len(pending):
        raise RuntimeError("BP conditional rejection exhausted")
    return pd.DataFrame({"row_id": np.arange(1, n + 1), "age": age, "female": female,
                         "bmi": bmi, "sbp": sbp, "dbp": dbp},
                        columns=["row_id", "age", "female", "bmi", "sbp", "dbp"])
