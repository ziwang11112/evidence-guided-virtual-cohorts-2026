"""Source-aggregate algebra only. No RNG, participant rows, or generator imports."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
OUT = W / 'biomedical_research/virtual_cohort_system/work/evidence_use_cross_task_2026-11-05/review'

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def inputs(author):
    bundle = W / ('evcUse' + author)
    registry = read_json(bundle / 'registry.json')
    source = {}
    bindings = []
    for entry in registry['artifacts']:
        path = bundle / entry['path']
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == entry['sha256']
        bindings.append({'source_id': entry['source_id'], 'sha256': actual, 'matches_registry': True})
        source[entry['source_id']] = read_json(path)
    agongo = {x['id']: x for x in source['agongo_2018_navrongo']['marginal_statistics']}
    greiner = {x['id']: x for x in source['greiner_2021']['reported_statistics']}
    obirikorang = {x['id']: x for x in source['obirikorang_2015_ashanti']['statistics']}
    return bundle, bindings, agongo, greiner, obirikorang

def rank_matrix(obirikorang):
    bt = obirikorang['obirikorang_rural_bmi_tc']['estimate']
    bh = obirikorang['obirikorang_rural_bmi_hdl']['estimate']
    th = obirikorang['obirikorang_rural_tc_hdl']['estimate']
    spearman = np.array([[1, bt, bh], [bt, 1, th], [bh, th, 1]])
    latent = 2*np.sin(np.pi*spearman/6)
    np.fill_diagonal(latent, 1.0)
    return spearman, latent

bundle, bindings, a, g, o = inputs('L02')
_, r = rank_matrix(o)
cv_ids = ['agongo_men_bmi_mean_sd', 'agongo_women_bmi_mean_sd',
          'agongo_pooled_total_cholesterol_mean_sd', 'agongo_pooled_hdl_cholesterol_mean_sd']
log_sd = [math.sqrt(math.log1p((a[k]['sd']/a[k]['mean'])**2)) for k in cv_ids]
claimed = [.15008518742354868, .17153121087276144, .27929359630610007, .32459284597450133]
assert np.allclose(log_sd, claimed, rtol=0, atol=2e-15)
r4 = np.eye(4)
r4[1:, 1:] = r
r4[0, 1:] = r4[1:, 0] = [.12, .25, .05]
eig4 = np.linalg.eigvalsh(r4)
assert np.all(eig4 > 0)
assert np.allclose(eig4, [.6801296892468623, .8273456761383242, 1.0880177807818767, 1.4045068538329362], rtol=0, atol=2e-14)
moment_margins = {}
for sex, label, sb in [('M','men',log_sd[0]), ('F','women',log_sd[1])]:
    result = {}
    for variable, sd in zip(['bmi','total_cholesterol','hdl_cholesterol'], [sb,log_sd[2],log_sd[3]]):
        geo = g[f'malawi_rural_{label}__{variable}__geometric_mean']['estimate']
        mean = geo*math.exp(sd*sd/2)
        result[variable] = {'geometric_mean':geo, 'log_sd':sd, 'arithmetic_mean':mean,
                            'arithmetic_sd':mean*math.sqrt(math.expm1(sd*sd))}
    moment_margins[sex] = result
l02 = {'scope':'deterministic source-aggregate algebra only; no rows, RNG, target data or generator execution',
       'source_hash_bindings':bindings, 'cv_log_sd_order':cv_ids, 'cv_log_sd':log_sd,
       'latent_correlation':r4.tolist(), 'eigenvalues':eig4.tolist(),
       'all_reported_calculations_match':True, 'positive_definite':True,
       'derived_margin_moments':moment_margins,
       'age_quantile_law':'Continuous monotone piecewise-linear inverse CDF on [18,85]; positive interval lengths and correct declared quartile locations.',
       'finite_moments':'Bounded age/sex and finite mixture of lognormal margins give every nonnegative polynomial joint moment finite.'}
(OUT/'L02_ANALYTIC_RECHECK.json').write_text(json.dumps(l02,indent=2)+'\n',encoding='utf-8')

bundle, bindings, a, g, o = inputs('L03')
spearman, r = rank_matrix(o)
variables = ['bmi', 'total_cholesterol', 'hdl_cholesterol']
m = np.array([a[f'agongo_pooled_{v}_mean_sd']['mean'] for v in variables])
t = np.array([a[f'agongo_pooled_{v}_mean_sd']['sd'] for v in variables])
ratio = np.array([g[f'malawi_rural_women__{v}__geometric_mean']['estimate'] /
                  g[f'malawi_rural_men__{v}__geometric_mean']['estimate'] for v in variables])
p = .5
A1 = 1-p+p*ratio
A2 = 1-p+p*ratio**2
v = np.log((1+t*t/(m*m))*A1*A1/A2)
sd = np.sqrt(v)
d = np.log(ratio)
intercept = np.log(m)-np.log(A1)-v/2
stratum_means = np.array([np.exp(intercept+d*f+v/2) for f in [0,1]])
stratum_covariances = np.array([np.outer(q,q)*np.expm1(r*np.outer(sd,sd)) for q in stratum_means])
within = .5*stratum_covariances.sum(axis=0)
pooled_mean = .5*stratum_means.sum(axis=0)
pooled_second = .5*sum(np.diag(c)+q*q for c,q in zip(stratum_covariances,stratum_means))
pooled_sd = np.sqrt(pooled_second-pooled_mean**2)
assert np.allclose(pooled_mean,m,rtol=0,atol=2e-14)
assert np.allclose(pooled_sd,t,rtol=0,atol=2e-13)
assert np.all(v>0) and np.all(np.linalg.eigvalsh(r)>0)
betas = within[0,1:]/within[0,0]
resid = within[1:,1:]-np.outer(within[0,1:],within[0,1:])/within[0,0]
resid_r = resid[0,1]/math.sqrt(resid[0,0]*resid[1,1])
effects = 5*38.67*betas
author_algebra = read_json(bundle/'ANALYTIC_DERIVATION.json')
assert np.allclose(effects,[author_algebra['model_implied_ols']['tc_per5_mg_dL'],author_algebra['model_implied_ols']['hdl_per5_mg_dL']],rtol=0,atol=3e-13)
assert math.isclose(resid_r,author_algebra['model_implied_ols']['residual_tc_hdl_pearson'],rel_tol=0,abs_tol=2e-14)
assert np.allclose(within,author_algebra['within_sex_covariance_averaged'],rtol=0,atol=3e-13)
assert np.all(np.linalg.eigvalsh(resid)>0)
l03 = {'scope':'deterministic source-aggregate algebra only; no rows, RNG, target data or generator execution',
       'source_hash_bindings':bindings, 'order':variables, 'log_locations':intercept.tolist(),
       'log_sex_shifts':d.tolist(), 'log_variances':v.tolist(), 'log_sd':sd.tolist(),
       'derived_pooled_arithmetic_mean':pooled_mean.tolist(), 'derived_pooled_arithmetic_sd':pooled_sd.tolist(),
       'latent_correlation':r.tolist(), 'latent_eigenvalues':np.linalg.eigvalsh(r).tolist(),
       'latent_determinant':float(np.linalg.det(r)), 'within_sex_covariance_averaged':within.tolist(),
       'residual_covariance':resid.tolist(), 'tc_per5_mg_dL':float(effects[0]), 'hdl_per5_mg_dL':float(effects[1]),
       'residual_tc_hdl_pearson':float(resid_r), 'all_reported_calculations_match':True,
       'age_quantile_law':'For upper-quartile y=(age-q75)/(90-q75), CDF=2*y-y*y and density=2*(1-y)/(90-q75); integrates to one conditionally and joins q75 continuously.',
       'ols_qualification':'Age is independent of biomarkers conditional on sex by explicit assumption. Centering within sex removes the sex intercept; age then has zero population covariance with centered biomarkers. Sex-averaged covariance projection is therefore correct.',
       'finite_moments':'Bounded age/sex and finite mixture of multivariate lognormals with finite covariance give every nonnegative polynomial joint moment finite.'}
(OUT/'L03_ANALYTIC_RECHECK.json').write_text(json.dumps(l03,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'L02':{'algebra_matches':True,'minimum_eigenvalue':float(eig4.min())},
                  'L03':{'algebra_matches':True,'tc_per5_mg_dL':float(effects[0]),
                         'hdl_per5_mg_dL':float(effects[1]),'residual_r':float(resid_r)}},indent=2))
