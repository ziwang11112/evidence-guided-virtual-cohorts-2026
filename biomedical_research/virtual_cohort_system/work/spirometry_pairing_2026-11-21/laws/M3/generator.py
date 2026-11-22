import heapq
from statistics import NormalDist
import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    rng = np.random.default_rng(seed)
    model = spec['model']
    normal = NormalDist()
    row_blocks = []
    index_blocks = []
    offset = 0

    for group in spec['groups']:
        sex = group['sex']
        a = np.asarray(group['fev1'], dtype=float)
        b = np.asarray(group['fvc'], dtype=float)
        if a.ndim != 1 or b.ndim != 1 or len(a) != len(b):
            raise ValueError('Each sex requires equal-length one-dimensional margins.')
        if (not np.all(np.isfinite(a)) or not np.all(np.isfinite(b))
                or np.any(a <= 0) or np.any(b <= 0)
                or np.any(a[1:] < a[:-1]) or np.any(b[1:] < b[:-1])):
            raise ValueError('Margins must be finite, positive, and sorted.')
        n = len(a)
        rho = float(model['latent_rank_correlation'][sex])
        if not -1.0 <= rho <= 1.0:
            raise ValueError('Invalid latent correlation.')

        if n:
            u = (np.arange(n, dtype=float) + 0.5) / n
            z = np.fromiter((normal.inv_cdf(float(v)) for v in u),
                            dtype=float, count=n)
            scores = rho * z + np.sqrt(max(0.0, 1.0-rho*rho)) * rng.standard_normal(n)
            if np.all(a <= b):
                pairing = np.empty(n, dtype=np.int64)
                eligible = []
                j = n - 1
                for i in range(n - 1, -1, -1):
                    while j >= 0 and b[j] >= a[i]:
                        heapq.heappush(eligible, (-float(scores[j]), int(j)))
                        j -= 1
                    if not eligible:
                        raise RuntimeError('Unexpected failure of feasible assignment.')
                    _, chosen = heapq.heappop(eligible)
                    pairing[i] = chosen
                if np.any(a > b[pairing]):
                    raise RuntimeError('Internal feasibility check failed.')
            else:
                # Increasing scores are paired with increasing FEV1.
                pairing = np.argsort(scores, kind='stable').astype(np.int64)
            if not np.array_equal(np.sort(pairing), np.arange(n)):
                raise RuntimeError('Output is not a permutation.')
        else:
            pairing = np.empty(0, dtype=np.int64)

        row_blocks.append(np.arange(offset, offset+n, dtype=np.int64))
        index_blocks.append(pairing)
        offset += n

    rows = np.concatenate(row_blocks) if row_blocks else np.empty(0, dtype=np.int64)
    indices = np.concatenate(index_blocks) if index_blocks else np.empty(0, dtype=np.int64)
    return pd.DataFrame({'row_id': rows, 'fvc_index': indices})
