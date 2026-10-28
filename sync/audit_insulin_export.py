"""Audit only exported code/aggregate metadata; never open omitted study rows."""
import json
from pathlib import PurePosixPath
import re

PREFIX = 'biomedical_research/insulin_feature_enrichment_2026-10-27/'
CSV_ALLOWLIST = {
    'results/evaluation_v1/endpoints.csv',
    'results/evaluation_v1/draw_summaries.csv',
    'results/report_v3/scientific_interpretation.csv',
    'review/postrun/independently_recomputed_endpoints.csv',
}


def audit_insulin(root, records, findings):
    selected = {p: r for p, r in records.items() if p.startswith(PREFIX)}
    if not selected:
        return {'included': False}

    def fail(path, rule):
        findings.append({'file': PREFIX + path, 'rule': rule})

    def read(name):
        return json.loads((root/PREFIX/name).read_text(encoding='utf-8-sig'))

    def committed(name, expected):
        key = name if name.startswith(PREFIX) else PREFIX+name
        entry = selected.get(key)
        if entry is None or entry['source_sha256'] != expected:
            fail(name, 'insulin_source_commitment_mismatch')
            return False
        return True

    for key, record in selected.items():
        name = key[len(PREFIX):]
        path = PurePosixPath(name)
        if (name.startswith(('agent/', 'literature/', 'custodian/raw/', 'custodian/documentation/'))
                or path.suffix == '.csv' and name not in CSV_ALLOWLIST
                or path.suffix in {'.xpt', '.html', '.htm', '.xlsx', '.pyc'}
                or '__pycache__' in path.parts
                or path.suffix == '.txt' and name != 'review/interface.txt'):
            fail(name, 'insulin_excluded_payload')
        if path.suffix not in {'.png', '.pdf'}:
            text = (root/key).read_text(encoding='utf-8-sig')
            if re.search(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', text, re.I):
                fail(name, 'unexpected_identity_literal')
        if path.suffix == '.csv' and not record.get('aggregate_table'):
            fail(name, 'missing_aggregate_schema')

    receipt = json.loads((root/'sync/INSULIN_EXPORT_RECEIPT.json').read_text())
    delivery = read('delivery_manifest.json')
    committed('delivery_manifest.json', receipt['source_delivery_manifest_sha256'])
    for name, expected in delivery['files'].items():
        committed(name, expected)
    if receipt['exported_files'] != len(selected) or len(delivery['files']) != 49:
        fail('delivery_manifest.json', 'insulin_inventory_count')
    committed('freeze_v1/outputs_freeze.json', delivery['output_freeze_sha256'])
    frozen = read('freeze_v1/outputs_freeze.json')
    included = omitted = 0
    for name, expected in frozen['files'].items():
        if name in selected:
            included += int(committed(name, expected))
        else:
            omitted += 1  # Commitment retained; intentionally do not open omitted data.
    evaluation_manifest = read('freeze_v1/evaluation_manifest.json')
    for field in ('analysis_spec', 'outputs_freeze'):
        artifact = evaluation_manifest[field]
        committed(artifact['path'], artifact['sha256'])
    draws = evaluation_manifest['draws']
    if len(draws) != 20 or [d['seed'] for d in draws] != list(range(270101, 270121)):
        fail('freeze_v1/evaluation_manifest.json', 'insulin_draw_accounting')
    for draw in draws:
        if draw['n_rows'] != 1700 or frozen['files'].get(draw['path']) != draw['sha256']:
            fail('freeze_v1/evaluation_manifest.json', 'insulin_draw_metadata_commitment')
    evaluation = read('results/evaluation_v1/evaluation.json')
    if evaluation['manifest_sha256'] != selected[PREFIX+'freeze_v1/evaluation_manifest.json']['source_sha256']:
        fail('results/evaluation_v1/evaluation.json', 'insulin_evaluation_manifest_binding')
    datasets = [evaluation['reference']] + evaluation['generated']
    fits = sum(len(d['fits']) for d in datasets)
    endpoints = sum(len(d['endpoints']) for d in datasets)
    if len(datasets) != 21 or fits != 84 or endpoints != 168:
        fail('results/evaluation_v1/evaluation.json', 'insulin_aggregate_accounting')
    postrun = read('review/postrun/audit_results.json')
    if postrun['status'] != 'PASS: numerical integrity and independent reproduction' or len(postrun['checks']) != 4237 or not all(c['passed'] for c in postrun['checks'] + postrun['hash_checks']):
        fail('review/postrun/audit_results.json', 'insulin_recorded_audit_failure')
    presentation = read('review/postrun/report_v3_checks.json')
    for name, expected in presentation['report_v3_sha256'].items():
        committed('results/report_v3/'+name, expected)
    # Its RESULTS digest is a historical audit snapshot; the final delivery above
    # seals the later link/readability-only prose revision. Preserve both records.
    return {'included': True, 'source_files': len(selected),
            'delivery_commitments_verified': len(delivery['files']),
            'included_freeze_commitments_verified': included,
            'omitted_freeze_commitments_retained_without_opening': omitted,
            'draw_metadata_verified': len(draws), 'aggregate_fits': fits,
            'aggregate_endpoints': endpoints,
            'recorded_independent_checks_passed': len(postrun['checks']),
            'independent_audit_rerun_in_export': False,
            'path_normalizations': sum(r['transform'] != 'none' for r in selected.values())}
