import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)
    mean = np.asarray(model['mean'], dtype=float)
    covariance = np.asarray(model['covariance'], dtype=float)
    factor = np.linalg.cholesky(covariance)
    values = rng.standard_normal((n, 3)) @ factor.T + mean
    frame = pd.DataFrame(values, columns=model['variable_order'])
    frame.insert(0, 'person_id', np.arange(n, dtype=np.int64))
    return frame.loc[:, [column['name'] for column in spec['task']['columns']]]
