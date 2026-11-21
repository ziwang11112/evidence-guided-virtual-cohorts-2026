import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Independently rescale ordered marginal grids; do not construct pairs."""
    model = spec['model']
    p = model['parameters']
    if float(p['shape_power_dimensionless']) != 1.0:
        raise ValueError('This implementation requires shape_power_dimensionless = 1.')
    n = int(spec['task']['n_rows'])
    if n < 1:
        raise ValueError('n_rows must be positive.')

    def transform(key, anchor):
        x = np.asarray(spec[key], dtype=np.float64)
        if x.ndim != 1 or len(x) != n:
            raise ValueError(key + ': expected a one-dimensional grid of length n_rows.')
        if not np.all(np.isfinite(x)) or not np.all(x > 0):
            raise ValueError(key + ': values must be finite and positive.')
        if not np.all(np.diff(x) > 0):
            raise ValueError(key + ': values must be strictly increasing.')
        anchor = float(anchor)
        if not np.isfinite(anchor) or anchor <= 0:
            raise ValueError('Anchor means must be finite and positive.')
        # Normalize before averaging to avoid overflow in the input mean.
        relative = x / x[-1]
        y = (relative / np.mean(relative)) * anchor
        if not np.all(np.isfinite(y)) or not np.all(y > 0) or not np.all(np.diff(y) > 0):
            raise ValueError(key + ': transformed grid is not representable as positive strictly increasing float64 values.')
        return y

    tc = transform('tc_mg_dl', p['tc_anchor_mean_mg_dl'])
    hdl = transform('hdl_mg_dl', p['hdl_anchor_mean_mg_dl'])
    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'tc_mg_dl': tc,
        'hdl_mg_dl': hdl
    }, columns=['row_id', 'tc_mg_dl', 'hdl_mg_dl'])
