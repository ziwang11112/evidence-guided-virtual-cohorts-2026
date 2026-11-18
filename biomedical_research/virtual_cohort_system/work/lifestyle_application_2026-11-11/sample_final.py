"""Close registered constructors, then draw only their selected immutable laws.

No target data or reference statistics are read by this module. Final draws are
separate from Agent-visible trials and require the complete global closure.
"""
from pathlib import Path
import argparse
import importlib.util
import json

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lifestyle_final_launcher',ROOT/'api_loop.py')
launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch)
spec=importlib.util.spec_from_file_location('lifestyle_final_tools',ROOT/'tools_runtime.py')
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
read,sha,write_new=launch.read,launch.sha,launch.write_new

def history(folder):
    return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*'))
            if p.is_file() and p.relative_to(folder).parts[0]!='evaluations'}

def engine(ep,plan):
    return runtime.ToolRuntime(ROOT/'episodes'/ep['episode_id'],read(ROOT/ep['task_path']),plan['limits'])

def close():
    plan=read(ROOT/'PLAN.json');launch.verify_live_gate(ROOT,plan)
    if (ROOT/'CONSTRUCTION_CLOSURE.json').exists():return verify()
    rows=[]
    for ep in plan['episodes']:
        folder=ROOT/'episodes'/ep['episode_id'];out=read(folder/'OUTCOME.json')
        assert out['episode_id']==ep['episode_id']
        if out['status'] not in launch.base.ORDINARY_TERMINAL:
            raise RuntimeError('Non-routine author failure requires root inspection before closing')
        candidate=out.get('selected_candidate');manifest=None
        if candidate:
            r=engine(ep,plan)
            assert r.finalized and r.selected_candidate==candidate
            path,_=r._candidate(candidate);manifest=sha(path/'manifest.json')
        rows.append(dict(episode_id=ep['episode_id'],candidate_id=candidate,
            candidate_manifest_sha256=manifest,outcome_status=out['status'],files=history(folder)))
    write_new(ROOT/'CONSTRUCTION_CLOSURE.json',dict(created_utc=launch.utc(),
        plan_sha256=sha(ROOT/'PLAN.json'),launch_freeze_sha256=sha(ROOT/'LAUNCH_FREEZE.json'),
        all_episodes_closed=True,episodes=rows,evaluation_seeds=plan['evaluation_seeds'],
        target_reference_read=False))
    return verify()

def verify():
    plan=read(ROOT/'PLAN.json');c=read(ROOT/'CONSTRUCTION_CLOSURE.json')
    assert c['all_episodes_closed'] and c['plan_sha256']==sha(ROOT/'PLAN.json')
    assert c['launch_freeze_sha256']==sha(ROOT/'LAUNCH_FREEZE.json')
    assert {r['episode_id'] for r in c['episodes']}=={e['episode_id'] for e in plan['episodes']}
    assert len(c['episodes'])==len(plan['episodes'])
    assert c['evaluation_seeds']==plan['evaluation_seeds']
    for row in c['episodes']:assert row['files']==history(ROOT/'episodes'/row['episode_id']),row['episode_id']
    return c

def verify_receipt(run,folder,candidate,seed):
    out=read(run/'execution.json')
    assert out['candidate_id']==candidate and out['seed']==seed
    if (run/'input_bindings.json').exists():
        bindings=read(run/'input_bindings.json')
        assert bindings=={p.name:sha(p) for p in (run/'input').iterdir() if p.is_file()}
        for n in ['generator.py','model_spec.json']:assert bindings[n]==sha(folder/'candidates'/candidate/n)
    if out['status']=='success':
        assert (run/'input_bindings.json').exists()
        assert out['generated_sha256']==sha(run/'output/generated.csv')
        assert out['statistics']['target_reference_read'] is False
    return out

def draw():
    plan=read(ROOT/'PLAN.json');launch.verify_live_gate(ROOT,plan);c=verify()
    assert len(plan['evaluation_seeds'])==3 and len(set(plan['evaluation_seeds']))==3
    assert not (ROOT/'FINAL_TABLES.json').exists(),'Final draw inventory already closed; do not relaunch'
    slots=[]
    for ep in plan['episodes']:
        closed=next(r for r in c['episodes'] if r['episode_id']==ep['episode_id'])
        folder=ROOT/'episodes'/ep['episode_id'];candidate=closed['candidate_id']
        r=engine(ep,plan) if candidate else None
        for seed in plan['evaluation_seeds']:
            slot=dict(episode_id=ep['episode_id'],case_id='lifestyle',arm=ep['arm'],seed=seed,
                      candidate_id=candidate,status='unavailable',statistics=None)
            if candidate:
                run=folder/'evaluations'/('seed_'+str(seed))
                if not run.exists():r.generate_for_evaluation(candidate,seed,run.name)
                if (run/'execution.json').exists():
                    out=verify_receipt(run,folder,candidate,seed)
                    slot.update(status=out['status'],statistics=out.get('statistics'),error=out.get('error'),
                        receipt_path=(run/'execution.json').relative_to(ROOT).as_posix(),receipt_sha256=sha(run/'execution.json'))
                    if out['status']=='success':slot.update(generated_path=(run/'output/generated.csv').relative_to(ROOT).as_posix(),generated_sha256=sha(run/'output/generated.csv'))
                else:
                    slot.update(status='failed',error={'type':'InterruptedExecution','message':'Existing run has no receipt; never automatically retried'})
            else:slot['reason']=closed['outcome_status']
            slots.append(slot)
    verify()
    write_new(ROOT/'FINAL_TABLES.json',dict(created_utc=launch.utc(),
        construction_closure_sha256=sha(ROOT/'CONSTRUCTION_CLOSURE.json'),slots=slots,
        target_reference_read=False))
    print(json.dumps({'slots':len(slots),'successful':sum(s['status']=='success' for s in slots),'unavailable_or_failed':sum(s['status']!='success' for s in slots)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['close','draw','verify'])
    args=parser.parse_args()
    if args.action=='close':print(json.dumps({'all_episodes_closed':close()['all_episodes_closed']}))
    elif args.action=='draw':draw()
    else:print(json.dumps({'closure_verified':verify()['all_episodes_closed']}))
