"""New unit controller. No reference access until all scheduled runs are closed."""
from pathlib import Path
from datetime import datetime, timezone
from numbers import Real
import hashlib, importlib.util, json, math, sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness import lifecycle, execution, semantic_feedback_v1 as semantic
from cohort_harness.__main__ import validate_bundle

BUNDLE = PROJECT.parent.parent / 'evcIncE01'
CANDIDATE = 'candidates/source_increment'
SEEDS = (5301, 5302, 5303)
PROVIDER = PROJECT / 'work/main_study_freeze_2026-11-03/cases/ENSANUT2018/generated_feedback.py'
PROVIDER_HASH = '1a5a3cd6126211dc2e24f2d1c7fa58e4afdbc980e29c6fdccb6b637c7cf4e551'
REFERENCE = PROJECT / 'work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json'
REFERENCE_HASH = '1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb'
ENDPOINTS = PROJECT / 'work/core_workflow_replication_2026-11-04/ENDPOINT_CONTRACT.json'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def require(ok, msg):
    if not ok: raise ValueError(msg)
def write(p, obj):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')
def bound_inputs():
    manifest = read(ROOT/'INPUT_MANIFEST.json')
    for p,h in manifest['files'].items(): require(sha(p)==h, 'Admitted input changed')
    require(sha(ROOT/'PROTOCOL.md')==manifest['protocol_sha256'], 'Original protocol changed')
def candidate_files():
    return {p.relative_to(BUNDLE/CANDIDATE).as_posix():sha(p)
            for p in (BUNDLE/CANDIDATE).rglob('*') if p.is_file() and p.name!='freeze.json'}

def verify_commit():
    bound_inputs()
    commit=read(ROOT/'FREEZE_COMMITMENT.json')
    require(commit['seeds']==list(SEEDS) and commit['candidate']==CANDIDATE,'Schedule or candidate changed')
    for key,path in [('controller_sha256',Path(__file__)),('freeze_sha256',BUNDLE/CANDIDATE/'freeze.json'),
        ('candidate_review_sha256',ROOT/'CANDIDATE_REVIEW_GATE.json'),('protocol_sha256',ROOT/'PROTOCOL.md'),
        ('clarification_sha256',ROOT/'PROTOCOL_CLARIFICATION_01.md')]:
        require(commit[key]==sha(path),'Committed artifact changed: '+key)
    lifecycle.verify_candidate(BUNDLE,CANDIDATE)
    return commit

def verified_run(rid,seed):
    receipt=execution.verify_execution(BUNDLE,rid)
    require(receipt['candidate']==CANDIDATE and receipt['route']=='generator.py','Unexpected candidate/route')
    require(type(receipt['limits']['seed']) is int and receipt['limits']['seed']==seed,'Unexpected seed')
    require(receipt['candidate_freeze_sha256']==sha(BUNDLE/CANDIDATE/'freeze.json'),'Execution freeze mismatch')
    return receipt

def verify_closed_unit():
    commit=verify_commit();closed=read(ROOT/'CLOSURE.json')
    require(closed['scientific_authoring_closed'] is True and closed['candidate']==CANDIDATE,'Authoring open/wrong candidate')
    require(closed['freeze_commitment_sha256']==sha(ROOT/'FREEZE_COMMITMENT.json'),'Closure commitment changed')
    require(len(closed['slots'])==3 and [s['seed'] for s in closed['slots']]==list(SEEDS),'Invalid closed schedule')
    reservations=list((ROOT/'attempts').glob('*.reserved.json'))
    require(len(reservations)==closed['physical_attempts']==3,'Unexpected attempt accounting')
    for slot,seed in zip(closed['slots'],SEEDS):
        rid=f'increment_{seed}_a1';require(type(slot['seed']) is int and slot['run_id']==rid,'Invalid closed slot identity')
        result_path=ROOT/'attempts'/f'{rid}.result.json';reserve_path=ROOT/'attempts'/f'{rid}.reserved.json'
        require(sha(result_path)==slot['result_sha256'] and sha(reserve_path)==slot['reservation_sha256'],'Closed attempt artifact changed')
        result=read(result_path);reservation=read(reserve_path)
        require(result['run_id']==reservation['run_id']==rid and result['seed']==reservation['seed']==seed,'Attempt identity mismatch')
        require(reservation['candidate']==CANDIDATE and result['status']==slot['status'],'Attempt candidate/status mismatch')
        if result['status']!='controller_exception':
            receipt=verified_run(rid,seed)
            require(receipt['status']==slot['status'],'Closed receipt status changed')
            require(sha(BUNDLE/'executions'/rid/'execution.json')==result['receipt_sha256'],'Closed receipt bytes changed')
        if slot['status']=='success':
            require(sha(BUNDLE/'executions'/rid/'output/generated.csv')==slot['table_sha256']==result['table_sha256'],'Closed table changed')
    return closed,commit

