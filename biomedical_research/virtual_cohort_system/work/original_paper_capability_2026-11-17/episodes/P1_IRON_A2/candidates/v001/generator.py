import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri, log_ndtr
from scipy.optimize import brentq
from scipy.stats import truncnorm
from numpy.polynomial.legendre import leggauss


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator represents a whole cohort, not conditional completion.')
    rng = np.random.default_rng(seed)
    n = int(spec['n_rows'])
    pdep = spec['store_mixture_probability']
    gm = np.asarray(spec['store_geometric_means'], dtype=float)
    ls = np.asarray(spec['store_log_sds'], dtype=float)
    pinf = spec['inflammation_probability']
    lf = np.log(spec['inflammation_ferritin_multiplier'])
    hb_sd = spec['hb_residual_sd']
    inf_loss = spec['inflammation_hb_decrement']
    knot = np.log(spec['store_response_knot'])
    cut = np.log(spec['ferritin_cutoff'])
    hb_cut = spec['hb_cutoff']
    p_ref = spec['reference_anemia_probability']
    counts = spec['source_cells_a_b_c_d']
    or_source = counts[0]*counts[3]/(counts[1]*counts[2])
    p_low = or_source*p_ref/(1-p_ref+or_source*p_ref)

    # Population integration, not integration over the generated cohort.
    # Separate integrals below/above the RAW ferritin threshold.
    gx, gw = leggauss(int(spec['quadrature_nodes']))
    u = (gx+1)/2
    gw = gw/2
    integration = {0: [[], [], []], 1: [[], [], []]}
    for j, pj in enumerate([pdep, 1-pdep]):
        for infl, pi in [(0, 1-pinf), (1, pinf)]:
            mu_z = np.log(gm[j])
            prob_low = ndtr((cut-infl*lf-mu_z)/ls[j])
            for low, lo, hi in [(1, 0.0, prob_low), (0, prob_low, 1.0)]:
                pp = lo+(hi-lo)*u
                pp = np.clip(pp, np.finfo(float).eps, 1-np.finfo(float).eps)
                z = mu_z+ls[j]*ndtri(pp)
                integration[low][0].append(np.maximum(0.0, knot-z))
                integration[low][1].append(np.full(len(z), infl))
                integration[low][2].append(pj*pi*(hi-lo)*gw)
    for low in integration:
        integration[low] = [np.concatenate(v) for v in integration[low]]

    def risk(intercept, slope, low):
        deficit, infl, wt = integration[low]
        loc = intercept-slope*deficit-inf_loss*infl
        # CDF at Hb cutoff for a normal distribution truncated below zero.
        pp = -np.expm1(log_ndtr((loc-hb_cut)/hb_sd)-log_ndtr(loc/hb_sd))
        return np.sum(wt*pp)/np.sum(wt)

    def intercept_for(slope):
        return brentq(lambda intercept: risk(intercept, slope, 0)-p_ref, 8.0, 30.0)

    slope = brentq(lambda b: risk(intercept_for(b), b, 1)-p_low, 0.0, 5.0)
    intercept = intercept_for(slope)

    depleted_component = rng.random(n) < pdep
    j = np.where(depleted_component, 0, 1)
    z = rng.normal(np.log(gm[j]), ls[j])
    inflammation = (rng.random(n) < pinf).astype(float)
    ferritin = np.exp(z+lf*inflammation)
    loc = intercept-slope*np.maximum(0.0, knot-z)-inf_loss*inflammation
    hb = truncnorm.rvs((0.0-loc)/hb_sd, np.inf, loc=loc, scale=hb_sd, size=n, random_state=rng)
    return pd.DataFrame({'row_id': np.arange(1, n+1, dtype=np.int64),
                         'hb_g_dl': hb,
                         'ferritin_ug_l': ferritin},
                        columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
