import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    t, m = spec['task'], spec['model']
    n = int(t['n_rows'])
    rng = np.random.default_rng(seed)
    root3 = np.sqrt(3.0)
    lo, hi = m['age']['support_year']
    age = rng.uniform(lo, hi, n)
    ac = age - (lo + hi) / 2.0
    p = m['sex']['probability_F']
    female = rng.random(n) < p
    fc = female.astype(float) - p
    va = (hi - lo) ** 2 / 12.0
    vf = p * (1.0 - p)
    bm = m['bmi']
    vb = bm['marginal_sd'] ** 2
    ba, bf = bm['age_slope'], bm['F_minus_M']
    bmi_noise_sd = np.sqrt(vb - ba * ba * va - bf * bf * vf)
    bmi = bm['mean'] + ba * ac + bf * fc + bmi_noise_sd * rng.uniform(-root3, root3, n)
    l = m['lipids']
    mean = np.asarray(l['marginal_mean'], dtype=float)
    sd = np.asarray(l['marginal_sd'], dtype=float)
    b = mean * np.asarray(l['reference_log_bmi'], dtype=float)
    a = np.asarray(l['age_slope'], dtype=float)
    f = np.asarray(l['F_minus_M'], dtype=float)
    load = np.asarray(l['shared_factor_loading'], dtype=float)
    cba, cbf = ba * va, bf * vf
    mean_var = b * b * vb + a * a * va + f * f * vf + 2.0 * b * a * cba + 2.0 * b * f * cbf
    residual_sd = np.sqrt(sd * sd - mean_var)
    u = rng.uniform(-root3, root3, (n, len(mean) + 1))
    errors = (u[:, 0, None] * load + u[:, 1:] * np.sqrt(1.0 - load * load)) * residual_sd
    lipids = mean + (bmi - bm['mean'])[:, None] * b + ac[:, None] * a + fc[:, None] * f + errors
    data = {
        'id': ['v' + str(i) for i in range(n)],
        'age': age,
        'sex': np.where(female, m['sex']['codes']['F'], m['sex']['codes']['M']),
        'bmi': bmi
    }
    for j, name in enumerate(m['law']['lipid_order']):
        data[name] = lipids[:, j]
    return pd.DataFrame(data, columns=[c['name'] for c in t['columns']])
