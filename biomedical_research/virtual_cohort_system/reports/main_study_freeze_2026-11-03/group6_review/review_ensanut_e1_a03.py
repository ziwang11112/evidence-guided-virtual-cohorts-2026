"""Independent bounded-factor/source-law review; no candidate code execution.

Only assigned frozen bundle inputs, registered sources, profile/decision and
trusted lifecycle validation are read. No rows, RNG, quadrature or target data.
"""
import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
W=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
PROJECT=W/'biomedical_research/virtual_cohort_system'
ROOT=W/'evcMS/ENSANUT2018_E1_A03'
BUNDLE=ROOT/'bundle'; CAND=BUNDLE/'candidates/initial'
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT))
from cohort_harness import lifecycle

def read(path):return lifecycle.read_json(path)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def close(a,b):
    if isinstance(a,list):return isinstance(b,list) and len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    return math.isclose(a,b,rel_tol=1e-11,abs_tol=2e-12)
checks=[]
def check(name,condition,detail):checks.append({'id':name,'passed':bool(condition),'detail':detail})

freeze_before=sha(CAND/'freeze.json'); decision_before=sha(ROOT/'decision.json')
receipt=lifecycle.verify_candidate(BUNDLE,'candidates/initial')
check('lifecycle_verify_candidate',True,'Fresh lifecycle verification passed without importing/executing candidate code.')
task=read(BUNDLE/'task.json'); profile=read(ROOT/'profile.json'); identity=read(BUNDLE/'input/identity.json')
decision=read(ROOT/'decision.json'); spec=read(CAND/'model_spec.json'); p=spec['parameters']
evidence=read(CAND/'evidence.json'); items={x['id']:x for x in evidence['items']}
norms={x['item_id']:x for x in read(BUNDLE/'input/evidence_normalization.json')['records']}
oplist=read(BUNDLE/'input/source_operations.json')['non_marginal_operations']; ops={x['operation_id']:x for x in oplist}
uptake=read(CAND/'numerical_uptake.json')['records']; uses={x['operation_id']:x for x in uptake}
analytic=read(CAND/'analytic_results.json')
check('identity_and_decision',task['task_id']==identity['author_id']==decision['author_id']==ROOT.name and
      profile['information_condition']==identity['information_condition']=='E1' and
      decision['candidate']=='candidates/initial' and decision['action']=='initial_final',
      'Task/profile/identity and initial_final decision agree.')
check('evidence_equals_admitted_input',evidence==read(BUNDLE/'input/evidence.json'),'All 30 candidate evidence items and source metadata preserve the admitted input.')
source_items={}; source_norms={}
for entry in read(BUNDLE/'registry.json')['artifacts']:
    path=BUNDLE/entry['path']
    check('source_hash_'+entry['source_id'],sha(path)==entry['sha256'],entry['path'])
    for block in re.findall(r'```json\s*(.*?)\s*```',path.read_text(encoding='utf-8-sig'),re.S):
        obj=json.loads(block)
        source_items[obj['evidence']['id']]=obj['evidence']
        source_norms[obj['normalization']['item_id']]=obj['normalization']
check('registered_source_mapping',source_items==items and source_norms==norms,
      'All evidence and normalization records match the JSON blocks in the three registered scoped source extracts.')
check('unit_conversions',close(items['J_T2_bmi_slope_task_derived']['estimate'],items['J_T2_bmi_slope_original']['estimate']*0.09148) and
      close(items['J_T2_glucose_slope_task_derived']['estimate'],items['J_T2_glucose_slope_original']['estimate']*0.09148/18) and
      close(items['J_T1_glucose_mean_mg_dL_derived']['estimate'],items['J_T1_glucose_mean_mmol_L']['estimate']*18) and
      close(items['J_T1_glucose_sd_mg_dL_derived']['estimate'],items['J_T1_glucose_sd_mmol_L']['estimate']*18),
      'Slopes receive NGSP multiplier only; glucose predictor conversion divides slope by 18. Levels/SDs convert as declared without double-counting.')
for key,eid in [('bmi_location_scale','J_T1_bmi'),('glucose_location_scale','J_T1_glucose')]:
    suffix='_task' if key=='bmi_location_scale' else '_mg_dL_derived'
    check('anchor_'+key,p[key]['mean']==items[eid+'_mean'+suffix]['estimate'] and
          p[key]['sd']==items[eid+'_sd'+suffix]['estimate'],'Location/individual scale matches the selected admitted source representation.')
