"""Run the fixed, root-released isolated schedule once; never analyze target effects."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

R = Path(__file__).resolve().parent.parent
P = R.parent.parent
sys.path.insert(0, str(P))
from cohort_harness.execution import run_candidate, DEFAULT_RUNTIME
from cohort_harness.lifecycle import verify_candidate


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, obj):
    with (R / name).open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')


def main():
    release_path = R / 'EXECUTION_RELEASE.json'
    release_hash = sha(release_path)
    assert release_hash == '1d87d08360fee80e0e0f6f746730a3be7e6a061c5e1b97cf9fd04ac2404754f2'
    release = json.loads(release_path.read_bytes())
    assert release['issuer'] == 'root' and release['status'] == 'approved'
    assert release['target_effects_authorized'] is False
    assert sha(R / 'PROTOCOL_v2.md') == release['protocol_sha256']
    assert sha(R / 'controller/prepare_target_release.py') == release['controller_script_sha256']
    for builder in release['builders']:
        for stage in ('initial', 'final'):
            candidate = builder[stage + '_candidate']
            verify_candidate(R / builder['bundle'], candidate)
            assert sha(R / builder['bundle'] / candidate / 'freeze.json') == builder[stage + '_freeze_sha256']
    expected = {(b, seed) for b in ('b1', 'b2') for seed in (18203, 18211, 18223)}
    assert {(v['bundle'], v['seed']) for v in release['unique_runs']} == expected
    assert len(release['unique_runs']) == 6
    for run in release['unique_runs']:
        assert not (R / run['bundle'] / 'executions' / run['run_id']).exists()
    save('TARGET_GENERATION_ATTEMPT.json', {
        'release_sha256': release_hash, 'controller_sha256': sha(Path(__file__)),
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'unique_runs': 6,
    })
    completed = []
    try:
        for run in release['unique_runs']:
            receipt = run_candidate(R / run['bundle'], run['candidate'], run['run_id'],
                                    run['seed'], runtime=DEFAULT_RUNTIME)
            record = {**run, 'status': receipt['status'],
                      'elapsed_seconds': receipt['elapsed_seconds'],
                      'receipt_sha256': sha(R / run['bundle'] / 'executions' / run['run_id'] / 'execution.json')}
            completed.append(record)
            print(json.dumps(record), flush=True)
        save('TARGET_GENERATION_COMPLETED.json', {'release_sha256': release_hash, 'runs': completed,
             'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'target_effects_evaluated': False})
    except Exception as error:
        save('TARGET_GENERATION_FAILURE.json', {'type': type(error).__name__,
             'completed_runs': completed, 'automatic_retry': False})
        raise


if __name__ == '__main__':
    main()
