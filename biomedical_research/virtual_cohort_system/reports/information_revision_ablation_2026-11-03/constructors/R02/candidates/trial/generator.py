"""Five-variable cohort from an explicitly assumed positive-support mixture.

This program is executed only by the coordinator's isolated harness.
"""
import math
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('Whole-cohort generation requires observed=None')
    p = spec['parameters']
    n = int(p['n_rows'])
    rng = np.random.default_rng(seed)
    component = rng.binomial(1, p['high_component_probability'], size=n)
    independent_normals = rng.standard_normal((n, 4))
    latent = np.empty((n, 4), dtype=float)
    for k in (0, 1):
        selected = component == k
        cholesky = np.linalg.cholesky(np.asarray(p['latent_correlations'][k], dtype=float))
        latent[selected] = independent_normals[selected] @ cholesky.T
    age_u = np.fromiter((0.5 * (1.0 + math.erf(v / math.sqrt(2.0)))
                        for v in latent[:, 0]), dtype=float, count=n)
    age_probabilities = np.asarray(p['age_probabilities'], dtype=float)
    age_values = np.asarray(p['age_values'], dtype=int)
    age_index = np.searchsorted(np.cumsum(age_probabilities), age_u, side='right')
    age = age_values[np.minimum(age_index, len(age_values) - 1)]
    female = rng.binomial(1, p['female_probability'], size=n).astype(int)
    bmi = np.exp(p['bmi_log_mean'] + p['bmi_log_sd'] * latent[:, 1])
    gp = np.asarray(p['glucose_log_parameters'], dtype=float).reshape(2, 2)
    hp = np.asarray(p['hba1c_log_parameters'], dtype=float).reshape(2, 2)
    glucose = np.exp(gp[component, 0] + gp[component, 1] * latent[:, 2])
    hba1c = np.exp(hp[component, 0] + hp[component, 1] * latent[:, 3])
    return pd.DataFrame({
        'row_id': [f'R02_{seed}_{i:05d}' for i in range(n)],
        'age': age,
        'female': female,
        'bmi': bmi,
        'glucose': glucose,
        'hba1c': hba1c,
    }, columns=['row_id', 'age', 'female', 'bmi', 'glucose', 'hba1c'])
