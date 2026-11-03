"""Deterministic finite algebra; no generator import, RNG, rows or quadrature."""
import hashlib
import json
import math
from pathlib import Path

C = Path(__file__).resolve().parents[1]
p = json.loads((C / 'model_spec.json').read_text(encoding='utf-8'))['parameters']
k = p['common_factor']['shape']
t = p['common_factor']['scale']
ec = k * t
vc = k * t * t
report = {'scope': 'model-implied target-scenario population moments, not source replay or target validation',
          'method': 'finite closed-form Gamma mean/variance/covariance arithmetic; no sampling or numerical quadrature',
          'model_spec_sha256': hashlib.sha256((C / 'model_spec.json').read_bytes()).hexdigest(),
          'common': {'mean': ec, 'variance': vc}, 'margins': {}}
for name, q in p['margins'].items():
    variance = q['sd'] ** 2
    loading = math.sqrt(variance * q['common_variance_fraction'] / vc)
    residual_mean = q['mean'] - loading * ec
    residual_variance = variance * (1 - q['common_variance_fraction'])
    assert residual_mean > 0 and residual_variance > 0
    shape = residual_mean ** 2 / residual_variance
    scale = residual_variance / residual_mean
    mean = loading * ec + shape * scale
    var = loading ** 2 * vc + shape * scale ** 2
    report['margins'][name] = {'loading': loading, 'residual_mean': residual_mean,
        'residual_variance': residual_variance, 'residual_shape': shape,
        'residual_scale': scale, 'implied_mean': mean, 'implied_variance': var,
        'implied_second_moment': var + mean ** 2, 'mathematical_support': '(0,infinity)',
        'mean_anchor_error': mean - q['mean'], 'variance_anchor_error': var - variance}
    assert math.isclose(mean, q['mean'], rel_tol=1e-12)
    assert math.isclose(var, variance, rel_tol=1e-12)
names = list(p['margins'])
cov = {}
corr = {}
for x in names:
    cov[x] = {}
    corr[x] = {}
    for y in names:
        value = (p['margins'][x]['sd'] ** 2 if x == y else
                 report['margins'][x]['loading'] * report['margins'][y]['loading'] * vc)
        cov[x][y] = value
        corr[x][y] = value / (p['margins'][x]['sd'] * p['margins'][y]['sd'])
report['covariance'] = cov
report['correlation'] = corr
count = p['age']['maximum'] - p['age']['minimum'] + 1
age_mean = (p['age']['minimum'] + p['age']['maximum']) / 2
age_var = (count ** 2 - 1) / 12
prob = p['female']['probability']
report['demographics'] = {'age_mean': age_mean, 'age_variance': age_var,
    'age_second_moment': age_var + age_mean ** 2, 'female_mean': prob,
    'female_variance': prob * (1 - prob), 'female_second_moment': prob}
report['population_analyses'] = {
    'E1_bmi_coefficient': cov['bmi']['hba1c'] / cov['bmi']['bmi'],
    'E2_glucose_coefficient': cov['glucose']['hba1c'] / cov['glucose']['glucose'],
    'E3_age_coefficient': 0.0,
    'interpretation': 'Algebraic consequences of chosen dependence and demographic independence. They are not reported source coefficients or inferred target quantities.'}
report['positivity_and_rank'] = {'residual_variances_strictly_positive': True,
    'population_covariance_positive_definite': True,
    'reason': 'Covariance=positive diagonal residual matrix plus positive-semidefinite rank-one common-factor covariance; demographic independent variances are also positive.',
    'finite_sample_rank_guarantee': False}
dest = C / 'analytic/moments.json'
dest.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2, allow_nan=False))
