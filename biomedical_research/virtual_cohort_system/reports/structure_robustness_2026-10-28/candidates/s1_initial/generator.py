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
    """Positive additive conditional arithmetic mean with multiplicative noise."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    reference = p["reference"]
    m = np.asarray(reference["tg_mean"])[sex]
    m = m + p["bmi_slope"] * (bmi - np.asarray(reference["bmi_mean"])[sex])
    m = m + np.asarray(p["age_slope"])[sex] * (age - np.asarray(reference["age_mean"])[sex])
    regular = p["positive_mean"]
    m = regular["floor"] + regular["width"] * np.logaddexp(0, (m - regular["floor"]) / regular["width"])
    cv = np.asarray(p["residual_cv"])[sex]
    variance = np.log1p(cv * cv)
    legacy = m * np.exp(rng.normal(size=len(observed)) * np.sqrt(variance) - .5 * variance)
    return _measurement(legacy, observed, p)
