"""Source-only aggregate generator. No individual source or target data are used."""
import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    p = spec["parameters"]
    active = p["active_context"]
    if active == "development":
        raise ValueError("The development descriptor is never executable")
    context = p["contexts"][active]
    x = context["inputs"]
    n = context["n_rows"]
    rng = np.random.default_rng(seed)

    def restricted_normal(mean, sd, low, high, size, integer=False):
        value = rng.normal(mean, sd, size)
        if integer:
            value = np.rint(value)
        bad = (value < low) | (value > high)
        while np.any(bad):
            value[bad] = rng.normal(mean, sd, int(bad.sum()))
            if integer:
                value[bad] = np.rint(value[bad])
            bad = (value < low) | (value > high)
        return value.astype(int) if integer else value

    if x["age_distribution"]["kind"] == "rounded_truncated_normal":
        a = x["age_distribution"]
        age = restricted_normal(a["mean"], a["sd"], a["minimum"], a["maximum"], n, True)
    else:
        bins = x["age_distribution"]["bins"]
        counts = np.array([b[2] for b in bins], dtype=float)
        bin_index = rng.choice(len(bins), size=n, p=counts/counts.sum())
        age = np.empty(n, dtype=int)
        for k, (low, high, count) in enumerate(bins):
            use = bin_index == k
            age[use] = rng.integers(low, high+1, int(use.sum()))
    female = rng.binomial(1, x["female_probability"], n)
    m, s = x["bmi_mean"], x["bmi_sd"]
    log_variance = np.log1p((s/m)**2)
    bmi = rng.lognormal(np.log(m)-log_variance/2, np.sqrt(log_variance), n)
    glucose = restricted_normal(x["glucose_pretruncation_mean"], x["glucose_pretruncation_sd"],
                                np.nextafter(0.0, 1.0), np.nextafter(126.0, 0.0), n)
    age_feature = age.astype(float)
    if p["age_structure"] == "fixed_hinge60_half_rate":
        age_feature = age_feature - 0.5*np.maximum(age_feature-60.0, 0.0)
    expected = (x["hba1c_reference_location"] + p["location_correction"]
                + p["age_coefficient"]*(age_feature-x["age_feature_reference"])
                + p["bmi_coefficient"]*(bmi-p["bmi_reference"])
                + p["glucose_coefficient"]*(glucose-p["glucose_reference"]))
    hba1c = expected + rng.normal(0, p["residual_sd"], n)
    bad = hba1c <= 0
    if np.any(bad) and p["residual_sd"] == 0:
        raise ValueError("Nonpositive deterministic HbA1c mean under the declared domain")
    while np.any(bad):
        hba1c[bad] = expected[bad] + rng.normal(0, p["residual_sd"], int(bad.sum()))
        bad = hba1c <= 0
    return pd.DataFrame({"row_id": [f"{active}_{i+1:06d}" for i in range(n)],
                         "age": age, "female": female, "bmi": bmi,
                         "glucose": glucose, "hba1c": hba1c})
