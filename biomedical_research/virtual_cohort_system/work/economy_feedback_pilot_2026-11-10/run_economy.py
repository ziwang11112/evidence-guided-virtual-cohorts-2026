"""Bounded captured API authoring, with a separately sealed review stage."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import json
import os
import threading
import time
import provider_client as client

U=Path(__file__).resolve().parent
STOP=threading.Event(); RATE=threading.Lock(); LAST={}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(name,value):client.dump_new(U/name,value)

def hashes():
    names=['bootstrap.py','budget_keys.py','provider_client.py','run_economy.py','execute_stages.py',
           'evaluate_stages.py','PROTOCOL.json','PROTOCOL.md','REVIEW_INSTRUCTION.txt','INPUT_ASSEMBLY.json',
           '_host_only/REFERENCE_SNAPSHOT.json']
    paths=[U/n for n in names]+sorted(p for p in (U/'packets').rglob('*') if p.is_file())
    return {p.relative_to(U).as_posix():client.sha(p) for p in paths}

def prepare():
    parents=[]
    for model,suffix,role in [('OA_SOL','SOL_A','paired_parent'),('DS_PRO','DS','benchmark'),
                              ('OA_SOL','SOL_B','benchmark'),('OA_ASTRA','ASTRA','benchmark')]:
        for case in (['PNS','LIPID'] if suffix in {'SOL_A','SOL_B'} else ['LIPID','PNS']):
            parents.append({'parent_id':case+'_'+suffix,'case_id':'PNS' if case=='PNS' else 'lipids',
                'model_config':model,'context':suffix,'role':role,'task_path':f'packets/{case}/task.json',
                'prompt_path':f'packets/{case}/prompt.txt'})
    branches=[]
    for case,arms in [('PNS',['second_look','feedback']),('LIPID',['feedback','second_look'])]:
        for arm in arms:branches.append({'branch_id':case+'_SOL_A_'+arm.upper(),
            'parent_id':case+'_SOL_A','arm':arm})
    save('RUN_PLAN.json',{'created_utc':client.utc(),'status':'prepared',
        'configs':client.CONFIGS,'caps':client.CAPS,'max_output_tokens':client.MAX_OUTPUT,
        'maximum_calls':12,'maximum_repairs':0,'maximum_initial_calls':8,'maximum_review_calls':4,
        'parents':parents,'branches':branches,'policy_sha256':client.sha(U.parents[1]/'docs/MODEL_USE_POLICY_2026-11-10.json'),
        'protocol_sha256':client.sha(U/'PROTOCOL.json'),
        'cost_scope':'usage-derived tariffs, not invoice; unknown usage retains reservation',
        'api_context':'standalone request, no previous_response_id or other candidate; native high effort unchanged',
        'authorization':'Latest user approves economy continuation; 8Sol+2Astra+2DS total12max calls, no other providers.'})
    print(json.dumps({'prepared_parents':8,'review_branches':4,'max_calls':12,'caps':client.CAPS}))

def freeze(review_name):
    review=load(U/review_name)
    assert review['status']=='pass' and not review.get('blocking_issues')
    assert review['implementation_and_packet_hashes']==hashes()
    assert review['run_plan_sha256']==client.sha(U/'RUN_PLAN.json')
    assert not (U/'calls').exists(),'Cannot first freeze after API calls'
    save('LAUNCH_FREEZE.json',{'created_utc':client.utc(),'implementation_and_packet_hashes':hashes(),
        'run_plan_sha256':client.sha(U/'RUN_PLAN.json'),'review_path':review_name,'review_sha256':client.sha(U/review_name)})

def verify():
    f=load(U/'LAUNCH_FREEZE.json');plan=load(U/'RUN_PLAN.json')
    assert f['implementation_and_packet_hashes']==hashes(),'Frozen code or inputs changed'
    assert f['run_plan_sha256']==client.sha(U/'RUN_PLAN.json')
    assert f['review_sha256']==client.sha(U/f['review_path'])
    assert plan['configs']==client.CONFIGS and plan['caps']==client.CAPS and sum(client.CAPS.values())==10
    assert set(client.CONFIGS)=={'OA_SOL','OA_ASTRA','DS_PRO'}
    assert len(plan['parents'])==8 and len(plan['branches'])==4
    return plan

def pace(provider):
    with RATE:
        delay=max(0,LAST.get(provider,0)+(25 if provider=='openai' else 2)-time.monotonic())
        LAST[provider]=time.monotonic()+delay
    if delay:time.sleep(delay)

def request(phase,ident,config,prompt):
    plan=verify()
    allowed={p['parent_id']:p['model_config'] for p in plan['parents']} if phase=='initial' else {b['branch_id']:'OA_SOL' for b in plan['branches']}
    assert ident in allowed and config==allowed[ident]
    folder=U/'calls'/phase/ident
    if folder.exists():
        return load(folder/'receipt.json') if (folder/'receipt.json').exists() else {'status':'interrupted_no_resend'}
    assert not STOP.is_set(),'Stopped before dispatch'
    pace(client.CONFIGS[config]['provider'])
    assert not STOP.is_set(),'Stopped before dispatch'
    print(json.dumps({'event':'dispatch','phase':phase,'id':ident,'model':client.CONFIGS[config]['model'],'utc':client.utc()}),flush=True)
    receipt,_=client.call_once(U,phase+'/'+ident,config,prompt)
    if receipt.get('reservation_exceeded'):STOP.set()
    print(json.dumps({'event':'received','phase':phase,'id':ident,'status':receipt.get('status'),
        'artifact_status':receipt.get('artifact_status'),'cost_usd':receipt.get('tariff_cost_usd')}),flush=True)
    return receipt

def complete(folder):
    if not (folder/'receipt.json').exists():return False
    r=load(folder/'receipt.json')
    return r.get('status')=='received' and r.get('completion_status')=='completed' and r.get('artifact_status')=='valid_structure_and_python_ast'

def copy_candidate(phase,ident,task_path):
    source=U/'calls'/phase/ident;artifact=load(source/'artifact.json');dest=U/'candidates'/phase/ident
    binding={'call_path':source.relative_to(U).as_posix(),'artifact_sha256':client.sha(source/'artifact.json'),'host_scientific_edits':False}
    wrapped={'task':load(U/task_path),'model':artifact['model_spec']}
    if not dest.exists():
        dest.mkdir(parents=True,exist_ok=False)
        (dest/'generator.py').write_text(artifact['generator_py'],encoding='utf-8',newline='\n')
        client.dump_new(dest/'model_spec.json',wrapped)
        client.dump_new(dest/'decision_record.json',artifact['decision_record'])
        client.dump_new(dest/'capture_binding.json',binding)
    assert (dest/'generator.py').read_bytes()==artifact['generator_py'].encode()
    assert load(dest/'model_spec.json')==wrapped and load(dest/'decision_record.json')==artifact['decision_record']
    assert load(dest/'capture_binding.json')==binding
    return dest.relative_to(U).as_posix()

def phase_lock(phase):
    path=U/'RUNNING.lock';fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,json.dumps({'phase':'api_'+phase,'pid':os.getpid(),'utc':client.utc()}).encode());os.close(fd)
    return path

def initial():
    plan=verify();lock=phase_lock('initial');errors={}
    try:
        def work(p):return request('initial',p['parent_id'],p['model_config'],(U/p['prompt_path']).read_text(encoding='utf-8'))
        with ThreadPoolExecutor(max_workers=3) as pool:
            fs={pool.submit(work,p):p for p in plan['parents']}
            for f in as_completed(fs):
                try:f.result()
                except Exception as e:errors[fs[f]['parent_id']]=type(e).__name__+': '+str(e)[:300]
        records=[]
        for p in plan['parents']:
            folder=U/'calls/initial'/p['parent_id']; ok=complete(folder)
            records.append({k:p[k] for k in ['parent_id','case_id','model_config','context','role','task_path']}|
                {'status':'sealed' if ok else 'failed','candidate_path':copy_candidate('initial',p['parent_id'],p['task_path']) if ok else None,
                 'failure_reason':None if ok else errors.get(p['parent_id'],'Incomplete/invalid/unavailable API artifact; see preserved call receipt')})
        save('INITIAL_OUTCOMES.json',{'created_utc':client.utc(),'records':records,'errors':errors})
        print(json.dumps({'event':'initial_closed','sealed':sum(r['status']=='sealed' for r in records),'failed':sum(r['status']=='failed' for r in records)}))
    finally:lock.unlink()

def prepare_reviews():
    import execute_stages as ex
    # Gate and generated-only payload names are supplied by the reviewed stage adapter.
    plan=verify(); ex.verify_stage_closure('diagnostic'); reports=ex.verify_diagnostic_reports()
    parents={r['parent_id']:r for r in ex.verify_initial()['records']}
    folder=U/'review_inputs';folder.mkdir(exist_ok=False); rows=[]
    for branch in plan['branches']:
        parent=parents[branch['parent_id']];ident=branch['branch_id']
        if parent['status']=='failed':
            rows.append(dict(branch,eligible=False,reason='parent_failed',prompt_path=None));continue
        old=load(U/'calls/initial'/parent['parent_id']/'artifact.json')
        original=next(p for p in plan['parents'] if p['parent_id']==parent['parent_id'])
        text=(U/original['prompt_path']).read_text(encoding='utf-8')+'\n\nREVIEW_TASK\n'+(U/'REVIEW_INSTRUCTION.txt').read_text(encoding='utf-8')
        text+='\n\nYOUR_FROZEN_EARLIER_SUBMISSION\n'+json.dumps(old,ensure_ascii=False,separators=(',',':'))
        diag_path=None
        if branch['arm']=='feedback':
            from evaluate_stages import feedback_for
            diag_path=reports['reports'][parent['parent_id']]['path']
            text+='\n\nRECORDED_OBSERVATIONS_OF_YOUR_OWN_GENERATOR\n'+json.dumps(feedback_for(ident),ensure_ascii=False,separators=(',',':'))
        dest=folder/(ident+'.txt');dest.write_text(text,encoding='utf-8',newline='\n')
        rows.append(dict(branch,eligible=True,prompt_path=dest.relative_to(U).as_posix(),prompt_sha256=client.sha(dest),
            initial_artifact_sha256=client.sha(U/'calls/initial'/parent['parent_id']/'artifact.json'),
            diagnostic_path=diag_path,diagnostic_sha256=client.sha(U/diag_path) if diag_path else None))
    save('REVIEW_INPUTS.json',{'created_utc':client.utc(),'rows':rows,'diagnostic_closure_sha256':client.sha(U/'DIAGNOSTIC_CLOSURE.json')})
    print(json.dumps({'review_inputs':len(rows),'eligible':sum(r['eligible'] for r in rows)}))

def reviews():
    import execute_stages as ex
    plan=verify();ex.verify_stage_closure('diagnostic');ex.verify_diagnostic_reports()
    inputs=load(U/'REVIEW_INPUTS.json');audit=load(U/'REVIEW_INPUT_AUDIT.json')
    assert audit['status']=='pass' and not audit.get('blocking_issues')
    assert audit['review_inputs_sha256']==client.sha(U/'REVIEW_INPUTS.json')
    for r in inputs['rows']:
        if r['eligible']:assert r['prompt_sha256']==client.sha(U/r['prompt_path'])
    parents={r['parent_id']:r for r in ex.verify_initial()['records']}
    lock=phase_lock('review'); errors={}
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            fs={pool.submit(request,'review',r['branch_id'],'OA_SOL',(U/r['prompt_path']).read_text(encoding='utf-8')):r for r in inputs['rows'] if r['eligible']}
            for f in as_completed(fs):
                try:f.result()
                except Exception as e:errors[fs[f]['branch_id']]=type(e).__name__+': '+str(e)[:300]
        rows=[]
        for b in plan['branches']:
            p=parents[b['parent_id']];folder=U/'calls/review'/b['branch_id'];path=p['candidate_path']
            if p['status']=='failed':disposition='parent_failed';reason='Preassigned parent unavailable; not substituted'
            elif not complete(folder):disposition='retained_review_failed';reason=errors.get(b['branch_id'],'Incomplete/invalid/unavailable review; original product retained explicitly')
            else:
                artifact=load(folder/'artifact.json');record=artifact['decision_record'].get('review')
                if not isinstance(record,dict) or record.get('action') not in {'retain','revise'} or any(k not in record for k in ['changes_summary','evidence_basis','remaining_limits']):
                    disposition='retained_review_failed';reason='Review declaration missing or invalid; original product retained'
                else:
                    captured=copy_candidate('review',b['branch_id'],p['task_path'])
                    old=load(U/'calls/initial'/p['parent_id']/'artifact.json')
                    same=artifact['model_spec']==old['model_spec'] and artifact['generator_py']==old['generator_py']
                    disposition='retained_noop' if same else 'revised';path=p['candidate_path'] if same else captured
                    reason='Actual code/spec comparison; declared action='+record['action']+'; scientific law equivalence beyond byte identity not presumed'
            rows.append(dict(b,disposition=disposition,candidate_path=path,reason=reason))
        save('REVIEW_OUTCOMES.json',{'created_utc':client.utc(),'records':rows,'errors':errors})
        print(json.dumps({'event':'review_closed','outcomes':[{k:r[k] for k in ['branch_id','disposition']} for r in rows],
            'accounted_usd':{p:client.ledger_accounted(U,p) for p in client.CAPS}}))
    finally:lock.unlink()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','freeze','initial','prepare-reviews','reviews']);ap.add_argument('--review',default='PREFLIGHT_REVIEW.json');args=ap.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='freeze':freeze(args.review)
    elif args.command=='initial':initial()
    elif args.command=='prepare-reviews':prepare_reviews()
    else:reviews()
