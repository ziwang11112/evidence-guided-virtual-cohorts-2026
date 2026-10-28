"""Bind all prescheduled outputs and provenance before reading target analyses."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_new(path, obj):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False)
        f.write('\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',action='append',required=True,help='model_label=execution_directory')
    p.add_argument('--provenance',nargs='+',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    out=Path(args.output).resolve()
    if out.exists(): raise FileExistsError('Preserve existing freeze')
    paths=[ROOT/'PROTOCOL.md',ROOT/'run_generation.py',ROOT/'seal_experiment.py',
           ROOT/'literature_gateway.py',ROOT/'shared/observed.csv',ROOT/'shared/schema.json',
           ROOT/'shared/target_description.md',ROOT/'review/frozen_analysis.json',
           ROOT/'review/analysis_spec.json',ROOT/'review/evaluate.py',
           ROOT/'custodian/locked/freeze_manifest.json',
           ROOT/'custodian/locked/evaluator_adapter_manifest.json']
    paths.extend(Path(x).resolve() for x in args.provenance)
    draws=[]; labels=set()
    for value in args.run:
        label, directory=value.split('=',1)
        if label in labels: raise ValueError('Repeated model label')
        labels.add(label)
        directory=Path(directory).resolve()
        execution=read(directory/'execution.json')
        if not execution['all_contract_checks_pass'] or len(execution['draws'])!=20:
            raise ValueError('Need every prescheduled output for each model')
        if sorted(d['seed'] for d in execution['draws'])!=list(range(270101,270121)):
            raise ValueError('Seed schedule mismatch')
        for path, expected in execution['input_files'].items():
            if sha(path)!=expected: raise ValueError('Committed input changed: '+path)
            paths.append(Path(path))
        paths.extend([directory/'execution.json',directory/'pre_execution.json'])
        for draw in execution['draws']:
            if sha(draw['path'])!=draw['sha256']: raise ValueError('Draw changed')
            draws.append({'model':label,**draw})
            paths.append(Path(draw['path']))
    reference=ROOT/'custodian/locked/evaluator_reference.csv'
    spine=ROOT/'custodian/locked/evaluator_design_spine.csv'
    spec=ROOT/'review/frozen_analysis.json'
    frozen_spec=read(spec)
    if sha(ROOT/'review/evaluate.py')!=frozen_spec['evaluator_sha256']:
        raise ValueError('Frozen evaluator changed')
    if sha(ROOT/'review/analysis_spec.json')!=frozen_spec['base_spec_sha256']:
        raise ValueError('Frozen base specification changed')
    if sha(ROOT/'shared/observed.csv')!=frozen_spec['observed_sha256']:
        raise ValueError('Observed input changed')
    paths.extend([reference,spine])
    commitments={str(path.resolve()):sha(path) for path in sorted(set(paths))}
    out.mkdir(parents=True)
    freeze_path=out/'outputs_freeze.json'
    write_new(freeze_path,{'created_utc':datetime.now(timezone.utc).isoformat(),
               'stage':'All generated outputs and analyses bound before target evaluation',
               'true_outcome_analyses_opened':False,'files':commitments,
               'model_labels':sorted(labels),'draw_count':len(draws)})
    manifest={'created_utc':datetime.now(timezone.utc).isoformat(),
              'analysis_spec':{'path':str(spec),'sha256':sha(spec)},
              'observed_sha256':sha(ROOT/'shared/observed.csv'),
              'reference_sha256':sha(reference),'spine_sha256':sha(spine),
              'outputs_freeze':{'path':str(freeze_path),'sha256':sha(freeze_path)},'draws':draws}
    write_new(out/'evaluation_manifest.json',manifest)
    print(json.dumps({'output':str(out),'models':sorted(labels),'draws':len(draws),
                     'outputs_freeze_sha256':sha(freeze_path)},indent=2))


if __name__=='__main__': main()
