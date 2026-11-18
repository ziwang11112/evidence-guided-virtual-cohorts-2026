import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')
    m = spec['model']
    h = m['hemoglobin']
    f = m['ferritin']
    rho = float(m['dependence']['latent_normal_correlation'])
    if not -1.0 < rho < 1.0:
        raise ValueError('Latent correlation must be strictly between -1 and 1')

    hm = float(h['untruncated_location_g_dl'])
    hs = float(h['untruncated_scale_g_dl'])
    hl = float(h['lower_g_dl'])
    hu = float(h['upper_g_dl'])
    fm = float(f['untruncated_log_location'])
    fs = float(f['untruncated_log_scale'])
    fl = float(f['lower_ug_l'])
    fu = float(f['upper_ug_l'])
    if not (hs > 0.0 and fs > 0.0 and 0.0 < hl < hu and 0.0 < fl < fu):
        raise ValueError('Invalid marginal scales or bounds')

    standard = NormalDist()
    ha = standard.cdf((hl - hm) / hs)
    hb = standard.cdf((hu - hm) / hs)
    fa = standard.cdf((math.log(fl) - fm) / fs)
    fb = standard.cdf((math.log(fu) - fm) / fs)
    if not (0.0 < ha < hb < 1.0 and 0.0 < fa < fb < 1.0):
        raise ValueError('Bounds must give numerically interior CDF endpoints')

    rng = np.random.default_rng(seed)
    independent = rng.standard_normal((n, 2))
    z_h = independent[:, 0]
    z_f = rho * z_h + math.sqrt(1.0 - rho * rho) * independent[:, 1]
    u_h = np.fromiter((standard.cdf(float(z)) for z in z_h), dtype=float, count=n)
    u_f = np.fromiter((standard.cdf(float(z)) for z in z_f), dtype=float, count=n)

    p_h = ha + (hb - ha) * u_h
    p_f = fa + (fb - fa) * u_f
    hb_values = np.fromiter(
        (hm + hs * standard.inv_cdf(float(p)) for p in p_h),
        dtype=float, count=n
    )
    ferritin_values = np.fromiter(
        (math.exp(fm + fs * standard.inv_cdf(float(p))) for p in p_f),
        dtype=float, count=n
    )

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'hb_g_dl': hb_values,
        'ferritin_ug_l': ferritin_values
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
