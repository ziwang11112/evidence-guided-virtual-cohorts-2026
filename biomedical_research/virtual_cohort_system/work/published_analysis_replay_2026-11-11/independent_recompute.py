"""Independent fixed-input covariance audit. Run only after the parent authorizes.

No production evaluator import, API, generator, fitting choices, or row exports.
The Schur complement of the joint covariance replaces production OLS/lstsq.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
FIELDS = ['age', 'sex', 'bmi', 'total_cholesterol', 'hdl_cholesterol']
REAL_FIELDS = ['Age', 'Sex', 'BMI', 'Total cholesterol', 'HDL cholesterol']
PAIR_INDICES = [(0, 1), (0, 2), (1, 2)]
PAIR_IDS = ['bmi__total_cholesterol', 'bmi__hdl_cholesterol',
            'total_cholesterol__hdl_cholesterol']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def checked_path(relative):
    p = (PROJECT / relative).resolve()
    if not p.is_relative_to(PROJECT.resolve()):
        raise RuntimeError('Input escapes project')
    return p


def verify_files(bindings, freeze):
    checks = []
    for name, expected in freeze['files'].items():
        checks.append((f'freeze:{name}', digest(HERE / name) == expected))
    for m in bindings['manifests']:
        checks.append((f'manifest:{m["path"]}', digest(checked_path(m['path'])) == m['sha256']))
    for d in bindings['inputs']:
        p = checked_path(d['path'])
        checks.extend([(f'input-hash:{d["id"]}', digest(p) == d['sha256']),
                       (f'input-bytes:{d["id"]}', p.stat().st_size == d['bytes'])])
        if 'receipt_path' in d:
            checks.append((f'receipt:{d["id"]}', digest(checked_path(d['receipt_path'])) == d['receipt_sha256']))
    if not all(v for _, v in checks):
        raise RuntimeError('Bound input/freeze mismatch: ' + str([k for k, v in checks if not v]))
    return checks


def independent_parse(path, is_real):
    # Positional CSV parser, with field validation before the common-case mask.
    selected = []
    excluded = dict(missing=0, nonfinite=0, age_not_above_18=0, nonpositive_biomarker=0)
    total = 0
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream, delimiter='\t' if is_real else ',')
        header = next(reader)
        required = REAL_FIELDS if is_real else FIELDS
        if not set(required).issubset(header):
            raise ValueError('Required schema columns absent')
        positions = [header.index(k) for k in required]
        for row in reader:
            if not row:
                continue
            total += 1
            cells = [(row[i] if i < len(row) else '').strip() for i in positions]
            if cells[1] not in ('F', 'M', '', 'NA'):
                raise ValueError('Unrecognized sex token; table withheld')
            numeric = []
            for i in (0, 2, 3, 4):
                if cells[i] in ('', 'NA'):
                    numeric.append(None)
                else:
                    try:
                        numeric.append(float(cells[i]))
                    except ValueError:
                        raise ValueError('Unrecognized numeric token; table withheld') from None
            if any(s in ('', 'NA') for s in cells):
                excluded['missing'] += 1
                continue
            if any(not math.isfinite(v) for v in numeric):
                excluded['nonfinite'] += 1
                continue
            age, bmi, tc, hdl = numeric
            if not age > 18:
                excluded['age_not_above_18'] += 1
                continue
            if any(v <= 0 for v in (bmi, tc, hdl)):
                excluded['nonpositive_biomarker'] += 1
                continue
            factor = 1.0 if is_real else 38.67
            selected.append((age, 1.0 if cells[1] == 'F' else 0.0,
                             bmi, tc * factor, hdl * factor))
    data = np.array(selected, dtype=float).reshape(-1, 5)
    counts = dict(input_rows=total, retained_rows=len(data), exclusions=excluded,
                  hdl_above_tc_retained_rows=sum(row[4] > row[3] for row in selected),
                  common_complete_cases=True)
    return data, counts


def covariance_partial_correlations(data):
    if len(data) <= 5:
        raise ValueError('Insufficient complete rows')
    centered = data - data.mean(axis=0)
    cov = centered.T @ centered / (len(data) - 1)
    nuisance = cov[:2, :2]
    if np.linalg.matrix_rank(nuisance) != 2:
        raise ValueError('Rank-deficient nuisance design')
    if np.any(np.sqrt(np.diag(cov)[2:]) <= np.finfo(float).eps):
        raise ValueError('Constant biomarker')
    conditional = cov[2:, 2:] - cov[2:, :2] @ np.linalg.solve(nuisance, cov[:2, 2:])
    residual_fraction = np.diag(conditional) / np.diag(cov)[2:]
    if np.any(residual_fraction <= 1e-24):
        raise ValueError('Degenerate residual variation')
    results = []
    for name, (i, j) in zip(PAIR_IDS, PAIR_INDICES):
        r = float(conditional[i, j] / math.sqrt(conditional[i, i] * conditional[j, j]))
        results.append(dict(pair=name, r=r, r_squared=r * r))
    return results


def main():
    if sys.argv[1:] != ['--authorized-after-results']:
        raise SystemExit('Requires explicit parent authorization after completed ANALYSIS.json')
    out_path = HERE / 'INDEPENDENT_RECOMPUTATION.json'
    if out_path.exists():
        raise RuntimeError('Independent audit already closed; no silent repeat')
    freeze = read_json(HERE / 'FREEZE.json')
    assert freeze['independent_review_passed']
    bindings = read_json(HERE / 'INPUT_BINDINGS.json')
    production = read_json(HERE / 'ANALYSIS.json')
    checks = verify_files(bindings, freeze)
    checks.append(('production-freeze', production['freeze_sha256'] == digest(HERE / 'FREEZE.json')))
    prod_by_id = {r['id']: r for r in production['records']}
    with (HERE / 'PAIR_RESULTS.csv').open(encoding='utf-8', newline='') as f:
        csv_rows = list(csv.DictReader(f))
    csv_index = {(r['id'], r['pair']): r for r in csv_rows}
    checks.extend([('bound-table-count', len(bindings['inputs']) == 25),
                   ('production-table-count', len(production['records']) == 25),
                   ('production-unique-ids', len(prod_by_id) == 25),
                   ('production-complete-ids', set(prod_by_id) == {d['id'] for d in bindings['inputs']}),
                   ('csv-slots', len(csv_rows) == len(csv_index) == 75)])
    rebuilt = []
    maximum_error = 0.0
    comparisons = 0
    for d in bindings['inputs']:
        result = {k: d[k] for k in ('id', 'episode', 'seed', 'role', 'sha256')}
        try:
            array, counts = independent_parse(checked_path(d['path']), d['role'] == 'real_reference')
            result['counts'] = counts
            result['analyses'] = covariance_partial_correlations(array)
            result['status'] = 'computed'
        except (ValueError, KeyError, csv.Error) as exc:
            result.update(status='failed', reason=str(exc),
                          analyses=[dict(pair=k, r=None, r_squared=None) for k in PAIR_IDS])
        expected = prod_by_id[d['id']]
        for key in ('episode', 'seed', 'role', 'sha256', 'status', 'counts'):
            checks.append((f'{d["id"]}:{key}', result.get(key) == expected.get(key)))
        checks.append((f'{d["id"]}:pair-order', [r['pair'] for r in expected['analyses']] == PAIR_IDS))
        for actual, old in zip(result['analyses'], expected['analyses']):
            csv_row = csv_index[(d['id'], actual['pair'])]
            checks.extend([(f'{d["id"]}:{actual["pair"]}:csv-status', csv_row['status'] == result['status']),
                           (f'{d["id"]}:{actual["pair"]}:csv-n', csv_row['n'] == str(result.get('counts', {}).get('retained_rows', '')))])
            for field in ('r', 'r_squared'):
                if actual[field] is None:
                    match = old[field] is None and csv_row[field] == ''
                else:
                    error = abs(actual[field] - old[field])
                    maximum_error = max(maximum_error, error)
                    comparisons += 1
                    match = error <= 1e-10 and abs(actual[field] - float(csv_row[field])) <= 1e-10
                checks.append((f'{d["id"]}:{actual["pair"]}:{field}', match))
        rebuilt.append(result)
    checks += verify_files(bindings, freeze)
    failed = [label for label, okay in checks if not okay]
    report = dict(status='pass' if not failed else 'failed',
                  created_utc=datetime.now(timezone.utc).isoformat(),
                  algorithm='Centered covariance Schur complement, independent parser; no production evaluator import',
                  checks=len(checks), failed_checks=failed,
                  tables=len(rebuilt), pair_slots=sum(len(r['analyses']) for r in rebuilt),
                  computed_tables=sum(r['status'] == 'computed' for r in rebuilt),
                  numeric_values_compared=comparisons, maximum_absolute_difference=maximum_error,
                  hashes={name: digest(HERE / name) for name in
                          ['FREEZE.json', 'INPUT_BINDINGS.json', 'ANALYSIS.json', 'PAIR_RESULTS.csv', 'independent_recompute.py']},
                  records=rebuilt, inputs_unchanged=True, row_exports=0,
                  new_generations=0, new_api_calls=0, new_reference_fits=0)
    with out_path.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')
    lines = ['# Independent numerical recomputation', '',
             f"Status: **{report['status']}**. {len(checks)} checks; {len(failed)} failures.", '',
             'All 25 bound tables were parsed independently under the fixed common-case rules. ',
             'The Schur complement of the centered covariance matrix supplies age/sex-adjusted correlations; ',
             'the production OLS residualization function was neither imported nor called.', '',
             f"{report['computed_tables']}/25 tables computed; 75 planned pair slots retained. ",
             f"{comparisons} r/r² values were compared with both JSON and CSV. Maximum absolute difference: {maximum_error:.3g}.", '',
             'All bound hashes remained unchanged. No API, new generation, new target fit, or participant-row export occurred.', '',
             '| Table | n | BMI–TC r | BMI–HDL r | TC–HDL r |',
             '|---|---:|---:|---:|---:|']
    for row in rebuilt:
        vals = ['NA' if a['r'] is None else f"{a['r']:.6f}" for a in row['analyses']]
        lines.append('| ' + ' | '.join([row['id'], str(row.get('counts', {}).get('retained_rows', 'NA'))] + vals) + ' |')
    lines += ['', 'These are developmental, method-guided partial reanalysis results, not original-code reproduction, ',
              'equivalence certification, or independent population confirmation. Seed differences are conditional simulation variation.']
    (HERE / 'INDEPENDENT_RECOMPUTATION.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['status', 'checks', 'failed_checks', 'tables', 'pair_slots', 'computed_tables', 'numeric_values_compared', 'maximum_absolute_difference']}))
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
