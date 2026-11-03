"""Whole-cohort scenario; scientific settings and provenance are in model_spec.json."""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires observed=None')
    p = spec['parameters']
    if p['continuous_family'] != 'one_factor_multivariate_lognormal':
        raise ValueError('Unsupported declared continuous family')
    if p['demographic_dependence'] != 'age_and_female_mutually_independent_and_independent_of_continuous_variables':
        raise ValueError('Unsupported demographic dependence declaration')
    if p['age_support']['distribution'] != 'discrete_uniform_inclusive':
        raise ValueError('Unsupported age distribution')
    rng = np.random.default_rng(seed)
    n = p['n_rows']
    age = rng.integers(p['age_support']['minimum'], p['age_support']['maximum'] + 1, size=n)
    female = rng.binomial(1, p['female_probability'], size=n)
    common = rng.standard_normal(n)
    continuous = {}
    for variable in ('bmi', 'glucose', 'hba1c'):
        margin = p['marginal_moments'][variable]
        mean, sd = margin['mean'], margin['individual_sd']
        sigma2 = np.log1p((sd / mean) ** 2)
        mu = np.log(mean) - sigma2 / 2
        loading = p['factor_loadings'][variable]
        z = loading * common + np.sqrt(1 - loading ** 2) * rng.standard_normal(n)
        continuous[variable] = np.exp(mu + np.sqrt(sigma2) * z)
    return pd.DataFrame({
        'row_id': [f'virtual_{i + 1:06d}' for i in range(n)],
        'age': age,
        'female': female,
        'bmi': continuous['bmi'],
        'glucose': continuous['glucose'],
        'hba1c': continuous['hba1c'],
    })
