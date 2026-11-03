"""Independent deterministic bounded-factor mixture review.

Reads only this assigned frozen bundle and its profile/decision, plus lifecycle.
No candidate/author code imports, RNG, participant rows, quadrature or references.
"""
import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode=True
W=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
PROJECT=W/'biomedical_research/virtual_cohort_system'
ROOT=W/'evcMS/CHNS2009_E1_A04'; BUNDLE=ROOT/'bundle'; CAND=BUNDLE/'candidates/initial'
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT))
from cohort_harness import lifecycle

def read(path):return lifecycle.read_json(path)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def close(a,b):
    if isinstance(a,list):return isinstance(b,list) and len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    return math.isclose(a,b,rel_tol=1e-11,abs_tol=2e-12)
checks=[]
def check(name,condition,detail):checks.append({'id':name,'passed':bool(condition),'detail':detail})

freeze_before=sha(CAND/'freeze.json'); decision_before=sha(ROOT/'decision.json')
receipt=lifecycle.verify_candidate(BUNDLE,'candidates/initial')
check('lifecycle_verify_candidate',True,'Fresh lifecycle verification passed; no generator import or execution.')
task=read(BUNDLE/'task.json'); profile=read(ROOT/'profile.json'); identity=read(BUNDLE/'input/identity.json')
decision=read(ROOT/'decision.json'); spec=read(CAND/'model_spec.json'); p=spec['parameters']
evidence=read(CAND/'evidence.json'); items={x['id']:x for x in evidence['items']}
packet=read(BUNDLE/'sources/evidence_packet.json')
oplist=read(BUNDLE/'input/source_operations.json')['operations']; ops={x['evidence_id']:x for x in oplist}
uptake=read(CAND/'numerical_uptake.json')['records']; uses={x['operation_id']:x for x in uptake}
analytic=read(CAND/'analytic/results.json')
check('identity_decision',task['task_id']==identity['author_id']==decision['author_id']==ROOT.name and
      profile['information_condition']==identity['information_condition']=='E1' and
      decision['candidate']=='candidates/initial' and decision['action']=='initial_final',
      'CHNS2009 E1 A04 initial_final decision agrees with task/profile/identity.')
check('admitted_evidence_exact',evidence==read(BUNDLE/'input/evidence.json'),'All 36 evidence records and source metadata preserve admitted input.')
check('admitted_packet_exact',packet==read(BUNDLE/'input/reported_packet.json'),'Registered packet matches reported input packet.')
for entry in read(BUNDLE/'registry.json')['artifacts']:
    check('registered_'+entry['source_id'],sha(BUNDLE/entry['path'])==entry['sha256'],entry['path'])

expected=set()
for m in packet['shared_base']['grouped_marginal_records']:
    if m['kind']=='reported_mean_and_individual_sd':pairs=[('_MEAN',m['mean'],'mean'),('_SD',m['individual_sd'],'sd')]
    elif m['kind']=='reported_median_and_quartile_endpoints':pairs=[('_MEDIAN',m['median'],'median'),('_Q1',m['q1'],'quantile'),('_Q3',m['q3'],'quantile')]
    else:
        pairs=[('_FRACTION',m['derived_fraction'],'proportion')]
        check('count_fraction_'+m['id'],close(m['derived_fraction'],m['numerator']/m['denominator']),
              'Count fraction preserves reported sex category; no weighted population proportion claim.')
    for suffix,value,kind in pairs:
        eid=m['id']+suffix; expected.add(eid); e=items[eid]
        check('marginal_'+eid,e['estimate']==value and e['kind']==kind and e['source_id']==m['source_id'] and
              e['locator']==m['locator'],'Marginal statistic type/value/source/locator map to the registered source record.')
relationships={x['id']:x for x in packet['relationship_records']}
for eid,r in relationships.items():
    expected.add(eid); op=ops[eid]; e=items[eid]
    check('relationship_'+eid,e['estimate']==r['reported']['estimate'] and e['unit']==r['reported']['unit'] and
          e['source_id']==r['source_id'] and e['locator']==r['source_locator']==op['locator'] and
          canonical_sha(r)==op['record_canonical_sha256'] and
          hashlib.sha256(op['locator'].encode()).hexdigest()==op['locator_utf8_sha256'],
          'Relationship point, native unit, source, locator and operation-record hashes preserved.')
