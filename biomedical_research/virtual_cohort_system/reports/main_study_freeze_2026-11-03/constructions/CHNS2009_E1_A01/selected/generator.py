"""Target-table generator. Execute only through the coordinator's frozen adapter."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort construction requires observed=None')
    p = spec['parameters']
    c = p['target']
    n = p['n_rows']
    rng = np.random.default_rng(seed)
    age = rng.integers(c['age_min'], c['age_max'] + 1, size=n)
    female = rng.binomial(1, c['female_probability'], size=n)
    ac = age-c['age_mean']
    fc = female-c['female_probability']
    u_b, u_g, u_h = rng.uniform(-np.sqrt(3.0), np.sqrt(3.0), size=(3, n))
    r = c['residual_bmi_glucose_correlation']
    b_res = c['bmi_residual_sd']*u_b
    g_res = c['glucose_residual_sd']*(r*u_b+np.sqrt(1-r*r)*u_g)
    high = rng.binomial(1, c['excess_probability'], size=n)
    excess = high*rng.lognormal(np.log(c['excess_mean'])-0.5*c['excess_log_sd']**2,
                               c['excess_log_sd'], size=n)
    bmi = c['bmi_mean']+c['bmi_age']*ac+c['bmi_female']*fc+b_res
    glucose = c['glucose_mean']+c['glucose_age']*ac+c['glucose_female']*fc+g_res+excess
    hba1c = (c['hba1c_mean']+c['hba1c_age']*ac+c['hba1c_female']*fc
             +c['hba1c_bmi_residual_slope']*b_res+c['hba1c_glucose_residual_slope']*g_res
             +c['excess_hba1c_slope']*excess+c['hba1c_residual_sd']*u_h)
    return pd.DataFrame({'row_id':[p['row_id_prefix']+str(i+1).zfill(6) for i in range(n)],
                         'age':age,'female':female,'bmi':bmi,'glucose':glucose,'hba1c':hba1c})
