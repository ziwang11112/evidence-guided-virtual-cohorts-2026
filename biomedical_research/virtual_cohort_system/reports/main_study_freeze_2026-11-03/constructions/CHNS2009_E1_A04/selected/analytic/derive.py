"""Deterministic population algebra only. No generator import, sampling, quadrature or rows."""
import sys
sys.dont_write_bytecode = True
import json, math, hashlib, importlib.util
from pathlib import Path
import numpy as np

C=Path(__file__).resolve().parents[1]
B=C.parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
p=json.loads((C/'model_spec.json').read_text())['parameters']
q=p['source_projection_constraints']; st=p['structure']; scale=p['unit_mapping']['ngsp_multiplier']
rho=st['bmi_glucose_rho']; root=math.sqrt(1-rho*rho)
cov=rho*q['reference_bmi_sd']*q['reference_glucose_sd']
kb=cov/q['reference_bmi_sd']**2;kg=cov/q['reference_glucose_sd']**2
bb=(scale*q['bmi_ifcc']-kb*scale*q['fpg_ifcc'])/(1-kb*kg)
bg=scale*q['fpg_ifcc']-kg*bb
a=st['age_hba1c_coefficient'];s=st['female_hba1c_coefficient'];half=st['uniform_half_width']
def derive(c):
    amin,amax=c['age_low'],c['age_high'];am=(amin+amax)/2
    av=(((amax-amin+1)**2-1)/12 if c['age_kind']=='integer_uniform' else (amax-amin)**2/12)
    pf,pc=c['female_probability'],c['class_probability'];vd=pc*(1-pc)
    gv=c['glucose_sd']**2-(c['glucose_class_shift']**2*vd if c['glucose_sd_mode']=='total' else 0)
    assert gv>0
    sg=math.sqrt(gv)
    lu=bb*c['bmi_sd']+bg*sg*rho;lv=bg*sg*root
    explained=lu*lu+lv*lv+a*a*av+s*s*pf*(1-pf)+c['hba1c_class_total_shift']**2*vd
    hv=c['hba1c_sd']**2-(explained if c['hba1c_sd_mode']=='total' else 0)
    assert hv>0
    sh=math.sqrt(hv)
    # Independent centered factors: age, female, U, V, D, E.
    factor_variance=np.array([av,pf*(1-pf),1,1,vd,1])
    L=np.array([[1,0,0,0,0,0],[0,1,0,0,0,0],
       [0,0,c['bmi_sd'],0,0,0],
       [0,0,sg*rho,sg*root,c['glucose_class_shift'],0],
       [a,s,lu,lv,c['hba1c_class_total_shift'],sh]])
    sigma=(L*factor_variance)@L.T
    means=np.array([am,pf,c['bmi_mean'],c['glucose_mean'],c['hba1c_mean']])
    dlo,dhi=(-pc,1-pc) if 0<pc<1 else (0,0)
    ranges=[(amin-am,amax-am),(-pf,1-pf),(-half,half),(-half,half),(dlo,dhi),(-half,half)]
    bounds=[]
    for mean,loading in zip(means,L):
        low=mean+sum(min(x*lo,x*hi) for x,(lo,hi) in zip(loading,ranges))
        high=mean+sum(max(x*lo,x*hi) for x,(lo,hi) in zip(loading,ranges))
        bounds.append([float(low),float(high)])
    for i in [2,3,4]: assert bounds[i][0]>0
    assert np.linalg.eigvalsh(sigma).min()>0
    names=['age','gender_binary','BMI','FPG','HbA1c_percent']
    source_context={
      'role':'declared_source_population_moments','source_context_id':c['context_id'],
      'assumption_ids':['A_LAW','A_J_PROJECTION', 'A_J_SOURCE' if c['context_id']=='CTX_JANSEN_SELECTED' else 'A_BAO'],
      'moment_derivation':'analytic/derive.py: Sigma=L diag(Var age, Var female, 1,1,p_D(1-p_D),1) L^T; exact independent bounded-factor law identical to generator formula. See mathematical_properties.md.',
      'selection_status':'moments_after_declared_source_selection','weights':'equal_assumption',
      'variables':names,'means':means.tolist(),'covariance':sigma.tolist(),
      'units':{'age':'year','gender_binary':'1','BMI':'kg/m^2','FPG':'mmol/L','HbA1c_percent':'%'},
      'gender_mapping':'female=1,male=0'
    }
    info={'context_parameters':c,'within_class_glucose_variance':gv,'residual_hba1c_variance':hv,'hba1c_explained_variance':explained,
      'factor_order':['age_centered','female_centered','U','V','D_centered','E'],'factor_variance':factor_variance.tolist(),'loadings':L.tolist(),
      'means':dict(zip(names,means.tolist())),'sd':dict(zip(names,np.sqrt(np.diag(sigma)).tolist())),
      'support_bounds':dict(zip(names,bounds)),'covariance_min_eigenvalue':float(np.linalg.eigvalsh(sigma).min()),'moments':source_context}
    # Algebraic target consequences: not fitted to or compared with target evidence.
    if c['context_id']=='TARGET_SCENARIO':
        projections={}
        for key,ix,term in [('E1',[0,1,2],2),('E2',[0,1,3],3),('E3',[1,2,3,0],0)]:
            beta=np.linalg.solve(sigma[np.ix_(ix,ix)],sigma[ix,4])
            projections[key]=float(beta[ix.index(term)])
        info['assumption_dependent_target_projection_implications']=projections
        # Do not misclassify the target covariance as a source scenario.
        info['moments']['role']='model_implied_target_moments_not_source'
        info['moments']['assumption_ids']=['A_LAW','A_TRANSPORT','A_CLASS','A_SCOPE']
        info['moments']['selection_status']='target_scenario_only'
        info['moments']['variables']=['age','female','bmi','glucose','hba1c']
        info['moments']['units']={'age':'year','female':'1','bmi':'kg/m^2','glucose':'mmol/L','hba1c':'%'}
        info['moments'].pop('gender_mapping')
        renaming=dict(zip(names,info['moments']['variables']))
        for key in ['means','sd','support_bounds']:
            info[key]={renaming[k]:v for k,v in info[key].items()}
    return info

