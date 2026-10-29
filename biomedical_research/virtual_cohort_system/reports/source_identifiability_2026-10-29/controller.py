"""Execute the frozen constructive pilot; no biological model is chosen here."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import read_json, sha256, verify_candidate
from cohort_harness.execution import verify_execution
from cohort_harness.source_replay import verify_source_replay
from cohort_harness.source_portfolio import summarize_source_portfolio

B = E / 'agent_bundle'

def now():
    return datetime.now(timezone.utc).isoformat()

def new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')

def anchors():
    commitment = read_json(E / 'protocol_commitment.json')
    for relative, digest in commitment['files'].items():
        assert sha256(E / relative) == digest, relative
    for relative, digest in commitment['core_files'].items():
        assert sha256(P / relative) == digest, relative
    assert sha256(P / 'work/m2-runtime-config.json') == commitment['runtime_config_sha256']
    protocol = read_json(E / 'protocol.json')
    records = []
    evidence_hashes, recipe_hashes, code_hashes = set(), set(), set()
    for label in protocol['labels']:
        path = B / 'candidates' / label
        receipt = verify_candidate(B, path)
        assert receipt['revision_index'] == 0
        assert sha256(path / 'freeze.json') == commitment['candidate_freezes'][label]
        evidence_hashes.add(sha256(path / 'evidence.json'))
        recipe_hashes.add(sha256(path / 'source_replay.json'))
        code_hashes.add(sha256(path / 'generator.py'))
        records.append({'label': label, 'path': str(path),
            'freeze_sha256': sha256(path / 'freeze.json'),
            'model_spec_path': str(path / 'model_spec.json'),
            'model_spec_sha256': sha256(path / 'model_spec.json'),
            'analytic_certificate_path': str(path / 'analytic_certificate.json'),
            'analytic_certificate_sha256': sha256(path / 'analytic_certificate.json'),
            'generator_sha256': sha256(path / 'generator.py')})
    assert len(evidence_hashes) == len(recipe_hashes) == len(code_hashes) == 1
    return protocol, records

def call(run_id, arguments):
    log = E / 'controller_logs' / (run_id + '.json')
    assert not log.exists(), 'Attempt already retained'
    started = now()
    result = subprocess.run([sys.executable, '-m', 'cohort_harness', *arguments], cwd=P,
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    new(log, {'started_utc': started, 'ended_utc': now(), 'arguments': arguments,
              'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    if result.returncode:
        raise RuntimeError('Failed attempt retained: ' + run_id)
    print('completed', run_id, flush=True)

def source():
    protocol, records = anchors()
    for record in records:
        label = record['label']
        ids = []
        for seed in protocol['source_seeds']:
            rid = f'{label}_{seed}'
            ids.append(rid)
            call(rid, ['source-replay', '--bundle', str(B), '--candidate', label,
                '--replay-id', rid, '--seed', str(seed), '--runtime', str(P / 'work/m2-runtime-config.json'),
                '--timeout-seconds', str(protocol['execution_timeout_seconds'])])
        report = summarize_source_portfolio(B, B / 'candidates' / label, ids, protocol['source_seeds'])
        new(E / 'source_feedback' / f'{label}_portfolio.json', report)
    manifest(False)

def source_verified(protocol):
    tables, portfolios = [], []
    for label in protocol['labels']:
        for seed in protocol['source_seeds']:
            rid = f'{label}_{seed}'
            report = verify_source_replay(B, rid, candidate=B / 'candidates' / label)
            assert report['status'] == 'success' and report['limits']['seed'] == seed
            rp = B / 'source_replays' / rid / 'replay.json'
            for context in protocol['source_contexts']:
                child = B / 'source_replays' / rid / 'contexts' / context / 'bundle'
                output, observed = child / 'executions/replay/output/generated.csv', child / 'observed.csv'
                tables.append({'label': label, 'seed': seed, 'context': context, 'replay_id': rid,
                    'path': str(output), 'sha256': sha256(output),
                    'observed_path': str(observed), 'observed_sha256': sha256(observed),
                    'replay_report_path': str(rp), 'replay_report_sha256': sha256(rp)})
        path = E / 'source_feedback' / f'{label}_portfolio.json'
        portfolios.append({'label': label, 'path': str(path), 'sha256': sha256(path)})
    return tables, portfolios

def probe():
    protocol, records = anchors()
    source_verified(protocol)
    gate = read_json(E / protocol['source_gate_result'])
    assert gate[protocol['source_gate_pass_field']] is True, 'Source screen failed: stop, no probe execution'
    new(E / 'probe_authorization.json', {'created_utc': now(),
        'source_commitment_sha256': sha256(E / 'source_commitment.json'),
        'source_gate_result_sha256': sha256(E / protocol['source_gate_result']),
        'all_paired_source_checks_passed': True,
        'scope': 'Synthetic model-separation probe; no real target outcomes'})
    for record in records:
        label = record['label']
        for seed in protocol['probe_seeds']:
            rid = f'{label}_{seed}'
            call(rid, ['execute', '--bundle', str(B), '--candidate', label,
                '--run-id', rid, '--seed', str(seed), '--runtime', str(P / 'work/m2-runtime-config.json'),
                '--timeout-seconds', str(protocol['execution_timeout_seconds'])])
            receipt = verify_execution(B, rid)
            assert receipt['status'] == 'success' and receipt['limits']['seed'] == seed
    manifest(True)

def manifest(complete):
    protocol, records = anchors()
    sources, portfolios = source_verified(protocol)
    probes = []
    if complete:
        assert (E / 'probe_authorization.json').is_file()
        for label in protocol['labels']:
            for seed in protocol['probe_seeds']:
                rid = f'{label}_{seed}'
                receipt = verify_execution(B, rid)
                assert receipt['status'] == 'success'
                assert receipt['candidate'] == f'candidates/{label}' and receipt['limits']['seed'] == seed
                path = B / 'executions' / rid / 'output/generated.csv'
                probes.append({'label': label, 'seed': seed, 'run_id': rid,
                               'path': str(path), 'sha256': sha256(path)})
    analysis = E / protocol['analysis_script']
    gate = E / protocol['gate_file']
    result = {'created_utc': now(), 'scope': 'constructive_synthetic_probe_no_real_target',
        'authorize_source_analysis': True, 'authorize_probe_analysis': complete,
        'labels': protocol['labels'], 'source_seeds': protocol['source_seeds'],
        'probe_seeds': protocol['probe_seeds'], 'source_contexts': protocol['source_contexts'],
        'bundle_path': str(B), 'protocol_path': str(E / 'protocol.json'),
        'protocol_sha256': sha256(E / 'protocol.json'),
        'protocol_commitment_path': str(E / 'protocol_commitment.json'),
        'protocol_commitment_sha256': sha256(E / 'protocol_commitment.json'),
        'gate_path': str(gate), 'gate_sha256': sha256(gate),
        'analysis_script_path': str(analysis), 'analysis_script_sha256': sha256(analysis),
        'observed_path': str(B / 'observed.csv'), 'observed_sha256': sha256(B / 'observed.csv'),
        'candidates': records, 'portfolios': portfolios, 'sources': sources, 'probes': probes}
    path = E / ('evaluation_commitment.json' if complete else 'source_commitment.json')
    new(path, result)
    print('committed', path.name, sha256(path), flush=True)

if __name__ == '__main__':
    phase = sys.argv[1]
    if phase == 'source':
        source()
    elif phase == 'probe':
        probe()
    else:
        raise ValueError('Unknown phase')