check('evidence_inventory',set(items)==expected|{'U_NGSP_SCALE'},'Only 31 marginals, four relationships and contextual NGSP guidance are present.')

d=p['design']; t=p['target_context']; q=p['source_projection_constraints']; st=p['structure']
check('task_design',d['n_rows']==task['n_rows']==3000 and d['columns']==[x['name'] for x in task['columns']] and
      t['age_kind']=='integer_uniform' and t['age_low']==35 and t['age_high']==74 and
      'composition is not supplied' in task['population'],
      '3000 rows, six ordered columns and integer target age bounds match; task supplies no exact demographic quotas.')
for key,eid in [('bmi','M_M_BMI'),('glucose','M_M_FSG'),('hba1c','M_M_HBA1C_PERCENT')]:
    check('target_anchor_'+key,t[key+'_mean']==items[eid+'_MEAN']['estimate'] and
          t[key+'_sd']==items[eid+'_SD']['estimate'],'MIND marginal mean and total individual SD are transported scenario anchors, not target observations.')
check('target_female_anchor',t['female_probability']==items['M_M_FEMALE_FRACTION']['estimate'],'Target sex probability uses the admitted MIND female count ratio under explicit transport.')
check('jansen_constraints',q['bmi_ifcc']==items['R_JANSEN_BMI']['estimate'] and q['fpg_ifcc']==items['R_JANSEN_FPG']['estimate'] and
      q['reference_bmi_sd']==items['M_J_BMI_SD']['estimate'] and q['reference_glucose_sd']==items['M_J_FPG_SD']['estimate'],
      'The two separate native IFCC projections and source predictor SDs match their admitted records.')
check('structure_assumed',spec['parameter_provenance']['structure']['evidence_ids']==[],
      'Residual correlation, age and female slopes and bounded uniform law are explicitly assumption-only.')

syntax=ast.parse((CAND/'generator.py').read_text(encoding='utf-8-sig'))
imports=[x.name for n in syntax.body if isinstance(n,ast.Import) for x in n.names]
calls=sorted({ast.unparse(n.func) for n in ast.walk(syntax) if isinstance(n,ast.Call)})
check('generator_static_law',imports==['math','numpy','pandas'] and
      not any(isinstance(n,(ast.ImportFrom,ast.While)) for n in ast.walk(syntax)) and
      not any(x in calls for x in ['open','eval','exec','compile','__import__']),
      'Static code matches centered independent bounded factors/class mixture, with no IO, clipping, rejection or source-row execution.')

scale=p['unit_mapping']['ngsp_multiplier']; offset=p['unit_mapping']['ngsp_offset']
rho=st['bmi_glucose_rho']; sr=math.sqrt(1-rho*rho); half=st['uniform_half_width']
a=st['age_hba1c_coefficient']; sex=st['female_hba1c_coefficient']
VB=q['reference_bmi_sd']**2; VG=q['reference_glucose_sd']**2; C=rho*math.sqrt(VB*VG)
det=VB*VG-C*C; rhsB=scale*q['bmi_ifcc']*VB; rhsG=scale*q['fpg_ifcc']*VG
bb=(VG*rhsB-C*rhsG)/det; bg=(VB*rhsG-C*rhsB)/det
check('derived_joint_coefficients',det>0 and close(bb,analytic['derived_joint_coefficients_percent']['bmi']) and
      close(bg,analytic['derived_joint_coefficients_percent']['glucose']) and close(half*half/3,1),
      'Independent 2x2 inverse solves two distinct source projections under assumed covariance; uniform half-width yields unit factor variance.')
j=p['source_contexts']['CTX_JANSEN_SELECTED']
check('jansen_scale_and_demography',scale==0.09148 and offset==2.152 and
      close(j['hba1c_mean'],scale*items['M_J_HBA1C_IFCC_MEAN']['estimate']+offset) and
      close(j['hba1c_sd'],scale*items['M_J_HBA1C_IFCC_SD']['estimate']) and
      close((j['age_low']+j['age_high'])/2,items['M_J_AGE_MEAN']['estimate']) and
      close((j['age_high']-j['age_low'])/math.sqrt(12),items['M_J_AGE_SD']['estimate']) and
      close(j['female_probability'],1-items['M_J_MALE_FRACTION']['estimate']),
      'NGSP offset applies to source level only, multiplier to SD/slopes; assumed source age uniform and sex membership preserve admitted moments.')

