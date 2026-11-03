"""Independent deterministic review. Never import or execute candidate code.

Permitted inputs: this bundle, its profile/decision, and the harness lifecycle.
No sampled rows, RNG calls, numerical quadrature, or target results are used.
"""
import ast
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
PROJECT = W / 'biomedical_research/virtual_cohort_system'
ROOT = W / 'evcMS/ENSANUT2018_E0_A03'
BUNDLE = ROOT / 'bundle'
CAND = BUNDLE / 'candidates/initial'
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT))
from cohort_harness import lifecycle

def read(path):
    return lifecycle.read_json(path)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def frac(value):
    return Fraction(str(value))

checks = []
def check(name, condition, detail):
    checks.append({'id': name, 'passed': bool(condition), 'detail': detail})

freeze_before = sha(CAND / 'freeze.json')
decision_before = sha(ROOT / 'decision.json')
receipt = lifecycle.verify_candidate(BUNDLE, 'candidates/initial')
check('lifecycle_verify_candidate', True, 'Fresh lifecycle.verify_candidate passed; no generator import or execution.')
task = read(BUNDLE / 'task.json')
profile = read(ROOT / 'profile.json')
identity = read(BUNDLE / 'input/identity.json')
decision = read(ROOT / 'decision.json')
spec = read(CAND / 'model_spec.json')
p = spec['parameters']
evidence = read(CAND / 'evidence.json')
input_evidence = read(BUNDLE / 'input/evidence.json')
normalization = read(BUNDLE / 'input/evidence_normalization.json')
operations = read(BUNDLE / 'input/source_operations.json')
uptake = read(CAND / 'numerical_uptake.json')
items = {r['id']: r for r in evidence['items']}
norms = {r['item_id']: r for r in normalization['records']}
check('identity_and_decision', task['task_id'] == identity['author_id'] == decision['author_id'] == ROOT.name and
      profile['information_condition'] == identity['information_condition'] == 'E0' and
      decision['candidate'] == 'candidates/initial' and decision['action'] == 'initial_final',
      'ENSANUT2018 E0 A03 initial_final decision and profile agree.')
check('admitted_evidence_exact', evidence == input_evidence, 'All candidate source and item records equal the admitted input evidence.')

source_items = {}
source_norms = {}
registry = read(BUNDLE / 'registry.json')
for entry in registry['artifacts']:
    source_path = BUNDLE / entry['path']
    check('source_hash_' + entry['source_id'], sha(source_path) == entry['sha256'], entry['path'])
    for block in re.findall(r'```json\s*(.*?)\s*```', source_path.read_text(encoding='utf-8-sig'), re.S):
        record = json.loads(block)
        source_items[record['evidence']['id']] = record['evidence']
        source_norms[record['normalization']['item_id']] = record['normalization']
check('scoped_source_mapping', source_items == items and source_norms == norms,
      '17 evidence items and normalizations match the registered scoped source JSON blocks.')
check('e0_non_marginal_uptake', operations['condition'] == 'E0' and
      operations['non_marginal_operations'] == uptake['records'] == [],
      'Empty uptake is the complete E0 operation inventory; no non-marginal operation omitted.')

selected = {
    'bmi': ('J_T1_bmi_mean_task', 'J_T1_bmi_sd_task'),
    'glucose': ('J_T1_glucose_mean_mg_dL_derived', 'J_T1_glucose_sd_mg_dL_derived'),
    'hba1c': ('J_T1_hba1c_mean_pct', 'J_T1_hba1c_sd_pct'),
}
for variable, (mean_id, sd_id) in selected.items():
    check('anchor_' + variable, p[variable]['mean'] == items[mean_id]['estimate'] and
          p[variable]['sd'] == items[sd_id]['estimate'] and
          p[variable]['unit'] == items[mean_id]['unit'] == items[sd_id]['unit'] and
          items[mean_id]['kind'] == 'mean' and items[sd_id]['kind'] == 'sd',
          'Selected mean and individual SD match the specified source representation and units.')
