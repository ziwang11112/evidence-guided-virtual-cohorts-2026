import heapq
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This generator does not use target observations.')
    model = spec['model']
    groups = spec['groups']
    if len(groups) != 2 or [g['sex'] for g in groups] != ['F', 'M']:
        raise ValueError('Expected groups in F, M order.')

    rng = np.random.default_rng(seed)
    normal = NormalDist()
    blocks = []

    for group in groups:
        sex = group['sex']
        x = np.asarray(group['fev1'], dtype=float)
        y = np.asarray(group['fvc'], dtype=float)
        if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
            raise ValueError('Each group requires equal-length one-dimensional arrays.')
        n = len(x)
        if (not np.all(np.isfinite(x)) or not np.all(np.isfinite(y))
                or np.any(x <= 0) or np.any(y <= 0)):
            raise ValueError('Volumes must be finite and positive.')
        if np.any(np.diff(x) < 0) or np.any(np.diff(y) < 0):
            raise ValueError('Marginal arrays must be sorted ascending.')
        # For sorted equal-length arrays this is necessary and sufficient
        # for a permutation satisfying x[i] <= y[permutation[i]].
        if np.any(x > y):
            raise ValueError('No feasible permutation exists for these marginals.')
        if n == 0:
            blocks.append(np.empty(0, dtype=np.int64))
            continue

        moments = model['source_moments_l'][sex]
        cvx = moments['fev1_sd'] / moments['fev1_mean']
        cvy = moments['fvc_sd'] / moments['fvc_mean']
        r = float(model['pearson_anchor'][sex])
        rho = np.log1p(r * cvx * cvy) / np.sqrt(
            np.log1p(cvx * cvx) * np.log1p(cvy * cvy))
        if not np.isfinite(rho) or abs(rho) > 1.0 + 1e-12:
            raise ValueError('Invalid latent correlation.')
        rho = float(np.clip(rho, -1.0, 1.0))
        z = np.fromiter(
            (normal.inv_cdf((i + 0.5) / n) for i in range(n)),
            dtype=float, count=n)
        priority = rho * z + np.sqrt(max(0.0, 1.0 - rho * rho)) * rng.standard_normal(n)

        permutation = np.empty(n, dtype=np.int64)
        eligible = []
        next_x = 0
        for j in range(n):
            while next_x < n and x[next_x] <= y[j]:
                heapq.heappush(eligible, (float(priority[next_x]), next_x))
                next_x += 1
            if not eligible:
                raise RuntimeError('Feasible-assignment invariant failed.')
            _, i = heapq.heappop(eligible)
            permutation[i] = j

        if not np.array_equal(np.sort(permutation), np.arange(n)):
            raise RuntimeError('Output is not a permutation.')
        if np.any(x > y[permutation]):
            raise RuntimeError('Output violates FEV1 <= FVC.')
        blocks.append(permutation)

    indices = np.concatenate(blocks).astype(np.int64, copy=False)
    return pd.DataFrame({
        'row_id': np.arange(len(indices), dtype=np.int64),
        'fvc_index': indices
    })
