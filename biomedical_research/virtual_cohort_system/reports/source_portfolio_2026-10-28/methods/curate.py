"""Copy an explicit aggregate/code allowlist; no source/target participant rows."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

root = Path(__file__).parent
project = root.parents[1]
destination = project / 'reports/source_portfolio_2026-10-28'
destination.mkdir(exist_ok=False)

def copy(source, relative):
    out = destination / relative
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, out)

for name in ('protocol.json', 'protocol_commitment.json', 'initial_portfolio.json',
             'final_portfolio.json', 'comparison.json', 'test_suite.txt'):
    copy(root / name, name)
raw_log = (root / 'test_suite.txt').read_bytes()
normalized_log, replacements = raw_log, 0
for prefix in (str(project).replace('\\', '\\\\'), str(project), project.as_posix()):
    encoded = prefix.encode()
    replacements += normalized_log.count(encoded)
    normalized_log = normalized_log.replace(encoded, b'<PROJECT>')
(destination / 'test_suite.txt').write_bytes(normalized_log)
(destination / 'test_log_normalization.json').write_text(json.dumps({
    'scope': 'current curated test log only; original work log retained',
    'normalization': 'two absolute workspace prefixes replaced with <PROJECT>; bytes otherwise unchanged',
    'replacement_count': replacements,
    'original_log_sha256': hashlib.sha256(raw_log).hexdigest(),
    'curated_log_sha256': hashlib.sha256(normalized_log).hexdigest()}, indent=2) + '\n', encoding='utf-8')
for name in ('controller.py', 'curate.py'):
    copy(root / name, 'methods/' + name)
for stage in ('initial', 'final'):
    candidate = root / 'agent_bundle/candidates' / stage
    for name in ('generator.py', 'model_spec.json', 'evidence.json', 'source_replay.json',
                 'decision.md', 'checks.json', 'freeze.json', 'revision.json'):
        if (candidate / name).is_file():
            copy(candidate / name, f'candidates/{stage}/{name}')
    for path in (candidate / 'checks').glob('*.json'):
        copy(path, f'candidates/{stage}/checks/{path.name}')
    for seed in (75101, 75102, 75103):
        copy(root / f'agent_bundle/source_replays/{stage}_{seed}/replay.json',
             f'receipts/{stage}_{seed}.json')

comparison = json.loads((root / 'comparison.json').read_text())
rows = []
for check in comparison['comparisons']:
    definition = check['definition']
    rows.append({'context': definition['context_id'], 'check': definition['check_id'],
                 'kind': definition['operator']['kind'], 'unit': definition['operator']['unit'],
                 'reported': definition['reported_value'],
                 'initial_mean': check['initial']['mean'], 'initial_min': check['initial']['minimum'],
                 'initial_max': check['initial']['maximum'],
                 'final_mean': check['revised']['mean'], 'paired_equal': check['paired_summary']['n_equal']})
with (destination / 'source_diagnostics.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)

pairs = []
for seed in (75101, 75102, 75103):
    a = json.loads((destination / f'receipts/initial_{seed}.json').read_text())
    b = json.loads((destination / f'receipts/final_{seed}.json').read_text())
    for left, right in zip(a['contexts'], b['contexts']):
        assert left['id'] == right['id']
        pairs.append({'seed': seed, 'context': left['id'], 'initial_output_sha256': left['generated_sha256'],
                      'final_output_sha256': right['generated_sha256'],
                      'identical': left['generated_sha256'] == right['generated_sha256']})
with (destination / 'output_identity.json').open('w', encoding='utf-8') as stream:
    json.dump({'scope': 'paired_source_execution_output_hashes', 'pairs': pairs}, stream, indent=2)
print(destination)
