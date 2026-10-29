import numpy as np


def _measurement(legacy, observed, p):
    regime = observed["tg_assay"].to_numpy()
    valid = (regime == "legacy_proxy") | (regime == "unblanked_2021_2023")
    if not np.all(valid):
        raise ValueError("Unknown measurement regime")
    result = observed.copy(deep=True)
    assay = p["assay"]
    result["tg_mg_dl"] = np.where(regime == "unblanked_2021_2023", assay["intercept"] + assay["slope"] * legacy, legacy)
    return result


def generate(observed, spec, seed):
    """Age/BMI-dependent latent state with separate gamma TG components."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    reference = p["reference"]
    eta = np.asarray(p["state_intercept"])[sex].copy()
    eta += np.asarray(p["state_bmi_slope"])[sex] * (bmi - np.asarray(reference["bmi_mean"])[sex])
    eta += np.asarray(p["state_age_slope"])[sex] * (age - np.asarray(reference["age_mean"])[sex])
    probability = np.exp(-np.logaddexp(0, -eta))
    state = (rng.random(len(observed)) < probability).astype(int)
    means = np.asarray(p["component_mean"])[sex, state]
    cv = np.asarray(p["component_cv"])[sex, state]
    shape = 1 / (cv * cv)
    legacy = rng.gamma(shape, means / shape)
    return _measurement(legacy, observed, p)
