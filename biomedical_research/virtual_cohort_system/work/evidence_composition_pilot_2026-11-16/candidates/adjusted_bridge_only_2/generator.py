def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    m = spec['model']
    rng = np.random.default_rng(seed)
    z, u, v = rng.standard_normal((3, n))

    a = float(m['corr_xz'])
    b = float(m['corr_yz'])
    r = float(m['residual_correlation'])
    x_std = a * z + np.sqrt(1.0 - a * a) * u
    y_std = b * z + np.sqrt(1.0 - b * b) * (r * u + np.sqrt(1.0 - r * r) * v)

    means = m['means']
    variances = m['variances']
    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X': float(means['X']) + np.sqrt(float(variances['X'])) * x_std,
        'Y': float(means['Y']) + np.sqrt(float(variances['Y'])) * y_std,
        'Z': float(means['Z']) + np.sqrt(float(variances['Z'])) * z
    }, columns=['person_id', 'X', 'Y', 'Z'])
