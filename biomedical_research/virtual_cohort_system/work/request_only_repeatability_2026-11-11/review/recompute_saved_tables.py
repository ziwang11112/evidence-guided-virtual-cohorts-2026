"""Independent saved-row audit. No production-estimator imports or generator runs.

Prepare/import is read-free. Run --closed-batch only after root confirms all twelve
authors and final evaluation are closed. --self-test uses algebraic fixtures only.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import json
import math
import numpy as np

UNIT = Path(__file__).resolve().parents[1]
PROJECT = UNIT.parents[1]
REFERENCE = PROJECT / 'work/cross_model_api_pilot_2026-11-10/_host_only/REFERENCE_SNAPSHOT.json'
ATOL, RTOL = 1e-9, 1e-10
ENDPOINTS = {
    'PNS': ['bmi_sbp', 'bmi_dbp', 'residual_correlation', 'sbp.sd_population', 'dbp.sd_population', 'sbp_below_dbp_fraction'],
    'lipids': ['K02-HDL-BMI', 'K02-TC-BMI', 'K02-LIPID-RESIDUAL', 'total_cholesterol.sd_sample', 'hdl_cholesterol.sd_sample', 'hdl_above_total_fraction'],
}


def read(path):
    def reject(value):
        raise ValueError('Nonfinite JSON token: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=reject)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def within(relative):
    path = (UNIT / relative).resolve()
    if not path.is_relative_to(UNIT.resolve()):
        raise ValueError('Saved path leaves pilot unit')
    return path


def load_table(path, task):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        expected = [c['name'] for c in task['columns']]
        if reader.fieldnames != expected:
            raise ValueError('CSV schema/order differs from task')
        rows = list(reader)
    if len(rows) != task['n_rows']:
        raise ValueError('CSV row count differs from task')
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError('Malformed CSV width')
    ids = [row[task['row_id']] for row in rows]
    if not all(ids) or len(set(ids)) != len(ids):
        raise ValueError('Empty/duplicate row identifiers')
    data = {}
    for c in task['columns']:
        key = c['name']
        if key == task['row_id']:
            continue
        if key == 'sex':
            data[key] = np.array([row[key] for row in rows])
            if not np.isin(data[key], ['F', 'M']).all():
                raise ValueError('Unknown sex category')
        else:
            data[key] = np.array([float(row[key]) for row in rows], dtype=float)
            if not np.isfinite(data[key]).all():
                raise ValueError('Nonfinite numerical column: ' + key)
            if 'minimum' in c and not (data[key] >= c['minimum']).all():
                raise ValueError('Column below declared eligibility: ' + key)
            if 'maximum' in c and not (data[key] <= c['maximum']).all():
                raise ValueError('Column above declared eligibility: ' + key)
            if 'categories' in c and not np.isin(data[key], c['categories']).all():
                raise ValueError('Unknown category: ' + key)
    if 'sex' in data and any(not (data[k] > 0).all() for k in ['bmi', 'total_cholesterol', 'hdl_cholesterol']):
        raise ValueError('Nonpositive lipid-case output; no row filtering permitted')
    return data, rows


def independent_statistics(data, case):
    """QR least squares, independent of production weighted-lstsq/SVD adapters."""
    n = len(data['age'])
    female = data['female'] if case == 'PNS' else (data['sex'] == 'F').astype(float)
    x = np.column_stack([np.ones(n), (data['age'] - 50) / 10, female, (data['bmi'] - 25) / 5])
    rank = int(np.linalg.matrix_rank(x))
    names = ['sbp', 'dbp'] if case == 'PNS' else ['total_cholesterol', 'hdl_cholesterol']
    y = np.column_stack([data[k] for k in names]) * (1 if case == 'PNS' else 38.67)
    values = {k: None for k in ENDPOINTS[case]}
    if case == 'PNS':
        values.update({'sbp.sd_population': float(np.std(y[:, 0], ddof=0)),
            'dbp.sd_population': float(np.std(y[:, 1], ddof=0)),
            'sbp_below_dbp_fraction': float(np.mean(data['sbp'] < data['dbp']))})
        violations = int(np.sum(data['sbp'] < data['dbp']))
    else:
        values.update({'total_cholesterol.sd_sample': float(np.std(y[:, 0], ddof=1)),
            'hdl_cholesterol.sd_sample': float(np.std(y[:, 1], ddof=1)),
            'hdl_above_total_fraction': float(np.mean(data['hdl_cholesterol'] > data['total_cholesterol']))})
        violations = int(np.sum(data['hdl_cholesterol'] > data['total_cholesterol']))
    if rank == 4:
        q, r = np.linalg.qr(x, mode='reduced')
        coefficients = np.linalg.solve(r, q.T @ y)
        residual = y - x @ coefficients
        if case == 'PNS':
            values.update(bmi_sbp=float(coefficients[3, 0]), bmi_dbp=float(coefficients[3, 1]))
            centered = residual - residual.mean(axis=0)
            rvar = np.mean(centered ** 2, axis=0)
            threshold = np.finfo(float).eps * max(float(np.var(y[:, 0])), float(np.var(y[:, 1])), 1.) * 100
            usable = bool(min(rvar) > threshold)
        else:
            usable_columns = []
            for j, key in enumerate(['K02-TC-BMI', 'K02-HDL-BMI']):
                if np.ptp(y[:, j]) != 0:
                    values[key] = float(coefficients[3, j])
                cutoff = 16 * np.finfo(float).eps * max(x.shape) * max(float(np.linalg.norm(y[:, j])), np.finfo(float).tiny)
                usable_columns.append(np.ptp(y[:, j]) != 0 and float(np.linalg.norm(residual[:, j])) > cutoff)
            usable = all(usable_columns)
        if usable:
            centered = residual - residual.mean(axis=0)
            correlation = float(np.dot(centered[:, 0], centered[:, 1]) / (np.linalg.norm(centered[:, 0]) * np.linalg.norm(centered[:, 1])))
            values['residual_correlation' if case == 'PNS' else 'K02-LIPID-RESIDUAL'] = float(np.clip(correlation, -1, 1))
    marginals = {}
    for name, column in data.items():
        if name == 'sex':
            continue
        marginals[name] = {'mean': float(np.mean(column)), 'sd_sample': float(np.std(column, ddof=1)),
            'min': float(np.min(column)), 'max': float(np.max(column)),
            'quantiles': {str(q): float(np.quantile(column, q)) for q in [.01, .25, .5, .75, .99]}}
    return {'values': values, 'marginals': marginals, 'design_rank': rank, 'component_violation_count': violations, 'n': n}


class Auditor:
    def __init__(self):
        self.blockers, self.checks, self.differences, self.hashes = [], 0, [], {}

    def same(self, label, actual, expected):
        self.checks += 1
        if actual != expected:
            self.blockers.append({'check': label, 'actual': actual, 'expected': expected})

    def number(self, label, actual, expected):
        self.checks += 1
        if actual is None or expected is None:
            if actual is not None or expected is not None:
                self.blockers.append({'check': label, 'actual': actual, 'expected': expected})
        elif not isinstance(actual, (int, float)) or not math.isfinite(actual) or not math.isfinite(expected):
            self.blockers.append({'check': label, 'reason': 'Nonfinite/non-numeric value'})
        else:
            diff = abs(actual - expected)
            self.differences.append(diff)
            if diff > ATOL + RTOL * abs(expected):
                self.blockers.append({'check': label, 'actual': actual, 'expected': expected, 'absolute_difference': diff})

    def file(self, path):
        path = Path(path)
        self.hashes[str(path.resolve()).replace('\\', '/')] = sha(path)
        return self.hashes[str(path.resolve()).replace('\\', '/')]


def audit_closed_batch():
    audit = Auditor()
    required = ['PLAN.json', 'LAUNCH_FREEZE.json', 'CONSTRUCTION_CLOSURE.json', 'FINAL_TABLES.json', 'EVALUATION.json']
    for name in required:
        if not (UNIT / name).is_file():
            raise ValueError('Closed-batch artifact missing: ' + name)
        audit.file(UNIT / name)
    plan, freeze, closure, final, evaluation = [read(UNIT / name) for name in required]
    planned = {e['episode_id']: e for e in plan['episodes']}
    assert len(planned) == 12 and len(closure['episodes']) == 12
    assert closure['all_episodes_closed'] and {r['episode_id'] for r in closure['episodes']} == set(planned)
    assert closure['plan_sha256'] == sha(UNIT / 'PLAN.json')
    assert final['construction_closure_sha256'] == sha(UNIT / 'CONSTRUCTION_CLOSURE.json')
    assert evaluation['final_tables_sha256'] == sha(UNIT / 'FINAL_TABLES.json')
    for name, digest in freeze['files'].items():
        assert audit.file(within(name)) == digest, 'Launch-frozen input changed: ' + name
    for name, digest in freeze.get('external_files', {}).items():
        assert audit.file(Path(name)) == digest, 'Frozen external code changed'
    outcomes = []
    for row in closure['episodes']:
        folder = UNIT / 'episodes' / row['episode_id']
        inventory = {f.relative_to(folder).as_posix(): audit.file(f) for f in sorted(folder.rglob('*'))
            if f.is_file() and f.relative_to(folder).parts[0] != 'evaluations'}
        assert inventory == row['files'], 'Closed author artifact changed: ' + row['episode_id']
        outcome = read(folder / 'OUTCOME.json')
        assert outcome['selected_candidate'] == row['candidate_id']
        assert outcome['status'] == row['outcome_status']
        outcomes.append(outcome)
    expected_slots = {(e, s) for e in planned for s in plan['evaluation_seeds']}
    slots = final['slots']
    assert len(slots) == len(expected_slots) == 36
    assert {(r['episode_id'], r['seed']) for r in slots} == expected_slots
    audit.same('Evaluation slots equal closed final slots', evaluation['slots'], slots)
    # No final row or reference read precedes the complete closure/freeze checks above.
    results, success_hashes = {}, []
    for slot in slots:
        identity = (slot['episode_id'], slot['seed'])
        label = f'{identity[0]}/{identity[1]}'
        ep = planned[identity[0]]
        closed = next(r for r in closure['episodes'] if r['episode_id'] == identity[0])
        audit.same(label + '/case', slot['case_id'], ep['case_id'])
        audit.same(label + '/arm', slot['arm'], ep['arm'])
        audit.same(label + '/candidate', slot['candidate_id'], closed['candidate_id'])
        if slot['status'] != 'success':
            if slot['status'] not in {'failed', 'unavailable'}:
                audit.blockers.append({'check': label, 'reason': 'Unknown slot status'})
            results[identity] = {'status': slot['status'], 'values': {k: None for k in ENDPOINTS[ep['case_id']]}}
            continue
        try:
            canonical = Path('episodes') / identity[0] / 'evaluations' / ('seed_' + str(identity[1]))
            assert Path(slot['generated_path']) == canonical / 'output/generated.csv'
            assert Path(slot['receipt_path']) == canonical / 'execution.json'
            table, receipt_path = within(slot['generated_path']), within(slot['receipt_path'])
            digest = audit.file(table)
            audit.same(label + '/CSV hash', digest, slot['generated_sha256'])
            audit.same(label + '/receipt hash', audit.file(receipt_path), slot['receipt_sha256'])
            receipt = read(receipt_path)
            audit.same(label + '/receipt candidate', receipt['candidate_id'], slot['candidate_id'])
            audit.same(label + '/receipt seed', receipt['seed'], identity[1])
            audit.same(label + '/receipt statistics', receipt['statistics'], slot['statistics'])
            task = read(within(ep['task_path']))
            data, rows = load_table(table, task)
            computed = independent_statistics(data, ep['case_id'])
            actual = {v['id']: v for category in ['analyses', 'diagnostics'] for v in slot['statistics'][category]}
            audit.same(label + '/endpoint inventory', sorted(actual), sorted(computed['values']))
            for key, value in computed['values'].items():
                audit.number(label + '/' + key, actual[key]['value'], value)
                audit.same(label + '/' + key + '/status', actual[key]['status'], 'computed' if value is not None else 'unavailable')
            for key in ['design_rank', 'component_violation_count', 'n']:
                audit.same(label + '/quality/' + key, slot['statistics']['quality'][key], computed[key])
            fields = [c['name'] for c in task['columns'] if c['name'] != task['row_id']]
            unique_measurements = {tuple(row[f] for f in fields) for row in rows}
            audit.same(label + '/duplicate measurement rows', slot['statistics']['quality']['duplicate_measurement_rows'], len(rows) - len(unique_measurements))
            for name, margin in computed['marginals'].items():
                reported = slot['statistics']['marginals_delivered_units'][name]
                for key in ['mean', 'sd_sample', 'min', 'max']:
                    audit.number(label + '/marginal/' + name + '/' + key, reported[key], margin[key])
                for q, value in margin['quantiles'].items():
                    audit.number(label + '/quantile/' + name + '/' + q, reported['quantiles'][q], value)
            results[identity] = {'status': 'success', **computed, 'generated_sha256': digest}
            success_hashes.append(digest)
        except Exception as error:
            audit.blockers.append({'check': label, 'reason': type(error).__name__ + ': ' + str(error)})
            results[identity] = {'status': slot['status'], 'values': {k: None for k in ENDPOINTS[ep['case_id']]}}
    assert audit.file(REFERENCE) == evaluation['reference_snapshot_sha256']
    references = read(REFERENCE)['references']  # Existing aggregate only; no patient record access or refit.
    expected_summary_ids = {(e, k) for e, ep in planned.items() for k in ENDPOINTS[ep['case_id']]}
    summaries = evaluation['summaries']
    audit.same('Summary inventory', sorted((s['episode_id'], s['analysis_id']) for s in summaries), sorted(expected_summary_ids))
    for summary in summaries:
        episode, key = summary['episode_id'], summary['analysis_id']
        case = planned[episode]['case_id']
        ref = references[case][key]
        audit.same(episode + '/' + key + '/reference object', summary['reference'], ref)
        values = [results[(episode, seed)]['values'][key] for seed in plan['evaluation_seeds']]
        available = [v for v in values if v is not None]
        audit.same(episode + '/' + key + '/n', summary['available_seeds'], len(available))
        for key2, expected in [('mean', float(np.mean(available)) if available else None),
            ('minimum', min(available) if available else None), ('maximum', max(available) if available else None),
            ('mean_absolute_reference_difference', float(np.mean([abs(v - ref['value']) for v in available])) if available and ref['value'] is not None else None)]:
            audit.number(episode + '/' + key + '/' + key2, summary[key2], expected)
        for index, row in enumerate(summary['values']):
            seed = plan['evaluation_seeds'][index]
            audit.same(episode + '/' + key + '/seed', row['seed'], seed)
            audit.same(episode + '/' + key + '/seed status', row['status'], results[(episode, seed)]['status'])
            audit.number(episode + '/' + key + '/seed value', row['value'], values[index])
    expected_counts = {'episodes': 12, 'cases': 2, 'final_slots': 36,
        'successful_tables': sum(s['status'] == 'success' for s in slots),
        'failed_tables': sum(s['status'] == 'failed' for s in slots),
        'unavailable_tables': sum(s['status'] == 'unavailable' for s in slots)}
    for key, value in expected_counts.items():
        audit.same('Counts/' + key, evaluation['counts'][key], value)
    audit.same('Counts/model calls', evaluation['counts']['model_calls'], sum(o['calls_reserved'] for o in outcomes))
    audit.number('Costs/known usage total', evaluation['costs']['known_tariff_usd'], sum(o['known_tariff_cost_usd'] for o in outcomes))
    audit.number('Costs/accounted total', evaluation['costs']['accounted_usd'], sum(o['accounted_usd'] for o in outcomes))
    return {'status': 'pass' if not audit.blockers else 'blocked', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Independent QR regression/residual, endpoint, marginal and summary recomputation from successful saved final tables',
        'counts': {**expected_counts, 'recomputed_tables': len(success_hashes), 'unique_csv_hashes': len(set(success_hashes))},
        'checks': audit.checks, 'numerical_comparisons': len(audit.differences),
        'max_absolute_difference': max(audit.differences, default=0.), 'absolute_tolerance': ATOL, 'relative_tolerance': RTOL,
        'blockers': audit.blockers, 'artifact_hashes': audit.hashes, 'review_script_sha256': sha(Path(__file__)),
        'per_slot': [{'episode_id': e, 'seed': seed, **value} for (e, seed), value in results.items()],
        'no_generator_reexecution': True, 'no_production_estimator_imports': True, 'no_patient_access_or_refits': True,
        'no_model_calls_or_credentials': True, 'reference_role': 'Previously exposed aggregate comparison, not population truth'}


def self_test():
    # Orthogonal numerical fixture, not an author generator or biomedical calibration.
    rng = np.random.default_rng(917)
    n = 64
    age = np.linspace(20, 79, n)
    female = np.tile([0., 1.], n // 2)
    bmi = 25 + rng.normal(size=n)
    x = np.column_stack([np.ones(n), (age - 50) / 10, female, (bmi - 25) / 5])
    q = np.linalg.qr(x)[0]
    noise = rng.normal(size=(n, 2))
    noise -= q @ (q.T @ noise)
    z = np.linalg.qr(noise)[0] * 5
    y = x @ np.array([[120., 80.], [2., 1.], [1., -1.], [3., 2.]]) + np.column_stack([z[:, 0], .4 * z[:, 0] + math.sqrt(.84) * z[:, 1]])
    data = {'age': age, 'female': female, 'bmi': bmi, 'sbp': y[:, 0], 'dbp': y[:, 1]}
    result = independent_statistics(data, 'PNS')['values']
    assert abs(result['bmi_sbp'] - 3) < 1e-10 and abs(result['bmi_dbp'] - 2) < 1e-10
    assert abs(result['residual_correlation'] - .4) < 1e-10
    lipid = {'age': age, 'sex': np.where(female == 1, 'F', 'M'), 'bmi': bmi,
        'total_cholesterol': y[:, 0] / 38.67, 'hdl_cholesterol': y[:, 1] / 38.67}
    result2 = independent_statistics(lipid, 'lipids')['values']
    assert abs(result2['K02-TC-BMI'] - 3) < 1e-10 and abs(result2['K02-HDL-BMI'] - 2) < 1e-10
    assert abs(result2['K02-LIPID-RESIDUAL'] - .4) < 1e-10
    return {'status': 'pass', 'fixtures': 2, 'final_rows_read': False, 'reference_read': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--self-test', action='store_true')
    action.add_argument('--closed-batch', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test()))
    else:
        result = audit_closed_batch()
        destination = Path(__file__).with_name('INDEPENDENT_RECOMPUTATION.json')
        with destination.open('x', encoding='utf-8', newline='\n') as out:
            json.dump(result, out, indent=2, ensure_ascii=False, allow_nan=False)
            out.write('\n')
        print(json.dumps({k: result[k] for k in ['status', 'counts', 'checks', 'max_absolute_difference', 'blockers']}))
