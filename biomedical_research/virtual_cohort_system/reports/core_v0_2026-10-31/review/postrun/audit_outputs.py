"""Read-only scalar audit of the artificial replay; never imports its generator."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys

UNIT = Path(__file__).resolve().parents[2]
PROJECT = UNIT.parents[1]
BUNDLE = UNIT / 'bundle'
EXPECTED_ASSEMBLY = '697d2728f64bc6da77a1d6e39339e444fb18d7a6c679f9432507ed8ca07ec17b'
sys.path.insert(0, str(PROJECT))
from cohort_harness.lifecycle import verify_candidate
from cohort_harness.execution import verify_execution
from cohort_harness.whole_cohort_feedback import verify_feedback


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def audit(stage):
    assembly = read(UNIT / 'ASSEMBLY.json')
    check(sha(UNIT / 'ASSEMBLY.json') == EXPECTED_ASSEMBLY, 'Assembly identity changed')
    for name, digest in assembly['files'].items():
        check(sha(name) == digest, 'Assembly byte mismatch: ' + name)
    historical = read(UNIT / 'HISTORICAL_BINDINGS.json')
    for name, digest in historical['files'].items():
        check(sha(PROJECT / name) == digest, 'Historical anchor hash mismatch: ' + name)
    candidate = BUNDLE / 'candidates' / stage
    frozen = verify_candidate(BUNDLE, candidate)
    receipt = verify_execution(BUNDLE, stage + '_run')
    report = verify_feedback(BUNDLE, stage + '_feedback', candidate=candidate, run_id=stage + '_run')
    check(receipt['status'] == 'success' and receipt['generator_executed'] is True, 'No successful program execution')
    check(receipt['limits']['seed'] == 26301 and receipt['isolation_scope'] == 'generator_process_only', 'Wrong execution profile')
    check(receipt['runtime'] == assembly['runtime_configuration'], 'Runtime configuration mismatch')
    run = BUNDLE / 'executions' / (stage + '_run')
    worker = read(run / 'output/worker_report.json')
    manifest = read(run / 'runtime_manifest.json')
    launch = read(run / 'launch.json')
    check(worker['status'] == 'completed' and worker['generator_started'] is True, 'Worker did not complete')
    check(worker['runtime'] == {k: manifest[k] for k in ['python', 'numpy', 'pandas']}, 'Worker runtime versions differ')
    check(worker['pre_import_probe']['mnt_visible'] is False and worker['pre_import_probe']['home_visible'] is False, 'Unexpected host mount visibility')
    check(worker['pre_import_probe']['route_table'] == [], 'Unexpected network routes')
    check(all(flag in launch['argv'] for flag in ['--unshare-all', '--clearenv', '--cap-drop', '--remount-ro']), 'Missing recorded isolation flags')
    check({p.name for p in (run / 'input').iterdir()} == {'task.json', 'model_spec.json', 'generator.py', 'request.json', 'worker.py'}, 'Unexpected staged input')
    check(not (BUNDLE / 'observed.csv').exists(), 'Observed data present')
    source = BUNDLE / 'sources/fictional-study-a.txt'
    check(sha(source) == 'a9a1831c74ef04d7ce97cd012c4c208a9815551cdd248d0762e244e75a5d66d2', 'Source changed')
    matches = re.findall(r'x=(\d): mean ([\d.]+) u, SD ([\d.]+) u\.', source.read_text(encoding='utf-8'))
    facts = {int(x): {'mean': float(mean), 'sd': float(sd)} for x, mean, sd in matches}
    check(facts == {0: {'mean': 2., 'sd': 1.}, 1: {'mean': 3., 'sd': 1.5}, 2: {'mean': 4., 'sd': 2.}}, 'Unexpected source facts')
    with (run / 'output/generated.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        check(reader.fieldnames == ['sample_id', 'x', 'group', 'y'], 'Wrong CSV schema')
        rows = list(reader)
    check(len(rows) == 768 and len({r['sample_id'] for r in rows}) == 768, 'Row/identifier count mismatch')
    grouped = {x: [] for x in facts}
    for row in rows:
        check(row['sample_id'] and row['group'] == '0' and row['x'] in {'0', '1', '2'}, 'Invalid design value')
        value = float(row['y'])
        check(math.isfinite(value) and value >= 0, 'Invalid y support')
        grouped[int(row['x'])].append(value)
    check(all(len(values) == 256 for values in grouped.values()), 'Quota mismatch')
    check(len(report['checks']) == 6 and report['n_computable'] == 6 and report['n_not_computable'] == 0, 'Incomplete feedback')
    scalar = []
    seen = set()
    for entry in report['checks']:
        op = entry['operator']
        selections = {(f['column'], f['op'], f['value']) for f in op['selection']}
        x = next(x for x in facts if selections == {('group', 'eq', 0), ('x', 'eq', x)})
        kind = op['kind']
        check(kind in {'mean', 'sd'} and op['column'] == 'y' and op['unit'] == 'u' and op['missing_policy'] == 'error', 'Wrong source operator')
        check((kind, x) not in seen, 'Duplicate source statistic')
        seen.add((kind, x))
        values = grouped[x]
        mean = math.fsum(values) / len(values)
        estimate = mean if kind == 'mean' else math.sqrt(math.fsum((y - mean) ** 2 for y in values) / (len(values) - 1))
        reported = facts[x][kind]
        difference = estimate - reported
        check(entry['reported_value'] == reported and entry['source_id'] == 'T1', 'Source value/link mismatch')
        check(entry['calculation']['n_input'] == 768 and entry['calculation']['n_selected'] == entry['calculation']['n_used'] == 256 and entry['calculation']['n_missing_dropped'] == 0, 'Feedback row counts differ')
        check(math.isclose(estimate, entry['calculation']['value'], rel_tol=0, abs_tol=1e-12), 'Independent statistic differs')
        check(math.isclose(difference, entry['difference'], rel_tol=0, abs_tol=1e-12), 'Independent difference differs')
        scalar.append({'id': entry['id'], 'kind': kind, 'x': x, 'n': 256, 'source_value': reported, 'independent_value': estimate, 'difference': difference, 'absolute_recomputation_error': abs(estimate-entry['calculation']['value'])})
    check(seen == {(k, x) for k in ['mean', 'sd'] for x in facts}, 'Missing source statistic')
    if stage == 'final':
        check(frozen['revision_index'] == 1 and frozen['revision']['kind'] == 'retain', 'Expected one retain decision')
        check(frozen['parent']['sha256'] == sha(BUNDLE / 'candidates/initial/freeze.json'), 'Wrong parent')
        for name in ['generator.py', 'model_spec.json', 'evidence.json', 'whole_cohort_feedback.json']:
            check((candidate / name).read_bytes() == (BUNDLE / 'candidates/initial' / name).read_bytes(), 'Retention bytes differ: ' + name)
        feedback_path = BUNDLE / 'whole_cohort_feedback/initial_feedback/feedback.json'
        check((candidate / 'initial_source_feedback.json').read_bytes() == feedback_path.read_bytes(), 'Feedback copy differs')
        check({'path': 'initial_source_feedback.json', 'sha256': sha(feedback_path)} in read(candidate / 'checks.json')['artifacts'], 'Feedback copy not bound')
        check((run / 'output/generated.csv').read_bytes() == (BUNDLE / 'executions/initial_run/output/generated.csv').read_bytes(), 'Same-seed retained output differs')
        check(sorted(p.name for p in (BUNDLE / 'executions').iterdir()) == ['final_run', 'initial_run'], 'Unexpected scientific run directory')
    return {'status': 'pass', 'stage': stage, 'scope': 'Independent arithmetic and retained-record audit; not scientific validity', 'created_utc': datetime.now(timezone.utc).isoformat(), 'audit_code_sha256': sha(__file__), 'assembly_sha256': EXPECTED_ASSEMBLY, 'assembly_files_checked': len(assembly['files']), 'historical_anchor_count': len(historical['files']), 'historical_scope': historical['scope'], 'source_sha256': sha(source), 'candidate_freeze_sha256': sha(candidate / 'freeze.json'), 'execution_sha256': sha(run / 'execution.json'), 'output_sha256': sha(run / 'output/generated.csv'), 'feedback_sha256': sha(BUNDLE / 'whole_cohort_feedback' / (stage + '_feedback') / 'feedback.json'), 'native_verifiers_passed': ['candidate', 'execution', 'feedback'], 'independent_method': 'Python csv + math.fsum; sample SD sqrt(sum((y-mean)^2)/(n-1)); no NumPy/pandas or shared estimator for independent values', 'floating_point_comparison_tolerance': 1e-12, 'tolerance_purpose': 'Arithmetic agreement only, never a source-fit acceptance threshold', 'rows': 768, 'quotas': {str(x): len(values) for x, values in grouped.items()}, 'nonnegative_y': True, 'isolation_evidence': {'scope': receipt['isolation_scope'], 'agent_isolation': receipt['agent_isolation'], 'launch': launch['isolation'], 'pre_import_probe': worker['pre_import_probe'], 'runtime': worker['runtime']}, 'checks': scalar, 'generator_imported_or_executed_by_audit': False, 'row_table_copied_by_audit': False, 'new_scientific_runs': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['initial', 'final'], required=True)
    stage = parser.parse_args().stage
    result = audit(stage)
    destination = Path(__file__).with_name(stage + '_independent_audit.json')
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'stage': stage, 'output': str(destination), 'checks': result['checks']}))
