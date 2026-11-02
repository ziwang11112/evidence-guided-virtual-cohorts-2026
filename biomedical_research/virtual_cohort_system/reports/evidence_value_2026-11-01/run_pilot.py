"""Bounded execution of four already-reviewed Agent programs; no scientific law."""
from pathlib import Path
import json
from datetime import datetime, timezone
from cohort_harness import lifecycle as life, execution as exe
from cohort_harness.__main__ import validate_bundle

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
ARMS = ('A','B','C','D')
SEEDS = (18101,18103,18107)

def write_new(path, value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write('\n')

def candidate_files(path):
    return {q.relative_to(path).as_posix():life.sha256(q) for q in sorted(path.rglob('*')) if q.is_file() and '__pycache__' not in q.parts}

def seal():
    assert not (ROOT/'FREEZE_MANIFEST.json').exists()
    admission=life.read_json(ROOT/'review/ADMISSION.json')
    assert admission['decision']=='approved'
    for relative,digest in admission['commitments'].items():
        assert life.sha256(ROOT/relative)==digest, relative
    engine={q.relative_to(PROJECT).as_posix():life.sha256(q) for q in sorted((PROJECT/'cohort_harness').glob('*.py'))}
    assert admission['engine_files']==engine
    frozen={}
    for arm in ARMS:
        bundle=ROOT/'bundles'/arm; candidate=bundle/'candidates/initial'
        assert not (bundle/'executions').exists()
        review=life.read_json(ROOT/'review'/f'{arm}_CANDIDATE.json')
        assert review['decision']=='approved'
        assert review['independent'] is True and review['reviewer_id'] != review['builder_id']
        assert review['candidate_files']==candidate_files(candidate)
        assert (candidate/'evidence.json').read_bytes()==(bundle/'evidence.json').read_bytes()
        task=life.read_json(bundle/'task.json')
        assert task['mode']=='whole_cohort' and task['n_rows']==3000 and task['budget']['revisions']==0
        assert validate_bundle(bundle,candidate)['route']=='program'
        if not (candidate/'freeze.json').exists():
            life.freeze_candidate(bundle,candidate)
        frozen[arm]=life.sha256(candidate/'freeze.json')
    bindings={'run_pilot.py':life.sha256(__file__),'PROTOCOL.md':life.sha256(ROOT/'PROTOCOL.md'),
              'review/ADMISSION.json':life.sha256(ROOT/'review/ADMISSION.json')}
    bindings.update(admission['commitments'])
    for arm in ARMS:
        name=f'review/{arm}_CANDIDATE.json';bindings[name]=life.sha256(ROOT/name)
    write_new(ROOT/'FREEZE_MANIFEST.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),files=bindings,engine_files=engine,candidate_freezes=frozen,seeds=list(SEEDS),maximum_tables=12))

def verify():
    manifest=life.read_json(ROOT/'FREEZE_MANIFEST.json')
    assert manifest['seeds']==list(SEEDS) and manifest['maximum_tables']==12
    for relative,digest in manifest['files'].items():
        assert life.sha256(ROOT/relative)==digest, relative
    for relative,digest in manifest['engine_files'].items():
        assert life.sha256(PROJECT/relative)==digest, relative
    for arm,digest in manifest['candidate_freezes'].items():
        bundle=ROOT/'bundles'/arm
        life.verify_candidate(bundle,'candidates/initial')
        assert life.sha256(bundle/'candidates/initial/freeze.json')==digest
    return manifest

def run():
    verify()
    write_new(ROOT/'EXECUTION_STARTED.json',dict(freeze_sha256=life.sha256(ROOT/'FREEZE_MANIFEST.json'),created_utc=datetime.now(timezone.utc).isoformat(),reserved_table_slots=12,schedule=[{'arm':a,'seed':s} for a in ARMS for s in SEEDS]))
    receipts=ROOT/'receipts';receipts.mkdir(exist_ok=False)
    rows=[]
    for arm in ARMS:
        bundle=ROOT/'bundles'/arm
        for seed in SEEDS:
            verify()
            run_id=f's{seed}'
            write_new(receipts/f'{arm}_{seed}_attempt.json',dict(arm=arm,seed=seed,run_id=run_id,freeze_sha256=life.sha256(ROOT/'FREEZE_MANIFEST.json')))
            try:
                receipt=exe.run_candidate(bundle,'candidates/initial',run_id,seed,timeout_seconds=60,memory_mb=1024)
                exe.verify_execution(bundle,run_id)
                out=bundle/'executions'/run_id/'output/generated.csv'
                row=dict(arm=arm,seed=seed,status=receipt['status'],execution_sha256=life.sha256(bundle/'executions'/run_id/'execution.json'),generated_sha256=life.sha256(out) if receipt['status']=='success' else None,elapsed_seconds=receipt.get('elapsed_seconds'),error=receipt.get('error'))
            except Exception as error:
                row=dict(arm=arm,seed=seed,status='failed',error={'type':type(error).__name__,'message':str(error)})
            rows.append(row)
            write_new(receipts/f'{arm}_{seed}_result.json',row)
    write_new(ROOT/'OUTPUTS.json',dict(freeze_sha256=life.sha256(ROOT/'FREEZE_MANIFEST.json'),slots=rows))
    return {'slots':len(rows),'successful':sum(r['status']=='success' for r in rows),'evaluation':'not_started'}
