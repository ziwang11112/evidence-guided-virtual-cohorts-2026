import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('observed must be None')
    n = spec['task']['n_rows']
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError('n_rows must be a nonnegative integer')
    n = int(n)
    m = spec['model']
    rng = np.random.default_rng(seed)

    counts = np.asarray(m['hb_stratum_counts'], dtype=float)
    depleted_counts = np.asarray(m['depleted_counts_by_hb_stratum'], dtype=float)
    bounds = np.asarray(m['hb_strata_g_dl'], dtype=float)
    if counts.shape != (3,) or depleted_counts.shape != (3,) or bounds.shape != (3, 2):
        raise ValueError('Expected three hemoglobin strata')
    if np.any(counts <= 0) or np.any(depleted_counts <= 0) or np.any(depleted_counts >= counts):
        raise ValueError('Invalid stratum counts')
    if np.any(bounds <= 0) or np.any(bounds[:, 1] <= bounds[:, 0]):
        raise ValueError('Invalid hemoglobin supports')
    w = counts / counts.sum()
    p_dep = depleted_counts / counts
    log_bounds = np.log(bounds)

    # Analytically calibrate the nonanemic log-hemoglobin mean.
    low_group_log_means = log_bounds[:2].mean(axis=1)
    overall_log_hb = np.log(float(m['hb_overall_geometric_mean_g_dl']))
    high_group_log_mean = (overall_log_hb - np.dot(w[:2], low_group_log_means)) / w[2]
    beta_mean = (high_group_log_mean - log_bounds[2, 0]) / (log_bounds[2, 1] - log_bounds[2, 0])
    concentration = float(m['hb_nonanemic_log_beta_concentration'])
    if not (0 < beta_mean < 1) or concentration <= 0:
        raise ValueError('Infeasible hemoglobin geometric-mean calibration')
    alpha = concentration * beta_mean
    beta = concentration * (1.0 - beta_mean)

    # Reconcile rounded conditional and overall ferritin geometric means.
    reported_gm = np.asarray(m['ferritin_reported_conditional_geometric_means_ug_l'], dtype=float)
    overall_gm = float(m['ferritin_overall_geometric_mean_ug_l'])
    if reported_gm.shape != (3,) or np.any(reported_gm <= 0) or overall_gm <= 0:
        raise ValueError('Invalid ferritin geometric means')
    conditional_log_gm = np.log(reported_gm)
    conditional_log_gm += np.log(overall_gm) - np.dot(w, conditional_log_gm)
    threshold = float(m['ferritin_threshold_ug_l'])
    b = float(m['ferritin_replete_mean_log_distance'])
    shape = float(m['ferritin_log_distance_gamma_shape'])
    if threshold <= 0 or b <= 0 or shape <= 0:
        raise ValueError('Invalid ferritin parameters')
    log_threshold = np.log(threshold)
    a = (log_threshold + (1.0 - p_dep) * b - conditional_log_gm) / p_dep
    if np.any(a <= 0):
        raise ValueError('Infeasible ferritin geometric-mean calibration')

    # Every row is drawn independently; category totals are not fixed.
    group = rng.choice(3, size=n, p=w)
    depleted = rng.random(n) < p_dep[group]
    log_hb = np.empty(n, dtype=float)
    for g in (0, 1):
        mask = group == g
        log_hb[mask] = rng.uniform(log_bounds[g, 0], log_bounds[g, 1], size=int(mask.sum()))
    mask = group == 2
    z = rng.beta(alpha, beta, size=int(mask.sum()))
    log_hb[mask] = log_bounds[2, 0] + (log_bounds[2, 1] - log_bounds[2, 0]) * z
    hb = np.exp(log_hb)
    for g in range(3):
        mask = group == g
        hb[mask] = np.clip(hb[mask], bounds[g, 0], np.nextafter(bounds[g, 1], bounds[g, 0]))

    mean_distance = np.where(depleted, a[group], b)
    distance = rng.gamma(shape=shape, scale=mean_distance / shape, size=n)
    log_ferritin = log_threshold + np.where(depleted, -distance, distance)
    ferritin = np.exp(np.clip(log_ferritin, -700.0, 700.0))
    ferritin[depleted] = np.minimum(ferritin[depleted], np.nextafter(threshold, 0.0))
    ferritin[~depleted] = np.maximum(ferritin[~depleted], threshold)

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
