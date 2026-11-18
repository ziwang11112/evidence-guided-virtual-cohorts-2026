import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)
    means = np.asarray(model['means'], dtype=float)
    covariance = np.asarray(model['covariance'], dtype=float)
    factor = np.linalg.cholesky(covariance)
    draws = rng.standard_normal((n, len(means))) @ factor.T + means
    frame = pd.DataFrame(draws, columns=model['variables'])
    frame.insert(0, 'person_id', np.arange(1, n + 1, dtype=np.int64))
    return frame.loc[:, [column['name'] for column in spec['task']['columns']]]
