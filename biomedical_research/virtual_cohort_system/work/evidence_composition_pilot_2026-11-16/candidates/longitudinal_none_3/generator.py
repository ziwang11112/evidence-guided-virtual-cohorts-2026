def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    model = spec['model']
    rng = np.random.default_rng(seed)
    means = np.asarray(model['means'], dtype=float)
    between_sd = np.sqrt(np.asarray(model['between_person_variances'], dtype=float))
    within_sd = np.sqrt(np.asarray(model['within_person_variances'], dtype=float))
    rb = float(model['between_person_correlation'])
    rw = float(model['within_visit_deviation_correlation'])
    between_cov = np.outer(between_sd, between_sd) * np.array([[1.0, rb], [rb, 1.0]])
    within_cov = np.outer(within_sd, within_sd) * np.array([[1.0, rw], [rw, 1.0]])

    stable = rng.multivariate_normal(means, between_cov, size=n)
    deviations = rng.multivariate_normal(np.zeros(2), within_cov, size=(n, 2))
    visit1 = stable + deviations[:, 0, :]
    visit2 = stable + deviations[:, 1, :]

    return pd.DataFrame({
        'person_id': np.arange(n, dtype=np.int64),
        'X_visit1': visit1[:, 0],
        'Y_visit1': visit1[:, 1],
        'X_visit2': visit2[:, 0],
        'Y_visit2': visit2[:, 1]
    }, columns=['person_id', 'X_visit1', 'Y_visit1', 'X_visit2', 'Y_visit2'])
