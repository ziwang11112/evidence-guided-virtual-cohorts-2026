"""Independent C5 actual-output audit. Uses stdlib arithmetic, never generators/evaluator."""
import csv
from datetime import datetime, timedelta, timezone
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

P = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
R = P/'work/c5'
O = R/'review/postrun_audit'
sys.path.insert(0,str(P))
from cohort_harness.execution import verify_execution
from cohort_harness.lifecycle import verify_candidate
from work.c5.method.adapter import verify_transition, verify_preservation


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name,obj):
    with (O/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')


checks=[]
numeric=[]
def check(name,condition,detail=None):
    checks.append({'check':name,'pass':bool(condition),'detail':detail})


def numeric_check(name,actual,reported):
    delta=abs(actual-reported)
    ok=math.isfinite(actual) and math.isfinite(reported) and delta <= 1e-9 + 1e-11*max(abs(actual),abs(reported))
    numeric.append({'field':name,'independent':actual,'reported':reported,'absolute_difference':delta,'pass':ok})


def compare(name,actual,reported):
    if isinstance(actual,dict):
        check(name+'.keys',set(actual)==set(reported))
        for k,v in actual.items():
            if k in reported: compare(name+'.'+k,v,reported[k])
    elif isinstance(actual,(int,float)) and not isinstance(actual,bool):
        numeric_check(name,float(actual),float(reported))
    else:
        check(name,actual==reported)


def avg(x): return math.fsum(x)/len(x)
def cov(x,y):
    a,b=avg(x),avg(y)
    return math.fsum((u-a)*(v-b) for u,v in zip(x,y))/(len(x)-1)
def sd(x): return math.sqrt(cov(x,x))
def corr(x,y): return cov(x,y)/math.sqrt(cov(x,x)*cov(y,y))
def quantile(x,q):
    values=sorted(x); t=(len(values)-1)*q; k=math.floor(t); w=t-k
    return values[k] if k==len(values)-1 else values[k]+w*(values[k+1]-values[k])
def item(v,truth):
    return {'estimate':v,'analytical_reference':truth,'signed_deviation':v-truth,'absolute_deviation':abs(v-truth)}


packet=load(R/'visible/final_source_packet.json')
names=[v['name'] for v in packet['variables']]
raw={(x['kind'],tuple(x['variables'])):F(str(x['value'])) for x in packet['reported_statistics']}
mu=[raw['mean',(x,)] for x in names]
sdev=[raw['sd',(x,)] for x in names]
sigma=[[sdev[i]**2 if i==j else sdev[i]*sdev[j]*raw['pearson_correlation',tuple(sorted([names[i],names[j]]))]
        for j in range(3)] for i in range(3)]
det=sigma[0][0]*sigma[1][1]-sigma[0][1]**2
beta=[(sigma[1][1]*sigma[0][2]-sigma[0][1]*sigma[1][2])/det,
      (sigma[0][0]*sigma[1][2]-sigma[0][1]*sigma[0][2])/det]
var=sigma[2][2]-sigma[0][2]*beta[0]-sigma[1][2]*beta[1]
intercept=mu[2]-beta[0]*mu[0]-beta[1]*mu[1]
truth={'A1_slope_x1':float(sigma[0][1]/sigma[0][0]),
       'A1_intercept':float(mu[1]-(sigma[0][1]/sigma[0][0])*mu[0]),
       'A2_slope_x1':float(beta[0]),'A2_slope_x2':float(beta[1]),'A2_intercept':float(intercept),
       'A3_residual_variance':float(var),'A3_residual_sd':math.sqrt(float(var))}


def analyze(frame):
    cols=list(frame); x,z=frame['x1'],frame['x2']; n=len(x)
    b=cov(x,z)/cov(x,x); a=avg(z)-b*avg(x)
    endpoints={'A1_slope_x1':item(b,truth['A1_slope_x1']),'A1_intercept':item(a,truth['A1_intercept'])}
    residual_checks=None
    if 'x3' in frame:
        y=frame['x3']; xx,zz,xz=cov(x,x),cov(z,z),cov(x,z)
        xy,zy=cov(x,y),cov(z,y); d=xx*zz-xz*xz
        bx,bz=(zz*xy-xz*zy)/d,(xx*zy-xz*xy)/d
        intercept_fit=avg(y)-bx*avg(x)-bz*avg(z)
        residuals=[v-intercept_fit-bx*u-bz*w for u,w,v in zip(x,z,y)]
        rv=math.fsum(v*v for v in residuals)/(n-3)
        values={'A2_intercept':intercept_fit,'A2_slope_x1':bx,'A2_slope_x2':bz,
                'A3_residual_variance':rv,'A3_residual_sd':math.sqrt(rv)}
        endpoints.update({k:item(v,truth[k]) for k,v in values.items()})
        pop_residuals=[v-(float(mu[2])+float(beta[0])*(u-float(mu[0]))+float(beta[1])*(w-float(mu[1])))
                       for u,w,v in zip(x,z,y)]
        residual_checks={'residual_definition':'x3 minus the analytical population conditional mean',
                         'mean':item(avg(pop_residuals),0.0),'sd':item(sd(pop_residuals),math.sqrt(float(var))),
                         'pearson_with_x1':item(corr(pop_residuals,x),0.0),
                         'pearson_with_x2':item(corr(pop_residuals,z),0.0)}
    diag={'mean':{},'sd':{},'quantiles':{},'covariance':{},'correlation':{}}
    for c in cols:
        i=names.index(c); values=frame[c]
        diag['mean'][c]=item(avg(values),float(mu[i]))
        diag['sd'][c]=item(sd(values),float(sdev[i]))
        diag['quantiles'][c]={str(q):item(quantile(values,q),float(mu[i])+float(sdev[i])*statistics.NormalDist().inv_cdf(q))
                              for q in [0.05,0.5,0.95]}
        for d in cols[cols.index(c):]:
            j=names.index(d); key=c+','+d
            diag['covariance'][key]=item(cov(values,frame[d]),float(sigma[i][j]))
            if c!=d: diag['correlation'][key]=item(corr(values,frame[d]),float(sigma[i][j]/(sdev[i]*sdev[j])))
    return {'endpoints':endpoints,'source_and_distribution_checks':diag,'population_conditional_residual_checks':residual_checks}


manifest=load(R/'final_output_manifest.json'); plan=load(R/'RUN_PLAN.json'); contract=load(R/'visible/output_contract.json')
started=load(R/'EXECUTION_STARTED.json'); reveal=load(R/'reveal_authorization.json')
evaluation=load(R/'evaluation/evaluation.json')
check('manifest_matches_parent_report_pin',sha(R/'final_output_manifest.json')=='e4a88df08a18d8fabf0fd111b7bbbed7ca73d3f876c5f9d74d58358faa363935')
check('frozen_plan_pinned_by_execution_start',sha(R/'RUN_PLAN.json')==started['plan_sha256'])
check('scheduled_runs_match_public_contract',plan['runs']==contract['runs'] and len(plan['runs'])==9)
for rel,value in plan['bindings'].items(): check('plan_binding:'+rel,sha(R/rel)==value)
for rel,value in plan['harness'].items(): check('native_harness_binding:'+rel,sha(P/'cohort_harness'/rel)==value)
history=load(R/'HISTORICAL_BINDINGS.json')
for rel,value in history['bindings'].items(): check('historical_anchor:'+rel,sha(P/rel)==value)
prior=load(R/'review/preexec_adapter_audit_01/SCIENCE_REVIEW_CHECKS.json')
for rel,value in prior['bindings'].items(): check('preexecution_science_binding:'+rel,sha(R/rel)==value)
check('reveal_bound_to_manifest',reveal['final_output_manifest_sha256']==sha(R/'final_output_manifest.json'))
check('evaluation_bound_to_manifest',evaluation['final_output_manifest_sha256']==sha(R/'final_output_manifest.json'))
check('recorded_sequence',datetime.fromisoformat(plan['created_utc'])<datetime.fromisoformat(started['created_utc'])<
      datetime.fromisoformat(manifest['committed_utc'])<datetime.fromisoformat(reveal['authorized_utc'])<datetime.fromisoformat(evaluation['evaluated_utc']))
compare('analytic_primary_answers',truth,evaluation['analytical_reference']['analytical_answers'])
results={}; tables={}; lexical={}; elapsed=[]; receipt_bindings={}; runtime_versions=[]
check('manifest_all_nine_unique_slots',len(manifest['outputs'])==9 and len({x['run_id'] for x in manifest['outputs']})==9)
for rec,expected in zip(manifest['outputs'],plan['runs']):
    run_id=rec['run_id']; path=Path(rec['path']); bundle=path.parents[3]
    check(run_id+'.schedule',{k:rec[k] for k in expected}==expected)
    check(run_id+'.output_hash',sha(path)==rec['sha256'])
    receipt=verify_execution(bundle,run_id)
    check(run_id+'.native_success',receipt['status']=='success' and receipt['generator_executed'] is True)
    check(run_id+'.seed',receipt['limits']['seed']==rec['seed'])
    elapsed.append({'run_id':run_id,'elapsed_seconds':receipt['elapsed_seconds']})
    receipt_bindings[run_id]=sha(bundle/'executions'/run_id/'execution.json')
    worker=load(bundle/'executions'/run_id/'output/worker_report.json')
    runtime_versions.append(worker.get('runtime',{}))
    check(run_id+'.completed_before_manifest',datetime.fromisoformat(receipt['created_utc'])+timedelta(seconds=receipt['elapsed_seconds'])<=datetime.fromisoformat(manifest['committed_utc']))
    with path.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream); fields=reader.fieldnames; rows=list(reader)
    wanted=['subject_id','x1','x2']+([] if rec['arm']=='parent' else ['x3'])
    structure={'column_order':fields==wanted,'row_count':len(rows)==2000,
               'identifiers':all(row['subject_id'] for row in rows) and len({row['subject_id'] for row in rows})==len(rows)}
    frame={key:[float(row[key]) for row in rows] for key in wanted[1:]}
    structure['finite_numeric_values']=all(math.isfinite(v) for values in frame.values() for v in values)
    compare(run_id+'.structure',structure,evaluation['runs'][run_id]['structural_checks'])
    tables[run_id]=frame; lexical[run_id]=rows
    analysis=analyze(frame)
    compare(run_id+'.analysis',analysis,evaluation['runs'][run_id]['analysis'])
    results[run_id]={'arm':rec['arm'],'replicate':rec['replicate'],'analysis':analysis,'structure':structure}

