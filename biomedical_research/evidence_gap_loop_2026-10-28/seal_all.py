"""Bind all scheduled artifacts before authorizing the separate evaluator.

Only hashes and manifests are read here, not true HDL values or analyses.
"""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
RUNS = {'ordinary_1':'ordinary', 'ordinary_2':'ordinary', 'gap_1':'gap_policy', 'gap_2':'gap_policy'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    release_path = ROOT/'custodian/evaluation_release.json'
    if release_path.exists() or (ROOT/'all_outputs_freeze.json').exists():
        raise RuntimeError('Preserve existing global freeze/release')
    artifacts, outputs = {}, []

    def bind(path, expected=None):
        p = Path(path)
        if not p.is_absolute(): p = ROOT/p
        p = p.resolve()
        if not p.is_relative_to(ROOT): raise ValueError('Artifact outside pilot')
        value = sha(p)
        if expected is not None and value != expected: raise ValueError('Changed artifact: '+str(p))
        key = p.relative_to(ROOT).as_posix()
        if key in artifacts and artifacts[key] != value: raise ValueError('Conflicting artifact commitment')
        artifacts[key] = value
        return key

    for receipt in ['framework_freeze.json','pre_evaluation_plan_freeze.json']:
        bind(receipt)
        for p,h in read(ROOT/receipt)['files'].items(): bind(p,h)
    bind(__file__)
    seeds = read(ROOT/'protocol.json')['generation_seeds']
    for name, arm in RUNS.items():
        run = ROOT/'runs'/name
        cfg = read(run/'run.json')
        if cfg['policy'] != arm: raise ValueError('Arm mismatch')
        bind(run/'run.json')
        for p,h in cfg['commitment'].items(): bind(p,h)
        bind(run/'review_receipt.json')
        review = read(run/'review_receipt.json')
        if not review['execution_allowed']: raise ValueError('Initial code not approved')
        for p,h in review['commitment'].items(): bind(p,h)
        bind(run/'final_code_review.json')
        if not read(run/'final_code_review.json')['execution_allowed']: raise ValueError('Final code not approved')
        for stage in ['initial','final']:
            candidate = run/stage
            bind(candidate/'freeze.json')
            frozen = read(candidate/'freeze.json')
            for p,h in frozen['commitment'].items(): bind(p,h)
            bind(candidate/'artificial_checks.json')
            bind(candidate/'outputs/execution.json')
            execution = read(candidate/'outputs/execution.json')
            if execution['candidate_freeze_sha256'] != sha(candidate/'freeze.json'): raise ValueError('Execution/freeze mismatch')
            draws = execution['draws']
            if [d['seed'] for d in draws] != seeds: raise ValueError('Seed schedule mismatch')
            for index, item in enumerate(draws, 1):
                relative = bind(item['path'], item['sha256'])
                outputs.append({'construction':name,'arm':arm,'stage':stage,'draw':index,
                    'seed':item['seed'],'file':relative,'sha256':item['sha256']})
    if len(outputs) != 40 or len({o['file'] for o in outputs}) != 40:
        raise ValueError('Incomplete or duplicate output paths')
    contract = read(ROOT/'custodian/evaluation_release_contract.json')
    bind(ROOT/'custodian/analysis_spec.json',contract['analysis_spec_sha256'])
    bind(ROOT/'custodian/evaluate.py',contract['evaluator_sha256'])
    timestamp = datetime.now(timezone.utc).isoformat()
    frozen = {'created_utc':timestamp, 'artifacts':artifacts,'outputs':outputs,
        'target_results_read_by_sealer':False,'scope':'All scheduled initial/final outputs; hashes only'}
    with (ROOT/'all_outputs_freeze.json').open('x',encoding='utf-8') as f:
        json.dump(frozen,f,indent=2,allow_nan=False)
    release = {'created_utc':timestamp,'all_four_constructions_frozen':True,
        'root_authorized_evaluation':True,'no_builder_access_to_target':True,
        'blinding_basis':'Procedural file scopes, fresh builder contexts, screened source interface and builder compliance attestations; not an OS sandbox or proof of absent pretrained knowledge.',
        'analysis_spec_sha256':contract['analysis_spec_sha256'],'evaluator_sha256':contract['evaluator_sha256'],
        'artifacts':artifacts,'outputs':outputs,'all_outputs_freeze_sha256':sha(ROOT/'all_outputs_freeze.json')}
    with release_path.open('x',encoding='utf-8') as f: json.dump(release,f,indent=2,allow_nan=False)
    print(json.dumps({'outputs_frozen':len(outputs),'artifacts_bound':len(artifacts),
        'release_sha256':sha(release_path),'note':'Custodian independently validates before reading target outcomes.'}))


if __name__ == '__main__': main()
