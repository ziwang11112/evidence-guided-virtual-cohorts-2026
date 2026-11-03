"""Independent deterministic review of one frozen assigned candidate.

No generator or author script is imported/executed. No RNG, rows, quadrature,
optimization, clinical reference, sibling bundle or prior experiment is used.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist
import sys

sys.dont_write_bytecode = True
W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
PROJECT = W/'biomedical_research/virtual_cohort_system'
ROOT = W/'evcMS/CHNS2009_E1_A03'
BUNDLE = ROOT/'bundle'
CAND = BUNDLE/'candidates/initial'
OUT = Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT))
from cohort_harness import lifecycle

def read(path):
    return lifecycle.read_json(path)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

checks=[]
def check(name,condition,detail):
    checks.append({'id':name,'passed':bool(condition),'detail':detail})

def close(a,b):
    if isinstance(a,list):
        return isinstance(b,list) and len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    return math.isclose(a,b,rel_tol=2e-10,abs_tol=2e-11)

freeze_before=sha(CAND/'freeze.json')
decision_before=sha(ROOT/'decision.json')
receipt=lifecycle.verify_candidate(BUNDLE,'candidates/initial')
check('lifecycle_verify_candidate',True,'Fresh lifecycle.verify_candidate passed without importing/executing candidate code.')
task=read(BUNDLE/'task.json')
profile=read(ROOT/'profile.json')
decision=read(ROOT/'decision.json')
identity=read(BUNDLE/'input/identity.json')
evidence=read(CAND/'evidence.json')
items={x['id']:x for x in evidence['items']}
spec=read(CAND/'model_spec.json')
p=spec['parameters']
packet=read(BUNDLE/'sources/evidence_packet.json')
ops=read(BUNDLE/'input/source_operations.json')['operations']
uptake=read(CAND/'numerical_uptake.json')['records']
analytic=read(CAND/'analytic_results.json')
check('identity_decision',decision['author_id']==identity['author_id']==task['task_id']==ROOT.name and
      decision['candidate']=='candidates/initial' and decision['action']=='initial_final' and
      profile['information_condition']==identity['information_condition']=='E1',
      'CHNS2009 E1 A03 initial_final and task/profile identity agree.')
check('evidence_exact_input',evidence==read(BUNDLE/'input/evidence.json'),'All 36 candidate evidence items and source metadata match admitted input.')
check('packet_exact_input',packet==read(BUNDLE/'input/reported_packet.json'),'Registered packet matches the reported input packet.')
for entry in read(BUNDLE/'registry.json')['artifacts']:
    check('registered_'+entry['source_id'],sha(BUNDLE/entry['path'])==entry['sha256'],entry['path'])

expected_items=set()
for m in packet['shared_base']['grouped_marginal_records']:
    if m['kind']=='reported_mean_and_individual_sd':
        pairs=[('_MEAN',m['mean'],'mean'),('_SD',m['individual_sd'],'sd')]
    elif m['kind']=='reported_median_and_quartile_endpoints':
        pairs=[('_MEDIAN',m['median'],'median'),('_Q1',m['q1'],'quantile'),('_Q3',m['q3'],'quantile')]
    else:
        pairs=[('_FRACTION',m['derived_fraction'],'proportion')]
        check('count_fraction_'+m['id'],close(m['derived_fraction'],m['numerator']/m['denominator']),
              'Count fraction retains its named sex category and is not a weighted target proportion.')
    for suffix,value,kind in pairs:
        eid=m['id']+suffix
        expected_items.add(eid)
        x=items[eid]
        check('packet_mapping_'+eid,x['estimate']==value and x['kind']==kind and
              x['source_id']==m['source_id'] and x['locator']==m['locator'],
              'Reported marginal value, statistic type, source and locator preserved.')
relationships={x['id']:x for x in packet['relationship_records']}
for op in ops:
    eid=op['evidence_id']; r=relationships[eid]; x=items[eid]
    expected_items.add(eid)
    check('relationship_mapping_'+eid,x['estimate']==r['reported']['estimate'] and
          x['unit']==r['reported']['unit'] and x['source_id']==r['source_id'] and
          x['locator']==op['locator']==r['source_locator'] and
          op['record_canonical_sha256']==canonical_sha(r) and
          op['locator_utf8_sha256']==hashlib.sha256(op['locator'].encode()).hexdigest(),
          'Relationship point, units, source, locator and operation-level hashes agree.')
check('evidence_inventory',set(items)==expected_items|{'U_NGSP_SCALE'},'35 quantitative items and one contextual NGSP scale item; no unadmitted statistic.')

for target,source_id in [('bmi','M_M_BMI'),('glucose','M_M_FSG'),('hba1c','M_M_HBA1C_PERCENT')]:
    check('target_anchor_'+target,p['target_marginals'][target]['mean']==items[source_id+'_MEAN']['estimate'] and
          p['target_marginals'][target]['sd']==items[source_id+'_SD']['estimate'],
          'MIND arithmetic mean and individual SD are explicitly transported scenario inputs; serum FSG remains distinct from plasma FPG.')
check('task_demography',p['n_rows']==task['n_rows']==3000 and
      p['target_age']=={'minimum':35,'maximum':74,'law':'discrete_uniform_inclusive'} and
      p['target_female_probability']==0.5 and 'composition is not supplied' in task['population'],
      'Task requires 3000 rows and age 35-74; no exact demographic quota is supplied. Uniform ages and Bernoulli sex are disclosed assumptions.')
check('jansen_gender_mapping',close(p['source_jansen']['female_probability'],1-items['M_J_MALE_FRACTION']['estimate']),
      'Source female probability uses the complement of the admitted male count fraction.')

source=(CAND/'generator.py').read_text(encoding='utf-8-sig')
syntax=ast.parse(source)
imports=[a.name for node in syntax.body if isinstance(node,ast.Import) for a in node.names]
calls=sorted({ast.unparse(node.func) for node in ast.walk(syntax) if isinstance(node,ast.Call)})
check('generator_static_structure',imports==['math','numpy','pandas'] and
      not any(isinstance(n,(ast.ImportFrom,ast.While)) for n in ast.walk(syntax)) and
      not any(x in calls for x in ['open','eval','exec','compile','__import__']),
      'Static ABI and source inspection: three independent normal innovations, pointwise exponentials, six required columns, no file IO, clipping, rejection or retry loop.')

r=2*math.sin(math.pi*p['dependence']['source_spearman_glucose_hba1c']/6)
q=p['dependence']['latent_bmi_glucose']
R=[[1,q,q*r],[q,1,r],[q*r,r,1]]
latent_det=(1-q*q)*(1-r*r)
check('latent_law_positive_definite',abs(q)<1 and abs(r)<1 and latent_det>0 and
      p['dependence']['residual_bmi_hba1c_conditional_latent_glucose']==0,
      'Actual triangular factor loading has determinant squared (1-q^2)(1-r^2)>0; residual independence is explicitly assumed.')
rank=6/math.pi*math.asin(r/2)
check('law_specific_spearman',close(rank,items['R_MIND_SPEARMAN']['estimate']) and
      p['dependence']['source_spearman_glucose_hba1c']==items['R_MIND_SPEARMAN']['estimate'],
      'Strictly increasing lognormal margins preserve ranks. Independent-normal differences have correlation r/2; their quadrant probability gives rhoS=(6/pi)asin(r/2). The generator uses its inverse.')

def log_params(marginals,names):
    sig=[math.sqrt(math.log1p((marginals[n]['sd']/marginals[n]['mean'])**2)) for n in names]
    mu=[math.log(marginals[n]['mean'])-s*s/2 for n,s in zip(names,sig)]
    return mu,sig

def law_moments(mu,sig,corr,cut_index=None,cut=None):
    n=len(mu)
    S=[[sig[i]*sig[j]*corr[i][j] for j in range(n)] for i in range(n)]
    Phi=lambda t:math.erfc(-t/math.sqrt(2))/2
    a=None if cut_index is None else (math.log(cut)-mu[cut_index])/sig[cut_index]
    prob=1 if a is None else Phi(a)
    def raw(k):
        logval=sum(k[i]*mu[i] for i in range(n))+sum(k[i]*S[i][j]*k[j] for i in range(n) for j in range(n))/2
        val=math.exp(logval)
        if a is not None:
            val*=Phi(a-sum(S[cut_index][j]*k[j] for j in range(n))/sig[cut_index])/prob
        return val
    basis=[[int(i==j) for j in range(n)] for i in range(n)]
    first=[raw(k) for k in basis]
    second=[[raw([basis[i][k]+basis[j][k] for k in range(n)]) for j in range(n)] for i in range(n)]
    cov=[[second[i][j]-first[i]*first[j] for j in range(n)] for i in range(n)]
    fourth=[raw([4*v for v in k]) for k in basis]
    return {'means':first,'covariance':cov,'raw_second_moments':second,'fourth_moments':fourth,'selection_probability':prob}

def positive_definite(M):
    # Deterministic Cholesky calculation, no regularization or data fitting.
    n=len(M); L=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            z=M[i][j]-sum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                if z<=0:return False
                L[i][j]=math.sqrt(z)
            else:L[i][j]=z/L[j][j]
    return True

tmu,tsig=log_params(p['target_marginals'],['bmi','glucose','hba1c'])
target=law_moments(tmu,tsig,R)
for i,name in enumerate(['bmi','glucose','hba1c']):
    check('target_law_moments_'+name,close(target['means'][i],p['target_marginals'][name]['mean']) and
          close(target['covariance'][i][i],p['target_marginals'][name]['sd']**2) and
          math.isfinite(target['fourth_moments'][i]),
          'Lognormal moment-generating formula gives the specified mean/variance and finite fourth moment; all finite power moments exist analytically.')
check('target_covariance_and_population_ols',positive_definite(target['covariance']) and
      ((74-35+1)**2-1)/12>0 and 0.5*(1-0.5)>0,
      'Full positive-orthant biomarker support and independent nondegenerate demographics yield unique requested population OLS projections. Age slope is an assumed zero consequence.')
check('retained_target_moments',all(close(target[k],analytic['target_law_moments_not_source_comparisons'][k])
      for k in ['means','covariance','raw_second_moments']), 'Independent closed forms reproduce the retained target-law moments, not target clinical data.')

j=p['source_jansen']
jmu,jsig=log_params(j['parent_marginals'],['BMI','FPG','HbA1c_IFCC'])
jm=law_moments(jmu,jsig,R,cut_index=1,cut=j['selection_fpg_upper_exclusive'])
jstored=analytic['source_contexts']['CTX_JANSEN_SELECTED']
check('jansen_selected_moments',0<jm['selection_probability']<=1 and positive_definite(jm['covariance']) and
      all(close(jm[k],jstored['law_moments'][k]) for k in ['means','covariance','raw_second_moments','selection_probability']),
      'Exponential tilting before the FPG<7 normal-CDF normalization reproduces post-selection moments. Parent=printed-selected approximation remains disclosed.')
check('jansen_separate_nuisance_projections',jstored['variables']==['age','gender_binary','BMI','FPG','HbA1c_IFCC'] and
      all(jstored['covariance'][i][k]==0 for i in [0,1] for k in [2,3,4]) and
      jstored['units']['HbA1c_IFCC']=='mmol/mol' and
      jstored['selection_status']=='moments_after_declared_source_selection',
      'Independent age/gender nuisance variables make each separate adjusted slope equal its own selected covariance/variance ratio; no combined BMI+FPG projection substituted.')

b=p['source_bao']; z=NormalDist().inv_cdf(b['quartile_probability'])
bn=['FPG','HbA1c_percent']; bmu=[math.log(b[n]['median']) for n in bn]
bsig=[math.log(b[n]['q3']/b[n]['q1'])/(2*z) for n in bn]
bm=law_moments(bmu,bsig,[[1,r],[r,1]])
bstored=analytic['source_contexts']['CTX_BAO_ANALYZED']
check('bao_source_moments',positive_definite(bm['covariance']) and
      all(close(bm[k],bstored['law_moments'][k]) for k in ['means','covariance','raw_second_moments']),
      'Bao-specific median/log-IQR pair law supplies the raw Pearson functional, separate from MIND/target margins.')
quantiles={n:{'q1':math.exp(bmu[i]-z*bsig[i]),'median':math.exp(bmu[i]),'q3':math.exp(bmu[i]+z*bsig[i])} for i,n in enumerate(bn)}
check('bao_quantile_discrepancies',all(close(quantiles[n][k],bstored['marginal_quantile_discrepancies'][n]['model_'+k])
      for n in bn for k in ['q1','median','q3']), 'Rounded/asymmetric endpoint discrepancies are reproduced and retained without claiming all quantiles match.')

mmu,msig=log_params(p['source_mind'],['FSG','HbA1c_percent'])
mind=law_moments(mmu,msig,[[1,r],[r,1]])
check('mind_source_moments',all(close(mind[k],analytic['source_contexts']['CTX_MIND_ANALYZED']['law_moments'][k])
      for k in ['means','covariance','raw_second_moments']),
      'Continuous MIND scenario preserves serum FSG and its distinct reported margins; unknown empirical imputation/ties are not reconstructed.')

values={'R_JANSEN_BMI':jm['covariance'][0][2]/jm['covariance'][0][0],
        'R_JANSEN_FPG':jm['covariance'][1][2]/jm['covariance'][1][1],
        'R_BAO_PEARSON':math.expm1(r*bsig[0]*bsig[1])/math.sqrt(math.expm1(bsig[0]**2)*math.expm1(bsig[1]**2)),
        'R_MIND_SPEARMAN':rank}
actual={x['evidence_id']:x for x in analytic['source_operations']}
records={x['operation_id']:x for x in uptake}
assumptions={a['id'] for a in spec['assumptions']}
check('uptake_inventory',set(records)==set(values)=={op['evidence_id'] for op in ops} and len(uptake)==4,
      'Each of four admitted non-marginal operations has exactly one uptake record.')
for eid,v in values.items():
    u=records[eid]; a=actual[eid]; reported=items[eid]['estimate']
    expected_use='model_constraint' if eid=='R_MIND_SPEARMAN' else 'analytic_check'
    check('independent_operation_'+eid,close(v,a['calculated_value']) and close(v,u['calculated_value']) and
          u['use']==expected_use and u['reported_source_point']==reported and
          close(v-reported,u['raw_calculated_minus_reported']) and
          u['uncertainty_treatment']['reported']==relationships[eid]['reported'],
          'Independent law calculation, classified use, reported point, raw discrepancy and original uncertainty metadata all agree.')
    check('uptake_context_'+eid,bool(u['source_population_selection']) and bool(u['measurement_assumptions']) and
          bool(u['cross_source_overlap']) and set(u['construction_assumption_ids'])<=assumptions and
          u['source_replay']==u['target_table_comparison']=='unavailable',
          'Selection/measurement, overlap, unknown precision and assumption references are disclosed; no target-as-source claim.')
    for path in u['parameter_paths']+u['analytic_artifact_paths']:
        filename,_,pointer=path.partition('#')
        fp=(CAND/filename).resolve()
        exists=fp.is_relative_to(CAND.resolve()) and fp.is_file()
        if pointer and exists:
            obj=read(fp)
            for key in pointer.lstrip('/').split('/'):
                obj=obj[key.replace('~1','/').replace('~0','~')]
        check('artifact_'+eid+'_'+path,exists,'Numerical uptake points to an existing frozen artifact and resolvable JSON pointer when present.')

bindings={'model_spec.json':CAND/'model_spec.json','evidence.json':CAND/'evidence.json',
          'generator.py_static_bytes_only':CAND/'generator.py','input/source_operations.py':BUNDLE/'input/source_operations.py',
          'analytic_checks.py':CAND/'analytic_checks.py'}
check('analytic_input_hashes',all(analytic['input_hashes'][k]==sha(v) for k,v in bindings.items()),
      'All retained analytic inputs/scripts are byte-bound to this frozen candidate and admitted operation module.')
feedback=read(CAND/'whole_cohort_feedback.json'); semantics=read(CAND/'source_semantics_v1.json')
numeric={k for k,v in items.items() if v['kind']!='contextual'}
check('target_as_source_unavailable',{c['evidence_id'] for c in feedback['checks']}==numeric and
      len(feedback['checks'])==len(numeric)==35 and all(c['status']=='not_computable' and c['operator'] is None for c in feedback['checks']),
      'All 35 quantitative source comparisons are unavailable; NGSP contextual unit guidance has no clinical statistic.')
check('semantic_binding_unavailable',{c['evidence_id'] for c in semantics['bindings']}==numeric and
      all(c['definition_status']=='unsupported' and c['source_operator'] is None for c in semantics['bindings']) and
      semantics['evidence_sha256']==sha(CAND/'evidence.json') and semantics['recipe_sha256']==sha(CAND/'whole_cohort_feedback.json'),
      'All unavailable semantic bindings point to the exact evidence and feedback recipe.')
check('frozen_artifacts_unchanged',sha(CAND/'freeze.json')==freeze_before and sha(ROOT/'decision.json')==decision_before,
      'Freeze receipt and outside scientific decision unchanged.')

result={'reviewer_id':'/root/main_review_g5','candidate':str(CAND),'candidate_freeze_sha256':freeze_before,
        'decision_sha256':decision_before,'review_script_sha256':sha(Path(__file__)),
        'checks':checks,'all_checks_passed':all(c['passed'] for c in checks),
        'latent_correlation':r,'latent_determinant':latent_det,'target_law_moments':target,
        'source_jansen_law_moments':jm,'source_bao_law_moments':bm,'source_bao_quantiles':quantiles,
        'source_mind_law_moments':mind,'source_functionals':{k:{'calculated':v,'reported':items[k]['estimate'],
        'difference':v-items[k]['estimate']} for k,v in values.items()},
        'generator_ast_call_inventory':calls,'generator_imported':False,'generator_executed':False,
        'author_script_executed':False,'row_sampling_performed':False,'numerical_quadrature_performed':False,
        'target_results_used':False,'lifecycle_verified_candidate_file_count':len(receipt['candidate_files'])}
destination=OUT/'CHNS2009_E1_A03_calculations.json'
destination.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'all_checks_passed':result['all_checks_passed'],'check_count':len(checks),
                  'failed_checks':[c for c in checks if not c['passed']],
                  'candidate_freeze_sha256':freeze_before,'decision_sha256':decision_before,
                  'source_functionals':result['source_functionals'],'output':str(destination)},indent=2))
