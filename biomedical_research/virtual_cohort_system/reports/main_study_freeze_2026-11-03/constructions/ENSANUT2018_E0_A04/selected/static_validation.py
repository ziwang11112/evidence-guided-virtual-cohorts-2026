"""Static artifact checks only. Does not import or execute generator.py."""
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
from pathlib import Path

directory = Path(__file__).resolve().parent
bundle = directory.parent.parent
harness = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
sys.path.insert(0, str(harness))
from cohort_harness import lifecycle
from cohort_harness.semantic_feedback_v1 import preflight

state = lifecycle._state(bundle, directory, 'candidates/initial')
semantic = preflight(bundle, 'candidates/initial')
assert all(row['semantic_status'] == 'unavailable' for row in semantic['checks'])
tree = ast.parse((directory/'generator.py').read_text(encoding='utf-8'))
assert sum(isinstance(node, ast.FunctionDef) and node.name == 'generate' for node in tree.body) == 1
assert not (directory/'freeze.json').exists()
report = {
    'status':'pass',
    'scope':'static_contract_and_declared_source_semantics_only',
    'generator_executed':False,
    'generator_imported':False,
    'frozen':False,
    'route':state['route'],
    'semantic_checks':len(semantic['checks']),
    'all_source_comparisons_unavailable':True,
    'checks':['Task/evidence/specification contract validation','Registered source artifact hash verification','Generator AST and three-positional-argument ABI','Candidate artifacts and check bindings','Source semantic sidecar and recipe hashes','All target-as-source comparisons unavailable'],
    'limitation':'No table was generated or read; output validity and biological validity remain untested.'
}
destination = directory/'static_validation_result.json'
destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
