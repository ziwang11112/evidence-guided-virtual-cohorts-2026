import numpy as np
import pandas as pd
from statistics import NormalDist


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('observed must be None')
    model = spec['model']
    if model['name'] != 'within_cell_gaussian_copula':
        raise ValueError('Unsupported model')
    rho = float(model['dependence']['latent_correlation'])
    if not np.isfinite(rho) or not (-1.0 < rho < 1.0):
        raise ValueError('Latent correlation must be strictly between -1 and 1')
    groups = spec['groups']
    cells = ['M50', 'M60', 'F50', 'F60']
    if len(groups) != 4 or [g['cell'] for g in groups] != cells:
        raise ValueError('Expected groups in M50, M60, F50, F60 order')

    validated = []
    common_size = None
    for g in groups:
        right = np.asarray(g['right'], dtype=float)
        left = np.asarray(g['left'], dtype=float)
        if right.ndim != 1 or left.ndim != 1:
            raise ValueError('Hand arrays must be one-dimensional')
        m = len(right)
        if m == 0 or len(left) != m:
            raise ValueError('Each cell needs equally sized, nonempty hand arrays')
        if common_size is None:
            common_size = m
        elif m != common_size:
            raise ValueError('All four strata must have the same size')
        if not np.isfinite(right).all() or not np.isfinite(left).all():
            raise ValueError('Hand values must be finite')
        if np.any(right[1:] < right[:-1]) or np.any(left[1:] < left[:-1]):
            raise ValueError('Hand arrays must be sorted ascending')
        validated.append(m)

    rng = np.random.default_rng(seed)
    normal = NormalDist()
    output = []
    offset = 0
    for m in validated:
        u = (np.arange(m, dtype=float) + 0.5) / m
        z_right = np.fromiter((normal.inv_cdf(float(p)) for p in u),
                              dtype=float, count=m)
        score = rho * z_right + np.sqrt(1.0 - rho * rho) * rng.standard_normal(m)
        # score_order lists right-row positions in ascending latent left order.
        score_order = np.lexsort((np.arange(m, dtype=np.int64), score))
        left_index = np.empty(m, dtype=np.int64)
        left_index[score_order] = np.arange(m, dtype=np.int64)
        output.append(pd.DataFrame({
            'row_id': np.arange(offset, offset + m, dtype=np.int64),
            'left_index': left_index
        }))
        offset += m
    return pd.concat(output, ignore_index=True)[['row_id', 'left_index']]
