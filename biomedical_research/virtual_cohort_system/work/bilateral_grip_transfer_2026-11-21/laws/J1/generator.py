import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('observed must be None')
    model = spec['model']
    if model['name'] != 'common_gaussian_rank_copula' or model['version'] != 1:
        raise ValueError('Unsupported model')
    expected = ['M50', 'M60', 'F50', 'F60']
    if model['cell_order'] != expected:
        raise ValueError('Invalid model cell order')
    groups = spec['groups']
    if len(groups) != 4 or [g['cell'] for g in groups] != expected:
        raise ValueError('Groups must be ordered M50, M60, F50, F60')

    par = model['dependence_parameter']
    refs = par['reference_cells']
    if len(refs) != 4 or [r['cell'] for r in refs] != expected:
        raise ValueError('Invalid reference cells')
    ratio_mean = float(par['ratio_mean'])
    ratio_sd = float(par['ratio_sd'])
    if not np.isfinite(ratio_mean) or not np.isfinite(ratio_sd) or ratio_mean <= 0 or ratio_sd < 0:
        raise ValueError('Invalid ratio summary')
    c2 = (ratio_sd / ratio_mean) ** 2
    correlations = []
    for ref in refs:
        values = np.array([ref['right_mean'], ref['right_sd'], ref['left_mean'], ref['left_sd']], dtype=float)
        if not np.all(np.isfinite(values)) or np.any(values <= 0):
            raise ValueError('Reference means and SDs must be positive and finite')
        a = values[1] / values[0]
        b = values[3] / values[2]
        correlations.append((a*a + b*b - c2) / (2*a*b))
    rho = float(np.mean(correlations))
    if not np.isfinite(rho) or not -1.0 < rho < 1.0:
        raise ValueError('Calibration gives an invalid nonsingular correlation')

    sizes = []
    for group in groups:
        right = np.asarray(group['right'], dtype=float)
        left = np.asarray(group['left'], dtype=float)
        if right.ndim != 1 or left.ndim != 1 or len(right) != len(left) or len(right) == 0:
            raise ValueError('Each group needs nonempty equal-length one-dimensional arrays')
        if not np.all(np.isfinite(right)) or not np.all(np.isfinite(left)):
            raise ValueError('Marginal values must be finite')
        if np.any(right[1:] < right[:-1]) or np.any(left[1:] < left[:-1]):
            raise ValueError('Marginal arrays must be sorted ascending')
        sizes.append(len(right))
    if len(set(sizes)) != 1:
        raise ValueError('All four strata must have equal size')

    rng = np.random.default_rng(seed)
    blocks = []
    residual_sd = np.sqrt(1.0 - rho*rho)
    for m in sizes:
        z_right = rng.standard_normal(m)
        z_left = rho*z_right + residual_sd*rng.standard_normal(m)
        right_order = np.argsort(z_right, kind='stable')
        left_order = np.argsort(z_left, kind='stable')
        left_rank = np.empty(m, dtype=np.int64)
        left_rank[left_order] = np.arange(m, dtype=np.int64)
        permutation = left_rank[right_order]
        if not np.array_equal(np.sort(permutation), np.arange(m, dtype=np.int64)):
            raise RuntimeError('Invalid generated permutation')
        blocks.append(permutation)
    left_index = np.concatenate(blocks).astype(np.int64, copy=False)
    return pd.DataFrame({'row_id': np.arange(left_index.size, dtype=np.int64), 'left_index': left_index})
