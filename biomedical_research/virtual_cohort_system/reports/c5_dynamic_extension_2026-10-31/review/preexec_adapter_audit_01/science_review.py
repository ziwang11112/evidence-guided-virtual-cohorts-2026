"""Independent source arithmetic and static contracts; never execute a generator."""
import ast
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
import json
from pathlib import Path
import sys

P = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
sys.path.insert(0, str(P))
from cohort_harness.contracts import validate_task, validate_evidence, validate_spec
from cohort_harness.lifecycle import read_json, sha256, verify_candidate, validate_program, _registry, _checks
from work.c5.method.adapter import _decision

ROOT = P / 'work/c5'
OUT = ROOT / 'review/preexec_adapter_audit_01'
checks = {}


def check(name, condition):
    checks[name] = bool(condition)
    if not condition:
        raise AssertionError(name)


def moments(packet):
    names = [x['name'] for x in packet['variables']]
    stats = {(x['kind'], tuple(x['variables'])): F(str(x['value']))
             for x in packet['reported_statistics']}
    mu = [stats[('mean', (x,))] for x in names]
    sd = [stats[('sd', (x,))] for x in names]
    cov = [[sd[i] ** 2 if i == j else
            sd[i] * sd[j] * stats[('pearson_correlation', tuple(sorted([names[i], names[j]])))]
            for j in range(len(names))] for i in range(len(names))]
    return names, mu, cov


initial = read_json(ROOT / 'visible/initial_source_packet.json')
final = read_json(ROOT / 'visible/final_source_packet.json')
n0, m0, s0 = moments(initial)
n, mu, s = moments(final)
check('same_population_id', initial['population_id'] == final['population_id'])
check('unchanged_old_units', initial['variables'] == final['variables'][:2])
check('unchanged_old_means', m0 == mu[:2])
check('unchanged_old_covariance', s0 == [r[:2] for r in s[:2]])
a, b, d = s[0][0], s[0][1], s[1][1]
c1, c2, vy = s[0][2], s[1][2], s[2][2]
det2 = a*d-b*b
beta = [(d*c1-b*c2)/det2, (a*c2-b*c1)/det2]
residual_variance = vy - c1*beta[0] - c2*beta[1]
det3 = det2 * residual_variance
intercept = mu[2] - beta[0]*mu[0] - beta[1]*mu[1]
check('positive_definite_by_leading_minors', a > 0 and det2 > 0 and det3 > 0)
check('conditional_construction_recovers_cov13', a*beta[0]+b*beta[1] == c1)
check('conditional_construction_recovers_cov23', b*beta[0]+d*beta[1] == c2)
check('conditional_construction_recovers_var3', beta[0]*c1+beta[1]*c2+residual_variance == vy)

directories = {'parent': ROOT/'b/p/candidates/c0', 'joint': ROOT/'b/j/candidates/c0',
               'extension': ROOT/'author/extension'}
native_tasks = {'parent': read_json(ROOT/'b/p/task.json'), 'joint': read_json(ROOT/'b/j/task.json')}
requests = read_json(ROOT/'author/request_decisions.json')['requests']
request_map = {r['request_id']:r for r in requests}
check('four_expected_requests', set(request_map) == {'2','3','4','5'} and len(requests) == 4)
extension_task = deepcopy(native_tasks['parent'])
extension_task.update(task_id='independent_review_in_memory_extension_contract', mode='enrichment',
                      columns=request_map['2']['decision']['requested_variables'])
native_tasks['extension'] = extension_task
specs = {}
for label, path in directories.items():
    task = native_tasks[label]
    evidence = read_json(path/'evidence.json')
    spec = read_json(path/'model_spec.json')
    validate_task(task)
    evidence_ids = validate_evidence(evidence, task)
    validate_spec(spec, evidence_ids)
    validate_program(path/'generator.py')
    _checks(path)
    checks[label+'_native_static_contracts'] = True
    specs[label] = spec['parameters']
    expected_packet = initial if label == 'parent' else final
    reported = {e['id']:e for e in expected_packet['reported_statistics']}
    parsed = {e['id']:e for e in evidence['items'] if e['kind'] != 'contextual'}
    check(label+'_all_reported_evidence_present', set(reported) == set(parsed))
    for ident, item in reported.items():
        actual = parsed[ident]
        kind = 'correlation' if item['kind'] == 'pearson_correlation' else item['kind']
        check(label+'_'+ident+'_faithful', actual['estimate'] == item['value'] and
              actual['unit'] == item['unit'] and actual['variables'] == item['variables'] and
              actual['kind'] == kind and actual['adjustment'] == [])
    packet_path = ROOT/('visible/initial_source_packet.json' if label == 'parent' else 'visible/final_source_packet.json')
    check(label+'_source_hash', specs[label]['source_version']['sha256'] == sha256(packet_path))
    program = ast.parse((path/'generator.py').read_text(encoding='utf-8-sig'))
    imports = [alias.name for node in ast.walk(program) if isinstance(node,ast.Import) for alias in node.names]
    check(label+'_declared_imports_only', imports == ['numpy','pandas'] and
          not any(isinstance(node,ast.ImportFrom) for node in ast.walk(program)))

