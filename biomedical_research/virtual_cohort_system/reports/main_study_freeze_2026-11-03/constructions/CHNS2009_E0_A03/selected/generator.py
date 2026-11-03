"""Assumption-dependent whole-cohort shared-Gamma construction.

All scientific settings live in model_spec.json. This file is submitted for
isolated controller execution only; it has no I/O, calibration or hidden input.
"""
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires observed=None')
    p = spec['parameters']
    n = int(p['n_rows'])
    rng = np.random.default_rng(seed)
    age = rng.integers(p['age']['minimum'], p['age']['maximum'], size=n, endpoint=True)
    female = rng.binomial(1, p['female']['probability'], size=n)
    common_parameters = p['common_factor']
    common_shape = common_parameters['shape']
    common_scale = common_parameters['scale']
    common_mean = common_shape * common_scale
    common_variance = common_shape * common_scale ** 2
    common = rng.gamma(common_shape, common_scale, size=n)
    generated = {}
    for name in ('bmi', 'glucose', 'hba1c'):
        margin = p['margins'][name]
        variance = margin['sd'] ** 2
        fraction = margin['common_variance_fraction']
        loading = np.sqrt(variance * fraction / common_variance)
        residual_mean = margin['mean'] - loading * common_mean
        residual_variance = variance * (1 - fraction)
        if residual_mean <= 0 or residual_variance <= 0:
            raise ValueError('Specification cannot support positive Gamma residuals')
        residual_shape = residual_mean ** 2 / residual_variance
        residual_scale = residual_variance / residual_mean
        generated[name] = loading * common + rng.gamma(residual_shape, residual_scale, size=n)
    return pd.DataFrame({
        'row_id': ['CHNS2009_E0_A03_' + str(index + 1).zfill(4) for index in range(n)],
        'age': age,
        'female': female,
        'bmi': generated['bmi'],
        'glucose': generated['glucose'],
        'hba1c': generated['hba1c'],
    })
