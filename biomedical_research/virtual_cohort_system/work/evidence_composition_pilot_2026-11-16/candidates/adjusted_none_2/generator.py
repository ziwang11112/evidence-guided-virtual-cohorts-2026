def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    m = spec['model']
    rng = np.random.default_rng(seed)
    a = float(m['xz_loading'])
    b = float(m['yz_loading'])
    r = float(m['residual_xy_correlation'])
    means = np.asarray(m['means'], dtype=float)
    variances = np.asarray(m['variances'], dtype=float)
    if means.shape != (3,) or variances.shape != (3,):
        raise ValueError('Means and variances must follow X, Y, Z order.')
    if np.any(variances <= 0) or not (abs(a) < 1 and abs(b) < 1 and abs(r) < 1):
        raise ValueError('Positive variances and nonsingular correlation parameters are required.')

    innovations = rng.standard_normal((n, 3))
    z0 = innovations[:, 0]
    u = innovations[:, 1]
    v = innovations[:, 2]
    x0 = a * z0 + np.sqrt(1.0 - a * a) * u
    y0 = b * z0 + np.sqrt(1.0 - b * b) * (r * u + np.sqrt(1.0 - r * r) * v)
    scales = np.sqrt(variances)
    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X': means[0] + scales[0] * x0,
        'Y': means[1] + scales[1] * y0,
        'Z': means[2] + scales[2] * z0
    }, columns=['person_id', 'X', 'Y', 'Z'])
