"""Bind a completed static review; never import or execute candidate code."""
from pathlib import Path
import ast
import hashlib
import json

W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
B = W/'evcUseL03'
C = B/'candidates/initial'
R = W/'biomedical_research/virtual_cohort_system/work/evidence_use_cross_task_2026-11-05/review'
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

# Same inventory rule as lifecycle._files: all regular files except freeze.json.
files = {}
for p in sorted(C.rglob('*')):
    assert not p.is_symlink() and not p.is_junction(), p
    assert p.is_dir() or p.is_file(), p
    name = p.relative_to(C).as_posix()
    if p.is_file() and name != 'freeze.json':
        files[name] = sha(p)
attempt = read(B/'implementation_validation/attempt01/attempt.json')
assert files == attempt['candidate_hashes']
assert attempt['all_static_gates_pass'] is True
spec = read(C/'model_spec.json')
p = spec['parameters']
task = read(B/'task.json')
assert p['n_rows'] == task['n_rows'] == 3000
assert p['female_probability'] == .5
assert p['age'] == {'probabilities':[0,.25,.5,.75,1], 'knots':{'M':[18,24,33,46,90],'F':[18,25,34,48,90]}, 'upper_tail_power':.5}
assert p['age_biomarker_conditional_independence'] is True
assert p['biomarker_order'] == ['bmi','total_cholesterol','hdl_cholesterol']
assert p['marginal_moments'] == {'bmi':{'mean':21.63,'sd':3.61},'total_cholesterol':{'mean':3.23,'sd':.92},'hdl_cholesterol':{'mean':1.14,'sd':.38}}
assert p['female_to_male_geometric_ratios'] == {'bmi':23.2/21.5,'total_cholesterol':3.9/3.6,'hdl_cholesterol':1.10/1.05}
assert p['copula_spearman'] == {'bmi_tc':.212,'bmi_hdl':-.1,'tc_hdl':.106}
assert 'A_sex_mapping' in {x['id'] for x in spec['assumptions']}
tree = ast.parse((C/'generator.py').read_text(encoding='utf-8-sig'))
fns = [n for n in tree.body if isinstance(n,ast.FunctionDef)]
assert len(fns) == 1 and fns[0].name == 'generate'
assert [a.arg for a in fns[0].args.args] == ['observed','specification','seed']
assert not fns[0].args.vararg and not fns[0].args.kwarg and not fns[0].args.kwonlyargs
assert [n.names[0].name for n in tree.body if isinstance(n,ast.Import)] == ['numpy','pandas']
sem = read(C/'source_semantics_v1.json')
feedback = read(C/'whole_cohort_feedback.json')
assert len(sem['bindings']) == len(feedback['checks']) == 21
assert all(x['weights'] == 'not_reported' for x in sem['bindings'])
assert all(x['status'] == 'not_computable' and x['operator'] is None for x in feedback['checks'])
assert sem['evidence_sha256'] == sha(C/'evidence.json')
assert sem['recipe_sha256'] == sha(C/'whole_cohort_feedback.json')
for entry in read(C/'checks.json')['artifacts']:
    assert sha(C/entry['path']) == entry['sha256']
assert sha(C/'checks/analytic_derivation.json') == sha(B/'ANALYTIC_DERIVATION.json')
assert sha(C/'checks/controller_analytic_recheck.json') == sha(R/'L03_ANALYTIC_RECHECK.json')
assert sha(C/'checks/controller_source_review.md') == sha(R/'L03_SOURCE_PROPOSAL.md')
for binding in read(C/'evidence_use_v1.json')['bindings'].values():
    assert sha(B/binding['path']) == binding['sha256']
report = {
    'schema_version':1, 'date':'2026-11-05', 'author':'L03',
    'reviewer_id':'/root/source_proposal_review_b', 'candidate':'candidates/initial',
    'approved':True, 'scientific_code_spec_consistency':True,
    'finite_moments_supported':True, 'source_semantics_reviewed':True,
    'target_results_used':False, 'candidate_files':files,
    'narrative_sha256':sha(R/'L03_CANDIDATE_REVIEW.md'),
    'narrative_path':'review/L03_CANDIDATE_REVIEW.md',
    'decision':'APPROVED_FOR_FREEZE_AND_SCHEDULED_ISOLATED_TRIAL',
    'blocking_findings':[], 'approved_source_law_unchanged':True,
    'required_sex_mapping_assumption_present':True,
    'all_numerical_specification_parameters_used':True,
    'seed_handling':'Single supplied seed passed to numpy.random.default_rng; no seed search or reseeding',
    'silent_filters_or_repairs_found':False,
    'source_feedback_not_computable_count':21,
    'matches_attempt01_candidate_hashes':True,
    'attempt01_static_gates_reported_pass':True,
    'checks_this_reviewer_performed':['Human code/spec/source semantics inspection','AST parse without import','Exact approved-parameter equality','All lifecycle file hash bindings','Auxiliary review/algebra copy hash equality','Evidence-use and source-semantic file bindings'],
    'generator_imported':False, 'generator_executed':False,
    'random_rows_produced':False, 'clinical_rows_read':False,
    'reference_results_read':False, 'other_scientific_candidates_read':False,
    'candidate_files_modified':False,
    'limitations':'Static approval supports the intended law and source consistency only; actual runtime outputs and target validity are untested.'
}
(R/'L03_CANDIDATE_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'approved':True,'candidate_file_count':len(files),'narrative_sha256':report['narrative_sha256']},indent=2))
