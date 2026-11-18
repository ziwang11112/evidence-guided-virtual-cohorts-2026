import numpy as np
import pandas as pd
from scipy.special import ndtr, log_ndtr


def generate(observed, spec, seed):
    task, m = spec['task'], spec['model']
    rng = np.random.default_rng(seed)
    n = task['n_rows']
    codes = m['sex']['codes']
    sex = np.where(rng.random(n) < m['sex']['p_F'], codes[1], codes[0])
    dep = m['dependence']
    names = dep['variable_order']
    r = np.eye(len(names))
    ranks = np.asarray(dep['bmi_tc_hdl_spearman'], dtype=float)
    r[1:, 1:] = 2 * np.sin(np.pi * ranks / 6)
    r[0, 1:] = dep['age_latent_correlations']
    r[1:, 0] = dep['age_latent_correlations']
    np.fill_diagonal(r, 1)
    z = rng.standard_normal((n, len(names))) @ np.linalg.cholesky(r).T
    data = {name: np.empty(n) for name in names}
    probabilities = np.asarray(m['age']['cdf_knots'], dtype=float)
    for code in codes:
        rows = sex == code
        za = z[rows, 0]
        u = ndtr(za)
        knots = np.asarray(m['age']['quantiles_years'][code], dtype=float)
        age = np.interp(u, probabilities, knots)
        upper = u > probabilities[-1]
        scale = m['age']['tail_scale_years'][code]
        age[upper] = knots[-1] - scale * (log_ndtr(-za[upper]) - np.log1p(-probabilities[-1]))
        data['age'][rows] = age
        for j, name in enumerate(names[1:], 1):
            gm = m['marginals']['geometric_mean_by_sex'][name][code]
            refs = m['marginals']['shape_reference_arithmetic_mean_sd'][name]
            ref_mean, ref_sd = refs[code] if code in refs else refs['pooled']
            log_sd = np.sqrt(np.log1p((ref_sd / ref_mean) ** 2))
            data[name][rows] = gm * np.exp(log_sd * z[rows, j])
    data[task['row_id']] = ['virtual_' + str(i) for i in range(n)]
    data['sex'] = sex
    return pd.DataFrame(data, columns=[column['name'] for column in task['columns']])
