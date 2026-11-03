"""Whole-cohort generator. Scientific execution belongs to the isolated controller."""
import numpy as np
import pandas as pd

def _standard_beta(rng, shape, size):
    a, b = shape
    mean = a / (a + b)
    sd = np.sqrt(a * b / ((a + b)**2 * (a + b + 1)))
    return (rng.beta(a, b, size=size) - mean) / sd

def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('whole_cohort requires observed=None')
    p = spec['parameters']
    d = p['design']
    rng = np.random.default_rng(seed)
    ages, females = [], []
    for female in d['female_values']:
        for low, high in d['age_bands']:
            ages.append(rng.integers(low, high + 1, size=d['rows_per_cell']))
            females.append(np.full(d['rows_per_cell'], female, dtype=int))
    age = np.concatenate(ages)
    female = np.concatenate(females)
    n = len(age)
    factors = p['factor_distributions']
    u = _standard_beta(rng, factors['bmi_beta'], n)
    v = _standard_beta(rng, factors['glucose_beta'], n)
    if factors['hba1c_residual'] != 'standardized_uniform':
        raise ValueError('unknown residual law')
    w = rng.uniform(-np.sqrt(3.0), np.sqrt(3.0), size=n)
    rho = p['bmi_glucose_rho']
    bmi = p['bmi_location_scale']['mean'] + p['bmi_location_scale']['sd'] * u
    glucose = p['glucose_location_scale']['mean'] + p['glucose_location_scale']['sd'] * (rho*u + np.sqrt(1-rho*rho)*v)
    hba1c = (p['hba1c_reference']['mean'] + p['age_slope']*(age-p['hba1c_reference']['age'])
             + p['female_slope']*female
             + p['joint_hba1c_slopes']['bmi']*(bmi-p['bmi_location_scale']['mean'])
             + p['joint_hba1c_slopes']['glucose']*(glucose-p['glucose_location_scale']['mean'])
             + p['hba1c_residual_sd']*w)
    return pd.DataFrame({'row_id':[d['row_id_prefix'] + str(i+1).zfill(4) for i in range(n)],
                         'age':age, 'female':female, 'bmi':bmi, 'glucose':glucose, 'hba1c':hba1c})