def cholesky(M):
    n=len(M); L=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for k in range(i+1):
            x=M[i][k]-math.fsum(L[i][z]*L[k][z] for z in range(k))
            if i==k:
                if x<=0:raise ValueError('Non-positive covariance pivot')
                L[i][k]=math.sqrt(x)
            else:L[i][k]=x/L[k][k]
    return L
def solve(M,rhs):
    L=cholesky(M); n=len(rhs); z=[0.0]*n; b0=[0.0]*n
    for i in range(n):z[i]=(rhs[i]-math.fsum(L[i][k]*z[k] for k in range(i)))/L[i][i]
    for i in reversed(range(n)):b0[i]=(z[i]-math.fsum(L[k][i]*b0[k] for k in range(i+1,n)))/L[i][i]
    return b0

def independent_context(c):
    lo,hi=c['age_low'],c['age_high']; am=(lo+hi)/2
    av=((hi-lo+1)**2-1)/12 if c['age_kind']=='integer_uniform' else (hi-lo)**2/12
    pf,pc=c['female_probability'],c['class_probability']; vf=pf*(1-pf); vd=pc*(1-pc)
    kg,kh=c['glucose_class_shift'],c['hba1c_class_total_shift']; sb=c['bmi_sd']
    gv=c['glucose_sd']**2-(kg*kg*vd if c['glucose_sd_mode']=='total' else 0)
    assert gv>0; sg=math.sqrt(gv)
    lu=bb*sb+bg*sg*rho; lv=bg*sg*sr
    explained=lu*lu+lv*lv+a*a*av+sex*sex*vf+kh*kh*vd
    hv=c['hba1c_sd']**2-(explained if c['hba1c_sd_mode']=='total' else 0)
    assert hv>0; sh=math.sqrt(hv)
    means=[am,pf,c['bmi_mean'],c['glucose_mean'],c['hba1c_mean']]
    bvar=sb*sb; gvar=gv+kg*kg*vd; hvar=explained+hv
    bgcov=sb*sg*rho; bhcov=sb*lu; ghcov=sg*rho*lu+sg*sr*lv+kg*kh*vd
    cov=[[av,0,0,0,a*av],[0,vf,0,0,sex*vf],[0,0,bvar,bgcov,bhcov],
         [0,0,bgcov,gvar,ghcov],[a*av,sex*vf,bhcov,ghcov,hvar]]
    # Extrema evaluated through the actual sequential B,G,H equation, including
    # extra=(total H shift - betaG*glucose shift), not a duplicate class shift.
    values=[[] for _ in range(5)]
    classes=[0,1] if 0<pc<1 else [int(pc)]
    for A,F,D,U,V,E in itertools.product([lo,hi],[0,1],classes,[-half,half],[-half,half],[-half,half]):
        dc=D-pc; B=c['bmi_mean']+sb*U
        G=c['glucose_mean']+sg*(rho*U+sr*V)+kg*dc
        H=c['hba1c_mean']+bb*(B-c['bmi_mean'])+bg*(G-c['glucose_mean'])+a*(A-am)+sex*(F-pf)+(kh-bg*kg)*dc+sh*E
        for k,x in enumerate([A,F,B,G,H]):values[k].append(x)
    bounds=[[min(x),max(x)] for x in values]
    cholesky(cov)
    return {'means':means,'covariance':cov,'sd':[math.sqrt(cov[k][k]) for k in range(5)],
            'raw_second_moments':[[cov[i][k]+means[i]*means[k] for k in range(5)] for i in range(5)],
            'within_class_glucose_variance':gv,'residual_hba1c_variance':hv,'hba1c_explained_variance':explained,
            'support_bounds':bounds}

