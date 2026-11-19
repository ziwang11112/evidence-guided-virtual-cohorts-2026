import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator requires observed=None.')
    n = spec['task']['n_rows']
    if not isinstance(n, (int, np.integer)) or n < 0:
        raise ValueError('n_rows must be a nonnegative integer.')
    if not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError('seed must be a nonnegative integer.')
    n = int(n)
    rng = np.random.default_rng(int(seed))
    m = spec['model']

    counts = np.asarray(m['hb_group_counts'], dtype=float)
    depleted_counts = np.asarray(m['depleted_counts_by_hb_group'], dtype=float)
    if counts.shape != (3,) or depleted_counts.shape != (3,):
        raise ValueError('Exactly three Hb groups are required.')
    if np.any(counts <= 0) or np.any(depleted_counts <= 0) or np.any(depleted_counts >= counts):
        raise ValueError('Each Hb group must contain both depletion states.')
    weights = counts / counts.sum()
    depletion_prob = depleted_counts / counts

    # Deterministic reconciliation of rounded source ferritin means.
    reported_gm = np.asarray(m['ferritin_group_reported_geometric_means_ug_l'], dtype=float)
    target_log_gm = np.log(float(m['ferritin_working_overall_geometric_mean_ug_l']))
    shift_lo, shift_hi = map(float, m['ferritin_common_rounding_shift_bracket_ug_l'])
    if reported_gm.shape != (3,) or shift_lo > shift_hi or np.any(reported_gm + shift_lo <= 0):
        raise ValueError('Invalid ferritin geometric means or shift bracket.')
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
    shift = 0.5 * (shift_lo + shift_hi)
    ferritin_group_gm = reported_gm + shift

    # Hb log-uniform supports, calibrated to the marginal Hb geometric mean.
    boundary1, boundary2 = map(float, m['hb_group_boundaries_g_dl'])
    anemia_cut = float(m['anemia_threshold_g_dl'])
    hb_min = float(m['hb_lowest_support_g_dl'])
    hb_overall_gm = float(m['hb_overall_geometric_mean_g_dl'])
    if not 0 < hb_min < boundary1 < boundary2 or boundary2 != anemia_cut:
        raise ValueError('Invalid Hb thresholds or support.')
    hb_log_center = np.empty(3, dtype=float)
    hb_log_center[0] = 0.5 * (np.log(hb_min) + np.log(boundary1))
    hb_log_center[1] = 0.5 * (np.log(boundary1) + np.log(boundary2))
    hb_log_center[2] = (np.log(hb_overall_gm) - np.dot(weights[:2], hb_log_center[:2])) / weights[2]
    hb_upper3 = float(np.exp(2.0 * hb_log_center[2] - np.log(boundary2)))
    if not np.isfinite(hb_upper3) or hb_upper3 <= boundary2:
        raise ValueError('Hb mean calibration gives an invalid upper support.')
    hb_lower = np.array([hb_min, boundary1, boundary2], dtype=float)
    hb_upper = np.array([boundary1, boundary2, hb_upper3], dtype=float)

    # Ferritin log-uniform components, calibrated to conditional log means.
    ferritin_cut = float(m['depletion_threshold_ug_l'])
    replete_lo, replete_hi = map(float, m['ferritin_replete_support_ug_l'])
    halfwidth = float(m['ferritin_depleted_log_halfwidth'])
    if not 0 < ferritin_cut == replete_lo < replete_hi or halfwidth <= 0:
        raise ValueError('Invalid ferritin support or log halfwidth.')
    replete_log_center = 0.5 * (np.log(replete_lo) + np.log(replete_hi))
    depleted_log_center = (np.log(ferritin_group_gm) - (1.0 - depletion_prob) * replete_log_center) / depletion_prob
    if np.any(depleted_log_center + halfwidth >= np.log(ferritin_cut)):
        raise ValueError('A depleted ferritin support crosses the depletion threshold.')
    if np.any(depleted_log_center[:-1] + halfwidth >= depleted_log_center[1:] - halfwidth):
        raise ValueError('Depleted supports must be ordered and nonoverlapping for this specification.')

    # Independent person-level draws; no realized-sample matching or reordering.
    group = rng.choice(3, size=n, p=weights)
    depleted = rng.random(n) < depletion_prob[group]
    hb_u = rng.random(n)
    hb = hb_lower[group] * np.exp(hb_u * np.log(hb_upper[group] / hb_lower[group]))
    ferritin_u = rng.random(n)
    ferritin_depleted = np.exp(depleted_log_center[group] + halfwidth * (2.0 * ferritin_u - 1.0))
    ferritin_replete = replete_lo * np.exp(ferritin_u * np.log(replete_hi / replete_lo))
    ferritin = np.where(depleted, ferritin_depleted, ferritin_replete)

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
