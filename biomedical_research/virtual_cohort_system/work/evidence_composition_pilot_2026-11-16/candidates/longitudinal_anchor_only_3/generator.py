def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)

    means = np.asarray(model['stable_means'], dtype=float)
    between_var = np.asarray(model['between_person_variances'], dtype=float)
    within_var = np.asarray(model['within_person_variances'], dtype=float)
    between_r = float(model['stable_correlation'])
    within_r = float(model['within_visit_deviation_correlation'])

    between_cov = np.diag(between_var)
    between_cov[0, 1] = between_cov[1, 0] = between_r * np.sqrt(between_var[0] * between_var[1])
    within_cov = np.diag(within_var)
    within_cov[0, 1] = within_cov[1, 0] = within_r * np.sqrt(within_var[0] * within_var[1])

    stable = rng.standard_normal((n, 2)) @ np.linalg.cholesky(between_cov).T + means
    deviations = rng.standard_normal((n, 2, 2)) @ np.linalg.cholesky(within_cov).T
    visits = stable[:, None, :] + deviations

    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X_visit1': visits[:, 0, 0],
        'Y_visit1': visits[:, 0, 1],
        'X_visit2': visits[:, 1, 0],
        'Y_visit2': visits[:, 1, 1]
    }, columns=['person_id', 'X_visit1', 'Y_visit1', 'X_visit2', 'Y_visit2'])
