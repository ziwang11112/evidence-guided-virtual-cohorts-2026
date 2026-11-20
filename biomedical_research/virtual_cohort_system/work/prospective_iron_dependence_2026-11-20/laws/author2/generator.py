def generate(observed, spec, seed):
    import math
    from statistics import NormalDist
    import numpy as np
    import pandas as pd

    model = spec['model']
    rng = np.random.default_rng(seed)
    normal = NormalDist()
    sqrt2 = math.sqrt(2.0)

    def normal_scores(k):
        return np.fromiter(
            (normal.inv_cdf((j + 0.5) / k) for j in range(k)),
            dtype=float, count=k
        )

    if len(spec['bands']) != 3:
        raise ValueError('Exactly three Hb bands are required')
    bands = []
    for band in spec['bands']:
        hb = np.asarray(band['hb'], dtype=float)
        fe = np.asarray(band['ferritin'], dtype=float)
        if hb.ndim != 1 or fe.ndim != 1 or len(hb) != len(fe):
            raise ValueError('Each band needs equal-length one-dimensional margins')
        if not np.all(np.isfinite(hb)) or not np.all(np.isfinite(fe)):
            raise ValueError('Margins must be finite')
        if np.any(fe <= 0):
            raise ValueError('Ferritin must be positive for logarithmic calibration')
        if np.any(np.diff(hb) < 0) or np.any(np.diff(fe) < 0):
            raise ValueError('Margins must be sorted in increasing order')
        bands.append((hb, fe))

    total = sum(len(hb) for hb, fe in bands)
    if total != int(spec['task']['n_rows']):
        raise ValueError('Band lengths do not match n_rows')

    target = math.log(float(model['conditional_gm_ratio']))
    rho_lo = float(model['rho_min'])
    rho_hi = float(model['rho_max'])
    if not (0.0 <= rho_lo < rho_hi < 1.0) or target < 0.0:
        raise ValueError('Invalid positive-dependence calibration parameters')

    # Fallback: balanced Hb subgroups and approximately lognormal ferritin.
    rho = target / (
        math.log(float(model['fallback_middle_ferritin_gsd']))
        * math.sqrt(8.0 / math.pi)
    )
    rho = min(rho_hi, max(rho_lo, rho))

    mid_hb, mid_fe = bands[1]
    k_mid = len(mid_hb)
    if k_mid >= 2:
        p_lower = float(np.mean(mid_hb < float(model['hb_split'])))
        log_fe = np.log(mid_fe)
        if 0.0 < p_lower < 1.0 and np.ptp(log_fe) > 0.0:
            cut = normal.inv_cdf(p_lower)
            z_fe = normal_scores(k_mid)

            # Midpoint quadrature over ferritin latent-normal quantiles.
            # P(Hb in upper subgroup | ferritin latent score = z).
            def expected_log_ratio(r):
                t = (r * z_fe - cut) / math.sqrt(1.0 - r * r)
                upper = np.fromiter(
                    (0.5 * math.erfc(-float(v) / sqrt2) for v in t),
                    dtype=float, count=k_mid
                )
                lower = 1.0 - upper
                return float(
                    np.dot(upper, log_fe) / upper.sum()
                    - np.dot(lower, log_fe) / lower.sum()
                )

            low_value = expected_log_ratio(rho_lo)
            high_value = expected_log_ratio(rho_hi)
            if target <= low_value:
                rho = rho_lo
            elif target >= high_value:
                rho = rho_hi
            else:
                left, right = rho_lo, rho_hi
                for _ in range(int(model['bisection_iterations'])):
                    middle = 0.5 * (left + right)
                    if expected_log_ratio(middle) < target:
                        left = middle
                    else:
                        right = middle
                rho = 0.5 * (left + right)

    residual_sd = math.sqrt(1.0 - rho * rho)
    permutations = []
    for hb, fe in bands:
        k = len(hb)
        if k == 0:
            permutation = np.empty(0, dtype=np.int64)
        else:
            hb_scores = normal_scores(k)
            ferritin_scores = rho * hb_scores + residual_sd * rng.standard_normal(k)
            order = np.argsort(ferritin_scores, kind='mergesort')
            permutation = np.empty(k, dtype=np.int64)
            permutation[order] = np.arange(k, dtype=np.int64)
            if not np.array_equal(np.sort(permutation), np.arange(k, dtype=np.int64)):
                raise RuntimeError('Invalid within-band permutation')
            if np.count_nonzero(fe[permutation] < 15.0) != np.count_nonzero(fe < 15.0):
                raise RuntimeError('Ferritin threshold count changed')
        permutations.append(permutation)

    indices = np.concatenate(permutations)
    return pd.DataFrame({
        'row_id': np.arange(total, dtype=np.int64),
        'fe_index': indices.astype(np.int64, copy=False)
    }, columns=['row_id', 'fe_index'])
