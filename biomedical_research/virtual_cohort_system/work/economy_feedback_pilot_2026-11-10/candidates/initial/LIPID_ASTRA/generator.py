import numpy as np
import pandas as pd
from scipy.special import ndtri


def generate(observed, spec, seed):
    task, model = spec['task'], spec['model']
    n = int(task['n_rows'])
    rng = np.random.default_rng(seed)
    copula = model['copula']
    names = copula['latent_order']
    index = {name: i for i, name in enumerate(names)}
    correlation = np.eye(len(names))
    for item in copula['latent_correlations']:
        i, j = [index[name] for name in item['pair']]
        correlation[i, j] = correlation[j, i] = item['value']
    for item in copula['rank_correlations']:
        i, j = [index[name] for name in item['pair']]
        value = 2 * np.sin(np.pi * item['spearman_rho'] / 6)
        correlation[i, j] = correlation[j, i] = value
    latent = rng.standard_normal((n, len(names))) @ np.linalg.cholesky(correlation).T
    sex = model['sex']
    threshold = ndtri(1 - sex['probability_above_threshold'])
    data = {
        task['row_id']: ['v' + str(i) for i in range(n)],
        sex['column']: np.where(latent[:, index[sex['latent']]] > threshold,
                                sex['above_threshold_code'], sex['otherwise_code'])
    }
    for margin in model['marginals']:
        mean = margin['mean_above_shift']
        variance_log = np.log1p((margin['sd_above_shift'] / mean) ** 2)
        mean_log = np.log(mean) - variance_log / 2
        data[margin['column']] = margin['shift'] + np.exp(
            mean_log + np.sqrt(variance_log) * latent[:, index[margin['latent']]])
    return pd.DataFrame(data, columns=[column['name'] for column in task['columns']])
