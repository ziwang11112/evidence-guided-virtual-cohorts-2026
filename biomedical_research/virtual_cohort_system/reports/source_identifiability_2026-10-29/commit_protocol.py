"""Bind the complete reviewed protocol and code before any execution."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import verify_candidate

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    status = json.loads((E / 'review/PRE_EXECUTION_STATUS.json').read_text())
    assert status['status'] == 'passed'
    assert not (E / 'agent_bundle/source_replays').exists()
    assert not (E / 'agent_bundle/executions').exists()
    protocol = json.loads((E / 'protocol.json').read_text())
    files = ['protocol.json', 'controller.py', 'commit_protocol.py', 'prepare_bundle.py',
             'bundle_preparation.json', 'agent_bundle/task.json', 'agent_bundle/registry.json',
             'agent_bundle/observed.csv', 'design/BUILDER_PLAN.md', 'design/FREEZE_READINESS.json',
             'review/GATE_REVIEW.md', 'review/PRE_EXECUTION_AUDIT.md', 'review/PRE_EXECUTION_STATUS.json']
    files += [p.relative_to(E).as_posix() for p in sorted((E / 'analysis').iterdir())
              if p.is_file() and p.suffix in ('.py', '.json', '.md')]
    assert protocol['analysis_script'] in files and protocol['gate_file'] in files
    freezes = {}
    for label in protocol['labels']:
        path = E / 'agent_bundle/candidates' / label
        receipt = verify_candidate(E / 'agent_bundle', path)
        assert receipt['revision_index'] == 0
        freezes[label] = sha(path / 'freeze.json')
    record = {'schema_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Reviewed constructive source/probe protocol; no real target outcomes',
        'files': {relative: sha(E / relative) for relative in files},
        'core_files': {p.relative_to(P).as_posix(): sha(p) for p in sorted((P / 'cohort_harness').glob('*.py'))},
        'runtime_config_sha256': sha(P / 'work/m2-runtime-config.json'),
        'candidate_freezes': freezes}
    path = E / 'protocol_commitment.json'
    with path.open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': 'committed', 'sha256': sha(path), 'files': len(files)}))

if __name__ == '__main__':
    main()
