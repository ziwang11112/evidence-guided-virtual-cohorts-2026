"""Prepare, freeze and run exactly twenty captured API construction slots.

No generated code or reference analyses execute here. All calls have durable
reservation files; interrupted calls cannot be silently resent on resume.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import hashlib
import json
import os
import threading
import time
import provider_client as client

U=Path(__file__).resolve().parent
ORDER=['OA_ASTRA','DS_PRO','CL_FABLE','GE_CARBON','OA_SOL']
RATE_LOCK=threading.Lock()
LAST={}
STOP=threading.Event()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def hashes():
    paths=[U/name for name in ['provider_preflight.py','provider_client.py','run_pilot.py','prepare_packets.py','execute_pilot.py','analyze_pilot.py','EVALUATION_PROTOCOL.json','EVALUATION_PROTOCOL.md','PROVIDER_CATALOGS.json','PROTOCOL.md','_host_only/REFERENCE_SNAPSHOT.json']]
    paths+=sorted((U/'packets').rglob('*'))
    paths=[p for p in paths if p.is_file()]
    return {p.relative_to(U).as_posix():client.sha(p) for p in paths}

def prepare():
    catalog=load(U/'PROVIDER_CATALOGS.json')['providers']
    for c in client.CONFIGS.values():
        available={m.get('id',m.get('name','')).removeprefix('models/') for m in catalog[c['provider']].get('models',[])}
        assert c['model'] in available, c['model']
    slots=[]
    for repeat in [1,2]:
        for index,config in enumerate(ORDER):
            cases=['PNS','LIPID'] if (index+repeat)%2 else ['LIPID','PNS']
            for case in cases:
                slots.append({'construction_id':f'{case}_{config}_C{repeat}','case_id':'PNS' if case=='PNS' else 'lipids','packet_case':case,'model_config':config,'context':repeat,'prompt_path':f'packets/{case}/prompt.txt','task_path':f'packets/{case}/task.json'})
    value={'schema_version':1,'status':'prepared_not_launched','created_utc':client.utc(),'configs':client.CONFIGS,'provider_caps_usd':client.CAPS,
           'maximum_output_tokens_per_call':client.MAX_OUTPUT,'maximum_initial_calls':20,'maximum_repairs':20,'primary_provider_balanced_slots':16,'secondary_openai_slots':4,'constructions':slots,
           'user_authorization':'Latest user explicitly requests connecting APIs from D:/.env, running first20 and analyzing scientific utility. No credential content is sent to models.',
           'generation_mode':'whole_cohort','same_prompt_per_case':True,'retrieval':False,'tools':[],
           'scientific_evaluation':'All models sealed before 3 fixed output seeds and all predefined analyses. Existing exposed references; no target feedback or scientific parameter tuning.',
           'input_limit_bytes':190000,'repair_policy':'One formatting/Python AST/ABI repair at most; initial scientific choices retained; no automatic resend after transport/API failure.',
           'cost_basis':'Usage-derived tariff estimate, not invoice; unknown charged failures retain full reservation.',
           'api_input_separation':'Explicit standalone requests with no prior response ID, conversation, filesystem tool or reference attachments; prior model training exposure cannot be excluded.'}
    client.dump_new(U/'RUN_PLAN.json',value)
    print(json.dumps({'status':'prepared','slots':len(slots),'models':[c['model'] for c in client.CONFIGS.values()]}))

def freeze(review_path):
    plan=load(U/'RUN_PLAN.json'); review=load(U/review_path)
    assert len(plan['constructions'])==20
    assert review['status']=='pass' and not review.get('blocking_issues')
    assert review['implementation_and_packet_hashes']==hashes(), 'Reviewed implementation/packets changed before freeze'
    assert review['run_plan_sha256']==client.sha(U/'RUN_PLAN.json'), 'Reviewed run plan changed'
    client.dump_new(U/'LAUNCH_FREEZE.json',{'created_utc':client.utc(),'run_plan_sha256':client.sha(U/'RUN_PLAN.json'),'implementation_and_packet_hashes':hashes(),'review_path':review_path,'review_sha256':client.sha(U/review_path),'provider_generation_calls_before_freeze':0,'root_review':'Approved controlled API construction with same source packets and scientific freedom; no target-feedback route.'})

def verify_freeze():
    f=load(U/'LAUNCH_FREEZE.json')
    assert f['run_plan_sha256']==client.sha(U/'RUN_PLAN.json')
    assert f['implementation_and_packet_hashes']==hashes(),'Frozen implementation or packet changed'
    assert f['review_sha256']==client.sha(U/f['review_path'])
    p=load(U/'RUN_PLAN.json')
    assert p['configs']==client.CONFIGS and p['provider_caps_usd']==client.CAPS
    return p

def pace(provider):
    # Protect the shared OpenAI key from a burst across its two configurations.
    interval=25 if provider=='openai' else 2
    with RATE_LOCK:
        delay=max(0,LAST.get(provider,0)+interval-time.monotonic())
        LAST[provider]=time.monotonic()+delay
    if delay:time.sleep(delay)

def initial(slot):
    call_id=slot['construction_id']+'_initial';folder=U/'calls'/call_id
    if folder.exists():
        if not (folder/'receipt.json').exists():
            return {'call_id':call_id,'status':'interrupted_no_resend','artifact_status':'unavailable'}
        return load(folder/'receipt.json')
    verify_freeze()
    if STOP.is_set():raise RuntimeError('Batch halted before dispatch')
    pace(client.CONFIGS[slot['model_config']]['provider'])
    if STOP.is_set():raise RuntimeError('Batch halted before dispatch')
    prompt=(U/slot['prompt_path']).read_text(encoding='utf-8')
    print(json.dumps({'event':'dispatch','call_id':call_id,'model':client.CONFIGS[slot['model_config']]['model'],'utc':client.utc()}),flush=True)
    receipt,_=client.call_once(U,call_id,slot['model_config'],prompt)
    if receipt.get('reservation_exceeded'):STOP.set()
    print(json.dumps({'event':'received','call_id':call_id,'status':receipt['status'],'artifact_status':receipt.get('artifact_status'),'tariff_cost_usd':receipt.get('tariff_cost_usd'),'utc':client.utc()}),flush=True)
    return receipt

def choose_final(slot):
    ident=slot['construction_id'];initial_dir=U/'calls'/(ident+'_initial'); selected=None; repairs=0;reason=None
    if (initial_dir/'receipt.json').exists():
        r=load(initial_dir/'receipt.json')
        if r.get('artifact_status')=='valid_structure_and_python_ast' and r.get('completion_status')=='completed':selected=initial_dir
        elif r.get('artifact_status')=='invalid' and r.get('status')=='received' and not STOP.is_set():
            repaired=U/'calls'/(ident+'_repair');repairs=1
            if not repaired.exists():
                # Only returned syntax/ABI diagnostic; no run, scientific estimate or reference is consulted.
                prompt=(U/slot['prompt_path']).read_text(encoding='utf-8')+'\n\nMECHANICAL FORMAT/ABI REPAIR ONLY. Preserve your original scientific structure and numerical choices. Return the complete corrected JSON object. Do not introduce new scientific assumptions.\nDiagnostic: '+r['mechanical_error']+'\nYour original response:\n'+(initial_dir/'response_text.txt').read_text(encoding='utf-8')
                pace(client.CONFIGS[slot['model_config']]['provider'])
                verify_freeze()
                rr,_=client.call_once(U,ident+'_repair',slot['model_config'],prompt)
                if rr.get('reservation_exceeded'):STOP.set()
                print(json.dumps({'event':'mechanical_repair','construction_id':ident,'status':rr['status'],'artifact_status':rr.get('artifact_status'),'tariff_cost_usd':rr.get('tariff_cost_usd')}),flush=True)
            if (repaired/'receipt.json').exists():
                rr=load(repaired/'receipt.json')
                if rr.get('artifact_status')=='valid_structure_and_python_ast' and rr.get('completion_status')=='completed':selected=repaired
            reason='initial mechanical artifact invalid; repair did not produce a complete valid artifact' if selected is None else None
        else:reason=r.get('status','unknown')+': '+str(r.get('stop_reason',r.get('api_error_code','')))
    else:reason='interrupted or not dispatched; no silent replacement'
    candidate=None
    if selected:
        artifact=load(selected/'artifact.json');candidate=U/'candidates'/ident
        if not candidate.exists():
            candidate.mkdir(parents=True,exist_ok=False)
            (candidate/'generator.py').write_text(artifact['generator_py'],encoding='utf-8',newline='\n')
            client.dump_new(candidate/'model_spec.json',{'task':load(U/slot['task_path']),'model':artifact['model_spec']})
            client.dump_new(candidate/'decision_record.json',artifact['decision_record'])
            client.dump_new(candidate/'capture_binding.json',{'initial_call_id':ident+'_initial','selected_call_id':selected.name,'selected_artifact_sha256':client.sha(selected/'artifact.json'),'repair_count':repairs,'scientific_edits_by_host':False})
        expected_binding={'initial_call_id':ident+'_initial','selected_call_id':selected.name,'selected_artifact_sha256':client.sha(selected/'artifact.json'),'repair_count':repairs,'scientific_edits_by_host':False}
        assert (candidate/'generator.py').read_bytes()==artifact['generator_py'].encode('utf-8'), 'Candidate program differs from captured API artifact'
        assert load(candidate/'model_spec.json')=={'task':load(U/slot['task_path']),'model':artifact['model_spec']}, 'Candidate specification differs from captured API artifact'
        assert load(candidate/'decision_record.json')==artifact['decision_record'], 'Candidate decision record differs from captured API artifact'
        assert load(candidate/'capture_binding.json')==expected_binding, 'Candidate capture binding differs'
    return {'construction_id':ident,'case_id':slot['case_id'],'task_path':slot['task_path'],'candidate_path':candidate.relative_to(U).as_posix() if candidate else None,'status':'sealed' if candidate else 'failed','model_config':slot['model_config'],'context':slot['context'],'repair_count':repairs,'failure_reason':reason}

def launch():
    plan=verify_freeze()
    lock=U/'RUNNING.lock'
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,json.dumps({'pid':os.getpid(),'started_utc':client.utc()}).encode());os.close(fd)
    try:
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures={pool.submit(initial,s):s for s in plan['constructions']}
            for f in as_completed(futures):
                try:
                    r=f.result()
                    if r.get('reservation_exceeded'):raise RuntimeError('Actual usage exceeded reserved cost; pause before further dispatch')
                except Exception as e:
                    print(json.dumps({'event':'slot_exception','construction_id':futures[f]['construction_id'],'type':type(e).__name__,'message':str(e)[:400]}),flush=True)
        # Initial opportunities for every slot precede any repair spending.
        rows=[]
        for slot in plan['constructions']:
            try:rows.append(choose_final(slot))
            except Exception as e:
                rows.append({'construction_id':slot['construction_id'],'case_id':slot['case_id'],'task_path':slot['task_path'],'candidate_path':None,'status':'failed','model_config':slot['model_config'],'context':slot['context'],'repair_count':int((U/'calls'/(slot['construction_id']+'_repair')).exists()),'failure_reason':type(e).__name__+': '+str(e)[:400]})
        client.dump_new(U/'CONSTRUCTION_OUTCOMES.json',{'created_utc':client.utc(),'records':rows,'all20_accounted':len(rows)==20,'usage_accounted_usd':{p:client.ledger_accounted(U,p) for p in client.CAPS}})
        print(json.dumps({'event':'construction_batch_closed','sealed':sum(r['status']=='sealed' for r in rows),'failed':sum(r['status']=='failed' for r in rows),'provider_cost_accounted_usd':{p:client.ledger_accounted(U,p) for p in client.CAPS}}),flush=True)
    finally:
        lock.unlink()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--freeze-review');ap.add_argument('--launch',action='store_true');a=ap.parse_args()
    if a.prepare:prepare()
    elif a.freeze_review:freeze(a.freeze_review)
    elif a.launch:launch()
    else:ap.error('Choose --prepare, --freeze-review or --launch')
