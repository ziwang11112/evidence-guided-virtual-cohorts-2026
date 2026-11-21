import numpy as np
import pandas as pd
from statistics import NormalDist


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator expects observed=None.')
    model = spec['model']
    if model['law'] != 'within_cell_gaussian_copula_rank_permutation':
        raise ValueError('Unsupported model law.')
    rho = float(model['rho'])
    if not np.isfinite(rho) or not (-1.0 < rho < 1.0):
        raise ValueError('rho must be finite and strictly between -1 and 1.')
    expected = ['M50', 'M60', 'F50', 'F60']
    if list(model['cell_order']) != expected:
        raise ValueError('Unexpected model cell order.')
    groups = spec['groups']
    if len(groups) != 4:
        raise ValueError('Exactly four groups are required.')

    validated = []
    common_m = None
    for cell, group in zip(expected, groups):
        if group['cell'] != cell:
            raise ValueError('Groups must be ordered M50, M60, F50, F60.')
        right = np.asarray(group['right'], dtype=float)
        left = np.asarray(group['left'], dtype=float)
        if right.ndim != 1 or left.ndim != 1:
            raise ValueError('Hand arrays must be one-dimensional.')
        m = len(right)
        if m == 0 or len(left) != m:
            raise ValueError('Each cell requires equal, nonempty hand arrays.')
        if common_m is None:
            common_m = m
        elif m != common_m:
            raise ValueError('All cells must have equal size.')
        if not (np.isfinite(right).all() and np.isfinite(left).all()):
            raise ValueError('Hand arrays must contain only finite values.')
        if np.any(right[1:] < right[:-1]) or np.any(left[1:] < left[:-1]):
            raise ValueError('Hand arrays must be sorted ascending.')
        validated.append(m)

    rng = np.random.default_rng(seed)
    normal = NormalDist()
    scale = np.sqrt(1.0 - rho * rho)
    blocks = []
    offset = 0
    for m in validated:
        z_right = np.fromiter(
            (normal.inv_cdf((i + 0.5) / m) for i in range(m)),
            dtype=float, count=m
        )
        latent_left = rho * z_right + scale * rng.standard_normal(m)
        order = np.argsort(latent_left, kind='mergesort')
        left_index = np.empty(m, dtype=np.int64)
        left_index[order] = np.arange(m, dtype=np.int64)
        if not np.array_equal(np.sort(left_index), np.arange(m, dtype=np.int64)):
            raise RuntimeError('Internal permutation check failed.')
        blocks.append(pd.DataFrame({
            'row_id': np.arange(offset, offset + m, dtype=np.int64),
            'left_index': left_index
        }))
        offset += m
    return pd.concat(blocks, ignore_index=True)[['row_id', 'left_index']]
