"""Frozen 24-construction controlled study, existing API client and isolated worker.

No automatic API retries, no hidden statistical feedback, no local code fallback.
Only this file orchestrates calls; analyze is deliberately a separate postclosure action.
"""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import argparse, hashlib, json, os, shutil, sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path[:0]=[str(PROJECT),str(PROJECT/'work/cross_model_api_pilot_2026-11-10')]
sys.dont_write_bytecode=True
import provider_client as client
from cohort_harness import contracts, execution, lifecycle
from analyzer import VARIABLES,ESTIMANDS,evaluate,source_checks,label_checks,REFERENCE,identified

PREP=PROJECT/'work/source_role_audit_2026-11-15/composition_probe'
WORKER=PROJECT/'cohort_harness/_worker.py'
SEEDS=[16101,16103,16109]
LIMITS=dict(timeout_seconds=60,memory_mb=1536,output_bytes=20_000_000,log_bytes=50_000)
N=3000
client.MAX_OUTPUT=16384
client.CAPS={'openai':6.0}
CONFIG='OA_SOL'

def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): client.dump_new(Path(p),x)
def require(c,m):
    if not c: raise ValueError(m)
def inv(folder): return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}

def task(family):
    columns=[{'name':'person_id','kind':'integer','unit':'','role':'identifier','nullable':False}]
    columns += [{'name':v,'kind':'number','unit':'standardized arbitrary units','role':'generated','nullable':False} for v in VARIABLES[family]]
    t={'schema_version':1,'task_id':'composition_'+family,'mode':'whole_cohort',
       'population':'Hypothetical population stipulated by the supplied mathematical records; not a clinical cohort',
       'row_id':'person_id','n_rows':N,'columns':columns,
       'information_policy':{'mode':'published_evidence','excluded_cohorts':[], 'allowed_tools':[]},
       'budget':{'source_queries':0,'source_downloads':0,'revisions':0}}
    # Legacy harness mode name is a serialization label, not a claim that artificial records are publications.
    contracts.validate_task(t); return t

def prompt(payload,family):
    return '''You are independently constructing a data generator for a controlled mathematical evidence-composition exercise. All supplied records are artificial, exact population constraints, not real clinical studies. Use only the supplied records. You choose the scientific model and any missing relationships. No reference target table or other authors are provided. Your goal is usable data for the requested analyses and honest identification/assumption labels.

Return a SINGLE JSON object with exactly model_spec, generator_py, decision_record. No markdown.
model_spec: an object of your freely chosen model parameters. The runner will pass {"task": task_contract, "model": model_spec} to generate.
generator_py: Python source defining exactly generate(observed, spec, seed), returning a pandas DataFrame. observed is None; n=spec["task"]["n_rows"]. Use numpy/pandas/standard library only. No filesystem reads/writes, processes, network, imports of project code, or installation. Use seed for randomness. Each row is a different independent person. Longitudinal tables are WIDE: one row/person containing both visits. Return EXACT columns in the task contract, in order, unique integer person_id. Negative values are legitimate standardized measurements. Generate random samples; do not rescale/correlate the realized sample to exactly force finite-sample moments, choose favorable seeds, sort or reject persons to improve scores. Parameters/model may be mathematically derived from evidence; no specific distribution is mandated. All quantities/analyses are Pearson and OLS as specified, never rank replacements.
decision_record: object with structure (short description), parameter_provenance (array of parameter/value, kind REPORTED/DERIVED/ASSUMED, record ids and concise basis), requested_estimands (array of EXACT three name keys below; each includes status identified/scenario/undetermined, value numeric or null, basis concise explanation), limitations (array), checks_actually_performed (array; do not claim execution that you have not performed). 'identified' means logically determined by supplied records and stipulated task assumptions, independently of additional distributional assumptions. A chosen point value for a relationship not so determined is 'scenario'. If you cannot supply a value use 'undetermined'. A non-Gaussian shape assumption does not by itself make an otherwise identified second-moment functional unidentified. Brief derivations are welcome; no private reasoning transcript needed.

Task and records:
'''+json.dumps(payload,ensure_ascii=False,indent=2)+'\nTask contract:\n'+json.dumps(task(family),indent=2)+'\nRequired estimand names, in primary/secondary order:\n'+json.dumps(ESTIMANDS[family])