check('hba1c_reference_representation',p['hba1c_reference']['mean']==items['J_T1_hba1c_mean_pct']['estimate'] and
      p['hba1c_reference']['lifelines_sd']==items['J_T1_hba1c_sd_pct']['estimate'] and
      p['hba1c_reference']['age']==items['J_T1_age_mean_task']['estimate'],
      'Direct percent HbA1c mean/SD and Jansen age reference used once; IFCC alternatives are not added as constraints.')

d=p['design']
check('exact_demographic_quotas',d['rows_per_cell']==375 and d['female_values']==[0,1] and
      d['age_bands']==[[25,39],[40,54],[55,69],[70,79]] and
      len(d['female_values'])*len(d['age_bands'])*d['rows_per_cell']==task['n_rows']==3000,
      'The nested loops produce eight exact 375-row cells, 3000 total, 1500 per sex; integer ages use inclusive band endpoints.')
syntax=ast.parse((CAND/'generator.py').read_text(encoding='utf-8-sig'))
imports=[x.name for n in syntax.body if isinstance(n,ast.Import) for x in n.names]
calls=sorted({ast.unparse(n.func) for n in ast.walk(syntax) if isinstance(n,ast.Call)})
check('generator_static_structure',imports==['numpy','pandas'] and
      not any(isinstance(n,(ast.ImportFrom,ast.While)) for n in ast.walk(syntax)) and
      not any(x in calls for x in ['open','eval','exec','compile','__import__']),
      'Static code links standard beta moments, independent beta/uniform draws and the stated affine equations; no file IO, clipping, rejection, nonlinear exponent or retries.')

muB=p['bmi_location_scale']['mean']; sB=p['bmi_location_scale']['sd']
muG=p['glucose_location_scale']['mean']; sG=p['glucose_location_scale']['sd']
rho=p['bmi_glucose_rho']; sr=math.sqrt(1-rho*rho)
ba=p['age_slope']; bf=p['female_slope']; h0=p['hba1c_reference']['mean']; a0=p['hba1c_reference']['age']
bb=p['joint_hba1c_slopes']['bmi']; bg=p['joint_hba1c_slopes']['glucose']; se=p['hba1c_residual_sd']
VB=sB*sB; VG=sG*sG; C=rho*sB*sG; determinant=VB*VG-C*C
rhsB=p['separate_source_slopes']['bmi']*VB; rhsG=p['separate_source_slopes']['glucose']*VG
betaB=(VG*rhsB-C*rhsG)/determinant; betaG=(VB*rhsG-C*rhsB)/determinant
resvar=p['hba1c_reference']['lifelines_sd']**2-ba**2*p['lifelines_context']['age_sd']**2-(betaB*rhsB+betaG*rhsG)
check('separate_to_joint_projection',determinant>0 and close([bb,bg],[betaB,betaG]) and
      p['separate_source_slopes']['bmi']==items['J_T2_bmi_slope_task_derived']['estimate'] and
      p['separate_source_slopes']['glucose']==items['J_T2_glucose_slope_task_derived']['estimate'] and
      ba==items['P_NHANES_age_slope']['estimate'],
      'Independent 2x2 inverse derives the joint coefficients from both separate projection constraints; the original slopes are not copied as joint coefficients.')
check('residual_variance',resvar>0 and close(se*se,resvar),
      'Source HbA1c total variance minus explained age and BMI/glucose variance is positive and matches the residual SD.')

def beta_support(shape):
    aa,bb0=shape
    assert aa>0 and bb0>0
    mean=aa/(aa+bb0); var=aa*bb0/((aa+bb0)**2*(aa+bb0+1)); sd=math.sqrt(var)
    return [-mean/sd,(1-mean)/sd]
u=beta_support(p['factor_distributions']['bmi_beta']); v=beta_support(p['factor_distributions']['glucose_beta']); w=[-math.sqrt(3),math.sqrt(3)]
check('standardized_primitives',p['factor_distributions']['hba1c_residual']=='standardized_uniform' and
      p['factor_distributions']['bmi_beta']==[2.0,5.0] and p['factor_distributions']['glucose_beta']==[2.0,2.0],
      'The implemented beta standardizations have zero mean/unit variance; uniform endpoints give variance one. Shapes and supports remain assumptions.')

