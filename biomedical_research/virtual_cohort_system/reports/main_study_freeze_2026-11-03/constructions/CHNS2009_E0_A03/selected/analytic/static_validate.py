"""Static contracts only. Never imports or executes candidate generator code."""
import ast
import hashlib
import json
from pathlib import Path
import sys

HARNESS = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system')
sys.path.insert(0, str(HARNESS))
from cohort_harness import contracts, lifecycle, semantic_feedback_v1

C = Path(__file__).resolve().parents[1]
BUNDLE = C.parents[1]
task = lifecycle.read_json(BUNDLE / 'task.json')
evidence = lifecycle.read_json(C / 'evidence.json')
spec = lifecycle.read_json(C / 'model_spec.json')
contracts.validate_task(task)
contracts.validate_spec(spec, contracts.validate_evidence(evidence, task))
contracts.validate_input(None, task)
lifecycle.validate_program(C / 'generator.py')
_, registrations, _ = lifecycle._registry(BUNDLE)
for source in evidence['sources']:
    for artifact in source['artifacts']:
        assert (source['id'], artifact['path'], artifact['sha256']) in registrations
tree = ast.parse((C / 'generator.py').read_text(encoding='utf-8'))
imports = [node.names[0].name for node in tree.body if isinstance(node, ast.Import)]
assert imports == ['numpy', 'pandas']
assert not any(isinstance(node, ast.ImportFrom) for node in tree.body)
assert not (C / 'generated.csv').exists()
assert not (C / 'freeze.json').exists()
assert not (BUNDLE / 'observed.csv').exists()
required = ['generator.py', 'model_spec.json', 'evidence.json', 'decision.md', 'checks.json',
            'whole_cohort_feedback.json', 'source_semantics_v1.json', 'numerical_uptake.json',
            'mathematical_properties.md']
assert all((C / name).is_file() for name in required)
assert lifecycle.read_json(C / 'numerical_uptake.json') == {'records': []}
semantic = semantic_feedback_v1.preflight(BUNDLE, C)
assert len(semantic['checks']) == 31
assert all(check['semantic_status'] == 'unavailable' for check in semantic['checks'])
(C / 'analytic/semantic_preflight.json').write_text(json.dumps(semantic, indent=2, allow_nan=False) + '\n', encoding='utf-8')
report = {'status': 'pass', 'scope': 'static schema, ABI syntax, source registration and declared semantics only',
          'generator_imported': False, 'generator_executed': False, 'sampling_performed': False,
          'scientific_validity': 'not_assessed', 'source_comparisons_available': 0,
          'source_comparisons_unavailable': len(semantic['checks']), 'required_artifacts_present': required,
          'validated_input_hashes': {name: hashlib.sha256((C / name).read_bytes()).hexdigest()
              for name in ['generator.py', 'model_spec.json', 'evidence.json', 'whole_cohort_feedback.json',
                           'source_semantics_v1.json', 'numerical_uptake.json']}}
(C / 'analytic/static_report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
