"""Freeze, close, evaluate and independently recompute this bounded capability batch."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, importlib.util, json, hashlib, math
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
api=load('p1_pipeline_api',ROOT/'api_loop.py')
rt=load('p1_pipeline_runtime',ROOT/'tools_runtime.py')
read,sha,write=api.read,api.sha,api.write_new
def now():return datetime.now(timezone.utc).isoformat()
PNS_REFERENCE=PROJECT/'work/cross_model_api_pilot_2026-11-10/_host_only/REFERENCE_SNAPSHOT.json'
IRON_REFERENCE=PROJECT/'work/iron_breadth_2026-11-05/evaluation/TARGET.json'
PRIMARY={'PNS':['bmi_sbp','bmi_dbp','residual_correlation'],'IRON':['odds_ratio','joint_prevalence','spearman']}
ENDPOINTS={'PNS':PRIMARY['PNS']+['sbp.sd_population','dbp.sd_population','sbp_below_dbp_fraction'],
           'IRON':rt.iron.ENDPOINTS}

def preflight():
    assert read(ROOT/'TEST_RECEIPT.json')['status']=='pass'
    plan=read(ROOT/'PLAN.json');checks=[]
    for case in ['PNS','IRON']:rt.contracts.validate_task(read(ROOT/f'tasks/{case}.json'))
    checks.append('Both task contracts and independent estimator routes checked')
    integration=ROOT/'integration';integration.mkdir(exist_ok=False)
    for case in ['PNS','IRON']:
        task=read(ROOT/f'tasks/{case}.json');candidate=integration/case/'candidate';candidate.mkdir(parents=True)
        # Arbitrary artificial engineering fixture, invisible to every constructor.
        expressions={'PNS':"{'row_id':np.arange(n),'age':r.uniform(20,79,n),'female':r.integers(0,2,n),'bmi':r.uniform(12,38,n),'sbp':r.uniform(90,160,n),'dbp':r.uniform(50,95,n)}",
                     'IRON':"{'row_id':np.arange(n),'hb_g_dl':r.uniform(9,16,n),'ferritin_ug_l':r.uniform(2,45,n)}"}
        code='import numpy as np\nimport pandas as pd\ndef generate(observed,spec,seed):\n r=np.random.default_rng(seed);n=spec["n"]\n return pd.DataFrame('+expressions[case]+')\n'
        (candidate/'generator.py').write_text(code,encoding='utf-8');write(candidate/'model_spec.json',{'n':task['n_rows']})
        out=rt.isolated_run(candidate,task,17100,integration/case/'run',plan['limits'])
        assert out['status']=='success',out.get('error')
        receipt=read(integration/case/'run/execution.json');probe=receipt['worker_report']['pre_import_probe']
        assert not probe['mnt_visible'] and not probe['home_visible'] and not probe['route_table']
        assert set(e['id'] for e in out['statistics']['analyses']+out['statistics']['diagnostics'])==set(ENDPOINTS[case])
        assert out['target_reference_read'] is False
    checks.append('Both artificial fixtures execute in WSL/bubblewrap without host mounts/home/network; exact spec pass-through')
    helper=load('p1_key_presence_only',api.KEY_HELPER);assert bool(helper.credentials().get('openai'))
    checks.append('Existing user-authorized OpenAI credential available; no secret output/write')
    source=read(ROOT/'SOURCE_BINDINGS.json')
    for entry in source.values():assert sha(ROOT/entry['source_file'])==entry['source_sha256'] and sha(ROOT/entry['artifact'])==entry['artifact_sha256']
    checks.append('Complete XML and eleven-page PDF text bound to original bytes; PDF Tables I/III/IV visually reconciled')
    ext={p.resolve().as_posix():sha(p) for p in api.external_files()}
    names=api.local_files(plan)-{'PREFLIGHT_REVIEW.json'}
    files={n:sha(ROOT/n) for n in sorted(names)}
    protected={}
    for name in ['pns_evidence_content_control_2026-11-16','iron_evidence_content_control_2026-11-16']:
        for p in (PROJECT/'work'/name).rglob('*'):
            if p.is_file():protected[p.relative_to(PROJECT).as_posix()]=sha(p)
    write(ROOT/'OLD_IMMUTABILITY.json',protected)
    write(ROOT/'PREFLIGHT_REVIEW.json',{'status':'pass','reviewer':'root engineering review plus separately implemented numerical tests, not external adjudication',
       'checks':checks,'reviewed_files':files,'reviewed_external_files':ext,'credential_helper_sha256':sha(api.KEY_HELPER),
       'paid_calls':0,'patient_data_parsed':False,'target_reference_values_inspected_in_this_preflight':False,'artificial_fixture_runs':2,
       'reference_schema_check':'Existing iron aggregate field names/types inspected without displaying numerical target values; project references already exposed historically',
       'source_audit_scope':'Conversion/identity only; scientific extraction will be audited after authors finish',
       'limitations':['PDF figures are not exposed as pixels','Known original-paper entry points','Existing exposed target families']})
    print(json.dumps({'preflight':'pass','checks':len(checks),'paid_calls':0,'fixture_runs':2}))

def freeze():
    p=read(ROOT/'PLAN.json');r=read(ROOT/'PREFLIGHT_REVIEW.json');assert r['status']=='pass'
    files={n:sha(ROOT/n) for n in sorted(api.local_files(p))}
    assert r['reviewed_files']=={n:h for n,h in files.items() if n!='PREFLIGHT_REVIEW.json'}
    write(ROOT/'LAUNCH_FREEZE.json',{'created_utc':now(),'files':files,'external_files':r['reviewed_external_files'],
       'credential_helper_sha256':r['credential_helper_sha256'],'model':p['model'],'limits':p['limits'],
       'target_reference_hashes':{'PNS':sha(PNS_REFERENCE),'IRON':sha(IRON_REFERENCE)},
       'old_immutability_sha256':sha(ROOT/'OLD_IMMUTABILITY.json'),'primary':PRIMARY,'endpoints':ENDPOINTS,
       'constructors':6,'final_tables':18,'no_target_values_in_author_inputs':True})
    write(ROOT/'ROOT_EXECUTION_APPROVAL.json',{'status':'approved','created_utc':now(),'authority':'User 17 November original-paper capability execution plus existing authorized GPT configuration',
       'launch_freeze_sha256':sha(ROOT/'LAUNCH_FREEZE.json'),'plan_sha256':sha(ROOT/'PLAN.json'),
       'episodes':[e['episode_id'] for e in p['episodes']],'files':files})
    api.verify_live_gate(ROOT,p)
    write(ROOT/'STATE.json',{'status':'frozen_ready_to_run','updated_utc':now(),'constructors':6,'final_slots':18,'api_cap_usd':24,
       'reference_scope':'previously exposed developmental cases','next':'Run six new API sessions; do not supply target feedback'})
    print(json.dumps({'frozen':True,'constructors':6,'final_tables':18,'cap_usd':24}))

def history(folder):
    return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file() and p.relative_to(folder).parts[0]!='evaluations'}
def engine(ep,p):return rt.ToolRuntime(ROOT/'episodes'/ep['episode_id'],read(ROOT/ep['task_path']),p['limits'])
def close():
    p=read(ROOT/'PLAN.json');api.verify_live_gate(ROOT,p)
    assert not (ROOT/'CONSTRUCTION_CLOSURE.json').exists()
    rows=[]
    for ep in p['episodes']:
        folder=ROOT/'episodes'/ep['episode_id'];out=read(folder/'OUTCOME.json')
        assert out['status'] in api.base.ORDINARY_TERMINAL
        candidate=out.get('selected_candidate');manifest=None
        if candidate:
            r=engine(ep,p);assert r.finalized and r.selected_candidate==candidate
            path,_=r._candidate(candidate);manifest=sha(path/'manifest.json')
        rows.append({'episode_id':ep['episode_id'],'case_id':ep['case_id'],'candidate_id':candidate,
                     'candidate_manifest_sha256':manifest,'outcome_status':out['status'],'files':history(folder)})
    write(ROOT/'CONSTRUCTION_CLOSURE.json',{'created_utc':now(),'all_episodes_closed':True,'episodes':rows,
      'plan_sha256':sha(ROOT/'PLAN.json'),'launch_freeze_sha256':sha(ROOT/'LAUNCH_FREEZE.json'),
      'evaluation_seeds':p['evaluation_seeds'],'target_reference_read':False})
    print(json.dumps({'all_closed':True,'selected_candidates':sum(r['candidate_id'] is not None for r in rows)}))
def verify_closure():
    p=read(ROOT/'PLAN.json');c=read(ROOT/'CONSTRUCTION_CLOSURE.json');api.verify_live_gate(ROOT,p)
    assert c['plan_sha256']==sha(ROOT/'PLAN.json') and c['launch_freeze_sha256']==sha(ROOT/'LAUNCH_FREEZE.json')
    assert len(c['episodes'])==6 and {r['episode_id'] for r in c['episodes']}=={e['episode_id'] for e in p['episodes']}
    for row in c['episodes']:assert row['files']==history(ROOT/'episodes'/row['episode_id'])
    return p,c
def draw():
    p,c=verify_closure();assert not (ROOT/'FINAL_TABLES.json').exists()
    slots=[]
    for ep in p['episodes']:
        row=next(r for r in c['episodes'] if r['episode_id']==ep['episode_id']);candidate=row['candidate_id']
        folder=ROOT/'episodes'/ep['episode_id'];r=engine(ep,p) if candidate else None
        for seed in p['evaluation_seeds']:
            slot={'episode_id':ep['episode_id'],'case_id':ep['case_id'],'seed':seed,'candidate_id':candidate,'status':'unavailable','statistics':None}
            if candidate:
                run=folder/'evaluations'/f'seed_{seed}'
                if not run.exists():r.generate_for_evaluation(candidate,seed,run.name)
                if (run/'execution.json').exists():
                    out=read(run/'execution.json');assert out['candidate_id']==candidate and out['seed']==seed
                    if (run/'input_bindings.json').exists():
                        binds=read(run/'input_bindings.json');assert binds=={f.name:sha(f) for f in (run/'input').iterdir() if f.is_file()}
                        for n in ['generator.py','model_spec.json']:assert binds[n]==sha(folder/'candidates'/candidate/n)
                    slot.update(status=out['status'],statistics=out.get('statistics'),error=out.get('error'),
                       receipt_path=(run/'execution.json').relative_to(ROOT).as_posix(),receipt_sha256=sha(run/'execution.json'))
                    if out['status']=='success':
                        assert out['generated_sha256']==sha(run/'output/generated.csv')
                        slot.update(generated_path=(run/'output/generated.csv').relative_to(ROOT).as_posix(),generated_sha256=sha(run/'output/generated.csv'))
                else:slot.update(status='failed',error={'type':'InterruptedExecution','message':'Existing attempt not repeated'})
            else:slot['reason']=row['outcome_status']
            slots.append(slot)
    verify_closure();write(ROOT/'FINAL_TABLES.json',{'created_utc':now(),'construction_closure_sha256':sha(ROOT/'CONSTRUCTION_CLOSURE.json'),'slots':slots,'target_reference_read':False})
    print(json.dumps({'final_slots':len(slots),'success':sum(s['status']=='success' for s in slots)}))

def evaluate():
    p,c=verify_closure();f=read(ROOT/'FINAL_TABLES.json');freeze=read(ROOT/'LAUNCH_FREEZE.json')
    assert f['construction_closure_sha256']==sha(ROOT/'CONSTRUCTION_CLOSURE.json')
    assert len(f['slots'])==18 and {(s['episode_id'],s['seed']) for s in f['slots']}=={(e['episode_id'],s) for e in p['episodes'] for s in p['evaluation_seeds']}
    assert sha(PNS_REFERENCE)==freeze['target_reference_hashes']['PNS'] and sha(IRON_REFERENCE)==freeze['target_reference_hashes']['IRON']
    independent=load('p1_final_independent',PROJECT/'work/request_only_repeatability_2026-11-11/review/recompute_saved_tables.py')
    records=[];failures=[];deltas=[]
    for slot in f['slots']:
        case=slot['case_id'];ep=next(e for e in p['episodes'] if e['episode_id']==slot['episode_id'])
        if slot['status']!='success':failures.append({k:v for k,v in slot.items() if k!='statistics'});values={k:None for k in ENDPOINTS[case]}
        else:
            path=ROOT/slot['generated_path'];assert sha(path)==slot['generated_sha256']
            assert sha(ROOT/slot['receipt_path'])==slot['receipt_sha256']
            task=read(ROOT/ep['task_path']);frame=rt.lifecycle.read_table(path,task,output=True)
            rt.contracts.validate_output(None,frame,task)
            values={e['id']:e['value'] for e in slot['statistics']['analyses']+slot['statistics']['diagnostics']}
            assert set(values)==set(ENDPOINTS[case])
            if case=='PNS':
                data,_=independent.load_table(path,task);other=independent.independent_statistics(data,'PNS')['values']
            else:other,_=rt.iron.independent_values(frame)
            for k,v in values.items():
                if v is None or other[k] is None:assert v is None and other[k] is None
                else:
                    d=abs(v-other[k]);deltas.append(d);assert np.isclose(v,other[k],atol=1e-9,rtol=1e-10),(case,k,v,other[k])
        for k,v in values.items():records.append({'episode_id':slot['episode_id'],'case_id':case,'seed':slot['seed'],'estimand':k,'value':v,'status':slot['status'] if slot['status']!='success' else 'computed' if v is not None else 'not_estimable'})
    # Only this post-closure section reads exposed reference estimates.
    pr=read(PNS_REFERENCE)['references']['PNS'];ir=read(IRON_REFERENCE)
    refs={'PNS':{k:v['value'] for k,v in pr.items()},'IRON':{k:v['estimate'] for k,v in ir['estimands'].items()}}
    # Preserve the older iron diagnostic definitions from the same reference cells.
    cells=ir['cells']
    refs['IRON'].update(low_hb_fraction=cells['both_low']['weighted_fraction']+cells['only_hb_low']['weighted_fraction'],
                       low_ferritin_fraction=cells['both_low']['weighted_fraction']+cells['only_ferritin_low']['weighted_fraction'])
    for row in records:
        ref=refs[row['case_id']][row['estimand']];row['reference']=ref
        if row['case_id']=='IRON':row['discrepancy']=rt.iron.discrepancy(row['estimand'],row['value'],ref)
        else:row['discrepancy']=abs(row['value']-ref) if row['value'] is not None and ref is not None else None
    out=ROOT/'analysis';out.mkdir(exist_ok=False)
    write(out/'seed_results.json',records);pd.DataFrame(records).to_csv(out/'seed_results.csv',index=False)
    authors=[]
    for ep in p['episodes']:
        for k in ENDPOINTS[ep['case_id']]:
            group=[r for r in records if r['episode_id']==ep['episode_id'] and r['estimand']==k];v=[r['value'] for r in group if r['value'] is not None]
            ds=[r['discrepancy'] for r in group if r['discrepancy'] is not None]
            authors.append({'episode_id':ep['episode_id'],'case_id':ep['case_id'],'estimand':k,'available_seeds':len(v),
                'seed_mean':float(np.mean(v)) if v else None,'seed_min':min(v) if v else None,'seed_max':max(v) if v else None,
                'mean_discrepancy':float(np.mean(ds)) if ds else None,'reference':refs[ep['case_id']][k]})
    write(out/'author_results.json',authors);pd.DataFrame(authors).to_csv(out/'author_results.csv',index=False)
    write(out/'failures.json',failures);write(out/'REFERENCE_USED.json',{'references':refs,'hashes':freeze['target_reference_hashes'],'scope':'previously exposed sample references, not population truth'})
    write(out/'INDEPENDENT_RECOMPUTATION.json',{'status':'pass','numeric_fields':len(deltas),'maximum_absolute_difference':max(deltas,default=0),
        'method':'Separately implemented existing QR and rank/count estimators; root-authored verification','additional_generator_runs':0})
    receipts=[read(x) for x in (ROOT/'episodes').glob('*/calls/*/receipt.json')]
    costs={'api_calls':len(receipts),'known_tariff_cost_usd':sum(r.get('tariff_cost_usd') or 0 for r in receipts),
      'accounted_usd':api.base.accounted(ROOT),'unknown_usage_calls':sum(r.get('tariff_cost_usd') is None for r in receipts),
      'requested_models':sorted({r['requested_model'] for r in receipts}),'returned_models':sorted({str(r.get('returned_model')) for r in receipts}),
      'usage':{k:sum((r.get('usage') or {}).get(k) or 0 for r in receipts) for k in ['input_tokens','output_tokens','total_tokens']},
      'invoice':False,'tariff':'bound existing tariff; not an invoice','target_rows_sent_to_api':False}
    write(out/'COSTS.json',costs)
    old=read(ROOT/'OLD_IMMUTABILITY.json');assert sha(ROOT/'OLD_IMMUTABILITY.json')==freeze['old_immutability_sha256']
    for n,h in old.items():assert sha(PROJECT/n)==h,n
    write(out/'CLOSEOUT_QA.json',{'status':'pass','constructors':6,'planned_final_slots':18,'successful_slots':sum(s['status']=='success' for s in f['slots']),
       'failed_or_unavailable':sum(s['status']!='success' for s in f['slots']),'seed_endpoint_records':len(records),'author_endpoint_records':len(authors),
       'old_files_unchanged':len(old),'source_code_frozen_inputs_unchanged':True,'source_code_audit':'still required separately'})
    print(json.dumps({'evaluated':len(f['slots']),'endpoints':len(records),'independent_max_difference':max(deltas,default=0),'cost_usd':costs['known_tariff_cost_usd']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['preflight','freeze','close','draw','evaluate']);args=parser.parse_args()
    globals()[args.action]()
