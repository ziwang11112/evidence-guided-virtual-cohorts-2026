import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("whole-cohort generator expects observed=None")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    accepted = []
    count = 0
    for _ in range(p["implementation"]["max_batches"]):
        m = p["implementation"]["batch_size"]
        ag = p["age"]
        age = np.floor(ag["minimum"] + ag["width"] * rng.beta(ag["beta_alpha"], ag["beta_beta"], m))
        sx = p["female"]
        prob = sx["intercept"] + sx["age_slope"] * (age - sx["age_center"])
        female = rng.binomial(1, prob, m)
        b = p["bmi"]
        bmi_mean = (b["mean_intercept"] + b["age_rise"] * (np.minimum(age, b["age_peak"]) - b["age_center"])
                    + b["age_fall"] * np.maximum(age - b["age_peak"], 0.0) + b["female_shift"] * female)
        log_location = np.log(bmi_mean - b["shift"]) - 0.5 * b["log_sd"] ** 2
        bmi = b["shift"] + rng.lognormal(log_location, b["log_sd"], m)
        s = p["bp_surface"]
        x_age = age - s["age_center"]
        x_bmi = bmi - s["bmi_center"]
        hinge = np.maximum(age - s["age_knot"], 0.0)
        sbp_mean = (s["sbp_intercept"] + s["sbp_age"] * x_age + s["sbp_age_hinge"] * hinge
                    + (s["sbp_female"] + s["sbp_female_age"] * x_age) * female + p["bmi_slopes"]["sbp"] * x_bmi)
        dbp_mean = (s["dbp_intercept"] + s["dbp_age"] * x_age + s["dbp_age_hinge"] * hinge
                    + s["dbp_female"] * female + p["bmi_slopes"]["dbp"] * x_bmi)
        r = p["residual"]
        z = rng.standard_normal((m, 2))
        mixing = np.sqrt((r["df"] - 2.0) / rng.chisquare(r["df"], m))
        es = z[:, 0] * mixing
        ed = (r["rho"] * z[:, 0] + np.sqrt(1.0 - r["rho"] ** 2) * z[:, 1]) * mixing
        sbp_sd = r["sbp_sd"] + r["sbp_sd_age_slope"] * np.maximum(age - r["sbp_sd_age_knot"], 0.0)
        sbp = sbp_mean + sbp_sd * es
        dbp = dbp_mean + r["dbp_sd"] * ed
        e = p["eligibility"]
        keep = ((sbp >= e["sbp_min"]) & (sbp <= e["sbp_max"]) & (dbp >= e["dbp_min"]) & (dbp <= e["dbp_max"])
                & (bmi >= e["bmi_min"]) & (bmi <= e["bmi_max"]))
        if e["positive_pulse_pressure"]:
            keep = keep & (sbp > dbp)
        rows = np.column_stack((age, female, bmi, sbp, dbp))[keep]
        accepted.append(rows)
        count += len(rows)
        if count >= p["n_rows"]:
            values = np.concatenate(accepted, axis=0)[:p["n_rows"]]
            frame = pd.DataFrame(values, columns=["age", "female", "bmi", "sbp", "dbp"])
            frame["female"] = frame["female"].astype(int)
            frame.insert(0, "row_id", np.arange(1, p["n_rows"] + 1, dtype=int))
            return frame
    raise RuntimeError("bounded rejection exhausted without enough eligible rows")
