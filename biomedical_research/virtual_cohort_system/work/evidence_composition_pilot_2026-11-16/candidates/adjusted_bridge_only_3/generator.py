import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    n = int(spec['task']['n_rows'])
    m = spec['model']
    rng = np.random.default_rng(seed)
    innovations = rng.standard_normal((n, 3))
    z_noise = innovations[:, 0]
    u = innovations[:, 1]
    v = innovations[:, 2]
    rho = float(m['residual_correlation'])
    z_centered = float(m['z_sd']) * z_noise
    z = float(m['means']['Z']) + z_centered
    x = (float(m['means']['X'])
         + float(m['x_z_slope']) * z_centered
         + float(m['x_residual_sd']) * u)
    y = (float(m['means']['Y'])
         + float(m['y_z_slope']) * z_centered
         + float(m['y_residual_sd'])
         * (rho * u + np.sqrt(1.0 - rho * rho) * v))
    return pd.DataFrame({
        'person_id': np.arange(1, n + 1, dtype=np.int64),
        'X': x,
        'Y': y,
        'Z': z
    }, columns=['person_id', 'X', 'Y', 'Z'])
