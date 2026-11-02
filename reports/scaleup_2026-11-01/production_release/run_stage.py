"""One nonretryable released stage. Output reports execution status, never effects."""
from pathlib import Path
import argparse
import json
import sys

HERE=Path(__file__).resolve().parent
SCALE=HERE.parent
PROJECT=SCALE.parents[1]
WORKSPACE=PROJECT.parents[1]
for directory in (PROJECT,SCALE/'production_integration',SCALE/'production_integration/campaign_control',SCALE/'production_integration/k01_sources',HERE/'runtime'):
    sys.path.insert(0,str(directory))
import campaign_control as control
import case_execution
import k01_sources
import runtime_check

def run(case,constructor,stage):
    ledger=control.CampaignLedger.open(WORKSPACE/'evcA/ledger')
    expected={'path':str(Path(__file__).resolve()),'sha256':control._file_hash(Path(__file__))}
    if expected not in ledger.manifest['artifacts']:
        raise ValueError('Actual stage entry is not release-bound')
    identity=runtime_check.verify()
    # A durable intent prevents replay even when process dispatch is interrupted.
    intent=ledger.begin_bridge(case,constructor,stage)
    bundle=WORKSPACE/'evcA'/case/constructor
    error=None
    try:
        guards=case_execution.execute_case_stage(bundle,stage,WORKSPACE/'evcA/ledger',case,constructor,stage)
        if case=='K01':
            for trial in guards['trials']:
                if trial['role']=='source' and trial['guard_status']=='valid' and trial['trial_status']=='success':
                    k01_sources.collect_descriptives(bundle,stage,trial['trial_id'])
    except Exception as exc:
        error=type(exc).__name__
    finally:
        event=ledger.finish_bridge(case,constructor,stage)
    result=event['payload']
    verified=result['verified']
    summary={'case':case,'constructor':constructor,'stage':stage,'runtime':identity,
        'intent_sha256':intent['event_sha256'],'completion_sha256':event['event_sha256'],
        'status':result['status'],'call_error_type':error,'verification_error_type':result['error_type'],
        'trial_statuses':[] if verified is None else [
            {k:item[k] for k in ('trial_id','context_id','role','guard_status','trial_status')}
            for item in verified['guards']['trials']],
        'target_effects_computed':False}
    folder=HERE/'execution_status';folder.mkdir(exist_ok=True)
    with (folder/f'{case}_{constructor}_{stage}.json').open('x',encoding='utf-8',newline='\n') as handle:
        json.dump(summary,handle,indent=2);handle.write('\n')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('case',choices=control.CASES)
    parser.add_argument('constructor',choices=control.CONSTRUCTORS)
    parser.add_argument('stage',choices=control.STAGES)
    args=parser.parse_args()
    print(json.dumps(run(args.case,args.constructor,args.stage),indent=2))
