"""Exact deterministic moment/finite-sum calculations; never imports generator.

No draws, quadrature, Monte Carlo or individual input. Re-run from any directory.
"""
from pathlib import Path
import ast, hashlib, importlib.util, json, math, sys
import numpy as np
sys.dont_write_bytecode = True

C = Path(__file__).resolve().parents[1]
B = C.parents[1]
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
spec = read(C/'model_spec.json')
p=spec['parameters']; a=p['anchors']; f=p['factor_law']; b=p['conditional_coefficients']
evidence={x['id']:x for x in read(C/'evidence.json')['items']}
operation_input=read(B/'input/source_operations.json')['non_marginal_operations']
module_spec=importlib.util.spec_from_file_location('admitted_source_operators',B/'input/source_operators.py')
operators=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(operators)
# Purely static parse, deliberately no generator import or function evaluation.
tree=ast.parse((C/'generator.py').read_text(encoding='utf-8'))
generate_nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='generate']
assert len(generate_nodes)==1 and [x.arg for x in generate_nodes[0].args.args]==['observed','spec','seed']

rho=f['bmi_glucose_correlation']; sb=a['bmi_sd']; sg=a['glucose_sd']
j=p['source_projection_constraints']; residual=p['hba1c_residual_sd']
expected_b=(j['jansen_bmi']-rho*sg/sb*j['jansen_glucose'])/(1-rho*rho)
expected_g=(j['jansen_glucose']-rho*sb/sg*j['jansen_bmi'])/(1-rho*rho)
assert math.isclose(b['bmi'],expected_b,abs_tol=1e-15)
assert math.isclose(b['glucose'],expected_g,abs_tol=1e-15)
assert b['age']==j['pani_age'] and b['female']==0
signal=b['bmi']**2*sb**2+b['glucose']**2*sg**2+2*b['bmi']*b['glucose']*rho*sb*sg
expected_rvar=a['lifelines_hba1c_sd']**2-b['age']**2*p['source_contexts']['lifelines']['age_sd']**2-signal
assert expected_rvar>0 and math.isclose(residual**2,expected_rvar,abs_tol=1e-15)
variables=['age','female','bmi','glucose','hba1c']
contexts={}
for name,ctx in p['source_contexts'].items():
    if name=='lifelines':
        ma,va=ctx['age_mean'],ctx['age_sd']**2
    else:
        ma=ctx['age_minimum']+ctx['gamma_shape']*ctx['gamma_scale']
        va=ctx['gamma_shape']*ctx['gamma_scale']**2
    pf=ctx['female_probability']
    mean=[ma,pf,a['bmi_mean'],a['glucose_mean'],a['hba1c_mean_at_reference']+b['age']*(ma-a['age_reference'])]
    cov=np.zeros((5,5))
    cov[0,0]=va;cov[1,1]=pf*(1-pf);cov[2,2]=sb**2;cov[3,3]=sg**2
    cov[2,3]=cov[3,2]=rho*sb*sg
    beta=np.array([b['age'],b['female'],b['bmi'],b['glucose']])
    cov[:4,4]=cov[:4,:4]@beta
    cov[4,:4]=cov[:4,4]
    cov[4,4]=float(beta@cov[:4,:4]@beta+residual**2)
    assert np.linalg.eigvalsh(cov).min()>0
    contexts[name]={'variables':variables,'mean':mean,'covariance':cov.tolist(),
      'minimum_covariance_eigenvalue':float(np.linalg.eigvalsh(cov).min()),
      'provenance':'Derived from independent factors and the affine assignments in mathematical_properties.md, matching generator.py; source age/sex laws replace target quota design only.'}
projections=[]
for operation in operation_input:
    oid=operation['operation_id']
    if oid not in operators.OPERATIONS:
        continue
    ctx=contexts[operation['source_context']]
    result=operators.source_projection(oid,source_context=operation['source_context'],variables=variables,mean=ctx['mean'],covariance=ctx['covariance'])
    result['reported_value']=evidence[oid]['estimate']
    result['difference']=result['value']-result['reported_value']
    assert abs(result['difference'])<1e-12
    projections.append(result)

def gamma_survival(integer_shape,t):
    if t is None:
        return 0.0
    if t<=0:
        return 1.0
    # Exact closed form for positive integer gamma shape; no numerical integration.
    return math.exp(-t)*sum(t**j/math.factorial(j) for j in range(integer_shape))

