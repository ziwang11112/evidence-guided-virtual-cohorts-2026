"""Audit only the author's predeclared deterministic sensitivity cases."""
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.special import ndtr

ROOT=Path(__file__).resolve().parent
C=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcBuild01/candidates/initial')
load=lambda name:json.loads((C/name).read_text(encoding='utf-8-sig'))
parameters=load('model_spec.json')['parameters']
declared=load('static_math_report.json')

def moments(model,changed_bg=None):
    r=np.asarray(model['latent_correlation'],dtype=float).copy()
    if changed_bg is not None:
        r[1,2]=r[2,1]=changed_bg
    eigen=np.linalg.eigvalsh(r)
    assert eigen.min()>0
    bounds=np.r_[-np.inf,model['age']['latent_thresholds_finite'],np.inf]
    ages=np.asarray(model['age']['values'],dtype=float)
    probability=np.diff(ndtr(bounds))
    laws=[model[key] for key in ('bmi','glucose','hba1c')]
    mu=np.asarray([law['log_mu'] for law in laws])
    sigma=np.asarray([law['log_sd'] for law in laws])
    unshifted=np.exp(mu+sigma*sigma/2)
    mean=np.r_[ages@probability,unshifted+np.asarray([law['floor'] for law in laws])]
    covariance=np.zeros((4,4))
    covariance[0,0]=(ages*ages)@probability-mean[0]**2
    for i in range(3):
        covariance[0,i+1]=covariance[i+1,0]=unshifted[i]*(ages@np.diff(ndtr(bounds-r[0,i+1]*sigma[i]))-mean[0])
        for j in range(3):
            covariance[i+1,j+1]=unshifted[i]*unshifted[j]*np.expm1(sigma[i]*sigma[j]*r[i+1,j+1])
    return mean,covariance,r,eigen

def pooled(group_moments):
    p=parameters['female_probability'];weights=[1-p,p]
    means=[row[0] for row in group_moments];covs=[row[1] for row in group_moments]
    overall=sum(w*np.r_[m,float(k)] for k,(w,m) in enumerate(zip(weights,means)))
    total=np.zeros((5,5))
    for k,(w,m,cov) in enumerate(zip(weights,means,covs)):
        conditional=np.zeros((5,5));conditional[:4,:4]=cov
        difference=np.r_[m,float(k)]-overall
        total+=w*(conditional+np.outer(difference,difference))
    projection={}
    for name,indices in [('primary',[1,2,0,4]),('secondary',[1,0,4])]:
        beta=np.linalg.solve(total[np.ix_(indices,indices)],total[indices,3])
        projection[name]=np.r_[overall[3]-beta@overall[indices],beta]
    return projection,total

models=[parameters['sex_models'][sex] for sex in ('male','female')]
baseline=[moments(model) for model in models]
baseline_projection,baseline_cov=pooled(baseline)
reports=[]
for case in declared['assumption_sensitivity']:
    value=case['changed_only_latent_bmi_glucose']
    altered=[moments(model,value) for model in models]
    group_checks=[]
    for sex,base,changed in zip(('male','female'),baseline,altered):
        bm,bc,br,_=base;cm,cc,cr,eigen=changed
        np.testing.assert_array_equal(cm,bm)
        keep=np.ones((4,4),dtype=bool);keep[1,2]=keep[2,1]=False
        np.testing.assert_array_equal(cr[keep],br[keep])
        np.testing.assert_array_equal(cc[keep],bc[keep])
        group_checks.append({'sex':sex,'all_marginal_moments_unchanged':True,
            'other_latent_pair_correlations_unchanged':True,'other_pair_covariances_unchanged':True,
            'minimum_latent_eigenvalue':float(eigen.min()),
            'BMI_glucose_covariance_before':float(bc[1,2]),'BMI_glucose_covariance_after':float(cc[1,2])})
    projection,total=pooled(altered)
    keep=np.ones((5,5),dtype=bool);keep[1,2]=keep[2,1]=False
    np.testing.assert_array_equal(total[keep],baseline_cov[keep])
    maximum_error=0.
    for name in ('primary','secondary'):
        np.testing.assert_allclose(projection[name],case[name],rtol=2e-11,atol=2e-12)
        maximum_error=max(maximum_error,float(np.max(np.abs(projection[name]-case[name]))))
    np.testing.assert_array_equal(projection['secondary'],baseline_projection['secondary'])
    reports.append({'declared_latent_BMI_glucose':value,'status':'PASS','group_checks':group_checks,
        'primary_order':case['primary_order'],'primary':projection['primary'].tolist(),
        'secondary_order':case['secondary_order'],'secondary':projection['secondary'].tolist(),
        'secondary_projection_unchanged':True,'maximum_declared_projection_error':maximum_error})
report={'status':'PASS','scope':'audit_of_predeclared_analytical_sensitivity_only',
    'generator_imported':False,'generator_executed':False,'random_draws':0,'target_read':False,
    'new_parameters_selected':False,
    'model_spec_sha256':hashlib.sha256((C/'model_spec.json').read_bytes()).hexdigest(),
    'static_math_report_sha256':hashlib.sha256((C/'static_math_report.json').read_bytes()).hexdigest(),
    'baseline_latent_BMI_glucose':models[0]['latent_correlation'][1][2],
    'baseline_primary':baseline_projection['primary'].tolist(),'cases':reports,
    'interpretation':'Only the BMI-glucose latent dependence changes. The sex distribution, all conditional marginal laws and every other conditional bivariate marginal law stay fixed because their Gaussian submatrices and transforms stay fixed; the pooled counterparts also stay fixed. Primary BMI changes sign across these predeclared scenarios, whereas secondary OLS excludes glucose and is identical. This demonstrates dependence on an unmeasured joint association, not calibrated uncertainty, source validation, new simulated cohorts or a basis for selecting a favorable scenario.'}
with (ROOT/'SENSITIVITY_REVIEW.json').open('x',encoding='utf-8') as stream:
    json.dump(report,stream,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps(report,indent=2,allow_nan=False))
