def generate(observed, spec, seed):
    import numpy as np
    import pandas as pd

    n = spec['task']['n_rows']
    m = spec['model']
    a = float(m['rho_xz'])
    b = float(m['rho_yz'])
    r = float(m['partial_xy_given_z'])
    if not (-1.0 < a < 1.0 and -1.0 < b < 1.0 and -1.0 < r < 1.0):
        raise ValueError('Scenario correlations must lie strictly between -1 and 1.')
    means = np.asarray(m['means'], dtype=float)
    variances = np.asarray(m['variances'], dtype=float)
    if means.shape != (3,) or variances.shape != (3,) or np.any(variances <= 0):
        raise ValueError('Expected three means and three positive variances.')

    rng = np.random.default_rng(seed)
    z, u, v = rng.standard_normal((3, n))
    x = a * z + np.sqrt(1.0 - a * a) * u
    y = b * z + np.sqrt(1.0 - b * b) * (r * u + np.sqrt(1.0 - r * r) * v)
    values = np.column_stack((x, y, z))
    values = means + values * np.sqrt(variances)
    result = pd.DataFrame(values, columns=['X', 'Y', 'Z'])
    result.insert(0, 'person_id', np.arange(n, dtype=np.int64))
    return result[['person_id', 'X', 'Y', 'Z']]