actual_receipts=list((R/'b').rglob('execution.json'))+list((R/'t').rglob('execution.json'))
check('exactly_nine_actual_scientific_receipts',len(actual_receipts)==9)
check('no_execution_under_routes',not list((R/'routes').rglob('execution.json')))
check('all_receipts_match_scheduled_paths',{p.parent.name for p in actual_receipts}=={x['run_id'] for x in plan['runs']})
check('no_failure_or_abort_manifest',not any((R/x).exists() for x in ['terminal_failure_manifest.json','CONTROLLER_ABORT.json']))
science_files=['generator.py','evidence.json','model_spec.json','decision.md','checks.json','derivation_check.json']
preservation=[]
for k in [1,2,3]:
    p,e=f'parent_r{k}',f'extended_r{k}'; destination=f't/e{k}'; child=R/destination/'child'
    pin=sha(R/destination/'transition.json')
    transition=verify_transition(R,destination,transition_sha256=pin)
    verified=verify_preservation(R,destination,e,transition_sha256=pin)
    check(e+'.native_preservation',verified['old_cells_and_row_order_preserved'])
    for f in science_files: check(e+'.same_scientific_template:'+f,sha(child/'candidates/c0'/f)==sha(R/'author/extension'/f))
    provenance=load(R/destination/'input_provenance.json')
    check(e+'.synthetic_input_provenance',provenance['real_patient_measurements_claimed'] is False and
          all(c['origin']=='synthetic_generated' for c in provenance['columns']))
    original=next(x for x in manifest['outputs'] if x['run_id']==p)
    check(e+'.input_is_exact_parent_bytes',sha(child/'observed.csv')==original['sha256']==provenance['parent_output_sha256']==provenance['observed_input_sha256'])
    ids=all(a['subject_id']==b['subject_id'] for a,b in zip(lexical[p],lexical[e]))
    diffs={c:max(abs(a-b) for a,b in zip(tables[p][c],tables[e][c])) for c in ['x1','x2']}
    lex=all(all(a[c]==b[c] for c in ['subject_id','x1','x2']) for a,b in zip(lexical[p],lexical[e]))
    preserved={'parent_run_id':p,'extended_run_id':e,'all_old_cells_exact':ids and max(diffs.values())==0,
        'identifier_and_order_exact':ids,'numeric_columns_exact':{c:d==0 for c,d in diffs.items()},
        'maximum_absolute_difference_by_column':diffs,'maximum_absolute_numeric_difference':max(diffs.values()),
        'lexical_old_cells_exact':lex,'A1_estimates_exact':all(results[p]['analysis']['endpoints'][f]['estimate']==results[e]['analysis']['endpoints'][f]['estimate'] for f in ['A1_slope_x1','A1_intercept'])}
    compare(e+'.preservation',preserved,evaluation['preservation'][k-1]); preservation.append(preserved)

