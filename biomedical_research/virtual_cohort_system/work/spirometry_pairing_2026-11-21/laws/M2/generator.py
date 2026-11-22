import numpy as np
import pandas as pd
from statistics import NormalDist


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator does not use target observations.')
    model = spec['model']
    groups = spec['groups']
    if len(groups) != 2 or [g['sex'] for g in groups] != ['F', 'M']:
        raise ValueError('Expected two groups ordered F, M.')
    sweeps = int(model['sweeps'])
    if sweeps < 0 or sweeps != model['sweeps']:
        raise ValueError('sweeps must be a nonnegative integer.')
    rng = np.random.default_rng(seed)
    normal = NormalDist()
    blocks = []
    offset = 0
    for group in groups:
        sex = group['sex']
        x = np.asarray(group['fev1'], dtype=float)
        y = np.asarray(group['fvc'], dtype=float)
        if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
            raise ValueError('Marginals must be equal-length one-dimensional arrays.')
        m = len(x)
        if (not np.all(np.isfinite(x)) or not np.all(np.isfinite(y))
                or np.any(x <= 0) or np.any(y <= 0)):
            raise ValueError('Marginals must be finite and positive.')
        if np.any(x[1:] < x[:-1]) or np.any(y[1:] < y[:-1]):
            raise ValueError('Marginals must be ascending.')
        # For sorted arrays, this condition is necessary and sufficient
        # for existence of a permutation satisfying every x <= paired y.
        if np.any(x > y):
            raise ValueError('No fully feasible permutation exists for sex ' + sex)
        rho = float(model['rho_by_sex'][sex])
        if not np.isfinite(rho) or not 0 <= rho < 1:
            raise ValueError('rho must lie in [0, 1).')
        beta = rho / (1.0 - rho * rho)
        p = np.arange(m, dtype=np.int64)
        if m > 1:
            z = np.fromiter(
                (normal.inv_cdf((i + 0.5) / m) for i in range(m)),
                dtype=float, count=m)
            for _ in range(sweeps):
                proposals = rng.integers(0, m, size=(m, 2))
                for i, j in proposals:
                    if i == j:
                        continue
                    a, b = int(p[i]), int(p[j])
                    if x[i] > y[b] or x[j] > y[a]:
                        continue
                    log_accept = beta * (z[i] - z[j]) * (z[b] - z[a])
                    if log_accept >= 0 or rng.random() < np.exp(log_accept):
                        p[i], p[j] = b, a
        if not np.array_equal(np.sort(p), np.arange(m)):
            raise RuntimeError('Invalid permutation.')
        if np.any(x > y[p]):
            raise RuntimeError('Infeasible output pairing.')
        blocks.append(pd.DataFrame({
            'row_id': np.arange(offset, offset + m, dtype=np.int64),
            'fvc_index': p
        }))
        offset += m
    return pd.concat(blocks, ignore_index=True)[['row_id', 'fvc_index']]
