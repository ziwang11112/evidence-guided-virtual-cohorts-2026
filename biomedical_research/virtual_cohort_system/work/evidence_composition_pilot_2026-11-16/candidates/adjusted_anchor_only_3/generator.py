def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    model = spec['model']
    means = np.asarray(model['means'], dtype=float)
    covariance = np.asarray(model['covariance'], dtype=float)
    factor = np.linalg.cholesky(covariance)
    rng = np.random.default_rng(seed)
    values = rng.standard_normal((n, 3)) @ factor.T + means
    frame = pd.DataFrame(values, columns=model['variable_order'])
    frame.insert(0, 'person_id', np.arange(1, n + 1, dtype=np.int64))
    columns = [column['name'] for column in spec['task']['columns']]
    return frame.loc[:, columns]
