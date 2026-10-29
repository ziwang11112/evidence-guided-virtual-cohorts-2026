"""Prepare approved source inputs and an unchanged historical baseline.

No target outcomes or biological parameter choice occur in this preparation.
The custodian's visible table is copied only after its separate protocol lock.
"""
from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime, timezone

E = Path(__file__).resolve().parent
P = E.parents[1]
OLD = P / 'work/structure-robustness-2026-10-28/agent_bundle'
B = E / 'agent_bundle'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write('\n')


def prepare_sources():
    if B.exists():
        raise ValueError('Refuse to overwrite prepared bundle')
    B.mkdir()
    registry = json.loads((OLD / 'registry.json').read_text(encoding='utf-8-sig'))
    for entry in registry['artifacts']:
        src, dst = OLD / entry['path'], B / entry['path']
        if digest(src) != entry['sha256']:
            raise ValueError('Historical source changed')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    new(B / 'registry.json', registry)
    origin = OLD / 'candidates/s1_final'
    candidate = B / 'candidates/baseline'
    candidate.mkdir(parents=True)
    copied = {}
    for src in sorted(origin.rglob('*')):
        if not src.is_file() or src.name == 'freeze.json':
            continue
        relative = src.relative_to(origin)
        dst = candidate / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied[relative.as_posix()] = digest(src)
    new(E / 'baseline_import.json', {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'origin': str(origin), 'historical_freeze_sha256': digest(origin / 'freeze.json'),
        'files': copied,
        'scope': 'Historical source-only baseline; original code/spec unchanged. '
                 'Old source feedback is historical. No new target data or results imported.',
    })


if __name__ == '__main__':
    prepare_sources()
