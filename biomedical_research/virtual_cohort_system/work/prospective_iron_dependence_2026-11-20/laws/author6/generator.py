import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    # observed is deliberately unused: calibration uses source-reconstructed margins only.
    model = spec['model']
    supplied = spec['bands']
    if len(supplied) != 3:
        raise ValueError('Exactly three Hb bands are required')

    bands = []
    for b in supplied:
        hb = np.asarray(b['hb'], dtype=float)
        fe = np.asarray(b['ferritin'], dtype=float)
        if hb.ndim != 1 or fe.ndim != 1 or hb.size != fe.size:
            raise ValueError('Each band must contain equally sized one-dimensional margins')
        if not np.all(np.isfinite(hb)) or not np.all(np.isfinite(fe)):
            raise ValueError('Margins must be finite')
        if np.any(fe <= 0):
            raise ValueError('Ferritin must be positive for log-scale calibration')
        if np.any(np.diff(hb) < 0) or np.any(np.diff(fe) < 0):
            raise ValueError('Input margins must be sorted')
        bands.append((hb, fe))

    total = sum(hb.size for hb, fe in bands)
    if total != int(spec['task']['n_rows']):
        raise ValueError('n_rows does not match supplied margins')

    normal = NormalDist()
    def normal_scores(n):
        return np.fromiter(
            (normal.inv_cdf((j + 0.5) / n) for j in range(n)),
            dtype=float, count=n
        )

    lower, upper = map(float, model['rho_bounds'])
    target = math.log(float(model['middle_ferritin_gm_ratio']))
    mid_hb, mid_fe = bands[1]
    n_mid = mid_hb.size
    split = int(np.searchsorted(mid_hb, float(model['middle_hb_split']), side='left'))

    if 0 < split < n_mid:
        p_low = split / n_mid
        z_cut = normal.inv_cdf(p_low)
        z_fe = normal_scores(n_mid)
        log_fe = np.log(mid_fe)

        def expected_contrast(r):
            # Conditional lower-Hb probability at each ferritin normal score.
            scale = math.sqrt(1.0 - r * r)
            arguments = (z_cut - r * z_fe) / scale
            weights_low = np.fromiter(
                (0.5 * math.erfc(-float(v) / math.sqrt(2.0)) for v in arguments),
                dtype=float, count=n_mid
            )
            weights_high = 1.0 - weights_low
            low_mean = float(np.dot(weights_low, log_fe) / weights_low.sum())
            high_mean = float(np.dot(weights_high, log_fe) / weights_high.sum())
            return high_mean - low_mean

        at_lower = expected_contrast(lower)
        at_upper = expected_contrast(upper)
        if target <= at_lower:
            rho = lower
        elif target >= at_upper:
            rho = upper
        else:
            lo, hi = lower, upper
            for _ in range(int(model['calibration_steps'])):
                center = (lo + hi) / 2.0
                if expected_contrast(center) < target:
                    lo = center
                else:
                    hi = center
            rho = (lo + hi) / 2.0
    else:
        # Source-lognormal approximation if a realized middle margin lacks either subgroup.
        # At a median split, the normal-score mean difference is sqrt(8/pi).
        log_sd = math.log(float(model['fallback_middle_ferritin_gsd']))
        approximate_rho = target / (log_sd * math.sqrt(8.0 / math.pi))
        rho = min(upper, max(lower, approximate_rho))

    rng = np.random.default_rng(seed)
    residual_scale = math.sqrt(1.0 - rho * rho)
    permutations = []
    for hb, fe in bands:
        n = hb.size
        if n == 0:
            permutations.append(np.empty(0, dtype=np.int64))
            continue
        z_hb = normal_scores(n)
        score = rho * z_hb + residual_scale * rng.standard_normal(n)
        order = np.argsort(score, kind='mergesort')
        permutation = np.empty(n, dtype=np.int64)
        permutation[order] = np.arange(n, dtype=np.int64)
        if not np.array_equal(np.sort(permutation), np.arange(n, dtype=np.int64)):
            raise RuntimeError('Invalid ferritin permutation')
        permutations.append(permutation)

    return pd.DataFrame({
        'row_id': np.arange(total, dtype=np.int64),
        'fe_index': np.concatenate(permutations).astype(np.int64, copy=False)
    }, columns=['row_id', 'fe_index'])
