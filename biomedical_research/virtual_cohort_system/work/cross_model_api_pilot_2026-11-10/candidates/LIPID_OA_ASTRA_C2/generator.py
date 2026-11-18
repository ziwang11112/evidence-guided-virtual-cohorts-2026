import numpy as np
import pandas as pd


def generate(observed, spec, seed):
    if observed is not None:
        raise ValueError('This construction requires observed=None.')
    task, m = spec['task'], spec['model']
    n = int(task['n_rows'])
    rng = np.random.default_rng(seed)
    p = m['sex']['female_probability']
    female = rng.random(n) < p
    sex = np.where(female, m['sex']['female_code'], m['sex']['male_code'])
    order = m['dependence']['latent_order']
    corr = np.eye(len(order))
    age_index = order.index('age')
    other = [i for i in range(len(order)) if i != age_index]
    corr[age_index, other] = m['dependence']['age_latent_correlations_with_remaining']
    corr[other, age_index] = m['dependence']['age_latent_correlations_with_remaining']
    template = m['dependence']['within_sex_rank_template']
    for pair, rank_corr in zip(template['pairs'], template['spearman']):
        i, j = [order.index(name) for name in pair]
        corr[i, j] = corr[j, i] = 2 * np.sin(np.pi * rank_corr / 6)
    z = rng.standard_normal((n, len(order))) @ np.linalg.cholesky(corr).T

    def by_sex(values):
        return np.where(female, values[m['sex']['female_code']], values[m['sex']['male_code']])

    def lognormal_draw(mean, sd, latent):
        variance = np.log1p((sd / mean) ** 2)
        return np.exp(np.log(mean) - variance / 2 + np.sqrt(variance) * latent)

    age = m['age']['lower_bound'] + lognormal_draw(
        by_sex(m['age']['excess_mean_by_sex']),
        by_sex(m['age']['excess_sd_by_sex']), z[:, age_index])
    bmi = lognormal_draw(
        by_sex(m['bmi']['arithmetic_mean_by_sex']),
        by_sex(m['bmi']['arithmetic_sd_by_sex']), z[:, order.index('bmi')])
    lm = m['lipids']
    means = np.asarray(lm['pooled_arithmetic_mean'], dtype=float)
    sds = np.asarray(lm['pooled_arithmetic_sd'], dtype=float)
    ratios = np.asarray(lm['female_to_male_arithmetic_mean_ratio'], dtype=float)
    denominator = (1 - p) + p * ratios
    mean_square = means ** 2 * ((1 - p) + p * ratios ** 2) / denominator ** 2
    log_variance = np.log((means ** 2 + sds ** 2) / mean_square)
    conditional_means = means * np.where(female[:, None], ratios, 1) / denominator
    lipid_indices = [order.index(name) for name in lm['order']]
    lipids = np.exp(np.log(conditional_means) - log_variance / 2 + z[:, lipid_indices] * np.sqrt(log_variance))
    data = {
        task['row_id']: ['virtual_' + str(i) for i in range(n)],
        'age': age,
        'sex': sex,
        'bmi': bmi
    }
    for j, name in enumerate(lm['order']):
        data[name] = lipids[:, j]
    return pd.DataFrame(data, columns=[column['name'] for column in task['columns']])
