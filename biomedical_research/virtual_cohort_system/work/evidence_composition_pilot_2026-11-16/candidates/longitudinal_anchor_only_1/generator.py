import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    m = spec['model']
    rng = np.random.default_rng(seed)

    stable_sd = np.sqrt(np.asarray(m['stable_variances'], dtype=float))
    deviation_sd = np.sqrt(np.asarray(m['deviation_variances'], dtype=float))
    rb = float(m['stable_correlation'])
    rw = float(m['deviation_correlation'])
    stable_cov = np.outer(stable_sd, stable_sd) * np.array([[1.0, rb], [rb, 1.0]])
    deviation_cov = np.outer(deviation_sd, deviation_sd) * np.array([[1.0, rw], [rw, 1.0]])

    stable = rng.standard_normal((n, 2)) @ np.linalg.cholesky(stable_cov).T
    stable += np.asarray(m['stable_mean'], dtype=float)
    deviations = rng.standard_normal((n, 2, 2)) @ np.linalg.cholesky(deviation_cov).T
    deviations += np.asarray(m['deviation_mean'], dtype=float)
    visits = stable[:, None, :] + deviations

    data = {
        'person_id': np.arange(n, dtype=np.int64),
        'X_visit1': visits[:, 0, 0],
        'Y_visit1': visits[:, 0, 1],
        'X_visit2': visits[:, 1, 0],
        'Y_visit2': visits[:, 1, 1]
    }
    columns = [column['name'] for column in spec['task']['columns']]
    return pd.DataFrame(data, columns=columns)
