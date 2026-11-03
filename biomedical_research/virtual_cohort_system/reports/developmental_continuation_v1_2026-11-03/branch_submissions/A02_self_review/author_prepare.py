"""One retain submission: packet reads, copies, metadata and scalar algebra only."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from fractions import Fraction

sys.dont_write_bytecode = True
W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
P = W / 'biomedical_research/virtual_cohort_system'
PACKET = W / 'evcDC/ledger/packets/A02_self_review'
BUNDLE = W / 'evcDC/A02'
C = BUNDLE / 'candidates/self_review'
R = P / 'work/developmental_continuation_v1_2026-11-03/branch_submissions/A02_self_review'
PACKET_HASH = '4bcc795378485e85e9185f5afbe3289cc7e3220cb24a8ae95e9fc6e5f061afe0'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique)

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')

def module(filename, name):
    path = PACKET / 'original_inputs' / filename
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value

R.mkdir(parents=True, exist_ok=True)
manifest = read(PACKET / 'manifest.json')
inventory = []
for relative, expected in manifest['files'].items():
    path = PACKET / relative
    raw = path.read_bytes()
    content = raw.decode('utf-8-sig')
    actual = hashlib.sha256(raw).hexdigest()
    assert actual == expected, relative
    row = {'path': relative, 'sha256': actual, 'bytes': len(raw)}
    if path.suffix == '.json':
        parsed = json.loads(content, object_pairs_hook=unique)
        row['json_root_keys'] = list(parsed)
    elif path.suffix == '.py':
        tree = ast.parse(content, filename=relative)
        row['static_symbols'] = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    inventory.append(row)
assert manifest['constructor'] == 'A02' and manifest['branch'] == 'self_review'
assert manifest['numerical_feedback'] is False and manifest['source_feedback_sha256'] is None
assert digest(BUNDLE / 'task.json') == manifest['files']['task.json']
assert digest(BUNDLE / 'registry.json') == manifest['files']['registry.json']
write(R / 'packet_read_inventory.json', {'scope': 'Assigned packet only; all listed bytes read, JSON parsed and Python parsed as AST without execution.', 'files': inventory})

C.mkdir(parents=True, exist_ok=False)
for source in (PACKET / 'initial').iterdir():
    assert source.is_file()
    shutil.copyfile(source, C / source.name)
bridge_path = C / 'context_bridge_v1.json'
raw_bridge = bridge_path.read_bytes()
assert raw_bridge.count(b'A02_initial_') == 12
bridge_path.write_bytes(raw_bridge.replace(b'A02_initial_', b'A02_self_review_'))

spec = read(C / 'model_spec.json')
evidence = read(C / 'evidence.json')
bridge = read(bridge_path)
qualified = read(C / 'qualified_plan_v1.json')
laws = read(C / 'scientific_validity_v1.json')['context_laws']
support = read(C / 'support_selection_v1.json')
required = read(PACKET / 'requirements/support_contract.json')
p = spec['parameters']
shared = p['shared']
assert set(p['contexts']) == set(laws) == set(support['contexts']) == {'J', 'B', 'M', 'T'}
assert p['contexts']['T']['population'] == read(BUNDLE / 'task.json')['population']
expected_trials = [('J', s) for s in (41011,41012,41013)] + [('B', s) for s in (41011,41012,41013)] + [('M', s) for s in (41011,41012,41013)] + [('T', s) for s in (41911,41912,41913)]
assert [(t['context_id'], t['seed']) for t in bridge['trials']] == expected_trials
assert all(t['id'] == 'A02_self_review_' + t['context_id'] + '_' + str(t['seed']) and t['n_rows'] == 3000 for t in bridge['trials'])
assert bridge['budget'] == {'source_attempts':9,'source_rows':27000,'target_attempts':3,'target_rows':9000}
assert bridge['execution_limits'] == {'timeout_seconds':60,'memory_mb':1536,'output_bytes':4000000,'log_bytes':20000}
assert all(q['bindings'] == {} for q in qualified['contexts'].values())
assert [q['id'] for ctx in qualified['contexts'].values() for q in ctx['checks']] == ['Q_J_bmi','Q_J_fpg','Q_B_pearson','Q_M_spearman']
analysis = read(C / 'analysis_evidence.json')
assert {a['id']:a['assessment'] for a in analysis['analyses']} == {'A_BMI':'partial','A_GLUCOSE':'partial','A_AGE':'unassessed'}
for ctx in bridge['contexts']:
    if ctx['role'] == 'source':
        assert ctx['feedback_policy'] == 'semantic_v1' and ctx['supplement'] is None
        assert ctx['recipe']['population'] == p['contexts'][ctx['id']]['population']
        assert ctx['recipe']['measurement']['description'] == p['contexts'][ctx['id']]['measurement']
        assert all(q['status'] == 'not_computable' and q['operator'] is None for q in ctx['recipe']['checks'])
        assert all(q['weights'] == 'not_reported' and q['source_operator'] is None for q in ctx['semantics']['bindings'])

eligibility = {'schema_version':1, 'contexts':{}}
for ctx, desc in p['contexts'].items():
    values = desc['inputs']['age_law']['values']
    assumptions = {'J':'A_J_SELECTION','B':'A_B_SELECTION','M':'A_M_SELECTION','T':'A_T_TRANSPORT'}
    conditions = [{'column':'age','op':'ge','value':min(values)}, {'column':'age','op':'le','value':max(values)}, {'column':'female','op':'ge','value':0}, {'column':'female','op':'le','value':1}]
    if ctx == 'J':
        conditions.append({'column':'glucose','op':'lt','value':7.0})
    eligibility['contexts'][ctx] = {'output_conditions':conditions, 'unobserved_selection_assumptions':[assumptions[ctx]], 'notes':['Metadata restatement of the unchanged direct eligible law and task integer/binary schema; no rows were generated or inspected.', 'Absent exclusion variables are assumed, not verified. Target has no additional diabetes, treatment or pregnancy exclusion.' if ctx == 'T' else 'Source eligibility and measurement details remain as declared in the unchanged model assumptions; observed support conditions cannot verify absent exclusions.']}
write(C / 'context_eligibility.json', eligibility)

static = {'schema_version':1, 'scope':'Metadata and deterministic scalar algebra only; no submitted generator import, random draw, table, source-output comparison or target analysis.', 'packet_manifest_sha256':digest(PACKET / 'manifest.json'), 'packet_files_read_and_hash_verified':len(inventory), 'inputs':{}, 'structural_checks':{}, 'scalar_law_checks':{}, 'limitations':['This author check is not independent scientific review, source authenticity, generated-output validity, transport validation or execution authorization.','Analytical source identities concern the assumed population law, not empirical source fit or unknown original processing.']}
for name in ('generator.py','model_spec.json','evidence.json','qualified_plan_v1.json','scientific_validity_v1.json','support_selection_v1.json','analysis_evidence.json','evidence_use_v1.json','context_bridge_v1.json'):
    static['inputs'][name] = digest(C / name)
static['structural_checks'] = {'all_packet_manifest_hashes_match':True,'bundle_task_registry_match_packet':True,'generator_and_spec_byte_identical_to_packet':all(digest(C / f) == manifest['files']['initial/' + f] for f in ('generator.py','model_spec.json')),'evidence_byte_identical_to_packet':digest(C / 'evidence.json') == manifest['files']['initial/evidence.json'],'bridge_bytes_differ_only_by_12_branch_trial_identities':True,'fixed_schedule_and_resource_limits_preserved':True,'strict_source_unavailability_preserved':True,'qualified_ids_and_empty_bindings_preserved':True,'analysis_support_labels_preserved':True}

for ctx, desc in p['contexts'].items():
    cfg = desc['inputs']
    rbg, rbh, rgh = shared['latent_bmi_glucose_correlation'], shared['latent_bmi_hba1c_correlation'], cfg['glucose_hba1c_latent_correlation']
    cg = math.sqrt(1-rbg*rbg)
    ch = (rgh-rbg*rbh)/cg
    eh2 = 1-rbh*rbh-ch*ch
    assert eh2 > 0 and 0 < cfg['female_probability'] < 1
    values, weights = cfg['age_law']['values'], cfg['age_law']['weights']
    assert len(values) == len(weights) >= 2 and all(w > 0 for w in weights)
    law = laws[ctx]['variables']
    age = law['age']
    if age['op'] == 'mixture':
        assert [b['law']['value'] for b in age['components']] == values
        assert [b['weight'] for b in age['components']] == weights
    else:
        assert age == {'op':'discrete_uniform', 'lower':min(values), 'upper':max(values)}
        assert len(set(weights)) == 1
    assert law['female'] == {'op':'bernoulli','p':cfg['female_probability']}
    assert law['u_g']['terms'][0]['scale'] == rbg and law['u_g']['terms'][1]['scale'] == cg
    assert law['u_h']['terms'][0]['scale'] == rbh and law['u_h']['terms'][1]['scale'] == ch and law['u_h']['terms'][2]['scale'] == math.sqrt(eh2)
    for name, margin in cfg['margins'].items():
        term = law[name] if margin['kind'] == 'affine' else law[name]['input']['input']
        assert term['scale'] == margin['scale'] and term['shift'] == margin['location']
        if margin['kind'] == 'shifted_exp':
            assert law[name]['shift'] == margin['shift']
    static['scalar_law_checks'][ctx] = {'remaining_hba1c_factor_variance':eh2,'positive_remaining_variance':True,'age_support':[min(values),max(values)],'age_weights_and_biometric_coefficients_match_manifest':True,'rank_argument':'At least two positive-probability age values and a nondegenerate independent binary margin; glucose retains positive continuous variation conditional on BMI. Thus no affine predictor identity holds in the declared population. Realized sample rank is checked by generator and can still fail.'}

j = p['contexts']['J']['inputs']
j_support = support['contexts']['J']['final_supports']
static['j_declared_enclosures_decimal'] = {name:{bound:float(Fraction(value['domain'][bound])) for bound in ('lower','upper')} for name,value in j_support.items()}
assert float(Fraction(j_support['glucose']['domain']['upper'])) < 7
assert float(Fraction(j_support['hba1c']['domain']['lower'])) > shared['ngsp_percent_intercept']
b = p['contexts']['B']['inputs']
sg, sh = b['margins']['glucose']['scale'], b['margins']['hba1c']['scale']
algebra = {'J_BMI_IFCC_population_projection':rbh * 3 / 4.1,'J_FPG_IFCC_population_projection':j['glucose_hba1c_latent_correlation'] * 3 / .5,'B_ideal_lognormal_Pearson':math.expm1(b['glucose_hba1c_latent_correlation']*sg*sh)/math.sqrt(math.expm1(sg*sg)*math.expm1(sh*sh)),'M_ideal_Gaussian_copula_Spearman':6/math.pi*math.asin(p['contexts']['M']['inputs']['glucose_hba1c_latent_correlation']/2)}
for actual, expected in zip(algebra.values(), (.13,2.29,.619,.529)):
    assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)
static['source_identity_algebra'] = {'values':algebra,'interpretation':'Deterministic checks of pre-existing parameter identities, without fitting or generated source data; finite decimals and unreported processing prevent exact source-reproduction claims.'}

support_module = module('017_support_selection_v1.py', '_a02self_support_metadata')
use_module = module('019_evidence_use_v1.py', '_a02self_use_metadata')
law_module = module('021_scientific_validity_v1.py', '_a02self_law_metadata')
static['support_metadata'] = support_module.assess_support_selection(support, required_contexts=required['required_contexts'], required_checks=required['required_checks'], known_provenance={'evidence':[i['id'] for i in evidence['items']], 'assumption':[a['id'] for a in spec['assumptions']], 'definition':required['definition_ids']})
assert static['support_metadata']['status'] == 'declaration_checks_pass'
checks = [check['id'] for ctx in bridge['contexts'] if ctx['recipe'] for check in ctx['recipe']['checks']]
use_result = use_module.assess_evidence_use(read(C / 'evidence_use_v1.json'), evidence, spec, recipe_check_ids=checks)
static['evidence_use_metadata'] = {k:v for k,v in use_result.items() if k != 'items'}
static['evidence_use_metadata']['items_covered'] = len(use_result['items'])
static['law_moment_metadata'] = {ctx:law_module.assess_law(law) for ctx,law in laws.items()}
assert all(row['manifest_valid'] and all(a['second_moment_status'] == 'pass' for a in row['analyses']) for row in static['law_moment_metadata'].values())
static['validator_sha256'] = {name:digest(PACKET / 'original_inputs' / name) for name in ('017_support_selection_v1.py','019_evidence_use_v1.py','021_scientific_validity_v1.py')}
write(C / 'STATIC_ASSESSMENT.json', static)
write(C / 'INPUT_BINDING.json', {'schema_version':1,'constructor':'A02','branch':'self_review','packet_sha256':PACKET_HASH,'manifest_sha256':digest(PACKET / 'manifest.json'),'initial_source_feedback_sha256':None,'numerical_source_feedback_supplied':False,'initial_freeze_sha256_from_packet_manifest':manifest['initial_freeze_sha256'],'packet_file_hash_verification':'All 43 manifest-listed files were read and verified; supplied packet_sha256 is retained as assigned identity, not a substitute for source authenticity.','task_sha256':digest(BUNDLE / 'task.json'),'registry_sha256':digest(BUNDLE / 'registry.json')})

reason = ('Retain: the accepted direct eligible-population construction preserves the four source functionals and native measurements under explicit assumptions, and static inspection identifies no specific defect warranting a scientific change. The fixed evidence does not identify replacement age/sex relationships or a better target joint law. Retention is a bounded developmental choice, not empirical validation or an assertion of improved data.')
limitations = ['No numerical source feedback is present in this self-review packet; no generator has been imported or run by this author.','Age and female independence, the assumed BMI-glucose association, source-specific tails and source-to-target transport remain unsupported; A_AGE stays unassessed.','A_BMI and A_GLUCOSE remain partial, assumption-dependent uses. Source similarity cannot establish target validity or causality.','Original weighting, analytic rows, missing-value processing and MIND ties remain unresolved; strict source comparisons stay not_computable.','Source age coarsening/support and Bao log-IQR margins are approximations; individual SDs and interval endpoints are not precision weights.','Finite moments and nonsingular population design do not guarantee finite, full-rank sampled output; failures must remain unrepaired.','No uncertainty calibration, measurement savings, clinical use or independent confirmation is established; CHNS remains researcher-exposed developmental reference.']
findings = ['Kept Jansen BMI and FPG as separate intercept-including adjusted projections, with the documented percent-to-IFCC native response mapping.','Kept Bao Pearson and MIND serum-glucose Spearman distinct; mapping aliases do not assert assay or serum/plasma equivalence.','Checked direct eligible support declarations and positive residual-factor variance; retained absence of clipping, retry or inferred unobserved exclusions.','Preserved every scientific file except branch decision prose and the twelve required bridge trial identity replacements; added truthful checks, input binding and an eligibility metadata restatement.']
write(R / 'decision.json', {'action':'retain','packet_sha256':PACKET_HASH,'reason':reason,'addressed_findings':findings,'remaining_limitations':limitations})
(C / 'decision.md').write_text('# A02 self-review decision: retain\n\n' + reason + '\n\nThe scientific generator, full model specification, evidence, qualified operators, final-law manifest, support declaration, evidence-use declaration and analysis-support labels are unchanged from the assigned accepted-initial packet. Only the twelve bridge trial IDs change from A02_initial to A02_self_review, with all seeds, row counts and budgets retained. This branch parents the accepted initial identified by the packet; it does not parent another branch.\n\nJansen supplies two separate covariance/projection identities under the assumed independence of age and female. Bao uses the ideal lognormal Pearson identity; MIND uses the Gaussian-copula Spearman identity with its serum measurement. These are mathematical properties of the chosen laws. Source summaries initialize assumed margins and categorical ages; they do not determine distributions, nuisance effects or the target. The exact HbA1c representation map does not imply assay equivalence.\n\nRetaining the bounded J law preserves its direct eligibility and native IFCC support. The positive B/M/T lognormal construction preserves finite polynomial moments but leaves tail plausibility unverified. Adding age effects, replacing unreported dependence or changing source-to-target sharing would introduce fresh unsupported choices without a supplied discriminating basis. A_AGE therefore remains unassessed; A_BMI and A_GLUCOSE retain partial support. No sign or target estimate has been sought.\n\nFresh author work consists of packet/hash checks, metadata checks, code reading and deterministic scalar algebra. The inherited initial decision\'s historical checks are not counted as newly performed. The auxiliary reports and checks.json specify the exact new checks. No independent approval, freeze or execution receipt is authored.\n\nRemaining limitations:\n\n' + '\n'.join('- ' + x for x in limitations) + '\n\nStop scientific editing at this one retain decision. No generated table, source discrepancy, target analysis or quality-improvement claim is submitted.\n', encoding='utf-8')
write(C / 'checks.json', {'scope':'source_only','records':[{'name':'packet_and_static_metadata','status':'pass','detail':'New assigned-packet hashes, retained-byte invariance, fixed schedule, evidence-use references, support declarations and declared-law moment checks were performed; STATIC_ASSESSMENT.json records scalar algebra and each scope limit.'},{'name':'empirical_output_and_transport','status':'not_computable','detail':'No generator imported or executed, no rows sampled, no numerical source feedback or target outcomes obtained; empirical validity and transport remain unevaluated.'}], 'artifacts':[{'path':name,'sha256':digest(C / name)} for name in ('INPUT_BINDING.json','STATIC_ASSESSMENT.json')]})
print(json.dumps({'status':'prepared','decision':'retain','packet_files_verified':len(inventory),'candidate':str(C),'source_identity_algebra':algebra,'candidate_bytes':sum(f.stat().st_size for f in C.iterdir() if f.is_file())}, indent=2))
