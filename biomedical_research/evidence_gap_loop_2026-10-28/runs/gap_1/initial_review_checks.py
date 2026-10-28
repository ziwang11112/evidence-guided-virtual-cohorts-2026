"""Independent initial review: approved aggregates and invented inputs only."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import math

import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.stats import norm, gamma, lognorm

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
INITIAL = RUN / 'initial'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

# No controller entrypoint is called; inspect top-level structure before import.
controller_ast = ast.parse((ROOT / 'loop_control.py').read_text(encoding='utf-8-sig'))
assert all(isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.Expr, ast.If)) for n in controller_ast.body)
controller = module('gap1_review_controller', ROOT / 'loop_control.py')
static_check = controller.source_check(INITIAL / 'generator.py')
generator = module('gap1_review_generator', INITIAL / 'generator.py')
spec = read(INITIAL / 'model_spec.json')
ledger = read(INITIAL / 'evidence.json')
p = spec['parameters']
items = {e['id']: e for e in ledger['evidence']}
_, eids = controller.validate_ledger(ledger)
controller.validate_spec(spec, eids)
gaps, actions = read(INITIAL / 'gaps.json'), read(INITIAL / 'actions.json')
controller.validate_gaps(gaps)
controller.validate_actions(actions, gaps)

# Verify only assigned-run candidate/source commitments, never shared rows.
freeze = read(INITIAL / 'freeze.json')
commitments = []
for name, expected in freeze['commitment'].items():
    path = Path(name)
    assert path.is_relative_to(RUN)
    assert sha(path) == expected
    commitments.append(str(path.relative_to(RUN)))
audit_bytes = (RUN / 'literature' / 'audit.jsonl').read_bytes()
registry = set()
for line in audit_bytes.splitlines():
    event = json.loads(line)
    if event.get('type') == 'artifact_approved' and event.get('status') == 'accepted':
        a = event['artifact']
        registry.add(('literature/' + a['session_relative_path'], a['sha256']))
artifacts = [a for s in ledger['sources'] for a in s['approved_artifacts']]
artifacts += [a for action in actions for a in action['evidence_artifacts']]
assert all((a['path'], a['sha256']) in registry and sha(RUN / a['path']) == a['sha256'] for a in artifacts)
snapshot = read(INITIAL / 'gateway_snapshot.json')
assert hashlib.sha256(audit_bytes[:snapshot['audit_bytes']]).hexdigest() == snapshot['audit_prefix_sha256']

toy = pd.DataFrame({'row_id': ['invented_c', 'invented_a', 'invented_d', 'invented_b'],
                    'bmi': [18.5, 27.0, 80.0, 40.0], 'age': [20, 45, 79, 60],
                    'sex': pd.array([1, 2, 1, 2], dtype='Int64')}, index=[9, 4, 4, -2])
before = toy.copy(deep=True)
before_spec = json.dumps(spec, sort_keys=True)
global_before = np.random.get_state()
out = generator.generate(toy, spec, 73991)
again = generator.generate(toy, spec, 73991)
changed = generator.generate(toy, spec, 73992)
global_after = np.random.get_state()
assert out.iloc[:, :4].equals(toy) and toy.equals(before)
assert list(out.columns) == ['row_id', 'bmi', 'age', 'sex', 'hdl']
assert out.equals(again) and not out.hdl.equals(changed.hdl)
assert before_spec == json.dumps(spec, sort_keys=True)
assert all(np.array_equal(a, b) if isinstance(a, np.ndarray) else a == b for a, b in zip(global_before, global_after))
assert generator.generate(toy.iloc[:0], spec, 1).iloc[:, :4].equals(toy.iloc[:0])

def age_effect(age):
    knots, levels = p['age_knots_years'], p['age_relative_means']
    def raw(x):
        if x <= knots[0]:
            return math.log(levels[0])
        for left in range(len(knots) - 1):
            if x <= knots[left + 1]:
                w = (x - knots[left]) / (knots[left + 1] - knots[left])
                return (1 - w) * math.log(levels[left]) + w * math.log(levels[left + 1])
        return math.log(levels[-1])
    return raw(age) - raw(p['age_reference'])

def moments(bmi, age, sex):
    mean = p['conditional_means_at_reference_by_sex'][sex] * math.exp(p['bmi_log_slopes_by_sex'][sex] * (bmi - p['bmi_reference']) + age_effect(age))
    sigma = p['residual_log_sd_by_sex'][sex]
    return mean, mean * mean * math.expm1(sigma * sigma), sigma

# Independent scalar equation agrees draw-for-draw with vectorized generator.
rng = np.random.default_rng(73991)
expected = []
for row in toy.itertuples():
    mean, var, sigma = moments(row.bmi, row.age, 'female' if row.sex == 2 else 'male')
    expected.append(rng.lognormal(math.log(mean) - sigma * sigma / 2, sigma))
assert np.allclose(expected, out.hdl, rtol=1e-14, atol=0)
grid = [(b, a, s) for b in [8, 18.5, 21.25, 27, 40, 80, 110] for a in [20, 35, 45, 55.5, 65.5, 79] for s in [1, 2]]
grid_input = pd.DataFrame(grid, columns=['bmi', 'age', 'sex'])
grid_input.insert(0, 'row_id', ['invented_grid_' + str(i) for i in range(len(grid))])
grid_out = generator.generate(grid_input, spec, 55501)
assert np.isfinite(grid_out.hdl).all() and (grid_out.hdl > 0).all()

mc = []
for i, (bmi, age, sex) in enumerate([(22, 25, 'male'), (38, 60, 'male'), (22, 50, 'female'), (38, 75, 'female')]):
    n, seed = 120000, 192301 + i
    x = pd.DataFrame({'row_id': ['invented_mc_' + str(j) for j in range(n)], 'bmi': bmi, 'age': age, 'sex': 1 if sex == 'male' else 2})
    y = generator.generate(x, spec, seed).hdl.to_numpy()
    mean, variance, sigma = moments(bmi, age, sex)
    z = (y.mean() - mean) / math.sqrt(variance / n)
    ratio = y.var(ddof=1) / variance
    assert abs(z) < 5 and abs(ratio - 1) < 0.03
    mc.append({'sex': sex, 'bmi': bmi, 'age': age, 'n': n, 'seed': seed, 'mean_z': float(z), 'variance_ratio': float(ratio)})

# Independently check quoted algebra and integrate the source closure adaptively,
# splitting at every age knot; do not call the builder/rebuild script.
for sex in ['male', 'female']:
    reported = items['E_TW_BMI']['reported'][sex + '_mean']
    assert abs(math.log(reported[3] / reported[1]) / (30 - 21.25) - p['bmi_log_slopes_by_sex'][sex]) < 1e-15
assert np.allclose(1 + np.asarray(items['E_TW_AGE']['reported']['beta_mg_dl']) / 55, p['age_relative_means'], rtol=1e-15)

calibration, cell_checks = [], []
cell_hdl = {'male': [(51,16),(58,21),(42,14),(50,14)], 'female': [(65,19),(62,17),(54,18),(59,20)]}
for sex in ['male', 'female']:
    cells = items['E_US_COVARIATES']['reported'][sex]
    total = sum(c['n'] for c in cells)
    assert total == items['E_US_MOMENTS']['reported']['n_' + sex]
    multipliers = [0.0, 0.0]
    base, sigma = p['conditional_means_at_reference_by_sex'][sex], p['residual_log_sd_by_sex'][sex]
    for ci, c in enumerate(cells):
        values = []
        bounds = [-np.inf] + p['age_knots_years'] + [np.inf]
        for power in [1, 2]:
            age_m = sum(quad(lambda a: math.exp(power * age_effect(a)) * norm.pdf(a, loc=c['age_mean'], scale=c['age_sd']), low, high, epsabs=1e-11)[0] for low, high in zip(bounds[:-1], bounds[1:]))
            beta = p['bmi_log_slopes_by_sex'][sex]
            bmi_m = math.exp(power * beta * (c['bmi_mean'] - p['bmi_reference']) + (power * beta * c['bmi_sd']) ** 2 / 2)
            values.append(age_m * bmi_m)
            multipliers[power - 1] += c['n'] / total * values[-1]
        predicted_mean = base * values[0]
        predicted_sd = math.sqrt(base * base * (math.exp(sigma * sigma) * values[1] - values[0] ** 2))
        reported_mean, reported_sd = cell_hdl[sex][ci]
        cell_checks.append({'sex': sex, 'group': c['group'], 'reported_hdl_mean': reported_mean, 'closure_hdl_mean': predicted_mean, 'reported_hdl_sd': reported_sd, 'closure_hdl_sd': predicted_sd, 'scope': 'Same declared closure, not an exact empirical source operator'})
    m1, m2 = multipliers
    source = items['E_US_MOMENTS']['reported'][sex]
    rebuilt_base = source['mean'] / m1
    rebuilt_sigma = math.sqrt(math.log((source['sd'] ** 2 + source['mean'] ** 2) / (rebuilt_base * rebuilt_base * m2)))
    assert abs(rebuilt_base / base - 1) < 3e-5 and abs(rebuilt_sigma / sigma - 1) < 3e-5
    calibration.append({'sex': sex, 'adaptive_mean_multiplier': m1, 'adaptive_second_multiplier': m2, 'base_relative_difference': rebuilt_base / base - 1, 'sigma_relative_difference': rebuilt_sigma / sigma - 1})

countermodel = []
for check in read(INITIAL / 'artificial_checks.json')['focused_tail_countermodel']:
    sex, bmi = check['sex'], check['invented_bmi']
    mean, var, sigma = moments(bmi, check['age'], sex)
    ln = lognorm(s=sigma, scale=mean * math.exp(-sigma * sigma / 2))
    gm = gamma(a=mean * mean / var, scale=var / mean)
    vals = {'lognormal_p_low': ln.cdf(check['low_threshold_mg_dl']), 'gamma_p_low': gm.cdf(check['low_threshold_mg_dl']), 'lognormal_p_above_100': ln.sf(100), 'gamma_p_above_100': gm.sf(100)}
    assert all(abs(vals[key] - check[key]) < 1e-12 for key in vals)
    countermodel.append({'sex': sex, 'bmi': bmi, 'reported_calculations_reproduced': True})

result = {'scope': 'Approved aggregates and invented inputs only; no observed CSV, target outcome, other run, external retrieval, or builder script execution.', 'static_check': static_check, 'implementation_checks_passed': ['exact columns, input values/dtypes/index/order', 'duplicate/nonmonotone index', 'input/spec immutability', 'same-seed reproducibility and changed-seed variation', 'global NumPy RNG preservation', 'empty input', 'scalar equation draw-for-draw agreement', '84-profile positive finite invented grid'], 'candidate_commitments_verified': commitments, 'evidence_action_registry_and_hashes': True, 'provenance_and_gap_action_schemas': True, 'source_aggregate_reextraction': 'Taiwan Table 2 sex rows and Table 3 age rows; MIDUS descriptive sex moments and Table 2 n/age/BMI/HDL-C rows; source units, SE/SD and adjustment checked manually against approved main text.', 'monte_carlo': mc, 'adaptive_source_closure': calibration, 'additional_same_source_cell_diagnostics': cell_checks, 'countermodel_recalculation': countermodel, 'hashes': {'generator_sha256': sha(INITIAL / 'generator.py'), 'model_spec_sha256': sha(INITIAL / 'model_spec.json'), 'evidence_sha256': sha(INITIAL / 'evidence.json'), 'candidate_freeze_sha256': sha(INITIAL / 'freeze.json')}}
(RUN / 'initial_review_checks.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2, allow_nan=False))