pani=p['source_contexts']['pani']; k=pani['gamma_shape']; theta=pani['gamma_scale']; amin=pani['age_minimum']
assert type(k) is int and k>0
agebands=[]
for operation in operation_input:
    if operation.get('kind')!='ageband_mean':
        continue
    oid=operation['operation_id']; rule=operation['age_rule']
    low=(rule['minimum_inclusive']-amin)/theta
    high=None if rule['maximum_exclusive'] is None else (rule['maximum_exclusive']-amin)/theta
    probability=gamma_survival(k,low)-gamma_survival(k,high)
    numerator=amin*probability+theta*k*(gamma_survival(k+1,low)-gamma_survival(k+1,high))
    mean_age=numerator/probability
    mean_h=a['hba1c_mean_at_reference']+b['age']*(mean_age-a['age_reference'])
    reported=evidence[oid]
    agebands.append({'operation_id':oid,'status':'qualified_analytic_conditional_mean','age_rule':rule,'probability':probability,'age_first_moment_over_event':numerator,'conditional_age_mean':mean_age,'value':mean_h,'reported_value':reported['estimate'],'reported_se':reported['uncertainty']['value'],'difference':mean_h-reported['estimate'],'interpretation':'Unstandardized compatibility discrepancy under assumed Pani population law; not survey replay, target feedback or residual dispersion.'})
assert math.isclose(sum(x['probability'] for x in agebands),1,abs_tol=1e-14)
halfwidth=math.sqrt(2*f['beta_alpha']+1)
b_bound=halfwidth*sb;g_bound=halfwidth*sg*(abs(rho)+math.sqrt(1-rho*rho))
h_factor_bound=halfwidth*(abs(b['bmi']*sb+b['glucose']*sg*rho)+abs(b['glucose']*sg*math.sqrt(1-rho*rho))+residual)
target_age_min=min(lo for lo,hi in p['design']['age_bands']);target_age_max=max(hi for lo,hi in p['design']['age_bands'])
target_h_bounds=[a['hba1c_mean_at_reference']+b['age']*(target_age_min-a['age_reference'])-h_factor_bound,a['hba1c_mean_at_reference']+b['age']*(target_age_max-a['age_reference'])+h_factor_bound]
bmi_bounds=[a['bmi_mean']-b_bound,a['bmi_mean']+b_bound]
glucose_bounds=[a['glucose_mean']-g_bound,a['glucose_mean']+g_bound]
assert bmi_bounds[0]>0 and glucose_bounds[0]>0 and glucose_bounds[1]<126 and target_h_bounds[0]>0
design=p['design']; assert len(design['female_values'])*len(design['age_bands'])*design['rows_per_cell']==3000
assert design['female_values']==[0,1] and design['age_bands']==[[25,39],[40,54],[55,69],[70,79]] and design['rows_per_cell']==375
out={'scope':'deterministic source-law algebra and static design checks; no generator execution',
 'inputs':{'model_spec_sha256':digest(C/'model_spec.json'),'generator_sha256':digest(C/'generator.py'),'evidence_sha256':digest(C/'evidence.json'),'source_operations_sha256':digest(B/'input/source_operations.json'),'source_operator_sha256':digest(B/'input/source_operators.py'),'analytic_script_sha256':digest(Path(__file__))},
 'derived_coefficients':{'bmi':expected_b,'glucose':expected_g,'age':b['age'],'female':b['female']},'joint_bmi_glucose_signal_variance':signal,'hba1c_residual_variance':expected_rvar,
 'source_context_moments':contexts,'source_projection_checks':projections,'pani_ageband_checks':agebands,
 'support_and_design':{'standardized_beta_halfwidth':halfwidth,'bmi_closed_bounds':bmi_bounds,'glucose_closed_bounds':glucose_bounds,'target_hba1c_closed_bounds':target_h_bounds,'pani_age_upper_support':'unbounded','source_beta_age_closed_bounds':[55.5-9.9*halfwidth,55.5+9.9*halfwidth],'source_pani_hba1c_lower_bound':a['hba1c_mean_at_reference']+b['age']*(amin-a['age_reference'])-h_factor_bound,'target_rows':3000,'rows_per_cell':375,'no_clipping_or_rejection':True},
 'not_established':['source-law authenticity','survey replay','target-population calibration','individual reconstruction','generator runtime success','source estimate or transport uncertainty coverage']}
(C/'analytic/results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'algebra':'pass','projection_checks':len(projections),'ageband_checks':len(agebands),'residual_variance':expected_rvar,'bounds':out['support_and_design']},indent=2))
