import math
from statistics import NormalDist
import numpy as np
import pandas as pd

_N = NormalDist()

def _cdf_array(z):
    return np.array([_N.cdf(float(x)) for x in z], dtype=float)

def _weibull_parameters(mean, sd):
    target = math.log1p((sd / mean) ** 2)
    lo, hi = 0.15, 10.0
    for _ in range(65):
        k = (lo + hi) / 2.0
        value = math.lgamma(1.0 + 2.0 / k) - 2.0 * math.lgamma(1.0 + 1.0 / k)
        if value > target:
            lo = k
        else:
            hi = k
    k = (lo + hi) / 2.0
    return k, mean / math.gamma(1.0 + 1.0 / k)

def _log_ferritin_parameters(p, gm, gsd, threshold):
    z = _N.inv_cdf(p)
    phi = math.exp(-z * z / 2.0) / math.sqrt(2.0 * math.pi)
    left_mean = -phi - z * p
    right_mean = phi - z * (1.0 - p)
    left_second = p * (1.0 + z * z) + z * phi
    right_second = (1.0 - p) * (1.0 + z * z) - z * phi
    d = math.log(gm / threshold)
    second = math.log(gsd) ** 2 + d * d
    qa = left_second + right_second * (left_mean / right_mean) ** 2
    qb = -2.0 * right_second * d * left_mean / right_mean ** 2
    qc = right_second * (d / right_mean) ** 2 - second
    a = (-qb + math.sqrt(qb * qb - 4.0 * qa * qc)) / (2.0 * qa)
    b = (d - left_mean * a) / right_mean
    if a <= 0.0 or b <= 0.0:
        raise ValueError('Ferritin moment fit requires positive slopes')
    return z, a, b

def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)
    counts = np.asarray(m['band_n'], dtype=float)
    band = rng.choice(3, size=n, p=counts / counts.sum())
    hb = np.empty(n, dtype=float)
    ferritin = np.empty(n, dtype=float)
    lower, upper = m['hb_cutpoints_g_dl']
    threshold = m['ferritin_cutpoint_ug_l']
    eps = np.finfo(float).eps
    for j in range(3):
        idx = np.flatnonzero(band == j)
        if len(idx) == 0:
            continue
        normals = rng.standard_normal((len(idx), 2))
        zh = normals[:, 0]
        rho = m['within_band_latent_normal_correlation'][j]
        zf = rho * zh + math.sqrt(1.0 - rho * rho) * normals[:, 1]
        u = np.clip(_cdf_array(zh), eps, 1.0 - eps)
        if j == 1:
            loc = m['hb_middle_normal_location_g_dl']
            scale = m['hb_middle_normal_scale_g_dl']
            a = _N.cdf((lower - loc) / scale)
            b = _N.cdf((upper - loc) / scale)
            q = np.clip(a + (b - a) * u, eps, 1.0 - eps)
            values = loc + scale * np.array([_N.inv_cdf(float(v)) for v in q])
            hb[idx] = np.clip(values, lower, np.nextafter(upper, lower))
        else:
            t = 0 if j == 0 else 1
            k, scale = _weibull_parameters(m['hb_tail_gap_mean_g_dl'][t], m['hb_tail_gap_sd_g_dl'][t])
            if j == 0:
                floor = math.exp(-(lower / scale) ** k)
                q = floor + (1.0 - floor) * u
                values = lower - scale * (-np.log(q)) ** (1.0 / k)
                hb[idx] = np.clip(values, np.nextafter(0.0, 1.0), np.nextafter(lower, 0.0))
            else:
                hb[idx] = upper + scale * (-np.log1p(-u)) ** (1.0 / k)
        p = m['ferritin_depleted_n'][j] / counts[j]
        z, left_scale, right_scale = _log_ferritin_parameters(p, m['ferritin_gm_ug_l'][j], m['ferritin_gsd'][j], threshold)
        log_f = math.log(threshold) + np.where(zf < z, left_scale, right_scale) * (zf - z)
        ferritin[idx] = np.exp(log_f)
    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'hb_g_dl': hb, 'ferritin_ug_l': ferritin}, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
