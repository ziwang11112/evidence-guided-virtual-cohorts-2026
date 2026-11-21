import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    scenario = spec['scenario']
    if scenario not in ('a', 'b'):
        raise ValueError('scenario must be a or b')
    t = np.asarray(spec['tc_mg_dl'], dtype=np.float64)
    h = np.asarray(spec['hdl_mg_dl'], dtype=np.float64)
    n = int(spec['task']['n_rows'])
    if t.ndim != 1 or h.ndim != 1 or len(t) != n or len(h) != n or n < 2:
        raise ValueError('Incompatible array lengths')
    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(h))):
        raise ValueError('Nonfinite input')
    if np.any(t <= 0) or np.any(h <= 0) or np.any(np.diff(t) < 0) or np.any(np.diff(h) < 0):
        raise ValueError('Inputs must be positive ascending arrays')
    if np.any(h > t):
        raise ValueError('No feasible HDL<=TC permutation exists for these sorted inputs')
    target = float(m['ratio_target'])
    threshold = float(m['threshold_mg_dl'])
    tol = float(m['final_ratio_tolerance'])
    band = float(m['optimization_ratio_band']) * n
    invh = 1.0 / h

    def proposals(p, rng):
        order = rng.permutation(n)
        i = order[:2*(n//2):2]
        j = order[1:2*(n//2):2]
        a, b = p[i], p[j]
        valid = (h[b] <= t[i]) & (h[a] <= t[j])
        ds = (t[i] - t[j]) * (invh[b] - invh[a])
        return i, j, a, b, valid, ds

    def apply(p, i, j, a, b, take):
        p[i[take]] = b[take]
        p[j[take]] = a[take]

    def calibrate(p, rng):
        # Disjoint feasible swaps move the ratio sum toward its target,
        # without crossing it. No marginal values are modified.
        for unused in range(int(m['calibration_sweeps'])):
            gap = target*n - float(np.sum(t*invh[p]))
            if abs(gap)/n <= tol/4.0:
                return
            i, j, a, b, valid, ds = proposals(p, rng)
            direction = 1.0 if gap > 0 else -1.0
            ix = np.flatnonzero(valid & (direction*ds > 0))
            if ix.size:
                cs = np.cumsum(direction*ds[ix])
                k = int(np.searchsorted(cs, abs(gap), side='right'))
                take = np.zeros(len(i), dtype=bool)
                take[ix[:k]] = True
                # A small residual may admit a later, smaller swap.
                residual = abs(gap) - (float(cs[k-1]) if k else 0.0)
                rest = ix[k:]
                fitting = rest[direction*ds[rest] <= residual]
                if fitting.size:
                    take[fitting[np.argmax(direction*ds[fitting])]] = True
                apply(p, i, j, a, b, take)
        if abs(float(np.mean(t*invh[p])) - target) > tol:
            raise RuntimeError('Ratio calibration failed; no result returned')

    # Common feasible initialization for the two scenarios.
    rng0 = np.random.default_rng(seed)
    initial = np.arange(n, dtype=np.int64)
    for unused in range(int(m['initial_randomization_sweeps'])):
        i, j, a, b, valid, ds = proposals(initial, rng0)
        apply(initial, i, j, a, b, valid)
    calibrate(initial, rng0)

    def fit(direction):
        p = initial.copy()
        # Common random proposals make the scenario contrast reproducible.
        rng = np.random.default_rng(seed)
        ratio_sum = float(np.sum(t*invh[p]))
        for unused in range(int(m['optimization_sweeps'])):
            i, j, a, b, valid, ds = proposals(p, rng)
            old = (t[i]-h[a] >= threshold).astype(np.int8)
            old += (t[j]-h[b] >= threshold).astype(np.int8)
            new = (t[i]-h[b] >= threshold).astype(np.int8)
            new += (t[j]-h[a] >= threshold).astype(np.int8)
            gain = direction*(new-old)
            neutral = valid & (gain == 0)
            take = valid & ((gain > 0) | (neutral & (rng.random(len(i)) < float(m['neutral_move_probability']))))
            residual = ratio_sum - target*n + float(np.sum(ds[take]))

            # Balance ratio changes first using count-neutral swaps, then
            # by withdrawing proposed moves. Every accepted move has
            # nonnegative threshold-count gain in the chosen direction.
            for mode in (0, 1):
                if residual == 0:
                    break
                sign = 1.0 if residual > 0 else -1.0
                if mode == 0:
                    ix = np.flatnonzero(neutral & ~take & (sign*ds < 0))
                    weights = -sign*ds[ix]
                else:
                    ix0 = np.flatnonzero(take & (gain == 0) & (sign*ds > 0))
                    ix1 = np.flatnonzero(take & (gain > 0) & (sign*ds > 0))
                    ix = np.concatenate((ix0, ix1))
                    weights = sign*ds[ix]
                if not ix.size:
                    continue
                cs = np.cumsum(weights)
                k = int(np.searchsorted(cs, abs(residual), side='right'))
                chosen = ix[:k]
                if mode == 0:
                    take[chosen] = True
                else:
                    take[chosen] = False
                residual -= sign*(float(cs[k-1]) if k else 0.0)
                # Also use one smaller move if the prefix left a gap.
                rest = ix[k:]
                wr = weights[k:]
                fits = np.flatnonzero(wr <= abs(residual))
                if fits.size:
                    q = fits[np.argmax(wr[fits])]
                    take[rest[q]] = (mode == 0)
                    residual -= sign*float(wr[q])
            if abs(residual) <= band:
                apply(p, i, j, a, b, take)
                ratio_sum = float(np.sum(t*invh[p]))
        calibrate(p, rng)
        ratio = float(np.mean(t*invh[p]))
        if abs(ratio-target) > tol:
            raise RuntimeError('Final ratio outside tolerance')
        if np.any(h[p] > t) or not np.array_equal(np.sort(p), np.arange(n)):
            raise RuntimeError('Pairing invariant failed')
        nonhdl = t-h[p]
        diagnostics = {
            'mean_individual_ratio': ratio,
            'mean_nonhdl_mg_dl': float(np.mean(nonhdl)),
            'fraction_nonhdl_at_least_160': float(np.mean(nonhdl >= threshold)),
            'hdl_le_tc_every_record': True,
            'hdl_index_is_permutation': True,
            'marginals_preserved': True
        }
        return p, diagnostics

    pa, da = fit(int(m['scenarios']['a']['objective_direction']))
    pb, db = fit(int(m['scenarios']['b']['objective_direction']))
    difference = db['fraction_nonhdl_at_least_160'] - da['fraction_nonhdl_at_least_160']
    chosen = pa if scenario == 'a' else pb
    out = pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'hdl_index': chosen})
    out.attrs['diagnostics'] = {
        'seed': int(seed),
        'scenario_a': da,
        'scenario_b': db,
        'b_minus_a_percentage_points': 100.0*difference,
        'absolute_difference_exceeds_4_percentage_points': bool(abs(difference) > float(m['consequential_difference_fraction'])),
        'mean_nonhdl_from_fixed_marginals_mg_dl': float(np.mean(t)-np.mean(h)),
        'interpretation': 'Heuristic assignment stress test; not clinically validated dependence or certified extrema.'
    }
    return out
