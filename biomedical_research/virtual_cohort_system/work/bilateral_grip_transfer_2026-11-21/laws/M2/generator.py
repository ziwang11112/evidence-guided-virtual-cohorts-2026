import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator expects observed=None.')
    model = spec['model']
    if model.get('name') != 'Gaussian-copula bilateral pairing with fixed marginal grids':
        raise ValueError('Unexpected model.')
    if model.get('version') != 1 or model.get('copula') != 'Gaussian':
        raise ValueError('Unsupported model version or copula.')
    rho = float(model['latent_correlation'])
    if not math.isfinite(rho) or rho != 0.8:
        raise ValueError('This primary model requires latent_correlation=0.8.')
    expected = ['M50', 'M60', 'F50', 'F60']
    if model.get('cell_order') != expected:
        raise ValueError('Unexpected model cell order.')
    groups = spec['groups']
    if len(groups) != 4 or [g['cell'] for g in groups] != expected:
        raise ValueError('Expected groups in order M50, M60, F50, F60.')

    arrays = []
    sizes = []
    for group in groups:
        right = np.asarray(group['right'], dtype=float)
        left = np.asarray(group['left'], dtype=float)
        if right.ndim != 1 or left.ndim != 1:
            raise ValueError('Marginal arrays must be one-dimensional.')
        if len(right) != len(left) or len(right) == 0:
            raise ValueError('Each cell must have equal, positive marginal lengths.')
        if not np.all(np.isfinite(right)) or not np.all(np.isfinite(left)):
            raise ValueError('Marginal values must be finite.')
        if np.any(right[1:] < right[:-1]) or np.any(left[1:] < left[:-1]):
            raise ValueError('Marginal arrays must already be sorted ascending.')
        arrays.append((right, left))
        sizes.append(len(right))
    if len(set(sizes)) != 1:
        raise ValueError('The four cells must have equal sizes.')

    rng = np.random.default_rng(seed)
    normal = NormalDist()
    m = sizes[0]
    z_right = np.fromiter(
        (normal.inv_cdf((i + 0.5) / m) for i in range(m)),
        dtype=float, count=m
    )
    residual_scale = math.sqrt(1.0 - rho * rho)
    blocks = []
    for right, left in arrays:
        latent_left = rho * z_right + residual_scale * rng.standard_normal(m)
        ascending_positions = np.argsort(latent_left, kind='mergesort')
        left_index = np.empty(m, dtype=np.int64)
        left_index[ascending_positions] = np.arange(m, dtype=np.int64)
        if not np.array_equal(np.sort(left_index), np.arange(m, dtype=np.int64)):
            raise RuntimeError('Internal permutation check failed.')
        blocks.append(left_index)

    indices = np.concatenate(blocks).astype(np.int64, copy=False)
    return pd.DataFrame({
        'row_id': np.arange(len(indices), dtype=np.int64),
        'left_index': indices
    }, columns=['row_id', 'left_index'])
