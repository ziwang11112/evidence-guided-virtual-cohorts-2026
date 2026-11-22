import math
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator does not use observed target data.')
    model = spec['model']
    groups = spec['groups']
    if len(groups) != 2 or [g['sex'] for g in groups] != ['F', 'M']:
        raise ValueError('Expected groups in order F, M.')
    sweeps = int(model['sweeps'])
    if sweeps < 0:
        raise ValueError('sweeps must be nonnegative.')
    rng = np.random.default_rng(seed)
    normal = NormalDist()
    blocks = []
    offset = 0
    for g in groups:
        x = np.asarray(g['fev1'], dtype=float)
        y = np.asarray(g['fvc'], dtype=float)
        if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
            raise ValueError('Each sex needs equally sized one-dimensional arrays.')
        if (not np.all(np.isfinite(x)) or not np.all(np.isfinite(y))
                or np.any(x <= 0) or np.any(y <= 0)):
            raise ValueError('Volumes must be finite and positive.')
        if np.any(np.diff(x) < 0) or np.any(np.diff(y) < 0):
            raise ValueError('Marginal arrays must be sorted.')
        m = len(x)
        rho = float(model['latent_rank_rho'][g['sex']])
        if not 0.0 <= rho < 1.0:
            raise ValueError('rho must lie in [0, 1).')
        # For sorted arrays, a feasible matching exists iff x[i] <= y[i].
        if np.any(x > y):
            raise ValueError('No permutation can satisfy FEV1 <= FVC for this sex.')
        p = np.arange(m, dtype=np.int64)
        if m > 1:
            z = np.fromiter(
                (normal.inv_cdf((i + 0.5) / m) for i in range(m)),
                dtype=float, count=m
            )
            coefficient = rho / (1.0 - rho * rho)
            for _ in range(sweeps):
                proposals = rng.integers(0, m, size=(m, 2))
                for pair in proposals:
                    i, j = int(pair[0]), int(pair[1])
                    if i == j:
                        continue
                    a, b = int(p[i]), int(p[j])
                    if x[i] > y[b] or x[j] > y[a]:
                        continue
                    log_accept = coefficient * (z[i] - z[j]) * (z[b] - z[a])
                    if log_accept >= 0.0 or rng.random() < math.exp(log_accept):
                        p[i], p[j] = b, a
        if not np.array_equal(np.sort(p), np.arange(m)):
            raise RuntimeError('Internal permutation failure.')
        if np.any(x > y[p]):
            raise RuntimeError('Internal feasibility failure.')
        blocks.append(pd.DataFrame({
            'row_id': np.arange(offset, offset + m, dtype=np.int64),
            'fvc_index': p
        }))
        offset += m
    return pd.concat(blocks, ignore_index=True)[['row_id', 'fvc_index']]
