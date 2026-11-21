import numpy as np
import pandas as pd
from statistics import NormalDist


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator expects observed=None.')
    model = spec['model']
    if model['name'] != 'within_cell_gaussian_rank_copula':
        raise ValueError('Unsupported model.')
    rho = float(model['latent_rho'])
    if not np.isfinite(rho) or not (-1.0 < rho < 1.0):
        raise ValueError('latent_rho must be finite and strictly between -1 and 1.')
    expected = ['M50', 'M60', 'F50', 'F60']
    groups = spec['groups']
    if len(groups) != 4 or [g['cell'] for g in groups] != expected:
        raise ValueError('Expected groups in order M50, M60, F50, F60.')

    validated = []
    common_size = None
    for group in groups:
        right = np.asarray(group['right'], dtype=float)
        left = np.asarray(group['left'], dtype=float)
        if right.ndim != 1 or left.ndim != 1:
            raise ValueError('Hand arrays must be one-dimensional.')
        m = right.size
        if m == 0 or left.size != m:
            raise ValueError('Each cell needs equally sized, nonempty hand arrays.')
        if common_size is None:
            common_size = m
        elif m != common_size:
            raise ValueError('The four cells must have equal sizes.')
        if not np.all(np.isfinite(right)) or not np.all(np.isfinite(left)):
            raise ValueError('Hand arrays must contain only finite values.')
        if np.any(right[1:] < right[:-1]) or np.any(left[1:] < left[:-1]):
            raise ValueError('Hand arrays must already be sorted ascending.')
        validated.append(m)

    rng = np.random.default_rng(seed)
    normal = NormalDist()
    total = sum(validated)
    left_indices = np.empty(total, dtype=np.int64)
    offset = 0
    residual_scale = np.sqrt(1.0 - rho * rho)
    for m in validated:
        z_right = np.fromiter(
            (normal.inv_cdf((i + 0.5) / m) for i in range(m)),
            dtype=float,
            count=m
        )
        latent_left = rho * z_right + residual_scale * rng.standard_normal(m)
        order = np.argsort(latent_left, kind='mergesort')
        permutation = np.empty(m, dtype=np.int64)
        permutation[order] = np.arange(m, dtype=np.int64)
        left_indices[offset:offset + m] = permutation
        offset += m

    return pd.DataFrame({
        'row_id': np.arange(total, dtype=np.int64),
        'left_index': left_indices
    }, columns=['row_id', 'left_index'])