check('glucose_conversion', frac(items['J_T1_glucose_mean_mg_dL_derived']['estimate']) ==
      frac(items['J_T1_glucose_mean_mmol_L']['estimate']) * 18 and
      frac(items['J_T1_glucose_sd_mg_dL_derived']['estimate']) ==
      frac(items['J_T1_glucose_sd_mmol_L']['estimate']) * 18,
      '91.8=5.1*18; 9.0=0.5*18; one source mean/SD pair.')
check('hba1c_alternative_conversion', math.isclose(items['J_T1_hba1c_mean_pct_from_ifcc']['estimate'], 38*0.09148+2.152) and
      math.isclose(items['J_T1_hba1c_sd_pct_from_ifcc']['estimate'], 3*0.09148) and
      spec['parameter_provenance']['hba1c']['evidence_ids'] == list(selected['hba1c']),
      'IFCC alternatives are correctly converted and are not additional HbA1c construction anchors.')
check('source_demography_not_imposed', not spec['parameter_provenance']['design']['evidence_ids'] and
      not spec['parameter_provenance']['age_law']['evidence_ids'],
      'Source age and sex margins are contextual; task demographics take precedence.')

d = p['design']
check('exact_demographic_quota_spec', d == {'n_rows':3000, 'per_cell':375, 'female_values':[0,1],
      'age_bands':[[25,39],[40,54],[55,69],[70,79]]} and task['n_rows'] == 3000,
      'Two sex values times four nonoverlapping age bands times 375 = 3000; 1500 per sex.')
source = (CAND / 'generator.py').read_text(encoding='utf-8-sig')
syntax = ast.parse(source)
imports = [a.name for node in syntax.body if isinstance(node, ast.Import) for a in node.names]
call_names = sorted({ast.unparse(node.func) for node in ast.walk(syntax) if isinstance(node, ast.Call)})
check('generator_static_interface', imports == ['numpy','pandas'] and
      not any(isinstance(node, (ast.ImportFrom, ast.While)) for node in ast.walk(syntax)) and
      'rng.gamma' in call_names and 'rng.beta' in call_names and
      not any(name in call_names for name in ['open','eval','exec','compile','__import__']),
      'AST-only inspection: standard RNG calls, no file access/dynamic execution/retry loop.')
check('law_selectors', p['age_law'] == 'discrete_uniform_within_each_band' and
      p['dependence_law'] == 'mutually_independent_biomarkers_and_demographics',
      'Independent biomarker draws and an inclusive integer age draw in each fixed cell; final permutation preserves cells.')

moments = {}
exact = {}
for variable in ('bmi','glucose','hba1c'):
    margin = p[variable]
    m, s = frac(margin['mean']), frac(margin['sd'])
    if margin['family'] == 'gamma':
        shape, scale = m*m/(s*s), s*s/m
        mean, variance = shape*scale, shape*scale*scale
        assert shape > 0 and scale > 0
        pars = {'shape':float(shape), 'scale':float(scale), 'support':'(0,infinity)'}
    elif margin['family'] == 'scaled_beta':
        lower, upper = frac(margin['lower']), frac(margin['upper'])
        width = upper-lower
        q, v = (m-lower)/width, (s/width)**2
        assert 0 < q < 1 and 0 < v < q*(1-q)
        c = q*(1-q)/v-1
        alpha, beta = q*c, (1-q)*c
        mean = lower+width*alpha/(alpha+beta)
        variance = width**2*alpha*beta/((alpha+beta)**2*(alpha+beta+1))
        assert alpha > 0 and beta > 0
        pars = {'alpha':float(alpha), 'beta':float(beta), 'concentration':float(c),
                'support':f'({lower},{upper})'}
    else:
        raise AssertionError('Unexpected law')
    assert mean == m and variance == s*s
    exact[variable] = (mean, variance)
    moments[variable] = {**pars, 'mean':float(mean), 'variance':float(variance),
                         'second_raw_moment':float(variance+mean*mean)}
    check('law_moments_' + variable, True, 'Exact rational arithmetic establishes proper shapes and source-anchored first two moments.')

