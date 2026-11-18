import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    t, m = spec['task'], spec['model']
    rng = np.random.default_rng(seed)
    n = int(t['n_rows'])
    s = m['transforms']
    edges = np.asarray(m['age']['edges_years'], dtype=float)
    probabilities = np.asarray(m['age']['stratum_probabilities'], dtype=float)
    group = rng.choice(len(probabilities), size=n, p=probabilities)
    age = rng.uniform(edges[group], edges[group + 1])
    p_female = np.asarray(m['female']['probabilities_by_age_stratum'], dtype=float)
    sex_index = (rng.random(n) < p_female[group]).astype(np.int64)
    female = np.asarray(m['female']['codes'], dtype=np.int64)[sex_index]
    a = (age - s['age_center']) / s['age_divisor']
    x0 = np.column_stack((np.ones(n), a, female))
    bm = m['bmi']
    lo, hi = bm['innovation_support_kg_m2']
    shape_a, shape_b = bm['innovation_beta_shapes']
    bmi_noise = lo + (hi - lo) * rng.beta(shape_a, shape_b, size=n)
    bmi = x0 @ np.asarray(bm['mean_coefficients'], dtype=float) + bmi_noise
    b = (bmi - s['bmi_center']) / s['bmi_divisor']
    x = np.column_stack((x0, b))
    bp = m['bp']
    slopes = np.asarray(bp['source_bmi_slopes_mmHg_per_kg_m2'], dtype=float) * s['bmi_divisor']
    slopes = slopes + np.asarray(bp['transport_slope_offset_mmHg_per5'], dtype=float)
    coefficients = np.vstack((bp['intercepts_mmHg'], bp['age_coefficients_mmHg_per10y'], bp['female_coefficients_mmHg'], slopes))
    loadings = np.asarray(bp['factor_loadings_mmHg'], dtype=float)
    score_mean = x @ np.asarray(bp['omitted_score_mean_coefficients'], dtype=float)
    lo, hi = bp['factor_support']
    innovations = rng.uniform(lo, hi, size=(n, loadings.shape[1]))
    outcomes = x @ coefficients + score_mean[:, None] * loadings[:, 0] + innovations @ loadings.T
    data = {t['row_id']: np.arange(n, dtype=np.int64) + 1, 'age': age, 'female': female, 'bmi': bmi}
    for j, name in enumerate(m['outcome_order']):
        data[name] = outcomes[:, j]
    return pd.DataFrame(data).loc[:, [column['name'] for column in t['columns']]]
