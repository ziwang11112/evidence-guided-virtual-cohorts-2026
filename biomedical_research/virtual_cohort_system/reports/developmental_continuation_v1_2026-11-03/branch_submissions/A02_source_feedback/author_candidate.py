"""One retain submission; only metadata, static algebra and supplied feedback.

Never imports the submitted generator, generates rows, or accesses target data.
"""
import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
P = W / 'biomedical_research/virtual_cohort_system'
PACKET = W / 'evcDC/ledger/packets/A02_source_feedback'
BUNDLE = W / 'evcDC/A02'
CANDIDATE = BUNDLE / 'candidates/source_feedback'
REPORT = P / 'work/developmental_continuation_v1_2026-11-03/branch_submissions/A02_source_feedback'
PACKET_HASH = '1d114453095a165a182bd9c226c19cf5e84859b02ecb448ce8b90aa6bf5a6c7e'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def canonical(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def pure_module(filename, name):
    path = PACKET / 'original_inputs' / filename
    module_spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[name] = module
    module_spec.loader.exec_module(module)
    return module


manifest = read(PACKET / 'manifest.json')
assert canonical(manifest) == PACKET_HASH
packet_checks = []
for name, expected in manifest['files'].items():
    actual = digest(PACKET / name)
    assert actual == expected, name
    packet_checks.append({'path': name, 'sha256': actual, 'matches_manifest': True})
for name in ('task.json', 'registry.json'):
    assert digest(BUNDLE / name) == digest(PACKET / name)
feedback = read(PACKET / 'initial_source_feedback.json')
assert canonical(feedback['source_feedback']['packet']) == manifest['source_feedback_sha256']
assert feedback['source_feedback']['packet_sha256'] == manifest['source_feedback_sha256']
CANDIDATE.mkdir(parents=True, exist_ok=False)
initial_names = [name for name in manifest['files'] if name.startswith('initial/')]
assert len(initial_names) == 10
for name in initial_names:
    (CANDIDATE / Path(name).name).write_bytes((PACKET / name).read_bytes())
bridge = read(CANDIDATE / 'context_bridge_v1.json')
original_bridge = read(PACKET / 'initial/context_bridge_v1.json')
for trial in bridge['trials']:
    assert trial['id'] == f"A02_initial_{trial['context_id']}_{trial['seed']}"
    trial['id'] = f"A02_source_feedback_{trial['context_id']}_{trial['seed']}"
write(CANDIDATE / 'context_bridge_v1.json', bridge)
for old, new in zip(original_bridge['trials'], bridge['trials']):
    assert {k: v for k, v in old.items() if k != 'id'} == {k: v for k, v in new.items() if k != 'id'}
    assert new['n_rows'] == 3000
assert {k: v for k, v in bridge.items() if k != 'trials'} == {k: v for k, v in original_bridge.items() if k != 'trials'}
for context in ('J', 'B', 'M', 'T'):
    assert [x['seed'] for x in bridge['trials'] if x['context_id'] == context] == (
        [41911, 41912, 41913] if context == 'T' else [41011, 41012, 41013])

binding = {
    'schema_version': 1, 'constructor': 'A02', 'branch': 'source_feedback',
    'packet_path': str(PACKET), 'packet_sha256': PACKET_HASH,
    'packet_sha256_convention': 'canonical sorted compact JSON of manifest.json',
    'manifest_sha256': digest(PACKET / 'manifest.json'),
    'initial_source_feedback_sha256': digest(PACKET / 'initial_source_feedback.json'),
    'source_feedback_payload_sha256': canonical(feedback['source_feedback']['packet']),
    'accepted_initial_freeze_sha256': manifest['initial_freeze_sha256'],
    'scope': 'Binds the supplied immutable packet; not a new execution, approval, or independent signature.'}
write(CANDIDATE / 'INPUT_BINDING.json', binding)

spec = read(CANDIDATE / 'model_spec.json')
evidence = read(CANDIDATE / 'evidence.json')
p = spec['parameters']
s = p['shared']
contexts = p['contexts']
native_sd = contexts['J']['inputs']['margins']['hba1c']['scale'] / s['ngsp_percent_per_ifcc']
sg = contexts['B']['inputs']['margins']['glucose']['scale']
sh = contexts['B']['inputs']['margins']['hba1c']['scale']
rb = contexts['B']['inputs']['glucose_hba1c_latent_correlation']
rm = contexts['M']['inputs']['glucose_hba1c_latent_correlation']
source_algebra = {
    'Q_J_bmi': {'ideal_formula': 'sd_IFCC * r_bh / sd_BMI; age and female independent',
                'calculated': native_sd * s['latent_bmi_hba1c_correlation'] / contexts['J']['inputs']['margins']['bmi']['scale'], 'reported': 0.13},
    'Q_J_fpg': {'ideal_formula': 'sd_IFCC * r_gh / sd_FPG; separate age/female-adjusted projection',
                'calculated': native_sd * contexts['J']['inputs']['glucose_hba1c_latent_correlation'] / contexts['J']['inputs']['margins']['glucose']['scale'], 'reported': 2.29},
    'Q_B_pearson': {'ideal_formula': 'expm1(r_gh*sg*sh)/sqrt(expm1(sg^2)*expm1(sh^2)); additive HbA1c shift does not change correlation',
                    'calculated': math.expm1(rb*sg*sh)/math.sqrt(math.expm1(sg*sg)*math.expm1(sh*sh)), 'reported': 0.619},
    'Q_M_spearman': {'ideal_formula': '6/pi*asin(r_gh/2); continuous Gaussian copula with strictly increasing margins',
                     'calculated': 6/math.pi*math.asin(rm/2), 'reported': 0.529}}
for row in source_algebra.values():
    row['floating_arithmetic_difference'] = row['calculated'] - row['reported']
    assert abs(row['floating_arithmetic_difference']) < 1e-12

law_module = pure_module('021_scientific_validity_v1.py', 'a02_branch_declared_law')
support_module = pure_module('017_support_selection_v1.py', 'a02_branch_support_metadata')
use_module = pure_module('019_evidence_use_v1.py', 'a02_branch_evidence_use')
laws = read(CANDIDATE / 'scientific_validity_v1.json')
law_reports = {context: law_module.assess_law(law) for context, law in laws['context_laws'].items()}
for report in law_reports.values():
    assert report['manifest_valid']
    assert all(a['second_moment_status'] == 'pass' for a in report['analyses'])
support_contract = read(PACKET / 'requirements/support_contract.json')
support_report = support_module.assess_support_selection(
    read(CANDIDATE / 'support_selection_v1.json'),
    required_contexts=support_contract['required_contexts'],
    required_checks=support_contract['required_checks'],
    known_provenance={'evidence': [x['id'] for x in evidence['items']],
                      'assumption': [x['id'] for x in spec['assumptions']],
                      'definition': support_contract['definition_ids']})
assert support_report['status'] == 'declaration_checks_pass'
use_report = use_module.assess_evidence_use(read(CANDIDATE / 'evidence_use_v1.json'), evidence, spec,
    recipe_check_ids=[c['id'] for context in bridge['contexts'] if context['role'] == 'source' for c in context['recipe']['checks']])
assert use_report['declaration_valid']
ast.parse((CANDIDATE / 'generator.py').read_text())
unchanged_names = [Path(name).name for name in initial_names if Path(name).name not in ('context_bridge_v1.json', 'decision.md')]
unchanged = {name: digest(CANDIDATE / name) for name in unchanged_names}
assert all(value == digest(PACKET / 'initial' / name) for name, value in unchanged.items())

inherited = []
for report in feedback['source_feedback']['packet']['reports']:
    inherited.append({'trial_id': report['trial_id'], 'context_id': report['context_id'],
        'status': report['status'], 'error': report['error'],
        'execution_diagnostic': report['execution_diagnostic'],
        'strict_checks': [{k: c[k] for k in ('id','status','semantic_status','unavailable_reason','difference','monte_carlo_uncertainty')} for c in report['feedback']['checks']],
        'qualified_checks': [{'id': c['id'], 'status': c['status'], 'unavailable_reason': c['unavailable_reason'],
            'reported': c['reported_evidence']['estimate'], 'calculation': c['calculation'],
            'raw_difference': c['raw_difference'], 'exact_source_check_allowed': c['exact_source_check_allowed']}
            for c in report['qualified_feedback']['checks']]})
support_rows = [row for report in feedback['source_eligibility']['support_checks'] for row in report['report']['checks']]
feedback_inspection = {
    'scope': 'Complete supplied initial feedback inspected; no recalculation from generated rows and no new source execution.',
    'input_binding': binding,
    'trials': inherited,
    'source_phase': feedback['source_feedback']['packet']['source_phase'],
    'support_reports': [{'run_id': r['run_id'], **r['report']} for r in feedback['source_eligibility']['support_checks']],
    'inherited_target_eligible': feedback['source_eligibility']['target_eligible'],
    'inherited_eligibility_reasons': feedback['source_eligibility']['reasons'],
    'source_point_fit_required': feedback['source_eligibility']['source_point_fit_required'],
    'interpretation': 'Eligibility is a supplied procedural result, not target performance or branch admission.',
    'strict_limitations': sorted({x for r in feedback['source_feedback']['packet']['reports'] for x in r['feedback']['limitations']}),
    'qualified_limitations': sorted({x for r in feedback['source_feedback']['packet']['reports'] for x in r['qualified_feedback']['limitations']})}
write(REPORT / 'INHERITED_FEEDBACK_INSPECTION.json', feedback_inspection)
static = {'scope': 'metadata_and_static_algebra_only',
    'packet_files_verified': packet_checks,
    'task_registry_match_packet': True,
    'retained_scientific_file_sha256': unchanged,
    'schedule_only_trial_identity_changed': True,
    'source_algebra': source_algebra,
    'source_algebra_limitations': 'Floating evaluation of ideal assumed population identities, not source data re-estimation or proof that discrepancies are Monte Carlo error. Unknown source processing and transport remain.',
    'declared_law_reports': law_reports,
    'support_declaration_report': support_report,
    'evidence_use_report': use_report,
    'generator_ast_parse': 'pass_without_import_or_execution',
    'inherited_feedback_inspection_sha256': digest(REPORT / 'INHERITED_FEEDBACK_INSPECTION.json'),
    'inherited_feedback_counts': {'source_trials': len(inherited),
        'qualified_results': sum(len(r['qualified_checks']) for r in inherited),
        'strict_results': sum(len(r['strict_checks']) for r in inherited),
        'retained_support_checks': len(support_rows)},
    'scientific_validity': 'not_certified', 'generator_executed_by_branch_author': False,
    'target_data_or_analysis_access': False}
write(CANDIDATE / 'AUTHOR_STATIC_CHECKS.json', static)

reason = ('Retain the accepted initial scientific law. All nine supplied source trials succeeded, all twelve qualified results were available, '
          'and each of the four raw discrepancy vectors spans zero. Static source algebra preserves the published functionals under the existing assumptions. '
          'The feedback supplies no structural defect or additional information identifying age/sex relationships, distribution shapes, or transport; '
          'changing parameters to remove these fixed-seed deviations would target realized source draws without resolving those limitations.')
addressed = [
    'Inspected all nine initial trial reports, twelve qualified comparisons, twelve unavailable strict checks, execution diagnostics and all 96 retained support checks; preserved every discrepancy.',
    'Checked the separate Jansen covariance-to-slope identities, Bao shifted-lognormal Pearson identity and MIND Gaussian-copula Spearman identity using unchanged constants; no generator import, sampling or fitted adjustment.',
    'Retained direct eligible laws, source-native aliases and NGSP/IFCC mapping, exact comparison/analysis IDs, source selection assumptions and fixed seed/row schedule.',
    'Bound the complete immutable input packet and initial feedback by SHA256, with a separate fresh metadata/static check record; inherited execution was not relabelled as newly performed work.'
]
limitations = [
    'Strict replay remains not_computable because original weights, analytic rows and processing are unresolved; MIND filling/tie details and Bao quantile conventions remain unknown.',
    'Raw differences are descriptive. Monte Carlo uncertainty was not estimated, original source precision is not supplied, and no interval-membership rule, pooled loss or statistical adequacy threshold is used.',
    'A_BMI and A_GLUCOSE retain partial assumption-dependent support; A_AGE remains unassessed. Assumed age/sex independence is not evidence of a null age effect.',
    'Latent BMI-glucose correlation 0.25, cross-source BMI-HbA1c transport, target composition and mixed-source target margins/dependence remain assumptions.',
    'Bao quartile asymmetry, coarsened source ages, latent-family choices, tails, and unobserved exclusions are not identified or validated by these four comparisons.',
    'HbA1c unit conversion and context-specific glucose aliases do not establish assay, fasting protocol or plasma/serum equivalence.',
    'Supplied eligibility and retained-frame support success do not establish population support or target utility. No branch source/target generation, target analysis, causal validation or calibration was performed.',
    'CHNS remains a researcher-exposed developmental reference; retaining the model creates a paired repeat, not a new independent scientific model or fresh confirmation.'
]
write(REPORT / 'decision.json', {'action': 'retain', 'packet_sha256': PACKET_HASH,
    'reason': reason, 'addressed_findings': addressed, 'remaining_limitations': limitations})

rows = []
for identifier in ('Q_J_bmi','Q_J_fpg','Q_B_pearson','Q_M_spearman'):
    values = [c for r in inherited for c in r['qualified_checks'] if c['id'] == identifier]
    rows.append('| ' + identifier + ' | ' + str(values[0]['reported']) + ' | ' +
                ' / '.join(f"{c['calculation']['value']:.9f}" for c in values) + ' | ' +
                ' / '.join(f"{c['raw_difference']:+.9f}" for c in values) + ' |')
decision_text = '''# A02 source-feedback decision: retain

Retain generator.py and the complete model_spec.json byte-for-byte. Preserve the accepted initial evidence, law, support, analysis-use, evidence-use and qualified declarations. Only the twelve bridge trial identities change to A02_source_feedback; seeds, rows, resources, budgets and scientific schedule are unchanged. Both branch lineage and accepted-initial hash are for the controller to bind; this author does not freeze or approve.

The complete supplied feedback contains nine successful source trials and twelve available qualified comparisons. All 96 retained support checks pass for their recorded rows, with no reported nonfinite/out-of-domain values or mutation/filtering. The supplied initial target-eligibility flag is true; target attempts are zero, target release is unauthorized, and transport validity is unassessed. These are inherited observations, not newly performed checks or target results.

All source comparisons are retained below, ordered by seeds 41011 / 41012 / 41013. Differences are calculated minus reported in the original native units: J BMI in mmol/mol/(kg/m^2), J FPG in mmol/mol/(mmol/L), and both correlations dimensionless.

| Comparison | Published point | Supplied calculated values | Supplied raw differences |
|---|---:|---|---|
''' + '\n'.join(rows) + '''

Each discrepancy vector has both signs. This observation does not estimate Monte Carlo uncertainty or prove absence of bias. The initial law already supplies the separate Jansen population slopes through covariance ratios under age/sex independence, Bao Pearson through the shifted-lognormal identity, and MIND Spearman through the continuous Gaussian-copula identity. Static evaluation of these existing formulas reproduces the four published points to decimal arithmetic precision. The relatively larger J BMI deviation at seed 41011 is retained, not screened out or offset by retuning. Three simulated draws do not create new source-study precision, and the printed Jansen intervals are not used as pass bounds.

Retaining keeps a transparent assumption-defined whole-cohort construction available for the fixed developmental evaluation. A revision to match these realized draws would alter an already specified population identity without new evidence about source processing or target transport. No numerical feedback here identifies a replacement law. This is not a claim that the current law is realistic, optimal, transportable or improved.

The scientific choices remain the bounded affine uniform-factor J law and Gaussian-factor lognormal/shifted-lognormal B/M/T laws, with independently assigned age and female. Source means/SDs and quartiles initialize margins under declared assumptions; source age coarsening and Bao asymmetric quartiles are only approximations. Native IFCC conversion remains a unit representation; J/B plasma, M serum and T central-serum meanings remain distinct. Direct eligible laws assume exclusions on unobserved variables and do not reconstruct selection. No clipping, retry, replacement seed, imputation or deletion is introduced.

A_BMI and A_GLUCOSE remain partial and assumption-dependent; A_AGE remains unassessed. Unreported age/sex relationships, the assumed BMI-glucose latent correlation, transferred BMI-HbA1c association, tails and mixed-source target law remain unsupported. Strict checks remain not_computable for unresolved original weighting/processing, including MIND filling/ties. Passing supplied retained-row supports is not a proof of population support. No precision weights, source confidence score, synthetic patient inference or causal interpretation is supplied.

Fresh checks are limited to packet/file bindings, retained-byte and schedule checks, generator AST parsing, source-only static algebra, pure declaration moment/support/evidence-use checks, and the actual metadata validate/preflight commands recorded in checks.json. Declared finite moments do not alone prove code correspondence or nonsingular sampled design. The full feedback remains outside this candidate and is bound by INPUT_BINDING.json. No new execution, simulation, generated table, hidden fitting pilot, literature search or target analysis was performed. No independent review, freeze or execution receipt was authored. Stop editing after this single retain submission and its metadata checks; no claim of data improvement is made.
'''
(CANDIDATE / 'decision.md').write_text(decision_text, encoding='utf-8')
checks = {'scope': 'source_only', 'records': [
    {'name':'packet_and_retained_bytes','status':'pass','detail':'Verified canonical assigned packet hash, every manifest file hash, full feedback file/payload hashes, task/registry identity and eight retained scientific files. See INPUT_BINDING.json and AUTHOR_STATIC_CHECKS.json.'},
    {'name':'branch_schedule','status':'pass','detail':'Only twelve bridge trial IDs changed; all contexts, seeds, n_rows=3000, budgets, limits and non-trial bridge metadata unchanged.'},
    {'name':'static_source_algebra','status':'pass','detail':'Evaluated the four existing source-only ideal population identities with math arithmetic; no generator import, sampling or target coefficient calculation. This is not exact source replay.'},
    {'name':'declared_moments_support_evidence_use','status':'pass','detail':'Pure packet-provided validators report finite required second moments, declaration support checks and evidence-use references passing. Full scientific validity remains unresolved and code/transport require independent review.'},
    {'name':'generator_syntax','status':'pass','detail':'Parsed generator.py with ast.parse only; body was never imported or executed.'},
    {'name':'initial_feedback_inspection','status':'pass','detail':'Inspected all supplied initial trial diagnostics, qualified values/raw discrepancies, strict unavailability and eligibility/support limitations. Counts and external inspection-report hash are in AUTHOR_STATIC_CHECKS.json; full feedback bound in INPUT_BINDING.json. No historical execution is claimed as new.'},
    {'name':'strict_source_replay','status':'not_computable','detail':'Original weights, source-row processing and MIND filling/ties unresolved; qualified results do not upgrade strict status.'},
    {'name':'branch_empirical_output_and_transport','status':'not_computable','detail':'No author-side generator execution, sampling, branch-source results or target data/analysis. Neither metadata acceptance nor inherited source fit establishes target utility.'}],
    'artifacts': [{'path': name, 'sha256': digest(CANDIDATE/name)} for name in ('INPUT_BINDING.json','AUTHOR_STATIC_CHECKS.json')]}
write(CANDIDATE/'checks.json',checks)
print(json.dumps({'candidate': str(CANDIDATE), 'action': 'retain',
    'source_algebra': source_algebra, 'inherited_support_checks': len(support_rows),
    'candidate_bytes': sum(x.stat().st_size for x in CANDIDATE.iterdir() if x.is_file())},indent=2))
