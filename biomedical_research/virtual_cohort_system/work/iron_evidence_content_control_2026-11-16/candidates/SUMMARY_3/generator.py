import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')

    inputs = m['source_marginal_inputs']
    denominator = float(inputs['denominator'])
    p_h = float(inputs['hb_below_cutoff_count']) / denominator
    p_f = float(inputs['ferritin_below_cutoff_count']) / denominator
    gm_f = float(inputs['ferritin_geometric_mean_ug_l'])
    if not (0.0 < p_h < 1.0 and 0.0 < p_f < 1.0):
        raise ValueError('Marginal probabilities must be interior')

    h = m['hb']
    h_low = float(h['lower_bound_g_dl'])
    h_high = float(h['upper_bound_g_dl'])
    h_cut = float(h['cutoff_g_dl'])
    h_scale = float(h['logistic_scale'])
    if not (0.0 < h_low < h_cut < h_high and h_scale > 0.0):
        raise ValueError('Invalid hemoglobin support or scale')

    f = m['ferritin']
    f_low = float(f['lower_bound_ug_l'])
    f_high = float(f['upper_bound_ug_l'])
    f_cut = float(f['cutoff_ug_l'])
    scale_low = float(f['below_log_distance_scale'])
    if not (0.0 < f_low < f_cut < f_high and scale_low > 0.0):
        raise ValueError('Invalid ferritin support or scale')

    rho = float(m['dependence']['latent_normal_pearson_rho'])
    if not (-1.0 < rho < 1.0):
        raise ValueError('Copula correlation must lie strictly between -1 and 1')

    nd = NormalDist()
    sqrt2 = math.sqrt(2.0)
    d_low = math.log(f_cut / f_low)
    d_high = math.log(f_high / f_cut)

    def truncated_halfnormal_mean(scale, endpoint):
        ratio = endpoint / scale
        numerator = -math.expm1(-0.5 * ratio * ratio)
        normalizer = math.erf(ratio / sqrt2)
        return scale * math.sqrt(2.0 / math.pi) * numerator / normalizer

    mean_low = truncated_halfnormal_mean(scale_low, d_low)
    target_mean_high = (math.log(gm_f / f_cut) + p_f * mean_low) / (1.0 - p_f)
    if not (0.0 < target_mean_high < 0.5 * d_high):
        raise ValueError('Ferritin log-mean cannot be matched by this family')

    left = 1.0e-12
    right = 1.0
    while truncated_halfnormal_mean(right, d_high) < target_mean_high:
        right *= 2.0
    for _ in range(100):
        midpoint = 0.5 * (left + right)
        if truncated_halfnormal_mean(midpoint, d_high) < target_mean_high:
            left = midpoint
        else:
            right = midpoint
    scale_high = 0.5 * (left + right)

    mass_low = math.erf(d_low / (sqrt2 * scale_low))
    mass_high = math.erf(d_high / (sqrt2 * scale_high))
    tail_low = 0.5 * math.erfc(d_low / (sqrt2 * scale_low))
    tail_high = 0.5 * math.erfc(d_high / (sqrt2 * scale_high))

    rng = np.random.default_rng(seed)
    innovations = rng.standard_normal((n, 2))
    z_f = innovations[:, 0]
    z_h = rho * z_f + math.sqrt(1.0 - rho * rho) * innovations[:, 1]

    h_location = math.log((h_cut - h_low) / (h_high - h_cut)) - h_scale * nd.inv_cdf(p_h)
    eta = h_location + h_scale * z_h
    exp_negative_abs = np.exp(-np.abs(eta))
    logistic = np.where(eta >= 0.0, 1.0 / (1.0 + exp_negative_abs), exp_negative_abs / (1.0 + exp_negative_abs))
    hb = h_low + (h_high - h_low) * logistic

    ferritin = np.empty(n, dtype=float)
    for i, z in enumerate(z_f):
        u = 0.5 * math.erfc(-float(z) / sqrt2)
        survival = 0.5 * math.erfc(float(z) / sqrt2)
        if u < p_f:
            q = tail_low + 0.5 * mass_low * (u / p_f)
            q = min(0.5, max(tail_low, q))
            distance = -scale_low * nd.inv_cdf(q)
            ferritin[i] = f_cut * math.exp(-distance)
        else:
            q = tail_high + 0.5 * mass_high * (survival / (1.0 - p_f))
            q = min(0.5, max(tail_high, q))
            distance = -scale_high * nd.inv_cdf(q)
            ferritin[i] = f_cut * math.exp(distance)

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
