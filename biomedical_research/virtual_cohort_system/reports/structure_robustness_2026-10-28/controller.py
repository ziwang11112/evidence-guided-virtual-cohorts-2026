"""Fixed experiment schedule. No biological coefficients or target analyses."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.lifecycle import read_json, sha256, verify_candidate
from cohort_harness.execution import verify_execution
from cohort_harness.source_replay import verify_source_replay
from cohort_harness.source_portfolio import summarize_source_portfolio, compare_source_portfolios

BUNDLE = ROOT / 'agent_bundle'
PROTOCOL = read_json(ROOT / 'protocol.json')
ANCHOR = read_json(ROOT / 'protocol_commitment.json')
for name, digest in ANCHOR['files'].items():
    assert sha256(ROOT / name) == digest, 'Committed experiment artifact changed: ' + name
STRUCTURES = PROTOCOL['structures']
SOURCE_SEEDS = PROTOCOL['source_seeds']
TARGET_SEEDS = PROTOCOL['target_seeds']
LOGS = ROOT / 'controller_logs'
LOGS.mkdir(exist_ok=True)

def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')

def command(label, args):
    log = LOGS / (label + '.json')
    if log.exists():
        raise RuntimeError('An attempt already exists: ' + label)
    result = subprocess.run([sys.executable, '-m', 'cohort_harness', *args], cwd=PROJECT,
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
    write_new(log, {'args': args, 'returncode': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr})
    if result.returncode:
        raise RuntimeError('Failed attempt retained at ' + str(log))
    print('completed', label, flush=True)
    return json.loads(result.stdout)

def candidates(stage):
    result = []
    for structure in STRUCTURES:
        name = PROTOCOL['candidate_names'][structure][stage]
        path = BUNDLE / 'candidates' / name
        receipt = verify_candidate(BUNDLE, path)
        assert receipt['revision_index'] == (0 if stage == 'initial' else 1)
        result.append((structure, name, path, receipt))
    # This function completes for ALL models before the caller executes any.
    return result

def source(stage):
    entries = candidates(stage)
    if stage == 'initial':
        plan = BUNDLE / 'STRUCTURE_PLAN.json'
        write_new(ROOT / 'structure_plan_commitment.json', {
            'created_utc': datetime.now(timezone.utc).isoformat(), 'plan_sha256': sha256(plan),
            'candidate_freezes': {s: sha256(path / 'freeze.json') for s, _, path, _ in entries},
            'protocol_sha256': sha256(ROOT / 'protocol.json')})
    for structure, name, path, _ in entries:
        ids = []
        for seed in SOURCE_SEEDS:
            replay_id = f'{name}_{seed}'
            ids.append(replay_id)
            command(replay_id, ['source-replay', '--bundle', str(BUNDLE), '--candidate', name,
                '--replay-id', replay_id, '--seed', str(seed), '--runtime', str(PROJECT / 'work/m2-runtime-config.json')])
        report = summarize_source_portfolio(BUNDLE, path, ids, SOURCE_SEEDS)
        write_new(ROOT / 'source_feedback' / f'{name}_portfolio.json', report)
    if stage == 'final':
        for structure in STRUCTURES:
            initial, final = f'{structure}_initial', f'{structure}_final'
            comparison = compare_source_portfolios(BUNDLE, BUNDLE / 'candidates' / initial,
                BUNDLE / 'candidates' / final,
                [f'{initial}_{s}' for s in SOURCE_SEEDS], [f'{final}_{s}' for s in SOURCE_SEEDS], SOURCE_SEEDS)
            write_new(ROOT / 'source_feedback' / f'{structure}_paired.json', comparison)

def target():
    entries = candidates('final')
    # Complete and verify ALL final source diagnostics before any target run.
    for _, name, path, _ in entries:
        for seed in SOURCE_SEEDS:
            assert verify_source_replay(BUNDLE, f'{name}_{seed}', candidate=path)['status'] == 'success'
    for structure, name, path, _ in entries:
        for seed in TARGET_SEEDS:
            run_id = f'{name}_{seed}'
            command(run_id, ['execute', '--bundle', str(BUNDLE), '--candidate', name,
                '--run-id', run_id, '--seed', str(seed), '--runtime', str(PROJECT / 'work/m2-runtime-config.json')])
            assert verify_execution(BUNDLE, run_id)['status'] == 'success'

def commit():
    candidate_records, source_records, outputs = [], [], []
    for stage in ('initial', 'final'):
        for structure, name, path, _ in candidates(stage):
            candidate_records.append({'structure': structure, 'stage': stage, 'candidate_name': name,
                'path': str(path / 'freeze.json'), 'sha256': sha256(path / 'freeze.json')})
            for seed in SOURCE_SEEDS:
                rid = f'{name}_{seed}'
                assert verify_source_replay(BUNDLE, rid, candidate=path)['status'] == 'success'
                source_records.append({'structure': structure, 'stage': stage, 'replay_id': rid, 'seed': seed})
            if stage == 'final':
                for seed in TARGET_SEEDS:
                    rid = f'{name}_{seed}'
                    receipt = verify_execution(BUNDLE, rid)
                    assert receipt['status'] == 'success' and receipt['candidate'] == f'candidates/{name}'
                    assert receipt['limits']['seed'] == seed
                    output = BUNDLE / 'executions' / rid / 'output/generated.csv'
                    outputs.append({'structure': structure, 'seed': seed, 'run_id': rid,
                        'candidate_name': name, 'path': str(output), 'sha256': sha256(output)})
    commitment = {'created_utc': datetime.now(timezone.utc).isoformat(),
        'structures': STRUCTURES, 'seeds': TARGET_SEEDS,
        'authorize_target_evaluation': True, 'all_structures_and_seeds_committed': True,
        'authorization_basis': 'User requested frozen structures followed by fresh public target validation.',
        'custodian_lock_sha256': sha256(ROOT / 'custodian/custodian_lock.json'),
        'bundle_path': str(BUNDLE), 'candidate_commitments': candidate_records,
        'source_replays': source_records, 'outputs': outputs,
        'experiment_protocol': {'path': str(ROOT / 'protocol.json'), 'sha256': sha256(ROOT / 'protocol.json')},
        'structure_plan_commitment': {'path': str(ROOT / 'structure_plan_commitment.json'),
                                      'sha256': sha256(ROOT / 'structure_plan_commitment.json')},
        'builder_observed': {'path': str(BUNDLE / 'observed.csv'), 'sha256': sha256(BUNDLE / 'observed.csv')},
        'controller_guard': {'path': str(ROOT / 'release_guard.py'), 'sha256': sha256(ROOT / 'release_guard.py'),
                             'function': 'verify_release'},
        'post_evaluation_builder_revision_allowed': False}
    destination = ROOT / 'evaluation_commitment.json'
    write_new(destination, commitment)
    from release_guard import verify_release
    verification = verify_release(destination)
    write_new(ROOT / 'release_verification.json', verification)
    print('commitment', sha256(destination), verification['status'], flush=True)

if __name__ == '__main__':
    phase = sys.argv[1]
    if phase in ('initial', 'final'):
        source(phase)
    elif phase == 'target':
        target()
    elif phase == 'commit':
        commit()
    else:
        raise ValueError('Unknown controller phase')
