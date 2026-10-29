"""Call the existing static freeze/verify harness; no generator execution."""
from pathlib import Path
import hashlib
import json
import sys

bundle = Path(__file__).resolve().parent
sys.path.insert(0, str(bundle.parents[2]))
from cohort_harness.lifecycle import freeze_candidate, verify_candidate


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


labels = ['zero', 'minus', 'plus']
specs = []
for label in labels:
    spec = json.loads((bundle/'candidates'/label/'model_spec.json').read_text(encoding='utf-8'))
    spec['parameters']['density_interaction'].pop('sign')
    specs.append(spec)
assert specs[0] == specs[1] == specs[2]
common = ['generator.py','evidence.json','source_replay.json','source_contexts/oh.csv','source_contexts/bansal.csv','analytic_certificate.json','semantic_metrics.json','baseline_lineage.json','baseline_source_feedback.json','builder_plan.md','static.json','contract_validation.json','checks.json']
for name in common:
    assert len({sha(bundle/'candidates'/label/name) for label in labels}) == 1, name

results = []
for label in labels:
    candidate = bundle/'candidates'/label
    freeze_candidate(bundle, candidate)
    verify_candidate(bundle, candidate)
    receipt = json.loads((candidate/'freeze.json').read_text(encoding='utf-8'))
    result = {
        'candidate': label,
        'freeze_sha256': sha(candidate/'freeze.json'),
        'generator_sha256': sha(candidate/'generator.py'),
        'spec_sha256': sha(candidate/'model_spec.json'),
        'analytic_certificate_sha256': sha(candidate/'analytic_certificate.json'),
        'created_utc': receipt['created_utc'],
        'revision_index': receipt['revision_index'],
        'parent': receipt['parent'],
        'verified': True,
        'generator_executed': False,
    }
    results.append(result)
    print(json.dumps(result))
report = {
    'scope': 'builder_static_freeze_verify_only',
    'common_files_identical': common,
    'specs_differ_only_in_density_interaction_sign': True,
    'candidates': results,
    'execution_status': 'not_run_controller_only_after_independent_review',
}
destination = bundle.parent/'design/FREEZE_READINESS.json'
destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
