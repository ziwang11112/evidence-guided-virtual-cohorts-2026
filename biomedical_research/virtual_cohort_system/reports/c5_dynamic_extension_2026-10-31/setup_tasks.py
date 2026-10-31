"""C5 controller-only source admission and task preparation; no generator logic."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from cohort_harness.contracts import require, validate_task
from cohort_harness.lifecycle import read_json, sha256, verify_candidate

SOURCE_COMMITMENT_PIN = 'fc65d14be56e35d700def8ed0292ef5dc3991ecfe6e0e8682368ba4f044e5548'


def verify_source_commitment(root):
    require(sha256(root / 'source_commitment.json') == SOURCE_COMMITMENT_PIN,
            'Custodian source commitment differs from the independently delivered pin')
    value = read_json(root / 'source_commitment.json')
    for entry in value['committed_files']:
        if entry['access_before_final_outputs'] == 'visible':
            require(sha256(root / entry['path']) == entry['sha256'], 'Visible source changed after custody seal')
    return value


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def columns(packet, *, extension=False):
    result = [{'name': 'subject_id', 'kind': 'string', 'unit': '',
               'role': 'identifier', 'nullable': False}]
    for variable in packet['variables']:
        result.append({'name': variable['name'], 'kind': 'number', 'unit': variable['unit'],
                       'role': 'observed' if extension and variable['name'] in {'x1', 'x2'} else 'generated',
                       'nullable': False})
    return result


def setup(root: Path, phase: str):
    require((root / 'source_commitment.json').is_file(), 'Custodian commitment must precede authoring')
    verify_source_commitment(root)
    initial = read_json(root / 'visible/initial_source_packet.json')
    if phase == 'initial':
        name, source_name = 'p', 'initial_source_packet.json'
    else:
        verify_candidate(root / 'b/p', 'candidates/c0')
        require((root / 'INITIAL_AUTHOR_COMMITMENT.json').is_file(), 'Initial author commitment required')
        commitment = read_json(root / 'INITIAL_AUTHOR_COMMITMENT.json')
        require(commitment['source_commitment_sha256'] == SOURCE_COMMITMENT_PIN, 'Wrong initial source commitment')
        for path, expected in commitment['bindings'].items():
            require(path.startswith('b/p/'), 'Initial commitment contains an unexpected path')
            require(sha256(root / path) == expected, 'Initial author artifact changed')
        name, source_name = 'j', 'final_source_packet.json'
    source = root / 'visible' / source_name
    packet = read_json(source)
    require(packet['population_id'] == initial['population_id'], 'Fixture population identity mismatch')
    bundle = root / 'b' / name
    require(not bundle.exists(), 'Task destination already exists')
    task = {'schema_version': 1, 'task_id': 'c5_' + name, 'mode': 'whole_cohort',
            'population': initial['population'], 'row_id': 'subject_id', 'n_rows': 2000,
            'columns': columns(packet),
            'information_policy': {'mode': 'published_evidence', 'excluded_cohorts': [],
                                   'allowed_tools': ['admitted_artificial_source']},
            'budget': {'source_queries': 0, 'source_downloads': 0, 'revisions': 0}}
    validate_task(task)
    bundle.mkdir(parents=True)
    write_new(bundle / 'task.json', task)
    (bundle / 'sources').mkdir()
    (bundle / 'sources' / source_name).write_bytes(source.read_bytes())
    write_new(bundle / 'registry.json', {'artifacts': [
        {'source_id': packet['packet_id'], 'path': 'sources/' + source_name,
         'sha256': sha256(source), 'origin': 'fixture', 'screening': 'approved'}]})
    (bundle / 'candidates').mkdir()
    if phase == 'final':
        extension_task = dict(task, task_id='c5_extension_template', mode='enrichment',
                              columns=columns(packet, extension=True))
        validate_task(extension_task)
        write_new(root / 'author/extension_task_template.json', extension_task)
    return {'phase': phase, 'bundle': str(bundle), 'task_sha256': sha256(bundle / 'task.json'),
            'source_sha256': sha256(source), 'source_origin': 'explicitly_artificial'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['initial', 'final'])
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(setup(args.root.resolve(), args.phase)))
