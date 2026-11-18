import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    m = spec['model']
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n, 6))

    means = np.asarray(m['measurement_means'], dtype=float)
    between_sd = np.sqrt(np.asarray(m['between_person_variances'], dtype=float))
    within_sd = np.sqrt(np.asarray(m['within_person_variances'], dtype=float))
    rb = float(m['between_person_correlation'])
    rw1, rw2 = [float(r) for r in m['within_visit_correlations']]

    bx = means[0] + between_sd[0] * z[:, 0]
    by = means[1] + between_sd[1] * (rb * z[:, 0] + np.sqrt(1.0 - rb**2) * z[:, 1])

    ex1 = within_sd[0] * z[:, 2]
    ey1 = within_sd[1] * (rw1 * z[:, 2] + np.sqrt(1.0 - rw1**2) * z[:, 3])
    ex2 = within_sd[0] * z[:, 4]
    ey2 = within_sd[1] * (rw2 * z[:, 4] + np.sqrt(1.0 - rw2**2) * z[:, 5])

    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X_visit1': bx + ex1,
        'Y_visit1': by + ey1,
        'X_visit2': bx + ex2,
        'Y_visit2': by + ey2
    }, columns=['person_id', 'X_visit1', 'Y_visit1', 'X_visit2', 'Y_visit2'])
