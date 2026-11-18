import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    m = spec['model']
    rng = np.random.default_rng(seed)
    innovations = rng.standard_normal((n, 3))
    z_standard = innovations[:, 0]
    u = innovations[:, 1]
    v = innovations[:, 2]
    a = float(m['correlation_xz'])
    b = float(m['correlation_yz'])
    r = float(m['residual_correlation_xy'])
    x_standard = a * z_standard + np.sqrt(1.0 - a * a) * u
    y_residual_standard = r * u + np.sqrt(1.0 - r * r) * v
    y_standard = b * z_standard + np.sqrt(1.0 - b * b) * y_residual_standard
    means = m['means']
    variances = m['variances']
    return pd.DataFrame({
        'person_id': np.arange(n, dtype=np.int64),
        'X': means['X'] + np.sqrt(variances['X']) * x_standard,
        'Y': means['Y'] + np.sqrt(variances['Y']) * y_standard,
        'Z': means['Z'] + np.sqrt(variances['Z']) * z_standard
    }, columns=['person_id', 'X', 'Y', 'Z'])
