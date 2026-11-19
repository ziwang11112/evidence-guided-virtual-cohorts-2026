import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def _betacf(a, b, x):
    qab, qap, qam = a+b, a+1.0, a-1.0
    c = 1.0
    d = 1.0-qab*x/qap
    if abs(d) < 1e-300:
        d = 1e-300
    d = 1.0/d
    h = d
    for j in range(1, 201):
        j2 = 2*j
        terms = (j*(b-j)*x/((qam+j2)*(a+j2)),
                 -(a+j)*(qab+j)*x/((a+j2)*(qap+j2)))
        for aa in terms:
            d = 1.0+aa*d
            c = 1.0+aa/c
            if abs(d) < 1e-300:
                d = 1e-300
            if abs(c) < 1e-300:
                c = 1e-300
            d = 1.0/d
            delta = d*c
            h *= delta
        if abs(delta-1.0) < 3e-14:
            break
    return h


def _betacdf(x, a, b):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)
                     +a*math.log(x)+b*math.log1p(-x))
    if x < (a+1.0)/(a+b+2.0):
        return front*_betacf(a, b, x)/a
    return 1.0-front*_betacf(b, a, 1.0-x)/b


def generate(observed, spec, seed):
    m = spec['model']
    n = int(spec['task']['n_rows'])
    rng = np.random.default_rng(seed)
    normal = NormalDist()
    bands = m['bands']
    weights = np.array([b['count'] for b in bands], dtype=float)
    group = rng.choice(len(bands), size=n, p=weights/weights.sum())
    hb = np.empty(n, dtype=float)
    ferritin = np.empty(n, dtype=float)
    threshold_log = math.log(m['ferritin_depletion_threshold_ug_l'])
    for j, b in enumerate(bands):
        ix = np.flatnonzero(group == j)
        k = len(ix)
        if k == 0:
            continue
        lower, upper = b['hb_lower'], b['hb_upper']
        width = upper-lower
        mean_unit = (b['hb_mean']-lower)/width
        var_unit = (b['hb_sd']/width)**2
        concentration = mean_unit*(1.0-mean_unit)/var_unit-1.0
        alpha = mean_unit*concentration
        beta = (1.0-mean_unit)*concentration
        x = rng.beta(alpha, beta, size=k)
        x = np.clip(x, np.nextafter(0.0, 1.0), np.nextafter(1.0, 0.0))
        hb[ix] = lower+width*x
        zh = np.fromiter((normal.inv_cdf(min(1.0-1e-15, max(1e-15,
                          _betacdf(float(v), alpha, beta)))) for v in x),
                         dtype=float, count=k)
        rho = b['within_band_copula_rho']
        zf = rho*zh+math.sqrt(1.0-rho*rho)*rng.standard_normal(k)
        p = b['ferritin_depleted_count']/b['count']
        cut = normal.inv_cdf(p)
        density = math.exp(-0.5*cut*cut)/math.sqrt(2.0*math.pi)
        low_first = -density-cut*p
        high_first = density-cut*(1.0-p)
        low_second = (1.0+cut*cut)*p+cut*density
        high_second = (1.0+cut*cut)*(1.0-p)-cut*density
        offset = math.log(b['ferritin_gm'])-threshold_log
        log_sd = math.log(b['ferritin_gsd'])
        qa = low_second+high_second*(low_first/high_first)**2
        qb = -2.0*high_second*offset*low_first/(high_first**2)
        qc = high_second*(offset/high_first)**2-log_sd**2-offset**2
        slope_low = (-qb+math.sqrt(qb*qb-4.0*qa*qc))/(2.0*qa)
        slope_high = (offset-low_first*slope_low)/high_first
        log_f = threshold_log+np.where(zf < cut, slope_low, slope_high)*(zf-cut)
        ferritin[ix] = np.exp(log_f)
    return pd.DataFrame({'row_id': np.arange(n, dtype=np.int64),
                         'hb_g_dl': hb, 'ferritin_ug_l': ferritin},
                        columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
