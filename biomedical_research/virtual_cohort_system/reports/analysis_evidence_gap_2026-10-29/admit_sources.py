"""Curator approval of two independently inspected primary source artifacts.

Approval permits referencing the documents; it is not approval to use their
numbers as calibrated target coefficients.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import read_json, sha256


def main():
    b = E / 'agent_bundle'
    manifest = read_json(E / 'research/source_artifact_manifest.json')
    records = {x['file']: x for x in manifest['artifacts']}
    registry = read_json(b / 'registry.json')
    if len(registry['artifacts']) != 4:
        raise ValueError('Unexpected existing registry; never repeat admission')
    original_hash = sha256(b / 'registry.json')
    approved = []
    for name, source in [('PMC10308115.xml', 'Mikkelsen2023_Tromso7'),
                         ('PMC13491077.xml', 'Zhang2026_ChinaPAR')]:
        src, dst = E / 'research' / name, b / 'sources' / name
        if sha256(src) != records[name]['sha256'] or dst.exists():
            raise ValueError('Source mismatch or duplicate admission')
        shutil.copyfile(src, dst)
        entry = {'source_id': source, 'path': 'sources/' + name, 'sha256': sha256(dst),
                 'origin': 'curator', 'screening': 'approved'}
        registry['artifacts'].append(entry)
        approved.append({**entry, 'url': records[name]['url']})
    (b / 'registry.json').write_text(json.dumps(registry, indent=2) + '\n', encoding='utf-8')
    audit = {'created_utc': datetime.now(timezone.utc).isoformat(),
        'prior_registry_sha256': original_hash, 'new_registry_sha256': sha256(b / 'registry.json'),
        'approved': approved, 'prior_registry_prefix_preserved': True,
        'review': 'Primary XML source identity, study cohort, measured variables, units and '
                  'Table3 coefficients inspected independently by controller. Neither document '
                  'uses NHANES. No target outcomes consulted. Missing Tromso supplement not admitted.',
        'restriction': 'Permitted contextual/partial evidence, not calibrated target-parameter updates. '
                       'Unresolved SD scaling, longitudinal transfer and meal/adjustment differences retained.'}
    with (E / 'source_admission.json').open('x', encoding='utf-8') as stream:
        json.dump(audit, stream, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
