"""Request B: fixed scientific assumptions; isolated execution only."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("whole_cohort requires observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    n = int(p["n_rows"])
    age = rng.integers(p["age"]["minimum"], p["age"]["maximum"] + 1, size=n)
    female = rng.binomial(1, p["female_probability"], size=n)
    ac = age - p["age"]["center"]
    bp = p["bmi"]
    bmi = bp["shift"] + rng.lognormal(np.log(bp["excess_median"]) + bp["age_log_slope"] * ac + bp["female_log_shift"] * female, bp["log_sd"], size=n)
    bc = bmi - bp["center"]
    ep = p["elevated_component"]
    pr = ep["reference_probability"]
    logit = np.log(pr / (1 - pr)) + ep["age_logit_slope"] * ac + ep["bmi_logit_slope"] * bc
    elevated = rng.binomial(1, 1 / (1 + np.exp(-logit)), size=n)
    shared = rng.standard_normal(n)
    independent = rng.standard_normal(n)
    rho = np.asarray(p["conditional_normal_correlation"])[elevated]
    hscore = rho * shared + np.sqrt(1 - rho * rho) * independent
    gp = p["serum_components"]
    gm = np.asarray(gp["mean"])[elevated]
    gs = np.asarray(gp["sd"])[elevated]
    glogsd = np.sqrt(np.log1p((gs / gm) ** 2))
    glucose = np.exp(np.log(gm) - 0.5 * glogsd ** 2 + gp["age_log_slope"] * ac + glogsd * shared) * (1 + gp["bmi_linear_slope"] * bc)
    hp = p["hba1c_components"]
    hm = np.asarray(hp["mean"])[elevated]
    hs = np.asarray(hp["sd"])[elevated]
    hlogsd = np.sqrt(np.log1p((hs / hm) ** 2))
    hba1c = np.exp(np.log(hm) - 0.5 * hlogsd ** 2 + hp["age_log_slope"] * ac + hp["female_log_shift"] * female + hlogsd * hscore) * (1 + hp["bmi_linear_slope"] * bc)
    mp = p["meal"]
    meal_sd = np.sqrt(np.log1p((mp["sd_increment"] / mp["mean_increment"]) ** 2))
    meal = rng.binomial(1, mp["probability"], size=n) * rng.lognormal(np.log(mp["mean_increment"]) - 0.5 * meal_sd ** 2, meal_sd, size=n)
    glucose = glucose + meal
    dec = int(p["round_decimals"])
    return pd.DataFrame({"person_id": [f"B{i+1:05d}" for i in range(n)], "age": age, "female": female, "bmi": np.round(bmi, dec), "hba1c": np.round(hba1c, dec), "glucose": np.round(glucose, dec)})
