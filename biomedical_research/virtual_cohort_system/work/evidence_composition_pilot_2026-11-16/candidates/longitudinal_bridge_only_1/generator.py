def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)
    means = np.asarray(model['measurement_means'], dtype=float)
    between_cov = np.asarray(model['between_person_covariance'], dtype=float)
    deviation_cov = np.asarray(model['visit_deviation_covariance'], dtype=float)

    stable = rng.standard_normal((n, 2)) @ np.linalg.cholesky(between_cov).T
    deviations = rng.standard_normal((n, 2, 2)) @ np.linalg.cholesky(deviation_cov).T
    measurements = means[None, None, :] + stable[:, None, :] + deviations

    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X_visit1': measurements[:, 0, 0],
        'Y_visit1': measurements[:, 0, 1],
        'X_visit2': measurements[:, 1, 0],
        'Y_visit2': measurements[:, 1, 1]
    }, columns=['person_id', 'X_visit1', 'Y_visit1', 'X_visit2', 'Y_visit2'])
