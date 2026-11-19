import math
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
    if not np.all(np.isfinite(counts)) or not np.all(np.isfinite(depleted_counts)):
        raise ValueError('Counts must be finite')
    if np.any(counts <= 0) or np.any(depleted_counts <= 0) or np.any(depleted_counts >= counts):
        raise ValueError('Invalid categorical counts')
    if not np.all(np.isfinite(bounds)) or np.any(bounds <= 0) or np.any(bounds[:, 1] <= bounds[:, 0]):
        raise ValueError('Invalid hemoglobin supports')
    w = counts / counts.sum()
    p = depleted_counts / counts
    log_bounds = np.log(bounds)

    # Calibrate the triangular distribution of nonanemic log hemoglobin.
    low_means = log_bounds[:2].mean(axis=1)
    overall_hb_gm = float(m['hb_overall_geometric_mean_g_dl'])
    if not np.isfinite(overall_hb_gm) or overall_hb_gm <= 0:
        raise ValueError('Invalid hemoglobin geometric mean')
    high_mean = (np.log(overall_hb_gm) - np.dot(w[:2], low_means)) / w[2]
    high_width = log_bounds[2, 1] - log_bounds[2, 0]
    q = (high_mean - log_bounds[2, 0]) / high_width
    mode = 3.0 * q - 1.0
    if not (0.0 < mode < 1.0):
        raise ValueError('Infeasible triangular hemoglobin calibration')

    reported_gm = np.asarray(m['ferritin_reported_conditional_geometric_means_ug_l'], dtype=float)
    overall_ferritin_gm = float(m['ferritin_overall_geometric_mean_ug_l'])
    if reported_gm.shape != (3,) or not np.all(np.isfinite(reported_gm)) or np.any(reported_gm <= 0):
        raise ValueError('Invalid conditional ferritin geometric means')
    if not np.isfinite(overall_ferritin_gm) or overall_ferritin_gm <= 0:
        raise ValueError('Invalid overall ferritin geometric mean')
    conditional_log_gm = np.log(reported_gm)
    conditional_log_gm += np.log(overall_ferritin_gm) - np.dot(w, conditional_log_gm)
    threshold = float(m['ferritin_threshold_ug_l'])
    b = float(m['ferritin_replete_mean_log_distance'])
    shape = float(m['ferritin_log_distance_gamma_shape'])
    rho = float(m['within_stratum_gaussian_copula_correlation'])
    if not np.isfinite(threshold) or threshold <= 0 or not np.isfinite(b) or b <= 0:
        raise ValueError('Invalid ferritin parameters')
    if shape != 3.0:
        raise ValueError('This implementation uses the Gamma(3,1) survival function')
    if not np.isfinite(rho) or not (-1.0 < rho < 1.0):
        raise ValueError('Copula correlation must be strictly between -1 and 1')
    log_threshold = np.log(threshold)
    a = (log_threshold + (1.0 - p) * b - conditional_log_gm) / p
    if not np.all(np.isfinite(a)) or np.any(a <= 0):
        raise ValueError('Infeasible ferritin calibration')

    safety = m['numerical_safeguards']
    iterations = int(safety['gamma_inverse_bisection_iterations'])
    upper_bracket = float(safety['gamma_inverse_upper_bracket'])
    min_exponent = float(safety['minimum_exponent'])
    max_exponent = float(safety['maximum_exponent'])
    if iterations <= 0 or not np.isfinite(upper_bracket) or upper_bracket <= 0:
        raise ValueError('Invalid inverse-survival settings')
    if not (-745.0 < min_exponent < max_exponent < 710.0):
        raise ValueError('Unsafe exponent limits')

    # Independent persons, each with a bivariate Gaussian copula draw.
    group = rng.choice(3, size=n, p=w)
    z = rng.standard_normal(n)
    e = rng.standard_normal(n)
    z_f = rho * z + math.sqrt(1.0 - rho * rho) * e
    sqrt_two = math.sqrt(2.0)
    u = np.fromiter((0.5 * math.erfc(-float(x) / sqrt_two) for x in z), dtype=float, count=n)
    v = np.fromiter((0.5 * math.erfc(-float(x) / sqrt_two) for x in z_f), dtype=float, count=n)
    open_zero = np.nextafter(0.0, 1.0)
    open_one = np.nextafter(1.0, 0.0)
    u = np.clip(u, open_zero, open_one)
    v = np.clip(v, open_zero, open_one)

    log_hb = np.empty(n, dtype=float)
    for g in (0, 1):
        mask = group == g
        log_hb[mask] = log_bounds[g, 0] + (log_bounds[g, 1] - log_bounds[g, 0]) * u[mask]
    mask = group == 2
    uh = u[mask]
    triangular_quantile = np.where(
        uh <= mode,
        np.sqrt(uh * mode),
        1.0 - np.sqrt((1.0 - uh) * (1.0 - mode))
    )
    log_hb[mask] = log_bounds[2, 0] + high_width * triangular_quantile
    hb = np.exp(log_hb)
    for g in range(3):
        mask = group == g
        hb[mask] = np.clip(hb[mask], bounds[g, 0], np.nextafter(bounds[g, 1], bounds[g, 0]))

    # Invert the stratum-specific ferritin mixture CDF without altering rows.
    pg = p[group]
    depleted = v < pg
    survival_probability = np.empty(n, dtype=float)
    survival_probability[depleted] = v[depleted] / pg[depleted]
    survival_probability[~depleted] = (1.0 - v[~depleted]) / (1.0 - pg[~depleted])
    survival_probability = np.clip(survival_probability, open_zero, open_one)
    log_survival_probability = np.log(survival_probability)
    bracket_log_survival = -upper_bracket + np.log1p(upper_bracket + 0.5 * upper_bracket * upper_bracket)
    if np.any(bracket_log_survival > log_survival_probability):
        raise ValueError('Gamma inverse-survival upper bracket is too small')
    lo = np.zeros(n, dtype=float)
    hi = np.full(n, upper_bracket, dtype=float)
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        log_survival = -mid + np.log1p(mid + 0.5 * mid * mid)
        too_small = log_survival > log_survival_probability
        lo = np.where(too_small, mid, lo)
        hi = np.where(too_small, hi, mid)
    unit_gamma_distance = 0.5 * (lo + hi)
    mean_distance = np.where(depleted, a[group], b)
    distance = unit_gamma_distance * mean_distance / shape
    log_ferritin = log_threshold + np.where(depleted, -distance, distance)
    ferritin = np.exp(np.clip(log_ferritin, min_exponent, max_exponent))
    ferritin[depleted] = np.minimum(ferritin[depleted], np.nextafter(threshold, 0.0))
    ferritin[~depleted] = np.maximum(ferritin[~depleted], threshold)

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
