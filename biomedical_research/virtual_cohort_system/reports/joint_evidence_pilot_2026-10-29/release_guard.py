"""Verify every committed source/output before allowing target outcome parsing."""
from datetime import datetime
from pathlib import Path
from cohort_harness.lifecycle import read_json,sha256,verify_candidate
from cohort_harness.execution import verify_execution
from cohort_harness.source_replay import verify_source_replay

def require(value,message):
    if not value: raise ValueError(message)

def stamp(value):
    t=datetime.fromisoformat(value.replace('Z','+00:00'))
    require(t.tzinfo is not None and t.utcoffset().total_seconds()==0,'Invalid UTC timestamp')
    return t

def ref(row,path):
    actual=Path(row['path'])
    require(actual.is_absolute() and '..' not in actual.parts,'Invalid artifact path')
    for part in [actual,*actual.parents]:
        require(not part.is_symlink() and not getattr(part,'is_junction',lambda:False)(),'Linked path')
    require(actual.resolve(strict=True)==path.resolve(strict=True),'Wrong path')
    require(sha256(path)==row['sha256'],'Changed artifact')

def verify_release(commitment_path):
    e=Path(__file__).resolve().parent;p=e.parents[1]
    b=Path(read_json(e/'execution_location.json')['bundle'])
    require(Path(commitment_path).resolve(strict=True)==e/'evaluation_commitment.json','Wrong commitment')
    m=read_json(commitment_path);a=read_json(e/'protocol_commitment.json')
    require(m['authorize_target_evaluation'] is True and m['all_candidates_and_seeds_committed'] is True,'Not authorized')
    require(m['post_evaluation_builder_revision_allowed'] is False,'Post-release revision forbidden')
    for rel,h in a['files'].items():require(sha256(e/rel)==h,'Protocol changed: '+rel)
    for rel,h in a['core_files'].items():require(sha256(p/rel)==h,'Harness changed: '+rel)
    require(sha256(p/'work/m2-runtime-config.json')==a['runtime_config_sha256'],'Runtime changed')
    require(m['custodian_lock_sha256']==a['custodian_lock_sha256']==sha256(p/'work/analysis-evidence-gap-2026-10-29/custodian/custodian_lock.json'),'Custody mismatch')
    intent=read_json(e/'pilot_intent.json');design=read_json(e/'evaluation_design.json')
    require(design['variants']==intent['variants'] and design['seeds']==intent['target_seeds'],'Schedule mismatch')
    ref(m['evaluation_design'],e/'evaluation_design.json')
    ref(m['evaluation_amendment'],e/'evaluation/protocol_amendment.json')
    ref(m['controller_guard'],e/'release_guard.py')
    require(m['controller_guard']['function']=='verify_release','Wrong guard')
    ref(m['builder_observed'],b/'observed.csv')
    require(sha256(b/'observed.csv')==read_json(e/'baseline_import.json')['observed_sha256'],'Observed changed')
    t0=stamp(a['created_utc']); freeze_receipts={}
    expected={(v,s) for v in intent['variants'] for s in ['initial','final']}
    rows=m['candidate_commitments']
    require(len(rows)==len(expected) and {(x['variant'],x['stage']) for x in rows}==expected,'Wrong candidate grid')
    for row in rows:
        name=row['variant'];cp=b/'candidates'/name
        ref(row,cp/'freeze.json');r=verify_candidate(b,cp)
        require(sha256(cp/'freeze.json')==a['candidate_freezes'][name],'Uncommitted candidate')
        require(r['commitments']['observed.csv']==m['builder_observed']['sha256'],'Wrong visible input')
        require(stamp(r['created_utc'])<=t0,'Late candidate freeze')
        freeze_receipts[name]=r
    require(freeze_receipts['baseline']['parent'] is None,'Baseline has parent')
    parent=freeze_receipts['joint_evidence']['parent']
    require(parent['candidate']=='candidates/baseline' and parent['sha256']==a['candidate_freezes']['baseline'],'Wrong lineage')
    origin=read_json(e/'baseline_import.json')
    for name in ['generator.py','model_spec.json']:
        require(sha256(b/'candidates/baseline'/name)==origin['files'][name],'Baseline scientific change')
    expected={(v,s) for v in intent['variants'] for s in intent['source_seeds']}
    rows=m['source_replays'];source_times=[]
    require(len(rows)==len(expected) and {(x['variant'],x['seed']) for x in rows}==expected,'Wrong replay grid')
    for row in rows:
        name=row['variant'];seed=row['seed'];rid=f'{name}_{seed}'
        require(row['replay_id']==rid,'Wrong replay ID');ref(row,b/'source_replays'/rid/'replay.json')
        r=verify_source_replay(b,rid,candidate=b/'candidates'/name)
        require(r['status']=='success' and r['limits']['seed']==seed,'Failed replay')
        require(r['parent']['freeze.json_sha256']==a['candidate_freezes'][name],'Replay wrong candidate')
        require(stamp(r['created_utc'])>=t0,'Replay before schedule')
        for context in r['contexts']:
            require(context['generation_link_verified'] is True,'Unlinked replay')
            er=read_json(b/'source_replays'/rid/'contexts'/context['id']/'bundle/executions/replay/execution.json')
            require(stamp(er['created_utc'])>=t0,'Execution before commitment')
        source_times.append(stamp(r['created_utc']))
    expected={(v,s) for v in intent['variants'] for s in intent['target_seeds']}
    rows=m['outputs']
    require(len(rows)==len(expected) and {(x['variant'],x['seed']) for x in rows}==expected,'Wrong target grid')
    for row in rows:
        name=row['variant'];seed=row['seed'];rid=f'{name}_{seed}'
        require(row['run_id']==rid,'Wrong run ID');ref(row,b/'executions'/rid/'output/generated.csv')
        r=verify_execution(b,rid)
        require(r['status']=='success' and r['candidate']==f'candidates/{name}' and r['limits']['seed']==seed,'Wrong output execution')
        require(max(source_times)<=stamp(r['created_utc'])<=stamp(m['created_utc']),'Wrong chronology')
    return {'status':'passed','variants':len(intent['variants']),'source_replays':len(m['source_replays']),
        'target_outputs':len(rows),'target_outcomes_opened':False,
        'scope':'Integrity and execution linkage only; not scientific validity.'}
