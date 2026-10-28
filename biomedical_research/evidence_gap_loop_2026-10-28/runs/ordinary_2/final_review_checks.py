"""Read-only final-candidate review; all generator inputs are invented."""
import copy
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import gammaincc, gammaincinv
from scipy.stats import norm

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
FINAL = RUN / 'final'
INITIAL = RUN / 'initial'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tests = []


def record(name, **details):
    tests.append({'name': name, 'passed': True, 'details': details})


before = {str(path): sha(path) for folder in [INITIAL, FINAL] for path in folder.iterdir() if path.is_file()}
initial_review = read(RUN / 'initial_review.json')
assert sha(INITIAL / 'freeze.json') == initial_review['candidate_freeze_sha256']
for folder in [INITIAL, FINAL]:
    freeze = read(folder / 'freeze.json')
    for name, digest in freeze['commitment'].items():
        path = Path(name).resolve()
        assert path.is_relative_to(RUN)
        assert path.parent in [INITIAL, FINAL, RUN / 'literature' / 'approved']
        assert sha(path) == digest
record('initial_and_final_committed_candidate_and_source_hashes_preserved', initial_files=11, final_files=12, note='No run_commitment files or participant outputs opened')

for name in ['generator.py', 'model_spec.json']:
    assert (INITIAL / name).read_bytes() == (FINAL / name).read_bytes()
old_ledger, ledger = read(INITIAL / 'evidence.json'), read(FINAL / 'evidence.json')
assert old_ledger['sources'] == ledger['sources']
assert old_ledger['evidence'] == ledger['evidence']
record('exact_generator_spec_noop_and_unchanged_quantitative_evidence', scientific_parameter_change=False, newly_added_quantitative_sources=0)

audit = (RUN / 'literature' / 'audit.jsonl').read_bytes()
for folder in [INITIAL, FINAL]:
    snapshot = read(folder / 'gateway_snapshot.json')
    assert hashlib.sha256(audit[:snapshot['audit_bytes']]).hexdigest() == snapshot['audit_prefix_sha256']
final_snapshot = read(FINAL / 'gateway_snapshot.json')
events = [json.loads(line) for line in audit[:final_snapshot['audit_bytes']].splitlines()]
registry = {(e['artifact']['session_relative_path'], e['artifact']['sha256']) for e in events if e.get('type') == 'artifact_approved' and e.get('status') == 'accepted'}
searches = ledger['retrieval_summary']['revision_searches']
assert len(searches) == 2
counts = []
for search in searches:
    item = search['artifact']
    assert sha(RUN / item['path']) == item['sha256']
    assert (item['path'].removeprefix('literature/'), item['sha256']) in registry
    data = read(RUN / item['path'])
    counts.append({k: data[k] for k in ['total_hit_count', 'retrieved_count', 'accepted_count', 'rejected_count']})
assert final_snapshot['usage']['queries'] == 12 and final_snapshot['usage']['downloads'] == 7
record('frozen_audit_prefixes_and_two_new_search_artifacts', pages=counts, final_queries=12, final_downloads=7)

controller = load('ordinary2_final_review_controller', ROOT / 'loop_control.py')
static = controller.source_check(FINAL / 'generator.py')
spec = read(FINAL / 'model_spec.json')
controller.validate_spec(spec, controller.validate_ledger(ledger)[1])
record('static_check_before_import_and_provenance_schema', **static)
state = copy.deepcopy(np.random.get_state())
old = load('ordinary2_initial_comparison', INITIAL / 'generator.py')
new = load('ordinary2_final_reviewed', FINAL / 'generator.py')
rows = list(itertools.product([1, 2], [14.1, 18.0, 28.0, 42.0, 77.5], [20, 34, 62, 79]))
toy = pd.DataFrame([{'row_id': f'final_toy_{i}', 'bmi': b, 'age': a, 'sex': s} for i, (s, b, a) in enumerate(rows)])
toy.index = [99 if i % 2 == 0 else -i for i in range(len(toy))]
toy_before, spec_before = toy.copy(deep=True), copy.deepcopy(spec)
for seed in [1701, 1702, 1703]:
    actual = new.generate(toy, spec, seed)
    pd.testing.assert_frame_equal(actual, old.generate(toy, spec, seed), check_exact=True)
    pd.testing.assert_frame_equal(actual, new.generate(toy, spec, seed), check_exact=True)
    controller.output_check(toy, actual, read(ROOT / 'runner_contract.json'))
pd.testing.assert_frame_equal(toy, toy_before, check_exact=True)
assert spec == spec_before
assert controller.rng_equal(state, np.random.get_state())
assert not new.generate(toy, spec, 1701).hdl.equals(new.generate(toy, spec, 1702).hdl)
record('40_invented_rows_three_seeds_exact_initial_final_equality', input_and_spec_unchanged=True, global_rng_unchanged=True, finite_positive=True, reproducible=True, stochastic=True)

