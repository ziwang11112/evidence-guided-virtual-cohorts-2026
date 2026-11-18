import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This whole-cohort generator expects observed=None.')
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative.')
    m = spec['model']
    cells = m['source_cells']
    total = float(sum(cells.values()))
    if total <= 0 or any(v < 0 for v in cells.values()):
        raise ValueError('Invalid source cell counts.')
    p_h = (cells['both_low'] + cells['only_hb_low']) / total
    p_f = (cells['both_low'] + cells['only_ferritin_low']) / total
    p_joint = cells['both_low'] / total
    if not (0 < p_h < 1 and 0 < p_f < 1):
        raise ValueError('Marginal threshold probabilities must be interior.')

    nd = NormalDist()
    sqrt2 = math.sqrt(2.0)
    sqrt2pi = math.sqrt(2.0 * math.pi)
    def Phi(x):
        return 0.5 * math.erfc(-float(x) / sqrt2)
    def phi(x):
        return math.exp(-0.5 * float(x) ** 2) / sqrt2pi
    open_lo = float(np.nextafter(0.0, 1.0))
    open_hi = float(np.nextafter(1.0, 0.0))
    def invPhi(u):
        return nd.inv_cdf(min(open_hi, max(open_lo, float(u))))
    def cdf_array(x):
        return np.fromiter((Phi(v) for v in x), dtype=float, count=len(x))
    def inv_array(u):
        return np.fromiter((invPhi(v) for v in u), dtype=float, count=len(u))

    iterations = int(m['numerics']['bisection_iterations'])
    def solve(fn, target, bounds):
        lo, hi = map(float, bounds)
        fl = fn(lo) - target
        fh = fn(hi) - target
        if not (math.isfinite(fl) and math.isfinite(fh)):
            raise ValueError('Nonfinite calibration endpoint.')
        if fl == 0:
            return lo
        if fh == 0:
            return hi
        if fl * fh > 0:
            raise ValueError('Calibration root is not bracketed.')
        for _ in range(iterations):
            mid = 0.5 * (lo + hi)
            fm = fn(mid) - target
            if not math.isfinite(fm):
                raise ValueError('Nonfinite calibration value.')
            if fm == 0:
                return mid
            if fl * fm <= 0:
                hi = mid
            else:
                lo, fl = mid, fm
        return 0.5 * (lo + hi)

    # Calibrate the Hb marginal analytically, without using generated rows.
    h_lo, h_hi = map(float, m['hb']['support_g_dl'])
    h_cut = float(m['hb']['threshold_g_dl'])
    h_sd = float(m['hb']['untruncated_sd_g_dl'])
    if not (h_lo < h_cut < h_hi and h_sd > 0):
        raise ValueError('Invalid Hb marginal parameters.')
    def hb_lower_probability(mu):
        a = Phi((h_lo - mu) / h_sd)
        b = Phi((h_hi - mu) / h_sd)
        return (Phi((h_cut - mu) / h_sd) - a) / (b - a)
    h_mu = solve(hb_lower_probability, p_h,
                 m['numerics']['hb_location_bracket_g_dl'])
    h_cdf_lo = Phi((h_lo - h_mu) / h_sd)
    h_cdf_hi = Phi((h_hi - h_mu) / h_sd)

    # Calibrate E[log ferritin], not the realized sample geometric mean.
    f_lo, f_hi = map(float, m['ferritin']['support_ug_l'])
    f_cut = float(m['ferritin']['threshold_ug_l'])
    f_gm = float(m['ferritin']['geometric_mean_ug_l'])
    s_lower = float(m['ferritin']['lower_log_sd'])
    if not (0 < f_lo < f_cut < f_hi and s_lower > 0 and f_gm > 0):
        raise ValueError('Invalid ferritin marginal parameters.')
    log_lo, log_hi, log_cut = math.log(f_lo), math.log(f_hi), math.log(f_cut)
    z_lower = (log_lo - log_cut) / s_lower
    lower_cdf = Phi(z_lower)
    lower_log_mean = log_cut + s_lower * (phi(z_lower) - phi(0.0)) / (0.5 - lower_cdf)
    def mixture_log_mean(s_upper):
        z_upper = (log_hi - log_cut) / s_upper
        upper_log_mean = log_cut + s_upper * (phi(0.0) - phi(z_upper)) / (Phi(z_upper) - 0.5)
        return p_f * lower_log_mean + (1.0 - p_f) * upper_log_mean
    s_upper = solve(mixture_log_mean, math.log(f_gm),
                    m['numerics']['ferritin_upper_log_sd_bracket'])
    upper_cdf = Phi((log_hi - log_cut) / s_upper)

    # Deterministic population calibration of a Gaussian copula.
    q_h, q_f = invPhi(p_h), invPhi(p_f)
    intervals = int(m['numerics']['copula_simpson_intervals'])
    if intervals < 2 or intervals % 2:
        raise ValueError('Simpson integration requires a positive even interval count.')
    lower_z = float(m['numerics']['copula_integration_lower_z'])
    if lower_z >= q_h:
        raise ValueError('Invalid copula integration interval.')
    grid = np.linspace(lower_z, q_h, intervals + 1)
    weights = np.ones(intervals + 1)
    weights[1:-1:2] = 4.0
    weights[2:-1:2] = 2.0
    step = (q_h - lower_z) / intervals
    integration_weights = weights * np.exp(-0.5 * grid * grid) / sqrt2pi * step / 3.0
    def joint_probability(rho):
        conditional_z = (q_f - rho * grid) / math.sqrt(1.0 - rho * rho)
        return float(np.dot(integration_weights, cdf_array(conditional_z)))
    rho = solve(joint_probability, p_joint,
                m['numerics']['copula_rho_bracket'])

    # All rows are independent draws; there is no sample-wide fitting or repair.
    rng = np.random.default_rng(seed)
    z_h = rng.standard_normal(n)
    z_independent = rng.standard_normal(n)
    z_f = rho * z_h + math.sqrt(1.0 - rho * rho) * z_independent
    u_h = cdf_array(z_h)
    u_f = cdf_array(z_f)

    hb = h_mu + h_sd * inv_array(h_cdf_lo + u_h * (h_cdf_hi - h_cdf_lo))
    log_ferritin = np.empty(n, dtype=float)
    lower = u_f < p_f
    within_lower = u_f[lower] / p_f
    log_ferritin[lower] = log_cut + s_lower * inv_array(
        lower_cdf + within_lower * (0.5 - lower_cdf))
    within_upper = (u_f[~lower] - p_f) / (1.0 - p_f)
    log_ferritin[~lower] = log_cut + s_upper * inv_array(
        0.5 + within_upper * (upper_cdf - 0.5))
    ferritin = np.exp(log_ferritin)

    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