def freeze():
    bound_inputs()
    gate = read(ROOT/'CANDIDATE_REVIEW_GATE.json')
    require(gate['decision']=='freeze_reviewed_candidate', 'Candidate review not approved')
    require(gate['candidate_files']==candidate_files(), 'Reviewed candidate bytes changed')
    require(gate['task_sha256']==sha(BUNDLE/'task.json') and gate['registry_sha256']==sha(BUNDLE/'registry.json'), 'Reviewed task/registry changed')
    validate_bundle(BUNDLE, BUNDLE/CANDIDATE)
    report=semantic.preflight(BUNDLE,CANDIDATE)
    write(ROOT/'SEMANTIC_PREFLIGHT.json',report)
    receipt=lifecycle.freeze_candidate(BUNDLE,CANDIDATE)
    lifecycle.verify_candidate(BUNDLE,CANDIDATE)
    write(ROOT/'FREEZE_COMMITMENT.json',{'created_utc':now(),'candidate':CANDIDATE,
        'freeze_sha256':sha(BUNDLE/CANDIDATE/'freeze.json'),'candidate_review_sha256':sha(ROOT/'CANDIDATE_REVIEW_GATE.json'),
        'protocol_sha256':sha(ROOT/'PROTOCOL.md'),'clarification_sha256':sha(ROOT/'PROTOCOL_CLARIFICATION_01.md'),
        'seeds':list(SEEDS),'n_rows':3000,'provider_sha256':sha(PROVIDER),
        'endpoint_contract_sha256':sha(ENDPOINTS),'reference_sha256_expected':REFERENCE_HASH,
        'controller_sha256':sha(Path(__file__))})
    return {'status':'frozen','route':receipt['route']}

def run(seed):
    require(type(seed) is int and seed in SEEDS,'Unscheduled seed')
    require(not (ROOT/'CLOSURE.json').exists(),'Scientific unit is closed')
    commit=verify_commit()
    log=ROOT/'attempts';log.mkdir(exist_ok=True)
    run_id=f'increment_{seed}_a1'
    write(log/f'{run_id}.reserved.json',{'run_id':run_id,'seed':seed,'candidate':CANDIDATE,'reserved_utc':now()})
    try:
        receipt=execution.run_candidate(BUNDLE,CANDIDATE,run_id,seed,runtime=execution.DEFAULT_RUNTIME,
                  timeout_seconds=30,memory_mb=1536,output_bytes=20_000_000,log_bytes=100_000)
        verified=verified_run(run_id,seed)
        result={'run_id':run_id,'seed':seed,'status':verified['status'],
                'receipt_sha256':sha(BUNDLE/'executions'/run_id/'execution.json'),
                'adapter_receipt':receipt,'completed_utc':now()}
        output=BUNDLE/'executions'/run_id/'output/generated.csv'
        if verified['status']=='success': result['table_sha256']=sha(output)
    except Exception as e:
        result={'run_id':run_id,'seed':seed,'status':'controller_exception','error_type':type(e).__name__,'error':str(e),'completed_utc':now()}
        write(log/f'{run_id}.result.json',result)
        raise
    write(log/f'{run_id}.result.json',result)
    return {k:result[k] for k in ('run_id','seed','status')}

def close():
    verify_commit()
    slots=[]
    for seed in SEEDS:
        rid=f'increment_{seed}_a1';p=ROOT/'attempts'/f'{rid}.result.json'
        require(p.is_file(),'Scheduled slot unresolved')
        slot=read(p)
        if slot['status']=='success':
            verified=verified_run(rid,seed)
            require(verified['status']=='success','Execution status changed')
            require(sha(BUNDLE/'executions'/rid/'output/generated.csv')==slot['table_sha256'],'Output changed')
        slots.append({'seed':seed,'run_id':rid,'status':slot['status'],'result_sha256':sha(p),
                      'reservation_sha256':sha(ROOT/'attempts'/f'{rid}.reserved.json'),'table_sha256':slot.get('table_sha256')})
    write(ROOT/'CLOSURE.json',{'created_utc':now(),'scientific_authoring_closed':True,
          'freeze_commitment_sha256':sha(ROOT/'FREEZE_COMMITMENT.json'),'candidate':CANDIDATE,'slots':slots,
          'physical_attempts':len(list((ROOT/'attempts').glob('*.reserved.json'))),
          'interpretation':'One scientific candidate; exposed-case development. No post-target revision.'})
    verify_closed_unit()
    return {'status':'closed','slots':len(slots)}

def finite(v): return isinstance(v,Real) and not isinstance(v,bool) and math.isfinite(v)
def missing(contract, reason):
    return {cat:[{**x,'value':None,'status':'unavailable','reason':reason} for x in contract[cat]] for cat in ('analyses','diagnostics')}
