"""Close all four authors, sample frozen final laws, then compare stored aggregates."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from statistics import mean
from datetime import datetime, timezone
import tools_runtime as runtime

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
SNAPSHOT=PROJECT/'work/cross_model_api_pilot_2026-11-10/_host_only/REFERENCE_SNAPSHOT.json'
SNAPSHOT_SHA='2c70de16a941b2f023f249f52b2c7084789b20b3af4df9c6b0d2061316f8e002'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def now():return datetime.now(timezone.utc).isoformat()

def history(folder):
    return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*'))
            if p.is_file() and p.relative_to(folder).parts[0]!='evaluations'}

def close():
    plan=read(ROOT/'PLAN.json');rows=[]
    for ep in plan['episodes']:
        folder=ROOT/'episodes'/ep['episode_id'];o=read(folder/'OUTCOME.json')
        assert o['episode_id']==ep['episode_id']
        candidate=o.get('selected_candidate')
        if candidate:
            task=read(ROOT/ep['task_path'])
            engine=runtime.ToolRuntime(folder,task,plan['limits'])
            assert engine.finalized and engine.selected_candidate==candidate
            cp,manifest=engine._candidate(candidate)
            mh=sha(cp/'manifest.json')
        else:mh=None
        rows.append(dict(episode_id=ep['episode_id'],case_id=ep['case_id'],arm=ep['arm'],
                         candidate_id=candidate,candidate_manifest_sha256=mh,
                         outcome_status=o['status'],files=history(folder)))
    write(ROOT/'CONSTRUCTION_CLOSURE.json',dict(created_utc=now(),plan_sha256=sha(ROOT/'PLAN.json'),
        episodes=rows,all_episodes_closed=True,evaluation_seeds=plan['evaluation_seeds'],
        new_reference_fits=False,reference_snapshot_sha256=SNAPSHOT_SHA))
    return verify()

def verify():
    c=read(ROOT/'CONSTRUCTION_CLOSURE.json');p=read(ROOT/'PLAN.json')
    assert c['all_episodes_closed'] and c['plan_sha256']==sha(ROOT/'PLAN.json')
    assert len(c['episodes'])==4
    assert {x['episode_id'] for x in c['episodes']}=={x['episode_id'] for x in p['episodes']}
    assert c['evaluation_seeds']==p['evaluation_seeds']
    for row in c['episodes']:
        assert row['files']==history(ROOT/'episodes'/row['episode_id']),row['episode_id']
    return c

def draw():
    c=verify();p=read(ROOT/'PLAN.json');slots=[]
    for ep in p['episodes']:
        closed=next(x for x in c['episodes'] if x['episode_id']==ep['episode_id'])
        folder=ROOT/'episodes'/ep['episode_id']
        engine=runtime.ToolRuntime(folder,read(ROOT/ep['task_path']),p['limits']) if closed['candidate_id'] else None
        for seed in p['evaluation_seeds']:
            rec=dict(episode_id=ep['episode_id'],case_id=ep['case_id'],arm=ep['arm'],seed=seed,
                     candidate_id=closed['candidate_id'],status='unavailable',statistics=None)
            if closed['candidate_id']:
                name='seed_'+str(seed);run=folder/'evaluations'/name
                if run.exists():
                    # A failed/interrupted attempt is preserved; never execute it again.
                    if (run/'execution.json').exists():out=verify_receipt(run,closed['candidate_id'],seed,folder)
                    else:out={'status':'failed','error':{'type':'InterruptedExecution','message':'No completed receipt; not retried'}}
                else:
                    engine.generate_for_evaluation(closed['candidate_id'],seed,name)
                    out=verify_receipt(run,closed['candidate_id'],seed,folder)
                rec.update(status=out['status'],statistics=out.get('statistics'),error=out.get('error'),
                           receipt_path=str((run/'execution.json').relative_to(ROOT)) if (run/'execution.json').exists() else None,
                           generated_path=str((run/'output/generated.csv').relative_to(ROOT)) if out['status']=='success' else None)
                if rec['receipt_path']:rec['receipt_sha256']=sha(ROOT/rec['receipt_path'])
                if rec['generated_path']:rec['generated_sha256']=sha(ROOT/rec['generated_path'])
            else:rec['reason']=closed['outcome_status']
            slots.append(rec)
    verify()
    write(ROOT/'FINAL_TABLES.json',dict(created_utc=now(),construction_closure_sha256=sha(ROOT/'CONSTRUCTION_CLOSURE.json'),slots=slots))
    return slots

def verify_receipt(run,candidate,seed,episode_folder):
    out=read(run/'execution.json')
    assert out['candidate_id']==candidate and out['seed']==seed
    if (run/'input_bindings.json').exists():
        bindings=read(run/'input_bindings.json')
        assert bindings=={x.name:sha(x) for x in (run/'input').iterdir() if x.is_file()}
        for name in ['generator.py','model_spec.json']:
            assert bindings[name]==sha(episode_folder/'candidates'/candidate/name)
    if out['status']=='success':
        assert (run/'input_bindings.json').is_file()
        assert out['generated_sha256']==sha(run/'output/generated.csv')
        assert out.get('statistics') is not None
    return out

def summarize_values(selected,key,ref):
    estimates=[];seeds=[]
    for s in selected:
        statistic=None
        if s['status']=='success' and s.get('statistics'):
            statistic=next((x for cat in ['analyses','diagnostics'] for x in s['statistics'].get(cat,[]) if x['id']==key),None)
        value=statistic['value'] if statistic else None
        seeds.append({'seed':s['seed'],'status':s['status'],'value':value})
        if value is not None:estimates.append(value)
    return dict(values=seeds,available_seeds=len(estimates),mean=mean(estimates) if estimates else None,
                minimum=min(estimates) if estimates else None,maximum=max(estimates) if estimates else None,
                mean_absolute_reference_difference=mean(abs(x-ref) for x in estimates) if estimates and ref is not None else None)

def evaluate():
    c=verify();p=read(ROOT/'PLAN.json');delivered=read(ROOT/'FINAL_TABLES.json')
    assert delivered['construction_closure_sha256']==sha(ROOT/'CONSTRUCTION_CLOSURE.json')
    slots=delivered['slots'];assert len(slots)==12
    expected={(ep['episode_id'],seed) for ep in p['episodes'] for seed in p['evaluation_seeds']}
    assert {(s['episode_id'],s['seed']) for s in slots}==expected
    for rec in slots:
        ep=next(x for x in p['episodes'] if x['episode_id']==rec['episode_id'])
        closed=next(x for x in c['episodes'] if x['episode_id']==rec['episode_id'])
        assert rec['case_id']==ep['case_id'] and rec['arm']==ep['arm']
        assert rec.get('candidate_id')==closed['candidate_id']
        assert rec['status'] in {'success','failed','unavailable'}
        if rec.get('receipt_path'):
            folder=ROOT/'episodes'/rec['episode_id']
            run=folder/'evaluations'/('seed_'+str(rec['seed']))
            assert Path(rec['receipt_path'])==(run/'execution.json').relative_to(ROOT)
            assert sha(run/'execution.json')==rec['receipt_sha256']
            receipt=verify_receipt(run,closed['candidate_id'],rec['seed'],folder)
            assert receipt['status']==rec['status'] and receipt.get('statistics')==rec.get('statistics')
        if rec['status']=='success':
            assert closed['candidate_id'] and rec.get('receipt_path') and rec.get('generated_path')
            assert Path(rec['generated_path'])==Path('episodes')/rec['episode_id']/'evaluations'/('seed_'+str(rec['seed']))/'output/generated.csv'
            assert sha(ROOT/rec['generated_path'])==rec['generated_sha256']
        if closed['candidate_id'] is None:
            assert rec['status']=='unavailable' and rec.get('statistics') is None
    # First reference-value read in the new evaluator; gated by complete closure and final draws.
    assert sha(SNAPSHOT)==SNAPSHOT_SHA
    refs=read(SNAPSHOT)['references'];summaries=[]
    for ep in p['episodes']:
        selected=[s for s in slots if s['episode_id']==ep['episode_id']]
        for key,reference in refs[ep['case_id']].items():
            summaries.append(dict(episode_id=ep['episode_id'],case_id=ep['case_id'],arm=ep['arm'],analysis_id=key,
                unit=reference['unit'],reference=reference,**summarize_values(selected,key,reference.get('value'))))
    outcomes=[read(ROOT/'episodes'/e['episode_id']/'OUTCOME.json') for e in p['episodes']]
    payload=dict(created_utc=now(),scope='Four request-only episodes, two existing cases; descriptive developmental pilot',
        reference_snapshot_sha256=SNAPSHOT_SHA,final_tables_sha256=sha(ROOT/'FINAL_TABLES.json'),
        counts={'episodes':4,'cases':2,'final_slots':12,'successful_tables':sum(s['status']=='success' for s in slots),
                'failed_tables':sum(s['status']=='failed' for s in slots),'unavailable_tables':sum(s['status']=='unavailable' for s in slots),
                'model_calls':sum(o['calls_reserved'] for o in outcomes)},
        costs={'known_tariff_usd':sum(o['known_tariff_cost_usd'] for o in outcomes),'accounted_usd':sum(o['accounted_usd'] for o in outcomes)},
        summaries=summaries,episodes=outcomes,slots=slots,
        limitations=['One constructor per arm/case; no superiority inference.','References already exposed at project level.','Source-screening aliases do not guarantee independence.','Seed ranges describe simulation variation, not statistical confidence or transport uncertainty.','No new patient records or target fitting.'])
    write(ROOT/'EVALUATION.json',payload)
    with (ROOT/'ANALYSIS_RESULTS.csv').open('x',encoding='utf-8-sig',newline='') as f:
        fields=['episode_id','case_id','arm','analysis_id','unit','available_seeds','mean','minimum','maximum','reference_value','mean_absolute_reference_difference']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for s in summaries:w.writerow({**{k:s.get(k) for k in fields if k!='reference_value'},'reference_value':s['reference'].get('value')})
    return {'counts':payload['counts'],'costs':payload['costs']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['close','draw','evaluate']);args=parser.parse_args()
    result={'close':close,'draw':draw,'evaluate':evaluate}[args.phase]()
    print(json.dumps(result if args.phase=='evaluate' else {'phase':args.phase,'status':'complete'},ensure_ascii=False))