routes=load(R/'ROUTING_RESULTS.json')['requests']
check('three_routing_only_results',[(x['request_id'],x['action'],x['generated_tables']) for x in routes]==[('3','reuse',0),('4','new_population',0),('5','clarify',0)])
for item0 in routes:
    dest='routes/r'+item0['request_id']; transition=verify_transition(R,dest,transition_sha256=sha(R/dest/'transition.json'))
    check(dest+'.no_child_or_execution',transition['child_bundle'] is None and not transition['execution_permitted'] and not (R/dest/'child').exists())

summaries={}
for arm in ['parent','joint','extended']:
    group=[r['analysis']['endpoints'] for r in results.values() if r['arm']==arm]; summary={}
    for endpoint in group[0]:
        values=[g[endpoint]['estimate'] for g in group]; target=truth[endpoint]; errors=[v-target for v in values]
        summary[endpoint]={'n_available_scheduled_draws':len(values),'mean':avg(values),'between_seed_sample_sd':sd(values),
          'minimum':min(values),'maximum':max(values),'analytical_reference':target,
          'mean_signed_deviation':avg(errors),'mean_absolute_deviation':avg([abs(v) for v in errors]),
          'maximum_absolute_deviation':max(abs(v) for v in errors)}
    summaries[arm]=summary
