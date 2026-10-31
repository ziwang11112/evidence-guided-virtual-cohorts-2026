"""Small controller for two source-only integration runs; no scientific law."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import platform
import json
import numpy as np
import pandas as pd
from cohort_harness import lifecycle as life, execution as exe, whole_cohort_feedback as feedback
from cohort_harness.contracts import require
from cohort_harness.__main__ import validate_bundle

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
BUNDLE = ROOT / 'bundle'
SEED = 26301

def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n')

def preflight(stage):
    candidate = BUNDLE / 'candidates' / stage
    validate_bundle(BUNDLE, candidate)
    plan, _ = feedback._read_plan(candidate, life.read_json(BUNDLE / 'task.json'))
    seen = []
    for check in plan['checks']:
        op = check['operator']
        require(check['status'] == 'approximate', 'This fixture requires explicitly approximate checks')
        require(isinstance(op,dict) and set(op)=={'kind','unit','selection','missing_policy','column'}, 'Unexpected operator fields')
        require(op['missing_policy']=='error' and isinstance(op['selection'],list), 'Invalid selection/missing policy')
        require(all(isinstance(v,dict) and set(v)=={'column','op','value'} and type(v['value']) is int for v in op['selection']), 'Invalid filter fields or values')
        require(op is not None and op['kind'] in {'mean', 'sd'} and op['column'] == 'y' and op['unit'] == 'u', 'Wrong statistic')
        filters = {(v['column'], v['op'], v['value']) for v in op['selection']}
        require(len(op['selection']) == 2 and ('group', 'eq', 0) in filters, 'Wrong group selection')
        strata = [k for k in [0, 1, 2] if ('x', 'eq', k) in filters]
        require(len(strata) == 1, 'Wrong x stratum')
        seen.append((op['kind'], strata[0]))
    require(len(seen) == 6 and set(seen) == {(kind,k) for kind in ['mean','sd'] for k in [0,1,2]}, 'Six fixed checks required')
    return candidate

def verify_assembly():
    value = life.read_json(ROOT / 'ASSEMBLY.json')
    for path, digest in value['files'].items():
        require(life.sha256(Path(path)) == digest, 'Assembly changed: ' + path)
    life.verify_candidate(BUNDLE, 'candidates/initial')
    return value

def seal():
    require(not (BUNDLE/'executions').exists(), 'Cannot seal after execution')
    candidate = preflight('initial')
    life.freeze_candidate(BUNDLE, candidate)
    paths = [ROOT/x for x in ['CORE_METHOD_V0.md','INTEGRATION_PLAN.md','run_integration.py','prompts/initial.md','prompts/revision.md','prompts/LAUNCH_MESSAGES.json','ADMISSION.json']]
    paths += list((PROJECT/'cohort_harness').rglob('*.py'))
    paths += [PROJECT/x for x in ['skills/evidence-cohort-generation/SKILL.md','skills/evidence-cohort-generation/references/harness-interface.md','docs/SOURCE_CHECKS.md','docs/WHOLE_COHORT_FEEDBACK.md','docs/SOURCE_REPLAY.md']]
    paths += [Path('D:/Codex/home/skills/evidence-cohort-generation/SKILL.md')]
    paths += [BUNDLE/'task.json', BUNDLE/'registry.json', BUNDLE/'sources/fictional-study-a.txt']
    paths += [p for p in candidate.rglob('*') if p.is_file()]
    write_new(ROOT/'ASSEMBLY.json', {'version':'core_v0_program_whole_cohort_identity_feedback','created_utc':datetime.now(timezone.utc).isoformat(),'files':{str(p.resolve()):life.sha256(p) for p in paths},'schedule':[{'stage':s,'run_id':s+'_run','seed':SEED} for s in ['initial','final']],'max_executions':2,'runtime_configuration':exe.DEFAULT_RUNTIME,'host_versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},'worker_dependencies':'Captured by actual execution runtime_manifest.json; no historical runtime is asserted current','model_metadata':life.read_json(ROOT/'prompts/LAUNCH_MESSAGES.json')})
    return {'sealed':True,'assembly_sha256':life.sha256(ROOT/'ASSEMBLY.json')}

def final_submission():
    feedback.verify_feedback(BUNDLE, 'initial_feedback', candidate='candidates/initial', run_id='initial_run')
    initial=life.read_json(ROOT/'receipts/initial.json')
    require(initial['status']=='success' and initial['execution_sha256']==life.sha256(BUNDLE/'executions/initial_run/execution.json'), 'Initial execution record mismatch')
    require(initial['feedback_sha256']==life.sha256(BUNDLE/'whole_cohort_feedback/initial_feedback/feedback.json'), 'Initial feedback record mismatch')
    candidate = preflight('final')
    old = BUNDLE/'whole_cohort_feedback/initial_feedback/feedback.json'
    copy = candidate/'initial_source_feedback.json'
    require(copy.read_bytes()==old.read_bytes(), 'Feedback copy differs')
    checks = life.read_json(candidate/'checks.json')
    require({'path':'initial_source_feedback.json','sha256':life.sha256(old)} in checks['artifacts'], 'Authentic feedback must be bound')
    for name in ['evidence.json','whole_cohort_feedback.json']:
        require((candidate/name).read_bytes()==(BUNDLE/'candidates/initial'/name).read_bytes(), 'Source evidence/checks changed')
    revision = life.read_json(ROOT/'revision.json')
    return candidate,revision

def final_freeze():
    verify_assembly()
    candidate,revision=final_submission()
    life.freeze_candidate(BUNDLE,candidate,parent_receipt='candidates/initial/freeze.json',revision=revision)
    return {'final_frozen':True,'decision':revision['kind']}

def run(stage):
    verify_assembly()
    if stage == 'final':
        require((ROOT/'receipts/initial.json').exists(), 'Initial stage must complete first')
        candidate,revision=final_submission()
        frozen=life.verify_candidate(BUNDLE,candidate)
        require(frozen['parent']=={'candidate':'candidates/initial','receipt_path':'candidates/initial/freeze.json','sha256':life.sha256(BUNDLE/'candidates/initial/freeze.json')}, 'Final parent mismatch')
        require(frozen['revision']==revision, 'Final decision differs from frozen record')
    require(not (ROOT/'STOP.json').exists(), 'Previous failure closed this integration')
    require(not (ROOT/('started_'+stage+'.json')).exists(), 'Stage already started; no retries')
    require(len(list((BUNDLE/'executions').glob('*/execution.json'))) < 2, 'Execution ceiling reached')
    preflight(stage); life.verify_candidate(BUNDLE,'candidates/'+stage)
    write_new(ROOT/('started_'+stage+'.json'),{'stage':stage,'seed':SEED,'created_utc':datetime.now(timezone.utc).isoformat()})
    try:
        exe.run_candidate(BUNDLE,'candidates/'+stage,stage+'_run',SEED)
        receipt = exe.verify_execution(BUNDLE,stage+'_run')
        require(receipt['status']=='success','Execution failed')
        frame = life.read_table(BUNDLE/f'executions/{stage}_run/output/generated.csv',life.read_json(BUNDLE/'task.json'),output=True)
        require(frame.groupby('x').size().to_dict()=={0:256,1:256,2:256},'Quota mismatch')
        report = feedback.collect_feedback(BUNDLE,'candidates/'+stage,stage+'_run',stage+'_feedback')
        feedback.verify_feedback(BUNDLE,stage+'_feedback',candidate='candidates/'+stage,run_id=stage+'_run')
        value={'status':'success','stage':stage,'run_id':stage+'_run','execution_sha256':life.sha256(BUNDLE/f'executions/{stage}_run/execution.json'),'feedback_sha256':life.sha256(BUNDLE/f'whole_cohort_feedback/{stage}_feedback/feedback.json'),'checks':len(report['checks'])}
        write_new(ROOT/f'receipts/{stage}.json',value)
        return value
    except Exception as error:
        value={'status':'closed_failure','stage':stage,'error':str(error),'type':type(error).__name__,'retry_permitted':False}
        write_new(ROOT/'STOP.json',value)
        raise

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['seal','initial','final-freeze','final']); args=parser.parse_args()
    value=seal() if args.action=='seal' else final_freeze() if args.action=='final-freeze' else run(args.action)
    print(json.dumps(value))
