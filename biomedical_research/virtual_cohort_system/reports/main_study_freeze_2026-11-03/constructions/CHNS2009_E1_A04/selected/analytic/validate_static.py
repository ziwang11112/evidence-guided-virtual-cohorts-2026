"""Static interfaces only; does not import or execute candidate scientific code."""
import sys
sys.dont_write_bytecode = True
import ast, hashlib, json
from pathlib import Path

C=Path(__file__).resolve().parents[1]
B=C.parents[1]
PROJECT=Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
sys.path.insert(0,str(PROJECT))
from cohort_harness import lifecycle, semantic_feedback_v1

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj): p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')
results=json.loads((C/'analytic/results.json').read_text())
assert results['bindings']['generator_text_sha256']==sha(C/'generator.py')
assert results['bindings']['model_spec_sha256']==sha(C/'model_spec.json')
assert results['bindings']['derivation_script_sha256']==sha(C/'analytic/derive.py')
assert results['checks']['target_rows_generated']==0 and results['checks']['source_rows_generated']==0
tree=ast.parse((C/'generator.py').read_text())
decl=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='generate']
assert len(decl)==1
assert [a.arg for a in decl[0].args.args]==['observed','spec','seed']
assert not (C/'generated.csv').exists()
assert not (C/'freeze.json').exists()
operations=json.loads((B/'input/source_operations.json').read_text())['operations']
uptake=json.loads((C/'numerical_uptake.json').read_text())['records']
assert {x['evidence_id'] for x in operations}=={x['operation_id'] for x in uptake}
assert len(uptake)==len(operations)
base_artifacts=['analytic/derive.py','analytic/results.json','analytic/validate_static.py']
records=[
 {'name':'law_moment_and_support_algebra','status':'pass','detail':'Executed analytic/derive.py only. All contexts have positive residual variances, positive measurement support, positive definite covariance; Jansen source FPG support below 7. Exact factor algebra; zero rows, Monte Carlo or quadrature.'},
 {'name':'qualified_source_operations','status':'pass','detail':'Admitted operator returned Jansen BMI 0.13000000000000003 and FPG 2.29 native IFCC slopes. Those are constraints by construction. Bao Pearson 0.6824284695170836 versus reported 0.619; raw discrepancy 0.06342846951708359 retained without pass margin or refitting.'},
 {'name':'mind_rank_numerical_check','status':'not_computable','detail':'No MIND post-imputation source rank law or source rows; ordinary moments do not identify Spearman. Contextual use is not claimed as numeric uptake.'},
 {'name':'source_comparisons_on_target','status':'not_computable','detail':'Every source statistic is marked unavailable on target execution; no source replay supplied.'},
 {'name':'row_production','status':'not_computable','detail':'Generator syntax/signature checked only; not imported or executed. No exploratory trial requested. Isolated controller owns all row production.'}
]
write(C/'checks.json',{'scope':'source_only','records':records,'artifacts':[{'path':x,'sha256':sha(C/x)} for x in base_artifacts]})
state=lifecycle._state(B,C,'candidates/initial')
semantic=semantic_feedback_v1.preflight(B,'initial')
assert all(x['semantic_status']=='unavailable' for x in semantic['checks'])
write(C/'analytic/semantic_preflight.json',semantic)
report={
 'status':'pass','scope':'Static contract/ABI/registry/hash and declared-semantics checks only; no generator import or execution.',
 'checks':['lifecycle._state accepted unfrozen candidate','generate(observed,spec,seed) AST signature accepted','registered source hashes verified by lifecycle','all four admitted operations have exactly one uptake record','all semantic target-as-source comparisons unavailable','analytic result bindings match current code/spec/script'],
 'route':state['route'],'source_operation_count':len(operations),'unavailable_target_source_checks':len(semantic['checks']),
 'generator_imported':False,'generator_executed':False,'rows_generated':0,'frozen_by_author':False,
 'inputs':{'generator_sha256':sha(C/'generator.py'),'model_spec_sha256':sha(C/'model_spec.json'),'evidence_sha256':sha(C/'evidence.json'),'script_sha256':sha(Path(__file__))}}
write(C/'analytic/static_validation.json',report)
records.append({'name':'static_contract_and_semantic_preflight','status':'pass','detail':'lifecycle._state and semantic_feedback_v1.preflight succeeded on the unfrozen program; all source comparison bindings unavailable. Registry source hashes and every required artifact verified. Static validation is not execution success.'})
all_artifacts=base_artifacts+['analytic/semantic_preflight.json','analytic/static_validation.json']
write(C/'checks.json',{'scope':'source_only','records':records,'artifacts':[{'path':x,'sha256':sha(C/x)} for x in all_artifacts]})
lifecycle._state(B,C,'candidates/initial')
print(json.dumps(report,indent=2))
