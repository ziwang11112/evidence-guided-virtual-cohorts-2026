def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = int(spec['task']['n_rows'])
    model = spec['model']
    a = float(model['z_loading_x'])
    b = float(model['z_loading_y'])
    rho = float(model['residual_correlation'])
    if not (-1.0 < a < 1.0 and -1.0 < b < 1.0 and -1.0 <= rho <= 1.0):
        raise ValueError('Invalid standardized model parameters')

    rng = np.random.default_rng(seed)
    latent = rng.standard_normal((n, 3))
    z = latent[:, 0]
    u = latent[:, 1]
    v = latent[:, 2]
    x = a * z + np.sqrt(1.0 - a * a) * u
    y = b * z + np.sqrt(1.0 - b * b) * (rho * u + np.sqrt(1.0 - rho * rho) * v)

    return pd.DataFrame(
        {'person_id': np.arange(n, dtype=np.int64), 'X': x, 'Y': y, 'Z': z},
        columns=['person_id', 'X', 'Y', 'Z']
    )
