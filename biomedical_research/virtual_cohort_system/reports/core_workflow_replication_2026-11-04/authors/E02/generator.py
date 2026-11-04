"""E02 whole-cohort candidate. No file/network I/O; settings come from spec."""
import math

import numpy as np
import pandas as pd


def _open_uniform(rng, limit):
    for _ in range(limit):
        value = float(rng.random())
        if 0.0 < value < 1.0:
            return value
    raise RuntimeError("Open-uniform sampler exhausted its attempt limit")


def _truncated_normal(rng, location, scale, lower, upper, limit):
    """Normal conditioned on an open interval, with bounded visible failures.

    In an exterior tail, distance y from the near endpoint (in SD units)
    has density proportional to exp(-t*y-y*y/2), 0<y<w, t>=0.
    A truncated exponential rate r=max(t,1) is an envelope after division
    by exp(M), M=max_{[0,w]}[(r-t)y-y*y/2]. The acceptance formula below
    is therefore exact in real arithmetic; no CDF tail subtraction occurs.
    """
    if not all(math.isfinite(x) for x in (location, scale, lower, upper)):
        raise FloatingPointError("Nonfinite truncated-normal parameter")
    if not scale > 0.0 or not upper > lower:
        raise ValueError("Invalid truncated-normal scale or interval")
    if lower <= location <= upper:
        for _ in range(limit):
            value = float(rng.normal(location, scale))
            if lower < value < upper:
                return value
        raise RuntimeError("Central truncated-normal sampler exhausted its limit")

    right_tail = location > upper
    endpoint = upper if right_tail else lower
    t = ((location - upper) if right_tail else (lower - location)) / scale
    width = (upper - lower) / scale
    if not math.isfinite(t) or not math.isfinite(width) or width <= 0.0:
        raise FloatingPointError("Standardized truncation geometry not representable")
    rate = max(t, 1.0)
    shift = rate - t
    peak = min(width, max(0.0, shift))
    log_envelope = shift * peak - 0.5 * peak * peak
    mass = -math.expm1(-rate * width)
    if not 0.0 < mass <= 1.0:
        raise FloatingPointError("Truncated exponential normalization not representable")
    for _ in range(limit):
        u = _open_uniform(rng, limit)
        distance = -math.log1p(-u * mass) / rate
        if not math.isfinite(distance) or not 0.0 < distance < width:
            raise FloatingPointError("Tail distance outside representable open support")
        log_acceptance = shift * distance - 0.5 * distance * distance - log_envelope
        if math.log(_open_uniform(rng, limit)) <= log_acceptance:
            value = endpoint - scale * distance if right_tail else endpoint + scale * distance
            if not lower < value < upper or not math.isfinite(value):
                raise FloatingPointError("Conditional glucose draw rounds to an endpoint; no clipping performed")
            return value
    raise RuntimeError("Tail truncated-normal sampler exhausted its attempt limit")


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError("E02 is a whole-cohort generator with no participant input")
    p = spec["parameters"]
    rng = np.random.default_rng(seed)
    limit = int(p["sampler_attempt_limit"])
    if limit < 1:
        raise ValueError("Attempt limit must be positive")
    ages, sexes = [], []
    for female in p["female_levels"]:
        for low, high in p["age_bands"]:
            ages.extend(rng.integers(low, high + 1, size=p["rows_per_cell"]).tolist())
            sexes.extend([female] * p["rows_per_cell"])
    age = np.asarray(ages, dtype=np.int64)
    female = np.asarray(sexes, dtype=np.int64)
    n = len(age)
    with np.errstate(over="raise", invalid="raise", under="ignore"):
        bmi = rng.lognormal(p["bmi_log_location"], p["bmi_log_sd"], n)
    if not np.isfinite(bmi).all() or not (bmi > 0.0).all():
        raise FloatingPointError("Positive finite BMI not representable; no resampling or cap")
    glucose = np.empty(n, dtype=float)
    for i in range(n):
        location = (p["glucose_reference_mean"]
                    + p["glucose_age_slope"] * (int(age[i]) - p["age_reference"])
                    + p["glucose_bmi_slope"] * (float(bmi[i]) - p["bmi_reference_mean"]))
        glucose[i] = _truncated_normal(
            rng, location, p["glucose_residual_sd"], p["glucose_lower"],
            p["glucose_upper"], limit)
    hba1c = np.empty(n, dtype=float)
    for i in range(n):
        mean = (p["hba1c_reference_mean"]
                + p["hba1c_age_slope"] * (int(age[i]) - p["age_reference"])
                + p["hba1c_female_slope"] * (int(female[i]) - p["female_reference"])
                + p["hba1c_bmi_slope"] * (float(bmi[i]) - p["bmi_reference_mean"])
                + p["hba1c_glucose_slope"] * (float(glucose[i]) - p["glucose_reference_mean"]))
        if not math.isfinite(mean) or mean <= 0.0:
            raise FloatingPointError("HbA1c conditional mean is not positive finite")
        log_variance = math.log1p((p["hba1c_residual_sd"] / mean) ** 2)
        if not math.isfinite(log_variance) or log_variance <= 0.0:
            raise FloatingPointError("Positive HbA1c conditional dispersion not representable")
        value = math.exp(float(rng.normal(math.log(mean) - 0.5 * log_variance,
                                          math.sqrt(log_variance))))
        if not math.isfinite(value) or value <= 0.0:
            raise FloatingPointError("Positive finite HbA1c draw not representable")
        hba1c[i] = value
    return pd.DataFrame({
        "row_id": [p["row_id_prefix"] + str(i + 1).zfill(4) for i in range(n)],
        "age": age, "female": female, "bmi": bmi,
        "glucose": glucose, "hba1c": hba1c,
    })