compare('per_arm_summary',summaries,evaluation['per_arm_descriptive_summary'])
differences=[]
for k in [1,2,3]:
    j,e=results[f'joint_r{k}']['analysis']['endpoints'],results[f'extended_r{k}']['analysis']['endpoints']
    diff={x:j[x]['estimate']-e[x]['estimate'] for x in j}
    compare(f'joint_minus_extended_{k}',diff,evaluation['joint_minus_extended_by_replicate'][k-1]['joint_minus_extended'])
    differences.append({'replicate':k,'joint_minus_extended':diff})

cost={'per_execution_recorded_elapsed_seconds':elapsed,'sum_recorded_execution_seconds':math.fsum(x['elapsed_seconds'] for x in elapsed),
      'controller_start_to_final_commit_seconds':(datetime.fromisoformat(manifest['committed_utc'])-datetime.fromisoformat(started['created_utc'])).total_seconds(),
      'cpu_time':'not_measured','peak_memory':'not_measured','total_human_and_agent_effort':'not_metered',
      'monetary_cost':'not_metered','runtime_versions':runtime_versions[0] if all(x==runtime_versions[0] for x in runtime_versions) else runtime_versions}
failures=[x for x in checks if not x['pass']]+[x for x in numeric if not x['pass']]
result={'status':'pass' if not failures else 'disagreement_preserved','checked_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Independent stdlib recomputation of actual artificial outputs; native verification for integrity only',
        'structural_and_integrity_checks':len(checks),'numeric_field_comparisons':len(numeric),
        'maximum_numeric_absolute_difference':max(x['absolute_difference'] for x in numeric),
        'failure_count':len(failures),'failures':failures,'historical_anchors_checked':len(history['bindings']),
        'historical_scope':history['scope'],'n_executions':len(actual_receipts),'n_output_files':len(manifest['outputs']),
        'n_unique_output_contents':len({x['sha256'] for x in manifest['outputs']}),'n_final_three_variable_tables':6,
        'n_rows_per_output':2000,'preservation':preservation,'cost':cost,
        'bindings':{x:sha(R/x) for x in ['RUN_PLAN.json','final_output_manifest.json','reveal_authorization.json','evaluation/evaluation.json','HISTORICAL_BINDINGS.json','ROUTING_RESULTS.json']},
        'execution_receipt_bindings':receipt_bindings,'audit_script_sha256':sha(Path(__file__)),
        'scientific_generators_rerun':0,'uses_evaluator_or_generator_code_for_independent_statistics':False,
        'floating_point_verification_tolerance':'abs <= 1e-9 + 1e-11*scale; arithmetic check only, not scientific agreement margin'}
write('INDEPENDENT_RESULTS.json',{'runs':results,'per_arm_descriptive_summary':summaries,'joint_minus_extended_by_replicate':differences,'analytic_reference_from_visible_source':truth})
write('AUDIT_CHECKS.json',{'checks':checks,'numeric_comparisons':numeric})
write('POSTRUN_AUDIT.json',result)
print(json.dumps({k:result[k] for k in ['status','structural_and_integrity_checks','numeric_field_comparisons','maximum_numeric_absolute_difference','failure_count','n_executions','n_unique_output_contents']}))
print(json.dumps({'cost':cost,'summary':summaries}))
