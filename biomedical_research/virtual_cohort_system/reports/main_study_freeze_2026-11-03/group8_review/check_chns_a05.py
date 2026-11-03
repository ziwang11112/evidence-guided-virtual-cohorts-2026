"""Independent deterministic review: no generator import, execution or row draws."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist
import numpy as np

W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
PROJECT = W / 'biomedical_research/virtual_cohort_system'
R = W / 'evcMS/CHNS2009_E1_A05'
B = R / 'bundle'
C = B / 'candidates/initial'
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT))
from cohort_harness import lifecycle

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def same(a, b):
    assert np.allclose(a, b, rtol=1e-11, atol=1e-12), (a, b)

receipt = lifecycle.verify_candidate(B, 'candidates/initial')
spec = read(C / 'model_spec.json')
p = spec['parameters']
t = p['target_law']
evidence = read(C / 'evidence.json')
items = {r['id']: r for r in evidence['items']}
packet = read(B / 'sources/evidence_packet.json')
ops = read(B / 'input/source_operations.json')['operations']
uptake = {r['operation_id']: r for r in read(C / 'numerical_uptake.json')['records']}
reported = {r['id']: r for r in packet['relationship_records']}
assert len(uptake) == 4 and set(uptake) == set(reported) == {r['evidence_id'] for r in ops}
assert sha(C / 'evidence.json') == sha(B / 'input/evidence.json')
assert read(R / 'decision.json')['candidate'] == 'candidates/initial'
assert read(R / 'decision.json')['action'] == 'initial_final'
assert read(R / 'decision.json')['author_id'] == 'CHNS2009_E1_A05'

# Trace every extracted marginal number and four source relationship records.
trace = []
for r in packet['shared_base']['grouped_marginal_records']:
    if r['kind'] == 'reported_mean_and_individual_sd':
        pairs = [(r['id'] + '_MEAN', r['mean']), (r['id'] + '_SD', r['individual_sd'])]
    elif r['kind'] == 'reported_median_and_quartile_endpoints':
        pairs = [(r['id'] + '_' + suffix, r[field]) for suffix, field in [('MEDIAN', 'median'), ('Q1', 'q1'), ('Q3', 'q3')]]
    else:
        pairs = [(r['id'] + '_FRACTION', r['numerator'] / r['denominator'])]
    for eid, value in pairs:
        same(items[eid]['estimate'], value)
        assert items[eid]['source_id'] == r['source_id']
        assert items[eid]['locator'] == r['locator']
        trace.append(eid)
for op in ops:
    eid = op['evidence_id']
    r = reported[eid]
    canonical = json.dumps(r, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    assert hashlib.sha256(canonical).hexdigest() == op['record_canonical_sha256']
    assert hashlib.sha256(r['source_locator'].encode()).hexdigest() == op['locator_utf8_sha256']
    assert items[eid]['source_id'] == r['source_id']
    assert items[eid]['estimate'] == r['reported']['estimate']
    assert items[eid]['unit'] == r['reported']['unit']
    assert items[eid]['locator'] == r['source_locator']
    assert uptake[eid]['source_context_id'] == r['source_context_id']
    assert uptake[eid]['target_as_source_comparison'] == 'unavailable'
    trace.append(eid)

# Independent probability-law arithmetic, using only the submitted parameters.
matrices = {'target': t, **p['source_laws']}
eigenvalues = {}
for name, law in matrices.items():
    corr = np.asarray(law['latent_correlation'])
    same(corr, corr.T)
    same(np.diag(corr), np.ones(len(corr)))
    ev = np.linalg.eigvalsh(corr)
    assert ev.min() > 0
    eigenvalues[name] = ev.tolist()
    chol = np.linalg.cholesky(corr)
    same(chol @ chol.T, corr)

def moments(m):
    if m['family'] == 'lognormal':
        mu, sd = m['log_mean'], m['log_sd']
        mean = math.exp(mu + sd * sd / 2)
        second = math.exp(2 * mu + 2 * sd * sd)
        return mean, second - mean * mean
    assert m['family'] == 'uniform'
    return (m['low'] + m['high']) / 2, (m['high'] - m['low']) ** 2 / 12

def source_cov(law):
    mar = [law['marginals'][n] for n in law['variables']]
    mv = [moments(m) for m in mar]
    means, variances = np.asarray(mv).T
    cov = np.diag(variances)
    for i in range(len(mar)):
        for j in range(i):
            rho = law['latent_correlation'][i][j]
            if mar[i]['family'] == mar[j]['family'] == 'uniform':
                value = math.sqrt(variances[i] * variances[j]) * (6 / math.pi * math.asin(rho / 2))
            else:
                assert mar[i]['family'] == mar[j]['family'] == 'lognormal'
                value = means[i] * means[j] * math.expm1(mar[i]['log_sd'] * mar[j]['log_sd'] * rho)
            cov[i,j] = cov[j,i] = value
    return means, cov

jlaw = p['source_laws']['CTX_JANSEN_SELECTED']
blaw = p['source_laws']['CTX_BAO_ANALYZED']
mlaw = p['source_laws']['CTX_MIND_ANALYZED']
same(np.asarray(t['latent_correlation'])[1:,1:], np.asarray(jlaw['latent_correlation'])[1:,1:])
same(t['latent_correlation'][2][3], blaw['latent_correlation'][0][1])
same(t['latent_correlation'][2][3], mlaw['latent_correlation'][0][1])
same(np.asarray(jlaw['latent_correlation'])[0,1:], [0,0,0])
same(p['ngsp_relation']['multiplier'], 0.09148)
same(p['ngsp_relation']['offset'], 2.152)
assert jlaw['marginals']['glucose']['high'] < 7
assert jlaw['marginals']['age']['low'] != 35 and jlaw['marginals']['age']['high'] != 74
assert t['marginals']['age'] == {'family':'discrete_uniform','low':35,'high':74}
assert p['n_rows'] == 3000
same(t['female_probability'], items['M_B_FEMALE_FRACTION']['estimate'])
same(jlaw['female_probability'], 1-items['M_J_MALE_FRACTION']['estimate'])
for n in ['glucose', 'hba1c']:
    assert t['marginals'][n] == mlaw['marginals'][n]

jm, jc = source_cov(jlaw)
bp = jlaw['female_probability']
fullmeans = np.array([jm[0], bp, jm[1], jm[2], jm[3]])
fullcov = np.zeros((5,5))
indices = [0,2,3,4]
fullcov[np.ix_(indices,indices)] = jc
fullcov[1,1] = bp*(1-bp)
stored = read(C / 'analytic/jansen_moments.json')
same(fullmeans, stored['means'])
same(fullcov, stored['covariance'])
values = {}
for eid, focal in [('R_JANSEN_BMI', 2), ('R_JANSEN_FPG', 3)]:
    ix = [0,1,focal]
    beta = np.linalg.solve(fullcov[np.ix_(ix,ix)], fullcov[ix,4] / 0.09148)
    values[eid] = float(beta[-1])
bm, bc = source_cov(blaw)
same(bm, read(C / 'analytic/bao_moments.json')['means'])
same(bc, read(C / 'analytic/bao_moments.json')['covariance'])
values['R_BAO_PEARSON'] = float(bc[0,1] / math.sqrt(bc[0,0]*bc[1,1]))
values['R_MIND_SPEARMAN'] = 6/math.pi*math.asin(mlaw['latent_correlation'][0][1]/2)
same(values['R_MIND_SPEARMAN'], read(C/'analytic/mind_rank.json')['calculated_spearman'])
for eid, val in values.items():
    same(val, uptake[eid]['calculated_value'])
    same(val-reported[eid]['reported']['estimate'], uptake[eid]['raw_difference'])

target_moments = {}
for n, prefix in [('bmi','M_M_BMI'),('glucose','M_M_FSG'),('hba1c','M_M_HBA1C_PERCENT')]:
    mean, variance = moments(t['marginals'][n])
    same(mean, items[prefix+'_MEAN']['estimate'])
    same(math.sqrt(variance), items[prefix+'_SD']['estimate'])
    assert math.isfinite(mean*mean+variance)
    target_moments[n] = {'mean':mean,'variance':variance,'second_moment':mean*mean+variance}
bao_quantiles = {}
for n,prefix in [('glucose','M_B_FPG'),('hba1c','M_B_HBA1C_PERCENT')]:
    m=blaw['marginals'][n]
    same(m['log_mean'],math.log(items[prefix+'_MEDIAN']['estimate']))
    same(m['log_sd'],math.log(items[prefix+'_Q3']['estimate']/items[prefix+'_Q1']['estimate'])/(2*NormalDist().inv_cdf(.75)))
    bao_quantiles[n] = {str(q):math.exp(m['log_mean']+m['log_sd']*NormalDist().inv_cdf(q)) for q in [.25,.5,.75]}

fb = read(C / 'whole_cohort_feedback.json')
sem = read(C / 'source_semantics_v1.json')
numeric = {k for k,v in items.items() if v['kind'] != 'contextual'}
assert {r['evidence_id'] for r in fb['checks']} == numeric
assert len(fb['checks']) == len(numeric) == 35
assert all(r['status']=='not_computable' and r['operator'] is None for r in fb['checks'])
assert {r['evidence_id'] for r in sem['bindings']} == numeric
assert all(r['definition_status']=='unsupported' and r['source_operator'] is None for r in sem['bindings'])
assert sem['evidence_sha256'] == sha(C / 'evidence.json')
assert sem['recipe_sha256'] == sha(C / 'whole_cohort_feedback.json')
tree = ast.parse((C/'generator.py').read_text())
assert [n.name for n in tree.body if isinstance(n, ast.FunctionDef)] == ['_normal_cdf','_marginal','generate']
assert not any(isinstance(n,ast.Import) and any(a.name=='generator' for a in n.names) for n in ast.walk(ast.parse(Path(__file__).read_text())))
result = {
 'status':'pass', 'reviewer_id':'/root/main_review_g8',
 'lifecycle_verify_candidate':'passed', 'candidate_freeze_sha256':sha(C/'freeze.json'),
 'decision_sha256':sha(R/'decision.json'), 'rows_produced':0,
 'generator_imported_or_executed':False, 'monte_carlo':False, 'numerical_quadrature':False,
 'target_results_used':False, 'source_trace_items':trace,
 'latent_eigenvalues':eigenvalues, 'source_target_copula_link':'verified_from_actual_spec_and_static_generator',
 'source_values':{eid:{'calculated':v,'reported':reported[eid]['reported']['estimate'],'difference':v-reported[eid]['reported']['estimate']} for eid,v in values.items()},
 'target_model_moments_not_target_measurements':target_moments,
 'bao_modeled_quantiles':bao_quantiles, 'unavailable_target_as_source_checks':len(numeric),
 'inputs':{str(x):sha(x) for x in [C/'generator.py',C/'model_spec.json',C/'evidence.json',C/'mathematical_properties.md',C/'numerical_uptake.json',B/'sources/evidence_packet.json',B/'sources/NGSP_UNITS.md',B/'input/source_operations.json',B/'input/source_operations.py',B/'task.json',R/'profile.json',PROJECT/'cohort_harness/contracts.py',PROJECT/'cohort_harness/lifecycle.py',OUT.parent/'implementation/main_session_v1.py']},
 'script_sha256':sha(Path(__file__))
}
destination = OUT/'CHNS2009_E1_A05_calculation.json'
destination.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','candidate_freeze_sha256','decision_sha256','source_values','latent_eigenvalues','unavailable_target_as_source_checks']},indent=2))
