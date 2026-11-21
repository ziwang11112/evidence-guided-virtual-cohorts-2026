import numpy as np
import pandas as pd
from statistics import NormalDist


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator expects observed=None.')
    model = spec['model']
    groups = spec['groups']
    order = model['cell_order']
    if len(groups) != 4 or [g['cell'] for g in groups] != order:
        raise ValueError('Expected four groups in M50, M60, F50, F60 order.')

    cells = model['calibration_cells']
    if [c['cell'] for c in cells] != order:
        raise ValueError('Calibration cells have the wrong order.')
    a = np.array([c['right_sd'] / c['right_mean'] for c in cells], dtype=float)
    b = np.array([c['left_sd'] / c['left_mean'] for c in cells], dtype=float)
    weights = np.asarray(model['cell_weights'], dtype=float)
    if weights.shape != (4,) or not np.allclose(weights, np.full(4, 0.25)):
        raise ValueError('This model requires equal cell weights.')
    ref = model['external_ratio_summary']
    if ref['mean'] <= 0 or ref['sd'] < 0:
        raise ValueError('Invalid reference ratio summary.')
    tau2 = np.log1p((ref['sd'] / ref['mean']) ** 2)
    A = float(np.dot(weights, a*a + b*b))
    B = float(np.dot(weights, 2*a*b))
    if B <= 0:
        raise ValueError('Invalid calibration denominator.')
    rho = (A - tau2) / B
    if not np.isfinite(rho) or not (-1.0 < rho < 1.0):
        raise ValueError('Calibration does not give a nondegenerate correlation; no clipping is applied.')

    arrays = []
    sizes = []
    for g in groups:
        right = np.asarray(g['right'], dtype=float)
        left = np.asarray(g['left'], dtype=float)
        if right.ndim != 1 or left.ndim != 1 or len(right) != len(left):
            raise ValueError('Each group requires equal-length one-dimensional margins.')
        if len(right) == 0:
            raise ValueError('Each group must be nonempty.')
        if not np.all(np.isfinite(right)) or not np.all(np.isfinite(left)):
            raise ValueError('Marginal values must be finite.')
        if np.any(right[1:] < right[:-1]) or np.any(left[1:] < left[:-1]):
            raise ValueError('Marginal arrays must already be sorted.')
        arrays.append((right, left))
        sizes.append(len(right))
    if len(set(sizes)) != 1:
        raise ValueError('The four strata must have equal size.')

    rng = np.random.default_rng(seed)
    normal = NormalDist()
    residual_sd = np.sqrt(1.0 - rho*rho)
    permutations = []
    for right, left in arrays:
        m = len(right)
        probabilities = (np.arange(m, dtype=float) + 0.5) / m
        z_right = np.fromiter((normal.inv_cdf(float(p)) for p in probabilities), dtype=float, count=m)
        latent_left = rho*z_right + residual_sd*rng.standard_normal(m)
        ascending_rows = np.argsort(latent_left, kind='mergesort')
        permutation = np.empty(m, dtype=np.int64)
        permutation[ascending_rows] = np.arange(m, dtype=np.int64)
        if not np.array_equal(np.sort(permutation), np.arange(m, dtype=np.int64)):
            raise RuntimeError('Internal permutation check failed.')
        permutations.append(permutation)

    left_indices = np.concatenate(permutations).astype(np.int64, copy=False)
    return pd.DataFrame({
        'row_id': np.arange(len(left_indices), dtype=np.int64),
        'left_index': left_indices
    }, columns=['row_id', 'left_index'])
