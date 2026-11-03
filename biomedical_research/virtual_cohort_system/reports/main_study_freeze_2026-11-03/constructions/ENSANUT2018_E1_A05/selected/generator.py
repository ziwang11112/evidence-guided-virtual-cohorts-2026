"""Bounded affine cohort law. File/network access and calibration are absent."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires observed=None')
    p = spec['parameters']
    d = p['design']
    rng = np.random.default_rng(seed)
    ages, sexes = [], []
    for female in d['female_values']:
        for low, high in d['age_bands']:
            ages.append(rng.integers(low, high + 1, size=d['rows_per_cell']))
            sexes.append(np.full(d['rows_per_cell'], female, dtype=int))
    age = np.concatenate(ages)
    female = np.concatenate(sexes)
    n = len(age)
    if n != d['n_rows']:
        raise ValueError('Design row count is inconsistent')
    shape = p['latent']['shape']
    z = (2 * rng.beta(shape, shape, size=(n, 3)) - 1) * np.sqrt(2 * shape + 1)
    c, v, s, h = p['centers'], p['covariate_effects'], p['residual_scales'], p['response']
    ac, fc = age - c['age'], female - c['female']
    rho = v['residual_correlation']
    bmi = c['bmi'] + v['bmi_age'] * ac + v['bmi_female'] * fc + s['bmi'] * z[:, 0]
    glucose = c['glucose'] + v['glucose_age'] * ac + v['glucose_female'] * fc + s['glucose'] * (rho * z[:, 0] + np.sqrt(1 - rho**2) * z[:, 1])
    hba1c = c['hba1c'] + h['age'] * ac + h['female'] * fc + h['bmi'] * (bmi - c['bmi']) + h['glucose'] * (glucose - c['glucose']) + s['hba1c'] * z[:, 2]
    frame = pd.DataFrame({'row_id':[d['row_id_prefix'] + str(i + 1).zfill(4) for i in range(n)], 'age':age, 'female':female, 'bmi':bmi, 'glucose':glucose, 'hba1c':hba1c})
    return frame