def validate_payload(payload,contract):
    for cat in ('analyses','diagnostics'):
        expected={x['id']:x['unit'] for x in contract[cat]}
        require(len(payload[cat])==len(expected) and {x['id'] for x in payload[cat]}==set(expected),'Endpoint coverage mismatch')
        for row in payload[cat]:
            require(row['unit']==expected[row['id']],'Endpoint unit changed')
            require((row['status']=='computed' and finite(row['value'])) or (row['status']=='unavailable' and row['value'] is None),'Invalid endpoint')
            if row['status']=='computed': row['value']=float(row['value'])

def evaluate():
    closed,commit=verify_closed_unit()
    require(commit['endpoint_contract_sha256']==sha(ENDPOINTS),'Endpoint contract changed')
    require(sha(PROVIDER)==PROVIDER_HASH==commit['provider_sha256'],'Provider changed')
    require(sha(REFERENCE)==REFERENCE_HASH,'Cached reference changed')
    dest=ROOT/'evaluation';dest.mkdir(exist_ok=False)
    write(dest/'STARTED.json',{'created_utc':now(),'closure_sha256':sha(ROOT/'CLOSURE.json'),'reference_sha256':REFERENCE_HASH})
    try:
        contract=read(ENDPOINTS)['cases']['ENSANUT2018']
        module_spec=importlib.util.spec_from_file_location('increment_generated_only_provider',PROVIDER)
        mod=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(mod)
        task=read(BUNDLE/'task.json');outputs=[]
        for slot in closed['slots']:
            result_path=ROOT/'attempts'/f"{slot['run_id']}.result.json"
            require(sha(result_path)==slot['result_sha256'],'Closed execution result changed')
            item=dict(slot)
            payload=missing(contract,'Execution '+slot['status'])
            if slot['status']=='success':
                receipt=verified_run(slot['run_id'],slot['seed'])
                require(receipt['status']=='success','Execution changed')
                table=BUNDLE/'executions'/slot['run_id']/'output/generated.csv'
                require(sha(table)==slot['table_sha256'],'Closed table changed')
                # No candidate revision follows these qualified source diagnostics.
                try:
                    semantic.collect_feedback(BUNDLE,CANDIDATE,slot['run_id'],slot['run_id']+'_source')
                    semantic.verify_feedback(BUNDLE,slot['run_id']+'_source',candidate=CANDIDATE,run_id=slot['run_id'])
                    item['source_feedback_path']=str(BUNDLE/'semantic_feedback_v1'/(slot['run_id']+'_source')/'feedback.json')
                except Exception as e:
                    item['source_feedback_error']={'type':type(e).__name__,'message':str(e)}
                try:
                    frame=lifecycle.read_table(table,task,output=True)
                    payload=mod.generated_statistics(frame,expected_rows=3000,expected_per_cell=375)
                    validate_payload(payload,contract)
                except Exception as e:
                    item['analysis_error']={'type':type(e).__name__,'message':str(e)}
                    payload=missing(contract,'Generated-table evaluation failed: '+type(e).__name__+': '+str(e))
            validate_payload(payload,contract)
            item.update(payload);outputs.append(item)
        # The cached exposed reference is first parsed here, after source/author closure.
        reference=read(REFERENCE)['references']['ENSANUT2018']
        for item in outputs:
            for cat in ('analyses','diagnostics'):
                for row in item[cat]:
                    ref=reference[row['id']]
                    require(ref['unit']==row['unit'],'Reference units mismatch')
                    row['reference']=ref
                    ok=finite(row['value']) and finite(ref['value'])
                    row['comparison_status']='computed' if ok else 'unavailable'
                    row['signed_difference']=float(row['value']-ref['value']) if ok else None
                    row['absolute_difference']=abs(row['signed_difference']) if ok else None
        report={'status':'completed_pending_independent_recalculation','created_utc':now(),
          'information_condition':'old admitted sources plus one reviewed supplement; explicit source-unit/transport assumptions',
          'exposed_development':True,'new_patient_rows_read':False,'target_in_generation':False,
          'scheduled_slots':3,'physical_attempts':closed['physical_attempts'],
          'successful_slots':sum(x['status']=='success' for x in closed['slots']),
          'source_feedback_entrypoint':'cohort_harness.semantic_feedback_v1',
          'closure_sha256':sha(ROOT/'CLOSURE.json'),'reference_sha256':REFERENCE_HASH,'slots':outputs}
        write(dest/'RESULTS.json',report)
        write(dest/'COMPLETED.json',{'created_utc':now(),'results_sha256':sha(dest/'RESULTS.json')})
        return {'status':report['status'],'successful_slots':report['successful_slots']}
    except Exception as e:
        write(dest/'FAILED.json',{'created_utc':now(),'type':type(e).__name__,'message':str(e)})
        raise

if __name__=='__main__':
    command=sys.argv[1]
    result=run(int(sys.argv[2])) if command=='run' else {'freeze':freeze,'close':close,'evaluate':evaluate}[command]()
    print(json.dumps(result,ensure_ascii=False))
