"""Bounded M13-B deployment: no target outcomes are read by this controller."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.lifecycle import freeze_candidate, verify_candidate, sha256
from cohort_harness.execution import run_candidate, verify_execution

SEEDS = [33101, 33102, 33103]
INPUTS = ['id','age','bmi','male','asian','inv_bmi','male_inv_bmi','asian_inv_bmi','male_age','asian_age']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def identities():
    result = []
    for builder in ['build01','build02']:
        bundle = PROJECT/'work/m13'/builder
        for name in ['initial','source_reviewed']:
            verify_candidate(bundle, f'candidates/{name}')
            directory = bundle/'candidates'/name
            result.append({'builder':builder, 'candidate':name,
                           'source_bundle':str(bundle),
                           'generator_sha256':sha256(directory/'generator.py'),
                           'spec_sha256':sha256(directory/'model_spec.json'),
                           'source_freeze_sha256':sha256(directory/'freeze.json')})
    return result


def initialize():
    models = identities()
    tables = []
    for model in models:
        for seed in SEEDS:
            tables.append({'table_id':f"{model['builder']}_{model['candidate']}_{seed}",
                           'kind':'agent','builder':model['builder'],
                           'candidate':model['candidate'],'seed':seed})
    tables.append({'table_id':'gallagher_mean','kind':'reference_deterministic',
                   'builder':'published_reference','candidate':'gallagher_mean','seed':None})
    for seed in SEEDS:
        tables.append({'table_id':f'gallagher_normal_{seed}','kind':'reference_stochastic',
                       'builder':'published_reference','candidate':'gallagher_normal','seed':seed})
    write_new(ROOT/'protocol.json', {'schema_version':1, 'case_id':'m13b_bodyfat_j',
              'target':'NHANES2017-18_DXDTOPF', 'seeds':SEEDS,'models':models,'tables':tables,
              'observed_columns':INPUTS,'generated_column':'bodyfat',
              'protocol_path':'PROTOCOL.md','proposed_reference':'../m13/protocol_review.md',
              'primary_bmi':[18.5,30],'primary_upper_inclusive':False,
              'extension_bmi':[30,35],'quantile_intervals':False,
              'rule':'No model/covariate/domain/analysis changes after target acquisition'})


def verify_preaccess():
    frozen = read(ROOT/'preaccess_freeze.json')
    for relative, digest in frozen['files'].items():
        if sha256(ROOT/relative) != digest:
            raise ValueError(f'Preaccess commitment changed: {relative}')
    protocol = read(ROOT/'protocol.json')
    if identities() != protocol['models']:
        raise ValueError('Original scientific candidate identity changed')
    return frozen, protocol


def freeze():
    # Custody authorisation is a separate explicit controller action after audit.
    paths = ['PROTOCOL.md','protocol.json','controller.py','test_controller.py']
    for folder in ['evaluator','custodian','audits']:
        paths += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/folder).glob('*'))
                  if p.is_file() and p.suffix in {'.py','.md','.json','.csv'}
                  and '__pycache__' not in p.parts and 'private' not in p.parts]
    if not any(p.startswith('audits/') for p in paths):
        raise ValueError('Independent preaccess audit required')
    identities()
    write_new(ROOT/'preaccess_freeze.json', {
        'schema_version':1, 'phase':'before_target_acquisition',
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'files':{p:sha256(ROOT/p) for p in sorted(set(paths))},
        'scientific_revision_allowed':False,
        'note':'Procedural integrity record, not an OS boundary or external timestamp attestation'})


def load_observed(path):
    observed = pd.read_csv(path, dtype={'id':str}, float_precision='round_trip')
    if list(observed.columns) != INPUTS or not observed.id.is_unique or observed.id.isna().any():
        raise ValueError('Observed whitelist or key violation')
    numeric = observed[INPUTS[1:]].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError('Nonfinite permitted input')
    if not observed.asian.eq(0).all() or not observed.male.isin([0,1]).all():
        raise ValueError('Invalid categorical input')
    if not observed.age.between(20,59).all() or not observed.bmi.between(18.5,35).all():
        raise ValueError('Target outside frozen input domain')
    expected = {'inv_bmi':1/observed.bmi,'male_inv_bmi':observed.male/observed.bmi,
                'asian_inv_bmi':observed.asian/observed.bmi,
                'male_age':observed.male*observed.age,'asian_age':observed.asian*observed.age}
    for column, values in expected.items():
        if not np.allclose(observed[column], values, atol=1e-14, rtol=1e-14):
            raise ValueError(f'Invalid deterministic covariate {column}')
    return observed


def deploy(observed_path):
    frozen, protocol = verify_preaccess()
    observed_path = Path(observed_path).resolve()
    observed = load_observed(observed_path)
    manifest = {'preaccess_sha256':sha256(ROOT/'preaccess_freeze.json'),
                'observed_path':str(observed_path),'observed_sha256':sha256(observed_path),
                'deployments':[]}
    for builder in ['build01','build02']:
        source = PROJECT/'work/m13'/builder
        dest = ROOT/'deployment'/builder
        dest.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(source/'registry.json',dest/'registry.json')
        shutil.copytree(source/'sources',dest/'sources')
        shutil.copyfile(observed_path,dest/'observed.csv')
        task = read(source/'task.json')
        task['task_id'] = f'm13b-bodyfat-j-{builder}'
        task['population'] = 'NHANES2017-18 White/Black age20-59 BMI18.5-35 complete-covariate valid-DXA domain; outcome hidden'
        task['n_rows'] = len(observed)
        task['budget']['revisions'] = 0
        write_new(dest/'task.json', task)
        for name in ['initial','source_reviewed']:
            original = source/'candidates'/name
            target = dest/'candidates'/name
            shutil.copytree(original,target,ignore=shutil.ignore_patterns('freeze.json','__pycache__'))
            identity = next(m for m in protocol['models'] if m['builder']==builder and m['candidate']==name)
            if sha256(target/'generator.py')!=identity['generator_sha256'] or sha256(target/'model_spec.json')!=identity['spec_sha256']:
                raise ValueError('Deployment changed science')
            write_new(target/'deployment_provenance.json', {
                'original':identity,'kind':'new_observed_input_execution_binding',
                'scientific_bytes_unchanged':True,'preaccess_sha256':manifest['preaccess_sha256'],
                'original_checks_scope':'source/qualification only, not new-target validation'})
            freeze_candidate(dest,f'candidates/{name}')
            verify_candidate(dest,f'candidates/{name}')
            manifest['deployments'].append({'builder':builder,'candidate':name,'bundle':str(dest),
                  'deployment_freeze_sha256':sha256(target/'freeze.json')})
    write_new(ROOT/'deployment_manifest.json',manifest)
    print(json.dumps({'deployed':len(manifest['deployments']),'n_rows':len(observed)}),flush=True)


def references(observed, seed):
    bmi,age,male = [observed[c].to_numpy(float) for c in ['bmi','age','male']]
    mean = 76 - 1097.8/bmi - 20.6*male + .053*age + 154*male/bmi + .034*male*age
    values = mean.copy()
    redraw_count = 0
    if seed is not None:
        rng = np.random.default_rng(seed)
        values += rng.normal(0,4.31,len(values))
        for _ in range(1000):
            invalid=(values<0)|(values>100)
            if not invalid.any(): break
            redraw_count+=int(invalid.sum())
            values[invalid]=mean[invalid]+rng.normal(0,4.31,int(invalid.sum()))
        else: raise ValueError('Reference rejection sampler did not terminate')
    if not np.isfinite(values).all() or ((values<0)|(values>100)).any():
        raise ValueError('Reference outside physiological range')
    output=observed.copy()
    output['bodyfat']=values
    return output,redraw_count


def generate():
    frozen,protocol=verify_preaccess()
    deployment=read(ROOT/'deployment_manifest.json')
    if deployment['preaccess_sha256'] != sha256(ROOT/'preaccess_freeze.json'):
        raise ValueError('Deployment belongs to another preaccess freeze')
    for entry in deployment['deployments']:
        directory=Path(entry['bundle'])/'candidates'/entry['candidate']
        identity=next(m for m in protocol['models']
                      if m['builder']==entry['builder'] and m['candidate']==entry['candidate'])
        if sha256(directory/'freeze.json') != entry['deployment_freeze_sha256']:
            raise ValueError('Deployment freeze replaced')
        if sha256(directory/'generator.py') != identity['generator_sha256'] or sha256(directory/'model_spec.json') != identity['spec_sha256']:
            raise ValueError('Deployed scientific identity changed')
        verify_candidate(entry['bundle'],f"candidates/{entry['candidate']}")
    observed_path=Path(deployment['observed_path'])
    if sha256(observed_path)!=deployment['observed_sha256']:
        raise ValueError('Permitted target inputs changed')
    observed=load_observed(observed_path)
    runtime=read(PROJECT/'work/m2-runtime-config.json')
    records=[]
    for scheduled in protocol['tables']:
        row=dict(scheduled)
        name=row['table_id']
        if row['kind']=='agent':
            bundle=ROOT/'deployment'/row['builder']
            run_id=f"{row['candidate']}_{row['seed']}"
            if (bundle/'executions'/run_id).exists():
                receipt=verify_execution(bundle,run_id)
            else:
                receipt=run_candidate(bundle,f"candidates/{row['candidate']}",run_id,row['seed'],
                       runtime=runtime,timeout_seconds=45,memory_mb=1024,output_bytes=20_000_000)
                verify_execution(bundle,run_id)
            # Execution adapter's documented run artifact, validated before release.
            artifact=bundle/'executions'/run_id/'output'/'generated.csv'
            row['status']='complete' if receipt['status']=='success' else 'failed'
            row['path']=str(artifact) if row['status']=='complete' else None
            row['execution_receipt_path']=str(bundle/'executions'/run_id/'execution.json')
            row['execution_status']=receipt['status']
        else:
            directory=ROOT/'references'
            directory.mkdir(exist_ok=True)
            artifact=directory/f'{name}.csv'
            receipt_path=directory/f'{name}.json'
            if artifact.exists() or receipt_path.exists():
                receipt=read(receipt_path)
                if sha256(artifact)!=receipt['output_sha256'] or receipt['observed_sha256']!=sha256(observed_path):
                    raise ValueError('Existing reference binding differs')
            else:
                table,redraws=references(observed,row['seed'])
                table.to_csv(artifact,index=False)
                write_new(receipt_path,{'table_id':name,'seed':row['seed'],
                         'output_sha256':sha256(artifact),'observed_sha256':sha256(observed_path),
                         'controller_sha256':sha256(Path(__file__)), 'redrawn_values':redraws,
                         'scope':'trusted published-formula reference, not Agent execution'})
            row.update(status='complete',path=str(artifact),reference_receipt_path=str(receipt_path))
        if row['status']=='complete': row['sha256']=sha256(artifact)
        records.append(row)
        print(json.dumps({'table_id':name,'status':row['status']}),flush=True)
    write_new(ROOT/'generated_manifest.json',{'schema_version':1,'observed_path':str(observed_path),
              'preaccess_sha256':sha256(ROOT/'preaccess_freeze.json'),'tables':records})


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['initialize','freeze','deploy','generate','verify'])
    parser.add_argument('--observed')
    args=parser.parse_args()
    if args.action=='initialize': initialize()
    elif args.action=='freeze': freeze()
    elif args.action=='deploy': deploy(args.observed)
    elif args.action=='generate': generate()
    else: verify_preaccess();print('preaccess and original scientific identities verified')
