"""Bind completed author metadata checks; no generator execution or approval."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

sys.dont_write_bytecode = True
W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
P = W / 'biomedical_research/virtual_cohort_system'
C = W / 'evcDC/A02/candidates/self_review'
R = P / 'work/developmental_continuation_v1_2026-11-03/branch_submissions/A02_self_review'
PACKET = W / 'evcDC/ledger/packets/A02_self_review'
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import _checks

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')

validate = read(C / 'HARNESS_VALIDATE.json')
preflight = read(C / 'QUALIFIED_PREFLIGHT.json')
assert validate == {'contract':'valid','route':'program','generator_executed':False,'scientific_validity':'not_assessed'}
assert preflight['status'] == 'metadata_checks_passed' and preflight['counts']['checks_passed'] == 4 and not preflight['findings']
for path, expected in preflight['input_sha256'].items():
    assert digest(Path(path)) == expected
checks = read(C / 'checks.json')
checks['records'].extend([
    {'name':'actual_harness_validate','status':'pass','detail':'Ran Python -B -m cohort_harness validate --bundle D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcDC/A02 --candidate self_review from the project root. Exit 0, program contract valid, generator_executed false; scientific_validity not_assessed.'},
    {'name':'canonical_qualified_author_preflight','status':'pass','detail':'Ran the canonical qualified_author_preflight.py with the same bundle and candidate. Exit 0; 3 contexts and 4 checks passed, 0 findings. This establishes only the stated authored metadata checks.'}
])
checks['artifacts'].extend({'path':name,'sha256':digest(C / name)} for name in ('HARNESS_VALIDATE.json','QUALIFIED_PREFLIGHT.json'))
write(C / 'checks.json', checks)
_checks(C)
manifest = read(PACKET / 'manifest.json')
assert all(digest(PACKET / f) == h for f,h in manifest['files'].items())
same = ('generator.py','model_spec.json','evidence.json','analysis_evidence.json','evidence_use_v1.json','qualified_plan_v1.json','scientific_validity_v1.json','support_selection_v1.json')
assert all(digest(C / f) == manifest['files']['initial/' + f] for f in same)
assert (C / 'context_bridge_v1.json').read_bytes() == (PACKET / 'initial/context_bridge_v1.json').read_bytes().replace(b'A02_initial_', b'A02_self_review_')
assert not any((C / name).exists() for name in ('freeze.json','generated.csv','initial_source_feedback.json'))
assert set(read(R / 'decision.json')) == {'action','packet_sha256','reason','addressed_findings','remaining_limitations'}
size = sum(f.stat().st_size for f in C.iterdir() if f.is_file())
assert size <= 1048576 and (C / 'generator.py').stat().st_size <= 65536
command = [sys.executable,'-B','-m','cohort_harness','validate','--bundle',str(W / 'evcDC/A02'),'--candidate','self_review']
completed = subprocess.run(command, cwd=P, capture_output=True, text=True, check=False)
write(R / 'final_validation.json', {'command':command,'exit_code':completed.returncode,'stdout':json.loads(completed.stdout),'stderr':completed.stderr,'lifecycle_checks_json_validation':'pass','candidate_bytes':size,'generator_bytes':(C / 'generator.py').stat().st_size})
assert completed.returncode == 0
write(R / 'submission_inventory.json', {'scope':'Final metadata inventory; not a freeze, execution or approval receipt.','action':'retain','files':{f.name:{'sha256':digest(f),'bytes':f.stat().st_size} for f in sorted(C.iterdir()) if f.is_file()},'candidate_bytes':size,'retained_scientific_files':list(same),'bridge_change':'Twelve trial identities only; all remaining bytes unchanged.'})
text = '''# A02 self-review author report

Decision: **retain**. The fixed evidence supplies no discriminating basis for replacing the declared age/sex independence, unreported BMI-glucose dependence, or target transport assumptions. The original four qualified source functionals and direct eligible laws are coherent enough to retain for this bounded developmental comparison. Retention does not establish source fit, target validity or improved data.

The generator, full model specification, evidence, final-law and support declarations, qualified plan, evidence-use declaration and analysis-evidence declaration are byte-identical to the assigned accepted-initial packet. The only bridge change is the twelve A02_self_review trial identities; seeds, 3,000-row sizes, budgets and runtime limits are unchanged. A_BMI and A_GLUCOSE remain partial; A_AGE remains unassessed. Added context_eligibility.json restates existing eligibility assumptions without changing the law.

New checks actually performed:

- Read and verified SHA-256 for all 43 manifest-listed packet files; parsed packet JSON and Python AST without executing candidate code. Confirmed assigned bundle task/registry hashes match the packet.
- Static inspection and deterministic scalar algebra checked retained-byte identity, fixed schedule, positive residual-factor variances, declared coefficients against the model, J support below the FPG cutoff and positive native IFCC support. Existing source-identity formulas were checked without data or fitting.
- Ran the packet's admitted pure support, evidence-use and declared-law validators. Support declarations passed; all 36 evidence items are covered; each of the 12 context/analysis moment checks passed. Full scientific-law statuses remain unresolved because independent code/law and rank review are required.
- Ran the actual `python -B -m cohort_harness validate --bundle D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcDC/A02 --candidate self_review` from the project root: exit 0, valid program contract, generator_executed false. Repeated after final metadata completion with the same result.
- Ran the canonical qualified_author_preflight.py with the same bundle/name: exit 0, 3 contexts, 4 operators, no findings. Verified its input hashes remain current.
- Ran the lifecycle `_checks` validator on final checks.json and verified all bound auxiliary hashes. Confirmed submission and generator byte caps.

The check results are bound by checks.json through INPUT_BINDING.json, STATIC_ASSESSMENT.json, HARNESS_VALIDATE.json and QUALIFIED_PREFLIGHT.json. The final CLI result and artifact inventory are in this submission-report directory. Historical checks mentioned by the inherited author were not counted as fresh checks.

No generator import/execution, random sampling, source-output calculation, target analysis, external evidence retrieval, optimization, review approval, freeze or execution receipt was performed or authored. No numerical source feedback was supplied. Original source weighting/processing, tail plausibility, source-to-target transport and uncertainty calibration remain unresolved. The retained law does not support individual recovery, causal or clinical claims, measurement savings, publication readiness, or new independent confirmation from researcher-exposed CHNS.

This is the single scientific retain submission. No scientific changes or schema-only returns were used. Editing stops here pending the controller's separate review.
'''
use_count = read(C / 'STATIC_ASSESSMENT.json')['evidence_use_metadata']['items_covered']
text = text.replace('all 36 evidence items', 'all ' + str(use_count) + ' evidence items')
(R / 'AUTHOR_REPORT.md').write_text(text, encoding='utf-8')
print(json.dumps({'ready':True,'action':'retain','candidate_bytes':size,'generator_bytes':(C / 'generator.py').stat().st_size,'evidence_items':use_count,'final_validate_exit':completed.returncode,'checks_schema':'pass','candidate':str(C),'report':str(R / 'AUTHOR_REPORT.md')}, indent=2))
