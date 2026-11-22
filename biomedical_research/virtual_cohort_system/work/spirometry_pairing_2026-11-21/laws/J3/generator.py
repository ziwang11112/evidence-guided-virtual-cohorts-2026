import numpy as np
import pandas as pd


def _feasible_assignment(x, y, proposal):
    n = len(x)
    if np.any(x > y):
        raise ValueError('No permutation can satisfy FEV1 <= FVC for these sorted marginals.')
    # Fenwick tree of unused FVC indices, initially all available.
    tree = np.zeros(n + 1, dtype=np.int64)
    for k in range(1, n + 1):
        tree[k] = k & -k

    def prefix(k):
        # Number of available indices strictly below k.
        s = 0
        while k > 0:
            s += int(tree[k])
            k -= k & -k
        return s

    def kth(k):
        # Zero-based index of the k-th available element; k is one-based.
        pos = 0
        step = 1 << (n.bit_length() - 1)
        while step:
            nxt = pos + step
            if nxt <= n and int(tree[nxt]) < k:
                k -= int(tree[nxt])
                pos = nxt
            step >>= 1
        return pos

    out = np.empty(n, dtype=np.int64)
    remaining = n
    for i in range(n - 1, -1, -1):
        lo = int(np.searchsorted(y, x[i], side='left'))
        p = int(proposal[i])
        cut = max(lo, p)
        below_lo = prefix(lo)
        below_cut = prefix(cut)
        candidates = []
        if below_cut > below_lo:
            candidates.append(kth(below_cut))
        if below_cut < remaining:
            candidates.append(kth(below_cut + 1))
        if not candidates:
            raise RuntimeError('Feasible assignment unexpectedly failed.')
        j = min(candidates, key=lambda q: (abs(q - p), q))
        out[i] = j
        k = j + 1
        while k <= n:
            tree[k] -= 1
            k += k & -k
        remaining -= 1
    return out


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator does not use target observations.')
    model = spec['model']
    groups = spec['groups']
    if len(groups) != 2 or [g['sex'] for g in groups] != ['F', 'M']:
        raise ValueError('Expected groups in F, M order.')
    rng = np.random.default_rng(seed)
    blocks = []
    for group in groups:
        sex = group['sex']
        x = np.asarray(group['fev1'], dtype=float)
        y = np.asarray(group['fvc'], dtype=float)
        if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
            raise ValueError('Marginals must be equal-length one-dimensional arrays.')
        if (not np.all(np.isfinite(x)) or not np.all(np.isfinite(y))
                or np.any(x <= 0) or np.any(y <= 0)
                or np.any(np.diff(x) < 0) or np.any(np.diff(y) < 0)):
            raise ValueError('Marginals must be finite, positive and sorted.')
        n = len(x)
        if n == 0:
            blocks.append(np.empty(0, dtype=np.int64))
            continue
        if np.any(x > y):
            raise ValueError('No feasible permutation exists for this sex.')
        moments = model['reference_moments_l'][sex]
        a = moments['fev1_sd'] / moments['fev1_mean']
        b = moments['fvc_sd'] / moments['fvc_mean']
        target_r = float(model['reference_pearson'][sex])
        rho = float(np.log1p(target_r * a * b) /
                    np.sqrt(np.log1p(a * a) * np.log1p(b * b)))
        if not np.isfinite(rho) or not -1 <= rho <= 1:
            raise ValueError('Invalid latent correlation.')
        z = rng.standard_normal((n, 2))
        u = z[:, 0]
        v = rho * u + np.sqrt(max(0.0, 1.0 - rho * rho)) * z[:, 1]
        order_u = np.argsort(u, kind='stable')
        order_v = np.argsort(v, kind='stable')
        ranks_v = np.empty(n, dtype=np.int64)
        ranks_v[order_v] = np.arange(n, dtype=np.int64)
        proposal = ranks_v[order_u]
        assignment = _feasible_assignment(x, y, proposal)
        if (not np.array_equal(np.sort(assignment), np.arange(n))
                or np.any(x > y[assignment])):
            raise RuntimeError('Output validation failed.')
        blocks.append(assignment)
    indices = np.concatenate(blocks).astype(np.int64, copy=False)
    return pd.DataFrame({'row_id': np.arange(len(indices), dtype=np.int64),
                         'fvc_index': indices})
