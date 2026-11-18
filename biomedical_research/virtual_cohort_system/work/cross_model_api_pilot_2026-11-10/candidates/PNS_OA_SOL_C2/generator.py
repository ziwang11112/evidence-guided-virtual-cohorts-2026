import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    t = spec['task']
    m = spec['model']
    n = int(t['n_rows'])
    rng = np.random.default_rng(seed)
    d = m['design']

    a = m['age']
    alo, ahi = a['bounds']
    age = alo + (ahi - alo) * rng.beta(*a['beta_shape'], size=n)
    age_x = (age - d['age_center']) / d['age_scale']

    f = m['female']
    p = f['reference_probability'] + f['probability_shift_per_age_decade'] * age_x
    female = rng.binomial(1, p, size=n)

    b = m['bmi']
    blo, bhi = b['bounds']
    bmi_mean = (b['reference_conditional_mean']
                + b['mean_shift_per_age_decade'] * age_x
                + b['mean_shift_female'] * female)
    q = (bmi_mean - blo) / (bhi - blo)
    k = b['beta_concentration']
    bmi = blo + (bhi - blo) * rng.beta(k * q, k * (1 - q), size=n)
    bmi_x = (bmi - d['bmi_center']) / d['bmi_scale']

    bp = m['bp']
    outcomes = bp['outcome_order']
    mean = (np.asarray(bp['reference_conditional_mean'])[None, :]
            + age_x[:, None] * np.asarray(bp['mean_shift_per_age_decade'])[None, :]
            + female[:, None] * np.asarray(bp['mean_shift_female'])[None, :]
            + bmi_x[:, None] * d['bmi_scale'] * np.asarray(bp['bmi_slope_per_kg_m2'])[None, :])
    e = m['innovations']
    lo, hi = e['bounds']
    z = rng.uniform(lo, hi, size=(n, 1 + len(outcomes)))
    z = (z - (lo + hi) / 2) / np.sqrt(e['base_variance'])
    values = (mean
              + z[:, :1] * np.asarray(bp['shared_innovation_loadings'])[None, :]
              + z[:, 1:] * np.asarray(bp['specific_innovation_loadings'])[None, :])

    data = {'row_id': np.arange(n, dtype=np.int64) + 1,
            'age': age, 'female': female, 'bmi': bmi}
    for j, name in enumerate(outcomes):
        data[name] = values[:, j]
    columns = [c['name'] for c in t['columns']]
    return pd.DataFrame(data).loc[:, columns]
