def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    model = spec['model']
    mean = np.asarray(model['mean'], dtype=float)
    covariance = np.asarray(model['covariance'], dtype=float)
    factor = np.linalg.cholesky(covariance)
    rng = np.random.default_rng(seed)
    innovations = rng.standard_normal((n, len(mean)))
    values = mean + innovations @ factor.T
    result = pd.DataFrame(values, columns=model['variable_order'])
    result.insert(0, 'person_id', np.arange(1, n + 1, dtype=np.int64))
    return result.loc[:, [column['name'] for column in spec['task']['columns']]]
