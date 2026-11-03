"""Metadata-only retain submission; never imports or executes the generator."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import math

W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
P = W / 'biomedical_research/virtual_cohort_system'
PACKET = W / 'evcDC/ledger/packets/A01_source_feedback'
BUNDLE = W / 'evcDC/A01'
CANDIDATE = BUNDLE / 'candidates/source_feedback'
REPORT = P / 'work/developmental_continuation_v1_2026-11-03/branch_submissions/A01_source_feedback'
PACKET_HASH = '718eba5a387e991235bdc1709e8da83f34156d668ae8142da2015f68b00a37d2'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


manifest = json.loads((PACKET / 'manifest.json').read_text())
assert canonical(manifest) == PACKET_HASH
verified_files = {}
for name, expected in manifest['files'].items():
    actual = sha(PACKET / name)
    assert actual == expected, name
    verified_files[name] = actual
for name in ['task.json', 'registry.json']:
    assert (BUNDLE / name).read_bytes() == (PACKET / name).read_bytes(), name

feedback = json.loads((PACKET / 'initial_source_feedback.json').read_text())
assert canonical(feedback['source_feedback']['packet']) == feedback['source_feedback']['packet_sha256']
assert feedback['source_feedback']['packet_sha256'] == manifest['source_feedback_sha256']
assert feedback['source_feedback']['packet']['target_results_included'] is False
assert feedback['source_feedback']['packet']['source_phase']['target_attempts'] == 0

CANDIDATE.mkdir(parents=True, exist_ok=False)
for source in (PACKET / 'initial').iterdir():
    assert source.is_file()
    (CANDIDATE / source.name).write_bytes(source.read_bytes())

bridge_path = CANDIDATE / 'context_bridge_v1.json'
bridge = json.loads(bridge_path.read_text())
original_bridge = copy.deepcopy(bridge)
for trial in bridge['trials']:
    assert trial['id'] == f"A01_initial_{trial['context_id']}_{trial['seed']}"
    trial['id'] = f"A01_source_feedback_{trial['context_id']}_{trial['seed']}"
write_json(bridge_path, bridge)
restored = copy.deepcopy(bridge)
for trial in restored['trials']:
    trial['id'] = f"A01_initial_{trial['context_id']}_{trial['seed']}"
assert restored == original_bridge
assert len(bridge['trials']) == 12
for context in ['J', 'B', 'M', 'T']:
    trials = [t for t in bridge['trials'] if t['context_id'] == context]
    expected = [41911, 41912, 41913] if context == 'T' else [41011, 41012, 41013]
    assert [t['seed'] for t in trials] == expected
    assert all(t['n_rows'] == 3000 for t in trials)

unchanged_names = ['generator.py', 'model_spec.json', 'evidence.json', 'analysis_evidence.json',
                   'evidence_use_v1.json', 'qualified_plan_v1.json', 'scientific_validity_v1.json',
                   'support_selection_v1.json']
unchanged = {}
for name in unchanged_names:
    assert (CANDIDATE / name).read_bytes() == (PACKET / 'initial' / name).read_bytes()
    unchanged[name] = sha(CANDIDATE / name)

spec = json.loads((CANDIDATE / 'model_spec.json').read_text())
parameters = spec['parameters']
tree = ast.parse((CANDIDATE / 'generator.py').read_text())
generate = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'generate']
assert len(generate) == 1
assert len(generate[0].args.args) == 3 and not generate[0].args.kwonlyargs
assert generate[0].args.vararg is None and generate[0].args.kwarg is None
assert len((CANDIDATE / 'generator.py').read_bytes()) <= 65536

qualified = json.loads((CANDIDATE / 'qualified_plan_v1.json').read_text())
assert all(d['bindings'] == {} for d in qualified['contexts'].values())
assert [c['id'] for d in qualified['contexts'].values() for c in d['checks']] == [
    'Q_J_bmi', 'Q_J_fpg', 'Q_B_pearson', 'Q_M_spearman']
analyses = json.loads((CANDIDATE / 'analysis_evidence.json').read_text())
assert [(a['id'], a['assessment']) for a in analyses['analyses']] == [
    ('A_BMI', 'partial'), ('A_GLUCOSE', 'partial'), ('A_AGE', 'unassessed')]

alpha, beta = parameters['glucose_on_bmi'], parameters['hba1c_on_glucose']
source_algebra = {}
for context in ['J', 'B', 'M']:
    x = parameters['contexts'][context]['inputs']
    innovation_variance = ((parameters['innovations']['uniform_upper'] -
                            parameters['innovations']['uniform_lower']) ** 2 / 12
                           if context == 'J' else 1.0)
    vg = innovation_variance * ((alpha * x['bmi_sd']) ** 2 + x['glucose_independent_scale'] ** 2)
    vh = beta ** 2 * vg + innovation_variance * x['residual_scale'] ** 2
    source_algebra[context] = {
        'calculation_scope': 'static scalar arithmetic on declared source-law parameters only',
        'glucose_variance': vg,
        'hba1c_variance': vh,
        'law_pearson_glucose_hba1c': beta * math.sqrt(vg / vh),
        'rank_correlation': 'not_calculated; Pearson is not substituted for Spearman',
    }
source_algebra['J']['native_fpg_projection'] = beta / parameters['ngsp']['percent_per_ifcc']
source_algebra['J']['native_bmi_projection'] = beta * alpha / parameters['ngsp']['percent_per_ifcc']

comparisons = []
for result in feedback['source_feedback']['packet']['reports']:
    for check in result['qualified_feedback']['checks']:
        comparisons.append({
            'trial_id': result['trial_id'], 'context_id': result['context_id'],
            'check_id': check['id'], 'status': check['status'],
            'reported_value': check['reported_evidence']['estimate'],
            'calculation': check['calculation'], 'raw_difference': check['raw_difference'],
            'strict_status': check['strict_result']['status'],
            'strict_unavailable_reason': check['strict_result']['unavailable_reason'],
            'qualified_unavailable_reason': check['unavailable_reason'],
            'unresolved_original_details': check['source_relation']['unresolved_original_details'],
        })
support = []
for entry in feedback['source_eligibility']['support_checks']:
    report = entry['report']
    support.append({
        'trial_id': entry['run_id'], 'context_id': report['context_id'],
        'status': report['status'], 'issues': report['issues'],
        'n_checks': len(report['checks']),
        'invalid_or_nonfinite': sum(c['invalid_or_nonfinite'] for c in report['checks']),
        'outside_required_domain': sum(c['outside_required_domain'] for c in report['checks']),
        'population_law_support_verified': report['population_law_support_verified'],
        'mutated_or_filtered': report['mutated_or_filtered'],
    })
write_json(REPORT / 'feedback_inspection.json', {
    'kind': 'inspection_of_supplied_initial_feedback_not_new_execution',
    'initial_source_feedback_file_sha256': sha(PACKET / 'initial_source_feedback.json'),
    'source_phase': feedback['source_feedback']['packet']['source_phase'],
    'comparison_count': len(comparisons), 'comparisons': comparisons,
    'support_reports': support,
    'source_eligibility': {k: v for k, v in feedback['source_eligibility'].items() if k != 'support_checks'},
    'limitations': sorted({s for r in feedback['source_feedback']['packet']['reports']
                           for key in ['feedback', 'qualified_feedback'] for s in r[key]['limitations']}),
    'new_source_or_target_execution': False,
})

binding = {
    'schema_version': 1, 'constructor': 'A01', 'branch': 'source_feedback',
    'packet_sha256': PACKET_HASH,
    'packet_hash_convention': 'SHA256 of sorted compact UTF-8 manifest JSON, ensure_ascii=False',
    'packet_path': str(PACKET),
    'manifest_sha256': sha(PACKET / 'manifest.json'),
    'initial_source_feedback_sha256': sha(PACKET / 'initial_source_feedback.json'),
    'source_feedback_payload_sha256': feedback['source_feedback']['packet_sha256'],
    'accepted_initial_freeze_sha256': manifest['initial_freeze_sha256'],
    'parent_candidate': 'initial',
    'binding_scope': 'Exact assigned bytes; hashes do not establish source truth or transport validity.',
}
write_json(CANDIDATE / 'INPUT_BINDING.json', binding)
write_json(CANDIDATE / 'author_static_checks.json', {
    'scope': 'metadata_and_source_law_scalar_arithmetic_only',
    'manifest_files_verified': len(verified_files), 'manifest_mismatches': [],
    'task_and_registry_match_assigned_packet': True,
    'unchanged_scientific_files_sha256': unchanged,
    'bridge_change': 'Only the twelve trial IDs change from A01_initial to A01_source_feedback.',
    'fixed_schedule_and_budgets_preserved': True,
    'ast_signature': 'One top-level synchronous generate(observed, spec, seed); parsed, not imported.',
    'fixed_qualified_ids_preserved': True, 'authored_qualified_bindings_empty': True,
    'analysis_assessments_preserved': {'A_BMI': 'partial', 'A_GLUCOSE': 'partial', 'A_AGE': 'unassessed'},
    'source_law_scalar_arithmetic': source_algebra,
    'independent_code_law_review': 'not_performed; historical reports are not claimed as new checks',
    'new_generator_import_or_execution': False, 'sampling': False,
    'target_analysis': False, 'empirical_output_validity': 'not_assessed_by_this_author',
})

decision_text = '''# A01 source-feedback branch: retain

Retain the accepted initial scientific law, generator and complete model specification byte-for-byte. The evidence, final-law/support declarations, native operators, mappings and analysis support labels also remain unchanged. The only bridge change is the twelve branch trial identities; seed IDs, row counts and budgets are fixed. This branch parents the accepted initial, never a sibling. Retention is a bounded developmental choice, not a declaration that the model adequately reproduces all source relationships.

The complete supplied initial feedback reports nine successful source draws, nine passing retained-support reports, and all twelve qualified comparisons available. No rows were filtered or repaired in those reports. Initial target eligibility is procedural: source-point fit was not required, population-law support was not verified by the retained-row checks, and transport validity remained unassessed. These are inherited packet results, not experiments performed by this author.

The qualified values for seeds 41011, 41012 and 41013, respectively, are:

| Comparison | Reported source point | Supplied initial values | Raw differences |
|---|---:|---|---|
| Q_J_bmi, mmol/mol per kg/m^2 | 0.13 | 0.110623, 0.134847, 0.130298 | -0.019377, +0.004847, +0.000298 |
| Q_J_fpg, mmol/mol per mmol/L | 2.29 | 2.241266, 2.318323, 2.162730 | -0.048734, +0.028323, -0.127270 |
| Q_B_pearson, dimensionless | 0.619 | 0.626858, 0.643560, 0.610783 | +0.007858, +0.024560, -0.008217 |
| Q_M_spearman, dimensionless | 0.529 | 0.305259, 0.324378, 0.279127 | -0.223741, -0.204622, -0.249873 |

All four strict replay definitions remain not_computable. Original weights and preprocessing are unknown; J's original intercept convention and numeric gender coding, and M's imputation/tie details, are not recovered. Qualified whole-table equal-weight operators preserve the separate age/gender-adjusted J projections, Bao Pearson, and MIND serum Spearman with average ties. The J native IFCC response uses the documented inverse percent map. No plasma/serum or assay equivalence follows from an alias or this scale map.

The MIND discrepancy is substantial and persists across all three supplied seeds. It is more consistent with a limitation of the assumed common glucose coefficient, independent residual and gamma joint structure than with a reason to select one favorable seed; the three draws do not identify the exact cause or provide a calibrated Monte Carlo test. It must not be dismissed as mere sampling fluctuation or relabelled as a Pearson comparison. The original law never derived the MIND rank point from its reported margins.

Static source-law arithmetic clarifies the trade-off. The shared coefficient is beta=0.2094892 and alpha=0.13/2.29; under the assumed independence these preserve the two separate J projection initializations. Bao's residual variance was initialized to its Pearson functional. In M, the fixed glucose SD 1.4 and HbA1c SD 1.0 with that shared beta imply a Pearson correlation near 0.293285, which is not the source Spearman statistic. Reducing M residual dispersion would change the source HbA1c variance initialization. Raising the shared beta would alter the J glucose projection and BMI projection unless other scientific assumptions also changed. A context-specific beta, dependent residual, mixture or copula could be proposed, but this packet does not select a unique version or its transfer to T. I therefore retain the transparent, partially supported law with the observed failure to reproduce M's rank point visible. No parameter is corrected by a feedback/source ratio and no Spearman-to-Pearson conversion is introduced.

The retained source means/individual SDs remain initializations, Bao medians remain approximate locations, and assumed scales, distribution families and tails remain assumptions. Age summaries and Bao HbA1c quartiles remain explicitly unfitted; numerical marginal feedback for them was not supplied. Age/female independence and the no-direct-BMI factorization are unsupported scientific restrictions. A_BMI and A_GLUCOSE remain partial; A_AGE remains unassessed. Target age/sex composition, shared associations and M biomarker transfer remain unverified. Source-only consistency cannot certify the requested target analyses, causal effects, individual recovery, measurement savings or publication readiness. The researcher-exposed CHNS developmental reference cannot provide fresh confirmation.

The author performed packet/hash checks, static parsing and source-law scalar arithmetic, and the metadata checks recorded in checks.json and AUTHOR_REPORT.md. No submitted generator was imported or executed, no rows were sampled, no fresh source search or target analysis was performed, and no review, freeze, execution receipt or approval was authored. Empirical branch output remains unevaluated; no improvement is claimed.
'''
(CANDIDATE / 'decision.md').write_text(decision_text, encoding='utf-8')

decision = {
    'action': 'retain', 'packet_sha256': PACKET_HASH,
    'reason': 'The supplied feedback exposes a persistent MIND Spearman discrepancy, but does not identify a unique defensible revision of the common joint law or its transfer to T. Retain the accepted scientific law as an explicitly partial developmental construction, preserving the discrepancy and all unsupported uses; numerical source eligibility is not adequacy.',
    'addressed_findings': [
        'Inspected all nine source trials, twelve qualified values and discrepancies, all strict unavailability reasons, execution diagnostics, support reports and eligibility limitations.',
        'Recorded MIND Spearman values 0.3052586801, 0.3243780294 and 0.2791273977 versus 0.529; retained this failure to reproduce the source rank point without changing the estimator.',
        'Retained J and Bao parameters because feedback does not reveal a concrete unit/estimator or implementation defect; their source-law projection/Pearson initializations remain distinct from finite-sample estimates.',
        'Explained why residual reduction, shared-slope change or a new dependence model would trade against existing moment/projection assumptions without uniquely identifying target transfer.',
        'Preserved fixed native mappings, qualified/analysis IDs, evidence bytes, schedule and unsupported scientific uses; bound the exact assigned packet and full feedback file hashes.',
    ],
    'remaining_limitations': [
        'MIND Spearman is materially under-reproduced across all supplied initial seeds; no formal sampling test or source precision weighting is available.',
        'All strict replay definitions remain unavailable because original weights/processing are unknown; M imputation and tie details remain unresolved.',
        'Age/female independence, no-direct-BMI structure, distribution shapes, tails, source age summaries and Bao HbA1c quartiles remain unsupported or unfitted.',
        'A_BMI and A_GLUCOSE are partial and A_AGE is unassessed; shared parameters and M-to-T biomarker transfer are unverified.',
        'Retained-row support and metadata passes do not establish population reconstruction, mathematical/code correctness, transport or scientific adequacy.',
        'No new generator execution, sampling, target analysis, independent review or empirical improvement assessment was performed by this author.',
    ],
}
write_json(REPORT / 'decision.json', decision)
write_json(CANDIDATE / 'checks.json', {
    'scope': 'source_only',
    'records': [
        {'name': 'packet_binding_and_retention', 'status': 'pass',
         'detail': 'Verified all 44 manifest-listed hashes and canonical packet hash; matched assigned task/registry and eight unchanged scientific files; bridge differs only by twelve trial IDs. See INPUT_BINDING.json and author_static_checks.json.'},
        {'name': 'static_source_law_and_signature', 'status': 'pass',
         'detail': 'Parsed generator AST without importing it and computed only scalar source-law moments/projection identities. No data generation, rank calculation or target analysis; this is not independent code-law certification.'},
        {'name': 'branch_empirical_output', 'status': 'not_computable',
         'detail': 'This author did not execute or sample the branch. Supplied initial feedback is inherited information, not a newly performed check; no branch-source or target quality claim is made.'},
    ],
    'artifacts': [{'path': name, 'sha256': sha(CANDIDATE / name)}
                  for name in ['INPUT_BINDING.json', 'author_static_checks.json']],
})
print(json.dumps({'action': 'retain', 'candidate': str(CANDIDATE),
                  'packet_files_verified': len(verified_files), 'inherited_comparisons_inspected': len(comparisons)}))
