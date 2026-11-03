"""Closed-form calculations only: no generator import, rows, draws or quadrature."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

C = Path(__file__).resolve().parent
B = C.parent.parent
P = json.loads((C/'model_spec.json').read_text(encoding='utf-8'))['parameters']
m,f,s = P['marginals'],P['factor'],P['source_projections']
j=P['source_contexts']['lifelines']
vb,vg=m['bmi_sd']**2,m['glucose_sd']**2
cov=f['bmi_loading']*f['glucose_loading']
sigma=np.array([[vb,cov],[cov,vg]])
beta=np.linalg.solve(sigma,np.array([s['bmi_age_sex']*vb,s['glucose_age_sex']*vg]))
vr=m['hba1c_sd']**2-s['age_full']**2*j['age_sd']**2-float(beta@sigma@beta)
assert np.linalg.eigvalsh(sigma).min()>0 and vr>0
beta_shapes={}
support={}
for var,var_total in [('bmi',vb),('glucose',vg)]:
    low,high=P['residual_support'][var]
    v=var_total-f[var+'_loading']**2
    k=-low*high/v-1
    a,b=-low*k/(high-low),high*k/(high-low)
    beta_shapes[var]={'alpha':a,'beta':b,'residual_mean':low+(high-low)*a/(a+b),'residual_variance':(high-low)**2*a*b/((a+b)**2*(a+b+1))}
    assert a>0 and b>0 and abs(beta_shapes[var]['residual_mean'])<1e-12 and abs(beta_shapes[var]['residual_variance']-v)<1e-10
    support[var]=[m[var+'_mean']-abs(f[var+'_loading'])+low,m[var+'_mean']+abs(f[var+'_loading'])+high]

def outcome_bounds(age_low,age_high):
    out=[m['hba1c_mean']-math.sqrt(3*vr),m['hba1c_mean']+math.sqrt(3*vr)]
    for coefficient,low,high,center in [(s['age_full'],age_low,age_high,j['age_mean']),(beta[0],*support['bmi'],m['bmi_mean']),(beta[1],*support['glucose'],m['glucose_mean'])]:
        vals=[coefficient*(low-center),coefficient*(high-center)]
        out[0]+=min(vals)
        out[1]+=max(vals)
    return out

support['hba1c_target_conservative']=outcome_bounds(25,79)
support['hba1c_lifelines_conservative']=outcome_bounds(j['age_mean']-math.sqrt(3)*j['age_sd'],j['age_mean']+math.sqrt(3)*j['age_sd'])
assert support['bmi'][0]>0 and support['glucose'][0]>0 and support['glucose'][1]<126
assert support['hba1c_target_conservative'][0]>0 and support['hba1c_lifelines_conservative'][0]>0

def moments(age_mean,age_var,female_probability):
    mean=[age_mean,female_probability,m['bmi_mean'],m['glucose_mean'],m['hba1c_mean']+s['age_full']*(age_mean-j['age_mean'])]
    # Independent primitives imply the entire covariance matrix, including H.
    linear=np.array([[1,0,0,0,0],[0,1,0,0,0],[0,0,1,0,0],[0,0,0,1,0],[s['age_full'],0,beta[0],beta[1],1]])
    primitive=np.zeros((5,5))
    primitive[0,0]=age_var
    primitive[1,1]=female_probability*(1-female_probability)
    primitive[2:4,2:4]=sigma
    primitive[4,4]=vr
    covariance=linear@primitive@linear.T
    return {'variables':['age','female','bmi','glucose','hba1c'],'mean':mean,'covariance':covariance.tolist()}

J=moments(j['age_mean'],j['age_sd']**2,j['female_probability'])
pani=P['source_contexts']['pani']
prob=pani['age_geometric_probability']
Pani=moments(pani['age_minimum']+(1-prob)/prob,(1-prob)/prob**2,pani['female_probability'])
ages=P['design']['age_bands']
age_means=[(lo+hi)/2 for lo,hi in ages]
age_mean=sum(age_means)/len(age_means)
age_var=sum(((hi-lo+1)**2-1)/12+(mu-age_mean)**2 for (lo,hi),mu in zip(ages,age_means))/len(ages)
T=moments(age_mean,age_var,0.5)

# Execute only the admitted analytic operator, never the generator module.
operator_path=B/'input/source_operators.py'
loader=importlib.util.spec_from_file_location('admitted_source_operators',operator_path)
module=importlib.util.module_from_spec(loader)
loader.loader.exec_module(module)
results=[]
for oid,context,mom in [('J_T2_bmi_slope_task_derived','lifelines',J),('J_T2_glucose_slope_task_derived','lifelines',J),('P_NHANES_age_slope','pani',Pani)]:
    result=module.source_projection(oid,source_context=context,**mom)
    estimate={'J_T2_bmi_slope_task_derived':s['bmi_age_sex'],'J_T2_glucose_slope_task_derived':s['glucose_age_sex'],'P_NHANES_age_slope':s['age_full']}[oid]
    result.update(reported_point=estimate,analytic_difference=result['value']-estimate)
    assert abs(result['analytic_difference'])<1e-12
    results.append(result)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

g_ast=ast.parse((C/'generator.py').read_text(encoding='utf-8'))
assert not any(isinstance(x,(ast.Import,ast.ImportFrom)) and 'generator' in ast.unparse(x) for x in ast.walk(ast.parse(Path(__file__).read_text(encoding='utf-8'))))
out={'calculation_kind':'exact_formula_evaluation_floating_point_no_sampling_no_quadrature',
     'bindings':{name:sha(C/name) for name in ['generator.py','model_spec.json','evidence.json','analytic_calculation.py']},
     'operator_sha256':sha(operator_path),'joint_slopes':{'bmi':float(beta[0]),'glucose':float(beta[1]),'age':s['age_full']},
     'bmi_glucose_covariance':cov,'bmi_glucose_correlation':cov/math.sqrt(vb*vg),
     'hba1c_residual_variance':vr,'hba1c_residual_sd':math.sqrt(vr),'beta_shapes':beta_shapes,
     'support':support,'source_context_moments':{'lifelines':J,'pani':Pani},'qualified_source_projections':results,
     'target_law_moments_not_target_reference':T,
     'scope':'Moments follow from independent primitive laws and linear maps written in mathematical_properties.md and generator.py. The source operator checks supplied moments only; independent source-law verification and biological applicability remain unassessed.'}
(C/'analytic_results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'status':'analytic_identities_pass','joint_slopes':out['joint_slopes'],'support':support,'no_rows_generated':True},indent=2))
