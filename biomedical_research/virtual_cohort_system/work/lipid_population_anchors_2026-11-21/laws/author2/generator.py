import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    """Transform ordered marginals independently; output rows are not paired people."""
    if observed is not None:
        raise ValueError('observed must be None')
    n_raw = spec['task']['n_rows']
    n = int(n_raw)
    if n < 1 or n != n_raw:
        raise ValueError('n_rows must be a positive integer')
    model = spec['model']
    targets = model['target_mean_mg_dl']
    output = {'row_id': np.arange(n, dtype=np.int64)}
    for column in ('tc_mg_dl', 'hdl_mg_dl'):
        x = np.asarray(spec[column], dtype=np.float64)
        if x.ndim != 1 or len(x) != n:
            raise ValueError(column + ': expected one ordered value per row')
        if not np.all(np.isfinite(x)) or np.any(x <= 0):
            raise ValueError(column + ': values must be finite and positive')
        if np.any(x[1:] <= x[:-1]):
            raise ValueError(column + ': values must be strictly increasing')
        target = float(targets[column])
        if not np.isfinite(target) or target <= 0:
            raise ValueError(column + ': target mean must be finite and positive')
        # Scaling by the maximum avoids overflow in computing the grid mean.
        relative = x / x[-1]
        y = (relative / np.mean(relative)) * target
        if not np.all(np.isfinite(y)) or np.any(y <= 0):
            raise ValueError(column + ': numerical range prevents positive finite output')
        if np.any(y[1:] <= y[:-1]):
            raise ValueError(column + ': floating-point precision prevents strict ordering')
        output[column] = y
    return pd.DataFrame(output, columns=['row_id', 'tc_mg_dl', 'hdl_mg_dl'])