def validate_artifact(obj,family):
    rows=obj['decision_record']['requested_estimands']
    require(len(rows)==3 and {x.get('name') for x in rows}==set(ESTIMANDS[family]),'Exactly three named estimands required')
    for r in rows:
        require(r.get('status') in ('identified','scenario','undetermined'),'Invalid estimand status')
        require(isinstance(r.get('basis'),str),'Estimand basis required')
        require(r.get('value') is None or (isinstance(r['value'],(int,float)) and not isinstance(r['value'],bool)),'Value must be numeric or null')

def files_to_bind():
    paths=[ROOT/'pilot.py',ROOT/'analyzer.py',ROOT/'verify_analysis.py',ROOT/'test_integration.py',ROOT/'PROTOCOL.md',
           ROOT/'PREFLIGHT.json',ROOT/'TARIFF.json',ROOT/'RUNTIME.json',PREP/'PLAN.json',
           WORKER,PROJECT/'cohort_harness/execution.py',PROJECT/'cohort_harness/contracts.py',PROJECT/'cohort_harness/lifecycle.py',
           PROJECT/'work/cross_model_api_pilot_2026-11-10/provider_client.py',PROJECT/'work/cross_model_api_pilot_2026-11-10/provider_preflight.py']
    paths += list((ROOT/'inputs').glob('*'))
    return {str(p.relative_to(PROJECT)).replace('\\','/'):sha(p) for p in paths}

def verify_freeze():
    f=read(ROOT/'FREEZE.json')
    for rel,h in f['files'].items(): require(sha(PROJECT/rel)==h,'Frozen file changed: '+rel)
    require(f['model_config']==client.CONFIGS[CONFIG] and f['max_output_tokens']==client.MAX_OUTPUT,'API configuration changed')
    require(f['seeds']==SEEDS and f['limits']==LIMITS,'Execution configuration changed')
    return f

def prepare():
    require(not (ROOT/'FREEZE.json').exists(),'Already frozen')
    plan=read(PREP/'PLAN.json'); require(len(plan['slots'])==24,'Expected 24 preordered slots')
    (ROOT/'inputs').mkdir(exist_ok=False)
    for row in plan['slots']:
        src=PREP/row['payload'];require(sha(src)==row['sha256'],'Prepared payload changed')
        (ROOT/'inputs'/row['payload']).write_bytes(src.read_bytes())
        (ROOT/'inputs'/(src.stem+'.prompt.txt')).write_text(prompt(read(src),row['family']),encoding='utf-8')
    for f in VARIABLES: write(ROOT/'inputs'/('task_'+f+'.json'),task(f))
    print(json.dumps({'prepared_inputs':24,'generation_calls':0}))

