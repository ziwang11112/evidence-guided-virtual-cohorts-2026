import numpy as np
import pandas as pd
from scipy.special import ndtri


def generate(observed, spec, seed):
    task, model = spec['task'], spec['model']
    rng = np.random.default_rng(seed)
    n = int(task['n_rows'])
    latent = model['latent']
    order = latent['order']
    index = {name: j for j, name in enumerate(order)}
    correlation = np.eye(len(order))
    for a, b, value in latent['pearson_pairs']:
        i, j = index[a], index[b]
        correlation[i, j] = correlation[j, i] = value
    for a, b, value in latent['spearman_pairs']:
        i, j = index[a], index[b]
        correlation[i, j] = correlation[j, i] = 2 * np.sin(np.pi * value / 6)
    z = rng.standard_normal((n, len(order))) @ np.linalg.cholesky(correlation).T
    data = {task['row_id']: ['v' + str(i) for i in range(n)]}
    for name, marginal in model['marginals'].items():
        mean = marginal['positive_mean']
        variance_log = np.log1p((marginal['positive_sd'] / mean) ** 2)
        data[name] = marginal['offset'] + np.exp(
            np.log(mean) - variance_log / 2 + np.sqrt(variance_log) * z[:, index[name]]
        )
    sex = model['sex']
    threshold = ndtri(1 - sex['upper_probability'])
    data['sex'] = np.where(z[:, index['sex']] > threshold, sex['upper_code'], sex['lower_code'])
    return pd.DataFrame(data, columns=[column['name'] for column in task['columns']])
