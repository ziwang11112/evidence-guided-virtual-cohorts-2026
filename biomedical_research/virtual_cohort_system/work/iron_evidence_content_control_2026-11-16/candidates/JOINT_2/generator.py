import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)
    nd = NormalDist()
    sqrt2 = math.sqrt(2.0)
    sqrt2pi = math.sqrt(2.0 * math.pi)
    steps = int(m['numerics']['bisection_iterations'])

    def Phi(x):
        return 0.5 * math.erfc(-float(x) / sqrt2)

    def phi(x):
        return math.exp(-0.5 * float(x) ** 2) / sqrt2pi

    prob_min = np.nextafter(0.0, 1.0)
    prob_max = np.nextafter(1.0, 0.0)

    def cdf_array(x):
        x = np.asarray(x, dtype=float)
        out = np.fromiter((Phi(v) for v in x.ravel()), dtype=float, count=x.size)
        return np.clip(out.reshape(x.shape), prob_min, prob_max)

    def ppf_array(q):
        q = np.clip(np.asarray(q, dtype=float), prob_min, prob_max)
        out = np.fromiter((nd.inv_cdf(float(v)) for v in q.ravel()), dtype=float, count=q.size)
        return out.reshape(q.shape)

    def solve_increasing(fun, target, bracket):
        lo, hi = map(float, bracket)
        if not fun(lo) <= target <= fun(hi):
            raise ValueError('Specified calibration bracket does not contain a solution')
        for _ in range(steps):
            mid = 0.5 * (lo + hi)
            if fun(mid) < target:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    cells = m['source_counts']
    total = float(cells['total'])
    if sum(cells[k] for k in ('both_low', 'only_hb_low', 'only_ferritin_low', 'neither_low')) != cells['total']:
        raise ValueError('Source cell counts are inconsistent')
    p_h = (cells['both_low'] + cells['only_hb_low']) / total
    p_f = (cells['both_low'] + cells['only_ferritin_low']) / total
    p_joint = cells['both_low'] / total
    h_cut = float(m['thresholds']['hb_g_dl'])
    f_cut = float(m['thresholds']['ferritin_ug_l'])

    hm = m['hb']
    h_lo = float(hm['lower_g_dl'])
    h_hi = float(hm['upper_g_dl'])
    h_sd = float(hm['scale_g_dl'])

    def hb_cdf_at_cut(mu):
        a = Phi((h_lo - mu) / h_sd)
        b = Phi((h_hi - mu) / h_sd)
        return (Phi((h_cut - mu) / h_sd) - a) / (b - a)

    h_mu = solve_increasing(lambda mu: 1.0 - hb_cdf_at_cut(mu), 1.0 - p_h, hm['location_bracket_g_dl'])
    h_cdf_lo = Phi((h_lo - h_mu) / h_sd)
    h_cdf_hi = Phi((h_hi - h_mu) / h_sd)

    fm = m['ferritin']
    log_cut = math.log(f_cut)
    log_lo = math.log(float(fm['lower_ug_l']))
    log_hi = math.log(float(fm['upper_ug_l']))
    s_lower = float(fm['lower_log_scale'])
    lower_extent = (log_cut - log_lo) / s_lower

    def truncated_halfnormal_mean_log_gap(scale, log_extent):
        t = log_extent / scale
        return scale * (phi(0.0) - phi(t)) / (Phi(t) - 0.5)

    lower_gap = truncated_halfnormal_mean_log_gap(s_lower, log_cut - log_lo)
    required_upper_gap = (math.log(float(fm['geometric_mean_ug_l'])) - log_cut + p_f * lower_gap) / (1.0 - p_f)
    s_upper = solve_increasing(
        lambda s: truncated_halfnormal_mean_log_gap(s, log_hi - log_cut),
        required_upper_gap,
        fm['upper_log_scale_bracket']
    )
    upper_extent = (log_hi - log_cut) / s_upper
    f_lower_cdf = Phi(-lower_extent)
    f_upper_cdf = Phi(upper_extent)

    z_h_cut = nd.inv_cdf(p_h)
    z_f_cut = nd.inv_cdf(p_f)
    nodes, weights = np.polynomial.legendre.leggauss(int(m['numerics']['quadrature_nodes']))

    def bivariate_lower_probability(rho):
        if rho == 0.0:
            return p_h * p_f
        t = 0.5 * rho * (nodes + 1.0)
        variance = 1.0 - t * t
        exponent = -(z_h_cut * z_h_cut - 2.0 * t * z_h_cut * z_f_cut + z_f_cut * z_f_cut) / (2.0 * variance)
        density = np.exp(exponent) / (2.0 * math.pi * np.sqrt(variance))
        integral = 0.5 * rho * float(np.dot(weights, density))
        return p_h * p_f + integral

    rho = solve_increasing(bivariate_lower_probability, p_joint, m['dependence']['latent_correlation_bracket'])

    latent = rng.standard_normal((n, 2))
    z_h = latent[:, 0]
    z_f = rho * latent[:, 0] + math.sqrt(1.0 - rho * rho) * latent[:, 1]
    u_h = cdf_array(z_h)
    u_f = cdf_array(z_f)

    h_q = h_cdf_lo + u_h * (h_cdf_hi - h_cdf_lo)
    hb = h_mu + h_sd * ppf_array(h_q)

    ferritin_log = np.empty(n, dtype=float)
    lower = u_f < p_f
    lower_u = u_f[lower] / p_f
    lower_q = f_lower_cdf + lower_u * (0.5 - f_lower_cdf)
    ferritin_log[lower] = log_cut + s_lower * ppf_array(lower_q)
    upper_u = (u_f[~lower] - p_f) / (1.0 - p_f)
    upper_q = 0.5 + upper_u * (f_upper_cdf - 0.5)
    ferritin_log[~lower] = log_cut + s_upper * ppf_array(upper_q)
    ferritin = np.exp(ferritin_log)

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
