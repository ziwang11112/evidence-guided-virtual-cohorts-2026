import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def _bounded_parameters(mean, sd):
    # Fit population moments using deterministic Gaussian quadrature.
    x, w = np.polynomial.hermite.hermgauss(64)
    x, w = np.sqrt(2.0) * x, w / np.sqrt(np.pi)
    variance = sd * sd
    def error(t):
        p = np.exp(-np.logaddexp(0.0, -(t[0] + np.exp(t[1]) * x)))
        mu = np.dot(w, p)
        var = np.dot(w, (p - mu) ** 2)
        return np.array([(mu - mean) / sd, (var - variance) / variance])
    t = np.array([math.log(mean / (1.0 - mean)), math.log(sd / (mean * (1.0 - mean)))])
    for _ in range(40):
        r = error(t)
        if np.max(np.abs(r)) < 1e-10:
            return t[0], math.exp(t[1])
        jac = np.column_stack([(error(t + np.eye(2)[j] * 1e-4) - r) / 1e-4 for j in range(2)])
        delta = np.linalg.solve(jac, r)
        step = 1.0
        for _ in range(20):
            trial = t - step * delta
            if np.linalg.norm(error(trial)) < np.linalg.norm(r):
                t = trial
                break
            step *= 0.5
        else:
            raise RuntimeError('Population-moment fitting failed')
    raise RuntimeError('Population-moment fitting did not converge')


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)
    counts = np.asarray(m['band_n'], dtype=float)
    band = rng.choice(3, size=n, p=counts / counts.sum())
    z = rng.standard_normal((n, 2))
    hb, logf = np.empty(n), np.empty(n)
    cuts = m['hb_cutpoints_g_dl']
    logcut = math.log(m['ferritin_cutoff_ug_l'])
    normal = NormalDist()
    for j in range(3):
        ix = np.flatnonzero(band == j)
        zh = z[ix, 0]
        rho = m['within_band_gaussian_rho'][j]
        zf = rho * zh + math.sqrt(1.0 - rho * rho) * z[ix, 1]
        hm, hs = m['hb_mean_g_dl'][j], m['hb_sd_g_dl'][j]
        if j < 2:
            lo, hi = (0.0 if j == 0 else cuts[0]), cuts[j]
            mu, sigma = _bounded_parameters((hm - lo) / (hi - lo), hs / (hi - lo))
            hb[ix] = lo + (hi - lo) * np.exp(-np.logaddexp(0.0, -(mu + sigma * zh)))
        else:
            gap = hm - cuts[1]
            v = math.log1p((hs / gap) ** 2)
            hb[ix] = cuts[1] + np.exp(math.log(gap) - v / 2.0 + math.sqrt(v) * zh)
        p = m['depleted_n'][j] / counts[j]
        q = normal.inv_cdf(p)
        phi = math.exp(-q * q / 2.0) / math.sqrt(2.0 * math.pi)
        A, B = -phi - q * p, phi - q * (1.0 - p)
        C = (1.0 + q * q) * p + q * phi
        D = (1.0 + q * q) * (1.0 - p) - q * phi
        d = math.log(m['ferritin_gm_ug_l'][j]) - logcut
        s = math.log(m['ferritin_gsd'][j])
        a = C + D * (A / B) ** 2
        b = -2.0 * D * d * A / (B * B)
        c = D * (d / B) ** 2 - s * s - d * d
        left = (-b + math.sqrt(b * b - 4.0 * a * c)) / (2.0 * a)
        right = (d - A * left) / B
        if left <= 0.0 or right <= 0.0:
            raise ValueError('Ferritin quantile transformation is not increasing')
        logf[ix] = logcut + np.where(zf < q, left * (zf - q), right * (zf - q))
    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'hb_g_dl': hb, 'ferritin_ug_l': np.exp(logf)}, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
