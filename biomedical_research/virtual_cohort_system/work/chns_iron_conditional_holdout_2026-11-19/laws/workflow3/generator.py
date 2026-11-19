import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)
    bands = m['bands']
    weights = np.array([b['count'] for b in bands], dtype=float)
    weights /= weights.sum()
    group = rng.choice(len(bands), size=n, p=weights)
    hb = np.empty(n, dtype=float)
    ferritin = np.empty(n, dtype=float)
    log_cut = math.log(m['ferritin_cutoff_ug_l'])
    for j, b in enumerate(bands):
        idx = np.flatnonzero(group == j)
        if not len(idx):
            continue
        lower = b['hb_lower']
        mean = b['hb_mean']
        sd = b['hb_sd']
        beta_family = b['hb_family'] == 'beta'
        if beta_family:
            width = b['hb_upper'] - lower
            xm = (mean - lower) / width
            precision = xm * (1.0 - xm) / (sd / width)**2 - 1.0
            alpha = xm * precision
            beta = (1.0 - xm) * precision
            power = int(b['hb_score_power'])
            score_mean = math.prod((alpha + k) / (alpha + beta + k) for k in range(power))
        else:
            gap_mean = mean - lower
            scale = sd**2 / gap_mean
            shape = gap_mean / scale
            score_mean = 2.0**(-shape)
        score_denominator = max(score_mean, 1.0 - score_mean)
        hs, zs = [], []
        remaining = len(idx)
        while remaining:
            if beta_family:
                x = rng.beta(alpha, beta, size=remaining)
                h = lower + width * x
                score = (x**power - score_mean) / score_denominator
            else:
                gap = rng.gamma(shape, scale, size=remaining)
                h = lower + gap
                score = (score_mean - np.exp(-gap / scale)) / score_denominator
            z = rng.standard_normal(remaining)
            accept_prob = (1.0 + b['dependence_theta'] * score * np.tanh(z)) / 2.0
            keep = rng.random(remaining) < accept_prob
            hs.append(h[keep])
            zs.append(z[keep])
            remaining -= int(keep.sum())
        h = np.concatenate(hs)
        z = np.concatenate(zs)
        p = b['depleted'] / b['count']
        q = NormalDist().inv_cdf(p)
        phi = math.exp(-q*q / 2.0) / math.sqrt(2.0 * math.pi)
        left_mean = -phi - q*p
        right_mean = phi - q*(1.0-p)
        left_second = (1.0+q*q)*p + q*phi
        right_second = (1.0+q*q)*(1.0-p) - q*phi
        delta = math.log(b['ferritin_gm']) - log_cut
        second = math.log(b['ferritin_gsd'])**2 + delta**2
        aa = left_second + right_second*(left_mean/right_mean)**2
        bb = -2.0*right_second*delta*left_mean/right_mean**2
        cc = right_second*(delta/right_mean)**2 - second
        left_scale = (-bb + math.sqrt(bb*bb - 4.0*aa*cc)) / (2.0*aa)
        right_scale = (delta - left_scale*left_mean) / right_mean
        if left_scale <= 0.0 or right_scale <= 0.0:
            raise ValueError('Incompatible ferritin marginal parameters')
        log_f = log_cut + np.where(z <= q, left_scale, right_scale)*(z-q)
        hb[idx] = h
        ferritin[idx] = np.exp(log_f)
    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'hb_g_dl': hb, 'ferritin_ug_l': ferritin}, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
