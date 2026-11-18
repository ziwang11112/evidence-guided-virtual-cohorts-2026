import numpy as np
import pandas as pd

def generate(observed, spec, seed):
    task = spec['task']
    m = spec['model']
    n = int(task['n_rows'])
    rng = np.random.default_rng(seed)
    lo, hi = m['covariates']['age']['support_years']
    age = rng.uniform(lo, hi, n)
    p0, p1 = m['covariates']['female']['probabilities_at_age_endpoints']
    pf = p0 + (p1 - p0) * (age - lo) / (hi - lo)
    female = (rng.random(n) < pf).astype(np.int64)
    ac, ast = m['design']['age_center_scale']
    bc, bst = m['design']['bmi_center_scale']
    a = (age - ac) / ast
    z = np.column_stack((np.ones(n), a, female))
    bm = m['covariates']['bmi']
    bl, bh = bm['support_kg_m2']
    mu = z @ np.asarray(bm['conditional_mean_coefficients'], dtype=float)
    q = (mu - bl) / (bh - bl)
    precision = bm['beta_precision']
    bmi = bl + (bh - bl) * rng.beta(q * precision, (1 - q) * precision)
    bp = m['bp']
    means = z @ np.asarray(bp['non_bmi_coefficients'], dtype=float).T
    slopes = bst * np.asarray(bp['transported_bmi_coefficients_per_kg_m2'], dtype=float)
    means = means + ((bmi - bc) / bst)[:, None] * slopes[None, :]
    ul, uh = bp['residual_latent_uniform_support']
    u = rng.uniform(ul, uh, (n, len(bp['outcome_order'])))
    u = (u - (ul + uh) / 2) / ((uh - ul) / np.sqrt(12.0))
    errors = (u @ np.asarray(bp['residual_mixing_matrix'], dtype=float).T) * np.asarray(bp['residual_sd_mmHg'], dtype=float)
    values = means + errors
    data = {'row_id': np.arange(n, dtype=np.int64), 'age': age, 'female': female, 'bmi': bmi}
    for j, name in enumerate(bp['outcome_order']):
        data[name] = values[:, j]
    return pd.DataFrame(data).loc[:, [c['name'] for c in task['columns']]]
