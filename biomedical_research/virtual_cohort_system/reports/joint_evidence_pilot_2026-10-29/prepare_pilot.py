"""Import only admitted sources, visible observations and inherited candidates."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

E = Path(__file__).resolve().parent
P = E.parents[1]
OLD = P / 'work/analysis-evidence-gap-2026-10-29'
B = E / 'agent_bundle'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def new(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')

def main():
    B.mkdir(exist_ok=False)
    registry = json.loads((OLD / 'agent_bundle/registry.json').read_text())
    for item in registry['artifacts']:
        src = OLD / 'agent_bundle' / item['path']
        assert sha(src) == item['sha256']
        dst = B / item['path']
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    new(B / 'registry.json', registry)
    shutil.copyfile(OLD / 'agent_bundle/observed.csv', B / 'observed.csv')
    task = json.loads((OLD / 'agent_bundle/task.json').read_text())
    task['task_id'] = 'joint-evidence-pilot-tg-2026-10-29'
    task['budget']['revisions'] = 1
    new(B / 'task.json', task)
    src = OLD / 'agent_bundle/candidates/evidence_augmented'
    dst = B / 'candidates/baseline'
    files = {}
    for f in sorted(src.rglob('*')):
        if not f.is_file() or f.name == 'freeze.json' or '__pycache__' in f.parts:
            continue
        rel = f.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, out)
        files[rel.as_posix()] = sha(f)
    new(E / 'baseline_import.json', {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'origin': str(src), 'historical_freeze_sha256': sha(src / 'freeze.json'),
        'files': files, 'observed_sha256': sha(B / 'observed.csv'),
        'scope': 'No scientific change; source maps/checks retain historical provenance. '
                 'No hidden outcomes or target analyses imported. Baseline has the same '
                 'M7 evidence registry available but no new scientific revision.'})
    new(E / 'pilot_intent.json', {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'variants': ['baseline', 'joint_evidence'],
        'source_seeds': [80201,80202,80203],
        'target_seeds': [80101,80102,80103],
        'purpose': 'Test whether an Agent source-informed joint-structure revision changes '
                   'unprovided scientific analyses in a reserved public-data period.',
        'primary_uses': ['age association', 'BMI curvature'],
        'secondary_uses': ['all predeclared joint subgroup summaries and ordered contrasts'],
        'scope': 'Exploratory evidence/structure update; not a same-information ordinary-Agent comparison.',
        'no_target_feedback': True,
        'source_replay_role': 'Report all fixed diagnostics; no unplanned fitting or seed selection.',
        'generation_route': 'Frozen source-informed program, isolated WSL/bubblewrap execution only.',
        'target_status': 'M7 reserved reference not analyzed or released; outcome analyses only after commitments.'})
    print(json.dumps({'bundle': str(B), 'copied_candidate_files': len(files),
                      'registered_source_artifacts': len(registry['artifacts'])}))

if __name__ == '__main__':
    main()
