import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator expects observed=None.')
    model = spec['model']
    expected = ['M50', 'M60', 'F50', 'F60']
    if list(model['cell_order']) != expected:
        raise ValueError('Unexpected model cell order.')
    groups = spec['groups']
    if len(groups) != 4:
        raise ValueError('Exactly four groups are required.')
    params = model['cells']
    if len(params) != 4 or [p['cell'] for p in params] != expected:
        raise ValueError('Invalid model cell parameters.')

    anchor = model['dependence_anchor']
    ratio_mean = float(anchor['ratio_mean'])
    ratio_sd = float(anchor['ratio_sd'])
    if not np.isfinite(ratio_mean) or ratio_mean <= 0:
        raise ValueError('Invalid ratio mean.')
    if not np.isfinite(ratio_sd) or ratio_sd < 0:
        raise ValueError('Invalid ratio SD.')
    c = ratio_sd / ratio_mean
    rng = np.random.default_rng(seed)
    blocks = []
    offset = 0
    common_size = None

    for cell, group, p in zip(expected, groups, params):
        if group['cell'] != cell:
            raise ValueError('Groups must be ordered M50, M60, F50, F60.')
        right = np.asarray(group['right'], dtype=float)
        left = np.asarray(group['left'], dtype=float)
        if right.ndim != 1 or left.ndim != 1:
            raise ValueError('Marginal arrays must be one-dimensional.')
        m = right.size
        if m == 0 or left.size != m:
            raise ValueError('Each cell needs nonempty equal-length hand arrays.')
        if common_size is None:
            common_size = m
        elif m != common_size:
            raise ValueError('All four strata must have equal size.')
        if not np.all(np.isfinite(right)) or not np.all(np.isfinite(left)):
            raise ValueError('Marginal values must be finite.')
        if np.any(np.diff(right) < 0) or np.any(np.diff(left) < 0):
            raise ValueError('Marginal arrays must already be sorted.')

        moments = np.array([p['right_mean'], p['right_sd'],
                            p['left_mean'], p['left_sd']], dtype=float)
        if not np.all(np.isfinite(moments)) or np.any(moments <= 0):
            raise ValueError('Cell means and SDs must be finite and positive.')
        a = moments[1] / moments[0]
        b = moments[3] / moments[2]
        rho = (a*a + b*b - c*c) / (2.0*a*b)
        if not np.isfinite(rho) or not -1.0 <= rho <= 1.0:
            raise ValueError('Relative-asymmetry anchor implies invalid rho.')

        z = rng.standard_normal((m, 2))
        x = z[:, 0]
        y = rho*x + np.sqrt(max(0.0, 1.0-rho*rho))*z[:, 1]
        right_order = np.argsort(x, kind='mergesort')
        y_in_right_order = y[right_order]
        left_order = np.argsort(y_in_right_order, kind='mergesort')
        left_index = np.empty(m, dtype=np.int64)
        left_index[left_order] = np.arange(m, dtype=np.int64)
        blocks.append(pd.DataFrame({
            'row_id': np.arange(offset, offset+m, dtype=np.int64),
            'left_index': left_index
        }))
        offset += m

    return pd.concat(blocks, ignore_index=True)[['row_id', 'left_index']]
