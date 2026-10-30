"""Independent post-freeze verification; never generates or repairs candidate rows."""
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent
BUNDLE = ROOT / 'visible/bundle'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def mean(values):
    return math.fsum(values) / len(values)
def sd(values):
    center = mean(values)
    return math.sqrt(math.fsum((x - center) ** 2 for x in values) / (len(values) - 1))

# Independently transcribed from original U1 Table 2 in the pre-run review.
SOURCE = {
    ('White', 'male'): (38, 36.9, 11.0, 28.6, 6.0, 6.1, 1.3),
    ('White', 'female'): (46, 37.1, 10.9, 28.0, 7.4, 4.5, 1.2),
    ('Black', 'male'): (19, 34.3, 11.5, 28.2, 7.3, 6.2, 1.5),
    ('Black', 'female'): (25, 35.1, 11.8, 31.4, 8.7, 4.6, 1.7),
}
KEYS = [('age', 'mean'), ('age', 'sd'), ('bmi', 'mean'), ('bmi', 'sd'), ('urate', 'mean')]
failures = []
comparisons = []
def require(ok, label):
    if not ok:
        failures.append(label)
def close(actual, expected, label, tolerance=1e-10):
    error = abs(float(actual) - float(expected))
    comparisons.append({'check': label, 'absolute_difference': error})
    require(error <= tolerance, label)

report = read(ROOT / 'private/evaluation/final_report.json')
precommit = read(ROOT / 'private/precommit.json')
for relative, digest in precommit['files'].items():
    require(sha(ROOT / relative) == digest, 'precommit:' + relative)
for relative, digest in precommit['harness_files'].items():
    require(sha(PROJECT / relative) == digest, 'harness:' + relative)
require(sha(ROOT / 'private/precommit.json') == report['precommit_sha256'], 'report precommit binding')

feedback_path = ROOT / 'visible/feedback/initial_feedback.json'
feedback = read(feedback_path)
require(feedback['structural_errors'] == [], 'feedback structural status')
require(len(feedback['visible_moment_errors']) == 20, 'feedback has 20 moments')
require(all(not (x['variable'] == 'urate' and x['statistic'] == 'sd') for x in feedback['visible_moment_errors']), 'feedback excludes urate SD')
budget = read(ROOT / 'private/feedback_budget_consumed.json')
require(budget['pass'] == budget['maximum'] == 1, 'single feedback budget')
events = [json.loads(line) for line in (ROOT / 'private/controller_events.jsonl').read_text().splitlines() if line.strip()]
require(sum(x['event'] == 'feedback_complete' for x in events) == 1, 'one logged feedback completion')
require(sum(x['event'] == 'final_evaluation_complete' for x in events) == 1, 'one logged evaluation completion')
result = {'scope': 'Independent source-only post-freeze audit', 'created_utc': datetime.now(timezone.utc).isoformat(), 'candidates': {}, 'execution_receipts': {}}
freezes = {}
for name in ('initial', 'final'):
    folder = BUNDLE / 'candidates' / name
    with (folder / 'generated.csv').open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == ['sample_id', 'race', 'sex', 'age', 'bmi', 'urate'], name + ':columns')
        rows = list(reader)
    require(len(rows) == 128, name + ':row count')
    require(len({x['sample_id'] for x in rows}) == 128 and all(x['sample_id'] for x in rows), name + ':identifiers')
    for row in rows:
        for variable in ('age', 'bmi', 'urate'):
            row[variable] = float(row[variable])
            require(math.isfinite(row[variable]), name + ':finite values')
        require(20 <= row['age'] <= 56 and row['bmi'] > 0 and row['urate'] >= 0, name + ':bounds')
    counts = Counter((x['race'], x['sex']) for x in rows)
    require(dict(counts) == {k: v[0] for k, v in SOURCE.items()}, name + ':group counts')
    frozen = read(folder / 'freeze.json')
    freezes[name] = frozen
    for relative, digest in frozen['commitments'].items():
        require(sha(BUNDLE / relative) == digest, name + ':frozen:' + relative)
    require(frozen['route'] == 'generated.csv', name + ':direct route')
    require(sha(folder / 'generated.csv') == report['candidates'][name]['generated_csv_sha256'], name + ':report CSV binding')
    require(sha(folder / 'freeze.json') == report['candidates'][name]['freeze_sha256'], name + ':report freeze binding')
    run = BUNDLE / 'executions' / (name + '_direct_validation')
    receipt = read(run / 'execution.json')
    require(receipt['generator_executed'] is False and receipt['runtime']['backend'] == 'direct_rows_validation' and receipt['status'] == 'success', name + ':validation-only execution')
    require(receipt['candidate_freeze_sha256'] == sha(folder / 'freeze.json'), name + ':execution freeze binding')
    for relative, digest in receipt['files'].items():
        require(sha(run / relative) == digest, name + ':execution:' + relative)
    require(sha(run / 'input/generated.csv') == sha(run / 'output/generated.csv') == sha(folder / 'generated.csv'), name + ':execution byte identity')
    result['execution_receipts'][name] = {'status': receipt['status'], 'generator_executed': receipt['generator_executed'], 'backend': receipt['runtime']['backend']}
    visible, heldout = [], []
    for (race, sex), source in SOURCE.items():
        group = [x for x in rows if x['race'] == race and x['sex'] == sex]
        group_key = race.lower() + '_' + sex
        for (variable, statistic), reference in zip(KEYS, source[1:6]):
            values = [x[variable] for x in group]
            observed = mean(values) if statistic == 'mean' else sd(values)
            item = {'group': group_key, 'variable': variable, 'statistic': statistic, 'reported': reference, 'observed': observed, 'absolute_error': abs(observed-reference), 'absolute_relative_error': abs(observed-reference)/reference}
            reported_item = next(x for x in report['candidates'][name]['visible_moment_errors'] if (x['group'], x['variable'], x['statistic']) == (group_key, variable, statistic))
            for field in ('reported', 'observed', 'absolute_error', 'absolute_relative_error'):
                close(item[field], reported_item[field], name + ':' + group_key + ':' + variable + ':' + statistic + ':' + field)
            visible.append(item)
        observed, reference = sd([x['urate'] for x in group]), source[6]
        item = {'race': race, 'sex': sex, 'reported': reference, 'observed': observed, 'absolute_error': abs(observed-reference), 'absolute_relative_error': abs(observed-reference)/reference}
        reported_item = next(x for x in report['candidates'][name]['heldout_urate_sd_errors'] if (x['race'], x['sex']) == (race, sex))
        for field in ('reported', 'observed', 'absolute_error', 'absolute_relative_error'):
            close(item[field], reported_item[field], name + ':' + group_key + ':urate_sd:' + field)
        heldout.append(item)
    summaries = {}
    for variable in ('age', 'bmi', 'urate'):
        subset = [x for x in visible if x['variable'] == variable]
        summaries[variable] = {'n_moments': len(subset), 'mean_absolute_error_in_variable_units': mean([x['absolute_error'] for x in subset]), 'mean_absolute_relative_error': mean([x['absolute_relative_error'] for x in subset])}
        for field, value in summaries[variable].items():
            close(value, report['candidates'][name]['visible_separate_variable_summaries'][variable][field], name + ':aggregate:' + variable + ':' + field)
    joint = mean([x['absolute_relative_error'] for x in visible])
    holdout = mean([x['absolute_relative_error'] for x in heldout])
    close(joint, report['candidates'][name]['visible_joint_mean_absolute_relative_error_descriptive_only'], name + ':visible aggregate')
    close(holdout, report['candidates'][name]['heldout_urate_sd_mean_absolute_relative_error'], name + ':heldout aggregate')
    result['candidates'][name] = {'n_rows': len(rows), 'visible_moments': visible, 'visible_variable_summaries': summaries, 'visible_mean_absolute_relative_error': joint, 'heldout_urate_sd': heldout, 'heldout_mean_absolute_relative_error': holdout}

