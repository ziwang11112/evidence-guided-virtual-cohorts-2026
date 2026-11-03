"""Bind completed metadata checks without executing candidate science."""
from pathlib import Path
import hashlib
import json
import sys
sys.dont_write_bytecode = True
W = Path('D:/AIR-014_ECRC_Paper_Clean_2026-08-16')
P = W / 'biomedical_research/virtual_cohort_system'
C = W / 'evcDC/A01/candidates/self_review'
R = P / 'work/developmental_continuation_v1_2026-11-03/branch_submissions/A01_self_review'
sys.path.insert(0, str(P))
from cohort_harness.lifecycle import _checks, read_json

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')

validate = read_json(C / 'METADATA_VALIDATE.json')
preflight = read_json(C / 'QUALIFIED_AUTHOR_PREFLIGHT.json')
assert validate == {'contract': 'valid', 'route': 'program', 'generator_executed': False, 'scientific_validity': 'not_assessed'}
assert preflight['status'] == 'metadata_checks_passed' and preflight['counts']['checks_passed'] == 4 and not preflight['findings']
checks = read_json(C / 'checks.json')
checks['records'] += [
    {'name': 'actual_harness_validate', 'status': 'pass', 'detail': 'Ran Python312 -B -m cohort_harness validate --bundle D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcDC/A01 --candidate self_review from the project root; exit 0, contract valid, program route, generator_executed false. CLI stdout is bound.'},
    {'name': 'canonical_qualified_author_preflight', 'status': 'pass', 'detail': 'Ran the canonical qualified_author_preflight.py with the same bundle and candidate from the project root; exit 0, all 3 contexts and 4 operators passed metadata checks, zero findings. This grants no source authenticity or scientific/lifecycle approval.'}
]
checks['artifacts'] += [{'path': name, 'sha256': digest(C / name)} for name in ['METADATA_VALIDATE.json', 'QUALIFIED_AUTHOR_PREFLIGHT.json']]
write(C / 'checks.json', checks)
_checks(C)
manifest = read_json(W / 'evcDC/ledger/packets/A01_self_review/manifest.json')
for name in ['generator.py', 'model_spec.json', 'evidence.json', 'analysis_evidence.json', 'qualified_plan_v1.json', 'evidence_use_v1.json', 'scientific_validity_v1.json', 'support_selection_v1.json']:
    assert digest(C / name) == manifest['files']['initial/' + name]
files = {p.name: {'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(C.iterdir()) if p.is_file()}
assert len(files) == len(list(C.iterdir()))
total = sum(v['bytes'] for v in files.values())
assert total <= 1048576 and files['generator.py']['bytes'] <= 65536
assert 'freeze.json' not in files and 'generated.csv' not in files
decision = read_json(R / 'decision.json')
assert set(decision) == {'action', 'packet_sha256', 'reason', 'addressed_findings', 'remaining_limitations'} and decision['action'] == 'retain'
write(R / 'FINAL_METADATA_CHECKS.json', {'scope': 'author_metadata_only', 'candidate_bytes': total,
    'generator_bytes': files['generator.py']['bytes'], 'candidate_cap': 1048576, 'generator_cap': 65536,
    'lifecycle_checks_schema_and_artifact_hashes': 'pass', 'decision_schema': 'pass',
    'retained_scientific_hashes': 'pass', 'candidate_files': files,
    'generator_executed': False, 'source_or_target_statistics_calculated': False,
    'approval_or_freeze': 'not_performed'})
report = f'''# A01 self-review author submission

Decision: **retain**. The assigned self-review packet contains no numerical source feedback. The inherited joint law is coherent under its explicit assumptions, but the evidence does not identify a better age/sex dependence, rank-dependence or target-transport replacement. The retained limitations remain scientifically consequential; this decision claims no improvement in data quality.

Candidate: `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcDC/A01/candidates/self_review`.
Decision: `decision.json` in this report directory.
Packet SHA256: `fb1311a17ec99f5d51a9907d0687e99c1ad13e78a33f180d21c4fd3a5f74a6c1`.

Generator, full specification, evidence and the five other scientific declaration files remain byte-identical to the assigned accepted initial packet. The twelve bridge trial IDs now use A01_self_review; contexts, seeds, 3,000 rows per trial, limits and budgets are unchanged. The same initial freeze identified by the packet is the intended parent; no sibling is parented. Added context_eligibility.json only restates existing required_domains and unobserved selection assumptions. The decision prose and check/binding artifacts record this branch's actual work.

Actual checks completed:

- Verified all 43 manifest-member hashes, assigned bundle task/registry equality, canonical metadata utility/contracts equality to the supplied interfaces, and eight retained scientific-file hashes.
- Parsed generator source with AST without importing it. Ran the packet pure declared-law, support-selection and evidence-use validators; 12 declared analysis moment checks and 22 support-domain checks passed. Exact decimal affine endpoint calculations matched the declared final supports. Population rank conditions were reviewed separately from empirical rank. Full scientific validity remains unresolved.
- Ran the actual `python -B -m cohort_harness validate --bundle .../evcDC/A01 --candidate self_review` from the project root: exit 0, contract valid, generator_executed false. Ran the canonical `qualified_author_preflight.py` with that bundle/name: exit 0, 3 contexts and 4 checks passed, no findings.
- Ran the lifecycle `_checks` metadata validator after binding all four auxiliary artifacts. Verified exact decision keys and final size caps: candidate {total:,} bytes; generator {files['generator.py']['bytes']:,} bytes. FINAL_METADATA_CHECKS.json records these checks and file hashes; it is not a freeze, approval or execution receipt.

No inherited historical check is claimed as newly performed. No generator import/execution, random sample, generated table, source statistic computation, retained-row check, target analysis, target/reference read, external retrieval or numerical source feedback access occurred. No review approval, freeze or execution receipt was authored. Empirical rank, numerical fidelity, runtime support, source reconstruction and target utility remain unevaluated by this author.

A_BMI and A_GLUCOSE retain partial evidence coverage; A_AGE remains unassessed. Age/sex independence, the no-direct-BMI factorization, gamma/uniform shapes, unfit source age summaries/Bao HbA1c quartiles, and J/M-to-T transport remain assumptions or gaps. Native source measurements and operators are preserved; strict replay stays unavailable. Individual dispersion and simulation seeds do not quantify evidence or transport uncertainty. CHNS remains researcher-exposed developmental reference.

The single scientific decision is submitted. No author-side schema return was needed. Editing stops at submission.
'''
(R / 'AUTHOR_REPORT.md').write_text(report, encoding='utf-8')
print(json.dumps({'decision': 'retain', 'submission_ready': True, 'candidate_bytes': total,
    'generator_bytes': files['generator.py']['bytes'], 'lifecycle_checks': 'pass',
    'report': str(R / 'AUTHOR_REPORT.md')}, indent=2))
