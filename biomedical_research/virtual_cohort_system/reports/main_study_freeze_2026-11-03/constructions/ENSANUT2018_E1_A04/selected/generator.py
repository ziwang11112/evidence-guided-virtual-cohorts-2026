"""Whole-cohort candidate. Only the controller may execute generate()."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires observed=None')
    p = spec['parameters']
    d, m, f = p['design'], p['marginals'], p['factor']
    slopes = p['source_projections']
    source_age = p['source_contexts']['lifelines']
    rng = np.random.default_rng(seed)
    ages, sexes = [], []
    for female in d['female_values']:
        for low, high in d['age_bands']:
            ages.append(rng.integers(low, high + 1, d['rows_per_cell']))
            sexes.append(np.full(d['rows_per_cell'], female, dtype=int))
    age = np.concatenate(ages)
    female = np.concatenate(sexes)
    n = len(age)
    if n != d['n_rows']:
        raise ValueError('Design quota mismatch')

    vb = m['bmi_sd'] ** 2
    vg = m['glucose_sd'] ** 2
    cov = f['bmi_loading'] * f['glucose_loading']
    determinant = vb * vg - cov ** 2
    rhs_b = slopes['bmi_age_sex'] * vb
    rhs_g = slopes['glucose_age_sex'] * vg
    beta_b = (vg * rhs_b - cov * rhs_g) / determinant
    beta_g = (vb * rhs_g - cov * rhs_b) / determinant
    residual_var_h = (m['hba1c_sd'] ** 2
                      - slopes['age_full'] ** 2 * source_age['age_sd'] ** 2
                      - beta_b ** 2 * vb - beta_g ** 2 * vg
                      - 2 * beta_b * beta_g * cov)
    if determinant <= 0 or residual_var_h <= 0 or f['positive_probability'] != 0.5:
        raise ValueError('Inadmissible specification')
    common = 2 * (rng.random(n) < f['positive_probability']).astype(int) - 1
    generated = {}
    for variable, total_variance in [('bmi', vb), ('glucose', vg)]:
        loading = f[variable + '_loading']
        low, high = p['residual_support'][variable]
        residual_variance = total_variance - loading ** 2
        concentration = (-low * high) / residual_variance - 1
        alpha = (-low / (high - low)) * concentration
        beta = (high / (high - low)) * concentration
        if alpha <= 0 or beta <= 0:
            raise ValueError('Invalid beta residual')
        residual = low + (high - low) * rng.beta(alpha, beta, n)
        generated[variable] = m[variable + '_mean'] + loading * common + residual
    hba1c = (m['hba1c_mean'] + slopes['age_full'] * (age - source_age['age_mean'])
             + beta_b * (generated['bmi'] - m['bmi_mean'])
             + beta_g * (generated['glucose'] - m['glucose_mean'])
             + np.sqrt(3 * residual_var_h) * rng.uniform(-1, 1, n))
    frame = pd.DataFrame({'row_id':[f'fictional_{i+1:04d}' for i in range(n)],
                          'age':age,'female':female,'bmi':generated['bmi'],
                          'glucose':generated['glucose'],'hba1c':hba1c},columns=d['columns'])
    return frame.iloc[rng.permutation(n)].reset_index(drop=True)
