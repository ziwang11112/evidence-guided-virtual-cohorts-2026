"""Independent deterministic specification check; no sampler imports or draws."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parent
C = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcBuild01/candidates/initial')
load = lambda name: json.loads((C/name).read_text(encoding='utf-8-sig'))
spec = load('model_spec.json')['parameters']
reported = load('static_math_report.json')
ev = {item['id']: item for item in load('evidence.json')['items']}
checks = []
means = []
covariances = []
for sex in ('male', 'female'):
    model = spec['sex_models'][sex]
    age = model['age']
    a = np.asarray(age['values'], dtype=float)
    bounds = np.r_[-np.inf, age['latent_thresholds_finite'], np.inf]
    probs = np.diff(ndtr(bounds))
    np.testing.assert_allclose(probs, age['probabilities'], atol=8e-16, rtol=1e-13)
    raw = np.diff(ndtr((np.arange(34.5, 75.5)-age['untruncated_mean'])/age['untruncated_sd']))
    np.testing.assert_allclose(probs, raw/raw.sum(), atol=8e-16, rtol=1e-13)
    assert np.array_equal(a, np.arange(35,75)) and np.all(probs>0)
    r = np.asarray(model['latent_correlation'])
    np.testing.assert_allclose(r, r.T, atol=0, rtol=0)
    np.testing.assert_allclose(np.diag(r), np.ones(4), atol=0, rtol=0)
    eigen = np.linalg.eigvalsh(r)
    assert np.min(eigen)>0
    laws = [model[name] for name in ('bmi','glucose','hba1c')]
    mu = np.asarray([law['log_mu'] for law in laws])
    s = np.asarray([law['log_sd'] for law in laws])
    floor = np.asarray([law['floor'] for law in laws])
    unshifted_mean = np.exp(mu+s*s/2)
    mean = np.r_[a@probs, floor+unshifted_mean]
    cov = np.zeros((4,4))
    cov[0,0] = (a*a)@probs-mean[0]**2
    for i in range(3):
        for j in range(3):
            cov[i+1,j+1] = unshifted_mean[i]*unshifted_mean[j]*np.expm1(s[i]*s[j]*r[i+1,j+1])
        # Integrate each exact integer-age cell under the normal tilted measure.
        tilted_mass = np.diff(ndtr(bounds-r[0,i+1]*s[i]))
        cov[0,i+1] = cov[i+1,0] = unshifted_mean[i]*(a@tilted_mass-mean[0])
    np.testing.assert_allclose(mean, reported['sex_moments'][sex]['mean'], rtol=1e-13,atol=1e-12)
    np.testing.assert_allclose(cov, reported['sex_moments'][sex]['covariance'], rtol=1e-11,atol=2e-12)
    np.testing.assert_allclose(eigen, reported['sex_moments'][sex]['latent_eigenvalues'],rtol=1e-12,atol=1e-12)
    corr_bh = cov[1,3]/math.sqrt(cov[1,1]*cov[3,3])
    rank_gh = 6/math.pi*math.asin(r[2,3]/2)
    np.testing.assert_allclose(corr_bh,ev[f'JDPP_{sex}_BH_pearson']['estimate'],rtol=1e-13,atol=1e-13)
    np.testing.assert_allclose(rank_gh,ev[f'Hainan_{sex}_HG_spearman']['estimate'],rtol=1e-13,atol=1e-13)
    slope = np.linalg.solve(cov[:3,:3], cov[:3,3])
    np.testing.assert_allclose(slope[0],.010,rtol=1e-10,atol=2e-13)
    checks.append({'sex':sex, 'status':'PASS', 'minimum_latent_eigenvalue':float(eigen.min()),
        'maximum_reported_covariance_error':float(np.max(np.abs(cov-np.asarray(reported['sex_moments'][sex]['covariance'])))),
        'derived_BMI_HbA1c_Pearson':float(corr_bh), 'derived_glucose_HbA1c_Spearman':float(rank_gh),
        'within_sex_age_slope':float(slope[0])})
    means.append(mean)
    covariances.append(cov)

# Recompute pooled projections through total covariance including the female
# regressor, independently of the author's within-sex projection implementation.
p=spec['female_probability']; weights=[1-p,p]
full_mean=sum(w*np.r_[m,float(k)] for k,(w,m) in enumerate(zip(weights,means)))
full_cov=np.zeros((5,5))
for k,(w,m,cov) in enumerate(zip(weights,means,covariances)):
    conditional=np.zeros((5,5));conditional[:4,:4]=cov
    centered=np.r_[m,float(k)]-full_mean
    full_cov+=w*(conditional+np.outer(centered,centered))
results={}
for name, indices in [('primary',[1,2,0,4]),('secondary',[1,0,4])]:
    beta=np.linalg.solve(full_cov[np.ix_(indices,indices)],full_cov[indices,3])
    values=np.r_[full_mean[3]-beta@full_mean[indices],beta]
    expected=reported['pooled_projection'][name]
    np.testing.assert_allclose(values,expected,rtol=2e-11,atol=2e-12)
    results[name]={'status':'PASS','maximum_projection_error':float(np.max(np.abs(values-expected))),
                   'coefficients':values.tolist()}
report={'status':'PASS','scope':'independent_deterministic_specification_math_only',
        'generator_imported':False,'generator_executed':False,'random_draws':0,'target_read':False,
        'model_spec_sha256':hashlib.sha256((C/'model_spec.json').read_bytes()).hexdigest(),
        'reported_math_sha256':hashlib.sha256((C/'static_math_report.json').read_bytes()).hexdigest(),
        'sex_checks':checks,'total_covariance_projection_checks':results}
with (ROOT/'CANDIDATE_MATH_REVIEW.json').open('x',encoding='utf-8') as stream:
    json.dump(report,stream,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps(report,indent=2,allow_nan=False))
