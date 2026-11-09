"""External-evidence developmental cohort; no host execution at submission."""

import math

import numpy as np
import pandas as pd


def _lognormal_parameters(mean, sd):
    variance = math.log1p((sd / mean) ** 2)
    return math.log(mean) - variance / 2.0, math.sqrt(variance)


def _lipid_parameters(parameters, female_probability):
    """Preserve specified pooled moments under the assumed sex mixture."""
    ratio = parameters["female_male_geometric_mean_ratio"]
    mean = parameters["pooled_arithmetic_mean"]
    sd = parameters["pooled_sd"]
    h1 = 1.0 - female_probability + female_probability * ratio
    h2 = 1.0 - female_probability + female_probability * ratio ** 2
    variance = math.log((1.0 + (sd / mean) ** 2) * h1 ** 2 / h2)
    if variance <= 0.0:
        raise ValueError("Sex mixture leaves no positive lipid residual variance")
    return math.log(mean / h1) - variance / 2.0, math.sqrt(variance), math.log(ratio)


def _assessment(frame, specification):
    """Executed only with the generator in the isolated worker; no I/O."""
    rules = specification["analysis"]
    n = len(frame)
    numeric_names = ["age", "bmi", "total_cholesterol", "hdl_cholesterol"]
    numbers = frame[numeric_names].to_numpy(dtype=float)
    finite = np.isfinite(numbers).all(axis=1)
    eligible = (
        finite
        & (numbers[:, 0] >= specification["age"]["minimum"])
        & (numbers[:, 1:] > 0.0).all(axis=1)
        & frame["sex"].isin(["F", "M"]).to_numpy()
        & frame["id"].map(lambda value: isinstance(value, str) and bool(value)).to_numpy()
    )
    invalid_count = int((~eligible).sum())
    d = frame.loc[eligible]
    count = len(d)
    diagnostics = {}
    for name in numeric_names:
        values = d[name].to_numpy(dtype=float)
        if name in ["total_cholesterol", "hdl_cholesterol"]:
            values = values * rules["lipids_mmol_L_to_mg_dL"]
        diagnostics[name + ".mean"] = float(values.mean()) if count else None
        diagnostics[name + ".sd_sample"] = float(values.std(ddof=1)) if count > 1 else None
        for label, q in [("q10", 0.1), ("q50", 0.5), ("q90", 0.9)]:
            diagnostics[name + "." + label] = (
                float(np.quantile(values, q, method=rules["quantile_method"])) if count else None
            )
    diagnostics["sex.F_fraction"] = float((d["sex"] == "F").mean()) if count else None
    design = np.column_stack([
        np.ones(count),
        (d["age"].to_numpy(dtype=float) - rules["age_center"]) / rules["age_scale"],
        (d["sex"] == "F").to_numpy(dtype=float),
        (d["bmi"].to_numpy(dtype=float) - rules["bmi_center"]) / rules["bmi_scale"],
    ])
    rank = int(np.linalg.matrix_rank(design)) if count else 0
    analysis_results = {goal: None for goal in rules["goal_ids"]}
    noncomputable = []
    residuals = {}
    bmi_residual_sd = None
    if count > 3:
        bmi = d["bmi"].to_numpy(dtype=float)
        bmi_residual = bmi - design[:, :3] @ np.linalg.lstsq(design[:, :3], bmi, rcond=None)[0]
        bmi_residual_sd = float(bmi_residual.std(ddof=1))
    if rank == 4 and count > 4:
        for name, goal in [
            ("hdl_cholesterol", "K02-HDL-BMI"),
            ("total_cholesterol", "K02-TC-BMI"),
        ]:
            values = d[name].to_numpy(dtype=float) * rules["lipids_mmol_L_to_mg_dL"]
            coefficients = np.linalg.lstsq(design, values, rcond=None)[0]
            residual = values - design @ coefficients
            residuals[name] = residual
            diagnostics[name + ".conditional_rms"] = float(np.sqrt(np.mean(residual ** 2)))
            analysis_results[goal] = float(coefficients[3] * rules["bmi_contrast"] / rules["bmi_scale"])
        tc = residuals["total_cholesterol"]
        hdl = residuals["hdl_cholesterol"]
        tc = tc - tc.mean()
        hdl = hdl - hdl.mean()
        denominator = math.sqrt(float(tc @ tc) * float(hdl @ hdl))
        if denominator > 0.0:
            analysis_results["K02-LIPID-RESIDUAL"] = float(tc @ hdl) / denominator
        else:
            noncomputable.append("K02-LIPID-RESIDUAL: zero residual variance")
    else:
        noncomputable.append("All regression goals: design rank below 4 or insufficient rows")
        diagnostics["total_cholesterol.conditional_rms"] = None
        diagnostics["hdl_cholesterol.conditional_rms"] = None
    subgroups = {}
    for sex in ["F", "M"]:
        group = d.loc[d["sex"] == sex]
        subgroups[sex] = {"n": len(group)}
        for name in numeric_names:
            values = group[name].to_numpy(dtype=float)
            subgroups[sex][name] = {
                "min": float(values.min()) if len(group) else None,
                "max": float(values.max()) if len(group) else None,
                "sd_sample": float(values.std(ddof=1)) if len(group) > 1 else None,
            }
    tails = {}
    for name in numeric_names:
        values = d[name].to_numpy(dtype=float)
        tails[name] = {
            "min": float(values.min()) if count else None,
            "q01": float(np.quantile(values, 0.01, method=rules["quantile_method"])) if count else None,
            "q99": float(np.quantile(values, 0.99, method=rules["quantile_method"])) if count else None,
            "max": float(values.max()) if count else None,
        }
    return {
        "scope": "Numerical checks of this fictional draw, not source or target validation",
        "schema": {
            "exact_columns": list(frame.columns) == specification["columns"],
            "row_count": n,
            "requested_row_count": specification["n_rows"],
            "invalid_rows": invalid_count,
            "duplicate_ids": int(frame["id"].duplicated().sum()),
            "eligible_rows": count,
        },
        "diagnostics": diagnostics,
        "analysis_results": analysis_results,
        "design_rank": rank,
        "design_condition_number": float(np.linalg.cond(design)) if rank == 4 else None,
        "bmi_after_age_sex_sd_sample": bmi_residual_sd,
        "same_rows_and_design_for_both_lipids": True,
        "tc_less_than_hdl_rows": int((d["total_cholesterol"] < d["hdl_cholesterol"]).sum()),
        "subgroups_in_delivered_units": subgroups,
        "tails_in_delivered_units": tails,
        "noncomputable": noncomputable,
    }


