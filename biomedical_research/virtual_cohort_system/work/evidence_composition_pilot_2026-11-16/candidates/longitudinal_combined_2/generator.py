import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)
    mean = np.asarray(model['measurement_mean'], dtype=float)
    between = np.asarray(model['between_covariance'], dtype=float)
    within = np.asarray(model['within_covariance'], dtype=float)
    between_factor = np.linalg.cholesky(between)
    within_factor = np.linalg.cholesky(within)

    stable = rng.standard_normal((n, 2)) @ between_factor.T
    deviation1 = rng.standard_normal((n, 2)) @ within_factor.T
    deviation2 = rng.standard_normal((n, 2)) @ within_factor.T
    visit1 = mean + stable + deviation1
    visit2 = mean + stable + deviation2

    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X_visit1': visit1[:, 0],
        'Y_visit1': visit1[:, 1],
        'X_visit2': visit2[:, 0],
        'Y_visit2': visit2[:, 1]
    })
