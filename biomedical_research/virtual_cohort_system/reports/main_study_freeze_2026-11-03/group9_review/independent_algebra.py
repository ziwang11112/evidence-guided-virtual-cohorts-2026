"""Independent deterministic review of ENSANUT2018_E1_A05.

No generator import, generator execution, row sampling, quadrature, Monte Carlo,
source retrieval, target results, session outcomes, or other candidates.
Only read the explicitly assigned artifacts and approved harness modules.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import numpy as np

W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
R = W/'evcMS/ENSANUT2018_E1_A05'
B = R/'bundle'
C = B/'candidates/initial'
PROJECT = W/'biomedical_research/virtual_cohort_system'
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT))
from cohort_harness import lifecycle

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def close(actual, expected, label, tol=1e-10):
    if not np.allclose(actual, expected, rtol=0, atol=tol):
        raise AssertionError(label + ': ' + str(actual) + ' != ' + str(expected))

receipt = lifecycle.verify_candidate(B, 'candidates/initial')
freeze_hash = sha(C/'freeze.json')
decision_hash = sha(R/'decision.json')
decision = read(R/'decision.json')
assert decision['author_id'] == 'ENSANUT2018_E1_A05'
assert decision['candidate'] == 'candidates/initial'
assert decision['action'] == 'initial_final' and decision['reason']
assert receipt['parent'] is None and receipt['revision_index'] == 0
task, spec = read(B/'task.json'), read(C/'model_spec.json')
p = spec['parameters']
ev_json = read(C/'evidence.json')
assert ev_json == read(B/'input/evidence.json')
ev = {x['id']: x for x in ev_json['items']}
registry = read(B/'registry.json')
source_extracts = {}
for record in registry['artifacts']:
    path = B/record['path']
    assert sha(path) == record['sha256']
    for block in re.findall(r'```json\s*(.*?)\s*```', path.read_text(encoding='utf-8-sig'), re.S):
        obj = json.loads(block)
        source_extracts[obj['evidence']['id']] = obj['evidence']
assert source_extracts == ev, 'Candidate evidence differs from admitted extract records'

code = (C/'generator.py').read_text(encoding='utf-8')
tree = ast.parse(code)
assert [n.names[0].name for n in tree.body if isinstance(n, ast.Import)] == ['numpy', 'pandas']
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
assert len(fn) == 1 and fn[0].name == 'generate'
assert len(fn[0].args.args) == 3
assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(fn[0]))
# Compare the actual implementation expressions with the independently reviewed law.
expressions = {
    'z': "(2 * rng.beta(shape, shape, size=(n, 3)) - 1) * np.sqrt(2 * shape + 1)",
    'bmi': "c['bmi'] + v['bmi_age'] * ac + v['bmi_female'] * fc + s['bmi'] * z[:, 0]",
    'glucose': "c['glucose'] + v['glucose_age'] * ac + v['glucose_female'] * fc + s['glucose'] * (rho * z[:, 0] + np.sqrt(1 - rho**2) * z[:, 1])",
    'hba1c': "c['hba1c'] + h['age'] * ac + h['female'] * fc + h['bmi'] * (bmi - c['bmi']) + h['glucose'] * (glucose - c['glucose']) + s['hba1c'] * z[:, 2]",
}
for name, expression in expressions.items():
    assignments = [node.value for node in fn[0].body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)]
    assert len(assignments) == 1
    assert ast.dump(assignments[0]) == ast.dump(ast.parse(expression, mode='eval').body), name
d = p['design']
assert d['age_bands'] == [[25,39],[40,54],[55,69],[70,79]]
assert d['female_values'] == [0,1]
assert d['rows_per_cell'] == 375 and d['n_rows'] == task['n_rows'] == 3000
assert "rng.integers(low, high + 1, size=d['rows_per_cell'])" in code
assert "np.full(d['rows_per_cell'], female, dtype=int)" in code
assert "for female in d['female_values']" in code
assert "for low, high in d['age_bands']" in code
frame_call = [n for n in ast.walk(fn[0]) if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Attribute) and n.func.attr == 'DataFrame'][0]
assert [k.value for k in frame_call.args[0].keys] == [x['name'] for x in task['columns']]

c, v, s, h = (p[k] for k in ['centers','covariate_effects','residual_scales','response'])
assert p['latent']['shape'] == 3.0
zbound = math.sqrt(7)
rho = v['residual_correlation']
assert -1 < rho < 1
assert all(x > 0 for x in s.values())
root = math.sqrt(1-rho*rho)
ka = h['age'] + h['bmi']*v['bmi_age'] + h['glucose']*v['glucose_age']
kf = h['female'] + h['bmi']*v['bmi_female'] + h['glucose']*v['glucose_female']
L = np.array([
    [1,0,0,0,0],
    [0,1,0,0,0],
    [v['bmi_age'],v['bmi_female'],s['bmi'],0,0],
    [v['glucose_age'],v['glucose_female'],s['glucose']*rho,s['glucose']*root,0],
    [ka,kf,h['bmi']*s['bmi'] + h['glucose']*s['glucose']*rho,
     h['glucose']*s['glucose']*root,s['hba1c']],
])
assert np.all(np.diag(L) > 0)
saved = read(C/'analytic_results.json')
close(L, saved['moment_derivation']['loading_matrix'], 'Actual affine loading')

conversions = {
    'J_T1_female_proportion_derived': 1-ev['J_T1_male_proportion_reported']['estimate'],
    'J_T1_glucose_mean_mg_dL_derived': ev['J_T1_glucose_mean_mmol_L']['estimate']*18,
    'J_T1_glucose_sd_mg_dL_derived': ev['J_T1_glucose_sd_mmol_L']['estimate']*18,
    'J_T1_hba1c_mean_pct_from_ifcc': ev['J_T1_hba1c_mean_ifcc']['estimate']*.09148+2.152,
    'J_T1_hba1c_sd_pct_from_ifcc': ev['J_T1_hba1c_sd_ifcc']['estimate']*.09148,
    'J_T2_bmi_slope_task_derived': ev['J_T2_bmi_slope_original']['estimate']*.09148,
    'J_T2_glucose_slope_task_derived': ev['J_T2_glucose_slope_original']['estimate']*.09148/18,
}
for item_id, value in conversions.items():
    close(value, ev[item_id]['estimate'], 'Unit conversion '+item_id)
assert p['measurement_conversion'] == {'ifcc_to_ngsp_scale':.09148,
    'ifcc_to_ngsp_offset':2.152,'glucose_mmol_L_to_mg_dL':18.0}
for key, eid in {'age':'J_T1_age_mean_task','female':'J_T1_female_proportion_derived',
                 'bmi':'J_T1_bmi_mean_task','glucose':'J_T1_glucose_mean_mg_dL_derived',
                 'hba1c':'J_T1_hba1c_mean_pct'}.items():
    close(c[key], ev[eid]['estimate'], 'Source center '+key)

j = p['source_contexts']['lifelines']
q = p['source_contexts']['pani']
assert j == {'age_family':'continuous_uniform_from_mean_sd','age_mean':55.5,
             'age_sd':9.9,'female_probability':.597}
assert q == {'age_family':'discrete_uniform','age_minimum':25,
             'age_maximum':84,'female_probability':.5}
vf = j['female_probability']*(1-j['female_probability'])
vbudget = {
    'bmi': p['source_marginal_sds']['bmi']**2-v['bmi_age']**2*j['age_sd']**2-v['bmi_female']**2*vf,
    'glucose': p['source_marginal_sds']['glucose']**2-v['glucose_age']**2*j['age_sd']**2-v['glucose_female']**2*vf,
    'hba1c': p['source_marginal_sds']['hba1c']**2-(ka*ka*j['age_sd']**2+kf*kf*vf+L[4,2]**2+L[4,3]**2),
}
for key, value in vbudget.items():
    assert value > 0
    close(value, s[key]**2, 'Positive residual variance '+key)

def moments(ma, va, pf):
    mu = np.array([ma,pf,c['bmi']+v['bmi_age']*(ma-c['age'])+v['bmi_female']*(pf-c['female']),
                   c['glucose']+v['glucose_age']*(ma-c['age'])+v['glucose_female']*(pf-c['female']),
                   c['hba1c']+ka*(ma-c['age'])+kf*(pf-c['female'])])
    cov = L@np.diag([va,pf*(1-pf),1,1,1])@L.T
    return mu,cov

means = [(lo+hi)/2 for lo,hi in d['age_bands']]
vars_ = [((hi-lo+1)**2-1)/12 for lo,hi in d['age_bands']]
task_ma = sum(means)/4
task_va = sum(vv+mm**2 for vv,mm in zip(vars_,means))/4-task_ma**2
contexts = {'lifelines':(55.5,9.9**2,.597), 'pani':(54.5,(60**2-1)/12,.5),
            'task_design':(task_ma,task_va,.5)}
moment_results = {}
for label, args in contexts.items():
    mu,cov = moments(*args)
    original = saved['moment_derivation']['source_moments'][label]
    close(mu, original['mean'], label+' mean')
    close(cov, original['covariance'], label+' covariance')
    eig = float(np.linalg.eigvalsh(cov).min())
    assert eig > 0
    moment_results[label] = {'mean':mu.tolist(), 'covariance':cov.tolist(),
        'second_raw_moments':(np.diag(cov)+mu*mu).tolist(), 'minimum_eigenvalue':eig}
for var, sd in p['source_marginal_sds'].items():
    idx = ['age','female','bmi','glucose','hba1c'].index(var)
    close(moment_results['lifelines']['covariance'][idx][idx], sd*sd, 'Source marginal '+var)

# Independent FWL formulas, followed by independently formed covariance solves.
slopes = {'J_T2_bmi_slope_task_derived': h['bmi']+h['glucose']*rho*s['glucose']/s['bmi'],
          'J_T2_glucose_slope_task_derived':h['glucose']+h['bmi']*rho*s['bmi']/s['glucose'],
          'P_NHANES_age_slope':h['age']}
xs_by_id = {'J_T2_bmi_slope_task_derived':[2,0,1],
            'J_T2_glucose_slope_task_derived':[3,0,1],'P_NHANES_age_slope':[0,1,2,3]}
ops = read(B/'input/source_operations.json')['non_marginal_operations']
assert len(ops) == 11
uptake = read(C/'numerical_uptake.json')['records']
assert len(uptake) == 11 and {x['operation_id'] for x in uptake} == {x['operation_id'] for x in ops}
assumptions = {x['id'] for x in spec['assumptions']}
for record in uptake:
    oid = record['operation_id']
    assert record['evidence_ids'] == [oid]
    assert record['source_ids'] == [ev[oid]['source_id']]
    assert record['source_population_selection'] == ev[oid]['selection']
    assert set(record['source_law_assumptions']) <= assumptions
    assert record['target_comparison_status'] == 'unavailable'
    assert record['use'] == ('model_constraint' if oid in slopes else 'analytic_check')
    for field in ['parameter_paths','constraint_paths','analytic_artifact_paths']:
        assert record[field]
        for reference in record[field]:
            filename, *pointer = reference.split('#',1)
            path = C/filename
            assert path.is_file()
            if pointer:
                obj = read(path)
                for part in pointer[0].lstrip('/').split('/'):
                    obj = obj[part]
    for field in ['measurement_assumptions','source_uncertainty_treatment','cross_source_overlap',
                  'identified_by_input','construction_assumes','reason']:
        assert record[field]

projection_results, ageband_results = {}, {}
for op in ops:
    oid = op['operation_id']
    if oid in slopes:
        close(slopes[oid], ev[oid]['estimate'], 'FWL slope '+oid)
        close(slopes[oid], saved['source_projections'][oid]['value'], 'Retained slope '+oid)
        mat = np.array(moment_results[op['source_context']]['covariance'])
        ids = xs_by_id[oid]
        beta = np.linalg.solve(mat[np.ix_(ids,ids)], mat[ids,4])
        close(beta[0], slopes[oid], 'Covariance slope '+oid)
        assert ev[oid]['adjustment'] == (['female','bmi','glucose'] if oid == 'P_NHANES_age_slope' else ['age','female'])
        projection_results[oid] = {'independent_fwl_value':slopes[oid],
            'independent_covariance_solve':float(beta[0]),'reported_value':ev[oid]['estimate'],
            'source_context':op['source_context']}
    else:
        rule = op['age_rule']
        lo = max(q['age_minimum'],rule['minimum_inclusive'])
        hi = min(q['age_maximum'],q['age_maximum'] if rule['maximum_exclusive'] is None else rule['maximum_exclusive']-1)
        ma = (lo+hi)/2
        prob = (hi-lo+1)/(q['age_maximum']-q['age_minimum']+1)
        value = c['hba1c']+ka*(ma-c['age'])+kf*(q['female_probability']-c['female'])
        retained = saved['pani_ageband_means'][oid]
        assert retained['assumed_age_support'] == [lo,hi]
        close(value,retained['value'],'Band mean '+oid)
        close(prob,retained['band_probability'],'Band probability '+oid)
        close(value*prob,retained['hba1c_indicator_expectation'],'Band numerator '+oid)
        close(value-ev[oid]['estimate'],retained['raw_difference'],'Band discrepancy '+oid)
        assert retained['source_estimate_uncertainty'] == ev[oid]['uncertainty']
        ageband_results[oid] = {'age_support':[lo,hi], 'probability':prob,
            'indicator_expectation':prob*value,'mean':value,'reported':ev[oid]['estimate'],
            'difference':value-ev[oid]['estimate'],'source_se':ev[oid]['uncertainty']['value']}

# Interval propagation of the expanded affine law; no generated points or vertices.
supports = {}
age_supports = {'task_design':[25,79], 'pani':[25,84],
                'lifelines':[55.5-math.sqrt(3)*9.9,55.5+math.sqrt(3)*9.9]}
for label, arange in age_supports.items():
    intervals = [(arange[0]-c['age'],arange[1]-c['age']),(-c['female'],1-c['female']),
                 (-zbound,zbound),(-zbound,zbound),(-zbound,zbound)]
    limits = {}
    for i,name in enumerate(['bmi','glucose','hba1c'],2):
        lower = c[name]+sum(min(coef*a,coef*b) for coef,(a,b) in zip(L[i],intervals))
        upper = c[name]+sum(max(coef*a,coef*b) for coef,(a,b) in zip(L[i],intervals))
        close([lower,upper],saved['support'][label][name],'Support '+label+'/'+name)
        assert lower > 0
        if name == 'glucose': assert upper < 126
        limits[name] = [float(lower),float(upper)]
    supports[label] = limits

feedback = read(C/'whole_cohort_feedback.json')
semantics = read(C/'source_semantics_v1.json')
preflight = read(C/'semantic_preflight_result.json')
assert len(feedback['checks']) == len(semantics['bindings']) == len(preflight['checks']) == 29
assert all(x['status'] == 'not_computable' and x['operator'] is None for x in feedback['checks'])
assert all(x['definition_status'] == 'unsupported' and x['source_operator'] is None for x in semantics['bindings'])
assert all(x['semantic_status'] == 'unavailable' for x in preflight['checks'])
assert semantics['evidence_sha256'] == sha(C/'evidence.json')
assert semantics['recipe_sha256'] == sha(C/'whole_cohort_feedback.json')
for filename, digest in saved['bindings'].items():
    assert sha(C/filename) == digest
assert saved['admitted_operator_sha256'] == sha(B/'input/source_operators.py')
# Verify once more after the calculations; no frozen writes occur in this script.
lifecycle.verify_candidate(B,'candidates/initial')
assert freeze_hash == sha(C/'freeze.json') and decision_hash == sha(R/'decision.json')

result = {'status':'pass','reviewer_id':'/root/main_review_g9',
    'candidate_freeze_sha256':freeze_hash,'decision_sha256':decision_hash,
    'lifecycle_verify_candidate':'passed twice; generator not imported/executed',
    'evidence_identity':'All 30 candidate items equal input and parsed registered source records',
    'law_link':'AST expressions checked, independently expanded affine equations, exact variance and FWL formulas',
    'exact_design':{'rows':3000,'cells':8,'rows_per_cell':375,'age_bands':d['age_bands'],'female_values':[0,1]},
    'proper_latent_law':{'family':'Beta(3,3)','normalizer_B_3_3':1/30,'standardized_mean':0,
        'standardized_variance':1,'support':[-zbound,zbound]},
    'finite_moment_basis':'Bounded A,F,Z and affine outputs imply finite absolute first, second and all higher moments; positive diagonal loading and component variances imply nonsingular covariance.',
    'residual_variance_budget':vbudget,'unit_conversions':conversions,
    'source_projections':projection_results,'pani_ageband_checks':ageband_results,
    'moments':moment_results,'support':supports,'uptake_records_verified':11,
    'target_as_source_unavailable_checks':29,'generator_imported':False,'generator_executed':False,
    'rows_sampled':0,'monte_carlo_used':False,'quadrature_used':False,'target_results_used':False,
    'script_sha256':sha(Path(__file__)),
    'read_only_bindings':{str(path):sha(path) for path in [R/'profile.json',B/'task.json',
        B/'input/source_operations.json', B/'input/source_operators.py',B/'input/evidence_normalization.json',
        PROJECT/'cohort_harness/contracts.py',PROJECT/'cohort_harness/lifecycle.py',
        PROJECT/'work/main_study_freeze_2026-11-03/implementation/main_session_v1.py']}}
(OUT/'independent_algebra_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'candidate_freeze_sha256':freeze_hash,
    'decision_sha256':decision_hash,'source_projections':projection_results,
    'task_support':supports['task_design'],'uptake_records_verified':11,
    'target_as_source_unavailable_checks':29},indent=2))
