import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)
    counts = np.asarray(m['hb_band_counts'], dtype=float)
    bands = rng.choice(3, size=n, p=counts / counts.sum())
    z = rng.standard_normal((n, 2))
    hb = np.empty(n, dtype=float)
    ferritin = np.empty(n, dtype=float)
    cut0, cut1 = m['hb_cutpoints_g_dl']
    logcut = math.log(m['ferritin_cutpoint_ug_l'])
    nd = NormalDist()
    eps = np.finfo(float).eps

    for k in range(3):
        ix = np.flatnonzero(bands == k)
        zh = z[ix, 0]
        u = np.fromiter((0.5 * math.erfc(-float(x) / math.sqrt(2.0)) for x in zh), dtype=float, count=len(ix))
        u = np.clip(u, eps, 1.0 - eps)
        mean = m['hb_band_means_g_dl'][k]
        sd = m['hb_band_sds_g_dl'][k]

        if k == 0:
            deficit = cut0 - mean
            r2 = (sd / deficit) ** 2
            power = r2 + math.sqrt(r2 * r2 + r2)
            scale = deficit * (power + 1.0)
            h = cut0 - scale * (1.0 - u) ** power
            h = np.minimum(h, np.nextafter(cut0, -np.inf))
        elif k == 2:
            excess = mean - cut1
            r2 = (sd / excess) ** 2
            power = r2 + math.sqrt(r2 * r2 + r2)
            scale = excess * (power + 1.0)
            h = cut1 + scale * u ** power
        else:
            center = (cut0 + cut1) / 2.0
            width = (cut1 - cut0) / 2.0
            delta = (mean - center) / width
            power = ((1.0 + delta * delta) / (sd / width) ** 2 - 1.0) / 2.0
            pivot = center + (mean - center) * (power + 1.0) / power
            h = np.where(u < 0.5,
                         pivot - (pivot - cut0) * np.abs(2.0 * u - 1.0) ** power,
                         pivot + (cut1 - pivot) * np.abs(2.0 * u - 1.0) ** power)
            h = np.clip(h, cut0, np.nextafter(cut1, -np.inf))
        hb[ix] = h

        p = m['ferritin_depleted_counts'][k] / counts[k]
        c = nd.inv_cdf(p)
        phi = math.exp(-0.5 * c * c) / math.sqrt(2.0 * math.pi)
        a1 = -phi - c * p
        b1 = phi - c * (1.0 - p)
        a2 = (1.0 + c * c) * p + c * phi
        b2 = (1.0 + c * c) * (1.0 - p) - c * phi
        offset = math.log(m['ferritin_band_geometric_means'][k]) - logcut
        logs = math.log(m['ferritin_band_geometric_sds'][k])
        qa = a2 + b2 * a1 * a1 / (b1 * b1)
        qb = -2.0 * b2 * offset * a1 / (b1 * b1)
        qc = b2 * offset * offset / (b1 * b1) - logs * logs - offset * offset
        slope_left = (-qb + math.sqrt(qb * qb - 4.0 * qa * qc)) / (2.0 * qa)
        slope_right = (offset - a1 * slope_left) / b1
        if min(slope_left, slope_right) <= 0.0:
            raise ValueError('Ferritin calibration requires positive slopes')
        rho = m['within_band_gaussian_copula_correlations'][k]
        zf = rho * zh + math.sqrt(1.0 - rho * rho) * z[ix, 1]
        lf = logcut + np.where(zf < c, slope_left, slope_right) * (zf - c)
        ferritin[ix] = np.exp(lf)

    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64),
                         'hb_g_dl': hb,
                         'ferritin_ug_l': ferritin},
                        columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