contexts={cid:independent_context(c) for cid,c in p['source_contexts'].items()}
contexts['TARGET_SCENARIO']=independent_context(t)
for cid,m in contexts.items():
    old=analytic['target_scenario_algebra'] if cid=='TARGET_SCENARIO' else analytic['source_contexts'][cid]
    varnames=['age','female','bmi','glucose','hba1c'] if cid=='TARGET_SCENARIO' else ['age','gender_binary','BMI','FPG','HbA1c_percent']
    check('moments_'+cid,close(m['means'],old['moments']['means']) and close(m['covariance'],old['moments']['covariance']) and
          close(m['sd'],[old['sd'][k] for k in varnames]) and
          all(close(m[k],old[k]) for k in ['within_class_glucose_variance','residual_hba1c_variance','hba1c_explained_variance']),
          'Direct affine mixture covariance identities reproduce retained actual moments and both variance decompositions; Cholesky pivots are positive.')
    check('support_'+cid,close(m['support_bounds'],[old['support_bounds'][k] for k in varnames]) and
          all(m['support_bounds'][k][0]>0 for k in [2,3,4]),
          'Independent primitive-corner extrema through the implemented sequential equation reproduce all positive support bounds; class shift is not double-counted.')
check('jansen_selection_support',contexts['CTX_JANSEN_SELECTED']['support_bounds'][3][1]<7,
      'The directly selected Jansen source law itself satisfies FPG<7; other eligibility remains a declared membership assumption.')
check('target_total_scales',close(contexts['TARGET_SCENARIO']['sd'][2:],[t['bmi_sd'],t['glucose_sd'],t['hba1c_sd']]),
      'Centered class effects preserve target means and positive within-class variance adjustments recover total source-anchored marginal SDs.')
check('finite_moment_proof',all(math.isfinite(x) for m in contexts.values() for row in m['raw_second_moments'] for x in row),
      'All primitive supports and finite mixture branches are bounded. Actual affine outputs therefore have finite absolute moments of every positive order, not merely finite sampled outputs.')

projections={}
for key,ix,term in [('E1',[0,1,2],2),('E2',[0,1,3],3),('E3',[1,2,3,0],0)]:
    m=contexts['TARGET_SCENARIO']; cov=m['covariance']; beta=solve([[cov[i][k] for k in ix] for i in ix],[cov[i][4] for i in ix])
    projections[key]=beta[ix.index(term)]
    check('target_law_projection_'+key,close(projections[key],analytic['target_scenario_algebra']['assumption_dependent_target_projection_implications'][key]),
          'Independent population OLS solution reproduces the retained assumption-dependent target-law implication; no target reference or favorable-fit criterion.')
check('age_assumption_not_inferred',close(projections['E3'],a),'Joint age coefficient is the explicit assumed additive term, not an inferred source or clinical effect.')

comparisons={x['evidence_id']:x for x in analytic['source_comparisons']}; values={}
jcov=contexts['CTX_JANSEN_SELECTED']['covariance']
for eid,term in [('R_JANSEN_BMI',2),('R_JANSEN_FPG',3)]:
    ix=[0,1,term]; beta=solve([[jcov[i][k] for k in ix] for i in ix],[jcov[i][4]/scale for i in ix])
    values[eid]=beta[-1]
bcov=contexts['CTX_BAO_ANALYZED']['covariance']
values['R_BAO_PEARSON']=bcov[3][4]/math.sqrt(bcov[3][3]*bcov[4][4])
for eid,value in values.items():
    old=comparisons[eid]
    check('source_operation_'+eid,close(value,old['calculated_value']) and old['reported_source_point']==items[eid]['estimate'] and
          close(value-items[eid]['estimate'],old['raw_calculated_minus_reported']),
          'Independent native-IFCC separate projection or native-measure Pearson arithmetic reproduces the retained point and raw discrepancy.')
check('mind_contextual_not_numeric',uses['R_MIND_SPEARMAN']['use']=='context_only' and
      not uses['R_MIND_SPEARMAN']['parameter_paths'] and not uses['R_MIND_SPEARMAN']['analytic_artifacts'] and
      'R_MIND_SPEARMAN' not in comparisons and [x['evidence_id'] for x in analytic['unavailable']]==['R_MIND_SPEARMAN'],
      'No MIND rank law is supplied; its record truthfully declines numeric uptake. Neither Pearson nor another population substitutes for Spearman.')
check('operation_inventory',len(uptake)==len(uses)==len(ops)==4 and set(uses)==set(ops),
      'Every admitted non-marginal operation is accounted for: two constraints, one analytic check and one contextual use.')