def isolated(candidate,t,run,seed):
    run.mkdir(parents=True,exist_ok=False)
    stage,out=run/'input',run/'output';stage.mkdir();out.mkdir()
    receipt={'created_utc':now(),'seed':seed,'status':'failed','generator_executed':False,
             'isolation':'existing WSL/bubblewrap, no network, curated read-only mounts','no_local_fallback':True}
    copies={'generator.py':candidate/'generator.py','model_spec.json':candidate/'model_spec.json','worker.py':WORKER}
    for name,src in copies.items(): (stage/name).write_bytes(src.read_bytes())
    write(stage/'task.json',t);write(stage/'request.json',execution._limits(**LIMITS,seed=seed))
    binding=inv(stage);write(run/'input_bindings.json',binding)
    runtime=execution._runtime(None)
    for name in ('generated.csv','worker_report.json'): (out/name).touch(exist_ok=False)
    command=execution._command(runtime,run,LIMITS['timeout_seconds'])
    write(run/'launch.json',{'command':command,'runtime':runtime,'worker_sha256':binding['worker.py'],'expected_mounts':sorted(binding)})
    try:
        receipt['process']=execution._capture(command,run,LIMITS['timeout_seconds']+20,LIMITS['log_bytes'],run/'stdout.log',run/'stderr.log')
        require((out/'worker_report.json').stat().st_size<=65536,'Oversize worker report')
        wr=read(out/'worker_report.json') if (out/'worker_report.json').stat().st_size else {}
        receipt['generator_executed']=wr.get('generator_started')
        require(receipt['process']['returncode']==0 and wr.get('status')=='completed','Isolated worker did not complete')
        require(wr['pre_import_probe']['mnt_visible'] is False and wr['pre_import_probe']['home_visible'] is False and not wr['pre_import_probe']['route_table'],'Isolation visibility check failed')
        execution._csv_guard(out/'generated.csv',t,LIMITS['output_bytes'])
        contracts.validate_output(None,lifecycle.read_table(out/'generated.csv',t,output=True),t)
        receipt.update(status='success',generated_sha256=sha(out/'generated.csv'))
    except Exception as e:
        receipt['error']={'type':type(e).__name__,'message':str(e)[:1500]}
    require(inv(stage)==binding,'Read-only staged inputs changed')
    require(set(inv(out))<={'generated.csv','worker_report.json'},'Unexpected outputs')
    receipt.update(completed_utc=now(),files=inv(run));write(run/'execution.json',receipt)
    return receipt

def freeze():
    pre=read(ROOT/'PREFLIGHT.json');require(pre['all_passed'] is True,'Preflight must pass')
    plan=read(PREP/'PLAN.json')
    reserves=[]
    for row in plan['slots']:
        payload=ROOT/'inputs'/row['payload'];text=(ROOT/'inputs'/(payload.stem+'.prompt.txt')).read_text(encoding='utf-8')
        require(sha(payload)==row['sha256'] and text==prompt(read(payload),row['family']),'Frozen input/prompt construction changed')
        body=client.make_request(CONFIG,text)[1];encoded=json.dumps(body,ensure_ascii=False).encode('utf-8')
        require(len(encoded)<190_000,'Request above byte ceiling')
        c=client.CONFIGS[CONFIG]
        reserves.append(((len(encoded)+4096)*max(c['input_rate'],c['cache_write_rate'])+client.MAX_OUTPUT*c['output_rate'])/1e6)
    require(sum(reserves)<=client.CAPS['openai'],'Worst-case full schedule exceeds study cap')
    runtime=execution._runtime_manifest(execution._runtime(None));write(ROOT/'RUNTIME.json',runtime)
    bound=files_to_bind()
    write(ROOT/'FREEZE.json',{'kind':'composition_pilot_v1','frozen_utc':now(),'slots':plan['slots'],'files':bound,
        'model_config':client.CONFIGS[CONFIG],'max_output_tokens':client.MAX_OUTPUT,'provider_budget_usd':6.0,
        'full_schedule_conservative_reservation_usd':sum(reserves),
        'max_api_calls':24,'api_concurrency':3,'scientific_revisions':0,'mechanical_repair_calls':0,
        'seeds':SEEDS,'n_rows_per_table':N,'max_final_tables':72,'limits':LIMITS,
        'identification_scope':'artificial exact-moment controlled task; no clinical validation',
        'api_retry_policy':'none; every dispatch consumes slot, failures retained; fresh standalone input',
        'analysis_rule':'all constructions sealed before generation; all generation closed before analysis; no result feedback',
        'tolerances':'descriptive Monte Carlo diagnostics, not biological equivalence thresholds',
        'tariff_source':'https://developers.openai.com/api/docs/models/gpt-6.1-sol'})
    print(json.dumps({'frozen':True,'sha256':sha(ROOT/'FREEZE.json'),'calls':24,'budget_usd':6}))

