"""Attach only the custodian-approved outcome-free inputs."""
from pathlib import Path
import json
import shutil
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import read_json, sha256, read_table
from cohort_harness.contracts import validate_input


def new(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    b, v = E / 'agent_bundle', E / 'visible/nhanes_tg_f'
    lock = read_json(E / 'custodian/custodian_lock.json')
    if sha256(v / 'input_hashes.json') != lock['visible_input_hashes_sha256']:
        raise ValueError('Custodian visible manifest changed')
    manifest = read_json(v / 'input_hashes.json')
    for name, h in manifest['files'].items():
        if sha256(v / name) != h:
            raise ValueError('Visible artifact changed: ' + name)
    task = read_json(P / 'work/source-identifiability-2026-10-29/agent_bundle/task.json')
    import pandas as pd
    frame = pd.read_csv(v / 'observed.csv', dtype={'record_id': str})
    if 'tg_assay' not in frame:
        frame['tg_assay'] = 'legacy_proxy'
    if list(frame.columns) != ['record_id', 'age', 'sex', 'bmi', 'tg_assay']:
        raise ValueError('Unexpected visible columns')
    task['task_id'] = 'analysis-evidence-gap-tg-2026-10-29'
    task['population'] = ('US noninstitutionalized adults aged40–79; morning examination, '
        '8.5 to<24hours fasting, positive sampling weight and complete age/sex/BMI/TG availability. '
        'TG outcomes are held by an independent custodian and never provided to the builder. '
        'The legacy_proxy token represents the documented glycerol-blanked assay with explicit '
        'source-to-target measurement assumptions. Preserve observed rows. Do not use identifiers '
        'or row order/count as biological predictors. No desired analytical signs are specified.')
    task['n_rows'] = len(frame)
    task['information_policy']['allowed_tools'] = ['approved_local_sources', 'source_replay']
    task['budget'] = {'source_queries': 0, 'source_downloads': 0, 'revisions': 1}
    new(b / 'task.json', task)
    with (b / 'observed.csv').open('x', newline='', encoding='utf-8') as stream:
        frame.to_csv(stream, index=False)
    validate_input(read_table(b / 'observed.csv', task), task)
    new(E / 'visible_attachment.json', {
        'custodian_lock_sha256': sha256(E / 'custodian/custodian_lock.json'),
        'visible_manifest_sha256': sha256(v / 'input_hashes.json'),
        'original_observed_sha256': sha256(v / 'observed.csv'),
        'builder_observed_sha256': sha256(b / 'observed.csv'),
        'n_rows': len(frame), 'target_outcome_opened': False,
        'conversion': 'Read/write CSV; unchanged values and order, legacy_proxy constant if absent. '
                      'Custodian independently verifies exact observed-cell preservation.'})
    print(json.dumps({'status': 'ready', 'rows': len(frame)}))


if __name__ == '__main__':
    main()
