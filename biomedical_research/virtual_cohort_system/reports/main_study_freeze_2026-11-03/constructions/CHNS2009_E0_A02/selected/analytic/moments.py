"""Closed-form arithmetic only: no generator import, RNG, rows or quadrature."""
import hashlib
import json
import math
from pathlib import Path

CAND = Path(__file__).resolve().parents[1]
spec_path = CAND / 'model_spec.json'
p = json.loads(spec_path.read_text(encoding='utf-8'))['parameters']
result = {'method': 'closed_form_finite_dimensional_algebra', 'generator_imported': False,
          'generator_executed': False, 'rows_created': 0, 'quadrature': False,
          'scope': 'Properties of the declared target scenario, not source replay, empirical checks or target-reference comparisons.',
          'inputs': {'model_spec.json': hashlib.sha256(spec_path.read_bytes()).hexdigest()},
          'marginal_moments': {}, 'continuous_covariances': {}, 'log_correlations': {}}
v = {}
for key, m in p['marginal_moments'].items():
    assert m['mean'] > 0 and m['individual_sd'] > 0
    v[key] = math.log1p((m['individual_sd']/m['mean'])**2)
    mu = math.log(m['mean']) - v[key]/2
    first = math.exp(mu+v[key]/2)
    second = math.exp(2*mu+2*v[key])
    result['marginal_moments'][key] = {'log_mean':mu, 'log_variance':v[key], 'mean':first, 'second_raw_moment':second, 'variance':second-first**2, 'individual_sd':math.sqrt(second-first**2)}
for i, left in enumerate(p['marginal_moments']):
    for right in list(p['marginal_moments'])[i+1:]:
        r = p['factor_loadings'][left]*p['factor_loadings'][right]
        cov = p['marginal_moments'][left]['mean']*p['marginal_moments'][right]['mean']*math.expm1(r*math.sqrt(v[left]*v[right]))
        result['log_correlations'][left+':'+right] = r
        result['continuous_covariances'][left+':'+right] = cov
for loading in p['factor_loadings'].values():
    assert abs(loading) < 1
lo, hi = p['age_support']['minimum'], p['age_support']['maximum']
count = hi-lo+1
age_mean, age_variance = (lo+hi)/2, (count**2-1)/12
result['marginal_moments']['age'] = {'mean':age_mean, 'variance':age_variance, 'second_raw_moment':age_variance+age_mean**2}
pf = p['female_probability']
assert 0 < pf < 1
result['marginal_moments']['female'] = {'mean':pf, 'variance':pf*(1-pf), 'second_raw_moment':pf}
result['population_projection_implications'] = {
    'E1_bmi': result['continuous_covariances']['bmi:hba1c']/p['marginal_moments']['bmi']['individual_sd']**2,
    'E2_glucose': result['continuous_covariances']['glucose:hba1c']/p['marginal_moments']['glucose']['individual_sd']**2,
    'E3_age': 0.0,
    'interpretation': 'Assumption-dependent algebraic implications, not measured or source-estimated target coefficients. Age/female independence leaves E1/E2 equal to the simple marginal slopes and makes E3 age zero.'
}
result['positive_definiteness'] = {'normal_residual_variances':{k:1-x*x for k,x in p['factor_loadings'].items()}, 'argument':'Log covariance is D times (ll^T+diag(1-l_i^2)) times D with positive diagonal residuals. Its density has full continuous support; nondegenerate independent age/female ensure population design covariance is positive definite.'}
(CAND/'analytic'/'moments.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
print(json.dumps({'status':'pass','rows_created':0,'output':'analytic/moments.json'}))
