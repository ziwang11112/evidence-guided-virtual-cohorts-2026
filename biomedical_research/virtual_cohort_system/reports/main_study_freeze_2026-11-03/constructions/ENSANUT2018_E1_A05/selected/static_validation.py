"""Static artifact validation only. Never imports or executes generator.py."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
from pathlib import Path

C=Path(__file__).resolve().parent
B=C.parent.parent
INTERFACE=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
sys.path.insert(0,str(INTERFACE))
from cohort_harness import lifecycle, semantic_feedback_v1

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj):
    (C/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')

assert not (C/'freeze.json').exists(), 'Author must not mutate a frozen candidate'
required={'generator.py','model_spec.json','evidence.json','decision.md','checks.json','whole_cohort_feedback.json','source_semantics_v1.json','numerical_uptake.json','mathematical_properties.md'}
base_records=[
 {'name':'analytic_affine_moments','status':'pass','detail':'Executed analytic_calculations.py only: closed-form source moments and separate source projections; reported constraints match within1e-12. Analytic result hashes bind the submitted equations/specification.'},
 {'name':'positive_support_and_finite_moments','status':'pass','detail':'Executed32 deterministic support vertices per context; all BMI/HbA1c strictly positive, all glucose strictly between0 and126. Positive variance budgets and positive-definite covariance checked. Mathematical proof covers all first/second moments.'},
 {'name':'pani_age_band_diagnostics','status':'pass','detail':'All8 conditional expectations computed algebraically. Raw discrepancies+0.1315 to+0.3394 percentage points remain unresolved; pass means calculation completed, not source agreement. Explicit age25-84 approximation is retained.'},
 {'name':'source_population_replay','status':'not_computable','detail':'No source-row replay, original survey weights or source individual data supplied. Target rows must not be used as source reconstruction.'},
 {'name':'generator_runtime','status':'not_computable','detail':'No generator import, execution, row generation or Monte Carlo occurred. Root owns isolated execution and final seeds.'},
]
artifacts=[{'path':f,'sha256':sha(C/f)} for f in ['analytic_calculations.py','analytic_results.json','static_validation.py']]
write('checks.json',{'scope':'source_only','records':base_records,'artifacts':artifacts})
assert required <= {p.name for p in C.iterdir()}
source_ops=read(B/'input/source_operations.json')['non_marginal_operations']
uptake=read(C/'numerical_uptake.json')['records']
assert len(uptake)==len(source_ops)==11
assert {x['operation_id'] for x in uptake}=={x['operation_id'] for x in source_ops}
assert len({x['operation_id'] for x in uptake})==len(uptake)
tree=ast.parse((C/'generator.py').read_text(encoding='utf-8'))
imports=[n.names[0].name for n in tree.body if isinstance(n,ast.Import)]
assert imports==['numpy','pandas']
assert not any(isinstance(n,ast.ImportFrom) for n in ast.walk(tree))
assert len([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='generate'])==1
state=lifecycle._state(B,C,'candidates/initial')
semantic=semantic_feedback_v1.preflight(B,'initial')
assert all(x['semantic_status']=='unavailable' for x in semantic['checks'])
analytic=read(C/'analytic_results.json')
assert all(analytic['bindings'][f]==sha(C/f) for f in analytic['bindings'])
spec=read(C/'model_spec.json')['parameters']
assert len(spec['design']['female_values'])*len(spec['design']['age_bands'])*spec['design']['rows_per_cell']==3000
report={
 'status':'pass','scope':'static candidate contracts and declared semantics only',
 'candidate':'candidates/initial','route':state['route'],'required_artifacts':sorted(required),
 'numerical_uptake_operations':len(uptake),'target_source_comparisons_unavailable':len(semantic['checks']),
 'generator_abi':'AST-validated generate(observed,spec,seed); synchronous with three positional arguments',
 'generator_imported':False,'generator_executed':False,'random_draws_performed':False,'rows_generated':0,
 'source_semantic_preflight':'all source comparisons unavailable, as required',
 'model_binding_check':'analytic report matches actual generator/spec/evidence/script hashes',
 'interface_import_bytecode_disabled':sys.dont_write_bytecode,
 'limitations':'Static validation does not establish runtime success, biological validity, source survey reconstruction or target performance.',
}
write('static_validation_result.json',report)
write('semantic_preflight_result.json',semantic)
records=base_records+[{'name':'static_candidate_contract','status':'pass','detail':'lifecycle._state validated task, approved registered source hashes, evidence/specification, generator AST ABI and all check-artifact hashes. No freezing or execution.'},{'name':'semantic_preflight_and_uptake_coverage','status':'pass','detail':'Version1 semantic preflight passed with every source comparison unavailable. All11 admitted non-marginal operations have numerical uptake records and analytic paths.'}]
artifacts += [{'path':f,'sha256':sha(C/f)} for f in ['static_validation_result.json','semantic_preflight_result.json']]
write('checks.json',{'scope':'source_only','records':records,'artifacts':artifacts})
lifecycle._state(B,C,'candidates/initial')
assert not (C/'freeze.json').exists()
print(json.dumps(report,indent=2))
