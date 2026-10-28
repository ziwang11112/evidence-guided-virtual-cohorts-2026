"""Independent reviewer checks: approved sources and invented inputs only."""
import ast
import copy
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
CANDIDATE = RUN / 'initial'
records = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def record(name, **details):
    records.append({'name': name, 'passed': True, 'details': details})


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The controller has been read. Verify it has no unexpected top-level execution.
tree = ast.parse((ROOT / 'loop_control.py').read_text(encoding='utf-8-sig'))
assert all(isinstance(n, (ast.Expr, ast.Import, ast.ImportFrom, ast.FunctionDef, ast.If)) for n in tree.body)
controller = load('review_controller_ordinary2', ROOT / 'loop_control.py')
static = controller.source_check(CANDIDATE / 'generator.py')
record('controller_static_check_before_candidate_import', **static)

spec = read(CANDIDATE / 'model_spec.json')
ledger = read(CANDIDATE / 'evidence.json')
freeze = read(CANDIDATE / 'freeze.json')
controller.validate_spec(spec, controller.validate_ledger(ledger)[1])
record('ledger_and_spec_schema_and_reference_resolution', parameters=len(spec['parameters']))

allowed = [CANDIDATE / name for name in ['generator.py', 'model_spec.json', 'evidence.json', 'decision.md', 'gateway_snapshot.json']]
for source in ledger['sources']:
    for item in source['approved_artifacts']:
        allowed.append(RUN / item['path'])
for path in allowed:
    assert sha(path) == freeze['commitment'][str(path)]
record('initial_candidate_commitments_unchanged', files=len(allowed), note='No run_commitment files or observed CSV were opened')

snapshot = read(CANDIDATE / 'gateway_snapshot.json')
audit = (RUN / 'literature' / 'audit.jsonl').read_bytes()
assert hashlib.sha256(audit[:snapshot['audit_bytes']]).hexdigest() == snapshot['audit_prefix_sha256']
registry = set()
for line in audit[:snapshot['audit_bytes']].splitlines():
    event = json.loads(line)
    if event.get('type') == 'artifact_approved' and event.get('status') == 'accepted':
        a = event['artifact']
        registry.add((a['session_relative_path'].replace('\\', '/'), a['sha256']))
for source in ledger['sources']:
    for a in source['approved_artifacts']:
        assert (a['path'].removeprefix('literature/'), a['sha256']) in registry
        assert sha(RUN / a['path']) == a['sha256']
record('all_six_source_artifacts_hash_and_frozen_registry_match', artifacts=6)

global_before = copy.deepcopy(np.random.get_state())
module = load('ordinary2_reviewed_initial', CANDIDATE / 'generator.py')
assert controller.rng_equal(global_before, np.random.get_state())

rows = list(itertools.product([1, 2], [14.1, 18.0, 28.0, 42.0, 77.5], [20, 34, 62, 79]))
obs = pd.DataFrame([{'row_id': f'invented_{i:03}', 'bmi': b, 'age': a, 'sex': s} for i, (s, b, a) in enumerate(rows)])
obs.index = [17 if i % 3 == 0 else -i for i in range(len(obs))]
obs_before, spec_before = obs.copy(deep=True), copy.deepcopy(spec)
out = module.generate(obs, spec, 901)
controller.output_check(obs, out, read(ROOT / 'runner_contract.json'))
pd.testing.assert_frame_equal(obs, obs_before, check_exact=True)
assert spec == spec_before
assert out.index.equals(obs.index)
pd.testing.assert_frame_equal(out, module.generate(obs, spec, 901), check_exact=True)
assert not np.array_equal(out.hdl.to_numpy(), module.generate(obs, spec, 902).hdl.to_numpy())
assert controller.rng_equal(global_before, np.random.get_state())
record('invented_40_row_boundary_grid_contract_dtypes_order_preservation_seed_and_rng', rows=len(obs), index='nonmonotone with duplicates', min_hdl=float(out.hdl.min()), max_hdl=float(out.hdl.max()), input_mutated=False, spec_mutated=False, global_rng_mutated=False)

p = spec['parameters']
rho = 2 * math.sin(math.pi * p['partial_spearman_bmi_hdl'] / 6)


def distribution(sex, bmi, age):
    key = str(sex)
    mean, sd = p['reference_hdl_mean_mgdl'][key], p['reference_hdl_sd_mgdl'][key]
    tau2 = math.log1p((sd / mean) ** 2)
    gamma = p['log_hdl_age_slope_per_year'][key]
    v = tau2 - (gamma * p['reference_age_sd_years']) ** 2
    beta = rho * math.sqrt(v) / p['reference_bmi_sd'][key]
    residual_variance = (1 - rho ** 2) * v
    mu = math.log(mean) - tau2 / 2 + beta * (bmi - p['reference_bmi_mean'][key]) + gamma * (age - p['reference_age_mean_years'])
    return mu, residual_variance, beta, tau2


