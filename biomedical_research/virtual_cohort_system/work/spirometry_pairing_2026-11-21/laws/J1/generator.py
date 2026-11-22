import numpy as np
import pandas as pd
from statistics import NormalDist


def _repair(x, y, proposed):
    n = len(x)
    if np.all(x <= y[proposed]):
        return proposed.copy()
    if np.any(x > y):
        raise ValueError('No feasible permutation exists for these marginals.')

    # Fenwick tree of available FVC indices; all indices initially available.
    tree = np.zeros(n + 1, dtype=np.int64)
    for k in range(1, n + 1):
        tree[k] = k & -k

    def prefix(k):
        # Number available in indices [0, k).
        s = 0
        while k > 0:
            s += int(tree[k])
            k -= k & -k
        return s

    def kth(k):
        # Zero-based index of the kth available item, with k one-based.
        pos = 0
        bit = 1 << (n.bit_length() - 1)
        while bit:
            nxt = pos + bit
            if nxt <= n and tree[nxt] < k:
                k -= int(tree[nxt])
                pos = nxt
            bit >>= 1
        return pos

    def remove(j):
        k = j + 1
        while k <= n:
            tree[k] -= 1
            k += k & -k

    result = np.empty(n, dtype=np.int64)
    remaining = n
    for i in range(n - 1, -1, -1):
        low = int(np.searchsorted(y, x[i], side='left'))
        below_low = prefix(low)
        if below_low == remaining:
            raise RuntimeError('Feasibility invariant failed.')
        p = int(proposed[i])
        through_p = prefix(p + 1)
        candidates = []
        if through_p > below_low:
            candidates.append(kth(through_p))
        next_order = max(below_low, through_p) + 1
        if next_order <= remaining:
            candidates.append(kth(next_order))
        j = min(candidates, key=lambda v: (abs(v - p), v))
        result[i] = j
        remove(j)
        remaining -= 1
    return result


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator uses no target observations.')
    model = spec['model']
    groups = spec['groups']
    if len(groups) != 2 or [g['sex'] for g in groups] != ['F', 'M']:
        raise ValueError('Expected groups in F, M order.')
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
        n = len(x)
        if (not np.all(np.isfinite(x)) or not np.all(np.isfinite(y))
                or np.any(x <= 0) or np.any(y <= 0)
                or np.any(np.diff(x) < 0) or np.any(np.diff(y) < 0)):
            raise ValueError('Marginals must be positive, finite and sorted.')
        if np.any(x > y):
            raise ValueError('No feasible permutation exists for these marginals.')
        if n <= 1:
            paired = np.arange(n, dtype=np.int64)
        else:
            cx = float(np.std(x, ddof=0) / np.mean(x))
            cy = float(np.std(y, ddof=0) / np.mean(y))
            denominator = np.sqrt(np.log1p(cx * cx) * np.log1p(cy * cy))
            r = float(model['source_volume_pearson'][sex])
            if not np.isfinite(r) or not 0 <= r <= 1:
                raise ValueError('Source correlation must lie in [0,1].')
            rho = (float(np.clip(np.log1p(r * cx * cy) / denominator, 0, 1))
                   if denominator > 0 else 0.0)
            z = np.fromiter((normal.inv_cdf((i + 0.5) / n)
                             for i in range(n)), dtype=float, count=n)
            score = rho * z + np.sqrt(max(0.0, 1.0 - rho * rho)) * rng.standard_normal(n)
            proposed = np.empty(n, dtype=np.int64)
            proposed[np.argsort(score, kind='stable')] = np.arange(n, dtype=np.int64)
            paired = _repair(x, y, proposed)
        if not np.array_equal(np.sort(paired), np.arange(n)):
            raise RuntimeError('Output is not a permutation.')
        if np.any(x > y[paired]):
            raise RuntimeError('Output contains infeasible pairs.')
        blocks.append(pd.DataFrame({
            'row_id': np.arange(offset, offset + n, dtype=np.int64),
            'fvc_index': paired.astype(np.int64, copy=False)
        }))
        offset += n
    return pd.concat(blocks, ignore_index=True)[['row_id', 'fvc_index']]