for label, means, covariance in [('parent',m0,s0),('joint',mu,s)]:
    p = specs[label]
    check(label+'_means_from_source', p['mean_vector'] == [float(x) for x in means])
    check(label+'_covariance_from_source', p['covariance_matrix'] == [[float(x) for x in r] for r in covariance])
    check(label+'_row_count', p['n_rows'] == native_tasks[label]['n_rows'] == 2000)
    verify_candidate(ROOT/('b/p' if label=='parent' else 'b/j'),'candidates/c0')
    checks[label+'_native_freeze_integrity'] = True

ep = specs['extension']
check('extension_conditioning_order', ep['conditioning_variables'] == n[:2])
check('extension_preserves_declared_columns', ep['preserved_columns'] == ['subject_id','x1','x2'])
check('extension_appends_only_x3', ep['generated_variable'] == 'x3')
check('extension_population_centering', ep['conditioning_mean'] == [float(x) for x in mu[:2]] and ep['outcome_mean'] == float(mu[2]))
check('extension_slopes_match_independent_rational_derivation', ep['conditional_slopes'] == [float(x) for x in beta])
check('extension_variance_matches_independent_rational_derivation', ep['conditional_residual_variance'] == float(residual_variance))
check('extension_row_count', ep['n_rows'] == 2000)
_registry(ROOT/'b/j')
registry = read_json(ROOT/'b/j/registry.json')
expected_routes = {'2':'extend','3':'reuse','4':'new_population','5':'clarify'}
for ident,item in request_map.items():
    check('request_'+ident+'_route', item['decision']['action'] == expected_routes[ident])
    task = native_tasks['parent'] if ident=='2' else extension_task
    _decision(item['raw_request'],item['decision'],task,registry)
    checks['request_'+ident+'_native_routing_contract'] = True

controller = ast.parse((ROOT/'run_unit.py').read_text(encoding='utf-8-sig'))
science_files = next(ast.literal_eval(node.value) for node in controller.body
                     if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SCIENCE_FILES' for t in node.targets))
check('six_science_files_copied_and_bound', science_files == ['generator.py','evidence.json','model_spec.json','decision.md','checks.json','derivation_check.json'])
bound = ['visible/initial_source_packet.json','visible/final_source_packet.json','author/request_decisions.json',
         'run_unit.py','PROTOCOL_DRAFT.md','EXPOSURE_NOTE.md']
for label,path in directories.items():
    bound.extend((path/f).relative_to(ROOT).as_posix() for f in science_files)
bound.extend(['b/p/candidates/c0/freeze.json','b/j/candidates/c0/freeze.json'])
result = {'schema_version':1,'status':'pass_preexecution_science_and_routing_review',
          'reviewed_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,
          'checks_passed':sum(checks.values()),'covariance_exact':[[str(x) for x in r] for r in s],
          'leading_minors_exact':[str(a),str(det2),str(det3)],
          'conditional_slopes_exact':[str(x) for x in beta],
          'conditional_intercept_exact':str(intercept),
          'conditional_variance_exact':str(residual_variance),
          'old_pair_slope_exact':str(b/a),'old_pair_intercept_exact':str(mu[1]-(b/a)*mu[0]),
          'bindings':{x:sha256(ROOT/x) for x in bound},
          'review_script_sha256':sha256(Path(__file__)),
          'generator_imports_or_executions':0,'generated_row_access':False,
          'sealed_custody_or_evaluator_access':False,
          'exposure_qualification':'Author incidental historical summaries and algebra helper disclosed; one scientific construction, not independent replications. Root final-source early intake disclosed separately.'}
with (OUT/'SCIENCE_REVIEW_CHECKS.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':result['status'],'checks_passed':result['checks_passed'],
                  'conditional_slopes_exact':result['conditional_slopes_exact'],
                  'conditional_variance_exact':result['conditional_variance_exact'],
                  'latest_controller_sha256':result['bindings']['run_unit.py']}))
