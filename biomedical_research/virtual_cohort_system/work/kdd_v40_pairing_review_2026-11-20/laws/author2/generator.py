import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    # observed is intentionally unused: only the supplied evidence is used.
    m = spec['model']
    scenario = spec['scenario']
    if scenario not in ('a', 'b'):
        raise ValueError('scenario must be a or b')
    t = np.asarray(spec['tc_mg_dl'], dtype=np.float64)
    h = np.asarray(spec['hdl_mg_dl'], dtype=np.float64)
    n = int(spec['task']['n_rows'])
    if t.ndim != 1 or h.ndim != 1 or len(t) != n or len(h) != n or n < 2:
        raise ValueError('Array lengths must equal n_rows >= 2')
    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(h))):
        raise ValueError('Nonfinite lipid value')
    if np.any(t <= 0) or np.any(h <= 0):
        raise ValueError('Lipids must be positive')
    if np.any(np.diff(t) < 0) or np.any(np.diff(h) < 0):
        raise ValueError('Arrays must be ascending')
    if np.any(h > t):
        raise ValueError('No permutation can satisfy HDL <= TC everywhere')

    target = float(m['ratio_target'])
    tol = float(m['maximum_absolute_ratio_error'])
    threshold = float(m['nonhdl_threshold_mg_dl'])
    rng = np.random.default_rng(seed)
    rank = np.arange(n, dtype=np.int64)
    block = int(m['local_rank_shuffle_block_size'])
    if block < 1:
        raise ValueError('Invalid shuffle block size')
    for start in range(0, n, block):
        rng.shuffle(rank[start:min(start + block, n)])

    def evaluate(direction, displacement):
        p = (rank + direction * int(displacement)) % n
        repairs = 0
        if np.any(h[p] > t):
            pos = np.empty(n, dtype=np.int64)
            pos[p] = np.arange(n, dtype=np.int64)
            smallest = 0
            for i in range(n):
                if h[p[i]] <= t[i]:
                    continue
                while smallest < n and pos[smallest] < i:
                    smallest += 1
                if smallest == n or h[smallest] > t[i]:
                    raise RuntimeError('Constraint repair failed')
                j = int(pos[smallest])
                old = int(p[i])
                p[i], p[j] = smallest, old
                pos[smallest], pos[old] = i, j
                repairs += 1
        ratio = float(np.mean(t / h[p]))
        return ratio, p, repairs, int(displacement)

    def calibrate(direction):
        lo, hi = 0, n // 2
        left = evaluate(direction, lo)
        right = evaluate(direction, hi)
        best = min((left, right), key=lambda x: abs(x[0] - target))
        if (left[0] - target) * (right[0] - target) > 0:
            raise RuntimeError('Ratio target not bracketed for this rank-cycle family')
        # Sign bracketing does not require assuming global monotonicity.
        while hi - lo > 1:
            mid = (lo + hi) // 2
            cur = evaluate(direction, mid)
            if abs(cur[0] - target) < abs(best[0] - target):
                best = cur
            if (left[0] - target) * (cur[0] - target) <= 0:
                hi, right = mid, cur
            else:
                lo, left = mid, cur
        center = best[3]
        for k in range(max(0, center - 3), min(n // 2, center + 3) + 1):
            cur = evaluate(direction, k)
            if abs(cur[0] - target) < abs(best[0] - target):
                best = cur
        ratio, p, repairs, displacement = best
        if abs(ratio - target) > tol:
            raise RuntimeError('Empirical ratio tolerance not achieved')
        if np.any(h[p] > t) or not np.array_equal(np.sort(p), np.arange(n)):
            raise RuntimeError('Invalid pairing')
        nonhdl = t - h[p]
        summary = {
            'mean_individual_ratio': ratio,
            'mean_nonhdl_mg_dl': float(np.mean(nonhdl)),
            'fraction_nonhdl_ge_160': float(np.mean(nonhdl >= threshold)),
            'cycle_displacement': displacement,
            'cycle_displacement_fraction': float(displacement / n),
            'constraint_repair_swaps': repairs,
            'maximum_hdl_minus_tc_mg_dl': float(np.max(h[p] - t)),
            'permutation_valid': True
        }
        return p, summary

    # Evaluate both assumptions; their threshold fractions never guide calibration.
    results = {}
    summaries = {}
    for label in ('a', 'b'):
        direction = int(m['scenarios'][label]['direction'])
        results[label], summaries[label] = calibrate(direction)
    gap = abs(summaries['a']['fraction_nonhdl_ge_160'] - summaries['b']['fraction_nonhdl_ge_160'])
    out = pd.DataFrame({
        'row_id': np.arange(n, dtype=np.int64),
        'hdl_index': results[scenario].astype(np.int64, copy=False)
    })
    out.attrs['diagnostics'] = {
        'scenario_summaries': summaries,
        'absolute_threshold_fraction_difference': float(gap),
        'absolute_threshold_difference_percentage_points': float(100 * gap),
        'exceeds_consequential_difference': bool(gap > float(m['consequential_absolute_fraction_difference'])),
        'fixed_marginal_mean_nonhdl_mg_dl': float(np.mean(t) - np.mean(h)),
        'ratio_tolerance_implies_three_seed_mean_in_required_interval': bool(tol < 0.005)
    }
    return out
