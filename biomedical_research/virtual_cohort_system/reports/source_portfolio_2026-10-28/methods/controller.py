"""Run the declared source-only schedule; never load a target outcome/evaluator."""
from pathlib import Path
import json
import subprocess
import sys

project = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project))
from cohort_harness.lifecycle import read_json, sha256
from cohort_harness.source_portfolio import summarize_source_portfolio, compare_source_portfolios

root = Path(__file__).parent
bundle = root / 'agent_bundle'
protocol_path = root / 'protocol.json'
commit = root / 'protocol_commitment.json'
if not commit.exists():
    raise RuntimeError('Pre-execution protocol commitment required')
assert read_json(commit)['protocol_sha256'] == sha256(protocol_path)
protocol = read_json(protocol_path)
assert protocol['target_outcomes_or_target_analyses_permitted'] is False
stage = sys.argv[1]
assert stage in protocol['candidate_names']
logs = root / 'logs'
logs.mkdir(exist_ok=True)
seeds = protocol['source_seeds']
ids = [f'{stage}_{s}' for s in seeds]
for seed, replay_id in zip(seeds, ids):
    record = logs / (replay_id + '.json')
    if record.exists():
        raise RuntimeError('Run already attempted: ' + replay_id)
    args = [sys.executable, '-m', 'cohort_harness', 'source-replay', '--bundle', str(bundle),
            '--candidate', stage, '--replay-id', replay_id, '--seed', str(seed),
            '--runtime', str(project / 'work/m2-runtime-config.json')]
    result = subprocess.run(args, cwd=project, capture_output=True, text=True, encoding='utf-8', errors='replace')
    with record.open('x', encoding='utf-8') as stream:
        json.dump({'args': args, 'returncode': result.returncode, 'stdout': result.stdout,
                   'stderr': result.stderr}, stream, indent=2)
    if result.returncode:
        raise RuntimeError('Source replay failed; inspect ' + str(record))
    print('completed', replay_id, flush=True)
report = summarize_source_portfolio(bundle, bundle / 'candidates' / stage, ids, seeds)
report['protocol_sha256'] = sha256(protocol_path)
feedback = root / (stage + '_portfolio.json')
with feedback.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, indent=2, allow_nan=False)
print('portfolio', len(report['checks']), str(feedback), sha256(feedback), flush=True)
if stage == 'final':
    comparison = compare_source_portfolios(bundle, bundle / 'candidates/initial', bundle / 'candidates/final',
        [f'initial_{s}' for s in seeds], ids, seeds)
    with (root / 'comparison.json').open('x', encoding='utf-8') as stream:
        json.dump(comparison, stream, indent=2, allow_nan=False)
    print('paired comparison saved', flush=True)
