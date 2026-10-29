"""Normalize copied metadata after export review; preserve all frozen originals."""
from pathlib import Path
import json
from datetime import datetime, timezone
from curate_results import E, P, C, normalize, sha256, read_json


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def main():
    prior = read_json(C / 'curation_provenance.json')
    old_manifest_hash = sha256(C / 'file_manifest.json')
    old_validation_hash = sha256(P / 'm7_validation.json')
    changes, records = [], []
    for old in prior['records']:
        src, dst = E / old['source_relative'], C / old['curated_relative']
        original_hash = sha256(src)
        if original_hash != old['original_sha256'] and old['source_relative'] != 'curate_results.py':
            raise ValueError('Unexpected original-file change')
        data, count = normalize(src.read_bytes(), old['scientific_bytes_preserved'])
        before = sha256(dst)
        dst.write_bytes(data)
        record = {**old, 'original_sha256': original_hash, 'copied_sha256': sha256(dst),
                  'path_replacements': count}
        records.append(record)
        if before != record['copied_sha256']:
            changes.append({'file': old['curated_relative'], 'old_copied_sha256': before,
                            'new_copied_sha256': record['copied_sha256']})
    src, dst = E / 'repair_curation.py', C / 'repair_curation.py'
    data, count = normalize(src.read_bytes())
    with dst.open('xb') as stream:
        stream.write(data)
    records.append({'source_relative': 'repair_curation.py', 'curated_relative': 'repair_curation.py',
        'original_sha256': sha256(src), 'copied_sha256': sha256(dst), 'path_replacements': count,
        'scientific_bytes_preserved': False})
    write(C / 'curation_provenance.json', {'scope': 'inspection_only', 'records': records})
    write(C / 'curation_repair.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
        'reason': 'Export review found escaped local runtime/test paths in four copied metadata files. '
                  'Normalize path prefixes at one, two, four and eight backslash-escape levels.',
        'previous_manifest_sha256': old_manifest_hash, 'previous_validation_sha256': old_validation_hash,
        'changed_copies': changes, 'frozen_candidate_and_custodian_originals_unchanged': True,
        'only_original_helper_changed': 'curate_results.py (normalization logic)',
        'scientific_execution_or_target_analysis': False})
    manifest = {p.relative_to(C).as_posix(): sha256(p) for p in sorted(C.rglob('*'))
                if p.is_file() and p.name != 'file_manifest.json'}
    write(C / 'file_manifest.json', manifest)
    validation = read_json(P / 'm7_validation.json')
    validation['code_sha256'] = {rel: sha256(P / rel) for rel in validation['code_sha256']}
    validation['code_sha256'][(C / 'repair_curation.py').relative_to(P).as_posix()] = sha256(C / 'repair_curation.py')
    validation['curated_file_manifest_sha256'] = sha256(C / 'file_manifest.json')
    validation['tests']['receipt_sha256'] = sha256(C / 'review/FULL_HARNESS_TESTS.json')
    validation['curation_repair_sha256'] = sha256(C / 'curation_repair.json')
    write(P / 'm7_validation.json', validation)
    print(json.dumps({'files': len(manifest) + 1, 'records': len(records),
        'normalized_files': sum(r['original_sha256'] != r['copied_sha256'] for r in records),
        'manifest_sha256': sha256(C / 'file_manifest.json'),
        'validation_sha256': sha256(P / 'm7_validation.json')}))


if __name__ == '__main__':
    main()
