"""Read-only aggregate/model audit; no generator import, execution or sampling.

Integrates the published recursive HbA1c law by deterministic Gaussian quadrature.
This is a post-hoc mathematical diagnostic, not a new clinical experiment.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.special import gammaincc

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent / 'hrs_public_example_2026-11-03'
FILES = {
    'agent_spec': UNIT / 'bundle/candidates/agent/model_spec.json',
    'native_spec': UNIT / 'recovery_v1/native_candidate/model_spec.json',
    'published': UNIT / 'sources/HRS_PUBLISHED_REFERENCES.json',
    'fits': UNIT / 'summary/fixed_effects_all_seeds.csv',
}

def integrate(p, order):
    x, w = np.polynomial.legendre.leggauss(order)
    z, v = np.polynomial.hermite.hermgauss(order)
    z = z * math.sqrt(2)
    v = v / math.sqrt(math.pi)
    cells = p['demographic_model']['cells']
    count = sum(c['count'] for c in cells)
    all_moments = np.zeros(3)
    upper_moments = np.zeros(3)
    age_moments = np.zeros(2)
    for c in cells:
        lo, hi = p['age_model']['bin_bounds'][c['age_bin']]
        age = (lo + hi) / 2 + x * (hi - lo) / 2
        age60 = (age - p['age_model']['center_years']) / p['age_model']['scale_years']
        weight = c['count'] / count
        age_moments += weight * np.array([(lo+hi)/2, (lo*lo+lo*hi+hi*hi)/3])
        male, black = float(c['sex']=='male'), float(c['race']=='black')
        a = np.broadcast_to(age60[:, None], (order,order))
        cs = p['cses_model']
        cses = cs['coefficients'][0] + cs['coefficients'][1]*a + cs['coefficients'][2]*black + cs['residual_sd']*z[None,:]
        features = {'intercept':np.ones_like(a),'baseline_age60':a,'sex_male':np.full_like(a,male),'race_black':np.full_like(a,black),'cses':cses}
        edu = p['education_model']
        ex = np.stack([features[t] for t in edu['terms']], axis=-1)
        logits = ex @ np.asarray(edu['coefficients']).T
        logits -= logits.max(axis=-1, keepdims=True)
        prob = np.exp(logits); prob /= prob.sum(axis=-1,keepdims=True)
        quad_weight = weight * (w[:,None]/2) * v[None,:]
        h = p['hba1c_model']; phi = h['dispersion']; shape = 1/phi
        for k, level in enumerate(edu['levels']):
            features['educ_HS']=np.full_like(a,float(level=='HS'))
            features['educ_LessThanHS']=np.full_like(a,float(level=='LessThanHS'))
            hx=np.stack([features[t] for t in h['terms']],axis=-1)
            mu=np.exp(hx @ np.asarray(h['coefficients']))
            scale=phi*mu
            # E[H^j 1(H>=knot)|X] = scale^j Gamma(shape+j)/Gamma(shape) Q(shape+j,knot/scale).
            raw=[np.ones_like(mu),mu,mu*mu*(1+phi)]
            for j in range(3):
                wt=quad_weight*prob[:,:,k]
                all_moments[j]+=np.sum(wt*raw[j])
                upper_moments[j]+=np.sum(wt*raw[j]*gammaincc(shape+j,p['memory_model']['hba1c_knot']/scale))
    def summarize(m):
        mean=m[1]/m[0]
        return {'probability':float(m[0]),'mean':float(mean),'sd':float(np.sqrt(m[2]/m[0]-mean*mean))}
    return {'overall':summarize(all_moments),'above':summarize(upper_moments),'below':summarize(all_moments-upper_moments),'age':{'mean':float(age_moments[0]),'sd':float(np.sqrt(age_moments[1]-age_moments[0]**2))}}

def main():
    a=json.loads(FILES['agent_spec'].read_text())['parameters']
    b=json.loads(FILES['native_spec'].read_text())['parameters']
    rename={'intercept':'(Intercept)','baseline_age60':'base.age60','race_black':'raceBlack','sex_male':'sexMale','educ_HS':'educHS','educ_LessThanHS':'educLessThanHS','U65':'hba1c_U65','O65':'hba1c_O65'}
    def term(t):return ':'.join(rename.get(x,x) for x in t.split(':'))
    coefficient_checks=[]
    for group, native in [('cses_model','cses'),('hba1c_model','hba1c'),('memory_model','memory')]:
        for t,value in zip(a[group]['terms'],a[group]['coefficients']):
            nv=b[native]['coefficients'][term(t)]['estimate']
            coefficient_checks.append({'model':group,'term':term(t),'agent':value,'native':nv,'difference':value-nv})
    assert all(c['difference']==0 for c in coefficient_checks)
    assert a['hba1c_model']['dispersion']==b['hba1c']['dispersion']['value']
    for c,nc in zip(a['demographic_model']['cells'],b['demographic_cells']):
        assert c['count']==nc['count'] and c['sex']==nc['sex'] and c['race']==nc['race']
    for k,lvl in enumerate(a['education_model']['levels']):
        if lvl!='College':assert a['education_model']['coefficients'][k]==b['education']['coefficients'][lvl]
    integrations={str(n):integrate(a,n) for n in [24,40,64]}
    change=max(abs(integrations['64'][g][v]-integrations['40'][g][v]) for g in ['overall','above','below','age'] for v in integrations['64'][g])
    rows=list(csv.DictReader(FILES['fits'].open(newline='')))
    standardized=[]
    for r in rows:
        estimate,se,source=map(float,[r['estimate'],r['se'],r['exported_coefficient']])
        standardized.append({'arm':r['arm'],'seed':int(r['seed']),'term':r['term'],'estimate':estimate,'se':se,'source':source,'error_over_fitted_se':(estimate-source)/se,'interval_includes_zero':float(r['wald_lower'])<=0<=float(r['wald_upper']),'interval_includes_source':float(r['wald_lower'])<=source<=float(r['wald_upper'])})
    output={
      'kind':'post_hoc_deterministic_model_and_aggregate_audit',
      'no_generator_import_or_execution':True,'no_sampling':True,'no_individual_tables_read':True,
      'method':'Gauss-Legendre integration over uniform age; Gauss-Hermite integration over normal CSES; exact categorical summation; analytic incomplete-Gamma truncated moments. Orders 24,40,64 assess numerical integration convergence.',
      'formula':'E[H^j 1(H>=k)|X] = theta^j Gamma(alpha+j)/Gamma(alpha) Q(alpha+j,k/theta), j=0,1,2.',
      'conditional_mean_identity':'Both laws have E[mem_s|covariates,age60] equal to the same 16-term linear predictor. All subject random effects and visit residuals have zero conditional mean and are independent of the covariates. Thus their population fixed-effect targets are the identical supplied coefficients; random-effect covariance rounding cannot reverse the population upper-interaction sign.',
      'coefficient_checks':coefficient_checks,
      'quadrature_by_order':integrations,'max_absolute_change_order_40_to_64':change,
      'original_published_distributions':json.loads(FILES['published'].read_text())['table2'],
      'all_96_fitted_coefficient_standardized_deviations':standardized,
      'focal_upper': [r for r in standardized if r['term']=='age60:hba1c_O65'],
      'source_upper_estimate_over_source_se':b['memory']['coefficients']['age60:hba1c_O65']['estimate']/b['memory']['coefficients']['age60:hba1c_O65']['standard_error'],
      'provenance':[{'role':k,'path':str(v),'sha256':hashlib.sha256(v.read_bytes()).hexdigest()} for k,v in FILES.items()],
      'limitation':'The coefficient/SE summaries support a conditional sampling explanation, not proof of its exact probability; no joint sampling-distribution test or independent REML rerun is performed. Rounded paper moments are descriptive sample estimates, not exact population constraints.'
    }
    (HERE/'HRS_DETERMINISTIC_AUDIT.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'law_moments':integrations['64'],'max_change':change,'focal_upper':output['focal_upper']},indent=2))

if __name__=='__main__': main()
