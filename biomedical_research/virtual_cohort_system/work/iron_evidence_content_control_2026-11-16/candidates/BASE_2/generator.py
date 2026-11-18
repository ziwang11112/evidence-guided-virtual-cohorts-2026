import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This whole-cohort generator requires observed=None.')
    n = int(spec['task']['n_rows'])
    if n < 0:
        raise ValueError('n_rows must be nonnegative.')
    m = spec['model']
    rho = float(m['within_component_hb_log_ferritin_rho'])
    p = float(m['ferritin_elevating_state_probability'])
    hs = float(m['hb_scale_g_dl'])
    fs = float(m['log_ferritin_sd'])
    fm = float(m['baseline_ferritin_median_ug_l'])
    mult = float(m['state_ferritin_multiplier'])
    lo = float(m['hb_lower_g_dl'])
    hi = float(m['hb_upper_g_dl'])
    if not (-1.0 < rho < 1.0 and 0.0 <= p <= 1.0):
        raise ValueError('Invalid correlation or component probability.')
    if not (hs > 0.0 and fs > 0.0 and fm > 0.0 and mult > 0.0 and 0.0 <= lo < hi):
        raise ValueError('Invalid scales, multipliers, or Hb bounds.')

    rng = np.random.default_rng(seed)
    state = (rng.random(n) < p).astype(np.int8)
    hb = np.empty(n, dtype=float)
    ferritin = np.empty(n, dtype=float)
    pending = np.arange(n, dtype=np.int64)
    independent_scale = np.sqrt(1.0 - rho * rho)
    log_fm = np.log(fm)
    log_mult = np.log(mult)

    # Rejection is individual-level conditioning within a fixed component.
    # It does not select cohort summaries or force realized moments.
    while pending.size:
        z = rng.standard_normal(pending.size)
        e = rng.standard_normal(pending.size)
        s = state[pending]
        candidate_hb = (float(m['hb_location_g_dl'])
                        + hs * (rho * z + independent_scale * e)
                        + float(m['state_hb_shift_g_dl']) * s)
        keep = (candidate_hb >= lo) & (candidate_hb <= hi)
        accepted = pending[keep]
        hb[accepted] = candidate_hb[keep]
        ferritin[accepted] = np.exp(log_fm + fs * z[keep] + log_mult * s[keep])
        pending = pending[~keep]

    return pd.DataFrame({
        'row_id': np.arange(1, n + 1, dtype=np.int64),
        'hb_g_dl': hb,
        'ferritin_ug_l': ferritin
    }, columns=['row_id', 'hb_g_dl', 'ferritin_ug_l'])