require(freezes['initial']['parent'] is None and freezes['initial']['revision_index'] == 0, 'initial lineage')
require(freezes['final']['parent']['candidate'] == 'candidates/initial' and freezes['final']['revision_index'] == 1, 'final lineage')
require(freezes['final']['parent']['sha256'] == sha(BUNDLE / 'candidates/initial/freeze.json'), 'parent receipt hash')
require(freezes['final']['revision']['kind'] == 'retain' and read(ROOT / 'visible/revision.json')['kind'] == 'retain', 'explicit retain')
require(feedback['input_sha256'] == sha(BUNDLE / 'candidates/initial/generated.csv') and feedback['freeze_sha256'] == sha(BUNDLE / 'candidates/initial/freeze.json'), 'feedback binding to initial')
checks = read(BUNDLE / 'candidates/final/checks.json')
require(any(x['sha256'] == sha(feedback_path) and sha(BUNDLE / 'candidates/final' / x['path']) == sha(feedback_path) for x in checks['artifacts']), 'final exact feedback binding')
same = {filename: (BUNDLE / 'candidates/initial' / filename).read_bytes() == (BUNDLE / 'candidates/final' / filename).read_bytes() for filename in ('generated.csv', 'model_spec.json')}
require(all(same.values()), 'retained bytes identical')
timeline = [precommit['created_utc'], freezes['initial']['created_utc'], budget['utc'], next(x['utc'] for x in events if x['event'] == 'feedback_complete'), freezes['final']['created_utc'], next(x['utc'] for x in events if x['event'] == 'final_evaluation_complete')]
times = [datetime.fromisoformat(x) for x in timeline]
require(times == sorted(times), 'recorded schedule order')
result.update({'status': 'pass' if not failures else 'fail', 'failures': failures, 'precommit_sha256': sha(ROOT / 'private/precommit.json'), 'precommitted_file_count': len(precommit['files']), 'harness_file_count': len(precommit['harness_files']), 'csv_sha256': sha(BUNDLE / 'candidates/initial/generated.csv'), 'identical_initial_final': same, 'recorded_schedule_utc': timeline, 'numeric_comparison_count': len(comparisons), 'maximum_numerical_difference': max(x['absolute_difference'] for x in comparisons), 'comparison_tolerance': 1e-10, 'exploratory_recomputation': 'not performed; audit restricted to requested 20 visible and 4 heldout summaries and provenance', 'authorship_limit': 'Declarations and observed literal tool submission support the direct-row route. This audit cannot prove internal LLM token-generation processes or exclude pretraining recall.'})
with (ROOT / 'postrun_audit_numbers.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
    stream.write('\n')
print(json.dumps({k: result[k] for k in ('status', 'failures', 'maximum_numerical_difference', 'numeric_comparison_count', 'identical_initial_final')}))
print(json.dumps({'visible_mare': result['candidates']['final']['visible_mean_absolute_relative_error'], 'heldout_mare': result['candidates']['final']['heldout_mean_absolute_relative_error'], 'heldout': result['candidates']['final']['heldout_urate_sd']}))
raise SystemExit(0 if not failures else 1)
