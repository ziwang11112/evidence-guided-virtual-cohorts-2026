"""Fixed source replay and sealed-target schedule; no scientific parameter fitting."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
B = Path(json.loads((E / 'execution_location.json').read_text())['bundle'])
OLD = P / 'work/analysis-evidence-gap-2026-10-29'
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import read_json, sha256, verify_candidate
from cohort_harness.execution import verify_execution
from cohort_harness.source_replay import verify_source_replay
from cohort_harness.source_portfolio import summarize_source_portfolio

def now():
    return datetime.now(timezone.utc).isoformat()

def new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')

def reference(path):
    return {'path': str(path.resolve()), 'sha256': sha256(path)}

def anchors():
    a = read_json(E / 'protocol_commitment.json')
    for rel, h in a['files'].items():
        if sha256(E / rel) != h:
            raise ValueError('Changed protocol file: ' + rel)
    for rel, h in a['core_files'].items():
        if sha256(P / rel) != h:
            raise ValueError('Changed harness: ' + rel)
    if sha256(P / 'work/m2-runtime-config.json') != a['runtime_config_sha256']:
        raise ValueError('Runtime changed')
    if sha256(OLD / 'custodian/custodian_lock.json') != a['custodian_lock_sha256']:
        raise ValueError('Custody changed')
    for name, h in a['candidate_freezes'].items():
        verify_candidate(B, B / 'candidates' / name)
        if sha256(B / 'candidates' / name / 'freeze.json') != h:
            raise ValueError('Candidate changed')
    return a, read_json(E / 'pilot_intent.json')

def freeze_protocol():
    p = read_json(E / 'pilot_intent.json')
    new(E / 'evaluation_design.json', {
        'variants': p['variants'], 'seeds': p['target_seeds'],
        'interpretation': p['scope'],
        'primary_uses': p['primary_uses'], 'secondary_uses': p['secondary_uses'],
        'post_evaluation_revision_allowed': False,
        'no_winner_selection': True})
    freezes = {}
    for name in p['variants']:
        cp = B / 'candidates' / name
        verify_candidate(B, cp)
        freezes[name] = sha256(cp / 'freeze.json')
    files = ['pilot_intent.json','baseline_import.json','pre_execution_review.json',
             'review/CANDIDATE_AUDIT.json','review/CANDIDATE_AUDIT.md','controller.py','release_guard.py',
             'evaluation_design.json','evaluation/protocol_amendment.json',
             'evaluation/analysis_protocol.json','evaluation/evaluate_committed.py',
             'evaluation/survey_analysis.py']
    new(E / 'protocol_commitment.json', {
        'created_utc': now(), 'files': {r: sha256(E/r) for r in files},
        'core_files': {r.relative_to(P).as_posix():sha256(r) for r in sorted((P/'cohort_harness').glob('*.py'))},
        'candidate_freezes': freezes,
        'runtime_config_sha256': sha256(P/'work/m2-runtime-config.json'),
        'custodian_lock_sha256': sha256(OLD/'custodian/custodian_lock.json'),
        'scope': 'Candidate, seed and evaluator commitments before source/target generation and target release.'})
    print('protocol committed', flush=True)

def call(label, args):
    log = E / 'controller_logs' / ('attempt2_' + label + '.json')
    if log.exists():
        raise ValueError('Existing attempt retained: ' + label)
    start = now()
    result = subprocess.run([sys.executable,'-B','-m','cohort_harness',*args],
        cwd=P, capture_output=True, text=True, encoding='utf-8', errors='replace')
    new(log, {'started_utc':start,'ended_utc':now(),'arguments':args,
              'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode:
        raise RuntimeError('Failed attempt retained: ' + label)
    print('completed',label,flush=True)

def source():
    _, p = anchors()
    for name in p['variants']:
        ids=[]
        for seed in p['source_seeds']:
            rid=f'{name}_{seed}'; ids.append(rid)
            call(rid,['source-replay','--bundle',str(B),'--candidate',name,
                '--replay-id',rid,'--seed',str(seed),'--runtime',str(P/'work/m2-runtime-config.json'),
                '--timeout-seconds','60'])
        summary=summarize_source_portfolio(B,B/'candidates'/name,ids,p['source_seeds'])
        new(E/'source_feedback'/f'{name}_portfolio.json',summary)

def source_refs(p):
    rows=[]
    for name in p['variants']:
        for seed in p['source_seeds']:
            rid=f'{name}_{seed}'
            r=verify_source_replay(B,rid,candidate=B/'candidates'/name)
            if r['status']!='success' or r['limits']['seed']!=seed:
                raise ValueError('Invalid replay')
            rows.append({'variant':name,'seed':seed,'replay_id':rid,
                         **reference(B/'source_replays'/rid/'replay.json')})
    return rows

def target():
    _, p=anchors(); source_refs(p)
    for name in p['variants']:
        for seed in p['target_seeds']:
            rid=f'{name}_{seed}'
            call(rid,['execute','--bundle',str(B),'--candidate',name,'--run-id',rid,
                '--seed',str(seed),'--runtime',str(P/'work/m2-runtime-config.json'),
                '--timeout-seconds','60'])
            if verify_execution(B,rid)['status']!='success':
                raise ValueError('Failed target generation')

def release():
    a,p=anchors(); sources=source_refs(p)
    candidates=[]; outputs=[]
    for name in p['variants']:
        for stage in ('initial','final'):
            candidates.append({'variant':name,'stage':stage,
                **reference(B/'candidates'/name/'freeze.json')})
        for seed in p['target_seeds']:
            rid=f'{name}_{seed}'; r=verify_execution(B,rid)
            if r['status']!='success' or r['candidate']!=f'candidates/{name}' or r['limits']['seed']!=seed:
                raise ValueError('Wrong execution')
            outputs.append({'variant':name,'seed':seed,'run_id':rid,
                **reference(B/'executions'/rid/'output/generated.csv')})
    manifest={'created_utc':now(),'authorize_target_evaluation':True,
        'all_candidates_and_seeds_committed':True,
        'custodian_lock_sha256':a['custodian_lock_sha256'],
        'evaluation_design':reference(E/'evaluation_design.json'),
        'evaluation_amendment':reference(E/'evaluation/protocol_amendment.json'),
        'candidate_commitments':candidates,'outputs':outputs,'source_replays':sources,
        'builder_observed':reference(B/'observed.csv'),
        'controller_guard':{**reference(E/'release_guard.py'),'function':'verify_release'},
        'post_evaluation_builder_revision_allowed':False}
    path=E/'evaluation_commitment.json';new(path,manifest)
    from release_guard import verify_release
    new(E/'release_verification.json',verify_release(path))
    print('release commitment verified; target outcomes not yet parsed',flush=True)

if __name__=='__main__':
    {'freeze_protocol':freeze_protocol,'source':source,'target':target,'release':release}[sys.argv[1]]()
