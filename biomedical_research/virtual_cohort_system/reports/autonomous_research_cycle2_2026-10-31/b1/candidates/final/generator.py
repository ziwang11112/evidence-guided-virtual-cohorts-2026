"""Shared aggregate-evidence construction. No I/O or local execution path."""
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort mode requires observed=None")
    p = specification["parameters"]
    active = p["active_context"]
    context = p["contexts"][active]
    inputs = context["inputs"]
    columns = context["columns"]
    bounds = {x["name"]: x for x in columns}
    n = context["n_rows"]
    rng = np.random.default_rng(seed)
    design = inputs["sampling_design"]
    if design == "balanced":
        age_parts, female_parts = [], []
        for female_value in inputs["female_values"]:
            for low, high in inputs["age_bands"]:
                size = inputs["per_cell"]
                age_parts.append(rng.integers(low, high + 1, size=size))
                female_parts.append(np.full(size, female_value, dtype=int))
        age = np.concatenate(age_parts)
        female = np.concatenate(female_parts)
        if len(age) != n:
            raise ValueError("Balanced design count disagrees with context")
    else:
        support = np.arange(bounds["age"]["minimum"], bounds["age"]["maximum"] + 1)
        if design == "discrete_gaussian":
            weights = np.exp(-0.5 * ((support-inputs["age_mean"])/inputs["age_sd"])**2)
        elif design == "age_band_mixture":
            weights = np.zeros(len(support), dtype=float)
            for band in inputs["age_bands"]:
                use = (support >= band["minimum"]) & (support <= band["maximum"])
                local = np.ones(int(use.sum()))
                if band["within_band"] == "exponential":
                    local = np.exp(-(support[use]-band["minimum"])/band["decay_years"])
                elif band["within_band"] != "uniform":
                    raise ValueError("Unknown within-band age law")
                weights[use] = band["sample_count"] * local/local.sum()
        else:
            raise ValueError("Unknown sampling design")
        age = rng.choice(support, size=n, p=weights/weights.sum())
        female = rng.binomial(1, inputs["female_probability"], size=n)

    reference = p["lifelines_reference"]
    trend = p["covariate_trends"]
    coefficient = p["conditional_coefficients"]
    correlation = p["conditional_residual_correlation"]
    centered_age = age-reference["age_mean"]
    centered_female = female-reference["female_probability"]
    mean_bmi = reference["bmi_mean"] + trend["bmi_age"]*centered_age + trend["bmi_female"]*centered_female
    mean_glucose = reference["glucose_mean"] + trend["glucose_age"]*centered_age + trend["glucose_female"]*centered_female
    bmi = np.empty(n)
    glucose = np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_rounds"]):
        if len(pending) == 0:
            break
        z = rng.normal(size=(len(pending), 2))
        b = mean_bmi[pending] + coefficient["bmi_residual_sd"]*z[:, 0]
        g = mean_glucose[pending] + coefficient["glucose_residual_sd"]*(correlation*z[:, 0] + np.sqrt(1-correlation**2)*z[:, 1])
        ok = (b > 0) & (g > 0) & (g <= bounds["glucose"]["maximum"])
        bmi[pending[ok]], glucose[pending[ok]] = b[ok], g[ok]
        pending = pending[~ok]
    if len(pending):
        raise RuntimeError("Conditional covariate rejection limit reached")

    anchor = p["hba1c_references"][inputs["hba1c_reference"]]
    anchor_bmi = reference["bmi_mean"] + trend["bmi_age"]*(anchor["age"]-reference["age_mean"]) + trend["bmi_female"]*(anchor["female_probability"]-reference["female_probability"])
    anchor_glucose = reference["glucose_mean"] + trend["glucose_age"]*(anchor["age"]-reference["age_mean"]) + trend["glucose_female"]*(anchor["female_probability"]-reference["female_probability"])
    mean_hba1c = (anchor["hba1c"] + coefficient["hba1c_age"]*(age-anchor["age"])
                  + coefficient["hba1c_bmi"]*(bmi-anchor_bmi)
                  + coefficient["hba1c_glucose"]*(glucose-anchor_glucose)
                  + coefficient["hba1c_female_direct"]*(female-anchor["female_probability"]))
    hba1c = np.empty(n)
    pending = np.arange(n)
    for _ in range(p["max_rejection_rounds"]):
        if len(pending) == 0:
            break
        h = mean_hba1c[pending] + rng.normal(0, coefficient["hba1c_residual_sd"], size=len(pending))
        ok = h > 0
        hba1c[pending[ok]] = h[ok]
        pending = pending[~ok]
    if len(pending):
        raise RuntimeError("Conditional HbA1c rejection limit reached")
    order = rng.permutation(n)
    return pd.DataFrame({
        "row_id": [f"SYN-{active}-{i:06d}" for i in range(1, n+1)],
        "age": age[order].astype(int), "female": female[order].astype(int),
        "bmi": bmi[order], "glucose": glucose[order], "hba1c": hba1c[order]
    }, columns=[c["name"] for c in columns])
