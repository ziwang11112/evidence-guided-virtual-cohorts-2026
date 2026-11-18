import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This whole-cohort generator expects observed=None.')
    m = spec['model']
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative.')

    c = m['source_counts']
    total = int(c['n'])
    cell_sum = sum(int(c[k]) for k in ('both_low', 'only_hb_low', 'only_ferritin_low', 'neither_low'))
    if total <= 0 or cell_sum != total:
        raise ValueError('Invalid source contingency table.')
    p_h = (c['both_low'] + c['only_hb_low']) / total
    p_f = (c['both_low'] + c['only_ferritin_low']) / total
    p_joint = c['both_low'] / total
    if not (0.0 < p_h < 1.0 and 0.0 < p_f < 1.0):
        raise ValueError('Interior marginal probabilities are required.')

    normal = NormalDist()
    h = normal.inv_cdf(p_h)
    k = normal.inv_cdf(p_f)

    # Plackett's identity integrates the bivariate normal density over rho.
    cop = m['copula']
    nodes, weights = np.polynomial.legendre.leggauss(int(cop['quadrature_nodes']))

    def joint_probability(rho):
        if rho == 0.0:
            return p_h * p_f
        r = 0.5 * rho * (nodes + 1.0)
        denom = 1.0 - r * r
        density = np.exp(-(h*h - 2.0*r*h*k + k*k) / (2.0*denom)) / (2.0*math.pi*np.sqrt(denom))
        return p_h*p_f + 0.5*rho*float(np.dot(weights, density))

    lo, hi = (float(x) for x in cop['rho_search_interval'])
    if not (-1.0 < lo < hi < 1.0):
        raise ValueError('Invalid correlation search interval.')
    if not (joint_probability(lo) <= p_joint <= joint_probability(hi)):
        raise ValueError('Joint probability is outside the calibration bracket.')
    for _ in range(int(cop['bisection_steps'])):
        mid = 0.5 * (lo + hi)
        if joint_probability(mid) < p_joint:
            lo = mid
        else:
            hi = mid
    rho = 0.5 * (lo + hi)

    fm = m['ferritin']
    f_threshold = float(fm['threshold'])
    gm = float(fm['geometric_mean'])
    s_high = float(fm['upper_log_slope'])
    if f_threshold <= 0.0 or gm <= 0.0:
        raise ValueError('Ferritin scale parameters must be positive.')
    phi_k = math.exp(-0.5*k*k) / math.sqrt(2.0*math.pi)
    a_lower = -phi_k - k*p_f
    b_upper = phi_k - k*(1.0-p_f)
    s_low = (math.log(gm/f_threshold) - s_high*b_upper) / a_lower
    if not (math.isfinite(s_low) and s_low > 0.0 and s_high > 0.0):
        raise ValueError('Ferritin marginal must be strictly increasing.')

    hm = m['hemoglobin']
    lower = float(hm['lower_bound'])
    upper = float(hm['upper_bound'])
    median = float(hm['median'])
    h_threshold = float(hm['threshold'])
    if not (0.0 <= lower < h_threshold < upper and lower < median < upper):
        raise ValueError('Invalid hemoglobin support or locations.')
    hb_intercept = math.log((median-lower)/(upper-median))
    threshold_logit = math.log((h_threshold-lower)/(upper-h_threshold))
    hb_slope = (threshold_logit-hb_intercept) / h
    if not (math.isfinite(hb_slope) and hb_slope > 0.0):
        raise ValueError('Hemoglobin marginal must be strictly increasing.')

    rng = np.random.default_rng(seed)
    independent_normals = rng.standard_normal((n, 2))
    z_f = independent_normals[:, 0]
    z_h = rho*z_f + math.sqrt(1.0-rho*rho)*independent_normals[:, 1]
    log_f = math.log(f_threshold) + np.where(z_f < k, s_low, s_high)*(z_f-k)
    ferritin = np.exp(log_f)
    logistic_argument = hb_intercept + hb_slope*z_h
    hb = lower + (upper-lower)*(0.5 + 0.5*np.tanh(0.5*logistic_argument))

    # Validation only: no clipping, reweighting, rejection of tables, or moment matching.
    if not (np.isfinite(hb).all() and np.isfinite(ferritin).all()):
        raise FloatingPointError('Nonfinite generated measurement.')
    if not ((hb >= lower).all() and (hb <= upper).all() and (ferritin > 0.0).all()):
        raise FloatingPointError('Generated measurement outside model support.')
    return pd.DataFrame({
        'row_id': np.arange(1, n+1, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
