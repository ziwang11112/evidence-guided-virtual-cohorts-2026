import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)
    mean = np.asarray(model['mean'], dtype=float)
    between = np.asarray(model['between_covariance'], dtype=float)
    within = np.asarray(model['within_covariance'], dtype=float)

    stable = rng.multivariate_normal(
        np.zeros(2), between, size=n, check_valid='raise'
    )
    deviations = rng.multivariate_normal(
        np.zeros(2), within, size=(n, 2), check_valid='raise'
    )
    visits = mean[None, None, :] + stable[:, None, :] + deviations

    return pd.DataFrame({
        'person_id': np.arange(n, dtype=np.int64),
        'X_visit1': visits[:, 0, 0],
        'Y_visit1': visits[:, 0, 1],
        'X_visit2': visits[:, 1, 0],
        'Y_visit2': visits[:, 1, 1]
    })