def construct(row):
    verify_freeze();cid=Path(row['payload']).stem; dest=ROOT/'candidates'/cid
    call=ROOT/'calls'/cid
    if call.exists():
        require((call/'receipt.json').exists(),'In-flight/unknown call must be resolved without automatic retry')
        receipt=read(call/'receipt.json');obj=read(call/'artifact.json') if (call/'artifact.json').exists() else None
    else:
        receipt,obj=client.call_once(ROOT,cid,CONFIG,(ROOT/'inputs'/(cid+'.prompt.txt')).read_text(encoding='utf-8'))
    result={'id':cid,**row,'status':'failed','call_receipt_sha256':sha(call/'receipt.json'),'tariff_cost_usd':receipt.get('tariff_cost_usd')}
    try:
        require(receipt['status']=='received' and obj is not None,'API incomplete or invalid artifact')
        require(receipt['returned_model']==client.CONFIGS[CONFIG]['model'],'Unexpected returned model; no silent substitution')
        validate_artifact(obj,row['family'])
        if not dest.exists():
            dest.mkdir(parents=True)
            (dest/'generator.py').write_text(obj['generator_py'],encoding='utf-8')
            write(dest/'model_spec.json',{'task':task(row['family']),'model':obj['model_spec']})
            write(dest/'decision_record.json',obj['decision_record'])
            write(dest/'SEAL.json',{'sealed_utc':now(),'files':inv(dest),'call_receipt_sha256':sha(call/'receipt.json')})
        seal=read(dest/'SEAL.json')
        for n,h in seal['files'].items(): require(sha(dest/n)==h,'Candidate mutated')
        result.update(status='sealed',candidate_seal_sha256=sha(dest/'SEAL.json'))
    except Exception as e: result['error']=str(e)[:1500]
    print(json.dumps({'constructor':cid,'status':result['status'],'cost_usd':result['tariff_cost_usd']}),flush=True)
    return result

def run():
    f=verify_freeze(); lock=ROOT/'RUNNING.lock'
    with lock.open('x',encoding='utf-8') as s: json.dump({'pid':os.getpid(),'started_utc':now()},s)
    try:
        # Probe failure precedes dispatch, so infrastructure does not waste a paid experiment.
        require(execution._runtime_manifest(execution._runtime(None))==read(ROOT/'RUNTIME.json'),'Frozen runtime changed')
        if not (ROOT/'CONSTRUCTION_CLOSURE.json').exists():
            with ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(construct,f['slots']))
            write(ROOT/'CONSTRUCTION_CLOSURE.json',{'closed_utc':now(),'freeze_sha256':sha(ROOT/'FREEZE.json'),'rows':rows})
        closed=read(ROOT/'CONSTRUCTION_CLOSURE.json')
        require(closed['freeze_sha256']==sha(ROOT/'FREEZE.json'),'Closure freeze mismatch')
        results=[]
        for row in closed['rows']:
            if row['status']!='sealed': continue
            dest=ROOT/'candidates'/row['id'];require(sha(dest/'SEAL.json')==row['candidate_seal_sha256'],'Candidate seal changed')
            for name,h in read(dest/'SEAL.json')['files'].items(): require(sha(dest/name)==h,'Candidate changed')
            for seed in SEEDS:
                folder=ROOT/'executions'/row['id']/str(seed)
                if folder.exists():
                    require((folder/'execution.json').exists(),'Incomplete execution: inspect, do not replace')
                    r=read(folder/'execution.json')
                else: r=isolated(dest,task(row['family']),folder,seed)
                results.append({'id':row['id'],'seed':seed,'status':r['status'],'receipt_sha256':sha(folder/'execution.json')})
            print(json.dumps({'executed':row['id'],'seeds':3}),flush=True)
        verify_freeze()
        if not (ROOT/'EXECUTION_CLOSURE.json').exists():
            write(ROOT/'EXECUTION_CLOSURE.json',{'closed_utc':now(),'construction_closure_sha256':sha(ROOT/'CONSTRUCTION_CLOSURE.json'),'rows':results})
        print(json.dumps({'closed':True,'constructions':len(closed['rows']),'successful_tables':sum(r['status']=='success' for r in results),'accounted_usd':client.ledger_accounted(ROOT,'openai')}),flush=True)
    finally: lock.unlink()

