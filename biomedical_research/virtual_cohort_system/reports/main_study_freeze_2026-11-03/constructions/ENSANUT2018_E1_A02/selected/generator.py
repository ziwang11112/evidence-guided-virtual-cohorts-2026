"""Fictional whole-cohort data. Scientific settings are supplied in model_spec."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort construction requires observed=None')
    p = spec['parameters']
    design, factor, anchors = p['design'], p['factor_law'], p['anchors']
    coef = p['conditional_coefficients']
    rng = np.random.default_rng(seed)
    ages, sexes = [], []
    for female in design['female_values']:
        for lo, hi in design['age_bands']:
            ages.append(rng.integers(lo, hi + 1, size=design['rows_per_cell']))
            sexes.append(np.full(design['rows_per_cell'], female, dtype=int))
    age = np.concatenate(ages)
    female = np.concatenate(sexes)
    n = len(age)
    alpha = factor['beta_alpha']
    # A symmetric Beta(alpha,alpha) has variance 1/[4(2 alpha+1)].
    u = (rng.beta(alpha, alpha, size=(3, n)) - 0.5) * np.sqrt(4 * (2 * alpha + 1))
    rho = factor['bmi_glucose_correlation']
    bmi = anchors['bmi_mean'] + anchors['bmi_sd'] * u[0]
    glucose = anchors['glucose_mean'] + anchors['glucose_sd'] * (rho * u[0] + np.sqrt(1-rho*rho) * u[1])
    hba1c = (anchors['hba1c_mean_at_reference']
             + coef['age'] * (age - anchors['age_reference'])
             + coef['female'] * female
             + coef['bmi'] * (bmi - anchors['bmi_mean'])
             + coef['glucose'] * (glucose - anchors['glucose_mean'])
             + p['hba1c_residual_sd'] * u[2])
    return pd.DataFrame({'row_id':[design['row_id_prefix'] + str(i + 1).zfill(5) for i in range(n)],
                         'age':age, 'female':female, 'bmi':bmi, 'glucose':glucose, 'hba1c':hba1c})