# Enumerate extrema of the primitive support rectangle. These are algebraic
# boundary combinations, not cohort rows or random draws.
def endpoints(age_bounds):
    bvals=[]; gvals=[]; hvals=[]
    for A,F,U,V,W0 in itertools.product(age_bounds,[0,1],u,v,w):
        B=muB+sB*U; G=muG+sG*(rho*U+sr*V)
        H=h0+ba*(A-a0)+bf*F+bb*(B-muB)+bg*(G-muG)+se*W0
        bvals.append(B); gvals.append(G); hvals.append(H)
    return {'bmi':[min(bvals),max(bvals)],'glucose':[min(gvals),max(gvals)],'hba1c':[min(hvals),max(hvals)]}
target_support=endpoints([25,79])
jc=p['lifelines_context']; jage_unit=beta_support(jc['age_beta'])
jage=[jc['age_mean']+jc['age_sd']*z for z in jage_unit]; jsupport=endpoints(jage)
check('target_support',target_support['bmi'][0]>0 and target_support['glucose'][0]>0 and
      target_support['glucose'][1]<126 and target_support['hba1c'][0]>0,
      'Independent affine corner extrema prove all task supports with wide positive margins; no clipping or draws establish these bounds.')
check('support_matches_retained',close(target_support['bmi'],analytic['support']['bmi']) and
      close(target_support['glucose'],analytic['support']['glucose']) and
      close(target_support['hba1c'],analytic['support']['target_hba1c']) and
      close(jage,analytic['support']['lifelines_age']) and close(jsupport['hba1c'],analytic['support']['lifelines_hba1c']),
      'Independent primitive-corner calculations reproduce target and selected Lifelines support bounds.')

def agepart(low,high):return ((low+high)/2,((high-low+1)**2-1)/12)
def mixture(parts,weights):
    mean=math.fsum(x[0]*q0 for x,q0 in zip(parts,weights))
    var=math.fsum((x[1]+x[0]**2)*q0 for x,q0 in zip(parts,weights))-mean**2
    return mean,var
pc=p['pani_context']; gprob=pc['geometric_probability']
parts=[agepart(*b0) for b0 in pc['finite_age_bands']]+[(pc['open_age_lower']+(1-gprob)/gprob,(1-gprob)/gprob**2)]
pmean,pvar=mixture(parts,pc['band_probabilities']); tmean,tvar=mixture([agepart(*z) for z in d['age_bands']],[.25]*4)
check('pani_open_tail',0<gprob<1 and pc['open_age_lower']==70 and len(parts)==8 and
      close(sum(pc['band_probabilities']),1) and all(x>0 for x in pc['band_probabilities']) and
      analytic['support']['pani_age']['maximum'] is None and analytic['support']['pani_hba1c']['maximum'] is None and ba>0,
      'Pani >=70 is an uncapped geometric-failures tail with finite moments, not a target-79 truncation; positive age slope preserves the finite positive HbA1c lower bound.')

def moments(age_mean,age_var,fp):
    # Direct covariance identities from the actual affine equation.
    BH=bb*VB+bg*C; GH=bb*C+bg*VG
    VH=ba*ba*age_var+bf*bf*fp*(1-fp)+bb*BH+bg*GH+se*se
    mean=[age_mean,fp,muB,muG,h0+ba*(age_mean-a0)+bf*fp]
    cov=[[age_var,0,0,0,ba*age_var],[0,fp*(1-fp),0,0,bf*fp*(1-fp)],
         [0,0,VB,C,BH],[0,0,C,VG,GH],[ba*age_var,bf*fp*(1-fp),BH,GH,VH]]
    return {'mean':mean,'covariance':cov,'second_raw_moment':[mean[i]**2+cov[i][i] for i in range(5)],
            'sd':[math.sqrt(cov[i][i]) for i in range(5)]}
contexts={'lifelines':moments(jc['age_mean'],jc['age_sd']**2,jc['female_probability']),
          'pani':moments(pmean,pvar,pc['female_probability']),
          'target_design_law_no_target_reference':moments(tmean,tvar,.5)}

