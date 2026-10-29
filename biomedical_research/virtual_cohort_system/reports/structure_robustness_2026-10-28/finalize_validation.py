"""Bind the completed M5 inspection package and unchanged engine."""
from pathlib import Path
import hashlib
import json

E = Path(__file__).resolve().parent
P = E.parents[1]
C = P / 'reports/structure_robustness_2026-10-28'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    previous = read(P / 'm4_validation.json')
    code = dict(previous['code_sha256'])
    for relative, old_hash in code.items():
        assert sha(P / relative) == old_hash, relative
    for path in sorted(C.rglob('*.py')):
        code[path.relative_to(P).as_posix()] = sha(path)
    manifest = read(C / 'file_manifest.json')
    actual = {p.relative_to(C).as_posix(): sha(p) for p in C.rglob('*') if p.is_file() and p.name != 'file_manifest.json'}
    assert manifest == actual
    source = read(C / 'review/source_diagnostic_review.json')
    target = read(C / 'review/target_aggregate_audit.json')
    assert source['status'] == target['status'] == 'passed'
    assert target['post_release_model_hashes_unchanged'] is True
    guard = read(C / 'review/release_guard_verification.json')
    custody = read(C / 'methods/guard_validation_receipt.json')
    result = {
        'schema_version': 1, 'milestone': 'M5', 'date': '2026-10-28',
        'scope': 'frozen_structural_sensitivity_and_new_period_target_analyses',
        'code_sha256': code,
        'report_sha256': sha(P / 'MILESTONE_5_RESULTS.md'),
        'curated_file_manifest_sha256': sha(C / 'file_manifest.json'),
        'postrun_audit_sha256': sha(C / 'POSTRUN_AUDIT.md'),
        'tests': {
            'new_release_guard_checks_passed': guard['test_count'],
            'new_custodian_checks_passed': custody['tests_run'],
            'release_guard_scope': guard['scope'],
            'custodian_scope': custody['scope'],
            'historical_core_suite': {'milestone': 'M4', 'passed': 258, 'skipped': 1, 'rerun_this_milestone': False},
            'core_engine_and_previous_test_bytes_unchanged': True,
            'independent_aggregate_source_audit': 'passed',
            'independent_aggregate_target_audit': 'passed',
            'figure_visually_inspected': True,
            'independent_survey_package_crosscheck': False},
        'execution': {
            'agent_constructions': 1, 'structural_alternatives': 3,
            'candidate_versions': 6, 'source_replays': 18, 'source_context_executions': 36,
            'target_executions': 15, 'isolated_executions_total': 51,
            'source_checks_per_replay': 46, 'input_only_checks_per_replay': 12,
            'TG_dependent_checks_per_replay': 34, 'source_seeds': [76101,76102,76103],
            'target_seeds': [76201,76202,76203,76204,76205],
            'revision_decisions': {'s1': 'revise', 's2': 'retain', 's3': 'retain_source_challenged'},
            'release_commitment_sha256': target['release_manifest_sha256'],
            'aggregate_endpoint_rows': target['endpoint_rows_checked'],
            'aggregate_structure_summaries': target['structure_summary_rows_checked'],
            'nonestimable_sensitivities': target['nonestimable_sensitivities'],
            'post_release_model_changes': False},
        'target': {'period': 'NHANES August 2021-August 2023', 'domain_n': 2660,
            'full_positive_weight_design_n': 3361, 'strata': 15, 'PSUs': 30, 'df': 15,
            'replication_type': 'temporal_same_survey_program',
            'primary_direction_agreement': {'adjusted_age_per10': '15/15 positive', 'bmi_curvature_second_difference': '15/15 negative'},
            'raw_curvature_direction_agreement': '15/15 negative',
            'magnitude_and_interaction_limitations_retained': True},
        'inspection_boundary': {'builder_target_results_available': False,
            'outer_agent_OS_isolated': False, 'generator_backend': 'wsl_bubblewrap',
            'independent_reviewer_participant_rows_read': False,
            'source_compatibility_certified': False, 'ordinary_agent_superiority_tested': False,
            'individual_recovery_claim': False, 'row_data_exported': False,
            'curated_package': 'inspection_only_requires_omitted_inputs_and_original_layout_for_full_replay'}}
    destination = P / 'm5_validation.json'
    assert not destination.exists()
    destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'code_files': len(code), 'curated_files': len(manifest) + 1,
                      'report_sha256': result['report_sha256'], 'validation_sha256': sha(destination)}))

if __name__ == '__main__':
    main()