source_module=B/'input/source_operations.py'
loader=importlib.util.spec_from_file_location('admitted_source_operations',source_module)
ops=importlib.util.module_from_spec(loader);loader.loader.exec_module(ops)
contexts={key:derive(c) for key,c in p['source_contexts'].items()}
target=derive(p['target_context'])
assert contexts['CTX_JANSEN_SELECTED']['support_bounds']['FPG'][1]<7
evidence={x['id']:x for x in json.loads((C/'evidence.json').read_text())['items']}
comparisons=[]
for eid,cid in [('R_JANSEN_BMI','CTX_JANSEN_SELECTED'),('R_JANSEN_FPG','CTX_JANSEN_SELECTED'),('R_BAO_PEARSON','CTX_BAO_ANALYZED')]:
    result=ops.evaluate(eid,contexts[cid]['moments'])
    result['reported_source_point']=evidence[eid]['estimate']
    result['raw_calculated_minus_reported']=result['calculated_value']-result['reported_source_point']
    result['interpretation']='Algebraically constrained source projection, not independent validation' if eid.startswith('R_JANSEN') else 'Prespecified source scenario discrepancy; not a fitting objective'
    comparisons.append(result)
result={'method':'Exact finite-factor population algebra and linear-system solve; no random draws, generated rows, numerical quadrature, target records, source replay or generator import.',
  'bindings':{'model_spec_sha256':sha(C/'model_spec.json'),'generator_text_sha256':sha(C/'generator.py'),'derivation_script_sha256':sha(Path(__file__)),'admitted_operations_sha256':sha(source_module)},
  'derived_joint_coefficients_percent':{'bmi':bb,'glucose':bg,'age_assumed':a,'female_assumed':s},
  'source_contexts':contexts,'source_comparisons':comparisons,
  'unavailable':[{'evidence_id':'R_MIND_SPEARMAN','reason':'No selected MIND rank/imputation law supplied; ordinary moments do not identify Spearman. No statistic substitution.'}],
  'target_scenario_algebra':target,
  'checks':{'positive_residual_variances':True,'positive_measurement_support':True,'source_jansen_fpg_below_7':True,'positive_definite_covariances':True,'source_rows_generated':0,'target_rows_generated':0}}
(C/'analytic/results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'derived_coefficients':result['derived_joint_coefficients_percent'],'source_comparisons':comparisons,'target_support':target['support_bounds'],'checks':result['checks']},indent=2))
