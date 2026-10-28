"""Verify exported HDL commitments and aggregates without opening omitted inputs."""
import csv
import json
from pathlib import PurePosixPath

PREFIX = 'biomedical_research/evidence_gap_loop_2026-10-28/'


def audit_gap_loop(root, records, findings):
    selected = {p: r for p, r in records.items() if p.startswith(PREFIX)}
    if not selected:
        return {'included': False}

    def fail(name, rule):
        findings.append({'file': PREFIX+name, 'rule': rule})

    def read(name):
        return json.loads((root/PREFIX/name).read_text(encoding='utf-8-sig'))

    def commitment(name, expected, require=True):
        key = name if name.startswith(PREFIX) else PREFIX+name
        record = selected.get(key)
        if record is None:
            if require:
                fail(name, 'gap_loop_missing_committed_export')
            return False
        if record['source_sha256'] != expected:
            fail(name, 'gap_loop_source_commitment_mismatch')
        return True

    for key, record in selected.items():
        name = key[len(PREFIX):]
        path = PurePosixPath(name)
        if (name.startswith(('custodian/raw/', 'custodian/locked/', 'custodian/documentation/', 'tools/smoke_neutral/'))
                or 'literature' in path.parts or '__pycache__' in path.parts
                or '_response.' in name or path.suffix in {'.xpt', '.xml', '.html', '.htm', '.xlsx', '.pyc'}
                or path.suffix == '.csv' and not record.get('aggregate_table')
                or 'outputs' in path.parts and path.name != 'execution.json'):
            fail(name, 'gap_loop_excluded_payload')

    receipt = json.loads((root/'sync/GAP_LOOP_EXPORT_RECEIPT_2026-10-28.json').read_text())
    if len(selected) != receipt['source_files']:
        fail('RESULTS.md', 'gap_loop_inventory_mismatch')
    commitment('RESULTS.md', receipt['final_results_source_sha256'])
    release = read('custodian/evaluation_release.json')
    frozen = read('all_outputs_freeze.json')
    commitment('all_outputs_freeze.json', release['all_outputs_freeze_sha256'])
    commitment('custodian/analysis_spec.json', release['analysis_spec_sha256'])
    commitment('custodian/evaluate.py', release['evaluator_sha256'])
    included = sum(commitment(name, expected, require=False) for name, expected in release['artifacts'].items())
    omitted = len(release['artifacts']) - included
    if len(release['artifacts']) != 189 or included != receipt['included_release_commitments_verified'] or omitted != receipt['omitted_release_commitments_retained_without_opening']:
        fail('custodian/evaluation_release.json', 'gap_loop_release_accounting')
    if frozen['artifacts'] != release['artifacts'] or frozen['outputs'] != release['outputs']:
        fail('all_outputs_freeze.json', 'gap_loop_release_freeze_mismatch')
    outputs = release['outputs']
    if len(outputs) != 40 or len({o['file'] for o in outputs}) != 40 or len({o['sha256'] for o in outputs}) != 25:
        fail('custodian/evaluation_release.json', 'gap_loop_scheduled_output_accounting')
    for run in ('ordinary_1', 'ordinary_2', 'gap_1', 'gap_2'):
        for stage in ('initial', 'final'):
            base = 'runs/'+run+'/'+stage+'/'
            candidate = read(base+'freeze.json')
            for group in ('commitment', 'run_commitment'):
                for name, expected in candidate[group].items():
                    commitment(name, expected, require=False)
            execution = read(base+'outputs/execution.json')
            commitment(base+'freeze.json', execution['candidate_freeze_sha256'])
            if len(execution['draws']) != 5 or [d['seed'] for d in execution['draws']] != list(range(281001, 281006)) or any(d['n_rows'] != 4885 for d in execution['draws']):
                fail(base+'outputs/execution.json', 'gap_loop_execution_accounting')

    analysis = read('custodian/results/analysis_results.json')
    commitment('custodian/evaluation_release.json', analysis['release_manifest_sha256'])
    datasets = [analysis['reference']] + analysis['generated']
    fits = sum(len(d['fits']) for d in datasets)
    endpoints = sum(len(d['endpoints']) for d in datasets)
    if len(datasets) != 41 or fits != 164 or endpoints != 328:
        fail('custodian/results/analysis_results.json', 'gap_loop_aggregate_accounting')
    report = read('report/report_manifest.json')
    for name, expected in report['files'].items():
        commitment('report/'+name, expected)
    for field, name in [('input_release_sha256', 'custodian/evaluation_release.json'),
                        ('input_analysis_sha256', 'custodian/results/analysis_results.json'),
                        ('reporting_plan_sha256', 'reporting_plan.json'),
                        ('script_sha256', 'make_report.py')]:
        commitment(name, report[field])
    narrative = read('review/postrun/final_narrative_review.json')
    for name, expected in narrative['inputs'].items():
        commitment(name, expected)
    if narrative['status'] != 'PASS' or not all(narrative['checks'].values()):
        fail('review/postrun/final_narrative_review.json', 'gap_loop_recorded_narrative_failure')
    audit = read('review/postrun/audit_report.json')
    if audit['status'] != 'PASS' or audit['counts']['numeric_mismatches'] or audit['counts']['failed_checks']:
        fail('review/postrun/audit_report.json', 'gap_loop_recorded_audit_failure')
    audit_hashes = read('review/postrun/audit_hashes.json')
    commitment('custodian/evaluation_release.json', audit_hashes['authorized_release_sha256'])
    commitment('review/postrun/independent_audit.py', audit_hashes['audit_source_sha256'])
    commitment('review/postrun/final_narrative_review.json', audit_hashes['final_narrative_review_sha256'])
    for section in ('inputs', 'outputs'):
        for name, expected in audit_hashes[section].items():
            commitment(name, expected, require=False)
    checks = {}
    for name in ('aggregate_discrepancies.csv', 'provenance_and_structure_checks.csv'):
        with (root/PREFIX/'review/postrun'/name).open(encoding='utf-8-sig', newline='') as stream:
            rows = list(csv.DictReader(stream))
        if not all(r['passed'].lower() == 'true' for r in rows):
            fail('review/postrun/'+name, 'gap_loop_recorded_check_failure')
        checks[name] = len(rows)
    return {'included': True, 'source_files': len(selected), 'source_release_commitments_verified': included,
            'omitted_commitments_retained_without_opening': omitted, 'scheduled_draws': len(outputs),
            'distinct_output_hashes': len({o['sha256'] for o in outputs}), 'aggregate_fits': fits,
            'aggregate_endpoints': endpoints, 'report_file_commitments_verified': len(report['files']),
            'recorded_checks': checks, 'experiments_or_numerical_audit_rerun': False,
            'path_normalizations': sum(r['transform'] != 'none' for r in selected.values())}
