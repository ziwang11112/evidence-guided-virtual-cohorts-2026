"""List/check, or explicitly stage, frozen C5 replay inputs. Never execute them."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

SCIENCE = ['generator.py', 'evidence.json', 'model_spec.json', 'decision.md', 'checks.json', 'derivation_check.json']


def inputs():
    names = ['PROTOCOL.md', 'EXPOSURE_NOTE.md', 'source_commitment.json',
             'INITIAL_AUTHOR_COMMITMENT.json', 'setup_tasks.py', 'run_unit.py',
             'method/adapter.py', 'method/README.md', 'method/test_adapter.py',
             'author/request_decisions.json', 'author/extension_task_template.json',
             'evaluation/evaluate.py']
    names += ['visible/' + name for name in ['analysis_plan.md', 'initial_source_packet.json',
              'final_source_packet.json', 'output_contract.json', 'request_transcript.md']]
    names += ['custody/' + name for name in ['analytic_truth.json', 'prepare_truth.py', 'README.md', 'setup_checks.json']]
    names += ['author/extension/' + name for name in SCIENCE]
    for bundle, packet in [('b/p', 'initial_source_packet.json'), ('b/j', 'final_source_packet.json')]:
        names += [bundle + '/task.json', bundle + '/registry.json', bundle + '/sources/' + packet]
        names += [bundle + '/candidates/c0/' + name for name in SCIENCE + ['freeze.json']]
    return sorted(names)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd(), help='Fresh clone virtual_cohort_system project directory')
    parser.add_argument('--stage', action='store_true', help='Copy checked inputs into absent project/work/c5; never execute generation')
    args = parser.parse_args()
    archive = Path(__file__).resolve().parent
    project = args.project.resolve()
    destination = project / 'work' / 'c5'
    if not (project / 'cohort_harness').is_dir():
        raise SystemExit('Project must contain the existing cohort_harness directory.')
    manifest = json.loads((archive / 'EXPORT_MANIFEST.json').read_text(encoding='utf-8'))
    expected = {record['destination'].split('/reports/c5_dynamic_extension_2026-10-31/', 1)[1]: record['destination_sha256']
                for record in manifest['files'] if '/reports/c5_dynamic_extension_2026-10-31/' in record['destination']}
    names = inputs()
    for name in names:
        if name not in expected or sha(archive / name) != expected[name]:
            raise SystemExit('Archive input missing or changed: ' + name)
    plan = json.loads((archive / 'RUN_PLAN.json').read_text(encoding='utf-8'))
    for name, digest in plan['harness'].items():
        if sha(project / 'cohort_harness' / name) != digest:
            raise SystemExit('Trusted harness differs from historical binding: ' + name)
    if args.stage:
        if destination.exists():
            raise SystemExit('Refusing existing work/c5. Use a fresh clean clone; no overwrite or cleanup is performed.')
        destination.mkdir(parents=True)
        for name in names:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(archive / name, target)
            if sha(target) != expected[name]:
                raise SystemExit('Staged hash mismatch: ' + name)
    print(json.dumps({'mode': 'staged_inputs_only' if args.stage else 'list_and_check_only',
                      'destination': str(destination), 'destination_preexisting_or_created': destination.exists(),
                      'input_count': len(names), 'inputs': names, 'archive_hashes_checked': True,
                      'historical_harness_hashes_checked': True, 'generation_executed': False,
                      'fresh_replay_tested': False}, indent=2))


if __name__ == '__main__':
    main()
