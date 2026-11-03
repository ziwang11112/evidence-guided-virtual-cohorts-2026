"""Closed-form analytic moments only; no sampling, generator import or tables."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import numpy as np

C = Path(__file__).resolve().parents[1]
BUNDLE = C.parents[1]

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p,x):
    p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

spec=read(C/'model_spec.json')
p=spec['parameters']
j=p['jansen_selected']
pf=j['female_probability']; vf=pf*(1-pf)
sb=math.sqrt(j['reported_bmi_sd']**2-j['bmi_age']**2*j['age_sd']**2-j['bmi_female']**2*vf)
sg=math.sqrt(j['reported_glucose_sd']**2-j['glucose_age']**2*j['age_sd']**2-j['glucose_female']**2*vf)
r=j['residual_bmi_glucose_correlation']
focal=np.array([j['separate_bmi_projection'],j['separate_glucose_projection']])
projection_map=np.array([[1,r*sg/sb],[r*sb/sg,1]])
theta=np.linalg.solve(projection_map,focal)
residual_hvar=(j['reported_hba1c_sd']**2-j['hba1c_age']**2*j['age_sd']**2-j['hba1c_female']**2*vf
               -theta[0]**2*sb**2-theta[1]**2*sg**2-2*theta[0]*theta[1]*r*sb*sg)
assert residual_hvar>0
assert np.allclose([sb,sg,*theta,math.sqrt(residual_hvar)],
    [j['bmi_residual_sd'],j['glucose_residual_sd'],j['hba1c_bmi_residual_slope'],
     j['hba1c_glucose_residual_slope'],j['hba1c_residual_sd']],rtol=1e-12,atol=1e-12)

def moments(c,context_id,assumptions):
    """The 5x6 matrix is a factor loading map, not sampled rows."""
    va=c['age_sd']**2
    pf=c['female_probability']; vf=pf*(1-pf)
    r=c['residual_bmi_glucose_correlation']; sb=c['bmi_residual_sd']; sg=c['glucose_residual_sd']
    tb=c['hba1c_bmi_residual_slope']; tg=c['hba1c_glucose_residual_slope']
    pq,mt,st,k=c['excess_probability'],c['excess_mean'],c['excess_log_sd'],c['excess_hba1c_slope']
    eq=pq*mt
    vq=pq*mt**2*math.exp(st**2)-eq**2
    L=np.array([[1,0,0,0,0,0],[0,1,0,0,0,0],
                [c['bmi_age'],c['bmi_female'],sb,0,0,0],
                [c['glucose_age'],c['glucose_female'],sg*r,sg*math.sqrt(1-r*r),0,1],
                [c['hba1c_age'],c['hba1c_female'],tb*sb+tg*sg*r,tg*sg*math.sqrt(1-r*r),c['hba1c_residual_sd'],k]])
    variances=np.array([va,vf,1,1,1,vq])
    cov=(L*variances)@L.T
    yname='HbA1c_IFCC' if c['hba1c_unit']=='mmol/mol' else 'HbA1c_percent'
    names=['age','gender_binary','BMI','FPG',yname]
    means=[c['age_mean'],pf,c['bmi_mean'],c['glucose_mean']+eq,c['hba1c_mean']+k*eq]
    assert np.linalg.eigvalsh(cov).min()>0
    return dict(role='declared_source_population_moments',source_context_id=context_id,
                selection_status='moments_after_declared_source_selection',weights='equal_assumption',
                assumption_ids=assumptions,moment_derivation='analytic/law_derivation.md; analytic/derive_moments.py exact loading map L diag(v) L^T; no simulation or quadrature',
                gender_mapping='female=1,male=0',variables=names,means=means,covariance=cov.tolist(),
                units=dict(zip(names,['year','1','kg/m^2','mmol/L',c['hba1c_unit']])),
                independent_centered_factors=['age_minus_mean','female_minus_probability','U_B','U_G','U_H','Q_minus_mean'],
                factor_loading_matrix=L.tolist(),factor_variances=variances.tolist(),
                excess_mean=eq,excess_variance=vq,
                selection_declaration='Direct law conditional on stated source eligibility. No parent law or target table is substituted.',
                positive_definite_eigenvalues=np.linalg.eigvalsh(cov).tolist())

contexts=[moments(j,'CTX_JANSEN_SELECTED',['A_FAMILY','A_J_SELECTION','A_J_COVARIATES','A_J_RESPONSE','A_QUALIFIED']),
          moments(p['bao_selected'],'CTX_BAO_ANALYZED',['A_FAMILY','A_BAO_CONTEXT','A_MEASUREMENT_TRANSPORT','A_QUALIFIED'])]
write(C/'analytic/source_moments.json',{'contexts':contexts})
operation_path=BUNDLE/'input/source_operations.py'
loader=importlib.util.spec_from_file_location('admitted_source_operations',operation_path)
module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module)
ev={x['id']:x for x in read(C/'evidence.json')['items']}
results=[]
for eid,context in [('R_JANSEN_BMI',contexts[0]),('R_JANSEN_FPG',contexts[0]),('R_BAO_PEARSON',contexts[1])]:
    result=module.evaluate(eid,context)
    result['reported_source_point']=ev[eid]['estimate']
    result['raw_difference']=result['calculated_value']-ev[eid]['estimate']
    result['interpretation']='Qualified fixed-law point comparison only; no tolerance, p-value, source reconstruction or target validation.'
    results.append(result)
write(C/'analytic/source_comparisons.json',{'method':'closed_form_analytic_no_rows_no_quadrature',
      'inputs':{'model_spec_sha256':sha(C/'model_spec.json'),'evidence_sha256':sha(C/'evidence.json'),
                'source_operations_sha256':sha(operation_path),'derivation_script_sha256':sha(Path(__file__))},
      'law_derivation':'analytic/law_derivation.md','comparisons':results,
      'unavailable':[{'evidence_id':'R_MIND_SPEARMAN','reason':'Ordinary moments do not determine ranks; no justified source imputation/tie/rank law is supplied.'}],
      'constraint_derivation':{'projection_map':projection_map.tolist(),'separate_source_slopes':focal.tolist(),
         'derived_structural_IFCC_slopes':theta.tolist(),'remaining_HbA1c_residual_variance':float(residual_hvar)}})

def support(c):
    if c['age_law']=='discrete_uniform_inclusive':
        lo,hi=c['age_min']-c['age_mean'],c['age_max']-c['age_mean']
    else:
        lo,hi=-math.sqrt(3)*c['age_sd'],math.sqrt(3)*c['age_sd']
    pf=c['female_probability']; r=c['residual_bmi_glucose_correlation']; sb=c['bmi_residual_sd'];sg=c['glucose_residual_sd']
    tb=c['hba1c_bmi_residual_slope'];tg=c['hba1c_glucose_residual_slope']
    domains=[(lo,hi),(-pf,1-pf),(-math.sqrt(3),math.sqrt(3)),(-math.sqrt(3),math.sqrt(3)),(-math.sqrt(3),math.sqrt(3))]
    values={}
    for name,m,coefs in [('BMI',c['bmi_mean'],[c['bmi_age'],c['bmi_female'],sb,0,0]),
             ('glucose',c['glucose_mean'],[c['glucose_age'],c['glucose_female'],sg*r,sg*math.sqrt(1-r*r),0]),
             ('HbA1c',c['hba1c_mean'],[c['hba1c_age'],c['hba1c_female'],tb*sb+tg*sg*r,tg*sg*math.sqrt(1-r*r),c['hba1c_residual_sd']])]:
        lower=m+sum(min(b*x,b*y) for b,(x,y) in zip(coefs,domains))
        upper=m+sum(max(b*x,b*y) for b,(x,y) in zip(coefs,domains))
        unbounded=c['excess_probability']>0 and name in ['glucose','HbA1c']
        values[name]={'lower_bound':lower,'upper_bound':None if unbounded else upper,'upper_unbounded':unbounded}
        assert lower>0
    return values

support_results={key:support(p[key]) for key in ['jansen_selected','bao_selected','target']}
assert support_results['jansen_selected']['glucose']['upper_bound']<7
write(C/'analytic/support_bounds.json',{'method':'exact_extrema_of_bounded_linear_part_plus_nonnegative_excess',
      'mathematical_probability_law_not_floating_point_overflow_guarantee':True,'bounds':support_results})
print(json.dumps({'rows_produced':0,'generator_imported':False,'analytical_source_comparisons':results,
                  'target_support_bounds':support_results['target']},indent=2))
