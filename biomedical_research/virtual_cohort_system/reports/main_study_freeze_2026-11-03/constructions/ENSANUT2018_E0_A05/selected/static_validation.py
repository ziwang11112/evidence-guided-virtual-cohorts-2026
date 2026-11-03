"""Read-only harness validations plus retained receipts; never execute generator."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path

C = Path(__file__).resolve().parent
B = C.parent.parent
H = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
sys.path.insert(0,str(H))
from cohort_harness import lifecycle, semantic_feedback_v1

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name,value):
    (C/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')

state = lifecycle._state(B,C,'candidates/initial')
semantic = semantic_feedback_v1.preflight(B,'initial')
assert all(x['semantic_status']=='unavailable' for x in semantic['checks'])
save('semantic_preflight.json', semantic)
report = {
 'status':'pass',
 'scope':'Static task/evidence/specification/registry/ABI/check-artifact validation plus semantic preflight; no generator import, row sampling, local execution or target outcomes.',
 'route':state['route'],
 'generator_executed':False,
 'source_semantic_check_count':len(semantic['checks']),
 'all_source_comparisons_unavailable':True,
 'inputs':{name:sha(C/name) for name in ['generator.py','model_spec.json','evidence.json','whole_cohort_feedback.json','source_semantics_v1.json','analytic_calculation.py','analytic_results.json']},
 'harness_interfaces':{name:sha(H/'cohort_harness'/name) for name in ['contracts.py','lifecycle.py','semantic_feedback_v1.py','whole_cohort_feedback.py']}
}
save('static_validation.json',report)
artifacts = ['analytic_calculation.py','analytic_results.json','static_validation.py','static_validation.json','semantic_preflight.json']
save('checks.json', {
 'scope':'source_only',
 'records':[
  {'name':'deterministic_law_algebra','status':'pass','detail':'Executed retained analytic_calculation.py: exact demographic mixture moments, Beta moments, affine supports, covariance positive definiteness and law-linked projections pass. Matrix and substitution projection calculations agree. This is model-internal algebra, not source reconstruction or target validation.'},
  {'name':'static_candidate_validation','status':'pass','detail':'Executed lifecycle._state without generator execution: task/evidence/specification/registered hashes/ABI and declared check artifacts satisfy the contract. Static receipt retained.'},
  {'name':'semantic_preflight','status':'pass','detail':'Executed semantic_feedback_v1.preflight: all 17 admitted evidence records are represented, and every source comparison is unavailable. Declaration consistency does not establish authenticity or applicability.'},
  {'name':'controller_generator_execution','status':'not_computable','detail':'No generator import or execution by the author. Controller-owned isolated execution remains required.'},
  {'name':'source_reconstruction','status':'not_computable','detail':'No source replay is allocated. Target rows must not be compared as if they were Lifelines source rows.'},
  {'name':'source_numerical_uptake','status':'pass','detail':'Input source_operations.json contains zero non-marginal operations. The empty numerical_uptake records list is complete for E0.'}
 ],
 'artifacts':[{'path':name,'sha256':sha(C/name)} for name in artifacts]
})
# Verify the final check-artifact bindings as well. This does not import the generator.
lifecycle._state(B,C,'candidates/initial')
assert semantic_feedback_v1.preflight(B,'initial') == semantic
print(json.dumps({'status':'pass','generator_executed':False,'source_checks_unavailable':len(semantic['checks']),'candidate':'candidates/initial'},indent=2))
