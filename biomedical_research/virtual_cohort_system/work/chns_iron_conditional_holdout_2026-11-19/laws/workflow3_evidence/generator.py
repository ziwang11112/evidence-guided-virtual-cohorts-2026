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
    group = rng.choice(len(bands), size=n, p=weights / weights.sum())
    hb = np.empty(n, dtype=float)
    ferritin = np.empty(n, dtype=float)
    log_cut = math.log(m['ferritin_cutoff_ug_l'])
    nodes, qw = np.polynomial.legendre.leggauss(int(m['calibration_quadrature_nodes']))
    normal_bound = m['calibration_normal_bound']
    for j, b in enumerate(bands):
        idx = np.flatnonzero(group == j)
        if not len(idx):
            continue
        lower, mean, sd = b['hb_lower'], b['hb_mean'], b['hb_sd']
        beta_family = b['hb_family'] == 'beta'
        if beta_family:
            width = b['hb_upper'] - lower
            xm = (mean - lower) / width
            precision = xm * (1.0 - xm) / (sd / width)**2 - 1.0
            alpha, beta = xm * precision, (1.0 - xm) * precision
            power = int(b['hb_score_power'])
            score_mean = math.prod((alpha + k) / (alpha + beta + k) for k in range(power))
        else:
            gap_mean = mean - lower
            scale = sd**2 / gap_mean
            shape = gap_mean / scale
            score_mean = 2.0**(-shape)
        score_denominator = max(score_mean, 1.0 - score_mean)
        p = b['depleted'] / b['count']
        q = NormalDist().inv_cdf(p)
        phi = math.exp(-q*q / 2.0) / math.sqrt(2.0 * math.pi)
        lm, rm = -phi - q*p, phi - q*(1.0-p)
        l2 = (1.0+q*q)*p + q*phi
        r2 = (1.0+q*q)*(1.0-p) - q*phi
        delta = math.log(b['ferritin_gm']) - log_cut
        second = math.log(b['ferritin_gsd'])**2 + delta**2
        aa = l2 + r2*(lm/rm)**2
        bb = -2.0*r2*delta*lm/rm**2
        cc = r2*(delta/rm)**2 - second
        left_scale = (-bb + math.sqrt(bb*bb - 4.0*aa*cc)) / (2.0*aa)
        right_scale = (delta - left_scale*lm) / rm
        if min(left_scale, right_scale) <= 0.0:
            raise ValueError('Incompatible ferritin marginal parameters')
        if 'dependence_gm_ratio_upper_lower' in b:
            split = (b['dependence_hb_split'] - lower) / width
            conditional_scores = []
            for lo, hi in ((0.0, split), (split, 1.0)):
                x = lo + (nodes + 1.0)*(hi-lo)/2.0
                w = qw * np.exp((alpha-1.0)*np.log(x) + (beta-1.0)*np.log1p(-x))
                s = (x**power - score_mean) / score_denominator
                conditional_scores.append(float(np.sum(w*s) / np.sum(w)))
            cross_moment = 0.0
            for lo, hi in ((-normal_bound, q), (q, normal_bound)):
                z = lo + (nodes + 1.0)*(hi-lo)/2.0
                log_delta = np.where(z <= q, left_scale, right_scale)*(z-q)
                integrand = log_delta*np.tanh(z)*np.exp(-z*z/2.0)/math.sqrt(2.0*math.pi)
                cross_moment += (hi-lo)/2.0 * float(np.sum(qw*integrand))
            theta = math.log(b['dependence_gm_ratio_upper_lower']) / (cross_moment * (conditional_scores[1]-conditional_scores[0]))
        else:
            theta = b['dependence_theta']
        if not math.isfinite(theta) or abs(theta) > 1.0:
            raise ValueError('Dependence calibration exceeds the Sarmanov bound')
        hs, zs = [], []
        remaining = len(idx)
        while remaining:
            if beta_family:
                x = rng.beta(alpha, beta, size=remaining)
                h = lower + width*x
                score = (x**power - score_mean) / score_denominator
            else:
                gap = rng.gamma(shape, scale, size=remaining)
                h = lower + gap
                score = (score_mean - np.exp(-gap/scale)) / score_denominator
            z = rng.standard_normal(remaining)
            keep = rng.random(remaining) < (1.0 + theta*score*np.tanh(z))/2.0
            hs.append(h[keep])
            zs.append(z[keep])
            remaining -= int(keep.sum())
        z = np.concatenate(zs)
        hb[idx] = np.concatenate(hs)
        ferritin[idx] = np.exp(log_cut + np.where(z <= q, left_scale, right_scale)*(z-q))
    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'hb_g_dl': hb, 'ferritin_ug_l': ferritin}, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
