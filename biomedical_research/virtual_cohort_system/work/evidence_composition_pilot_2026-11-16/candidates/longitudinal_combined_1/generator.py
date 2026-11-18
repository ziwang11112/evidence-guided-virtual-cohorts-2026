def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)
    mean = np.asarray(model['component_mean'], dtype=float)
    component_cov = np.asarray(model['component_covariance'], dtype=float)
    deviation_cov = np.asarray(model['deviation_covariance'], dtype=float)
    component_factor = np.linalg.cholesky(component_cov)
    deviation_factor = np.linalg.cholesky(deviation_cov)

    components = mean + rng.standard_normal((n, 2)) @ component_factor.T
    deviations = rng.standard_normal((n, 2, 2)) @ deviation_factor.T
    visits = components[:, None, :] + deviations

    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X_visit1': visits[:, 0, 0],
        'Y_visit1': visits[:, 0, 1],
        'X_visit2': visits[:, 1, 0],
        'Y_visit2': visits[:, 1, 1]
    }, columns=['person_id', 'X_visit1', 'Y_visit1', 'X_visit2', 'Y_visit2'])
