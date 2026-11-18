import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    task = spec['task']
    m = spec['model']
    rng = np.random.default_rng(seed)
    n = int(task['n_rows'])
    codes = m['sex']['codes']
    s = rng.choice(len(codes), size=n, p=m['sex']['probabilities'])
    dep = m['dependence']
    order = dep['block_order']
    index = {name: j for j, name in enumerate(order)}
    R = np.eye(len(order))
    for pair, rank_r in zip(dep['pair_order'], dep['conditional_spearman_parameters']):
        i, j = index[pair[0]], index[pair[1]]
        R[i, j] = R[j, i] = 2 * np.sin(np.pi * rank_r / 6)
    z = rng.standard_normal((n, len(order))) @ np.linalg.cholesky(R).T

    def lognormal_from_moments(mean, sd, latent):
        variance_log = np.log1p((sd / mean) ** 2)
        return np.exp(np.log(mean) - variance_log / 2 + np.sqrt(variance_log) * latent)

    values = {}
    for name in order:
        margin = m['margins'][name]
        mean = np.asarray(margin['arithmetic_mean_by_sex'], dtype=float)[s]
        sd = np.asarray(margin['arithmetic_sd_by_sex'], dtype=float)[s]
        values[name] = lognormal_from_moments(mean, sd, z[:, index[name]])
    age = m['age']
    loading = dep['age_bmi_latent_correlation']
    za = loading * z[:, index['bmi']] + np.sqrt(1 - loading ** 2) * rng.standard_normal(n)
    gap_mean = np.asarray(age['gap_arithmetic_mean_by_sex'], dtype=float)[s]
    gap_sd = np.asarray(age['gap_arithmetic_sd_by_sex'], dtype=float)[s]
    values['age'] = age['lower_endpoint_year'] + lognormal_from_moments(gap_mean, gap_sd, za)
    values['sex'] = np.asarray(codes)[s]
    values[task['row_id']] = ['vc_' + str(i) for i in range(n)]
    columns = [column['name'] for column in task['columns']]
    return pd.DataFrame(values, columns=columns)
