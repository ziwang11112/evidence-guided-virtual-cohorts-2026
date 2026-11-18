"""Record reviewed bytes and read-only configuration checks. No model calls/rows."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location('lifestyle_preflight_adapter', ROOT / 'api_loop.py')
api = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(api)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
plan = read(ROOT / 'PLAN.json')
files = api.required_local_files(plan) - {'PREFLIGHT_REVIEW.json'}
files |= {'SOURCE_METHODS.md', 'LIFESTYLE_TOKEN_AUDIT.json', 'reference_adapter.py', 'evaluate.py',
          'test_analysis.py', 'ANALYSIS_TEST_RECEIPT.json', 'test_runtime_adapter.py',
          'RUNTIME_ADAPTER_TESTS.json', 'RUNTIME_PLAN.md', 'review/check_lr.py', 'review/LR_CHECK.json',
          'review/METHOD_REVIEW_PRELIM.md'}
reviewed = {name: sha(ROOT / name) for name in sorted(files)}
external = {p.resolve().as_posix(): sha(p) for p in api.required_external_files()}
checks = []
def check(label, condition): checks.append(dict(check=label, passed=bool(condition)))
check('exactly two fresh registered constructors', [x['episode_id'] for x in plan['episodes']] == ['LIFESTYLE_A1', 'LIFESTYLE_A2'])
check('three exact final seeds', plan['evaluation_seeds'] == [64001, 64003, 64007])
check('one revision cap through two immutable submissions', plan['limits']['max_candidates'] == 2)
check('two diagnostic execution cap', plan['limits']['max_runs'] == plan['limits']['max_executions'] == 2)
check('USD4 per author and USD8 total ceilings', plan['limits']['episode_usd_cap'] == 4 and plan['limits']['total_usd_cap'] == 8)
check('fresh diagnostic seed', plan['limits']['diagnostic_seed'] == 63001 and 63001 not in plan['evaluation_seeds'])
task = read(ROOT / plan['episodes'][0]['task_path'])
check('whole cohort 1226 rows', task['mode'] == 'whole_cohort' and task['n_rows'] == 1226)
check('exact seven columns', [c['name'] for c in task['columns']] == ['id','age','sex','lifestyle','bmi','total_cholesterol','hdl_cholesterol'])
check('complete generated data supported by unchanged contract', all(c['nullable'] is False for c in task['columns']))
check('both lipids use mg/dL', all(c['unit'] == 'mg/dL' for c in task['columns'] if c['name'] in ['total_cholesterol','hdl_cholesterol']))
check('source-rich exclusions only project', task['information_policy']['excluded_cohorts'] == ['evidence-guided-virtual-cohorts-2026','virtual_cohort_system'])
check('same task and policy for both authors', len({(x['task_path'],x['request_path'],x['policy_path']) for x in plan['episodes']}) == 1)
operator = read(ROOT / 'ANALYSIS_TEST_RECEIPT.json')
check('six earlier invented operator checks passed', operator['passed'] == 6 and operator['failed'] == 0)
for n, h in operator['files'].items(): check('operator-test-byte-binding:' + n, sha(ROOT / n) == h)
runtime = read(ROOT / 'RUNTIME_ADAPTER_TESTS.json')
check('seven earlier runtime mocks passed', runtime['status'] == 'pass' and runtime['tests'] == 7 and runtime['api_requests'] == runtime['generator_executions'] == runtime['patient_reads'] == 0)
for n, h in runtime['file_hashes'].items(): check('runtime-test-byte-binding:' + n, sha(ROOT / n) == h)
lr = read(ROOT / 'review/LR_CHECK.json')
check('new independent LR fixture passed for all three outcomes', lr['status'] == 'pass' and len(lr['checks']) == 3 and all(x['pass_check'] for x in lr['checks']))
for n, h in lr['hashes'].items(): check('LR-test-byte-binding:' + n, sha(ROOT / n) == h)
check('no current target analysis opened or present at preflight', not (ROOT / 'ANALYSIS_RESULTS.json').exists())
failed = [x['check'] for x in checks if not x['passed']]
report = dict(status='pass' if not failed else 'require_fix',
              reviewer='revision_independent_review', created_utc=datetime.now(timezone.utc).isoformat(),
              reviewed_files=reviewed, reviewed_external_files=external,
              credential_helper_sha256=sha(api.KEY_HELPER),
              checks=checks, blocking_issues=failed,
              manual_review=[
                  'Original source Methods model 1 and 2, outcome scaling and measurement meanings checked against the primary paper; available aggregate values distinguished from unrecovered supplementary workbooks.',
                  'One three-category fit supplies all three linear contrasts with full coefficient covariance; raw-unit conversion uses the selected table/trait SD.',
                  'All nine additive and 18 sex-specific contrasts remain visible; pooled scaling is reused for sex-specific fits; Gaussian ML LRT has two interaction degrees of freedom.',
                  'BH9 is explicitly the current additive subset family, not the original eleven-outcome family or post-selection guarantee.',
                  'Real adapter excludes missing covariates and strict age-ineligible records, validates nonmissing tokens, uses per-trait available cases; virtual completeness is an explicit difference.',
                  'Generated statistics dispatch only to the new pure operator; no prior PNS/lipid fallback or target reference is exposed in trials.',
                  'Immutable candidate submission, recorded diagnostics, bounded model/tool spending and original-source retrieval are retained; actual trial use or non-revision must be reported, not assumed.',
                  'Global construction closure precedes all final draws and new reference evaluation; isolated worker remains WSL/bubblewrap with no host generator import.',
                  'Evaluation retains failed datasets and all 27 CSV slots; all real/virtual input hashes are checked before and after analysis.',
                  'No frozen historical experiment was changed; source-rich reconstruction is explicitly distinguished from independent target validation.'
              ],
              limitations=[
                  'The original author script and S1/S2 workbooks were not recovered. Scaling-denominator, common categorical fit and LRT implementation details are declared reimplementation choices.',
                  'Published demographic counts disagree with the narrative recruitment total, and some age-bin boundaries are ambiguous; the Agent must explain assumptions rather than calibrate to private rows.',
                  'The task schema permits age=18 at the interface minimum while scientific eligibility is strictly >18. Such rows are excluded and counted, not silently accepted scientifically.',
                  'Generated-only diagnostics and declared finite-moment requirements do not certify a proposed probability law; actual submitted laws still need post-construction scientific inspection.',
                  'Complete synthetic biomarker data do not reproduce real measurement missingness. Conditional intervals/p-values cannot represent evidence uncertainty or new clinical information.',
                  'Two constructors and six conditional draws support a bounded application pilot, not model-wide superiority. No pre/post feedback-quality causal claim is warranted without matched earlier final draws.'
              ],
              target_rows_decoded=False, current_target_effects_inspected=False,
              new_api_calls=0, generator_executions=0,
              tests_repeated=False,
              audit_scope='read-only files, source methods and metadata; one explicitly authorized new invented LR fixture')
with (ROOT / 'PREFLIGHT_REVIEW.json').open('x', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False, allow_nan=False)
    f.write('\n')
print(json.dumps(dict(status=report['status'], checks=len(checks), failures=failed,
                     reviewed_files=len(reviewed), external_files=len(external),
                     receipt_sha256=sha(ROOT / 'PREFLIGHT_REVIEW.json'))))
if failed: raise SystemExit(1)
