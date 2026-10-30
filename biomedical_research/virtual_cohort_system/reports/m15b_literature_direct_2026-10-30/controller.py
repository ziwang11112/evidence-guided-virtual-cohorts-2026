"""M15-B1 source-only lifecycle helper. Never creates/repairs rows or reads target outcomes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import sys

RUN = Path(__file__).resolve().parent
PROJECT = RUN.parent.parent
sys.path.insert(0, str(PROJECT))
from cohort_harness.lifecycle import read_json, sha256, verify_candidate, _registry
from cohort_harness.__main__ import validate_bundle
from cohort_harness.execution import run_candidate, verify_execution
from cohort_harness.source_checks import run_source_checks

BUNDLE = RUN/'visible/bundle'


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def verify_inputs():
    commit = read_json(RUN/'private/prelaunch_commitment.json')
    for name, expected in commit['files'].items():
        if sha256(RUN/name) != expected:
            raise ValueError('Prelaunch input changed: '+name)
    registry = read_json(BUNDLE/'registry.json')
    prefix = commit['registry_initial_prefix']
    if registry['artifacts'][:len(prefix)] != prefix:
        raise ValueError('Initial source registry prefix changed')
    _registry(BUNDLE)
    return sha256(RUN/'private/prelaunch_commitment.json')


def candidate(name):
    if name not in {'initial','revision1','final'}:
        raise ValueError('Unknown scheduled candidate name')
    return BUNDLE/'candidates'/name


def source_feedback(name, slot):
    commitment = verify_inputs()
    if slot not in (1,2):
        raise ValueError('At most two source-feedback passes')
    c = candidate(name)
    validate_bundle(BUNDLE,c)
    receipt = verify_candidate(BUNDLE,c)
    if receipt['route'] != 'generated.csv':
        raise ValueError('This task requires direct authored rows')
    prior = RUN/f'private/feedback_pass_{slot-1}.json'
    if slot==2 and not prior.is_file():
        raise ValueError('Second pass requires recorded first pass')
    marker = RUN/f'private/feedback_pass_{slot}.json'
    write_new(marker, {'slot':slot,'candidate':name,'utc':datetime.now(timezone.utc).isoformat(),
                       'freeze_sha256':sha256(c/'freeze.json'),'prelaunch_sha256':commitment,
                       'meaning':'Pass reserved before calculation; failure does not reset budget.'})
    execution = run_candidate(BUNDLE,c,f'{name}_direct_validation_{slot}',0,runtime=None)
    if execution['status']!='success' or execution['generator_executed'] is not False:
        raise ValueError('Direct-row validation failed; see retained execution receipt')
    verify_execution(BUNDLE,f'{name}_direct_validation_{slot}')
    if not (c/'source_checks.json').is_file():
        raise ValueError('Reviewed source-check definitions are required before feedback')
    report = run_source_checks(BUNDLE,c)
    output = {'schema_version':1,'scope':'source_only_feedback_no_target_results','slot':slot,
              'candidate':name,'freeze_sha256':sha256(c/'freeze.json'),
              'table_sha256':sha256(c/'generated.csv'),'controller_sha256':sha256(Path(__file__)),
              'source_operator_sha256':sha256(PROJECT/'cohort_harness/source_checks.py'),
              'prelaunch_sha256':commitment,'direct_validation_run':f'{name}_direct_validation_{slot}',
              'generator_executed':False,'source_statistics':report,
              'interpretation':'Target-shaped table checks are declared approximate transport diagnostics where source contexts differ; no true target outcome or validity score is supplied. Every reported source value must be an admitted evidence item.'}
    path=RUN/f'visible/feedback/{name}_feedback.json'
    write_new(path,output)
    verify_candidate(BUNDLE,c)
    verify_inputs()
    print(json.dumps({'feedback_path':str(path),'source_check_count':len(report['checks']),
                      'slot':slot,'target_outcomes_read':False,'rows_created_or_changed':False}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['preflight','source-feedback'])
    parser.add_argument('--candidate',choices=['initial','revision1','final'])
    parser.add_argument('--slot',type=int)
    args=parser.parse_args()
    if args.action=='preflight':
        print(json.dumps({'prelaunch_verified':verify_inputs(),'target_outcomes_read':False}))
    else:
        if args.candidate is None or args.slot is None:
            parser.error('source-feedback requires candidate and slot')
        source_feedback(args.candidate,args.slot)


if __name__=='__main__':
    main()
