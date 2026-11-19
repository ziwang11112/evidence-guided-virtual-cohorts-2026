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
    depleted = np.asarray(m['depleted_counts_by_stratum'], dtype=float)
    if counts.shape != (3,) or depleted.shape != (3,):
        raise ValueError('Exactly three strata are required.')
    if np.any(counts <= 0) or np.any(depleted <= 0) or np.any(depleted >= counts):
        raise ValueError('Each stratum must contain both depleted and replete women.')
    p = counts / counts.sum()
    q = depleted / counts

    # Hemoglobin: uniform on the log scale within disjoint strata.
    hb_lo = np.asarray(m['hb_lower_g_dl_by_stratum'], dtype=float)
    hb_hi_first = np.asarray(m['hb_upper_g_dl_first_two_strata'], dtype=float)
    if hb_lo.shape != (3,) or hb_hi_first.shape != (2,):
        raise ValueError('Invalid hemoglobin bounds.')
    if np.any(hb_lo <= 0) or np.any(hb_hi_first <= hb_lo[:2]):
        raise ValueError('Invalid hemoglobin bounds.')
    hb_log_lo = np.log(hb_lo)
    hb_log_hi = np.empty(3)
    hb_log_hi[:2] = np.log(hb_hi_first)
    hb_log_means_first = (hb_log_lo[:2] + hb_log_hi[:2]) / 2.0
    hb_log_mean_last = (
        np.log(float(m['hb_overall_geometric_mean_g_dl']))
        - np.dot(p[:2], hb_log_means_first)
    ) / p[2]
    hb_log_hi[2] = 2.0 * hb_log_mean_last - hb_log_lo[2]
    if hb_log_hi[2] <= hb_log_lo[2]:
        raise ValueError('Infeasible overall hemoglobin geometric mean.')

    # Ferritin stratum log means, reconciling the rounded source summaries.
    f_log_means = np.empty(3)
    f_log_means[:2] = np.log(np.asarray(
        m['ferritin_geometric_mean_ug_l_first_two_strata'], dtype=float
    ))
    f_log_means[2] = (
        np.log(float(m['ferritin_overall_geometric_mean_ug_l']))
        - np.dot(p[:2], f_log_means[:2])
    ) / p[2]
    threshold = float(m['depletion_cutoff_ug_l'])
    replete_gm = float(m['ferritin_replete_geometric_mean_ug_l'])
    replete_upper = float(m['ferritin_replete_upper_ug_l'])
    if not (0 < threshold < replete_gm < replete_upper):
        raise ValueError('Invalid ferritin component parameters.')
    log_t = np.log(threshold)
    replete_log_mean = np.log(replete_gm)
    depleted_log_mean = (f_log_means - (1.0 - q) * replete_log_mean) / q
    depleted_log_lo = 2.0 * depleted_log_mean - log_t
    if np.any(depleted_log_lo >= log_t):
        raise ValueError('Infeasible depleted-component means.')
    replete_log_span = np.log(replete_upper / threshold)
    beta_b = replete_log_span / np.log(replete_gm / threshold) - 1.0

    rng = np.random.default_rng(seed)
    group = rng.choice(3, size=n, p=p)
    u_hb = rng.random(n)
    u_f = rng.random(n)
    log_hb = hb_log_lo[group] + u_hb * (hb_log_hi[group] - hb_log_lo[group])

    # A continuous inverse conditional CDF handles both ferritin components.
    person_q = q[group]
    is_depleted = u_f < person_q
    log_f = np.empty(n, dtype=float)
    if np.any(is_depleted):
        g = group[is_depleted]
        z = u_f[is_depleted] / person_q[is_depleted]
        log_f[is_depleted] = depleted_log_lo[g] + z * (log_t - depleted_log_lo[g])
    if np.any(~is_depleted):
        z = (u_f[~is_depleted] - person_q[~is_depleted]) / (1.0 - person_q[~is_depleted])
        beta_draw = -np.expm1(np.log1p(-z) / beta_b)
        log_f[~is_depleted] = log_t + replete_log_span * beta_draw

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hb_g_dl': np.exp(log_hb),
        'ferritin_ug_l': np.exp(log_f)
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
