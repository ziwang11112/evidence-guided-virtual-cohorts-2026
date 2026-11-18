"""Bounded source-increment experiment. No target feedback or host model coefficients."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, hashlib, importlib.util, json, os, random, sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.dont_write_bytecode=True
sys.path[:0]=[str(PROJECT),str(PROJECT/'work/cross_model_api_pilot_2026-11-10'),str(PROJECT/'work/request_only_repeatability_2026-11-11')]
import provider_client as client
import tools_runtime as runtime
from cohort_harness import contracts,execution,lifecycle

client.MAX_OUTPUT=16384
client.CAPS={'openai':3.0}
CONFIG='OA_SOL'
SEEDS=[16121,16123,16127]
LIMITS={'timeout_seconds':60,'memory_mb':1536,'output_bytes':20000000,'log_bytes':50000}
REFERENCE=PROJECT/'work/cross_model_api_pilot_2026-11-10/_host_only/REFERENCE_SNAPSHOT.json'
REVIEW=PROJECT/'work/request_only_repeatability_2026-11-11/review/recompute_saved_tables.py'
PRIMARY=['residual_correlation','bmi_sbp','bmi_dbp']
ENDPOINTS=PRIMARY+['sbp.sd_population','dbp.sd_population','sbp_below_dbp_fraction']

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):client.dump_new(Path(p),x)
def check(c,m):
    if not c:raise ValueError(m)
def inventory(p):return {q.relative_to(p).as_posix():sha(q) for q in sorted(p.rglob('*')) if q.is_file()}
def load_review():
    spec=importlib.util.spec_from_file_location('pns_joint_independent_review',REVIEW)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def task():return read(ROOT/'inputs/generation_task.json')
def endpoints(result):return {e['id']:e['value'] for e in result['analyses']+result['diagnostics']}

def make_prompt(payload):
    return '''You are an independent scientific Agent constructing a useful whole biomedical cohort from published evidence. You choose the scientific structure, parameters, distributions and transport assumptions. Use the supplied evidence, not undisclosed target results or other constructors. The purpose is scientific analysis, not recovery of individual measurements. No desired numerical answer is provided. Source-population and target-population quantities can differ. Decide whether each source is usable, partial, transformed or unsuitable; do not silently equate different adjustment sets or raw/multilevel/residual correlations. You may retain your assumptions if additional evidence is insufficient. There is no prescribed distribution or correlation to select.

Return exactly one JSON object with model_spec, generator_py, decision_record. No markdown.
model_spec is your freely designed parameter object. The runner passes {"task": task_contract, "model": model_spec} as spec.
generator_py defines generate(observed, spec, seed), returning a pandas DataFrame. observed is None. n=spec["task"]["n_rows"]. Return exactly the columns in the task, in order; unique integer row_id. Use numpy, pandas and standard library only. No filesystem, network, processes, project imports, installation or execution claims. Randomness must use the supplied seed. Draw independent virtual people from your chosen law, rather than forcing realized moments through sample-wide recentering/reweighting, selecting seeds or selecting output tables. Physiological support and finite relevant moments matter; you choose and explain any bounds, transformations or rejection sampling as part of your population law. No silent post-hoc host repairs will occur. Do not multiply hypothetical evidence by the number of generated people.
decision_record requires structure (string), parameter_provenance (array), requested_estimands (array), limitations (array) and checks_actually_performed (array). For material parameters give the actual value/expression, REPORTED/DERIVED/ASSUMED status, source IDs and concise derivation or rationale. Explicitly distinguish source estimates from transported choices. requested_estimands must contain exactly the three IDs in the request, each with id, support_basis and key_unresolved_assumptions (array). If useful provide an expected value, but do not invent identification or sampling intervals. Give concise scientific explanations, not private reasoning transcripts. Explain covariance/scale choices, source suitability, tail properties and any physiological constraints. You have no execution tools in this single construction call; do not claim actual runs.

Task, requested analyses and evidence:
'''+json.dumps(payload,ensure_ascii=False,indent=2)

def source_derivation():
    # These are published source moments, not target values or generation parameters.
    r=np.array([[1,.78,.21,.12],[.78,1,.02,.16],[.21,.02,1,-.17],[.12,.16,-.17,1.]])
    a=r[:2,2:];res=r[:2,:2]-a@np.linalg.solve(r[2:,2:],a.T)
    scale=np.diag([18.22,10.98]);cov=scale@res@scale
    corr=float(res[0,1]/np.sqrt(res[0,0]*res[1,1]))
    # Independent exact covariance fixture: Cholesky coordinates projected off age/BMI.
    l=np.linalg.cholesky(r);q,_=np.linalg.qr(l[2:,:].T);e=l[:2,:]@(np.eye(4)-q@q.T)
    check(np.allclose(e@e.T,res,atol=1e-12),'Source algebra cross-check failed')
    return {'source':'BF_AGE_BMI_JOINT','order':['SBP','DBP','age','BMI'],'reported_correlation_matrix':r.tolist(),
        'minimum_eigenvalue':float(np.linalg.eigvalsh(r).min()),'residual_standardized_covariance':res.tolist(),
        'residual_covariance_mmHg2':cov.tolist(),'partial_pearson_given_age_bmi':corr,
        'independent_QR_max_difference':float(np.max(np.abs(e@e.T-res))),
        'scope':'Rounded same-source inputs; linear age and BMI only, NOT sex; neither target constraint nor uncertainty interval'}

def prepare():
    inp=ROOT/'inputs';check(not (inp/'schedule.json').exists(),'Already prepared')
    report=read(ROOT/'episodes/PNS_SEARCH/EVIDENCE_REPORT.json')
    check([s['id'] for s in report['proposed_evidence']]==['BF_AGE_BMI_JOINT','GHANA_MULTILEVEL_JOINT'],'Unexpected admission proposal')
    deriv=source_derivation();write(inp/'source_derivation_check.json',deriv)
    added={'status':'partial source constraints; target transport is not identified',
        'records':report['proposed_evidence'], 'remaining_assumptions':report['remaining_assumptions'],
        'root_audit':'Original cached tables/methods checked separately; Uganda omitted for reporting ambiguity. No target comparison used in selection.',
        'independent_source_derivation':deriv}
    write(inp/'additional_evidence.json',added)
    t=read(inp/'task.json');t['task_id']='pns_joint_evidence_followup_v1'
    t['information_policy']['allowed_tools']=[];t['budget']={'source_queries':0,'source_downloads':0,'revisions':0}
    contracts.validate_task(t);write(inp/'generation_task.json',t)
    for arm in ['ORIGINAL','AUGMENTED']:
        obj={'task':t,'requested_analyses':read(inp/'requested_analyses.json'),'existing_evidence':read(inp/'base_evidence.json'),
             'additional_joint_evidence':added if arm=='AUGMENTED' else None}
        write(inp/(arm+'.json'),obj);(inp/(arm+'.prompt.txt')).write_text(make_prompt(obj),encoding='utf-8')
    slots=[{'id':f'{a}_{i}','arm':a,'author_repetition':i} for a in ['ORIGINAL','AUGMENTED'] for i in range(1,4)]
    random.Random(16116).shuffle(slots);write(inp/'schedule.json',slots)
    (ROOT/'TARIFF.json').write_bytes((PROJECT/'work/evidence_composition_pilot_2026-11-16/TARIFF.json').read_bytes())
    print(json.dumps({'prepared':True,'source_partial_correlation':deriv['partial_pearson_given_age_bmi'],'target_read':False,'author_calls':0}))

def preflight():
    q=ROOT/'integration';q.mkdir(exist_ok=False);checks=[]
    contracts.validate_task(task());checks.append('generation task schema')
    left=read(ROOT/'inputs/ORIGINAL.json');right=read(ROOT/'inputs/AUGMENTED.json')
    check({k:v for k,v in left.items() if k!='additional_joint_evidence'}=={k:v for k,v in right.items() if k!='additional_joint_evidence'},'Arms differ beyond sources')
    checks.append('only additional source object differs')
    check(sha(ROOT/'inputs/base_evidence.json')==sha(PROJECT/'work/cross_model_api_pilot_2026-11-10/packets/PNS/evidence.json'),'Old evidence changed');checks.append('baseline packet byte-identical')
    check('REFERENCE_SNAPSHOT' not in (ROOT/'inputs/AUGMENTED.prompt.txt').read_text(),'Host reference path in prompt');checks.append('payload built only from task/source files')
    source_derivation();checks.append('source Schur complement independently verified by QR')
    # Trusted integration fixture, not biomedical model, not an experimental candidate.
    candidate=q/'candidate';candidate.mkdir()
    code='''import numpy as np\nimport pandas as pd\ndef generate(observed,spec,seed):\n r=np.random.default_rng(seed);n=spec["task"]["n_rows"];age=r.uniform(20,79,n);sex=r.integers(0,2,n);bmi=r.uniform(15,35,n);noise=r.normal(size=(n,2));return pd.DataFrame({"row_id":np.arange(n),"age":age,"female":sex,"bmi":bmi,"sbp":100+2*(bmi-25)/5+noise[:,0],"dbp":70+3*(bmi-25)/5+noise[:,0]+noise[:,1]})\n'''
    (candidate/'generator.py').write_text(code,encoding='utf-8');write(candidate/'model_spec.json',{'task':task(),'model':{}})
    result=runtime.isolated_run(candidate,task(),16119,q/'smoke',LIMITS)
    check(result['status']=='success','Isolated fixture failed: '+str(result.get('error')));checks.append('curated sandbox + unchanged analyzer')
    execution_receipt=read(q/'smoke/execution.json');probe=execution_receipt['worker_report']['pre_import_probe']
    check(not probe['mnt_visible'] and not probe['home_visible'] and not probe['route_table'],'Sandbox leak');checks.append('host drives/home and network absent')
    independent=load_review();data,_=independent.load_table(q/'smoke/output/generated.csv',task());calc=independent.independent_statistics(data,'PNS')
    normal=endpoints(result['statistics']);check(set(normal)==set(ENDPOINTS),'Endpoint inventory mismatch')
    for k,v in calc['values'].items():check(np.isclose(v,normal[k],atol=1e-9,rtol=1e-10),'Estimator mismatch '+k)
    checks.append('six scientific/diagnostic endpoints independently recomputed')
    # Behavioral difference when paired dependence changes: analysts must not return a configured constant.
    altered={k:v.copy() for k,v in data.items()};altered['dbp']=np.random.default_rng(1).permutation(altered['dbp'])
    other=independent.independent_statistics(altered,'PNS')['values']['residual_correlation']
    check(abs(other-calc['values']['residual_correlation'])>.3,'Residual analyzer does not react to changed pairing');checks.append('paired-relationship perturbation changes analysis')
    bad=json.dumps({'model_spec':{},'generator_py':'def generate(x): pass','decision_record':{}})
    try:client.parse_artifact(bad)
    except ValueError:checks.append('malformed constructor interface rejected')
    else:raise ValueError('Malformed artifact accepted')
    write(ROOT/'PREFLIGHT.json',{'passed':True,'checks':checks,'target_reference_read':False,'paid_calls':0,'fixture_is_artificial':True})
    print(json.dumps({'preflight_passed':True,'checks':len(checks)}))

def dependencies():
    rels=['cohort_harness/_worker.py','cohort_harness/contracts.py','cohort_harness/execution.py','cohort_harness/lifecycle.py',
        'work/cross_model_api_pilot_2026-11-10/provider_client.py','work/cross_model_api_pilot_2026-11-10/provider_preflight.py',
        'work/cross_model_api_pilot_2026-11-10/execute_pilot.py','work/cross_model_api_pilot_2026-11-10/analyze_pilot.py',
        'work/next_case_validation_2026-11-09/runtime/analysis_tools.py','work/request_only_repeatability_2026-11-11/tools_runtime.py',
        'work/request_only_repeatability_2026-11-11/review/recompute_saved_tables.py']
    paths=[PROJECT/r for r in rels]+[Path(__file__),ROOT/'PROTOCOL.md',ROOT/'SOURCE_AUDIT.md',ROOT/'ADMISSION_PLAN.md',ROOT/'PREFLIGHT.json',ROOT/'TARIFF.json',ROOT/'RUNTIME.json',ROOT/'SEARCH_FREEZE.json',ROOT/'episodes/PNS_SEARCH/EVIDENCE_REPORT.json',ROOT/'episodes/PNS_SEARCH/OUTCOME.json']
    paths+=list((ROOT/'inputs').glob('*'))
    # Bind the complete archived source-search trajectory, not just selected positive papers.
    paths+=list((ROOT/'episodes/PNS_SEARCH/tool_actions').rglob('result.json'))
    return {p.relative_to(PROJECT).as_posix():sha(p) for p in paths}

def freeze():
    check(read(ROOT/'PREFLIGHT.json')['passed'],'Integration checks required')
    reserves=[]
    for row in read(ROOT/'inputs/schedule.json'):
        prompt=(ROOT/'inputs'/(row['arm']+'.prompt.txt')).read_text(encoding='utf-8')
        check(prompt==make_prompt(read(ROOT/'inputs'/(row['arm']+'.json'))),'Prompt construction changed')
        body=client.make_request(CONFIG,prompt)[1];b=len(json.dumps(body,ensure_ascii=False).encode())
        check(b<190000,'Request too large')
        reserves.append(((b+4096)*2.5+client.MAX_OUTPUT*10.)/1000000)
    check(sum(reserves)<client.CAPS['openai'],'Schedule exceeds conservative cap')
    write(ROOT/'RUNTIME.json',execution._runtime_manifest(execution._runtime(None)))
    write(ROOT/'GENERATION_FREEZE.json',{'frozen_utc':client.utc(),'files':dependencies(),'reference_sha256':sha(REFERENCE),
        'model_config':client.CONFIGS[CONFIG],'system':client.SYSTEM,'max_output_tokens':client.MAX_OUTPUT,'cap_usd':client.CAPS['openai'],
        'schedule':read(ROOT/'inputs/schedule.json'),'seeds':SEEDS,'limits':LIMITS,'max_calls':6,'max_tables':18,
        'conservative_schedule_reservation_usd':sum(reserves),'primary':PRIMARY,'diagnostics':ENDPOINTS[3:],
        'reference_scope':'Already exposed developmental reference; no new clinical validation','source_replay':'No target rows masquerading as source population'})
    print(json.dumps({'frozen':True,'sha256':sha(ROOT/'GENERATION_FREEZE.json'),'reserved_schedule_usd':sum(reserves)}))

def verify():
    f=read(ROOT/'GENERATION_FREEZE.json')
    for p,h in f['files'].items():check(sha(PROJECT/p)==h,'Frozen file changed: '+p)
    check(sha(REFERENCE)==f['reference_sha256'],'Reference changed')
    check(f['model_config']==client.CONFIGS[CONFIG] and f['system']==client.SYSTEM and f['max_output_tokens']==client.MAX_OUTPUT and f['cap_usd']==client.CAPS['openai'],'API configuration changed')
    check(f['seeds']==SEEDS and f['limits']==LIMITS,'Execution configuration changed')
    return f

def construct(row):
    verify();cid=row['id'];dest=ROOT/'candidates'/cid;call=ROOT/'calls'/cid
    if call.exists():
        check((call/'receipt.json').exists(),'Unresolved call; no automatic retry')
        receipt=read(call/'receipt.json');obj=read(call/'artifact.json') if (call/'artifact.json').exists() else None
    else:receipt,obj=client.call_once(ROOT,cid,CONFIG,(ROOT/'inputs'/(row['arm']+'.prompt.txt')).read_text(encoding='utf-8'))
    result={**row,'status':'failed','call_receipt_sha256':sha(call/'receipt.json'),'tariff_cost_usd':receipt.get('tariff_cost_usd')}
    try:
        check(receipt['status']=='received' and obj is not None,'API incomplete or invalid artifact')
        check(receipt['returned_model']==client.CONFIGS[CONFIG]['model'],'Unexpected returned model')
        entries=obj['decision_record']['requested_estimands']
        check(len(entries)==3 and {v.get('id') for v in entries}==set(PRIMARY),'Wrong requested estimands')
        for v in entries:check('support_basis' in v and isinstance(v.get('key_unresolved_assumptions'),list),'Missing estimand provenance')
        if not dest.exists():
            dest.mkdir(parents=True);(dest/'generator.py').write_text(obj['generator_py'],encoding='utf-8')
            write(dest/'model_spec.json',{'task':task(),'model':obj['model_spec']});write(dest/'decision_record.json',obj['decision_record'])
            lifecycle.validate_program(dest/'generator.py')
            write(dest/'SEAL.json',{'sealed_utc':client.utc(),'files':inventory(dest),'api_receipt_sha256':sha(call/'receipt.json')})
        for n,h in read(dest/'SEAL.json')['files'].items():check(sha(dest/n)==h,'Candidate changed')
        result.update(status='sealed',seal_sha256=sha(dest/'SEAL.json'))
    except Exception as e:result['error']=str(e)[:1500]
    print(json.dumps({'id':cid,'status':result['status'],'cost':result['tariff_cost_usd']}),flush=True);return result

def run():
    f=verify();lock=ROOT/'RUNNING.lock'
    with lock.open('x') as fp:json.dump({'pid':os.getpid(),'started_utc':client.utc()},fp)
    try:
        check(execution._runtime_manifest(execution._runtime(None))==read(ROOT/'RUNTIME.json'),'Runtime changed')
        if not (ROOT/'CONSTRUCTION_CLOSURE.json').exists():
            with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(construct,f['schedule']))
            write(ROOT/'CONSTRUCTION_CLOSURE.json',{'closed_utc':client.utc(),'freeze_sha256':sha(ROOT/'GENERATION_FREEZE.json'),'rows':rows})
        closure=read(ROOT/'CONSTRUCTION_CLOSURE.json');check(closure['freeze_sha256']==sha(ROOT/'GENERATION_FREEZE.json'),'Closure mismatch')
        outputs=[]
        for row in closure['rows']:
            if row['status']!='sealed':continue
            candidate=ROOT/'candidates'/row['id'];check(sha(candidate/'SEAL.json')==row['seal_sha256'],'Candidate seal changed')
            for n,h in read(candidate/'SEAL.json')['files'].items():check(sha(candidate/n)==h,'Frozen candidate changed')
            for seed in SEEDS:
                folder=ROOT/'executions'/row['id']/str(seed)
                if folder.exists():check((folder/'execution.json').exists(),'Incomplete local execution; inspect before resuming')
                else:runtime.isolated_run(candidate,task(),seed,folder,LIMITS)
                r=read(folder/'execution.json')
                if r['status']=='success':
                    probe=r['worker_report']['pre_import_probe'];check(not probe['mnt_visible'] and not probe['home_visible'] and not probe['route_table'],'Isolation failed')
                outputs.append({'id':row['id'],'seed':seed,'status':r['status'],'receipt_sha256':sha(folder/'execution.json')})
            print(json.dumps({'executed':row['id'],'seeds':3}),flush=True)
        verify()
        if not (ROOT/'EXECUTION_CLOSURE.json').exists():write(ROOT/'EXECUTION_CLOSURE.json',{'closed_utc':client.utc(),'construction_sha256':sha(ROOT/'CONSTRUCTION_CLOSURE.json'),'rows':outputs})
        print(json.dumps({'closed':True,'outputs':len(outputs),'success':sum(x['status']=='success' for x in outputs),'accounted_usd':client.ledger_accounted(ROOT,'openai')}),flush=True)
    finally:lock.unlink()

def analyze():
    verify();cc=read(ROOT/'CONSTRUCTION_CLOSURE.json');ec=read(ROOT/'EXECUTION_CLOSURE.json')
    check(cc['freeze_sha256']==sha(ROOT/'GENERATION_FREEZE.json') and ec['construction_sha256']==sha(ROOT/'CONSTRUCTION_CLOSURE.json'),'Closure changed')
    authors={r['id']:r for r in cc['rows']};independent=load_review();records=[];details=[];failures=[];max_difference=0.;comparisons=0
    for a in cc['rows']:
        if a['status']!='sealed':failures.append({'id':a['id'],'stage':'construction','error':a.get('error')})
    for out in ec['rows']:
        folder=ROOT/'executions'/out['id']/str(out['seed']);check(sha(folder/'execution.json')==out['receipt_sha256'],'Receipt changed');r=read(folder/'execution.json')
        if r['status']!='success':failures.append({**out,'stage':'execution','error':r.get('error')});continue
        for n,h in read(folder/'input_bindings.json').items():check(sha(folder/'input'/n)==h,'Staged input changed')
        csv=folder/'output/generated.csv';check(sha(csv)==r['generated_sha256'],'Generated rows changed')
        data,_=independent.load_table(csv,task());recalc=independent.independent_statistics(data,'PNS');values=endpoints(r['statistics'])
        check(set(values)==set(ENDPOINTS),'Endpoint mismatch')
        for k,v in values.items():
            w=recalc['values'][k]
            if v is None or w is None:check(v is None and w is None,'Null mismatch')
            else:
                delta=abs(v-w);max_difference=max(max_difference,delta);check(np.isclose(v,w,atol=1e-9,rtol=1e-10),'Independent recomputation differs')
            comparisons+=1;records.append({'id':out['id'],'arm':authors[out['id']]['arm'],'seed':out['seed'],'estimand':k,'value':v})
        physical={k:int((data[k]<=0).sum()) for k in ['bmi','sbp','dbp']}
        details.append({**out,'statistics':r['statistics'],'nonpositive_counts':physical,'generated_sha256':sha(csv)})
    # Only now parse the already exposed aggregate reference; no patient rows are read.
    refs=read(REFERENCE)['references']['PNS'];summary=[];arm_summary=[]
    for row in records:
        ref=refs[row['estimand']]['value'];row['reference']=ref
        row['absolute_reference_difference']=abs(row['value']-ref) if row['value'] is not None and ref is not None else None
    for a in cc['rows']:
        for endpoint in ENDPOINTS:
            selected=[r for r in records if r['id']==a['id'] and r['estimand']==endpoint and r['value'] is not None]
            vals=[r['value'] for r in selected];errors=[r['absolute_reference_difference'] for r in selected]
            summary.append({'id':a['id'],'arm':a['arm'],'estimand':endpoint,'available_seeds':len(vals),
                'seed_mean':float(np.mean(vals)) if vals else None,'seed_min':min(vals) if vals else None,'seed_max':max(vals) if vals else None,
                'mean_absolute_reference_difference':float(np.mean(errors)) if vals else None})
    for arm in ['ORIGINAL','AUGMENTED']:
        for endpoint in ENDPOINTS:
            ss=[r for r in summary if r['arm']==arm and r['estimand']==endpoint and r['available_seeds']]
            arm_summary.append({'arm':arm,'estimand':endpoint,'available_authors':len(ss),
                'author_mean':float(np.mean([r['seed_mean'] for r in ss])) if ss else None,
                'author_mean_absolute_reference_difference':float(np.mean([r['mean_absolute_reference_difference'] for r in ss])) if ss else None})
    dest=ROOT/'analysis';dest.mkdir(exist_ok=False)
    for name,obj in [('seed_results',records),('author_results',summary),('arm_results',arm_summary),('details',details),('failures',failures)]:
        write(dest/(name+'.json'),obj)
        if obj and name not in ['details','failures']:pd.DataFrame(obj).to_csv(dest/(name+'.csv'),index=False)
    write(dest/'REFERENCE_USED.json',{'reference_sha256':sha(REFERENCE),'reference_scope':'Exposed sample estimates, not known population truth','PNS':refs})
    write(dest/'INDEPENDENT_RECOMPUTATION.json',{'passed':True,'endpoint_comparisons':comparisons,'maximum_absolute_difference':max_difference,
        'method':'Existing independently written QR versus unchanged production weighted/SVD analysis','no_extra_generator_runs':True})
    receipts=[read(p) for p in (ROOT/'calls').glob('*/receipt.json')];search=read(ROOT/'episodes/PNS_SEARCH/OUTCOME.json')
    write(dest/'COSTS.json',{'author_calls':len(receipts),'author_tariff_usd':sum(r.get('tariff_cost_usd') or 0 for r in receipts),
        'search_calls':search['calls'],'search_tariff_usd':search['accounted_usd'],
        'total_known_tariff_usd':sum(r.get('tariff_cost_usd') or 0 for r in receipts)+search['accounted_usd'],
        'unknown_author_reservations_usd':sum(r['reserved_usd'] for r in receipts if r.get('tariff_cost_usd') is None),
        'requested_models':sorted({r['requested_model'] for r in receipts}),'returned_models':sorted({str(r.get('returned_model')) for r in receipts}),
        'author_usage':{k:sum((r.get('usage') or {}).get(k) or 0 for r in receipts) for k in ['input','output','cached','reasoning']},
        'invoice':False,'tariff':'TARIFF.json; inherited historical receipt tariff_date is not a new verification date'})
    print(json.dumps({'analysis_complete':True,'tables':len(details),'failures':len(failures),'independent_max_difference':max_difference,'arms':arm_summary}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','preflight','freeze','run','analyze']);args=parser.parse_args();globals()[args.action]()
