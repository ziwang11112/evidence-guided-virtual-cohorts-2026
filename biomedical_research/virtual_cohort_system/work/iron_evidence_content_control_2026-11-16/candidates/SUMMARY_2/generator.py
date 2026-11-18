import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    model = spec['model']
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative')

    anchors = model['source_anchors']
    hb_model = model['hemoglobin']
    normal = NormalDist()
    p_hb = anchors['hb_low_count'] / anchors['denominator']
    p_f = anchors['ferritin_low_count'] / anchors['denominator']
    hb_cut = float(anchors['hb_cutoff_g_dl'])
    f_cut = float(anchors['ferritin_cutoff_ug_l'])
    f_gm = float(anchors['ferritin_geometric_mean_ug_l'])
    lower = float(hb_model['lower_g_dl'])
    upper = float(hb_model['upper_g_dl'])
    hb_sd = float(hb_model['parent_sd_g_dl'])
    rho = float(model['dependence']['latent_normal_correlation'])

    if not (0.0 < p_hb < 1.0 and 0.0 < p_f < 1.0):
        raise ValueError('Anchor probabilities must lie strictly between zero and one')
    if not (lower < hb_cut < upper and hb_sd > 0.0 and abs(rho) < 1.0):
        raise ValueError('Invalid hemoglobin or dependence parameters')

    def hb_probability(mu):
        a = normal.cdf((lower - mu) / hb_sd)
        b = normal.cdf((upper - mu) / hb_sd)
        c = normal.cdf((hb_cut - mu) / hb_sd)
        return (c - a) / (b - a)

    # Deterministic population-parameter calibration, not sample calibration.
    left, right = lower, upper
    if not (hb_probability(left) >= p_hb >= hb_probability(right)):
        raise ValueError('Hemoglobin location root is not bracketed')
    for _ in range(100):
        midpoint = (left + right) / 2.0
        if hb_probability(midpoint) > p_hb:
            left = midpoint
        else:
            right = midpoint
    hb_mu = (left + right) / 2.0

    f_log_mu = math.log(f_gm)
    f_log_sd = math.log(f_cut / f_gm) / normal.inv_cdf(p_f)
    if not (math.isfinite(f_log_sd) and f_log_sd > 0.0):
        raise ValueError('Ferritin anchors do not yield a positive lognormal scale')

    rng = np.random.default_rng(seed)
    innovations = rng.standard_normal((n, 2))
    z_f = innovations[:, 0]
    z_hb = rho * z_f + math.sqrt(1.0 - rho * rho) * innovations[:, 1]
    ferritin = np.exp(f_log_mu + f_log_sd * z_f)

    u_hb = np.fromiter((normal.cdf(float(z)) for z in z_hb), dtype=float, count=n)
    a = normal.cdf((lower - hb_mu) / hb_sd)
    b = normal.cdf((upper - hb_mu) / hb_sd)
    quantile_probabilities = a + (b - a) * u_hb
    # Fixed floating-point endpoint protection, not physiological clipping.
    quantile_probabilities = np.clip(
        quantile_probabilities,
        np.nextafter(0.0, 1.0),
        np.nextafter(1.0, 0.0)
    )
    hb = np.fromiter(
        (hb_mu + hb_sd * normal.inv_cdf(float(p)) for p in quantile_probabilities),
        dtype=float,
        count=n
    )

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
