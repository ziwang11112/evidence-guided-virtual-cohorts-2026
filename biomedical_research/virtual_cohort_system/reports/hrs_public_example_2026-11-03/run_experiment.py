"""Bounded controller: six exclusive generation slots, then native evaluations.

No scientific parameter is defined here. Preparation/release is separate. Never
repeat an existing slot, including an interrupted or failed attempt.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess
import sys
import time

UNIT = Path(__file__).resolve().parent
PROJECT = UNIT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.execution import run_candidate, verify_execution, DEFAULT_RUNTIME
from cohort_harness.lifecycle import verify_candidate

BUNDLE = UNIT / 'bundle'
SEEDS = [6101, 6102, 6103]
ARMS = ['native', 'agent']

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write_new(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write('\n')

def state(phase, **extra):
    value = read(UNIT / 'STATE.json')
    value.update(phase=phase, updated_utc=utc(), **extra)
    (UNIT / 'STATE.json').write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def verify_release():
    release = read(UNIT / 'RELEASE.json')
    assert release['execution_released'] is True
    assert release['seeds'] == SEEDS and release['arms'] == ARMS
    assert release['generation_attempts_allowed'] == 6
    assert release['generator_runtime'] == DEFAULT_RUNTIME
    for relative, expected in release['files'].items():
        assert sha(UNIT / relative) == expected, 'Release commitment changed: ' + relative
    for arm in ARMS:
        verify_candidate(BUNDLE, 'candidates/' + arm)
    return release

def slots():
    return [(arm, seed, f'{arm}_{seed}') for arm in ARMS for seed in SEEDS]

def generate_all():
    verify_release()
    reservations = UNIT / 'attempts'
    reservations.mkdir(exist_ok=True)
    for arm, seed, run_id in slots():
        final = reservations / (run_id + '.json')
        reserved = reservations / (run_id + '.reserved.json')
        if final.exists():
            continue
        if reserved.exists():
            raise RuntimeError('Reserved attempt without closure; inspect actual process/receipt, never rerun: ' + run_id)
        verify_release()
        write_new(reserved, {'created_utc': utc(), 'arm': arm, 'seed': seed,
                            'run_id': run_id, 'attempt_spent': True,
                            'release_sha256': sha(UNIT / 'RELEASE.json')})
        state('generation', final_attempts_spent=len(list(reservations.glob('*.reserved.json'))))
        result = {'arm': arm, 'seed': seed, 'run_id': run_id, 'started_utc': utc()}
        try:
            receipt = run_candidate(BUNDLE, 'candidates/' + arm, run_id, seed,
                                    runtime=DEFAULT_RUNTIME, timeout_seconds=120,
                                    memory_mb=1024, output_bytes=30_000_000, log_bytes=100_000)
            verified = verify_execution(BUNDLE, run_id)
            result.update(status=receipt['status'], generator_executed=receipt['generator_executed'],
                          execution_integrity_verified=True,
                          execution_sha256=sha(BUNDLE / 'executions' / run_id / 'execution.json'),
                          elapsed_seconds=receipt['elapsed_seconds'], error=receipt['error'])
            assert verified['status'] == receipt['status']
        except Exception as error:
            result.update(status='controller_error', error={'type': type(error).__name__, 'message': str(error)})
        result['finished_utc'] = utc()
        write_new(final, result)
        print(json.dumps({'stage': 'generation', 'run_id': run_id, 'status': result['status']}), flush=True)
    assert len(list(reservations.glob('*.reserved.json'))) == 6
    closures = [read(reservations / (run_id + '.json')) for _, _, run_id in slots()]
    if not (UNIT / 'GENERATION_CLOSED.json').exists():
        write_new(UNIT / 'GENERATION_CLOSED.json', {'created_utc': utc(), 'slots': closures,
                  'attempts_spent': 6, 'scientific_results_inspected_before_closure': False,
                  'release_sha256': sha(UNIT / 'RELEASE.json'),
                  'attempt_bindings': {run_id: sha(reservations / (run_id + '.json'))
                                       for _, _, run_id in slots()}})
    state('generation_closed', final_attempts_spent=6)

def wsl(path):
    resolved = str(Path(path).resolve()).replace('\\', '/')
    return '/mnt/' + resolved[0].lower() + resolved[2:]

def evaluate_all():
    verify_release()
    closed = read(UNIT / 'GENERATION_CLOSED.json')
    assert closed['attempts_spent'] == 6 and len(closed['slots']) == 6
    assert closed['release_sha256'] == sha(UNIT / 'RELEASE.json')
    assert [(x['arm'], x['seed'], x['run_id']) for x in closed['slots']] == slots()
    assert set(closed['attempt_bindings']) == {x[2] for x in slots()}
    for arm, seed, run_id in slots():
        attempt_path = UNIT / 'attempts' / (run_id + '.json')
        assert sha(attempt_path) == closed['attempt_bindings'][run_id]
        attempt = read(attempt_path)
        reservation = read(UNIT / 'attempts' / (run_id + '.reserved.json'))
        assert (attempt['arm'], attempt['seed'], attempt['run_id']) == (arm, seed, run_id)
        assert (reservation['arm'], reservation['seed'], reservation['run_id']) == (arm, seed, run_id)
        assert reservation['release_sha256'] == closed['release_sha256']
        if attempt['status'] == 'success':
            execution_path = BUNDLE / 'executions' / run_id / 'execution.json'
            assert sha(execution_path) == attempt['execution_sha256']
            receipt = verify_execution(BUNDLE, run_id)
            assert receipt['status'] == 'success' and receipt['candidate'] == 'candidates/' + arm
            assert receipt['limits']['seed'] == seed
    folder = UNIT / 'results'
    folder.mkdir(exist_ok=True)
    for arm, seed, run_id in slots():
        generation = read(UNIT / 'attempts' / (run_id + '.json'))
        final = folder / (run_id + '.evaluation.json')
        if final.exists():
            continue
        reserved = folder / (run_id + '.reserved.json')
        if reserved.exists():
            raise RuntimeError('Evaluation already reserved; inspect and close without rerunning: ' + run_id)
        if any((folder / (run_id + suffix)).exists() for suffix in ['.native.json', '.gls.json', '.stdout.log', '.stderr.log']):
            raise RuntimeError('Unreserved evaluation has preexisting artifacts: ' + run_id)
        verify_release()
        write_new(reserved, {'created_utc': utc(), 'run_id': run_id,
                             'generation_closure_sha256': sha(UNIT / 'GENERATION_CLOSED.json')})
        record = {'run_id': run_id, 'arm': arm, 'seed': seed, 'started_utc': utc(), 'fit_attempts': 0}
        try:
            if generation['status'] != 'success':
                record.update(status='not_evaluable', reason='Generation slot was not successful')
            else:
                receipt = verify_execution(BUNDLE, run_id)
                assert receipt['status'] == 'success'
                table = BUNDLE / 'executions' / run_id / 'output/generated.csv'
                native = folder / (run_id + '.native.json')
                record.update(input_sha256=sha(table), fit_attempts=1)
                command = ['wsl.exe', '-d', 'Ubuntu-24.04', '--', 'python3',
                           wsl(UNIT / 'evaluation/run_r.py'), wsl(UNIT / 'evaluation/native_evaluate.R'),
                           wsl(table), wsl(native)]
                started = time.monotonic()
                try:
                    completed = subprocess.run(command, capture_output=True, timeout=325)
                    (folder / (run_id + '.stdout.log')).write_bytes(completed.stdout)
                    (folder / (run_id + '.stderr.log')).write_bytes(completed.stderr)
                    record['returncode'] = completed.returncode
                    native_result = read(native) if native.exists() else None
                    if native_result:
                        assert native_result['input_sha256'] == record['input_sha256']
                    record['status'] = native_result['status'] if native_result else 'no_native_output'
                    if completed.returncode != 0 and record['status'] == 'computed':
                        record['status'] = 'process_failed_with_partial_result'
                except subprocess.TimeoutExpired as error:
                    record.update(status='controller_timeout', error='325s host cap; no retry')
                    (folder / (run_id + '.stdout.log')).write_bytes(error.stdout or b'')
                    (folder / (run_id + '.stderr.log')).write_bytes(error.stderr or b'')
                record['elapsed_seconds'] = time.monotonic() - started
                if native.exists():
                    record['native_json_sha256'] = sha(native)
                if record['status'] == 'computed':
                    check = folder / (run_id + '.gls.json')
                    try:
                        completed = subprocess.run([sys.executable, str(UNIT / 'evaluation/independent_gls.py'),
                            '--input-csv', str(table), '--native-json', str(native), '--output-json', str(check)],
                            capture_output=True, timeout=120)
                        record['gls_returncode'] = completed.returncode
                        record['gls_status'] = read(check)['status'] if check.exists() else 'no_output'
                        if completed.returncode != 0 and record['gls_status'] == 'pass':
                            record['gls_status'] = 'process_failed_with_partial_result'
                        if check.exists():
                            record['gls_json_sha256'] = sha(check)
                    except Exception as error:
                        record['gls_status'] = 'check_failed_no_retry'
                        record['gls_error'] = {'type': type(error).__name__, 'message': str(error)}
        except Exception as error:
            record.update(status='evaluation_error_no_retry', error={'type': type(error).__name__, 'message': str(error)})
        finally:
            record['finished_utc'] = utc()
            write_new(final, record)
        print(json.dumps({'stage': 'evaluation', 'run_id': run_id, 'status': record['status'],
                          'gls': record.get('gls_status')}), flush=True)
    state('evaluated_pending_review')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['generate', 'evaluate', 'all'])
    args = parser.parse_args()
    if args.stage in ('generate', 'all'):
        generate_all()
    if args.stage in ('evaluate', 'all'):
        evaluate_all()