def analyze():
    verify_freeze(); ec=read(ROOT/'EXECUTION_CLOSURE.json');cc=read(ROOT/'CONSTRUCTION_CLOSURE.json')
    require(ec['construction_closure_sha256']==sha(ROOT/'CONSTRUCTION_CLOSURE.json'),'Construction closure changed')
    rows={r['id']:r for r in cc['rows']}; analyses=[];checks=[];labels=[];failures=[]; details=[]
    for row in cc['rows']:
        if row['status']=='sealed':
            for r in label_checks(read(ROOT/'candidates'/row['id']/'decision_record.json'),row['family'],row['condition']): labels.append({'id':row['id'],'family':row['family'],'condition':row['condition'],**r})
        else: failures.append({'id':row['id'],'stage':'construction','error':row.get('error')})
    for er in ec['rows']:
        row=rows[er['id']];folder=ROOT/'executions'/er['id']/str(er['seed'])
        require(sha(folder/'execution.json')==er['receipt_sha256'],'Execution receipt changed')
        receipt=read(folder/'execution.json')
        for name,h in receipt['files'].items():require(sha(folder/name)==h,'Execution artifact changed')
        if receipt['status']!='success': failures.append({'id':row['id'],'seed':er['seed'],'stage':'execution','error':receipt.get('error')});continue
        csv=folder/'output/generated.csv';require(sha(csv)==receipt['generated_sha256'],'Generated table changed')
        try:
            frame=lifecycle.read_table(csv,task(row['family']),output=True);result=evaluate(frame,row['family'])
            meta={k:row[k] for k in ('id','family','condition','author_repetition')};meta['seed']=er['seed']
            details.append({**meta,**result})
            for name,value in result['analyses'].items():
                known=identified(row['family'],row['condition'],name)
                ref=REFERENCE[row['family']][name]
                analyses.append({**meta,'estimand':name,'value':value,'identified':known,'reference':ref,
                    'absolute_error_to_full_information_world':abs(value-ref),'identified_within_0_08':bool(abs(value-ref)<=.08) if known else None,
                    'error_interpretation':'identified functional' if known else 'scenario separation only; not an error score'})
            for check in source_checks(result,row['family'],row['condition']): checks.append({**meta,**check})
        except Exception as e:failures.append({'id':row['id'],'seed':er['seed'],'stage':'analysis','error':str(e)})
    import pandas as pd
    out=ROOT/'analysis';out.mkdir(exist_ok=False)
    for name,value in [('analyses',analyses),('source_checks',checks),('identification_labels',labels),('failures',failures),('details',details)]:
        write(out/(name+'.json'),value)
        if value and name!='details':pd.DataFrame(value).to_csv(out/(name+'.csv'),index=False)
    receipts=[read(p) for p in sorted((ROOT/'calls').glob('*/receipt.json'))]
    write(out/'COSTS.json',{'api_calls':len(receipts),'requested_models':sorted({r['requested_model'] for r in receipts}),
        'returned_models':sorted({str(r.get('returned_model')) for r in receipts}),
        'known_tariff_usd':sum(r.get('tariff_cost_usd') or 0 for r in receipts),
        'unknown_call_reservations_usd':sum(r['reserved_usd'] for r in receipts if r.get('tariff_cost_usd') is None),
        'usage':{k:sum((r.get('usage') or {}).get(k) or 0 for r in receipts) for k in ['input','output','cached','reasoning']},
        'not_invoice':True,'tariff_verification':'TARIFF.json overrides inherited receipt tariff_date; same numeric rates'})
    print(json.dumps({'analysis_rows':len(analyses),'source_checks':len(checks),'labels':len(labels),'failures':len(failures)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','freeze','run','analyze']);args=parser.parse_args()
    globals()[args.action]()
