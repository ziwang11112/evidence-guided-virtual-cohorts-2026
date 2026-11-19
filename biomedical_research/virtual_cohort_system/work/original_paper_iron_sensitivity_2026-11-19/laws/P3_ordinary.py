import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator requires observed=None.')
    n = spec['task']['n_rows']
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError('n_rows must be a nonnegative integer.')
    n = int(n)
    m = spec['model']

    counts = np.asarray(m['stratum_counts'], dtype=float)
    depleted_counts = np.asarray(m['depleted_counts_by_stratum'], dtype=float)
    if counts.shape != (3,) or depleted_counts.shape != (3,):
        raise ValueError('Exactly three strata are required.')
    if not np.all(np.isfinite(counts)) or not np.all(np.isfinite(depleted_counts)):
        raise ValueError('Counts must be finite.')
    if np.any(counts <= 0) or np.any(depleted_counts <= 0) or np.any(depleted_counts >= counts):
        raise ValueError('Each stratum must contain depleted and replete women.')
    p = counts / counts.sum()
    q = depleted_counts / counts

    theta = float(m['within_stratum_fgm_theta'])
    if not np.isfinite(theta) or not (-1.0 < theta < 1.0):
        raise ValueError('FGM theta must be strictly between -1 and 1.')

    # Hemoglobin marginal quantiles within the three strata.
    hb_lo = np.asarray(m['hb_lower_g_dl_by_stratum'], dtype=float)
    hb_hi_first = np.asarray(m['hb_upper_g_dl_first_two_strata'], dtype=float)
    if hb_lo.shape != (3,) or hb_hi_first.shape != (2,):
        raise ValueError('Invalid hemoglobin bounds.')
    if not np.all(np.isfinite(hb_lo)) or not np.all(np.isfinite(hb_hi_first)):
        raise ValueError('Hemoglobin bounds must be finite.')
    if np.any(hb_lo <= 0) or np.any(hb_hi_first <= hb_lo[:2]):
        raise ValueError('Invalid hemoglobin bounds.')
    anemia_cutoff = float(m['anemia_cutoff_g_dl'])
    if not (hb_hi_first[0] == hb_lo[1] and hb_hi_first[1] == hb_lo[2] == anemia_cutoff):
        raise ValueError('Hemoglobin strata must be contiguous and respect the anemia cutoff.')
    hb_gm = float(m['hb_overall_geometric_mean_g_dl'])
    if not np.isfinite(hb_gm) or hb_gm <= 0:
        raise ValueError('Invalid hemoglobin geometric mean.')
    hb_log_lo = np.log(hb_lo)
    hb_log_hi = np.empty(3, dtype=float)
    hb_log_hi[:2] = np.log(hb_hi_first)
    first_hb_log_means = (hb_log_lo[:2] + hb_log_hi[:2]) / 2.0
    last_hb_log_mean = (np.log(hb_gm) - np.dot(p[:2], first_hb_log_means)) / p[2]
    hb_log_hi[2] = 2.0 * last_hb_log_mean - hb_log_lo[2]
    if hb_log_hi[2] <= hb_log_lo[2]:
        raise ValueError('Infeasible marginal hemoglobin geometric mean.')

    # Reconcile the rounded ferritin geometric means on the log scale.
    f_gm_first = np.asarray(m['ferritin_geometric_mean_ug_l_first_two_strata'], dtype=float)
    f_gm = float(m['ferritin_overall_geometric_mean_ug_l'])
    if f_gm_first.shape != (2,) or not np.all(np.isfinite(f_gm_first)) or np.any(f_gm_first <= 0):
        raise ValueError('Invalid conditional ferritin geometric means.')
    if not np.isfinite(f_gm) or f_gm <= 0:
        raise ValueError('Invalid marginal ferritin geometric mean.')
    f_log_means = np.empty(3, dtype=float)
    f_log_means[:2] = np.log(f_gm_first)
    f_log_means[2] = (np.log(f_gm) - np.dot(p[:2], f_log_means[:2])) / p[2]

    threshold = float(m['depletion_cutoff_ug_l'])
    replete_gm = float(m['ferritin_replete_geometric_mean_ug_l'])
    replete_upper = float(m['ferritin_replete_upper_ug_l'])
    if not (0 < threshold < replete_gm < replete_upper < np.inf):
        raise ValueError('Invalid ferritin component parameters.')
    log_t = np.log(threshold)
    depleted_log_mean = (f_log_means - (1.0 - q) * np.log(replete_gm)) / q
    depleted_log_lo = 2.0 * depleted_log_mean - log_t
    if np.any(depleted_log_lo >= log_t):
        raise ValueError('Infeasible depleted-component geometric means.')
    replete_log_span = np.log(replete_upper / threshold)
    beta_b = replete_log_span / np.log(replete_gm / threshold) - 1.0

    rng = np.random.default_rng(seed)
    group = rng.choice(3, size=n, p=p)
    u = rng.random(n)
    w = rng.random(n)

    # Invert P(V <= v | U=u) = v + theta*(1-2*u)*v*(1-v).
    # The rationalized quadratic root is stable when theta*(1-2*u) is near zero.
    k = theta * (1.0 - 2.0 * u)
    discriminant = (1.0 + k) ** 2 - 4.0 * k * w
    v = 2.0 * w / (1.0 + k + np.sqrt(np.maximum(discriminant, 0.0)))
    v = np.clip(v, 0.0, np.nextafter(1.0, 0.0))

    log_hb = hb_log_lo[group] + u * (hb_log_hi[group] - hb_log_lo[group])
    person_q = q[group]
    is_depleted = v < person_q
    log_f = np.empty(n, dtype=float)
    if np.any(is_depleted):
        g = group[is_depleted]
        z = v[is_depleted] / person_q[is_depleted]
        log_f[is_depleted] = depleted_log_lo[g] + z * (log_t - depleted_log_lo[g])
    if np.any(~is_depleted):
        z = (v[~is_depleted] - person_q[~is_depleted]) / (1.0 - person_q[~is_depleted])
        z = np.clip(z, 0.0, np.nextafter(1.0, 0.0))
        beta_draw = -np.expm1(np.log1p(-z) / beta_b)
        log_f[~is_depleted] = log_t + replete_log_span * beta_draw

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hb_g_dl': np.exp(log_hb),
        'ferritin_ug_l': np.exp(log_f)
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