band_moments = [(Fraction(a+b,2), Fraction((b-a+1)**2-1,12)) for a,b in d['age_bands']]
age_mean = sum(m for m,v in band_moments)/4
age_second = sum(v+m*m for m,v in band_moments)/4
age_variance = age_second-age_mean*age_mean
moments['age'] = {'mean':float(age_mean),'variance':float(age_variance),'second_raw_moment':float(age_second)}
moments['female'] = {'mean':0.5,'variance':0.25,'second_raw_moment':0.5}
diagonal = {'age10':age_variance/100, 'female':Fraction(1,4), 'bmi5':exact['bmi'][1]/25,
            'glucose10':exact['glucose'][1]/100}
check('population_ols_exists', all(v > 0 for v in diagonal.values()),
      'Independent centered predictors have positive diagonal covariance; all requested population OLS projections exist uniquely.')
check('task_support', task['columns'][3]['minimum'] == math.nextafter(0,math.inf) and
      p['glucose']['lower'] == 0 and p['glucose']['upper'] == 126 and
      task['columns'][4]['maximum'] == math.nextafter(126,-math.inf),
      'Generator finite/open-support guards imply the numeric task bounds on successful execution; HbA1c upper 100 is disclosed modeling support.')

authored = read(CAND / 'analytic_results.json')
for variable, result in moments.items():
    check('retained_algebra_' + variable, all(math.isclose(authored['moments'][variable][k],result[k],rel_tol=1e-12,abs_tol=1e-12)
          for k in ('mean','variance','second_raw_moment')),
          'Independently recomputed moments agree with the frozen analytic record.')
check('analytic_input_hashes', authored['generator_sha256'] == sha(CAND/'generator.py') and
      authored['model_spec_sha256'] == sha(CAND/'model_spec.json'), 'Retained authored analytic record binds the current frozen generator and specification.')

feedback = read(CAND / 'whole_cohort_feedback.json')
semantics = read(CAND / 'source_semantics_v1.json')
check('source_checks_unavailable', {c['evidence_id'] for c in feedback['checks']} == set(items) and
      len(feedback['checks']) == len(items) and all(c['status'] == 'not_computable' and c['operator'] is None for c in feedback['checks']),
      'All 17 target-as-source checks declare not_computable with no statistic operator.')
check('source_semantics_unavailable', {c['evidence_id'] for c in semantics['bindings']} == set(items) and
      len(semantics['bindings']) == len(items) and all(c['definition_status'] == 'unsupported' and c['source_operator'] is None for c in semantics['bindings']),
      'All 17 source definitions explicitly deny a target-table source calculation.')
check('semantic_hash_bindings', semantics['evidence_sha256'] == sha(CAND/'evidence.json') and
      semantics['recipe_sha256'] == sha(CAND/'whole_cohort_feedback.json'),
      'Semantic declarations bind the exact evidence and unavailable-feedback recipe.')
check('unmodified_commitments', sha(CAND/'freeze.json') == freeze_before and sha(ROOT/'decision.json') == decision_before,
      'Candidate receipt and outside decision hashes unchanged throughout independent review.')

result = {'candidate':str(CAND), 'reviewer_id':'/root/main_review_g5',
          'candidate_freeze_sha256':freeze_before, 'decision_sha256':decision_before,
          'review_script_sha256':sha(Path(__file__)), 'checks':checks,
          'all_checks_passed':all(c['passed'] for c in checks),
          'moments':moments, 'predictor_centered_covariance_diagonal':{k:float(v) for k,v in diagonal.items()},
          'lifecycle_receipt_route':receipt['route'], 'lifecycle_verified_candidate_file_count':len(receipt['candidate_files']),
          'generator_ast_call_inventory':call_names, 'generator_imported':False, 'generator_executed':False,
          'row_sampling_performed':False, 'numerical_quadrature_performed':False, 'target_results_used':False}
destination = OUT / 'ENSANUT2018_E0_A03_calculations.json'
destination.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'all_checks_passed':result['all_checks_passed'], 'check_count':len(checks),
                  'failed_checks':[c for c in checks if not c['passed']], 'candidate_freeze_sha256':freeze_before,
                  'decision_sha256':decision_before, 'output':str(destination)},indent=2))
