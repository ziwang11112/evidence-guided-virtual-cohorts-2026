"""Shared aggregate-evidence joint model; the controller alone executes generate."""
import numpy as np
import pandas as pd


def generate(observed, specification, seed):
    if observed is not None:
        raise ValueError("Whole-cohort generation requires observed=None")
    p = specification["parameters"]
    active = p["active_context"]
    context = p["contexts"][active]
    inp = context["inputs"]
    n = context["n_rows"]
    rng = np.random.default_rng(seed)
    maximum_rounds = p["simulation"]["maximum_rejection_rounds"]
    age_law = inp["age_distribution"]
    if age_law["kind"] == "balanced_age_sex":
        ages, sexes = [], []
        for lo, hi in age_law["bands"]:
            for sex in (0, 1):
                m = age_law["per_sex_per_band"]
                ages.append(rng.integers(lo, hi + 1, size=m))
                sexes.append(np.full(m, sex, dtype=np.int64))
        age = np.concatenate(ages)
        female = np.concatenate(sexes)
        if len(age) != n:
            raise ValueError("Balanced design and declared row count disagree")
        permutation = rng.permutation(n)
        age, female = age[permutation], female[permutation]
    else:
        female = rng.binomial(1, inp["female_probability"], n)
        if age_law["kind"] == "rounded_normal":
            age = np.empty(n, dtype=np.int64)
            remaining = np.arange(n)
            for _ in range(maximum_rounds):
                draws = np.rint(rng.normal(age_law["mean"], age_law["sd"], len(remaining))).astype(np.int64)
                accepted = (draws >= age_law["minimum"]) & (draws <= age_law["maximum"])
                age[remaining[accepted]] = draws[accepted]
                remaining = remaining[~accepted]
                if len(remaining) == 0:
                    break
            if len(remaining):
                raise RuntimeError("Age rejection cap exceeded")
        elif age_law["kind"] == "age_band_mixture":
            weights = np.asarray(age_law["unweighted_counts"], dtype=float)
            bands = age_law["bands"]
            labels = rng.choice(len(bands), n, p=weights / weights.sum())
            age = np.empty(n, dtype=np.int64)
            for j, (lo, hi) in enumerate(bands):
                remaining = np.flatnonzero(labels == j)
                if j != len(bands) - 1:
                    age[remaining] = rng.integers(lo, hi + 1, len(remaining))
                else:
                    for _ in range(maximum_rounds):
                        draws = lo + rng.geometric(age_law["last_band_geometric_probability"], len(remaining)) - 1
                        accepted = draws <= hi
                        age[remaining[accepted]] = draws[accepted]
                        remaining = remaining[~accepted]
                        if len(remaining) == 0:
                            break
                    if len(remaining):
                        raise RuntimeError("Open age-band rejection cap exceeded")
        else:
            raise ValueError("Unknown aggregate age distribution")

    ref, dep, rule = p["reference_moments"], p["covariate_dependence"], p["hba1c_rule"]
    age_variance = ref["age_sd"] ** 2
    sex_variance = ref["female_probability"] * (1 - ref["female_probability"])
    da, df = dep["bmi_per_year"], dep["bmi_female_shift"]
    ga, gf = dep["glucose_per_year"], dep["glucose_female_shift"]
    vb = ref["bmi_sd"] ** 2 - da ** 2 * age_variance - df ** 2 * sex_variance
    vg = ref["glucose_sd"] ** 2 - ga ** 2 * age_variance - gf ** 2 * sex_variance
    rho = dep["bmi_glucose_residual_correlation"]
    if vb <= 0 or vg <= 0 or abs(rho) >= 1:
        raise ValueError("Invalid reference conditional covariance")
    sb, sg = np.sqrt(vb), np.sqrt(vg)
    cov = rho * sb * sg
    pb, pg = rule["bmi_projection_age_sex_adjusted"], rule["glucose_projection_age_sex_adjusted"]
    beta_b = (pb - pg * cov / vb) / (1 - rho ** 2)
    beta_g = (pg - pb * cov / vg) / (1 - rho ** 2)
    beta_a, beta_f = rule["conditional_age_per_year"], rule["conditional_female_shift"]
    total_age = beta_a + beta_b * da + beta_g * ga
    total_sex = beta_f + beta_b * df + beta_g * gf
    explained = (total_age ** 2 * age_variance + total_sex ** 2 * sex_variance
                 + beta_b ** 2 * vb + beta_g ** 2 * vg + 2 * beta_b * beta_g * cov)
    residual_variance = ref["hba1c_sd"] ** 2 - explained
    if residual_variance <= 0:
        raise ValueError("Reference variance decomposition is not positive")
    mean_b = ref["bmi_mean"] + da * (age - ref["age_mean"]) + df * (female - ref["female_probability"])
    mean_g = ref["glucose_mean"] + ga * (age - ref["age_mean"]) + gf * (female - ref["female_probability"])
    bmi, glucose = np.empty(n), np.empty(n)
    remaining = np.arange(n)
    glucose_max = next(c["maximum"] for c in context["columns"] if c["name"] == "glucose")
    for _ in range(maximum_rounds):
        z_b, z_g = rng.normal(size=(2, len(remaining)))
        b = mean_b[remaining] + sb * z_b
        g = mean_g[remaining] + sg * (rho * z_b + np.sqrt(1 - rho ** 2) * z_g)
        accepted = (b > 0) & (g > 0) & (g <= glucose_max)
        bmi[remaining[accepted]], glucose[remaining[accepted]] = b[accepted], g[accepted]
        remaining = remaining[~accepted]
        if len(remaining) == 0:
            break
    if len(remaining):
        raise RuntimeError("Biomarker eligibility rejection cap exceeded")

    anchor = inp["hba1c_anchor"]
    anchor_b = ref["bmi_mean"] + da * (anchor["age"] - ref["age_mean"]) + df * (anchor["female_probability"] - ref["female_probability"])
    anchor_g = ref["glucose_mean"] + ga * (anchor["age"] - ref["age_mean"]) + gf * (anchor["female_probability"] - ref["female_probability"])
    mean_h = (anchor["mean"] + beta_a * (age - anchor["age"])
              + beta_f * (female - anchor["female_probability"])
              + beta_b * (bmi - anchor_b) + beta_g * (glucose - anchor_g))
    hba1c = np.empty(n)
    remaining = np.arange(n)
    for _ in range(maximum_rounds):
        h = mean_h[remaining] + rng.normal(0, np.sqrt(residual_variance), len(remaining))
        accepted = h > 0
        hba1c[remaining[accepted]] = h[accepted]
        remaining = remaining[~accepted]
        if len(remaining) == 0:
            break
    if len(remaining):
        raise RuntimeError("HbA1c positivity rejection cap exceeded")
    frame = pd.DataFrame({"row_id": [f"fictional_{active}_{seed}_{i+1:06d}" for i in range(n)],
                          "age": age, "female": female, "bmi": bmi, "glucose": glucose, "hba1c": hba1c})
    return frame[[c["name"] for c in context["columns"]]]
