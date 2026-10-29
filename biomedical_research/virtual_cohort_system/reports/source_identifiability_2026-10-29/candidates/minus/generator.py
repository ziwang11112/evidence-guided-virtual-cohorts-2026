import math
import numpy as np


def _normal_cdf(values):
    root_two = math.sqrt(2.0)
    return np.fromiter((0.5 * (1.0 + math.erf(float(v) / root_two)) for v in values), dtype=float, count=len(values))


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
    """Shared lognormal anchor, with a bounded male conditional-density interaction."""
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
    cv = np.asarray(p["residual_cv"])[sex]
    variance = np.log1p(cv * cv)
    z = rng.normal(size=len(observed))
    legacy = m * np.exp(z * np.sqrt(variance) - .5 * variance)

    d = p["density_interaction"]
    sign = d["sign"]
    if sign == 0:
        return _measurement(legacy, observed, p)
    if sign not in (-1, 1):
        raise ValueError("Unknown density-interaction sign")
    ap, an = d["age_positive"], d["age_negative"]
    bp, bn = d["bmi_positive"], d["bmi_negative"]
    ha = d["age_positive_weight"] * ((age >= ap[0]) & (age <= ap[1])).astype(float) - ((age >= an[0]) & (age <= an[1])).astype(float)
    hb = d["bmi_positive_weight"] * ((bmi >= bp[0]) & (bmi < bp[1])).astype(float) - ((bmi >= bn[0]) & (bmi < bn[1])).astype(float)
    yp, yn = d["tg_positive"], d["tg_negative"]
    active = (sex == 0) & (ha != 0) & (hb != 0) & (legacy > yp[0]) & (legacy < yn[1])
    if not np.any(active):
        return _measurement(legacy, observed, p)
    u = _normal_cdf(z[active])
    log_location = np.log(m[active]) - .5 * variance[active]
    sigma = np.sqrt(variance[active])
    amount = sign * d["delta"] * ha[active] * hb[active]
    low = np.full(len(u), yp[0], dtype=float)
    high = np.full(len(u), yn[1], dtype=float)
    for _ in range(d["inverse_cdf_steps"]):
        mid = .5 * (low + high)
        base_cdf = _normal_cdf((np.log(mid) - log_location) / sigma)
        kernel_cdf = np.clip((mid - yp[0]) / (yp[1] - yp[0]), 0.0, 1.0) - np.clip((mid - yn[0]) / (yn[1] - yn[0]), 0.0, 1.0)
        cdf = base_cdf + amount * kernel_cdf
        below = cdf < u
        low = np.where(below, mid, low)
        high = np.where(below, high, mid)
    legacy[active] = .5 * (low + high)
    return _measurement(legacy, observed, p)
