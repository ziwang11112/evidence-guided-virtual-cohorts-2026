import math
from statistics import NormalDist

import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator requires observed=None.')

    model = spec['model']
    if model['name'] != 'stratified_gaussian_copula_rank_pairing':
        raise ValueError('Unsupported model name.')
    rho = float(model['latent_pearson_rho'])
    if not math.isfinite(rho) or not (-1.0 < rho < 1.0):
        raise ValueError('latent_pearson_rho must be finite and strictly between -1 and 1.')

    expected_order = ['M50', 'M60', 'F50', 'F60']
    if list(model['cell_order']) != expected_order:
        raise ValueError('Unexpected model cell order.')
    groups = spec['groups']
    if len(groups) != 4:
        raise ValueError('Exactly four groups are required.')

    sizes = []
    for expected_cell, group in zip(expected_order, groups):
        if group['cell'] != expected_cell:
            raise ValueError('Groups must be ordered M50, M60, F50, F60.')
        right = np.asarray(group['right'], dtype=float)
        left = np.asarray(group['left'], dtype=float)
        if right.ndim != 1 or left.ndim != 1:
            raise ValueError('Marginal arrays must be one-dimensional.')
        if right.size == 0 or right.size != left.size:
            raise ValueError('Each group needs nonempty, equal-length marginal arrays.')
        if not np.all(np.isfinite(right)) or not np.all(np.isfinite(left)):
            raise ValueError('Marginal arrays must be finite.')
        if np.any(right[1:] < right[:-1]) or np.any(left[1:] < left[:-1]):
            raise ValueError('Marginal arrays must be sorted ascending.')
        sizes.append(int(right.size))
    if len(set(sizes)) != 1:
        raise ValueError('The four strata must have equal sizes.')

    rng = np.random.default_rng(seed)
    normal = NormalDist()
    m = sizes[0]
    probabilities = (np.arange(m, dtype=float) + 0.5) / m
    right_scores = np.fromiter(
        (normal.inv_cdf(float(p)) for p in probabilities),
        dtype=float,
        count=m,
    )
    innovation_sd = math.sqrt(1.0 - rho * rho)
    blocks = []
    for group in groups:
        left_scores = rho * right_scores + innovation_sd * rng.standard_normal(m)
        order = np.argsort(left_scores, kind='mergesort')
        left_index = np.empty(m, dtype=np.int64)
        left_index[order] = np.arange(m, dtype=np.int64)
        blocks.append(left_index)

    all_left_indices = np.concatenate(blocks)
    return pd.DataFrame({
        'row_id': np.arange(all_left_indices.size, dtype=np.int64),
        'left_index': all_left_indices,
    }, columns=['row_id', 'left_index'])