noise = np.random.default_rng(901).standard_normal(len(obs))
expected = [math.exp(distribution(s, b, a)[0] + math.sqrt(distribution(s, b, a)[1]) * z) for (s, b, a), z in zip(rows, noise)]
np.testing.assert_allclose(out.hdl.to_numpy(), expected, rtol=2e-15, atol=0)
record('independent_scalar_equations_match_vectorized_draws', max_absolute_difference=float(np.max(np.abs(out.hdl.to_numpy() - expected))))

derived = []
for sex, (young, old) in [(1, (1.27, 1.42)), (2, (1.45, 1.50))]:
    key = str(sex)
    gamma = math.log(old / young) / (69.5 - 34.5)
    assert math.isclose(gamma, p['log_hdl_age_slope_per_year'][key], rel_tol=1e-14)
    mu, residual_variance, beta, tau2 = distribution(sex, p['reference_bmi_mean'][key], p['reference_age_mean_years'])
    total = residual_variance + (beta * p['reference_bmi_sd'][key]) ** 2 + (gamma * p['reference_age_sd_years']) ** 2
    assert math.isclose(total, tau2, rel_tol=1e-14)
    implied_mean = math.exp(mu + total / 2)
    implied_sd = implied_mean * math.sqrt(math.expm1(total))
    assert math.isclose(implied_mean, p['reference_hdl_mean_mgdl'][key], rel_tol=1e-14)
    assert math.isclose(implied_sd, p['reference_hdl_sd_mgdl'][key], rel_tol=1e-14)
    assert math.isclose(beta, spec['derived_values']['bmi_log_slopes_per_kg_m2'][key], rel_tol=1e-14)
    assert math.isclose(math.sqrt(residual_variance), spec['derived_values']['residual_log_sd'][key], rel_tol=1e-14)
    derived.append({'sex': sex, 'age_slope': gamma, 'bmi_slope': beta, 'residual_log_sd': math.sqrt(residual_variance), 'reference_mean': implied_mean, 'reference_sd': implied_sd})
record('source_transformations_and_reference_variance_partition', rho=rho, results=derived, scope='Mathematics under the declared independent-normal reference assumptions, not empirical validation')

mc = []
for j, (sex, bmi, age) in enumerate([(1, 28.0, 62), (2, 29.0, 62), (1, 42.0, 34), (2, 18.0, 79)]):
    n = 100000
    invented = pd.DataFrame({'row_id': [f'mc_{j}_{i}' for i in range(n)], 'bmi': bmi, 'age': age, 'sex': sex})
    generated = module.generate(invented, spec, 3300 + j).hdl.to_numpy()
    mu, v, _, _ = distribution(sex, bmi, age)
    mean = math.exp(mu + v / 2)
    sd = mean * math.sqrt(math.expm1(v))
    mean_z = (float(generated.mean()) - mean) / (sd / math.sqrt(n))
    sd_error = float(generated.std(ddof=1)) / sd - 1
    assert abs(mean_z) < 6
    assert abs(sd_error) < 0.025
    assert np.unique(generated).size == n
    mc.append({'sex': sex, 'bmi': bmi, 'age': age, 'n': n, 'mean_standard_error_units': mean_z, 'relative_sd_error': sd_error})
record('conditional_monte_carlo_on_four_invented_cells', results=mc, thresholds='absolute mean error < 6 Monte Carlo SE; relative SD error < 2.5%')

empty = module.generate(obs.iloc[:0], spec, 14)
controller.output_check(obs.iloc[:0], empty, read(ROOT / 'runner_contract.json'))
rejections = []
for column, value in [('bmi', 0), ('bmi', -1), ('age', float('nan')), ('sex', 0), ('sex', 1.5), ('sex', float('inf'))]:
    broken = obs.iloc[:1].copy()
    broken[column] = value
    try:
        module.generate(broken, spec, 22)
    except ValueError:
        rejections.append(f'{column}={value}')
    else:
        raise AssertionError(f'Invalid {column} accepted')
try:
    module.generate(obs.drop(columns='age'), spec, 22)
except ValueError:
    rejections.append('missing age column')
else:
    raise AssertionError('Missing predictor accepted')
record('empty_frame_and_invalid_input_handling', rejected=rejections)

result = {'scope': 'Independent source/implementation review and invented inputs only; no observed participant rows or target outcomes read', 'all_passed': True, 'tests': records, 'hash_bindings': {'generator_sha256': sha(CANDIDATE / 'generator.py'), 'model_spec_sha256': sha(CANDIDATE / 'model_spec.json'), 'evidence_sha256': sha(CANDIDATE / 'evidence.json'), 'candidate_freeze_sha256': sha(CANDIDATE / 'freeze.json')}}
(RUN / 'initial_review_checks.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2, allow_nan=False))
