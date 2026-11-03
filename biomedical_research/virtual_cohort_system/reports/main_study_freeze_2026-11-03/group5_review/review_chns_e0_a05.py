"""Independent exact finite-mixture arithmetic; never import candidate code.

Enumeration here covers the entire 40-year by 2-sex demographic state space,
not simulated participants, quadrature nodes or empirical target records.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode=True
W=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
PROJECT=W/'biomedical_research/virtual_cohort_system'
ROOT=W/'evcMS/CHNS2009_E0_A05'
BUNDLE=ROOT/'bundle'
CAND=BUNDLE/'candidates/initial'
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT))
from cohort_harness import lifecycle

def read(path):return lifecycle.read_json(path)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def close(a,b):
    if isinstance(a,list):return isinstance(b,list) and len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    return math.isclose(a,b,rel_tol=2e-9,abs_tol=3e-11)
checks=[]
def check(name,condition,detail):checks.append({'id':name,'passed':bool(condition),'detail':detail})

freeze_before=sha(CAND/'freeze.json'); decision_before=sha(ROOT/'decision.json')
receipt=lifecycle.verify_candidate(BUNDLE,'candidates/initial')
check('lifecycle_verify_candidate',True,'Fresh lifecycle verification passed without importing or executing the generator.')
task=read(BUNDLE/'task.json'); profile=read(ROOT/'profile.json'); identity=read(BUNDLE/'input/identity.json')
decision=read(ROOT/'decision.json'); spec=read(CAND/'model_spec.json'); p=spec['parameters']
evidence=read(CAND/'evidence.json'); items={x['id']:x for x in evidence['items']}
packet=read(BUNDLE/'sources/evidence_packet.json'); authored=read(CAND/'analytic_properties.json')
analyses=read(BUNDLE/'input/analysis_definitions.json')['uses']
check('identity_and_decision',task['task_id']==identity['author_id']==decision['author_id']==ROOT.name and
      profile['information_condition']==identity['information_condition']=='E0' and
      decision['candidate']=='candidates/initial' and decision['action']=='initial_final',
      'Task, profile and initial_final decision agree on CHNS2009 E0 A05.')
check('input_evidence_preserved',evidence==read(BUNDLE/'input/evidence.json'),'All 32 retained evidence items and source metadata equal the admitted input.')
check('input_packet_preserved',packet==read(BUNDLE/'input/reported_packet.json'),'Registered evidence packet equals the provided reported packet.')
for entry in read(BUNDLE/'registry.json')['artifacts']:
    check('source_hash_'+entry['source_id'],sha(BUNDLE/entry['path'])==entry['sha256'],entry['path'])

expected=set()
for m in packet['shared_base']['grouped_marginal_records']:
    if m['kind']=='reported_mean_and_individual_sd':
        pairs=[('_MEAN',m['mean'],'mean'),('_SD',m['individual_sd'],'sd')]
    elif m['kind']=='reported_median_and_quartile_endpoints':
        pairs=[('_MEDIAN',m['median'],'median'),('_Q1',m['q1'],'quantile'),('_Q3',m['q3'],'quantile')]
    else:
        pairs=[('_FRACTION',m['derived_fraction'],'proportion')]
        check('count_fraction_'+m['id'],close(m['derived_fraction'],m['numerator']/m['denominator']),
              'Named source sex category and unweighted count-derived fraction preserved.')
    for suffix,value,kind in pairs:
        eid=m['id']+suffix; expected.add(eid); e=items[eid]
        check('source_mapping_'+eid,e['estimate']==value and e['kind']==kind and e['source_id']==m['source_id'] and
              e['locator']==m['locator'],'Admitted marginal value, type, source and locator preserved.')
check('evidence_inventory',set(items)==expected|{'U_NGSP_SCALE'},'31 quantitative marginal items and contextual NGSP scale item; no additional relationship evidence.')
check('e0_empty_uptake',packet['arm']=='E0' and packet['relationship_records']==[] and
      read(CAND/'numerical_uptake.json')['records']==[],
      'No admitted non-marginal operation; empty uptake is explicitly valid for this E0 task.')
for j,eid in enumerate(['M_M_BMI','M_M_FSG','M_M_HBA1C_PERCENT']):
    check('selected_scale_'+eid,p['biomarker_means'][j]==items[eid+'_MEAN']['estimate'] and
          p['biomarker_sds'][j]==items[eid+'_SD']['estimate'],
          'Selected working unconditional mean/individual SD maps to the MIND source item in its native unit.')
check('female_probability',p['female_probability']==items['M_M_FEMALE_FRACTION']['estimate'] and
      close(p['female_probability'],2049/3547),'The source female count fraction is an explicitly assumed target-composition transfer.')
check('joint_terms_assumed',all(spec['parameter_provenance'][k]['evidence_ids']==[] for k in
      ['log_age_effects','log_female_effects','residual_factor_loadings']),
      'Age/sex effects and residual factor strengths are assumption-indexed, not attributed to E0 quantitative relationships.')
check('demographic_contract',p['n_rows']==task['n_rows']==3000 and p['age_min']==35 and p['age_max']==74 and
      0<p['female_probability']<1 and 'composition is not supplied' in task['population'],
      'Task fixes 3000 rows and age bounds; no exact demographic quota is supplied. The law uses uniform integer age and Bernoulli sex.')
check('output_columns',p['output_columns']==[x['name'] for x in task['columns']] and
      p['biomarker_order']==['bmi','glucose','hba1c'],'Generator returns exactly the six task columns in order.')

syntax=ast.parse((CAND/'generator.py').read_text(encoding='utf-8-sig'))
imports=[a.name for n in syntax.body if isinstance(n,ast.Import) for a in n.names]
calls=sorted({ast.unparse(n.func) for n in ast.walk(syntax) if isinstance(n,ast.Call)})
check('generator_static_structure',imports==['numpy','pandas'] and
      not any(isinstance(n,(ast.ImportFrom,ast.While)) for n in ast.walk(syntax)) and
      not any(x in calls for x in ['open','eval','exec','compile','__import__']),
      'Direct AST inspection matches finite demographic MGFs plus common/individual Gaussian residuals and one pointwise exponential; no IO, clipping or retries.')

ages=list(range(p['age_min'],p['age_max']+1)); age_center=sum(ages)/len(ages)
prob=p['female_probability']; a=p['log_age_effects']; b=p['log_female_effects']; lam=p['residual_factor_loadings']
states=[(age,f,(prob if f else 1-prob)/len(ages)) for age in ages for f in [0,1]]
effect=lambda age,f,j:a[j]*(age-age_center)/p['age_effect_unit_years']+b[j]*(f-prob)
m1=[math.fsum(w*math.exp(effect(age,f,j)) for age,f,w in states) for j in range(3)]
m2=[math.fsum(w*math.exp(2*effect(age,f,j)) for age,f,w in states) for j in range(3)]
v=[math.log1p((p['biomarker_sds'][j]/p['biomarker_means'][j])**2)-math.log(m2[j]/m1[j]**2) for j in range(3)]
ell=[math.log(p['biomarker_means'][j])-math.log(m1[j])-v[j]/2 for j in range(3)]
K=[[v[j] if j==k else math.sqrt(v[j]*v[k])*lam[j]*lam[k] for k in range(3)] for j in range(3)]
check('state_mass',len(states)==80 and close(math.fsum(w for _,_,w in states),1),
      'Exactly 40 by 2 demographic support states with positive probabilities summing to one; no generated rows.')
check('residual_variance_feasible',all(z>0 and math.isfinite(z) for z in v) and all(abs(x)<1 for x in lam),
      'Demographic second/first-moment ratio leaves strictly positive residual log variances; positive diagonal idiosyncratic residuals give a proper nonsingular law.')
check('finite_sum_matches_generator_factorization',all(close(m1[j],
      math.fsum(math.exp(a[j]*(age-age_center)/p['age_effect_unit_years']) for age in ages)/len(ages)*
      ((1-prob)*math.exp(-prob*b[j])+prob*math.exp((1-prob)*b[j]))) for j in range(3)),
      'Independent joint-state enumeration equals the generator age-MGF times sex-MGF factorization.')

# Derive conditional moments per demographic state, then integrate the full
# mixture. This computes actual law moments, not a desired covariance matrix.
pieces=[]
for age,f,w in states:
    loc=[ell[j]+effect(age,f,j) for j in range(3)]
    first=[math.exp(loc[j]+v[j]/2) for j in range(3)]
    raw=[[math.exp(loc[j]+loc[k]+(v[j]+v[k]+2*K[j][k])/2) for k in range(3)] for j in range(3)]
    moments4=[math.exp(4*loc[j]+8*v[j]) for j in range(3)]
    fullfirst=[age,f,*first]
    fullraw=[[fullfirst[i]*fullfirst[k] for k in range(5)] for i in range(5)]
    for j in range(3):
        for k in range(3):fullraw[j+2][k+2]=raw[j][k]
    pieces.append((w,fullfirst,fullraw,moments4))
means=[math.fsum(w*x[j] for w,x,_,__ in pieces) for j in range(5)]
raw2=[[math.fsum(w*x[j][k] for w,_,x,__ in pieces) for k in range(5)] for j in range(5)]
cov=[[raw2[j][k]-means[j]*means[k] for k in range(5)] for j in range(5)]
fourth=[math.fsum(w*x[j] for w,_,__,x in pieces) for j in range(3)]
sds=[math.sqrt(cov[j][j]) for j in range(5)]
check('all_mixture_moments_finite',all(math.isfinite(x) for x in means+fourth) and
      all(math.isfinite(x) for row in raw2 for x in row),
      'Finite conditional lognormal moments integrated over all 80 bounded demographic states; the same formula proves every finite-power moment exists.')
check('unconditional_scale_recovery',close(means[2:],p['biomarker_means']) and close(sds[2:],p['biomarker_sds']),
      'Actual mixture has the selected unconditional means and total individual SDs despite demographic effects.')
for key,value in [('means',means),('sds',sds),('raw_second_moments',raw2),('covariance',cov),
                  ('residual_log_variances',v),('log_intercepts',ell),('residual_log_covariance',K)]:
    check('retained_'+key,close(value,authored[key]),'Independent full-mixture calculation reproduces the frozen analytic result.')

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

cholesky(K); cholesky(cov)
check('full_covariance_positive_definite',True,'Independent Cholesky factors exist; nonsingular within-state biomarker density plus nondegenerate independent demographics establish population rank analytically.')
names=['age','female',*p['biomarker_order']]; projections={}
for use in analyses:
    ix=[names.index(n) for n in use['predictors']]; y=names.index(use['outcome'])
    M=[[cov[j][k] for k in ix] for j in ix]; rhs=[cov[j][y] for j in ix]
    beta=solve(M,rhs); intercept=means[y]-math.fsum(beta[i]*means[j] for i,j in enumerate(ix))
    residual=max(abs(math.fsum(M[i][j]*beta[j] for j in range(len(ix)))-rhs[i]) for i in range(len(ix)))
    result={'predictors':use['predictors'],'coefficients':dict(zip(use['predictors'],beta)),
            'intercept':intercept,'term':use['term'],'term_value':beta[use['predictors'].index(use['term'])],
            'normal_equation_max_abs_residual':residual}
    projections[use['id']]=result; old=authored['population_ols'][use['id']]
    check('ols_'+use['id'],old['predictors']==use['predictors'] and old['term']==use['term'] and
          close(result['term_value'],old['term_value']) and close(intercept,old['intercept']) and
          all(close(beta[j],old['coefficients'][n]) for j,n in enumerate(use['predictors'])) and residual<1e-11,
          'Independent Cholesky population projection preserves the visible adjustment set and matches all retained coefficients/intercept; no target reference or fit criterion used.')

check('analytic_input_hashes',authored['spec_sha256']==sha(CAND/'model_spec.json') and
      authored['generator_sha256']==sha(CAND/'generator.py'),
      'Retained law calculation is bound to the frozen specification and actual generator bytes.')
feedback=read(CAND/'whole_cohort_feedback.json'); semantics=read(CAND/'source_semantics_v1.json')
check('all_source_checks_unavailable',{x['evidence_id'] for x in feedback['checks']}==set(items) and
      len(feedback['checks'])==32 and all(x['status']=='not_computable' and x['operator'] is None for x in feedback['checks']),
      'All 32 source items are explicitly unavailable in target-table feedback, including contextual scale guidance.')
check('semantic_bindings_unavailable',{x['evidence_id'] for x in semantics['bindings']}==set(items) and
      all(x['definition_status']=='unsupported' and x['source_operator'] is None for x in semantics['bindings']) and
      semantics['evidence_sha256']==sha(CAND/'evidence.json') and semantics['recipe_sha256']==sha(CAND/'whole_cohort_feedback.json'),
      'Unavailable source semantic bindings cover all items and bind the exact evidence/recipe bytes.')
check('frozen_bytes_unchanged',sha(CAND/'freeze.json')==freeze_before and sha(ROOT/'decision.json')==decision_before,
      'Frozen receipt and outside author decision are unchanged.')

result={'reviewer_id':'/root/main_review_g5','candidate':str(CAND),'candidate_freeze_sha256':freeze_before,
        'decision_sha256':decision_before,'review_script_sha256':sha(Path(__file__)),
        'checks':checks,'all_checks_passed':all(c['passed'] for c in checks),'demographic_state_count':80,
        'ordered_variables':names,'means':means,'sds':sds,'raw_second_moments':raw2,'covariance':cov,
        'residual_log_variances':v,'log_intercepts':ell,'residual_log_covariance':K,'biomarker_fourth_moments':fourth,
        'population_ols':projections,'generator_ast_call_inventory':calls,
        'generator_imported':False,'generator_executed':False,'author_script_executed':False,
        'row_sampling_performed':False,'numerical_quadrature_performed':False,'target_results_used':False,
        'lifecycle_verified_candidate_file_count':len(receipt['candidate_files'])}
destination=OUT/'CHNS2009_E0_A05_calculations.json'
destination.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'all_checks_passed':result['all_checks_passed'],'check_count':len(checks),
                  'failed_checks':[c for c in checks if not c['passed']],
                  'candidate_freeze_sha256':freeze_before,'decision_sha256':decision_before,
                  'residual_log_variances':v,'population_ols':projections,'output':str(destination)},indent=2))
