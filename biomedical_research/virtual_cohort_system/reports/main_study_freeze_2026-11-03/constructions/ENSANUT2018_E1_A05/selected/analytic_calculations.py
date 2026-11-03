"""Deterministic closed-form moments only; no generator import, sampling or quadrature."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import numpy as np

C = Path(__file__).resolve().parent
B = C.parent.parent
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
spec = read(C/'model_spec.json')
p = spec['parameters']
ev = {x['id']:x for x in read(C/'evidence.json')['items']}
ops = read(B/'input/source_operations.json')['non_marginal_operations']
loader = importlib.util.spec_from_file_location('admitted_source_operators',B/'input/source_operators.py')
module = importlib.util.module_from_spec(loader)
loader.loader.exec_module(module)
c,v,s,h = p['centers'],p['covariate_effects'],p['residual_scales'],p['response']
rho = v['residual_correlation']
root = math.sqrt(1-rho*rho)
ka = h['age']+h['bmi']*v['bmi_age']+h['glucose']*v['glucose_age']
kf = h['female']+h['bmi']*v['bmi_female']+h['glucose']*v['glucose_female']
L = np.array([
 [1,0,0,0,0],
 [0,1,0,0,0],
 [v['bmi_age'],v['bmi_female'],s['bmi'],0,0],
 [v['glucose_age'],v['glucose_female'],s['glucose']*rho,s['glucose']*root,0],
 [ka,kf,h['bmi']*s['bmi']+h['glucose']*s['glucose']*rho,h['glucose']*s['glucose']*root,s['hba1c']],
],dtype=float)
variables=['age','female','bmi','glucose','hba1c']

def law_moments(ma,va,pf):
    mb=c['bmi']+v['bmi_age']*(ma-c['age'])+v['bmi_female']*(pf-c['female'])
    mg=c['glucose']+v['glucose_age']*(ma-c['age'])+v['glucose_female']*(pf-c['female'])
    mh=c['hba1c']+h['age']*(ma-c['age'])+h['female']*(pf-c['female'])+h['bmi']*(mb-c['bmi'])+h['glucose']*(mg-c['glucose'])
    variances=[va,pf*(1-pf),1,1,1]
    covariance=L@np.diag(variances)@L.T
    return {'variables':variables,'mean':[ma,pf,mb,mg,mh],'covariance':covariance.tolist(),'loading_matrix':L.tolist(),'independent_component_variances':variances,'covariance_minimum_eigenvalue':float(np.linalg.eigvalsh(covariance).min())}

def discrete_uniform_moments(low,high):
    return (low+high)/2,((high-low+1)**2-1)/12

j=p['source_contexts']['lifelines']
q=p['source_contexts']['pani']
moments={'lifelines':law_moments(j['age_mean'],j['age_sd']**2,j['female_probability'])}
pa,pv=discrete_uniform_moments(q['age_minimum'],q['age_maximum'])
moments['pani']=law_moments(pa,pv,q['female_probability'])
bands=p['design']['age_bands']
within=[discrete_uniform_moments(a,b) for a,b in bands]
tma=sum(a for a,b in within)/len(within)
tva=sum(b+a*a for a,b in within)/len(within)-tma*tma
moments['task_design']=law_moments(tma,tva,0.5)

projections={}
agebands={}
for op in ops:
    oid=op['operation_id']
    if oid in module.OPERATIONS:
        mm=moments[op['source_context']]
        result=module.source_projection(oid,source_context=op['source_context'],variables=variables,mean=mm['mean'],covariance=mm['covariance'])
        result.update(reported_value=ev[oid]['estimate'],raw_difference=result['value']-ev[oid]['estimate'],law_link='Loading matrix L is the affine expansion of generator.py formulas using model_spec parameters; source-specific age/sex moments replace only the demographic distribution.')
        projections[oid]=result
    else:
        rule=op['age_rule']
        low=max(q['age_minimum'],rule['minimum_inclusive'])
        high=min(q['age_maximum'],q['age_maximum'] if rule['maximum_exclusive'] is None else rule['maximum_exclusive']-1)
        ma,va=discrete_uniform_moments(low,high)
        value=law_moments(ma,va,q['female_probability'])['mean'][-1]
        probability=(high-low+1)/(q['age_maximum']-q['age_minimum']+1)
        agebands[oid]={'status':'qualified_analytic_source_law_check','assumed_age_support':[low,high],'source_age_rule':rule,'conditional_age_mean':ma,'band_probability':probability,'hba1c_indicator_expectation':probability*value,'value':value,'reported_value':ev[oid]['estimate'],'raw_difference':value-ev[oid]['estimate'],'source_estimate_uncertainty':ev[oid]['uncertainty'],'calculation':'E[H I_band]/Pr(band), from affine conditional law and discrete-uniform mean; finite arithmetic formula, not numerical quadrature.','support_warning':'Source support25-84 is assumed; >=70 is approximated by70-84, not by the task upper age79.'}

# Exact support extrema of an affine image of a rectangular support occur at vertices.
# Enumerating2^5=32 vertices per context is deterministic algebra, not cohort rows.
latent_bound=math.sqrt(2*p['latent']['shape']+1)
supports={}
age_supports={'lifelines':[j['age_mean']-math.sqrt(3)*j['age_sd'],j['age_mean']+math.sqrt(3)*j['age_sd']], 'pani':[q['age_minimum'],q['age_maximum']], 'task_design':[min(a for a,b in bands),max(b for a,b in bands)]}
for name,(alo,ahi) in age_supports.items():
    extrema=[[],[],[]]
    for a,f,z1,z2,z3 in itertools.product([alo,ahi],[0,1],[-latent_bound,latent_bound],[-latent_bound,latent_bound],[-latent_bound,latent_bound]):
        # Expanded affine equation, no call to submitted generator.
        centered=np.array([a-c['age'],f-c['female'],z1,z2,z3])
        vals=np.array([c['bmi'],c['glucose'],c['hba1c']])+L[2:]@centered
        for i,value in enumerate(vals):
            extrema[i].append(float(value))
    limits={var:[min(vals),max(vals)] for var,vals in zip(variables[2:],extrema)}
    assert limits['bmi'][0]>0 and limits['hba1c'][0]>0
    assert limits['glucose'][0]>0 and limits['glucose'][1]<126
    supports[name]={'age':[alo,ahi],'female':[0,1],**limits,'positive_outputs_and_glucose_below126':True,'vertex_count':32}

targets=p['source_projection_constraints']
recomputed_b=(targets['bmi_age_female']-rho*s['glucose']/s['bmi']*targets['glucose_age_female'])/(1-rho*rho)
recomputed_g=(targets['glucose_age_female']-rho*s['bmi']/s['glucose']*targets['bmi_age_female'])/(1-rho*rho)
assert abs(recomputed_b-h['bmi'])<1e-14
assert abs(recomputed_g-h['glucose'])<1e-14
assert abs(projections['J_T2_bmi_slope_task_derived']['raw_difference'])<1e-12
assert abs(projections['J_T2_glucose_slope_task_derived']['raw_difference'])<1e-12
assert abs(projections['P_NHANES_age_slope']['raw_difference'])<1e-12
for i,var in enumerate(variables):
    if var in p['source_marginal_sds']:
        assert abs(moments['lifelines']['covariance'][i][i]-p['source_marginal_sds'][var]**2)<1e-10
assert all(x['covariance_minimum_eigenvalue']>0 for x in moments.values())

generator_ast=ast.parse((C/'generator.py').read_text(encoding='utf-8'))
functions=[n for n in generator_ast.body if isinstance(n,ast.FunctionDef) and n.name=='generate']
assert len(functions)==1 and len(functions[0].args.args)==3
results={
 'method':'Closed-form affine moment propagation L diag(VarA,VarF,1,1,1) L^T; exact finite age-band expectations;32 support vertices/context. No generator import/execution, random draw, Monte Carlo, numerical quadrature or target statistic.',
 'bindings':{f:sha(C/f) for f in ['generator.py','model_spec.json','evidence.json','analytic_calculations.py']},
 'admitted_operator_sha256':sha(B/'input/source_operators.py'),
 'latent_properties':{'family':'symmetric_beta','alpha':p['latent']['shape'],'mean':0,'variance':1,'support':[-latent_bound,latent_bound],'formula':'For U~Beta(a,a): E(U)=1/2,Var(U)=1/[4(2a+1)]; Z=(2U-1)sqrt(2a+1).'},
 'moment_derivation':{'independent_components':['age-Eage','female-Efemale','Z1','Z2','Z3'],'loading_matrix':L.tolist(),'source_moments':moments},
 'source_projections':projections,'pani_ageband_means':agebands,
 'variance_budget':{'bmi_residual_variance':s['bmi']**2,'glucose_residual_variance':s['glucose']**2,'hba1c_residual_variance':s['hba1c']**2,'hba1c_source_explained_variance':p['source_marginal_sds']['hba1c']**2-s['hba1c']**2,'positive_remainders':True},
 'support':supports,
 'source_moment_checks':'Lifelines chosen marginal means/SD and all three separate source projection constraints hold within1e-10 arithmetic tolerance, conditional on explicit completion assumptions. Pani band discrepancies intentionally retained.',
 'execution_status':'Generator never imported or executed by this script.'
}
(C/'analytic_results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'response':h,'support':supports,'pani_raw_differences':{k:x['raw_difference'] for k,x in agebands.items()},'source_slopes':{k:x['value'] for k,x in projections.items()}},indent=2))
