import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    scenario = spec['scenario']
    if scenario not in ('a', 'b'):
        raise ValueError('scenario must be a or b')
    tc = np.asarray(spec['tc_mg_dl'], dtype=float)
    hd = np.asarray(spec['hdl_mg_dl'], dtype=float)
    n = int(spec['task']['n_rows'])
    if tc.shape != (n,) or hd.shape != (n,) or n < 2:
        raise ValueError('Incorrect marginal dimensions')
    if not (np.all(np.isfinite(tc)) and np.all(np.isfinite(hd))):
        raise ValueError('Nonfinite marginal value')
    if np.any(tc <= 0) or np.any(hd <= 0):
        raise ValueError('Marginals must be positive')
    if np.any(np.diff(tc) < 0) or np.any(np.diff(hd) < 0):
        raise ValueError('Marginals must be ascending')
    if np.any(hd > tc):
        raise ValueError('No ordered feasible starting assignment')
    target = float(m['ratio_target'])
    tol = float(m['ratio_calibration_tolerance']) * n
    band = float(m['optimization_ratio_half_band']) * n
    cutoff = float(m['threshold_mg_dl'])
    target_sum = target * n
    root = np.random.default_rng(seed)
    child_seeds = root.integers(0, 2**63 - 1, size=3, dtype=np.int64)

    def proposals(p, rng):
        order = rng.permutation(n)
        x = order[:2 * (n // 2):2]
        y = order[1:2 * (n // 2):2]
        hx, hy = hd[p[x]], hd[p[y]]
        feasible = (hy <= tc[x]) & (hx <= tc[y])
        dr = (tc[x] - tc[y]) * (1.0 / hy - 1.0 / hx)
        old = (tc[x] - hx >= cutoff).astype(np.int8) + (tc[y] - hy >= cutoff).astype(np.int8)
        new = (tc[x] - hy >= cutoff).astype(np.int8) + (tc[y] - hx >= cutoff).astype(np.int8)
        return x, y, feasible, dr, new - old

    def calibrate(p, rng, sweeps, neutral_only):
        total = float(np.sum(tc / hd[p]))
        for _ in range(int(sweeps)):
            if abs(total - target_sum) <= tol:
                break
            x, y, feasible, dr, dc = proposals(p, rng)
            if neutral_only:
                feasible &= dc == 0
            for k in np.flatnonzero(feasible):
                change = float(dr[k])
                if abs(total + change - target_sum) < abs(total - target_sum):
                    i, j = x[k], y[k]
                    p[i], p[j] = p[j], p[i]
                    total += change
                    if abs(total - target_sum) <= tol:
                        break
            total = float(np.sum(tc / hd[p]))
        return abs(total - target_sum) <= tol

    base = np.arange(n, dtype=np.int64)
    init_rng = np.random.default_rng(int(child_seeds[0]))
    if not calibrate(base, init_rng, m['initial_calibration_sweeps'], False):
        raise RuntimeError('Initial ratio calibration failed; no invalid output returned')

    def construct(direction, child_seed):
        rng = np.random.default_rng(int(child_seed))
        p = base.copy()
        total = float(np.sum(tc / hd[p]))
        neutral_probability = float(m['neutral_swap_probability'])
        for _ in range(int(m['optimization_sweeps'])):
            x, y, feasible, dr, dc = proposals(p, rng)
            gain = direction * dc
            eligible = feasible & ((gain > 0) | ((gain == 0) & (rng.random(len(x)) < neutral_probability)))
            for k in np.flatnonzero(eligible):
                candidate = total + float(dr[k])
                if abs(candidate - target_sum) <= band:
                    i, j = x[k], y[k]
                    p[i], p[j] = p[j], p[i]
                    total = candidate
            total = float(np.sum(tc / hd[p]))
        ok = calibrate(p, rng, m['final_neutral_calibration_sweeps'], True)
        if not ok:
            ok = calibrate(p, rng, m['final_unrestricted_calibration_sweeps'], False)
        if not ok:
            raise RuntimeError('Final ratio calibration failed; no invalid output returned')
        if not np.array_equal(np.sort(p), np.arange(n)):
            raise RuntimeError('Assignment is not a permutation')
        if np.any(hd[p] > tc):
            raise RuntimeError('HDL exceeds TC')
        ratio = float(np.mean(tc / hd[p]))
        if abs(ratio - target) > float(m['ratio_calibration_tolerance']) * 1.01:
            raise RuntimeError('Ratio tolerance not met')
        nonhdl = tc - hd[p]
        diagnostics = {
            'mean_individual_ratio': ratio,
            'mean_nonhdl_mg_dl': float(np.mean(nonhdl)),
            'fraction_nonhdl_at_least_160': float(np.mean(nonhdl >= cutoff)),
            'permutation_valid': True,
            'hdl_le_tc_everywhere': True
        }
        return p, diagnostics

    pa, da = construct(-1, child_seeds[1])
    pb, db = construct(1, child_seeds[2])
    gap = abs(db['fraction_nonhdl_at_least_160'] - da['fraction_nonhdl_at_least_160'])
    selected = pa if scenario == 'a' else pb
    result = pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'hdl_index': selected})
    result.attrs['diagnostics'] = {
        'a': da,
        'b': db,
        'absolute_fraction_difference': float(gap),
        'absolute_percentage_point_difference': float(100.0 * gap),
        'exceeds_four_percentage_points': bool(gap > float(m['consequential_difference'])),
        'note': 'Local stress scenarios, not certified extrema or population estimates.'
    }
    return result
