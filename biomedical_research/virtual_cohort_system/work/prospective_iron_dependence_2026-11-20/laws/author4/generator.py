def generate(observed, spec, seed):
    import math
    from statistics import NormalDist
    import numpy as np
    import pandas as pd

    cfg = spec['model']
    bands = spec['bands']
    if len(bands) != 3:
        raise ValueError('Exactly three Hb bands are required.')
    arrays = []
    for j, band in enumerate(bands):
        h = np.asarray(band['hb'], dtype=float)
        f = np.asarray(band['ferritin'], dtype=float)
        if h.ndim != 1 or f.ndim != 1 or len(h) != len(f):
            raise ValueError('Each band requires equal-length one-dimensional margins.')
        if not np.all(np.isfinite(h)) or not np.all(np.isfinite(f)):
            raise ValueError('Margins must be finite.')
        if np.any(f <= 0):
            raise ValueError('Ferritin must be positive for log-scale calibration.')
        if np.any(np.diff(h) < 0) or np.any(np.diff(f) < 0):
            raise ValueError('Margins must be sorted separately.')
        valid_h = ((h < 12) if j == 0 else
                   ((h >= 12) & (h < 14)) if j == 1 else (h >= 14))
        if not np.all(valid_h):
            raise ValueError('Hb values do not match their declared band.')
        arrays.append((h, f))
    n = sum(len(h) for h, f in arrays)
    if n != int(spec['task']['n_rows']):
        raise ValueError('Total margin length differs from n_rows.')

    normal = NormalDist()
    lower, upper = map(float, cfg['rho_bounds'])
    if not (0 <= lower < upper < 1):
        raise ValueError('Require 0 <= lower rho < upper rho < 1.')
    target = math.log(float(cfg['source_middle_gm_ratio']))
    if target < 0:
        raise ValueError('This primary model assumes a nonnegative source contrast.')

    def calibrate_middle(h, f):
        k = len(h)
        m = int(np.count_nonzero(h < float(cfg['middle_split_hb'])))
        # Symmetric lognormal approximation, used only if the finite middle
        # margin cannot identify the stipulated subgroup contrast.
        fallback = target / (math.log(float(cfg['source_middle_ferritin_gsd']))
                             * math.sqrt(8.0 / math.pi))
        fallback = float(np.clip(fallback, lower, upper))
        if k < 2 or m == 0 or m == k or f[0] == f[-1]:
            return fallback

        cut = normal.inv_cdf(m / k)
        nodes, weights = np.polynomial.legendre.leggauss(int(cfg['quadrature_order']))
        local_u = (nodes + 1.0) / 2.0
        u = (np.arange(k, dtype=float)[:, None] + local_u[None, :]) / k
        zf = np.fromiter((normal.inv_cdf(float(v)) for v in u.ravel()),
                         dtype=float, count=u.size).reshape(u.shape)
        qw = weights / 2.0
        logf = np.log(f)
        root2 = math.sqrt(2.0)

        def expected_log_contrast(rho):
            x = (cut - rho * zf) / math.sqrt(1.0 - rho * rho)
            p_low = np.fromiter((0.5 * math.erfc(-float(v) / root2)
                                 for v in x.ravel()),
                                dtype=float, count=x.size).reshape(x.shape)
            # Integrate over each interval of the empirical ferritin quantile
            # function. The common interval width cancels in these means.
            w_low = p_low @ qw
            w_high = 1.0 - w_low
            mean_low = float(np.dot(logf, w_low) / np.sum(w_low))
            mean_high = float(np.dot(logf, w_high) / np.sum(w_high))
            return mean_high - mean_low

        left, right = lower, upper
        if target <= expected_log_contrast(left):
            return left
        if target >= expected_log_contrast(right):
            return right
        for unused in range(int(cfg['bisection_steps'])):
            middle = (left + right) / 2.0
            if expected_log_contrast(middle) < target:
                left = middle
            else:
                right = middle
        return (left + right) / 2.0

    rho = calibrate_middle(*arrays[1])
    residual_sd = math.sqrt(1.0 - rho * rho)
    rng = np.random.default_rng(seed)
    assignments = []
    for h, f in arrays:
        k = len(h)
        if k == 0:
            assignments.append(np.empty(0, dtype=np.int64))
            continue
        ranks = pd.Series(h).rank(method='average').to_numpy(dtype=float)
        u_h = (ranks - 0.5) / k
        z_h = np.fromiter((normal.inv_cdf(float(v)) for v in u_h),
                          dtype=float, count=k)
        score = rho * z_h + residual_sd * rng.standard_normal(k)
        order = np.argsort(score, kind='mergesort')
        fe_index = np.empty(k, dtype=np.int64)
        fe_index[order] = np.arange(k, dtype=np.int64)
        if not np.array_equal(np.sort(fe_index), np.arange(k, dtype=np.int64)):
            raise RuntimeError('Invalid ferritin permutation.')
        if np.count_nonzero(f[fe_index] < 15.0) != np.count_nonzero(f < 15.0):
            raise RuntimeError('Ferritin threshold count changed.')
        assignments.append(fe_index)

    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64),
                         'fe_index': np.concatenate(assignments)},
                        columns=['row_id', 'fe_index'])
