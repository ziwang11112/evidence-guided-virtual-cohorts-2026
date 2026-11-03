"""Finite-factor whole-cohort scenario. Execute only through the task controller."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires observed=None')
    p = spec['parameters']
    rng = np.random.default_rng(seed)
    bands = np.asarray(p['age_bands'], dtype=int)
    band_means = (bands[:, 0] + bands[:, 1]) / 2.0
    band_variances = ((bands[:, 1] - bands[:, 0] + 1.0) ** 2 - 1.0) / 12.0
    age_mean = band_means.mean()
    age_sd = np.sqrt(np.mean(band_variances + (band_means - age_mean) ** 2))
    ages = []
    females = []
    for female in p['female_values']:
        for low, high in bands:
            ages.append(rng.integers(low, high + 1, size=p['rows_per_cell']))
            females.append(np.full(p['rows_per_cell'], female, dtype=int))
    age = np.concatenate(ages)
    female = np.concatenate(females)
    n = len(age)
    a = (age - age_mean) / age_sd
    s = (female - np.mean(p['female_values'])) / np.std(p['female_values'])
    shape = p['residual_beta_shape']
    z = (rng.beta(shape, shape, size=(n, 3)) - 0.5) * np.sqrt(4.0 * (2.0 * shape + 1.0))
    ub, ug, uh = z[:, 0], z[:, 1], z[:, 2]
    b = p['bmi_loadings']
    g = p['glucose_loadings']
    h = p['hba1c_loadings']
    rb = np.sqrt(1.0 - sum(x*x for x in b.values()))
    rg = np.sqrt(1.0 - sum(x*x for x in g.values()))
    rh = np.sqrt(1.0 - sum(x*x for x in h.values()))
    bmi = p['bmi_mean'] + p['bmi_sd'] * (b['age']*a + b['female']*s + rb*ub)
    glucose = p['glucose_mean'] + p['glucose_sd'] * (g['age']*a + g['female']*s + g['bmi_factor']*ub + rg*ug)
    hba1c = p['hba1c_mean'] + p['hba1c_sd'] * (h['age']*a + h['female']*s + h['bmi_factor']*ub + h['glucose_factor']*ug + rh*uh)
    frame = pd.DataFrame({'row_id':[p['row_id_prefix'] + str(i+1).zfill(4) for i in range(n)], 'age':age, 'female':female, 'bmi':bmi, 'glucose':glucose, 'hba1c':hba1c}, columns=p['columns'])
    return frame.iloc[rng.permutation(n)].reset_index(drop=True)
