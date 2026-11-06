import numpy as np
import pandas as pd


_BAND_COUNTS = np.array([53, 205, 1413])
_LOW_FERRITIN = np.array([50, 123, 331]) / _BAND_COUNTS
_LOG_GEOMEANS = np.log([1.3, 5.9, 22.3])
_LOG_CUTOFF = np.log(15.0)
_LOGISTIC_SCALE = 0.48


def _ferritin_locations():
    # Solve the mean log concentration under the imposed low-ferritin fractions.
    left = np.full(3, -4.0)
    right = np.full(3, 8.0)
    for _ in range(48):
        loc = (left + right) / 2
        cut = 1 / (1 + np.exp((loc - _LOG_CUTOFF) / _LOGISTIC_SCALE))
        integral = cut * np.log(cut) + (1 - cut) * np.log1p(-cut)
        low_mean = loc + _LOGISTIC_SCALE * integral / cut
        high_mean = loc - _LOGISTIC_SCALE * integral / (1 - cut)
        projected = _LOW_FERRITIN * low_mean + (1 - _LOW_FERRITIN) * high_mean
        left = np.where(projected < _LOG_GEOMEANS, loc, left)
        right = np.where(projected < _LOG_GEOMEANS, right, loc)
    return (left + right) / 2


def _hemoglobin(bands, rng):
    hb = np.empty(len(bands))
    rank = np.empty(len(bands))

    severe = bands == 0
    rank[severe] = rng.random(severe.sum())
    hb[severe] = 4 + 6 * rank[severe] ** 0.2

    moderate = bands == 1
    rank[moderate] = rng.random(moderate.sum())
    hb[moderate] = 10 + 2 * np.sqrt(rank[moderate])

    upper = bands == 2
    excess = rng.gamma(3.0, 1.0, upper.sum())
    hb[upper] = 12 + 0.46 * excess
    rank[upper] = 1 - np.exp(-excess) * (1 + excess + excess ** 2 / 2)
    return hb, rank


def _ferritin(bands, hb_rank, rng):
    p = _LOW_FERRITIN
    # Match the low-ferritin probability at the 12 g/dL boundary.
    last_theta = (p[1] - p[1] * (1 - p[1]) - p[2]) / (p[2] * (1 - p[2]))
    theta = np.array([1.0, 1.0, last_theta])[bands]
    a = theta * (1 - 2 * hb_rank)
    r = rng.random(len(bands))
    # Invert the conditional FGM copula CDF r = v + a*v*(1-v).
    disc = np.maximum((1 + a) ** 2 - 4 * a * r, 0)
    denom = np.maximum(1 + a + np.sqrt(disc), np.finfo(float).tiny)
    rank = np.clip(2 * r / denom, np.finfo(float).eps, 1 - np.finfo(float).eps)

    loc = _ferritin_locations()[bands]
    cut = 1 / (1 + np.exp((loc - _LOG_CUTOFF) / _LOGISTIC_SCALE))
    low_p = p[bands]
    low = rank < low_p
    logit = np.empty(len(bands))
    low_cdf = cut[low] * rank[low] / low_p[low]
    logit[low] = np.log(low_cdf) - np.log1p(-low_cdf)
    high_surv = (1 - cut[~low]) * (1 - rank[~low]) / (1 - low_p[~low])
    logit[~low] = np.log1p(-high_surv) - np.log(high_surv)
    return np.exp(loc + _LOGISTIC_SCALE * logit)


def generate(n, rng, context):
    if context not in ("zhu_source", "target"):
        raise ValueError("Expected zhu_source or target")
    bands = rng.choice(3, size=n, p=_BAND_COUNTS / _BAND_COUNTS.sum())
    hb, hb_rank = _hemoglobin(bands, rng)
    ferritin = _ferritin(bands, hb_rank, rng)
    return pd.DataFrame({"hb_g_dl": hb, "ferritin_ug_l": ferritin})
