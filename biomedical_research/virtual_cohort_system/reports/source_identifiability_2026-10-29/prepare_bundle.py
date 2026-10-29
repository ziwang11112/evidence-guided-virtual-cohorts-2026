"""Prepare synthetic covariate probes and previously approved sources only."""
from pathlib import Path
import hashlib
import itertools
import json
import shutil
import pandas as pd

E = Path(__file__).resolve().parent
P = E.parents[1]
OLD = P / 'work/structure-robustness-2026-10-28/agent_bundle'
B = E / 'agent_bundle'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def main():
    B.mkdir(exist_ok=False)
    registry = json.loads((OLD / 'registry.json').read_text())
    (B / 'sources').mkdir()
    for item in registry['artifacts']:
        source = OLD / item['path']
        assert sha(source) == item['sha256']
        shutil.copyfile(source, B / item['path'])
    shutil.copyfile(OLD / 'registry.json', B / 'registry.json')
    rows = []
    for i, (sex, age, bmi, repeat) in enumerate(itertools.product([1, 2], range(20, 80), range(18, 41), range(10))):
        rows.append({'record_id': f'probe_{i:06d}', 'age': age, 'sex': sex,
                     'bmi': float(bmi), 'tg_assay': 'legacy_proxy'})
    pd.DataFrame(rows).to_csv(B / 'observed.csv', index=False)
    task = json.loads((OLD / 'task.json').read_text())
    task['task_id'] = 'tg-source-identifiability-synthetic-probe-2026-10-29'
    task['population'] = ('Synthetic Cartesian covariate probe, not a real target cohort: age20..79, '
        'BMI18..40 at integer grid spacing, sex1/2, ten replicate rows per cell. '
        'Append plausible legacy-proxy TG according to the approved source-only construction. '
        'This is a constructive model sensitivity experiment, not clinical validation. '
        'Do not use record identifiers, row order/count or assay labels as biological selectors. '
        'No real target outcomes, target answers or desired relationship directions are supplied. '
        'The two original paper contexts retain their declared measurement/joint-covariate assumptions.')
    task['n_rows'] = len(rows)
    task['budget']['revisions'] = 0
    write(B / 'task.json', task)
    write(E / 'bundle_preparation.json', {
        'synthetic_only': True, 'n_rows': len(rows), 'participant_rows_used': False,
        'grid': {'sex': [1,2], 'age': [20,79,1], 'bmi': [18,40,1], 'replicates': 10},
        'task_sha256': sha(B / 'task.json'), 'observed_sha256': sha(B / 'observed.csv'),
        'registry_sha256': sha(B / 'registry.json'), 'approved_source_count': len(registry['artifacts'])})
    print(json.dumps({'prepared': True, 'synthetic_probe_rows': len(rows)}))

if __name__ == '__main__':
    main()
