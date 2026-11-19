import math
from statistics import NormalDist
import numpy as np
import pandas as pd

_N = NormalDist()

def _Phi(x):
    a = np.asarray(x, dtype=float)
    return np.fromiter((0.5 * math.erfc(-float(t) / math.sqrt(2)) for t in a.ravel()), dtype=float, count=a.size).reshape(a.shape)

def _weibull_params(mean, sd):
    target = (sd / mean) ** 2
    lo, hi = 0.15, 20.0
    for _ in range(65):
        k = (lo + hi) / 2
        cv2 = math.expm1(math.lgamma(1 + 2 / k) - 2 * math.lgamma(1 + 1 / k))
        if cv2 > target:
            lo = k
        else:
            hi = k
    k = (lo + hi) / 2
    return k, mean / math.gamma(1 + 1 / k)

def _bounded_probit_params(mean, sd, lower, upper):
    q = (mean - lower) / (upper - lower)
    target = (sd / (upper - lower)) ** 2
    nodes, weights = np.polynomial.hermite.hermgauss(40)
    lo, hi = 0.0, 8.0
    for _ in range(50):
        b = (lo + hi) / 2
        a = math.sqrt(1 + b * b) * _N.inv_cdf(q)
        variance = np.dot(weights, (_Phi(a + math.sqrt(2) * b * nodes) - q) ** 2) / math.sqrt(math.pi)
        if variance < target:
            lo = b
        else:
            hi = b
    b = (lo + hi) / 2
    return math.sqrt(1 + b * b) * _N.inv_cdf(q), b

def _ferritin_slopes(gm, gsd, p, threshold):
    c = _N.inv_cdf(p)
    density = math.exp(-c * c / 2) / math.sqrt(2 * math.pi)
    A = -density - c * p
    B = density - c * (1 - p)
    C = (1 + c * c) * p + c * density
    D = (1 + c * c) * (1 - p) - c * density
    m = math.log(gm / threshold)
    second = math.log(gsd) ** 2 + m * m
    target = m / math.sqrt(second)
    lo, hi = 1e-6, 1e6
    for _ in range(85):
        ratio = (lo + hi) / 2
        value = (A * ratio + B) / math.sqrt(C * ratio * ratio + D)
        if value > target:
            lo = ratio
        else:
            hi = ratio
    ratio = (lo + hi) / 2
    right = math.sqrt(second / (C * ratio * ratio + D))
    return c, ratio * right, right

def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)
    counts = np.asarray(m['hb_band_counts'], dtype=float)
    band = rng.choice(3, size=n, p=counts / counts.sum())
    zh = rng.standard_normal(n)
    error = rng.standard_normal(n)
    hb = np.empty(n, dtype=float)
    ferritin = np.empty(n, dtype=float)
    lower_cut, upper_cut = m['hb_cutpoints_g_dl']
    threshold = m['ferritin_cutpoint_ug_l']
    for j in range(3):
        ix = np.flatnonzero(band == j)
        if ix.size == 0:
            continue
        z = zh[ix]
        u = np.clip(_Phi(z), 1e-14, 1 - 1e-14)
        mean = m['hb_band_means_g_dl'][j]
        sd = m['hb_band_sds_g_dl'][j]
        if j == 0:
            k, scale = _weibull_params(lower_cut - mean, sd)
            floor = math.exp(-(lower_cut / scale) ** k)
            hb[ix] = lower_cut - scale * (-np.log(floor + (1 - floor) * u)) ** (1 / k)
        elif j == 1:
            a, b = _bounded_probit_params(mean, sd, lower_cut, upper_cut)
            hb[ix] = lower_cut + (upper_cut - lower_cut) * _Phi(a + b * z)
        else:
            k, scale = _weibull_params(mean - upper_cut, sd)
            hb[ix] = upper_cut + scale * (-np.log1p(-u)) ** (1 / k)
        rho = m['within_band_gaussian_copula_rho'][j]
        zf = rho * z + math.sqrt(1 - rho * rho) * error[ix]
        p = m['ferritin_depleted_counts'][j] / counts[j]
        c, left, right = _ferritin_slopes(m['ferritin_geometric_means'][j], m['ferritin_geometric_sds'][j], p, threshold)
        logf = math.log(threshold) + np.where(zf < c, left, right) * (zf - c)
        ferritin[ix] = np.exp(logf)
    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'hb_g_dl': hb, 'ferritin_ug_l': ferritin})