reported = read(FINAL / 'artificial_checks.json')
assert len(reported['tests']) == 17 and all(t['passed'] for t in reported['tests'])
records = {t['name']: t['details'] for t in reported['tests']}
p = spec['parameters']
rho = 2 * math.sin(math.pi * p['partial_spearman_bmi_hdl'] / 6)


def pieces(sex):
    mean = p['reference_hdl_mean_mgdl'][sex]
    tau2 = math.log1p((p['reference_hdl_sd_mgdl'][sex] / mean) ** 2)
    g = p['log_hdl_age_slope_per_year'][sex]
    variance = tau2 - (g * p['reference_age_sd_years']) ** 2
    return mean, tau2, g, variance


for case in records['F1_omitted_covariance_nonidentification_demonstration']['cases']:
    a, d = case['correlation_BMI_C'], case['correlation_logHDL_C']
    r = a * d + math.sqrt((1-a*a) * (1-d*d)) * rho
    matrix = np.array([[1, a, r], [a, 1, d], [r, d, 1]])
    assert np.linalg.eigvalsh(matrix).min() > 0
    residual_r = (r-a*d) / math.sqrt((1-a*a) * (1-d*d))
    assert math.isclose(residual_r, rho, rel_tol=1e-14)
    assert math.isclose(6 / math.pi * math.asin(residual_r / 2), -0.26, rel_tol=1e-14)
    for sex in ['1', '2']:
        beta = r * math.sqrt(pieces(sex)[3]) / p['reference_bmi_sd'][sex]
        assert math.isclose(beta, case['logHDL_BMI_slopes_when_C_unavailable'][sex], rel_tol=1e-14)
        assert math.isclose(math.exp(15*beta), case['conditional_mean_ratio_BMI40_vs25'][sex], rel_tol=1e-14)
record('independent_covariance_sensitivity_arithmetic', cases=4, scope='Invented Gaussian residual ranks only; not the reported partial-Spearman procedure')

for case in records['F2_age_contrast_decomposition_nonidentification']['cases']:
    sex = case['sex']
    young, old_mean = (1.27, 1.42) if sex == '1' else (1.45, 1.50)
    fraction = case['fraction_of_log_group_contrast_assigned_to_conditional_age']
    slope = fraction * math.log(old_mean / young) / 35
    offset = (1-fraction) * math.log(old_mean / young)
    assert math.isclose(young * math.exp(slope * 35 + offset), old_mean, rel_tol=1e-14)
    assert math.isclose(math.exp(-42 * slope), case['fixed_BMI_mean_ratio_age20_vs62'], rel_tol=1e-14)
record('independent_age_contrast_decomposition_arithmetic', cases=8)

for case in records['F3_positive_families_same_moments_different_tails']['cases']:
    sex = case['sex']
    mean, tau2, g, variance = pieces(sex)
    beta = rho * math.sqrt(variance) / p['reference_bmi_sd'][sex]
    residual2 = (1-rho*rho) * variance
    mu = math.log(mean) - tau2 / 2 + beta * (25-p['reference_bmi_mean'][sex]) + g*(60-62)
    m = math.exp(mu + residual2/2)
    v = m*m * math.expm1(residual2)
    shape, scale = m*m/v, v/m
    assert math.isclose(shape*scale, m, rel_tol=1e-14)
    assert math.isclose(shape*scale*scale, v, rel_tol=1e-14)
    assert math.isclose(m, case['shared_mean'], rel_tol=1e-14)
    assert math.isclose(v, case['shared_variance'], rel_tol=1e-14)
    assert math.isclose(norm.sf((math.log(100)-mu)/math.sqrt(residual2)), case['lognormal_probability_above_100'], rel_tol=1e-12)
    assert math.isclose(gammaincc(shape, 100/scale), case['gamma_probability_above_100'], rel_tol=1e-12)
    np.testing.assert_allclose(np.exp(mu + math.sqrt(residual2)*norm.ppf([0.01, 0.99])), case['lognormal_1st_99th_percentiles'], rtol=1e-12)
    np.testing.assert_allclose(scale*gammaincinv(shape, [0.01, 0.99]), case['gamma_1st_99th_percentiles'], rtol=1e-12)
record('independent_equal_moment_tail_comparison', cases=2, functions='Normal survival and incomplete-gamma functions')

for name, digest in before.items():
    assert sha(Path(name)) == digest
record('all_initial_and_final_candidate_files_unchanged_during_review', files=len(before))
result = {'all_passed': True, 'tests': tests, 'scope': 'Own candidate files, approved source/search artifacts, common contract/controller and invented inputs only', 'hash_bindings': {'generator_sha256': sha(FINAL/'generator.py'), 'model_spec_sha256': sha(FINAL/'model_spec.json'), 'evidence_sha256': sha(FINAL/'evidence.json'), 'candidate_freeze_sha256': sha(FINAL/'freeze.json')}}
(RUN/'final_review_checks.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
