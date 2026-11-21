import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    m = spec['model']
    scenario = spec['scenario']
    if scenario not in ('a', 'b'):
        raise ValueError('scenario must be a or b')
    t = np.array(spec['tc_mg_dl'], dtype=float, copy=True)
    h = np.array(spec['hdl_mg_dl'], dtype=float, copy=True)
    n = int(spec['task']['n_rows'])
    if t.ndim != 1 or h.ndim != 1 or len(t) != n or len(h) != n or n < 2:
        raise ValueError('incompatible array dimensions')
    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(h))):
        raise ValueError('nonfinite input')
    if np.any(t <= 0) or np.any(h <= 0) or np.any(np.diff(t) < 0) or np.any(np.diff(h) < 0):
        raise ValueError('arrays must be positive and ascending')
    if np.any(h > t):
        raise ValueError('sorted arrays do not admit HDL <= TC everywhere')
    target = float(m['ratio_target'])
    goal = n * target
    init_tol = n * float(m['initial_ratio_tolerance'])
    band = n * float(m['ratio_search_half_width'])
    threshold = float(m['threshold_mg_dl'])
    streams = np.random.SeedSequence(int(seed)).spawn(3)
    rng = np.random.default_rng(streams[0])
    base = np.arange(n, dtype=np.int64)

    # Start from a feasible assignment and randomize using feasible swaps.
    for _ in range(int(m['initial_shuffle_sweeps'])):
        z = rng.permutation(n)[:2 * (n // 2)].reshape(-1, 2)
        i, j = z[:, 0], z[:, 1]
        hi, hj = h[base[i]], h[base[j]]
        good = (hj <= t[i]) & (hi <= t[j])
        ii, jj = i[good], j[good]
        tmp = base[ii].copy()
        base[ii] = base[jj]
        base[jj] = tmp

    # Calibrate the mean of individual ratios, not the ratio of means.
    total = float(np.sum(t / h[base]))
    for _ in range(int(m['calibration_sweeps'])):
        if abs(total - goal) <= init_tol:
            break
        z = rng.permutation(n)[:2 * (n // 2)].reshape(-1, 2)
        i, j = z[:, 0], z[:, 1]
        hi, hj = h[base[i]], h[base[j]]
        dr = (t[i] - t[j]) * (1.0 / hj - 1.0 / hi)
        valid = (hj <= t[i]) & (hi <= t[j])
        for k in np.flatnonzero(valid):
            new_total = total + float(dr[k])
            if abs(new_total - goal) < abs(total - goal):
                u, v = int(i[k]), int(j[k])
                base[u], base[v] = base[v], base[u]
                total = new_total
                if abs(total - goal) <= init_tol:
                    break
        total = float(np.sum(t / h[base]))
    if abs(total - goal) > init_tol:
        raise RuntimeError('ratio calibration failed; no uncalibrated output returned')

    def search(direction, search_rng):
        p = base.copy()
        total = float(np.sum(t / h[p]))
        for _ in range(int(m['search_sweeps'])):
            z = search_rng.permutation(n)[:2 * (n // 2)].reshape(-1, 2)
            i, j = z[:, 0], z[:, 1]
            ti, tj = t[i], t[j]
            hi, hj = h[p[i]], h[p[j]]
            dr = (ti - tj) * (1.0 / hj - 1.0 / hi)
            old = (ti - hi >= threshold).astype(np.int8) + (tj - hj >= threshold).astype(np.int8)
            new = (ti - hj >= threshold).astype(np.int8) + (tj - hi >= threshold).astype(np.int8)
            improvement = direction * (new - old)
            neutral = search_rng.random(len(i)) < float(m['neutral_swap_probability'])
            valid = (hj <= ti) & (hi <= tj) & ((improvement > 0) | ((improvement == 0) & neutral))
            accepted = []
            # Candidate pairs are disjoint within a sweep, so their increments remain valid.
            for k in np.flatnonzero(valid):
                new_total = total + float(dr[k])
                if abs(new_total - goal) <= band:
                    accepted.append(k)
                    total = new_total
            if accepted:
                k = np.asarray(accepted, dtype=np.int64)
                ii, jj = i[k], j[k]
                tmp = p[ii].copy()
                p[ii] = p[jj]
                p[jj] = tmp
            total = float(np.sum(t / h[p]))
        return p

    pairings = {}
    diagnostics = {}
    for label, stream in zip(('a', 'b'), streams[1:]):
        direction = int(m['scenarios'][label]['count_direction'])
        p = search(direction, np.random.default_rng(stream))
        paired_h = h[p]
        ratio = float(np.mean(t / paired_h))
        if not np.array_equal(np.sort(p), np.arange(n)):
            raise RuntimeError('not a permutation')
        if np.any(paired_h > t):
            raise RuntimeError('HDL exceeds TC')
        if abs(ratio - target) > float(m['ratio_search_half_width']) + 1e-9:
            raise RuntimeError('ratio constraint failed')
        if not (abs(ratio - 3.66) <= 0.02 and 3.655 <= ratio < 3.665):
            raise RuntimeError('published ratio acceptance condition failed')
        pairings[label] = p
        diagnostics[label] = {
            'mean_individual_tc_hdl_ratio': ratio,
            'mean_nonhdl_mg_dl': float(np.mean(t - paired_h)),
            'fraction_nonhdl_ge_160': float(np.mean(t - paired_h >= threshold)),
            'hdl_le_tc_all': True,
            'hdl_index_is_permutation': True
        }
    difference = diagnostics['b']['fraction_nonhdl_ge_160'] - diagnostics['a']['fraction_nonhdl_ge_160']
    out = pd.DataFrame({'row_id': np.arange(n, dtype=np.int64), 'hdl_index': pairings[scenario]})
    out.attrs['diagnostics'] = diagnostics
    out.attrs['b_minus_a_percentage_points'] = 100.0 * difference
    out.attrs['exceeds_consequential_difference'] = bool(abs(difference) > float(m['consequential_difference_fraction']))
    out.attrs['seed'] = int(seed)
    return out
