import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri, expit
from scipy.optimize import brentq, root
from scipy.stats import truncnorm
from numpy.polynomial.legendre import leggauss

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generator expects observed=None')
    n = int(spec['n_rows'])
    rng = np.random.default_rng(seed)
    sigma_f = spec['latent_log_ferritin_sd']
    pi = spec['inflammation_probability']
    delta_f = np.log(spec['inflammation_ferritin_multiplier'])
    hb_sd = spec['hb_residual_sd_g_dl']
    hb_infl = spec['inflammation_hb_decrement_g_dl']
    other_p = spec['other_anemia_component_probability']
    other_drop = spec['other_component_hb_decrement_g_dl']
    # Calibration is to the population law, before any virtual rows are drawn.
    # Rounding to 0.1 means strict reported <15 and <12 use these boundaries.
    ferritin_boundary = spec['ferritin_threshold'] - spec['ferritin_resolution']/2
    hb_boundary = spec['hb_threshold'] - spec['hb_resolution']/2
    prevalence = spec['transported_raw_ferritin_low_probability']
    def low_probability(mu):
        return ((1-pi)*ndtr((np.log(ferritin_boundary)-mu)/sigma_f)
                + pi*ndtr((np.log(ferritin_boundary)-mu-delta_f)/sigma_f))
    mu_f = brentq(lambda mu: low_probability(mu)-prevalence, -5, 10, xtol=1e-12)
    nodes, weights = leggauss(int(spec['quadrature_nodes']))
    uu, ww = (nodes+1)/2, weights/2
    quadrature = []
    for infl, infl_weight in [(0,1-pi),(1,pi)]:
        cut = ndtr((np.log(ferritin_boundary)-mu_f-infl*delta_f)/sigma_f)
        for low, left, right in [(True,0.0,cut),(False,cut,1.0)]:
            u = left+(right-left)*uu
            log_store = mu_f+sigma_f*ndtri(u)
            restriction = expit(spec['restriction_exponent']*(np.log(spec['restriction_halfpoint_ug_l'])-log_store))
            for other, other_weight in [(0,1-other_p),(1,other_p)]:
                quadrature.append((low, infl, other, restriction,
                                   infl_weight*other_weight*(right-left)*ww))
    target_low = spec['source_anemia_low_ferritin_count']/spec['source_low_ferritin_count']
    target_high = spec['source_anemia_high_ferritin_count']/spec['source_high_ferritin_count']
    def equations(theta):
        base, log_amplitude = theta
        amplitude = np.exp(log_amplitude)
        joint_low, joint_high = 0.0, 0.0
        for low, infl, other, restriction, weight in quadrature:
            m = base-amplitude*restriction-hb_infl*infl-other_drop*other
            lower = ndtr(-m/hb_sd)
            p = (ndtr((hb_boundary-m)/hb_sd)-lower)/(1-lower)
            total = np.dot(weight,p)
            if low:
                joint_low += total
            else:
                joint_high += total
        return [joint_low/prevalence-target_low,
                joint_high/(1-prevalence)-target_high]
    fit = root(equations, [13.6,np.log(3.0)], tol=1e-10)
    if not fit.success or np.max(np.abs(equations(fit.x)))>1e-7:
        raise RuntimeError('Population-law calibration did not converge')
    hb_base, amplitude = float(fit.x[0]), float(np.exp(fit.x[1]))
    infl = rng.binomial(1,pi,n)
    log_store = rng.normal(mu_f,sigma_f,n)
    raw_ferritin = np.exp(log_store+infl*delta_f)
    restriction = expit(spec['restriction_exponent']*(np.log(spec['restriction_halfpoint_ug_l'])-log_store))
    other = rng.binomial(1,other_p,n)
    hb_mean = hb_base-amplitude*restriction-hb_infl*infl-other_drop*other
    hb = truncnorm.rvs(-hb_mean/hb_sd,np.inf,loc=hb_mean,scale=hb_sd,size=n,random_state=rng)
    hb = np.round(hb/spec['hb_resolution'])*spec['hb_resolution']
    ferritin = np.round(raw_ferritin/spec['ferritin_resolution'])*spec['ferritin_resolution']
    return pd.DataFrame({'row_id':np.arange(1,n+1,dtype=np.int64),
                         'hb_g_dl':hb,'ferritin_ug_l':ferritin},
                         columns=['row_id','hb_g_dl','ferritin_ug_l'])
