"""Independent deterministic L01 parameter algebra. No rows or RNG."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT.parents[3] / 'evcUseL01'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=1e-11, atol=1e-12)


def main():
    a = read(BUNDLE / 'ANALYTIC_PROPOSAL_CHECK.json')
    registry = read(BUNDLE / 'registry.json')['artifacts']
    sources = {}
    for item in registry:
        path = BUNDLE / item['path']
        assert sha(path) == item['sha256']
        sources[item['source_id']] = read(path)
    ag = {x['id']: x for x in sources['agongo_2018_navrongo']['marginal_statistics']}
    ob = {x['id']: x for x in sources['obirikorang_2015_ashanti']['statistics']}
    gr = {x['id']: x for x in sources['greiner_2021']['reported_statistics']}
    R = np.asarray(a['latent_correlation_matrix'], dtype=float)
    for label, i, j in [('bmi_tc', 1, 2), ('bmi_hdl', 1, 3), ('tc_hdl', 2, 3)]:
        rho = ob['obirikorang_rural_' + label]['estimate']
        check(a['source_spearman'][label], rho)
        check(R[i, j], 2 * math.sin(math.pi * rho / 6))
        check(6 / math.pi * math.asin(R[i, j] / 2), rho)
    check(R, R.T)
    check(np.diag(R), np.ones(4))
    eig = np.linalg.eigvalsh(R)
    assert eig.min() > 0
    chol = np.linalg.cholesky(R)
    check(chol, a['cholesky'])
    check(chol @ chol.T, R)

    p = a['female_probability']
    check(p, .5)
    moments = {}
    for sex, source_label in [('M', 'men'), ('F', 'women')]:
        item = ag['agongo_' + source_label + '_bmi_mean_sd']
        mu, sigma = a['bmi'][sex]['log_mu'], a['bmi'][sex]['log_sigma']
        mean = math.exp(mu + sigma * sigma / 2)
        sd = mean * math.sqrt(math.expm1(sigma * sigma))
        check([mean, sd], [item['mean'], item['sd']])
    for label, col in [('tc', 'total_cholesterol'), ('hdl', 'hdl_cholesterol')]:
        item = ag['agongo_pooled_' + col + '_mean_sd']
        model = a[label]
        ratio = (gr['malawi_rural_women__' + col + '__geometric_mean']['estimate'] /
                 gr['malawi_rural_men__' + col + '__geometric_mean']['estimate'])
        check(model['ratio'], ratio)
        means, variances, geometric = [], [], []
        for sex in ('M', 'F'):
            mu, sigma = model[sex]['log_mu'], model[sex]['log_sigma']
            means.append(math.exp(mu + sigma * sigma / 2))
            variances.append(math.expm1(sigma * sigma) * means[-1]**2)
            geometric.append(math.exp(mu))
            check([means[-1], math.sqrt(variances[-1])], [model[sex]['mean'], model[sex]['sd']])
        pooled_mean = (1-p)*means[0] + p*means[1]
        between = p*(1-p)*(means[1]-means[0])**2
        pooled_var = (1-p)*variances[0] + p*variances[1] + between
        check([pooled_mean, math.sqrt(pooled_var)], [item['mean'], item['sd']])
        check([geometric[1]/geometric[0], means[1]/means[0]], [ratio, ratio])
        assert item['sd']**2 - between > 0
        moments[label] = {'pooled_mean': pooled_mean, 'pooled_sd': math.sqrt(pooled_var),
                          'between_sex_variance': between,
                          'remaining_within_sex_variance': item['sd']**2 - between,
                          'arithmetic_and_geometric_sex_ratio': ratio}

    knots = np.asarray(a['age']['quantile_knots'])
    widths = np.diff(a['age']['cdf_knots'])
    left, right = knots[:-1], knots[1:]
    age_mean = np.dot(widths, (left+right)/2)
    age_second = np.dot(widths, (left*left+left*right+right*right)/3)
    age_sd = math.sqrt(age_second-age_mean**2)
    check([age_mean, age_sd], [a['age']['mean'], a['age']['sd']])
    covariance_eigenvalues, crossing_probabilities = {}, {}
    for sex in ('M', 'F'):
        means = np.asarray([a[x][sex]['mean'] for x in ('bmi', 'tc', 'hdl')])
        sigma = np.asarray([a[x][sex]['log_sigma'] for x in ('bmi', 'tc', 'hdl')])
        cov = np.outer(means, means) * np.expm1(np.outer(sigma, sigma) * R[1:, 1:])
        values = np.linalg.eigvalsh(cov)
        assert values.min() > 0
        covariance_eigenvalues[sex] = values.tolist()
        log_mean = a['tc'][sex]['log_mu'] - a['hdl'][sex]['log_mu']
        log_sd = math.sqrt(sigma[1]**2 + sigma[2]**2 - 2*sigma[1]*sigma[2]*R[2, 3])
        crossing_probabilities[sex] = .5 * math.erfc(log_mean / (log_sd * math.sqrt(2)))
    out = {'scope': 'deterministic proposed-law algebra; no rows, RNG, fitting, generators or reference reads',
           'status': 'passed', 'latent_correlation_eigenvalues': eig.tolist(),
           'raw_bmi_tc_hdl_covariance_eigenvalues': covariance_eigenvalues,
           'age_mean': float(age_mean), 'age_sd': age_sd, 'lipid_mixture_moments': moments,
           'model_probability_tc_less_than_hdl_by_sex': crossing_probabilities,
           'interpretation': 'Mathematical and source-number consistency only; no population validity claim',
           'bindings': {name: sha(BUNDLE / name) for name in
                        ['SOURCE_REVIEW_REQUEST.md', 'PROPOSED_CONSTRUCTION.md', 'ANALYTIC_PROPOSAL_CHECK.json',
                         'SEARCH_LEDGER.json', 'registry.json', 'task.json', 'request.json']}}
    destination = ROOT / 'review/L01_ANALYTIC_RECHECK.json'
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(out, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(out, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