assumptions={x['id'] for x in spec['assumptions']}
for eid,u in uses.items():
    required_use='model_constraint' if eid.startswith('R_JANSEN') else ('analytic_check' if eid=='R_BAO_PEARSON' else 'context_only')
    check('uptake_'+eid,u['use']==required_use and u['evidence_id']==eid and u['source_id']==items[eid]['source_id'] and
          u['context_id']==relationships[eid]['source_context_id'] and set(u['assumptions'])<=assumptions and
          all(bool(u[k]) for k in ['population_selection','measurement_assumptions','uncertainty_treatment','cross_source_overlap','reason']),
          'Source/evidence/context, use category, selection/measurement, overlap and uncertainty caveats are explicitly traceable.')
    for path in u['parameter_paths']+u['analytic_artifacts']:
        filename,_,pointer=path.partition('#'); fp=(CAND/filename).resolve()
        exists=fp.is_relative_to(CAND.resolve()) and fp.is_file()
        if pointer and exists:
            obj=read(fp)
            for key in pointer.lstrip('/').split('/'):obj=obj[key.replace('~1','/').replace('~0','~')]
        check('artifact_'+eid+'_'+path,exists,'Numeric uses identify existing frozen artifacts and resolvable parameter pointers.')

hashfiles={'model_spec_sha256':CAND/'model_spec.json','generator_text_sha256':CAND/'generator.py',
           'derivation_script_sha256':CAND/'analytic/derive.py','admitted_operations_sha256':BUNDLE/'input/source_operations.py'}
check('analytic_bindings',all(analytic['bindings'][k]==sha(v) for k,v in hashfiles.items()),'Retained analytic hashes bind the actual specification/generator/script/admitted operator.')
feedback=read(CAND/'whole_cohort_feedback.json'); semantics=read(CAND/'source_semantics_v1.json')
numeric={k for k,v in items.items() if v['kind']!='contextual'}; scheduled={x['evidence_id'] for x in feedback['checks']}
check('source_comparisons_unavailable',numeric<=scheduled<=set(items) and len(scheduled)==len(feedback['checks']) and
      all(x['status']=='not_computable' and x['operator'] is None for x in feedback['checks']),
      'All quantitative source comparisons on target tables are unavailable; no target-to-source statistic is enabled.')
check('semantic_bindings_unavailable',{x['evidence_id'] for x in semantics['bindings']}==scheduled and
      all(x['definition_status']=='unsupported' and x['source_operator'] is None for x in semantics['bindings']) and
      semantics['evidence_sha256']==sha(CAND/'evidence.json') and semantics['recipe_sha256']==sha(CAND/'whole_cohort_feedback.json'),
      'Unavailable semantics exactly match scheduled checks and evidence/recipe hashes.')
check('frozen_bytes_unchanged',sha(CAND/'freeze.json')==freeze_before and sha(ROOT/'decision.json')==decision_before,
      'Frozen candidate receipt and outside decision remained unchanged.')

result={'reviewer_id':'/root/main_review_g5','candidate':str(CAND),'candidate_freeze_sha256':freeze_before,
        'decision_sha256':decision_before,'review_script_sha256':sha(Path(__file__)),
        'checks':checks,'all_checks_passed':all(x['passed'] for x in checks),'derived_joint_coefficients_percent':{'bmi':bb,'glucose':bg},
        'contexts':contexts,'target_law_projections':projections,'source_operations':{k:{'calculated':v,'reported':items[k]['estimate'],
        'difference':v-items[k]['estimate']} for k,v in values.items()},'unavailable_rank':'R_MIND_SPEARMAN',
        'generator_ast_call_inventory':calls,'generator_imported':False,'generator_executed':False,'author_script_executed':False,
        'row_sampling_performed':False,'numerical_quadrature_performed':False,'target_results_used':False,
        'lifecycle_verified_candidate_file_count':len(receipt['candidate_files'])}
destination=OUT/'CHNS2009_E1_A04_calculations.json'
destination.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'all_checks_passed':result['all_checks_passed'],'check_count':len(checks),
                  'failed_checks':[x for x in checks if not x['passed']],
                  'candidate_freeze_sha256':freeze_before,'decision_sha256':decision_before,
                  'source_operations':result['source_operations'],'target_law_projections':projections,
                  'target_support':contexts['TARGET_SCENARIO']['support_bounds'],'output':str(destination)},indent=2))
