import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    # Only the supplied source-derived margins and model parameters are used.
    m = spec['model']
    raw_bands = spec['bands']
    if len(raw_bands) != 3:
        raise ValueError('Exactly three Hb bands are required')
    bands = []
    for j, b in enumerate(raw_bands):
        h = np.asarray(b['hb'], dtype=float)
        f = np.asarray(b['ferritin'], dtype=float)
        if h.ndim != 1 or f.ndim != 1 or len(h) != len(f):
            raise ValueError('Each band must contain equal-length one-dimensional margins')
        if not np.all(np.isfinite(h)) or not np.all(np.isfinite(f)) or np.any(f <= 0):
            raise ValueError('Margins must be finite and ferritin must be positive')
        if np.any(np.diff(h) < 0) or np.any(np.diff(f) < 0):
            raise ValueError('Margins must be sorted')
        if j == 0 and np.any(h >= 12.0):
            raise ValueError('Invalid first Hb band')
        if j == 1 and np.any((h < 12.0) | (h >= 14.0)):
            raise ValueError('Invalid middle Hb band')
        if j == 2 and np.any(h < 14.0):
            raise ValueError('Invalid third Hb band')
        bands.append((h, f))
    n = sum(len(h) for h, f in bands)
    if n != int(spec['task']['n_rows']):
        raise ValueError('n_rows does not match supplied margins')

    nd = NormalDist()
    target = math.log(float(m['middle_band_gm_ratio']))
    cap = float(m['rho_ceiling'])
    if target < 0 or not 0 < cap < 1:
        raise ValueError('This primary model requires a ratio >= 1 and 0 < rho_ceiling < 1')

    # Source-only fallback: Gaussian/lognormal approximation to the middle band.
    # For a lower-group fraction q, the conditional log-mean difference is
    # sigma_logF * rho * phi(Phi^-1(q)) / (q * (1-q)).
    q0 = float(m['fallback_lower_fraction'])
    sigma0 = math.log(float(m['fallback_middle_ferritin_gsd']))
    if not 0 < q0 < 1 or sigma0 <= 0:
        raise ValueError('Invalid fallback parameters')
    c0 = nd.inv_cdf(q0)
    phi0 = math.exp(-0.5 * c0 * c0) / math.sqrt(2.0 * math.pi)
    rho = min(cap, max(0.0, target * q0 * (1.0 - q0) / (sigma0 * phi0)))

    # Calibrate the shared copula parameter using the source-derived middle
    # margins. Midpoint quadrature predicts the difference in conditional
    # means of log ferritin across Hb 13 under a Gaussian copula.
    hm, fm = bands[1]
    k = len(hm)
    if k >= 2:
        q = float(np.count_nonzero(hm < float(m['middle_band_hb_split']))) / k
        logf = np.log(fm)
        if 0 < q < 1 and float(np.std(logf)) > 1e-12:
            cut = nd.inv_cdf(q)
            yf = np.fromiter((nd.inv_cdf((i + 0.5) / k) for i in range(k)), dtype=float, count=k)

            def contrast(r):
                den = math.sqrt(1.0 - r * r)
                plow = np.fromiter((nd.cdf((cut - r * y) / den) for y in yf), dtype=float, count=k)
                pup = 1.0 - plow
                return float(np.dot(logf, pup) / np.sum(pup) - np.dot(logf, plow) / np.sum(plow))

            if target == 0:
                rho = 0.0
            elif contrast(cap) < target:
                rho = cap
            else:
                lo, hi = 0.0, cap
                for _ in range(int(m['bisection_steps'])):
                    mid = 0.5 * (lo + hi)
                    if contrast(mid) < target:
                        lo = mid
                    else:
                        hi = mid
                rho = 0.5 * (lo + hi)

    # Stochastic rank pairing preserves every supplied marginal value.
    rng = np.random.default_rng(seed)
    fe_index = np.empty(n, dtype=np.int64)
    offset = 0
    residual_scale = math.sqrt(1.0 - rho * rho)
    for h, f in bands:
        k = len(h)
        if k:
            # Average-rank normal scores handle possible Hb ties.
            _, starts, counts = np.unique(h, return_index=True, return_counts=True)
            u = np.repeat((starts + 0.5 * counts) / k, counts)
            x = np.fromiter((nd.inv_cdf(float(v)) for v in u), dtype=float, count=k)
            latent_f = rho * x + residual_scale * rng.standard_normal(k)
            order = np.argsort(latent_f, kind='mergesort')
            perm = np.empty(k, dtype=np.int64)
            perm[order] = np.arange(k, dtype=np.int64)
            fe_index[offset:offset + k] = perm
        offset += k

    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'fe_index': fe_index})
