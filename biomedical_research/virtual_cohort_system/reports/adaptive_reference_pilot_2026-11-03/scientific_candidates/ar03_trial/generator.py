"""Reference-assisted finite-support latent-mixture cohort, authored 2026-11-03."""
import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This whole-cohort construction accepts no individual input.')
    p = spec['parameters']
    rng = np.random.default_rng(seed)
    n = p['n_rows']
    age = rng.choice(np.asarray(p['age']['values']), size=n,
                     p=np.asarray(p['age']['probabilities']))
    female = rng.binomial(1, p['female_probability'], size=n)
    bmi = np.clip(rng.lognormal(p['bmi']['log_mu'], p['bmi']['log_sigma'], n),
                  *p['bmi']['support'])
    broad = rng.binomial(1, p['mixture_probability'], size=n)
    zg = rng.standard_normal(n)
    zi = rng.standard_normal(n)
    rho = np.asarray(p['copula_correlations'])[broad]
    zh = rho * zg + np.sqrt(1.0-rho*rho) * zi

    def margin(z, kind):
        par = p[kind]
        mus = np.asarray(par['log_mu'])[broad]
        sigs = np.asarray(par['log_sigma'])[broad]
        low, high = par['baseline_support']
        a = ndtr((np.log(low)-mus)/sigs)
        b = ndtr((np.log(high)-mus)/sigs)
        u = np.clip(a+(b-a)*ndtr(z), p['probability_epsilon'],
                    1.0-p['probability_epsilon'])
        return np.clip(np.exp(mus+sigs*ndtri(u)), low, high)

    glucose = margin(zg, 'glucose') + p['glucose_age_slope']*(age-p['age']['mean'])
    hba1c = (margin(zh, 'hba1c') + p['hba1c_age_slope']*(age-p['age']['mean'])
             + p['hba1c_bmi_slope']*(bmi-p['bmi']['mean']))
    glucose = np.round(glucose, p['measurement_decimals']['glucose'])
    hba1c = np.round(hba1c, p['measurement_decimals']['hba1c'])
    return pd.DataFrame({'row_id':[f'syn_{seed}_{i:05d}' for i in range(n)],
                         'age':age.astype(int), 'female':female.astype(int),
                         'bmi':bmi, 'glucose':glucose, 'hba1c':hba1c})
