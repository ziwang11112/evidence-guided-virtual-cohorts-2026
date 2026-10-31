"""M16 controller: commitments, frozen diagnostics and lineage; no target access or row generation."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import json
import shutil
import sys

R=Path(__file__).resolve().parent
P=R.parent.parent
sys.path.insert(0,str(P))
from cohort_harness.lifecycle import read_json,sha256,_registry,freeze_candidate,verify_candidate
from cohort_harness.contracts import validate_task,validate_evidence,validate_spec
from cohort_harness.__main__ import validate_bundle
from cohort_harness.source_checks import run_source_checks
from cohort_harness.execution import run_candidate,verify_execution
from cohort_harness.self_consistency import run_self_consistency,validate_self_consistency_spec

SCIENCE=('evidence.json','model_spec.json','audit/construction.json','audit/revision_plan.json')
BUILDERS=('b1','b2','b3')
STAGES=('initial','revision1','final')

def write_new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')

def check(condition,message):
    if not condition: raise ValueError(message)

def paths(bid,stage):
    check(bid in BUILDERS and stage in STAGES,'Unknown builder or stage')
    bundle=R/'visible'/bid/'bundle'
    return bundle,bundle/'candidates'/stage

def verify_inputs():
    pre=read_json(R/'prelaunch.json')
    for rel,h in pre['files'].items():
        p=(R/rel).resolve();check(p.is_relative_to(R),'Prelaunch path escapes run')
        check(sha256(p)==h,'Prelaunch input changed: '+rel)
    for absolute,h in pre['engine_files'].items():
        check(sha256(absolute)==h,'Engine changed: '+absolute)
    for bid,prefix in pre['registry_prefixes'].items():
        b,_=paths(bid,'initial');reg=read_json(b/'registry.json')
        check(reg['artifacts'][:len(prefix)]==prefix,'Seed registry changed')
        _registry(b)
    return sha256(R/'prelaunch.json')

def precommit(bid,stage):
    prehash=verify_inputs();b,c=paths(bid,stage)
    check(not (b/'candidates/final/freeze.json').exists(),'Builder already terminal')
    if stage=='revision1':
        check(not (R/'commitments'/bid/'final.json').exists(),'Final already committed')
    check(not (c/'generated.csv').exists(),'Rows exist before construction commitment')
    check(not (c/'freeze.json').exists(),'Candidate already frozen')
    task=read_json(b/'task.json');validate_task(task)
    ids=validate_evidence(read_json(c/'evidence.json'),task)
    spec=read_json(c/'model_spec.json');validate_spec(spec,ids)
    construction=read_json(c/'audit/construction.json')
    validate_self_consistency_spec(task,construction)
    check(spec['parameters'].get('construction')==construction,'Scientific and diagnostic construction differ')
    plan=read_json(c/'audit/revision_plan.json')
    check(plan['stage']==stage,'Plan stage mismatch')
    check(plan['action'] in {'initial','row_repair','model_revision','retain'},
          'A stop needs a separate failure/stop record, not a new candidate freeze')
    if stage=='initial':
        check(plan['parent_candidate'] is None and plan['action']=='initial','Initial lineage invalid')
    else:
        check(plan['action']!='initial','Noninitial stage cannot use initial action')
        parent=plan['parent_candidate']
        check(parent in {'initial','revision1'},'Invalid parent')
        check(stage=='final' or parent=='initial','Revision1 parent must be initial')
        if stage=='final' and (R/'commitments'/bid/'revision1.json').exists():
            check(parent=='revision1','Cannot bypass a committed revision1')
        _,pc=paths(bid,parent);verify_candidate(b,pc)
        f=R/'visible'/bid/'feedback'/f'{parent}.json'
        check(f.is_file(),'Actual parent feedback missing')
        if plan['action'] in {'row_repair','retain'}:
            check(sha256(c/'audit/construction.json')==sha256(pc/'audit/construction.json'),
                  'Row repair or retain cannot change construction')
            check(sha256(c/'model_spec.json')==sha256(pc/'model_spec.json'),
                  'Row repair or retain cannot change model')
    check(isinstance(plan['findings'],list) and bool(plan['reason'].strip()),'Decision record incomplete')
    source_plan=spec['parameters'].get('source_check_plan')
    check(isinstance(source_plan,list) and bool(source_plan),'Source check plan must be committed in model parameters')
    for item in source_plan:
        check(set(item)=={'id','evidence_id','status','operator','assumption_ids','reason'},'Source plan fields incorrect')
    check(len({item['id'] for item in source_plan})==len(source_plan),'Duplicate source plan IDs')
    for finding in plan['findings']:
        check(set(finding)=={'finding_id','possible_cause','observable_check','planned_action',
                            'expected_analysis_impact','unresolved_uncertainty'},'Finding fields incorrect')
    receipt={'schema_version':1,'builder':bid,'candidate':'candidates/'+stage,
             'created_utc':datetime.now(timezone.utc).isoformat(),'generated_exists':False,
             'prelaunch_sha256':prehash,'files':{s:sha256(c/s) for s in SCIENCE}}
    path=R/'commitments'/bid/(stage+'.json');write_new(path,receipt)
    target=c/'audit/preauthoring_commitment.json'
    check(not target.exists(),'Candidate commitment copy already exists')
    shutil.copyfile(path,target)
    print(json.dumps({'builder':bid,'stage':stage,'preauthoring_sha256':sha256(path),'rows_created':False}))

def verify_precommit(bid,stage):
    _,c=paths(bid,stage)
    path=R/'commitments'/bid/(stage+'.json');receipt=read_json(path)
    check(receipt['prelaunch_sha256']==verify_inputs(),'Prelaunch receipt binding changed')
    check(receipt['generated_exists'] is False,'Preauthoring chronology not established')
    check(receipt['candidate']=='candidates/'+stage and receipt['builder']==bid,'Receipt identity differs')
    check(sha256(path)==sha256(c/'audit/preauthoring_commitment.json'),'Commitment copy differs')
    for name,h in receipt['files'].items():check(sha256(c/name)==h,'Committed science changed: '+name)
    return receipt

def freeze(bid,stage):
    verify_precommit(bid,stage);b,c=paths(bid,stage)
    validate_bundle(b,c)
    source_plan=read_json(c/'model_spec.json')['parameters']['source_check_plan']
    checks=read_json(c/'source_checks.json')['checks']
    actual_plan=[{k:v for k,v in item.items() if k!='table'} for item in checks]
    check(actual_plan==source_plan,'Source check definitions differ from preauthoring plan')
    for item in checks:
        expected=None if item['status']=='not_computable' else {
            'path':'generated.csv','sha256':sha256(c/'generated.csv'),'origin':'agent_supplied_simulation'}
        check(item['table']==expected,'Source feedback must use the frozen authored table')
    check((c/'generated.csv').is_file() and not (c/'generator.py').exists(),'Literal table required')
    plan=read_json(c/'audit/revision_plan.json')
    if stage=='initial':
        result=freeze_candidate(b,c)
    else:
        parent=plan['parent_candidate'];_,pc=paths(bid,parent)
        feedback=R/'visible'/bid/'feedback'/f'{parent}.json'
        bound=c/'audit/parent_feedback.json'
        check(bound.is_file() and sha256(bound)==sha256(feedback),'Actual parent feedback not bound')
        artifacts=read_json(c/'checks.json')['artifacts']
        check(any(a['path']=='audit/parent_feedback.json' and a['sha256']==sha256(feedback) for a in artifacts),
              'Checks do not bind actual feedback')
        if plan['action']=='retain':
            for name in ('generated.csv','model_spec.json','evidence.json','audit/construction.json'):
                check(sha256(c/name)==sha256(pc/name),'Retain changed '+name)
        revision={'reason':plan['reason'],'kind':'retain' if plan['action']=='retain' else 'revise',
                  'addressed_findings':[str(x) for x in plan['findings']],
                  'remaining_limitations':['See committed decision plan and decision.md; source/self checks are not target validation.']}
        result=freeze_candidate(b,c,parent_receipt=pc/'freeze.json',revision=revision)
    verify_candidate(b,c)
    print(json.dumps({'builder':bid,'stage':stage,'freeze_sha256':sha256(c/'freeze.json'),
                      'table_sha256':sha256(c/'generated.csv'),'route':result['route']}))

def feedback(bid,stage):
    verify_precommit(bid,stage);b,c=paths(bid,stage);verify_candidate(b,c)
    check(stage=='final' or not (b/'candidates/final/freeze.json').exists(),
          'No further editing feedback after terminal freeze')
    slot={'initial':1,'revision1':2,'final':3}[stage]
    base=R/'visible'/bid/'feedback'
    base.mkdir(parents=True,exist_ok=True)
    marker=R/'feedback_reservations'/bid/(stage+'.json')
    write_new(marker,{'stage':stage,'slot':slot,'terminal':stage=='final',
                     'freeze_sha256':sha256(c/'freeze.json'),'created_utc':datetime.now(timezone.utc).isoformat()})
    runid=stage+'_direct_validation'
    execution=run_candidate(b,c,runid,0,runtime=None)
    check(execution['status']=='success' and execution['generator_executed'] is False,'Direct validation failed')
    verify_execution(b,runid)
    current=base/(stage+'_self_current.json')
    run_self_consistency(b/'task.json',b/'observed.csv',c/'generated.csv',c/'audit/construction.json',current)
    reports={'current':{'path':str(current),'sha256':sha256(current)}}
    if stage!='initial':
        original=base/(stage+'_self_original.json')
        run_self_consistency(b/'task.json',b/'observed.csv',c/'generated.csv',b/'candidates/initial/audit/construction.json',original)
        reports['original']={'path':str(original),'sha256':sha256(original)}
    sources=run_source_checks(b,c)
    result={'schema_version':1,'builder':bid,'candidate':stage,'slot':slot,'terminal':stage=='final',
            'scope':'source_and_own_construction_only','target_outcomes_read':False,
            'rows_created_or_changed':False,'freeze_sha256':sha256(c/'freeze.json'),
            'table_sha256':sha256(c/'generated.csv'),'self_reports':reports,'source_statistics':sources,
            'controller_sha256':sha256(Path(__file__)),
            'source_engine_sha256':sha256(P/'cohort_harness/source_checks.py'),
            'interpretation':'Self-consistency is not biological truth. Approximate source-population comparisons are not equality targets. No target answer is included.'}
    write_new(base/(stage+'.json'),result)
    verify_candidate(b,c);verify_inputs()
    print(json.dumps({'builder':bid,'stage':stage,'source_checks':len(sources['checks']),
                      'feedback_path':str(base/(stage+'.json')),'terminal':stage=='final'}))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['preflight','precommit','freeze','feedback'])
    parser.add_argument('--builder',choices=BUILDERS);parser.add_argument('--stage',choices=STAGES)
    args=parser.parse_args()
    if args.action=='preflight':print(json.dumps({'prelaunch_sha256':verify_inputs()}));return
    if args.builder is None or args.stage is None:parser.error('builder/stage required')
    try:
        globals()[args.action](args.builder,args.stage)
    except Exception as error:
        error_dir=R/'operational_failures'
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        write_new(error_dir/(stamp+'.json'),{'action':args.action,'builder':args.builder,
                  'stage':args.stage,'error_type':type(error).__name__,'message':str(error),
                  'retained_budget_reservations':True,'target_outcomes_read':False})
        raise

if __name__=='__main__':main()
