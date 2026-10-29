"""Bind final M7 code/report/inspection artifacts without outcome access."""
from pathlib import Path
import json
import sys

E = Path(__file__).resolve().parent
P = E.parents[1]
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import read_json, sha256, verify_candidate


def main():
    c = P / 'reports/analysis_evidence_gap_2026-10-29'
    b = E / 'agent_bundle'
    tests = read_json(E / 'review/FULL_HARNESS_TESTS.json')
    if tests['returncode'] != 0 or '302 passed, 1 skipped' not in tests['stdout']:
        raise ValueError('Unexpected full-test result')
    for rel, h in tests['code_hashes'].items():
        if sha256(P / rel) != h:
            raise ValueError('Code changed after full tests: ' + rel)
    manifest = read_json(c / 'file_manifest.json')
    for rel, h in manifest.items():
        if sha256(c / rel) != h:
            raise ValueError('Curated artifact changed: ' + rel)
    retention = read_json(E / 'retention_freeze.json')
    for name, h in retention['candidate_freezes'].items():
        verify_candidate(b, b / 'candidates' / name)
        if sha256(b / 'candidates' / name / 'freeze.json') != h:
            raise ValueError('Retained freeze changed')
    for path in [b / 'source_replays', b / 'executions', E / 'custodian/evaluation', E / 'evaluation_commitment.json']:
        if path.exists():
            raise ValueError('Unexpected scientific execution or release')
    previous = read_json(P / 'm6_validation.json')['code_sha256']
    paths = set(previous) | {'cohort_harness/analysis_evidence.py', 'tests/test_analysis_evidence.py',
                             'docs/ANALYSIS_EVIDENCE.md'}
    paths |= {f.relative_to(P).as_posix() for f in c.rglob('*.py')}
    code = {rel: sha256(P / rel) for rel in sorted(paths)}
    changed = {rel: {'M6_sha256': previous[rel], 'M7_sha256': code[rel]}
               for rel in previous if previous[rel] != code[rel]}
    if set(changed) != {'cohort_harness/__main__.py', 'cohort_harness/lifecycle.py'}:
        raise ValueError('Unexpected prior code change')
    data = {
        'schema_version': 1, 'milestone': 'M7', 'date': '2026-10-29',
        'scope': 'analysis_evidence_map_and_source_insufficiency_retention_no_scientific_execution',
        'code_sha256': code, 'report_sha256': sha256(P / 'MILESTONE_7_RESULTS.md'),
        'curated_file_manifest_sha256': sha256(c / 'file_manifest.json'),
        'postrun_audit_sha256': sha256(c / 'review/RETENTION_AUDIT.md'),
        'audit_name_caveat': 'Postrun here means post static-check/review, not scientific generator run.',
        'tests': {'passed': 302, 'skipped': 1, 'exit_code': 0,
                  'skip': 'Existing Windows symlink fixture privilege limitation',
                  'receipt_sha256': sha256(c / 'review/FULL_HARNESS_TESTS.json')},
        'execution': {'scientific_generator_runs': 0, 'source_replays': 0, 'target_analyses': 0,
                      'fixture_tests_executed': True, 'post_target_tuning': False},
        'retention': {'kind': 'retain', 'scientific_bytes_unchanged': True,
                      'candidate_freezes': retention['candidate_freezes'],
                      'generator_sha256': retention['generator_sha256'],
                      'model_spec_sha256': retention['model_spec_sha256'],
                      'sources_before_after': [2, 4], 'evidence_items_before_after': [71, 79],
                      'analyses_per_map': 3, 'search_queries': 6,
                      'candidate_maps_built_after_retrieval': True,
                      'retention_freeze_sha256': sha256(c / 'retention_freeze.json')},
        'reserved_case': {'name': 'NHANES2009–2010', 'eligible_n': 1575, 'age_range': [40, 79],
                          'reference_variable': 'LBXTR', 'weight': 'WTSAF2YR',
                          'outcome_statistics_evaluated': False,
                          'custodian_parsed_rows_for_preparation_QC': True,
                          'raw_custodian_lock_sha256': sha256(E / 'custodian/custodian_lock.json'),
                          'independent_study': False},
        'boundary': {'outer_agent_OS_isolated': False, 'new_target_results_released_to_builder': False,
                     'patient_rows_exported': False, 'full_papers_exported': False,
                     'standalone_agent_launcher': False, 'scientific_advantage_established': False,
                     'curated_archive': 'Inspection only; inputs/full sources/runtime omitted.'},
        'prior_code_changes': changed,
        'historical_code_commit': '15787a0898562a7c7bebad7cbdcda124113af2f9',
        'future_evaluation_review_items': ['Global rank failure should emit nonestimability',
            'Clarify evaluation-only wording for reserved thresholds',
            'Do not count positive means/proportions as directional fidelity'],
        'local_cleanup': 'Failed-test scratch cleanup rejected by automatic approval review; '
                         'scratch retained locally and excluded from curated package.'}
    with (P / 'm7_validation.json').open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': 'passed', 'code_bindings': len(code), 'curated_files': len(manifest) + 1,
                      'report_sha256': data['report_sha256'], 'validation_sha256': sha256(P / 'm7_validation.json')}))


if __name__ == '__main__':
    main()
