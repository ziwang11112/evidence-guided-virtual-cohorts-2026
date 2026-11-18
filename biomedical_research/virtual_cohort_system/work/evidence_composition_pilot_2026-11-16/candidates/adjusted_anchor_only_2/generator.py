def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = spec['task']['n_rows']
    model = spec['model']
    mean = np.asarray(model['mean'], dtype=float)
    covariance = np.asarray(model['covariance'], dtype=float)
    factor = np.linalg.cholesky(covariance)
    rng = np.random.default_rng(seed)
    values = rng.standard_normal((n, 3)) @ factor.T + mean
    result = pd.DataFrame(values, columns=model['variable_order'])
    result.insert(0, 'person_id', np.arange(n, dtype=np.int64))
    return result[['person_id', 'X', 'Y', 'Z']]
