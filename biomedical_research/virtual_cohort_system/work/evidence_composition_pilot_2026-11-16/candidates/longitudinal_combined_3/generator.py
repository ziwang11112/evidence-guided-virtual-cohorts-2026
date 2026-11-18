def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    m = spec['model']
    rng = np.random.default_rng(seed)
    means = np.asarray(m['means'], dtype=float)
    bv = np.asarray(m['between_person_variances'], dtype=float)
    wv = np.asarray(m['within_person_variances'], dtype=float)
    rb = float(m['between_person_correlation'])
    rw = float(m['within_visit_deviation_correlation'])

    z_stable = rng.standard_normal((n, 2))
    z_visit = rng.standard_normal((n, 2, 2))

    stable_x = means[0] + np.sqrt(bv[0]) * z_stable[:, 0]
    stable_y = means[1] + np.sqrt(bv[1]) * (
        rb * z_stable[:, 0] + np.sqrt(1.0 - rb * rb) * z_stable[:, 1]
    )
    deviation_x = np.sqrt(wv[0]) * z_visit[:, :, 0]
    deviation_y = np.sqrt(wv[1]) * (
        rw * z_visit[:, :, 0] + np.sqrt(1.0 - rw * rw) * z_visit[:, :, 1]
    )
    x = stable_x[:, None] + deviation_x
    y = stable_y[:, None] + deviation_y

    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X_visit1': x[:, 0],
        'Y_visit1': y[:, 0],
        'X_visit2': x[:, 1],
        'Y_visit2': y[:, 1]
    }, columns=['person_id', 'X_visit1', 'Y_visit1', 'X_visit2', 'Y_visit2'])