def cholesky(M):
    n=len(M); L=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            x=M[i][j]-math.fsum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                if x<=0:raise ValueError('Non-positive covariance pivot')
                L[i][j]=math.sqrt(x)
            else:L[i][j]=x/L[j][j]
    return L
def solve(M,rhs):
    L=cholesky(M); n=len(rhs); z=[0.0]*n; beta=[0.0]*n
    for i in range(n):z[i]=(rhs[i]-math.fsum(L[i][j]*z[j] for j in range(i)))/L[i][i]
    for i in reversed(range(n)):beta[i]=(z[i]-math.fsum(L[j][i]*beta[j] for j in range(i+1,n)))/L[i][i]
    return beta
for name,mom in contexts.items():
    cholesky(mom['covariance'])
    check('moments_'+name,all(close(value,analytic['contexts'][name][key]) for key,value in mom.items()),
          'Direct affine covariance/mean identities reproduce the retained derived law moments; all covariance Cholesky pivots are positive.')
check('finite_source_and_target_moments',all(math.isfinite(x) for m in contexts.values() for x in m['mean']+m['second_raw_moment']),
      'Target and Lifelines are bounded; geometric Pani age has all polynomial moments and HbA1c is affine in age plus bounded variables. Required moments exist under actual laws.')

names=['age','female','bmi','glucose','hba1c']; calculated={}
for oid,ctx,predictors,term in [
    ('J_T2_bmi_slope_task_derived','lifelines',['bmi','age','female'],'bmi'),
    ('J_T2_glucose_slope_task_derived','lifelines',['glucose','age','female'],'glucose'),
    ('P_NHANES_age_slope','pani',['age','female','bmi','glucose'],'age')]:
    m=contexts[ctx]; ix=[names.index(k) for k in predictors]
    beta=solve([[m['covariance'][j][k] for k in ix] for j in ix],[m['covariance'][j][4] for j in ix])
    intercept=m['mean'][4]-math.fsum(b0*m['mean'][i] for b0,i in zip(beta,ix))
    value=beta[predictors.index(term)]; calculated[oid]={'value':value,'reported':items[oid]['estimate'],'difference':value-items[oid]['estimate']}
    old=analytic['operations'][oid]
    check('projection_'+oid,close(value,old['value']) and close(value,items[oid]['estimate']) and close(intercept,old['intercept']) and
          all(close(b0,old['coefficients'][n]) for n,b0 in zip(predictors,beta)),
          'Independent population OLS solve preserves the source-specific separate adjustment set and reproduces every retained coefficient/intercept. Agreement is imposed, not independent validation.')

bandops=[op for op in oplist if op.get('kind')=='ageband_mean']
for index,(op,part,mass) in enumerate(zip(bandops,parts,pc['band_probabilities'])):
    oid=op['operation_id']; rule=op['age_rule']; old=analytic['operations'][oid]
    low,high=(pc['finite_age_bands'][index] if index<7 else [pc['open_age_lower'],None])
    check('age_rule_'+oid,rule['minimum_inclusive']==low and rule['maximum_exclusive']==(high+1 if high is not None else None),
          'Admitted half-open age band is matched by the declared source age component; open upper boundary stays absent.')
    value=h0+ba*(part[0]-a0)+bf*pc['female_probability']; numerator=mass*value
    calculated[oid]={'value':value,'reported':items[oid]['estimate'],'difference':value-items[oid]['estimate'],
                     'numerator':numerator,'denominator':mass,'conditional_age_mean':part[0],'conditional_age_variance':part[1]}
    check('band_mean_'+oid,close(value,old['value']) and close(numerator,old['numerator_E_H_times_indicator']) and
          close(mass,old['denominator_probability']) and close(part[0],old['conditional_mean_age_assumed']) and
          close(part[1],old['conditional_variance_age_assumed']) and close(value-items[oid]['estimate'],old['difference']) and
          old['reported_estimator_uncertainty']==items[oid]['uncertainty'],
          'Independent conditional numerator/denominator and age moments reproduce the retained source mean discrepancy. Reported SE remains estimator uncertainty.')

check('uptake_inventory',len(uses)==len(uptake)==len(ops)==11 and set(uses)==set(ops)==set(calculated),
      'All 11 admitted operations have one explicit use: three model constraints and eight analytic checks.')
