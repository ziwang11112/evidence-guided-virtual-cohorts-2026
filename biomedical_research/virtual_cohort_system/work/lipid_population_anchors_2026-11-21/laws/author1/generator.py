import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    # Deterministic marginal-only transformation; observed and seed are unused.
    n = int(spec['task']['n_rows'])
    if n < 1:
        raise ValueError('n_rows must be positive')
    model = spec['model']
    columns = {}
    for name, constant_name in (
        ('tc_mg_dl', 'tc_reference_mean_mg_dl'),
        ('hdl_mg_dl', 'hdl_reference_mean_mg_dl'),
    ):
        x = np.asarray(spec[name], dtype=np.float64)
        if x.ndim != 1 or x.size != n:
            raise ValueError(name + ': expected a one-dimensional list of length n_rows')
        if not np.all(np.isfinite(x)) or not np.all(x > 0):
            raise ValueError(name + ': values must be finite and positive')
        if not np.all(np.diff(x) > 0):
            raise ValueError(name + ': values must be strictly increasing')
        target = float(model['constants'][constant_name]['value'])
        if not np.isfinite(target) or target <= 0:
            raise ValueError('Reference means must be finite and positive')
        # Normalize before summation to avoid overflow in the grid mean.
        scaled = x / x[-1]
        relative_mean = float(np.mean(scaled))
        y = (scaled / relative_mean) * target
        if not np.all(np.isfinite(y)) or not np.all(y > 0) or not np.all(np.diff(y) > 0):
            raise ValueError(name + ': output is not representable as a positive strictly increasing float64 grid')
        columns[name] = y
    # Common row positions are quantile positions, not within-person pairs.
    return pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'tc_mg_dl': columns['tc_mg_dl'],
        'hdl_mg_dl': columns['hdl_mg_dl'],
    }, columns=['row_id', 'tc_mg_dl', 'hdl_mg_dl'])
