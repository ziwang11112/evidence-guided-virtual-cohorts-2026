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
        raise ValueError('Expected two groups in F, M order.')
    rng = np.random.default_rng(seed)
    nd = NormalDist()
    row_blocks = []
    index_blocks = []
    offset = 0

    for group in groups:
        sex = group['sex']
        x = np.asarray(group['fev1'], dtype=float)
        y = np.asarray(group['fvc'], dtype=float)
        if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
            raise ValueError('Each group must have equally sized one-dimensional arrays.')
        if (not np.all(np.isfinite(x)) or not np.all(np.isfinite(y))
                or np.any(x <= 0) or np.any(y <= 0)):
            raise ValueError('Volumes must be finite and positive.')
        if np.any(np.diff(x) < 0) or np.any(np.diff(y) < 0):
            raise ValueError('Marginal arrays must be sorted ascending.')
        m = len(x)
        assignment = np.arange(m, dtype=np.int64)

        if m > 1 and np.all(x <= y):
            moments = model['source_moments_l'][sex]
            cvx = moments['fev1_sd'] / moments['fev1_mean']
            cvy = moments['fvc_sd'] / moments['fvc_mean']
            r = float(model['source_pearson_anchor'][sex])
            rho = np.log1p(r * cvx * cvy) / np.sqrt(
                np.log1p(cvx * cvx) * np.log1p(cvy * cvy))
            if not np.isfinite(rho) or not (-1.0 <= rho <= 1.0):
                raise ValueError('Invalid latent correlation.')
            z = np.fromiter(
                (nd.inv_cdf((i + 0.5) / m) for i in range(m)),
                dtype=float, count=m)
            scores = rho * z + np.sqrt(max(0.0, 1.0 - rho * rho)) * rng.standard_normal(m)
            proposed_order = np.argsort(scores, kind='stable')
            priority = np.empty(m, dtype=np.int64)
            priority[proposed_order] = np.arange(m, dtype=np.int64)

            # Assign each ascending FVC to the highest-priority eligible row.
            eligible = []
            next_row = 0
            for j in range(m):
                while next_row < m and x[next_row] <= y[j]:
                    heapq.heappush(eligible, (int(priority[next_row]), next_row))
                    next_row += 1
                if not eligible:
                    raise RuntimeError('Unexpected failure of feasible assignment.')
                _, i = heapq.heappop(eligible)
                assignment[i] = j

        if not np.array_equal(np.sort(assignment), np.arange(m)):
            raise RuntimeError('Output is not a permutation.')
        if np.all(x <= y) and np.any(x > y[assignment]):
            raise RuntimeError('Feasibility repair failed.')
        row_blocks.append(np.arange(offset, offset + m, dtype=np.int64))
        index_blocks.append(assignment)
        offset += m

    return pd.DataFrame({
        'row_id': np.concatenate(row_blocks).astype(np.int64, copy=False),
        'fvc_index': np.concatenate(index_blocks).astype(np.int64, copy=False)
    })