assumptions={x['id'] for x in spec['assumptions']}
for oid,u0 in uses.items():
    expected_use='analytic_check' if 'age_' in oid and oid.endswith('_mean') else 'model_constraint'
    check('uptake_semantics_'+oid,u0['use']==expected_use and u0['evidence_ids']==[oid] and
          u0['source_ids']==[items[oid]['source_id']] and u0['source_uncertainty']['reported']==items[oid]['uncertainty'] and
          u0['source_uncertainty']['extra_normalization']==norms[oid] and
          set(u0['source_context_assumptions'])<=assumptions and bool(u0['source_population_selection']) and
          bool(u0['measurement_assumptions']) and bool(u0['cross_source_overlap']) and bool(u0['reason']),
          'Source/evidence IDs, classified use, reported uncertainty, normalization, overlap and explicit assumptions are complete and correctly mapped.')
    for path in u0['parameter_paths']+u0['analytic_artifact_paths']:
        filename,_,pointer=path.partition('#'); fp=(CAND/filename).resolve()
        exists=fp.is_relative_to(CAND.resolve()) and fp.is_file()
        if pointer and exists:
            obj=read(fp)
            for key in pointer.lstrip('/').split('/'):obj=obj[key.replace('~1','/').replace('~0','~')]
        check('artifact_'+oid+'_'+path,exists,'Numerical use has an existing frozen artifact and resolvable JSON pointer where specified.')

hashfiles={'generator_sha256':CAND/'generator.py','model_spec_sha256':CAND/'model_spec.json',
           'evidence_sha256':CAND/'evidence.json','source_operator_sha256':BUNDLE/'input/source_operators.py',
           'calculation_script_sha256':CAND/'analytic_calculations.py'}
check('retained_calculation_hashes',all(analytic['bindings'][k]==sha(v0) for k,v0 in hashfiles.items()),
      'All retained analytic inputs and script hashes match the frozen candidate and admitted operator.')
feedback=read(CAND/'whole_cohort_feedback.json'); semantics=read(CAND/'source_semantics_v1.json')
quantitative={k for k,x in items.items() if x['kind']!='contextual'}
check('target_source_unavailable',{x['evidence_id'] for x in feedback['checks']}==quantitative and
      len(feedback['checks'])==len(quantitative)==29 and all(x['status']=='not_computable' and x['operator'] is None for x in feedback['checks']),
      'All 29 quantitative target-table source comparisons are unavailable; contextual NGSP guidance has no clinical statistic to compute.')
check('semantic_hash_binding',{x['evidence_id'] for x in semantics['bindings']}==quantitative and
      all(x['definition_status']=='unsupported' and x['source_operator'] is None for x in semantics['bindings']) and
      semantics['evidence_sha256']==sha(CAND/'evidence.json') and semantics['recipe_sha256']==sha(CAND/'whole_cohort_feedback.json'),
      'All unsupported semantic declarations bind the exact evidence and recipe bytes.')
check('frozen_bytes_unchanged',sha(CAND/'freeze.json')==freeze_before and sha(ROOT/'decision.json')==decision_before,
      'Freeze and decision hashes remained unchanged during independent review.')

result={'reviewer_id':'/root/main_review_g5','candidate':str(CAND),'candidate_freeze_sha256':freeze_before,
        'decision_sha256':decision_before,'review_script_sha256':sha(Path(__file__)),
        'checks':checks,'all_checks_passed':all(c['passed'] for c in checks),'derived_joint_slopes':[betaB,betaG],
        'derived_residual_variance':resvar,'target_support':target_support,'lifelines_support':jsupport,
        'contexts':contexts,'operations':calculated,'generator_ast_call_inventory':calls,
        'generator_imported':False,'generator_executed':False,'author_script_executed':False,
        'row_sampling_performed':False,'numerical_quadrature_performed':False,'target_results_used':False,
        'lifecycle_verified_candidate_file_count':len(receipt['candidate_files'])}
destination=OUT/'ENSANUT2018_E1_A03_calculations.json'
destination.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'all_checks_passed':result['all_checks_passed'],'check_count':len(checks),
                  'failed_checks':[x for x in checks if not x['passed']],
                  'candidate_freeze_sha256':freeze_before,'decision_sha256':decision_before,
                  'derived_joint_slopes':[betaB,betaG],'derived_residual_variance':resvar,
                  'target_support':target_support,'operations':calculated,'output':str(destination)},indent=2))
