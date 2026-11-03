"""Closed-form source-law calculations only: no rows, RNG, quadrature or generator import."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

C = Path(__file__).resolve().parent
B = C.parents[1]
def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
spec=load(C/'model_spec.json'); p=spec['parameters']
e={x['id']:x for x in load(C/'evidence.json')['items']}
operator_path=B/'input/source_operators.py'
mod_spec=importlib.util.spec_from_file_location('approved_source_operators',operator_path)
operator=importlib.util.module_from_spec(mod_spec)
mod_spec.loader.exec_module(operator)

def beta_moments(shape):
    a,b=shape
    mu=a/(a+b)
    var=a*b/((a+b)**2*(a+b+1))
    return mu,var,[-mu/math.sqrt(var),(1-mu)/math.sqrt(var)]
def age_uniform(lo,hi):
    n=hi-lo+1
    return (lo+hi)/2,(n*n-1)/12
def mixture_moments(parts,weights):
    mean=sum(w*x[0] for w,x in zip(weights,parts))
    variance=sum(w*(x[1]+x[0]**2) for w,x in zip(weights,parts))-mean**2
    return mean,variance
muB=p['bmi_location_scale']['mean']; sB=p['bmi_location_scale']['sd']
muG=p['glucose_location_scale']['mean']; sG=p['glucose_location_scale']['sd']
rho=p['bmi_glucose_rho']; sr=math.sqrt(1-rho*rho)
ba=p['age_slope']; bf=p['female_slope']
bb=p['joint_hba1c_slopes']['bmi']; bg=p['joint_hba1c_slopes']['glucose']; se=p['hba1c_residual_sd']
vB=sB*sB;vG=sG*sG;c=rho*sB*sG
sigmaBG=np.array([[vB,c],[c,vG]])
required=np.array([p['separate_source_slopes']['bmi']*vB,p['separate_source_slopes']['glucose']*vG])
recomputed_beta=np.linalg.solve(sigmaBG,required)
recomputed_variance=p['hba1c_reference']['lifelines_sd']**2-ba*ba*p['lifelines_context']['age_sd']**2-recomputed_beta@sigmaBG@recomputed_beta
assert np.allclose(recomputed_beta,[bb,bg],atol=1e-15,rtol=0)
assert recomputed_variance>0 and abs(se*se-recomputed_variance)<1e-15

variables=['age','female','bmi','glucose','hba1c']
def law_moments(age_mean,age_var,female_probability):
    # Same structural equation as generator.py. Primitive variables are
    # (A-E[A], F-E[F], standardized U, standardized V, standardized W).
    # Independent primitive covariances are assumptions, not source estimates.
    L=np.array([[1,0,0,0,0], [0,1,0,0,0], [0,0,sB,0,0],
                [0,0,sG*rho,sG*sr,0], [ba,bf,bb*sB+bg*sG*rho,bg*sG*sr,se]],dtype=float)
    latent_variance=np.array([age_var,female_probability*(1-female_probability),1,1,1])
    covariance=(L*latent_variance)@L.T
    mean=np.array([age_mean,female_probability,muB,muG,
                   p['hba1c_reference']['mean']+ba*(age_mean-p['hba1c_reference']['age'])+bf*female_probability])
    assert np.linalg.eigvalsh(covariance).min()>0
    return {'variables':variables,'mean':mean.tolist(),'covariance':covariance.tolist(),
            'second_raw_moment':(mean**2+np.diag(covariance)).tolist(),
            'sd':np.sqrt(np.diag(covariance)).tolist(),'factor_loading_matrix':L.tolist(),
            'primitive_variances':latent_variance.tolist(),
            'derivation':'E[Z]=0; Cov(Z)=diag(Var(A),pF(1-pF),1,1,1). X=mean+LZ; Cov(X)=L diag Var(Z) L.T. These L coefficients are exactly the common generator equations.'}

jm=law_moments(p['lifelines_context']['age_mean'],p['lifelines_context']['age_sd']**2,p['lifelines_context']['female_probability'])
pc=p['pani_context']
parts=[age_uniform(*b) for b in pc['finite_age_bands']]
q=pc['geometric_probability']
parts.append((pc['open_age_lower']+(1-q)/q,(1-q)/(q*q)))
pmean,pvar=mixture_moments(parts,pc['band_probabilities'])
pm=law_moments(pmean,pvar,pc['female_probability'])
tmn,tvar=mixture_moments([age_uniform(*b) for b in p['design']['age_bands']],[1/len(p['design']['age_bands'])]*len(p['design']['age_bands']))
tm=law_moments(tmn,tvar,0.5)

results={}
for oid,context,mom in [('J_T2_bmi_slope_task_derived','lifelines',jm),('J_T2_glucose_slope_task_derived','lifelines',jm),('P_NHANES_age_slope','pani',pm)]:
    result=operator.source_projection(oid,source_context=context,variables=mom['variables'],mean=mom['mean'],covariance=mom['covariance'])
    result.update(reported=e[oid]['estimate'],difference=result['value']-e[oid]['estimate'],moment_context=context,
                  source_reconstruction=False,target_validation=False)
    assert abs(result['difference'])<1e-12
    results[oid]=result

banditems=[x for x in e.values() if x['id'].startswith('P_NHANES_hba1c_age_')]
for item,(mean_age,var_age),weight in zip(banditems,parts,pc['band_probabilities']):
    value=p['hba1c_reference']['mean']+ba*(mean_age-p['hba1c_reference']['age'])+bf*pc['female_probability']
    results[item['id']]={'operation_id':item['id'],'source_context':'pani','status':'qualified_analytic_ageband_mean',
       'band_probability_assumed':weight,'conditional_mean_age_assumed':mean_age,'conditional_variance_age_assumed':var_age,
       'numerator_E_H_times_indicator':weight*value,'denominator_probability':weight,'value':value,
       'reported':item['estimate'],'reported_estimator_uncertainty':item['uncertainty'],
       'difference':value-item['estimate'],'difference_interpretation':'Raw discrepancy, not a z-score or fit criterion; source survey distribution is not reconstructed.',
       'derivation':'Independence of centered B,G,W from age gives E[H|band]=h0+bA*(E[A|band]-a0)+bF*pF. Finite uniform sums and infinite geometric series evaluated in closed form.',
       'source_reconstruction':False,'target_validation':False}

u=beta_moments(p['factor_distributions']['bmi_beta'])[2]
v=beta_moments(p['factor_distributions']['glucose_beta'])[2]
w=[-math.sqrt(3),math.sqrt(3)]
def linear_bounds(intercept,terms):
    return [intercept+sum(min(coef*support[0],coef*support[1]) for coef,support in terms),
            intercept+sum(max(coef*support[0],coef*support[1]) for coef,support in terms)]
bs=linear_bounds(muB,[(sB,u)])
gs=linear_bounds(muG,[(sG*rho,u),(sG*sr,v)])
age_support=[min(b[0] for b in p['design']['age_bands']),max(b[1] for b in p['design']['age_bands'])]
hs=linear_bounds(p['hba1c_reference']['mean']-ba*p['hba1c_reference']['age'],
                 [(ba,age_support),(bf,[0,1]),(bb*sB+bg*sG*rho,u),(bg*sG*sr,v),(se,w)])
jas=beta_moments(p['lifelines_context']['age_beta'])[2]
jas=[p['lifelines_context']['age_mean']+p['lifelines_context']['age_sd']*x for x in jas]
jhs=linear_bounds(p['hba1c_reference']['mean']-ba*p['hba1c_reference']['age'],
                 [(ba,jas),(bf,[0,1]),(bb*sB+bg*sG*rho,u),(bg*sG*sr,v),(se,w)])
assert bs[0]>0 and gs[0]>0 and gs[1]<126 and hs[0]>0 and jhs[0]>0
assert all(math.isfinite(z) for m in (jm,pm,tm) for z in m['mean']+m['second_raw_moment'])
report={'calculation_type':'closed_form_deterministic_no_sampling_no_quadrature',
 'bindings':{'generator_sha256':sha(C/'generator.py'),'model_spec_sha256':sha(C/'model_spec.json'),'evidence_sha256':sha(C/'evidence.json'),'source_operator_sha256':sha(operator_path),'calculation_script_sha256':sha(Path(__file__))},
 'law_linkage':{'generator_function':'generate(observed,spec,seed)','generator_imported_or_executed':False,
    'bmi':'muB+sB*U','glucose':'muG+sG*(rho*U+sqrt(1-rho^2)*V)',
    'hba1c':'h0+bA*(A-a0)+bF*F+bB*(B-muB)+bG*(G-muG)+sE*W',
    'different_contexts':'Only analytic age and sex laws differ by source context; the B,G,H conditional equation and coefficients are shared.'},
 'coefficient_derivation':{'Sigma_BG':sigmaBG.tolist(),'required_Cov_BG_H':required.tolist(),'solved_joint_slopes':recomputed_beta.tolist(),'residual_variance':float(recomputed_variance)},
 'contexts':{'lifelines':jm,'pani':pm,'target_design_law_no_target_reference':tm},
 'support':{'standardized_U':u,'standardized_V':v,'standardized_W':w,'bmi':bs,'glucose':gs,'target_age':age_support,'target_hba1c':hs,'lifelines_age':jas,'lifelines_hba1c':jhs,'pani_age':{'minimum':25,'maximum':None,'tail':'70+geometric_failures(p=0.1)'},'pani_hba1c':{'minimum_bound':hs[0],'maximum':None}},
 'operations':results,
 'assertions':{'spec_derivation_matches':True,'positive_residual_variance':True,'moments_finite':True,'covariance_positive_definite':True,'target_numeric_support_valid':True,'source_projection_constraints_match':True},
 'limitations':['Hypothetical source laws do not reconstruct original samples or complex surveys.','Pani age-band mean differences are retained, not forced to agree.','Target-design moments are properties of this chosen law, never target measurements.','No scientific generator execution or Monte Carlo row creation occurred.']}
(C/'analytic_results.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'assertions':report['assertions'],'support':report['support'],'operations':{k: {'value':v['value'],'difference':v['difference']} for k,v in results.items()}},indent=2))