def generate(observed, specification, seed):
    """Return exactly the requested table; attach worker-only descriptive checks."""
    if observed is not None:
        raise ValueError("This whole-cohort law expects observed=None")
    n = int(specification["n_rows"])
    if n != 3000:
        raise ValueError("This submitted contract requires exactly 3000 rows")
    rng = np.random.default_rng(seed)
    p = specification["composition"]["female_probability"]
    female = rng.random(n) < p
    dependence = specification["dependence"]
    r = dependence["source_spearman"]
    bt = 2.0 * math.sin(math.pi * r["bmi_total_cholesterol"] / 6.0)
    bh = 2.0 * math.sin(math.pi * r["bmi_hdl_cholesterol"] / 6.0)
    th = 2.0 * math.sin(math.pi * r["total_cholesterol_hdl_cholesterol"] / 6.0)
    a = dependence["assumed_age_latent_correlations"]
    correlation = np.array([
        [1.0, a["bmi"], a["total_cholesterol"], a["hdl_cholesterol"]],
        [a["bmi"], 1.0, bt, bh],
        [a["total_cholesterol"], bt, 1.0, th],
        [a["hdl_cholesterol"], bh, th, 1.0],
    ])
    latent = rng.standard_normal((n, 4)) @ np.linalg.cholesky(correlation).T
    age_spec = specification["age"]
    age = age_spec["minimum"] + age_spec["median_excess"] / math.log(2.0) * np.logaddexp(
        0.0, latent[:, 0] / age_spec["softplus_shape"]
    )
    bmi = np.empty(n)
    for sex, mask in [("F", female), ("M", ~female)]:
        parameters = specification["bmi"][sex]
        mu, sigma = _lognormal_parameters(parameters["arithmetic_mean"], parameters["sd"])
        bmi[mask] = np.exp(mu + sigma * latent[mask, 1])
    lipids = {}
    for name, index in [("total_cholesterol", 2), ("hdl_cholesterol", 3)]:
        mu, sigma, difference = _lipid_parameters(specification["lipids"][name], p)
        lipids[name] = np.exp(mu + difference * female + sigma * latent[:, index])
    frame = pd.DataFrame({
        "id": [specification["identifier_prefix"] + str(i + 1).zfill(6) for i in range(n)],
        "age": age,
        "sex": np.where(female, "F", "M"),
        "bmi": bmi,
        "total_cholesterol": lipids["total_cholesterol"],
        "hdl_cholesterol": lipids["hdl_cholesterol"],
    }, columns=specification["columns"])
    frame.attrs["developmental_assessment"] = _assessment(frame, specification)
    return frame
