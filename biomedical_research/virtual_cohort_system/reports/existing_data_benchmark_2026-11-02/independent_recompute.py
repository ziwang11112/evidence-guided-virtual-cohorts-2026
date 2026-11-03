"""Separate CSV/QR recomputation; never imports a generator or primary evaluator."""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys
import numpy as np


HERE = Path(__file__).resolve().parent
IDS = [f'{arm}_A{i:02d}' for arm in ('E0', 'E1') for i in range(1, 6)]
SEEDS = [1701, 1702, 1703]
MODELS = {'E1': (['age', 'female', 'bmi'], 'bmi'),
          'E2': (['age', 'female', 'glucose'], 'glucose'),
          'E3': (['age', 'female', 'bmi', 'glucose'], 'age')}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    release = read(HERE / 'RELEASE.json')
    root = Path(release['bundle_root'])
    control = root / 'benchmark_control'
    inventory = read(control / 'FINAL_INVENTORY.json')
    report_path = control / 'evaluation/REPORT.json'
    report = read(report_path)
    out = HERE / 'INDEPENDENT_RECOMPUTATION.json'
    if out.exists():
        raise FileExistsError('Independent result already exists; no overwrite')
    checks, failures = [], []

    def check(name, actual, expected, numeric=False):
        ok = (math.isclose(float(actual), float(expected), rel_tol=1e-8, abs_tol=1e-10)
              if numeric else actual == expected)
        checks.append(name)
        if not ok:
            failures.append({'check': name, 'actual': actual, 'expected': expected})

    # An algebraic solver fixture, not a generated biomedical table.
    a = np.array([[1., 0., 0.], [1., 1., 0.], [1., 0., 1.], [1., 2., 3.]])
    q, r = np.linalg.qr(a, mode='reduced')
    fixture = np.linalg.solve(r, q.T @ (a @ np.array([1., 2., 3.])))
    for k, value in enumerate(fixture):
        check(f'QR_fixture_{k}', value, [1., 2., 3.][k], True)
    check('absolute_before_average_fixture', sum(abs(x - 2.) for x in (1., 3.)) / 2., 1., True)

    expected_slots = {(i, s) for i in IDS for s in SEEDS}
    check('inventory_slot_count', len(inventory['slots']), 30)
    check('inventory_slot_identities', sorted((x['constructor'], x['seed']) for x in inventory['slots']), sorted(expected_slots))
    check('report_slot_count', len(report['slots']), 30)
    check('report_slot_identities', sorted((x['constructor'], x['seed']) for x in report['slots']), sorted(expected_slots))
    ref_binding = release['evaluation']['reference_report']
    check('reference_hash', sha(ref_binding['path']), ref_binding['sha256'])
    check('reference_contents', report['reference'], read(ref_binding['path'])['reference'])
    independent_old = release['evaluation']['independent_reference_report']
    check('historical_independent_receipt_hash', sha(independent_old['path']), independent_old['sha256'])
    values = {e: {} for e in MODELS}
    rows_read = 0
    for slot in report['slots']:
        identifier, seed = slot['constructor'], slot['seed']
        key = (identifier, seed)
        inv = next(x for x in inventory['slots'] if (x['constructor'], x['seed']) == key)
        check(f'{key}_execution_status', slot['status'], inv['status'])
        check(f'{key}_sealed_run_id', slot['run_id'], inv['run_id'])
        check(f'{key}_sealed_output_identity', slot['output_sha256'], inv['output_sha256'])
        if slot['status'] != 'success':
            continue
        path = root / identifier / 'executions' / slot['run_id'] / 'output/generated.csv'
        check(f'{key}_output_hash', sha(path), slot['output_sha256'])
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            check(f'{key}_columns', reader.fieldnames, ['row_id', 'age', 'female', 'bmi', 'glucose', 'hba1c'])
            rows = list(reader)
        rows_read += len(rows)
        check(f'{key}_row_count', len(rows), 3000)
        check(f'{key}_unique_ids', len({x['row_id'] for x in rows}), 3000)
        data = {k: np.array([float(x[k]) for x in rows]) for k in ['age', 'female', 'bmi', 'glucose', 'hba1c']}
        for name, arr in data.items():
            check(f'{key}_{name}_finite', bool(np.isfinite(arr).all()), True)
        valid = (all(np.isfinite(x).all() for x in data.values())
                 and ((data['age'] >= 35) & (data['age'] <= 74)).all()
                 and np.isin(data['female'], [0, 1]).all()
                 and (data['bmi'] > 0).all() and (data['glucose'] > 0).all()
                 and (data['hba1c'] > 0).all())
        check(f'{key}_analysis_present', slot['analysis'] is not None, True)
        if slot['analysis'] is None:
            continue
        if not valid:
            check(f'{key}_scientific_gate_withheld', slot['analysis']['status'], 'withheld')
            for endpoint in MODELS:
                check(f'{key}_{endpoint}_unavailable', slot['analysis']['estimands'][endpoint]['status'], 'unavailable')
                check(f'{key}_{endpoint}_no_coefficient', slot['analysis']['estimands'][endpoint]['coefficient'], None)
            continue  # No row deletion or repair of a withheld table.
        for endpoint, (predictors, focal) in MODELS.items():
            design = np.column_stack([np.ones(len(rows))] + [data[k] for k in predictors])
            q, r = np.linalg.qr(design, mode='reduced')
            if np.linalg.matrix_rank(r) < design.shape[1]:
                check(f'{key}_{endpoint}_singular_uncomputed', slot['analysis']['estimands'][endpoint]['status'] != 'computed', True)
                continue
            beta = np.linalg.solve(r, q.T @ data['hba1c'])
            point = float(beta[1 + predictors.index(focal)])
            values[endpoint][key] = point
            claimed = slot['analysis']['estimands'][endpoint]
            check(f'{key}_{endpoint}_computed', claimed['status'], 'computed')
            if claimed['status'] == 'computed':
                check(f'{key}_{endpoint}_coefficient', point, claimed['coefficient'], True)

    computed = {}
    for endpoint in MODELS:
        ref = report['reference']['estimands'][endpoint]
        anchors = {'point': ref['coefficient']}
        if ref['interval']['status'] == 'available':
            anchors.update({k: ref['interval'][k] for k in ('lower', 'upper')})
        computed[endpoint] = {}
        for label, anchor in anchors.items():
            expected = report['endpoints'][endpoint] if label == 'point' else report['endpoints'][endpoint]['reference_interval_endpoint_sensitivity'][label]
            constructor_values, arms = {}, {}
            for identifier in IDS:
                estimates = [values[endpoint].get((identifier, s)) for s in SEEDS]
                mad = sum(abs(v - anchor) for v in estimates) / 3 if all(v is not None for v in estimates) else None
                constructor_values[identifier] = mad
                claimed = next(x for x in expected['constructors'] if x['constructor'] == identifier)
                check(f'{endpoint}_{label}_{identifier}_complete', claimed['complete'], mad is not None)
                check(f'{endpoint}_{label}_{identifier}_MAD', mad, claimed['mean_absolute_discrepancy'], mad is not None and claimed['mean_absolute_discrepancy'] is not None)
            for arm in ('E0', 'E1'):
                group = [constructor_values[i] for i in IDS if i.startswith(arm)]
                arms[arm] = sum(group) / 5 if all(v is not None for v in group) else None
                claimed = expected['arm_mean_absolute_discrepancy'][arm]
                check(f'{endpoint}_{label}_{arm}_MAD', arms[arm], claimed, arms[arm] is not None and claimed is not None)
            delta = arms['E1'] - arms['E0'] if all(v is not None for v in arms.values()) else None
            check(f'{endpoint}_{label}_contrast', delta, expected['E1_minus_E0'], delta is not None and expected['E1_minus_E0'] is not None)
            computed[endpoint][label] = {'arm_MAD': arms, 'E1_minus_E0': delta}
    complete = all(len(values[e]) == 30 for e in MODELS)
    positive = complete and all(computed[e]['point']['E1_minus_E0'] < 0 for e in ('E1', 'E2'))
    check('complete_arms', complete, report['complete_arms_all_three_endpoints'])
    check('prespecified_improvement_statement', positive, report['both_addressed_projections_improve'])
    result = {'status': 'passed' if not failures else 'failed', 'checks': len(checks), 'failures': failures,
              'method': 'Independent csv.DictReader parsing and QR linear solve, not primary analyze or summarize functions.',
              'report_sha256': sha(report_path), 'code_sha256': sha(__file__),
              'generated_rows_read': rows_read, 'patient_rows_read': 0, 'generator_executions': 0,
              'recomputed_endpoint_coefficients': sum(len(x) for x in values.values()),
              'summary': computed, 'complete_arms': complete, 'both_addressed_projections_improve': positive,
              'scope': 'Three prespecified coefficient estimates and their arm/interval-endpoint arithmetic; historical clinical-reference uncertainty is reused, not re-estimated.'}
    with out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'checks', 'failures', 'recomputed_endpoint_coefficients')}))
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
