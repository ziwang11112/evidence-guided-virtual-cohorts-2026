import heapq
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator requires observed=None.')
    model = spec['model']
    groups = spec['groups']
    if len(groups) != 2 or [g['sex'] for g in groups] != ['F', 'M']:
        raise ValueError('Expected two groups in order F, M.')
    rng = np.random.default_rng(seed)
    blocks = []
    offset = 0
    for group in groups:
        sex = group['sex']
        a = np.asarray(group['fev1'], dtype=float)
        b = np.asarray(group['fvc'], dtype=float)
        if a.ndim != 1 or b.ndim != 1 or len(a) != len(b) or len(a) == 0:
            raise ValueError('Each sex requires equally sized, nonempty 1D arrays.')
        if not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
            raise ValueError('Volumes must be finite.')
        if np.any(a <= 0) or np.any(b <= 0):
            raise ValueError('Volumes must be positive.')
        if np.any(a[1:] < a[:-1]) or np.any(b[1:] < b[:-1]):
            raise ValueError('Marginal arrays must be sorted ascending.')
        if np.any(a > b):
            raise ValueError('No feasible permutation exists for sex ' + sex)
        rho = float(model['latent_rho_by_sex'][sex])
        if not np.isfinite(rho) or not (-1.0 <= rho <= 1.0):
            raise ValueError('Latent rho must lie in [-1, 1].')
        m = len(a)
        z = np.sort(rng.standard_normal(m))
        scores = rho * z + np.sqrt(max(0.0, 1.0 - rho * rho)) * rng.standard_normal(m)
        assignment = np.full(m, -1, dtype=np.int64)
        eligible = []
        next_i = 0
        for j in range(m):
            while next_i < m and a[next_i] <= b[j]:
                heapq.heappush(eligible, (float(scores[next_i]), next_i))
                next_i += 1
            if not eligible:
                raise RuntimeError('Feasibility invariant failed.')
            _, i = heapq.heappop(eligible)
            assignment[i] = j
        if not np.array_equal(np.sort(assignment), np.arange(m)):
            raise RuntimeError('Assignment is not a permutation.')
        if np.any(a > b[assignment]):
            raise RuntimeError('Assignment violates FEV1 <= FVC.')
        blocks.append(pd.DataFrame({
            'row_id': np.arange(offset, offset + m, dtype=np.int64),
            'fvc_index': assignment
        }))
        offset += m
    return pd.concat(blocks, ignore_index=True)[['row_id', 'fvc_index']]
