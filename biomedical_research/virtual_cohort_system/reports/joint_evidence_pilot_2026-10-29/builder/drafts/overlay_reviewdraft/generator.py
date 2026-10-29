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


def _joint_log_departure(age, bmi, sex, settings):
    """Bilinear source interaction surface; clamped at assumed support knots."""
    ages = np.asarray(settings["age_knots"], dtype=float)
    bmis = np.asarray(settings["bmi_knots"], dtype=float)
    logs = np.log(np.asarray(settings["relative_differences"], dtype=float))
    departure = logs - logs[:, :, :1] - logs[:, :1, :] + logs[:, :1, :1]
    a = np.clip(age, ages[0], ages[-1])
    b = np.clip(bmi, bmis[0], bmis[-1])
    ai = np.clip(np.searchsorted(ages, a, side="right") - 1, 0, len(ages) - 2)
    bi = np.clip(np.searchsorted(bmis, b, side="right") - 1, 0, len(bmis) - 2)
    wa = (a - ages[ai]) / (ages[ai + 1] - ages[ai])
    wb = (b - bmis[bi]) / (bmis[bi + 1] - bmis[bi])
    lower = (1 - wb) * departure[sex, ai, bi] + wb * departure[sex, ai, bi + 1]
    upper = (1 - wb) * departure[sex, ai + 1, bi] + wb * departure[sex, ai + 1, bi + 1]
    return settings["transfer_fraction"] * ((1 - wa) * lower + wa * upper)


def generate(observed, spec, seed):
    """Inherited positive mean times one source-derived interaction departure."""
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    sex = observed["sex"].to_numpy(dtype=int) - 1
    age = observed["age"].to_numpy(dtype=float)
    bmi = observed["bmi"].to_numpy(dtype=float)
    reference = p["reference"]
    m = np.asarray(reference["tg_mean"])[sex]
    m = m + np.asarray(p["bmi_slope"])[sex] * (bmi - np.asarray(reference["bmi_mean"])[sex])
    m = m + np.asarray(p["age_slope"])[sex] * (age - np.asarray(reference["age_mean"])[sex])
    regular = p["positive_mean"]
    m = regular["floor"] + regular["width"] * np.logaddexp(0, (m - regular["floor"]) / regular["width"])
    m = m * np.exp(_joint_log_departure(age, bmi, sex, p["joint_interaction"]))
    cv = np.asarray(p["residual_cv"])[sex]
    variance = np.log1p(cv * cv)
    legacy = m * np.exp(rng.normal(size=len(observed)) * np.sqrt(variance) - .5 * variance)
    return _measurement(legacy, observed, p)
