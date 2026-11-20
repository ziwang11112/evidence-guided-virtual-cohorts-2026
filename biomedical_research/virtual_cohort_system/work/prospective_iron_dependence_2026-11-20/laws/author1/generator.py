import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    model = spec['model']
    supplied = spec['bands']
    if len(supplied) != 3:
        raise ValueError('Exactly three Hb bands are required.')

    bands = []
    for b, item in enumerate(supplied):
        h = np.asarray(item['hb'], dtype=np.float64)
        f = np.asarray(item['ferritin'], dtype=np.float64)
        if h.ndim != 1 or f.ndim != 1 or len(h) != len(f):
            raise ValueError('Each band requires equal-length one-dimensional margins.')
        if not np.all(np.isfinite(h)) or not np.all(np.isfinite(f)):
            raise ValueError('Margins must be finite.')
        if np.any(f <= 0):
            raise ValueError('Ferritin must be positive for geometric-mean calibration.')
        if np.any(np.diff(h) < 0) or np.any(np.diff(f) < 0):
            raise ValueError('Margins must be sorted increasingly.')
        valid_h = (h < 12) if b == 0 else ((h >= 12) & (h < 14) if b == 1 else h >= 14)
        if not np.all(valid_h):
            raise ValueError('Hb values do not match their supplied band.')
        bands.append((h, f))

    n = sum(len(h) for h, f in bands)
    if n != int(spec['task']['n_rows']):
        raise ValueError('Total margin length differs from n_rows.')

    normal = NormalDist()
    score_cache = {}

    def normal_scores(k):
        if k not in score_cache:
            score_cache[k] = np.fromiter(
                (normal.inv_cdf((j + 0.5) / k) for j in range(k)),
                dtype=np.float64, count=k
            ) if k else np.empty(0, dtype=np.float64)
        return score_cache[k]

    target = math.log(float(model['source_gm_ratio']))
    upper = float(model['rho_upper'])
    if target <= 0 or not 0 < upper < 1:
        raise ValueError('This primary model requires a positive source contrast and 0 < rho_upper < 1.')

    # Source-normal approximation is used only when a finite middle-band
    # realization lacks one of the two calibration subgroups.
    fallback = target / (
        math.log(float(model['fallback_source_ferritin_gsd'])) * math.sqrt(8.0 / math.pi)
    )
    rho = min(upper, max(0.0, fallback))

    h_mid, f_mid = bands[int(model['calibration_band_index'])]
    k_mid = len(h_mid)
    n_low = int(np.count_nonzero(h_mid < float(model['calibration_hb_cut'])))
    if 0 < n_low < k_mid:
        threshold = normal.inv_cdf(n_low / k_mid)
        z_f = normal_scores(k_mid)
        log_f = np.log(f_mid)
        log_f = log_f - log_f.mean()
        sqrt_two = math.sqrt(2.0)

        def expected_log_ratio(r):
            if r == 0.0:
                return 0.0
            a = (r * z_f - threshold) / math.sqrt(1.0 - r * r)
            # P(Hb >= 13 | latent ferritin score), integrated over
            # the source-derived empirical ferritin quantile function.
            w = np.fromiter(
                (0.5 * math.erfc(-float(x) / sqrt_two) for x in a),
                dtype=np.float64, count=k_mid
            )
            v = 1.0 - w
            return float(np.dot(log_f, w) / w.sum() - np.dot(log_f, v) / v.sum())

        attainable = expected_log_ratio(upper)
        if attainable <= target:
            # Preserve the margins if a small realization cannot attain
            # the published contrast under the selected copula family.
            rho = upper
        else:
            lo, hi = 0.0, upper
            for _ in range(int(model['bisection_steps'])):
                mid = 0.5 * (lo + hi)
                if expected_log_ratio(mid) < target:
                    lo = mid
                else:
                    hi = mid
            rho = 0.5 * (lo + hi)

    rng = np.random.default_rng(seed)
    residual_sd = math.sqrt(1.0 - rho * rho)
    permutations = []
    for h, f in bands:
        k = len(h)
        if k == 0:
            permutation = np.empty(0, dtype=np.int64)
        else:
            latent_f = rho * normal_scores(k) + residual_sd * rng.standard_normal(k)
            order = np.argsort(latent_f, kind='mergesort')
            permutation = np.empty(k, dtype=np.int64)
            permutation[order] = np.arange(k, dtype=np.int64)

        if not np.array_equal(np.sort(permutation), np.arange(k, dtype=np.int64)):
            raise RuntimeError('Invalid within-band permutation.')
        if np.count_nonzero(f[permutation] < 15.0) != np.count_nonzero(f < 15.0):
            raise RuntimeError('Ferritin threshold count changed.')
        permutations.append(permutation)

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'fe_index': np.concatenate(permutations).astype(np.int64, copy=False)
    })
