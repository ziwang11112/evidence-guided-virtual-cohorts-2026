"""Metadata-only branch submission; never imports or calls the generator."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
from fractions import Fraction
import sys

sys.dont_write_bytecode = True
W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
P = W / 'biomedical_research/virtual_cohort_system'
PACKET = W / 'evcDC/ledger/packets/A01_self_review'
BUNDLE = W / 'evcDC/A01'
CANDIDATE = BUNDLE / 'candidates/self_review'
REPORT = P / 'work/developmental_continuation_v1_2026-11-03/branch_submissions/A01_self_review'
PACKET_SHA = 'fb1311a17ec99f5d51a9907d0687e99c1ad13e78a33f180d21c4fd3a5f74a6c1'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, key
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=reject_duplicates)

def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')

def metadata_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, PACKET / 'original_inputs' / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

manifest = read(PACKET / 'manifest.json')
assert manifest['constructor'] == 'A01' and manifest['branch'] == 'self_review'
assert manifest['numerical_feedback'] is False and manifest['source_feedback_sha256'] is None
file_results = {name: digest(PACKET / name) == expected for name, expected in manifest['files'].items()}
assert all(file_results.values())
assert digest(BUNDLE / 'task.json') == digest(PACKET / 'task.json')
assert digest(BUNDLE / 'registry.json') == digest(PACKET / 'registry.json')
assert digest(P / 'cohort_harness/contracts.py') == digest(PACKET / 'original_inputs/007_contracts.py')
assert digest(P / 'work/qualified_author_preflight_v1_2026-11-03/qualified_author_preflight.py') == digest(PACKET / 'original_inputs/025_qualified_author_preflight.py')
CANDIDATE.mkdir(parents=True, exist_ok=False)
for source in (PACKET / 'initial').iterdir():
    assert source.is_file()
    (CANDIDATE / source.name).write_bytes(source.read_bytes())

bridge_path = CANDIDATE / 'context_bridge_v1.json'
bridge_path.write_bytes(bridge_path.read_bytes().replace(b'A01_initial_', b'A01_self_review_'))
bridge, original_bridge = read(bridge_path), read(PACKET / 'initial/context_bridge_v1.json')
restored = copy.deepcopy(bridge)
for trial in restored['trials']:
    trial['id'] = trial['id'].replace('A01_self_review_', 'A01_initial_', 1)
assert restored == original_bridge
for context in ('J', 'B', 'M', 'T'):
    rows = [t for t in bridge['trials'] if t['context_id'] == context]
    assert [t['seed'] for t in rows] == ([41911, 41912, 41913] if context == 'T' else [41011, 41012, 41013])
    assert all(t['n_rows'] == 3000 for t in rows)
    assert all(t['id'] == f"A01_self_review_{context}_{t['seed']}" for t in rows)

binding = {
    'schema_version': 1, 'constructor': 'A01', 'branch': 'self_review',
    'packet_sha256': PACKET_SHA, 'manifest_sha256': digest(PACKET / 'manifest.json'),
    'initial_source_feedback_sha256': None, 'numerical_source_feedback_supplied': False,
    'initial_freeze_sha256_from_manifest': manifest['initial_freeze_sha256'],
    'binding_scope': 'Assigned packet identifier and raw manifest SHA256; all manifest member hashes checked. No source feedback was supplied or accessed. No freeze or approval is asserted.'
}
write(CANDIDATE / 'INPUT_BINDING.json', binding)

spec, evidence = read(CANDIDATE / 'model_spec.json'), read(CANDIDATE / 'evidence.json')
laws = read(CANDIDATE / 'scientific_validity_v1.json')
support = read(CANDIDATE / 'support_selection_v1.json')
support_contract = read(PACKET / 'requirements/support_contract.json')
moment_module = metadata_module('a01_self_moment_metadata', '021_scientific_validity_v1.py')
support_module = metadata_module('a01_self_support_metadata', '017_support_selection_v1.py')
evidence_module = metadata_module('a01_self_evidence_metadata', '019_evidence_use_v1.py')
moment_result = {key: moment_module.assess_law(value) for key, value in laws['context_laws'].items()}
assert all(r['manifest_valid'] and all(a['second_moment_status'] == 'pass' for a in r['analyses']) for r in moment_result.values())
support_result = support_module.assess_support_selection(
    support, required_contexts=support_contract['required_contexts'], required_checks=support_contract['required_checks'],
    known_provenance={'evidence': [i['id'] for i in evidence['items']],
                     'assumption': [a['id'] for a in spec['assumptions']],
                     'definition': support_contract['definition_ids']})
assert support_result['status'] == 'declaration_checks_pass'
evidence_result = evidence_module.assess_evidence_use(read(CANDIDATE / 'evidence_use_v1.json'), evidence, spec,
    recipe_check_ids=[c['id'] for context in bridge['contexts'] if context['recipe'] is not None for c in context['recipe']['checks']])
assert evidence_result['declaration_valid']

syntax = ast.parse((CANDIDATE / 'generator.py').read_text(encoding='utf-8-sig'))
functions = [node for node in syntax.body if isinstance(node, ast.FunctionDef) and node.name == 'generate']
assert len(functions) == 1 and len(functions[0].args.args) == 3
F = lambda x: Fraction(str(x))
p = spec['parameters']
support_algebra = {}
for context, descriptor in p['contexts'].items():
    x = descriptor['inputs']
    lo = F(p['innovations']['uniform_lower']) if context == 'J' else -F(p['innovations']['gamma_center'])
    hi = F(p['innovations']['uniform_upper']) if context == 'J' else None
    a, b, scale = F(p['glucose_on_bmi']), F(p['hba1c_on_glucose']), F(x['bmi_sd'])
    gs, rs = F(x['glucose_independent_scale']), F(x['residual_scale'])
    bounds = {}
    for endpoint, innovation in [('lower', lo), ('upper', hi)]:
        vals = {'bmi': None, 'glucose': None, 'hba1c': None}
        if innovation is not None:
            vals['bmi'] = F(x['bmi_location']) + scale * innovation
            vals['glucose'] = F(x['glucose_location']) + (a * scale + gs) * innovation
            vals['hba1c'] = F(x['hba1c_location']) + (b * (a * scale + gs) + rs) * innovation
        for variable, value in vals.items():
            declared = support['contexts'][context]['final_supports'][variable]['domain'][endpoint]
            assert (None if declared is None else F(declared)) == value
        bounds[endpoint] = {name: None if value is None else str(value) for name, value in vals.items()}
    assert x['age_lower'] < x['age_upper'] and 0 < x['female_probability'] < 1 and scale > 0 and gs > 0 and rs > 0
    support_algebra[context] = {'exact_decimal_affine_endpoints_match_declaration': True, 'bounds': bounds,
        'population_rank_conditions': 'Nondegenerate independent age and membership; positive triangular BMI/glucose scales. Empirical rank not assessed.'}

eligibility = {'schema_version': 1, 'contexts': {}}
for context, descriptor in p['contexts'].items():
    d = p['required_domains'][context]
    conditions = [{'column': 'age', 'op': 'ge', 'value': d['age_lower']},
                  {'column': 'age', 'op': 'le', 'value': d['age_upper']},
                  {'column': 'female', 'op': 'ge', 'value': 0},
                  {'column': 'female', 'op': 'le', 'value': 1}]
    conditions += [{'column': name, 'op': 'gt', 'value': 0} for name in d['positive_columns']]
    if d['glucose_upper_exclusive'] is not None:
        conditions.append({'column': 'glucose', 'op': 'lt', 'value': d['glucose_upper_exclusive']})
    if d['hba1c_lower_inclusive'] is not None:
        conditions.append({'column': 'hba1c', 'op': 'ge', 'value': d['hba1c_lower_inclusive']})
    eligibility['contexts'][context] = {'output_conditions': conditions,
        'unobserved_selection_assumptions': [f'A_{context}_SELECTION'],
        'notes': ['Metadata restatement of the retained model required_domains; no new selection or scientific law.',
                  'Age is integer and female is integer 0/1 under the unchanged task and generator. Conditions on absent variables are assumed, not verified.']}
write(CANDIDATE / 'context_eligibility.json', eligibility)

retained_names = [name for name in manifest['files'] if name.startswith('initial/') and name not in {'initial/decision.md', 'initial/context_bridge_v1.json'}]
unchanged = {name.removeprefix('initial/'): digest(CANDIDATE / name.removeprefix('initial/')) == manifest['files'][name] for name in retained_names}
assert all(unchanged.values())
static = {'scope': 'metadata_and_declared_law_only', 'packet_member_hashes_match': file_results,
    'manifest_sha256': binding['manifest_sha256'], 'retained_scientific_file_hashes_match': unchanged,
    'schedule_difference': 'Only twelve branch trial identity prefixes changed; seeds, context IDs, rows, limits and budgets unchanged.',
    'generator_ast_syntax_and_signature': 'pass_without_import_or_execution',
    'moment_checks': moment_result, 'support_declaration_checks': support_result,
    'static_affine_endpoint_checks': support_algebra, 'evidence_use_declaration_checks': evidence_result,
    'historical_checks_newly_claimed': False, 'generated_or_sampled_rows': False,
    'source_statistics_calculated': False, 'target_analysis_performed': False,
    'limits': ['Declared-law checks do not certify arbitrary-code correspondence, source authenticity, empirical rank, floating runtime behavior, transport or scientific utility.',
               'No numerical feedback was supplied. No original source estimator, fresh evidence or target outcome was reconstructed.']}
write(CANDIDATE / 'STATIC_REVIEW_CHECKS.json', static)

reason = ('Retain the inherited direct eligible-population law as a bounded, explicitly assumption-dependent construction. '
          'Static review preserves separate Jansen projections and native Pearson/Spearman meanings; it identifies no algebraic or support defect requiring a scientific change. '
          'The packet supplies no numerical source feedback and does not identify age/sex dependence, a replacement rank-dependence law, or target transport parameters. '
          'Changing those components here would exchange disclosed assumptions without evidence that the replacement supports the intended analyses better.')
limitations = [
    'A_BMI and A_GLUCOSE retain partial evidence coverage and unverified population, measurement, selection and joint-distribution transport; A_AGE remains unassessed.',
    'Age and female independence, no direct BMI term in HbA1c, uniform/gamma shape choices and source age distributions remain unsupported assumptions.',
    'Bao medians are approximate location anchors and its HbA1c quartiles are not fitted; MIND Spearman is a prospective native diagnostic with no claimed analytic equality.',
    'Shared Jansen coefficients and MIND biomarker settings in T remain transport hypotheses, not target measurements or evidence-supported causal effects.',
    'Strict source replay remains unavailable because original weights and processing are unknown. Qualified comparison metadata does not establish exact source recovery.',
    'No generator execution, random sampling, source statistic computation, retained-row check, empirical rank check or target analysis was performed by this author.',
    'Individual residual variability and repeated seeds do not quantify evidence, model or transport uncertainty; researcher-exposed CHNS is developmental, not fresh confirmation.'
]
decision = {'action': 'retain', 'packet_sha256': PACKET_SHA, 'reason': reason,
    'addressed_findings': [
        'Reviewed the separate Jansen adjusted projections under the declared no-direct-BMI factorization; preserved their distinct operators and adjustment sets.',
        'Reviewed native HbA1c mapping, plasma/serum distinctions, Pearson versus Spearman semantics, direct eligibility and final affine supports; preserved the scientific declarations.',
        'Kept source ages, Bao quartiles, rank fidelity, age/sex dependence and target transport explicitly unresolved rather than filling the gaps with unsupported estimates.',
        'Rebound the assigned immutable packet and updated the twelve branch trial IDs while preserving all scientific code, specification, evidence and scheduled seeds.'
    ], 'remaining_limitations': limitations}
write(REPORT / 'decision.json', decision)
decision_text = '''# A01 self-review decision: retain

Retain generator.py and model_spec.json byte-for-byte from the assigned accepted initial packet. This is a new bounded scientific decision on inherited science, not a fresh construction or a claim of improved data. The packet supplies no numerical source feedback.

The separate Jansen projections are coherent under the disclosed no-direct-BMI factorization: the glucose projection is beta and the BMI projection is beta*alpha, with age/female independent. These are identities of the proposed final joint law, not proof that the factorization describes a source or target population. Retain the native NGSP-to-IFCC response map and its offset; it creates no plasma/serum or assay equivalence. Bao Pearson remains the qualified residual-scale initialization, while MIND Spearman remains a native rank diagnostic with average ties and no claimed analytic equality. A Pearson implication of a linear model cannot substitute for the MIND rank functional.

The direct eligible-population construction supplies the declared positive biomarker supports and the J glucose restriction without clipping or reconstructed exclusions. The bounded uniform and centered-gamma choices remain unverified shape assumptions. All required second moments exist in the declared grammar; nondegenerate independent age/membership and the positive triangular biomarker scales support nonsingular population designs. Neither statement guarantees runtime success or empirical design rank.

There are substantial unresolved limitations. Source age summaries are unfitted. Bao medians are approximate locations and its HbA1c quartiles are not fitted. Age/sex independence and the absence of a direct BMI term are not reported relationships. Transferring Jansen alpha/beta and MIND biomarker locations/dispersions to T does not establish target applicability. A_BMI and A_GLUCOSE remain partial; A_AGE remains unassessed. Strict replay stays unavailable. Original unknown weights, source row processing, MIND imputation and estimator uncertainty remain unknown. Repeated rows and seeds are not independent clinical evidence or uncertainty about transport. CHNS remains researcher-exposed developmental reference.

The fixed packet does not identify a defensible replacement dependence or transport law. Retaining the inspectable construction preserves these limitations for the bounded controller evaluation; it does not endorse clinical use, causal interpretation, recovery of participant values or publication readiness. No sign, coefficient or favorable draw was selected. The scientific opportunity is closed with this retain decision.

Only bridge trial IDs change from A01_initial to A01_self_review; all seeds, rows, limits and budgets remain fixed. The same accepted initial is the intended parent for controller freeze. The added context_eligibility.json only restates the retained required_domains and unobserved-selection assumptions. All other scientific declarations, including evidence bytes, are unchanged. INPUT_BINDING.json binds the assigned packet; checks.json records work actually performed here. Historical checks are not represented as newly run. No generator import, simulation, source/target execution, target analysis, independent approval, freeze or execution receipt was performed or written by this author.
'''
(CANDIDATE / 'decision.md').write_text(decision_text, encoding='utf-8')

checks = {'scope': 'source_only', 'records': [
    {'name': 'assigned_packet_and_retained_bytes', 'status': 'pass', 'detail': 'Verified every manifest member hash, bundle task/registry equality, and eight unchanged scientific files including evidence, generator and full specification. Bound artifacts contain the actual metadata-only results.'},
    {'name': 'fixed_schedule_and_branch_identity', 'status': 'pass', 'detail': 'All twelve trials preserve context, seed and n_rows=3000; restored identity prefixes reproduce the original bridge object exactly.'},
    {'name': 'declared_moments_support_and_evidence_use', 'status': 'pass', 'detail': 'Ran the packet pure assess_law, assess_support_selection and assess_evidence_use APIs; checked exact decimal affine endpoints and generator AST without importing it. Scope is declaration checks only; full scientific validity remains unresolved.'},
    {'name': 'empirical_output_and_source_target_utility', 'status': 'not_computable', 'detail': 'No generator import/execution, random sampling, source statistics, retained-row testing or target analysis was performed. No empirical quality improvement is claimed.'}
], 'artifacts': [{'path': name, 'sha256': digest(CANDIDATE / name)} for name in ['INPUT_BINDING.json', 'STATIC_REVIEW_CHECKS.json']]}
write(CANDIDATE / 'checks.json', checks)
print(json.dumps({'candidate': str(CANDIDATE), 'decision': 'retain', 'packet_members_verified': len(file_results),
                  'unchanged_scientific_files': len(unchanged), 'declared_moment_analyses': 12,
                  'support_checks': len(support_result['checks']), 'candidate_bytes': sum(f.stat().st_size for f in CANDIDATE.rglob('*') if f.is_file())}, indent=2))
