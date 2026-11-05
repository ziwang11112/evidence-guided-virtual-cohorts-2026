"""Reviewed L01 finite-moment whole-cohort law. Execution belongs to the harness."""
import math
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = specification["parameters"]
    output = p["output"]
    n = int(output["n_rows"])
    rng = np.random.default_rng(seed)
    female = rng.random(n) < p["female_probability"]

    rank = p["copula"]["source_spearman"]
    age_cor = p["copula"]["age_latent_correlations"]
    r_bt = 2.0 * math.sin(math.pi * rank["bmi_tc"] / 6.0)
    r_bh = 2.0 * math.sin(math.pi * rank["bmi_hdl"] / 6.0)
    r_th = 2.0 * math.sin(math.pi * rank["tc_hdl"] / 6.0)
    correlation = np.array([
        [1.0, age_cor["bmi"], age_cor["tc"], age_cor["hdl"]],
        [age_cor["bmi"], 1.0, r_bt, r_bh],
        [age_cor["tc"], r_bt, 1.0, r_th],
        [age_cor["hdl"], r_bh, r_th, 1.0],
    ])
    latent = rng.standard_normal((n, 4)) @ np.linalg.cholesky(correlation).T
    uniforms = np.fromiter(
        (0.5 * (1.0 + math.erf(float(z) / math.sqrt(2.0))) for z in latent[:, 0]),
        dtype=float, count=n,
    )
    age = np.interp(uniforms, p["age"]["probability_knots"], p["age"]["value_knots_years"])

    bmi_mean = np.where(female, p["bmi"]["F"]["mean"], p["bmi"]["M"]["mean"])
    bmi_sd = np.where(female, p["bmi"]["F"]["sd"], p["bmi"]["M"]["sd"])
    bmi_variance_log = np.log1p((bmi_sd / bmi_mean) ** 2)
    bmi = np.exp(np.log(bmi_mean) - 0.5 * bmi_variance_log + np.sqrt(bmi_variance_log) * latent[:, 1])

    lipids = {}
    for key, score in (("tc", 2), ("hdl", 3)):
        settings = p["lipids"][key]
        proportion_female = p["female_probability"]
        ratio = settings["female_male_ratio"]
        mean_m = settings["pooled_mean"] / ((1.0 - proportion_female) + proportion_female * ratio)
        mean_f = ratio * mean_m
        between = proportion_female * (1.0 - proportion_female) * (mean_f - mean_m) ** 2
        squared_means = (1.0 - proportion_female) * mean_m ** 2 + proportion_female * mean_f ** 2
        variance_log = math.log1p((settings["pooled_sd"] ** 2 - between) / squared_means)
        row_mean = np.where(female, mean_f, mean_m)
        lipids[key] = np.exp(np.log(row_mean) - 0.5 * variance_log + math.sqrt(variance_log) * latent[:, score])

    sex = np.where(female, output["sex_codes"][1], output["sex_codes"][0])
    identifiers = [output["id_prefix"] + str(i + 1).zfill(output["id_width"]) for i in range(n)]
    # The positional schema is bound to the task; no post hoc lipid clipping or redraw.
    data = dict(zip(output["columns"], (identifiers, age, sex, bmi, lipids["tc"], lipids["hdl"])))
    return pd.DataFrame(data, columns=output["columns"])
