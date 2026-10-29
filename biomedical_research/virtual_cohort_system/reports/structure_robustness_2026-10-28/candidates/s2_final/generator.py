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
    """Nonlinear multiplicative log-location model with saturation."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    reference = p["reference"]
    dx = bmi - np.asarray(reference["bmi_mean"])[sex]
    w = p["bmi_saturation_width"]
    log_location = np.log(np.asarray(p["reference_median"])[sex])
    log_location += np.asarray(p["log_bmi_slope"])[sex] * w * np.tanh(dx / w)
    female_age = p["female_age"]
    transition = 1 / (1 + np.exp(-(age - female_age["midpoint"]) / female_age["width"]))
    age_effect = np.where(sex == 1, female_age["amplitude"] * (transition - female_age["source_center"]), p["male_log_age_slope"] * (age - reference["age_mean"][0]))
    log_location += age_effect
    log_sd = np.asarray(p["residual_log_sd"])[sex]
    legacy = np.exp(log_location + log_sd * rng.normal(size=len(observed)))
    return _measurement(legacy, observed, p)
