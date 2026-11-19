import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator requires observed=None.')
    n = spec['task']['n_rows']
    if not isinstance(n, (int, np.integer)) or isinstance(n, (bool, np.bool_)) or n < 0:
        raise ValueError('n_rows must be a nonnegative integer.')
    if not isinstance(seed, (int, np.integer)) or isinstance(seed, (bool, np.bool_)) or seed < 0:
        raise ValueError('seed must be a nonnegative integer.')
    n = int(n)
    rng = np.random.default_rng(int(seed))
    m = spec['model']

    counts = np.asarray(m['hb_group_counts'], dtype=float)
    depleted_counts = np.asarray(m['depleted_counts_by_hb_group'], dtype=float)
    if counts.shape != (3,) or depleted_counts.shape != (3,):
        raise ValueError('Exactly three Hb groups are required.')
    if not np.all(np.isfinite(counts)) or not np.all(np.isfinite(depleted_counts)):
        raise ValueError('Counts must be finite.')
    if np.any(counts <= 0) or np.any(depleted_counts <= 0) or np.any(depleted_counts >= counts):
        raise ValueError('Every Hb group must contain both depletion states.')
    weights = counts / counts.sum()
    p = depleted_counts / counts

    # Reconcile rounded conditional and overall ferritin geometric means.
    reported_gm = np.asarray(m['ferritin_group_reported_geometric_means_ug_l'], dtype=float)
    target_gm = float(m['ferritin_working_overall_geometric_mean_ug_l'])
    shift_lo, shift_hi = map(float, m['ferritin_common_rounding_shift_bracket_ug_l'])
    if reported_gm.shape != (3,) or not np.all(np.isfinite(reported_gm)):
        raise ValueError('Invalid conditional ferritin geometric means.')
    if not np.isfinite(target_gm) or target_gm <= 0:
        raise ValueError('Invalid overall ferritin geometric mean.')
    if not np.isfinite(shift_lo + shift_hi) or shift_lo > shift_hi or np.any(reported_gm + shift_lo <= 0):
        raise ValueError('Invalid rounding-reconciliation bracket.')
    target_log_gm = np.log(target_gm)
    low_value = float(np.dot(weights, np.log(reported_gm + shift_lo)))
    high_value = float(np.dot(weights, np.log(reported_gm + shift_hi)))
    if not low_value <= target_log_gm <= high_value:
        raise ValueError('Overall ferritin mean is outside the reconciliation bracket.')
    for _ in range(80):
        shift_mid = 0.5 * (shift_lo + shift_hi)
        value = float(np.dot(weights, np.log(reported_gm + shift_mid)))
        if value < target_log_gm:
            shift_lo = shift_mid
        else:
            shift_hi = shift_mid
    ferritin_group_gm = reported_gm + 0.5 * (shift_lo + shift_hi)

    # Retain the primary artifact's Hb conditional marginal distributions.
    boundary1, boundary2 = map(float, m['hb_group_boundaries_g_dl'])
    hb_min = float(m['hb_lowest_support_g_dl'])
    anemia_cut = float(m['anemia_threshold_g_dl'])
    hb_gm = float(m['hb_overall_geometric_mean_g_dl'])
    if not 0 < hb_min < boundary1 < boundary2 or boundary2 != anemia_cut:
        raise ValueError('Invalid Hb supports or anemia threshold.')
    if not np.isfinite(hb_gm) or hb_gm <= 0:
        raise ValueError('Invalid Hb geometric mean.')
    hb_log_centers = np.empty(3, dtype=float)
    hb_log_centers[0] = 0.5 * (np.log(hb_min) + np.log(boundary1))
    hb_log_centers[1] = 0.5 * (np.log(boundary1) + np.log(boundary2))
    hb_log_centers[2] = (np.log(hb_gm) - np.dot(weights[:2], hb_log_centers[:2])) / weights[2]
    upper3 = float(np.exp(2.0 * hb_log_centers[2] - np.log(boundary2)))
    if not np.isfinite(upper3) or upper3 <= boundary2:
        raise ValueError('Hb calibration gives an invalid upper support.')
    hb_lower = np.array([hb_min, boundary1, boundary2])
    hb_upper = np.array([boundary1, boundary2, upper3])

    # Retain the primary artifact's ferritin conditional marginal distributions.
    ferritin_cut = float(m['depletion_threshold_ug_l'])
    replete_lo, replete_hi = map(float, m['ferritin_replete_support_ug_l'])
    halfwidth = float(m['ferritin_depleted_log_halfwidth'])
    if not 0 < ferritin_cut == replete_lo < replete_hi:
        raise ValueError('Invalid replete ferritin support.')
    if not np.isfinite(halfwidth) or halfwidth <= 0:
        raise ValueError('Invalid depleted log halfwidth.')
    replete_log_center = 0.5 * (np.log(replete_lo) + np.log(replete_hi))
    depleted_log_center = (np.log(ferritin_group_gm) - (1.0 - p) * replete_log_center) / p
    if np.any(depleted_log_center + halfwidth >= np.log(ferritin_cut)):
        raise ValueError('A depleted support crosses the ferritin threshold.')
    if np.any(depleted_log_center[:-1] + halfwidth >= depleted_log_center[1:] - halfwidth):
        raise ValueError('This specification requires ordered, nonoverlapping depleted supports.')

    theta = float(m['within_hb_group_fgm_theta'])
    if not np.isfinite(theta) or not -1.0 < theta < 1.0:
        raise ValueError('FGM theta must be strictly between -1 and 1.')

    # Independent persons; within each person, couple conditional biomarker ranks.
    group = rng.choice(3, size=n, p=weights)
    u = rng.random(n)
    z = rng.random(n)
    a = theta * (1.0 - 2.0 * u)
    # Invert P(V <= v | U=u) = v + a*v*(1-v).
    discriminant = np.maximum((1.0 + a) ** 2 - 4.0 * a * z, 0.0)
    v = 2.0 * z / (1.0 + a + np.sqrt(discriminant))
    v = np.clip(v, 0.0, np.nextafter(1.0, 0.0))

    hb = hb_lower[group] * np.exp(u * np.log(hb_upper[group] / hb_lower[group]))
    depleted = v < p[group]
    ferritin = np.empty(n, dtype=float)
    depleted_quantile = v[depleted] / p[group[depleted]]
    ferritin[depleted] = np.exp(
        depleted_log_center[group[depleted]] + halfwidth * (2.0 * depleted_quantile - 1.0)
    )
    replete_quantile = (v[~depleted] - p[group[~depleted]]) / (1.0 - p[group[~depleted]])
    ferritin[~depleted] = replete_lo * np.exp(replete_quantile * np.log(replete_hi / replete_lo))

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
