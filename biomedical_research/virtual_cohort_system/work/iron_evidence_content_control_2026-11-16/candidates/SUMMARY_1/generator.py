import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')

    t = m['transport']
    h = m['hb']
    f = m['ferritin']
    numerics = m['numerics']
    denominator = float(t['source_denominator'])
    p_h = float(t['source_hb_low_count']) / denominator
    p_f = float(t['source_ferritin_low_count']) / denominator
    gm = float(t['ferritin_geometric_mean_ug_l'])
    h_cut = float(h['cutoff_g_dl'])
    f_cut = float(f['cutoff_ug_l'])
    h_lo = float(h['lower_g_dl'])
    h_hi = float(h['upper_g_dl'])
    h_sd = float(h['parent_sd_g_dl'])
    s_lo = float(f['lower_log_scale'])
    rho = float(m['dependence']['latent_correlation'])
    eps = float(numerics['inverse_normal_probability_guard'])
    if not (0.0 < p_h < 1.0 and 0.0 < p_f < 1.0):
        raise ValueError('Invalid transported probabilities')
    if not (0.0 < h_lo < h_cut < h_hi and h_sd > 0.0):
        raise ValueError('Invalid Hb parameters')
    if not (gm > 0.0 and f_cut > 0.0 and s_lo > 0.0 and abs(rho) < 1.0):
        raise ValueError('Invalid ferritin or copula parameters')
    if not (0.0 < eps < 0.5):
        raise ValueError('Invalid numerical guard')

    sqrt_two = math.sqrt(2.0)
    half_normal_mean = math.sqrt(2.0 / math.pi)
    s_hi = (math.log(gm / f_cut) / half_normal_mean + p_f * s_lo) / (1.0 - p_f)
    if s_hi <= 0.0:
        raise ValueError('The selected ferritin shape cannot satisfy the constraints')

    def cdf(x):
        return 0.5 * math.erfc(-float(x) / sqrt_two)

    normal = NormalDist()

    def inv_cdf(u):
        # Endpoint protection only; no sample-wide transformations are used.
        q = min(1.0 - eps, max(eps, float(u)))
        return normal.inv_cdf(q)

    def hb_probability_below_cut(mu):
        a = cdf((h_lo - mu) / h_sd)
        b = cdf((h_hi - mu) / h_sd)
        c = cdf((h_cut - mu) / h_sd)
        return (c - a) / (b - a)

    left, right = h_lo, h_hi
    if not (hb_probability_below_cut(left) >= p_h >= hb_probability_below_cut(right)):
        raise ValueError('Hb location is not bracketed')
    for _ in range(int(numerics['location_bisection_iterations'])):
        mid = 0.5 * (left + right)
        if hb_probability_below_cut(mid) > p_h:
            left = mid
        else:
            right = mid
    mu_h = 0.5 * (left + right)
    cdf_lo = cdf((h_lo - mu_h) / h_sd)
    cdf_hi = cdf((h_hi - mu_h) / h_sd)

    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n, 2))
    z_f = z[:, 0]
    z_h = rho * z[:, 0] + math.sqrt(1.0 - rho * rho) * z[:, 1]
    u_f = np.fromiter((cdf(x) for x in z_f), dtype=float, count=n)
    u_h = np.fromiter((cdf(x) for x in z_h), dtype=float, count=n)

    hb = np.fromiter(
        (mu_h + h_sd * inv_cdf(cdf_lo + (cdf_hi - cdf_lo) * u) for u in u_h),
        dtype=float,
        count=n
    )
    log_f = np.empty(n, dtype=float)
    log_cut = math.log(f_cut)
    for i, u in enumerate(u_f):
        if u < p_f:
            log_f[i] = log_cut + s_lo * inv_cdf(u / (2.0 * p_f))
        else:
            q = 0.5 + 0.5 * (u - p_f) / (1.0 - p_f)
            log_f[i] = log_cut + s_hi * inv_cdf(q)
    ferritin = np.exp(log_f)

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
