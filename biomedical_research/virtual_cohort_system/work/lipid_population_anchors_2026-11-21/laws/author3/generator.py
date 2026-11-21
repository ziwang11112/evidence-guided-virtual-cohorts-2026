import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Transform ordered marginal grids independently; rows are not person pairs."""
    if observed is not None:
        raise ValueError('observed must be None')
    n = spec['task']['n_rows']
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError('n_rows must be a positive integer')
    model = spec['model']
    result = {'row_id': np.arange(n, dtype=np.int64)}
    for key in ('tc_mg_dl', 'hdl_mg_dl'):
        x = np.asarray(spec[key], dtype=np.float64)
        if x.ndim != 1 or len(x) != n:
            raise ValueError(key + ': expected a one-dimensional grid of length n_rows')
        if not np.all(np.isfinite(x)) or not np.all(x > 0) or not np.all(x[1:] > x[:-1]):
            raise ValueError(key + ': input must be finite, positive and strictly increasing')
        anchor = float(model['anchors'][key]['value'])
        if not np.isfinite(anchor) or anchor <= 0:
            raise ValueError(key + ': invalid mean anchor')
        # Normalize first to avoid overflow when summing the original values.
        z = x / x[-1]
        y = (z / np.mean(z)) * anchor
        if not np.all(np.isfinite(y)) or not np.all(y > 0) or not np.all(y[1:] > y[:-1]):
            raise ValueError(key + ': transport exceeds floating-point resolution')
        result[key] = y
    return pd.DataFrame(result, columns=['row_id', 'tc_mg_dl', 'hdl_mg_dl'])
