"""Independent v2 arithmetic for main-study outputs, after global closure.

Does not import either case provider, the original clinical analysis engines or
the main evaluator. Original clinical-reference arithmetic has earlier audits;
here its frozen aggregate mapping is separately checked, not new patient data.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import numpy as np
import pandas as pd

UNIT = Path(__file__).resolve().parents[1]
PROJECT = UNIT.parents[1]
sys.path.insert(0, str(UNIT / "implementation"))
import main_session_v1 as control

VARIABLES = ["age", "female", "bmi", "glucose", "hba1c"]


def qr_fit(x, y, weights):
    sw = np.sqrt(weights)
    design = x * sw[:, None]
    if np.linalg.matrix_rank(design) != design.shape[1]:
        return None, None
    q, r = np.linalg.qr(design, mode="reduced")
    beta = np.linalg.solve(r, q.T @ (y * sw))
    if not np.isfinite(beta).all():
        return None, None
    residual = y - x @ beta
    return beta, float(np.sqrt(np.sum(weights * residual**2) / np.sum(weights)))


def inverse_weighted_quantile(values, weights, probability):
    # Retain original row weights and stable value order. Recover the exact
    # rounding residual of each addition with fsum, then accumulate those
    # residuals separately. This is independent error-recovery code for the
    # pinned compensated-prefix convention, not normalized naive cumsum.
    values, weights = np.asarray(values, dtype=float), np.asarray(weights, dtype=float)
    if values.ndim != 1 or weights.shape != values.shape or not len(values):
        raise ValueError("Quantiles need nonempty equal-length vectors")
    if not np.isfinite(values).all() or not np.isfinite(weights).all():
        raise ValueError("Quantile operands must be finite")
    if np.any(weights < 0) or not np.any(weights > 0) or not 0 <= probability <= 1:
        raise ValueError("Invalid quantile masses or probability")
    keep = weights > 0
    values, weights = values[keep], weights[keep]
    order = np.argsort(values, kind="stable")
    ordered = values[order]
    prefixes = []
    total = lost = 0.0
    for mass in weights[order]:
        mass = float(mass)
        updated = total + mass
        lost += math.fsum((total, mass, -updated))
        total = updated
        prefixes.append(total + lost)
    if not math.isfinite(prefixes[-1]):
        raise ValueError("Nonfinite quantile mass")
    threshold = probability * prefixes[-1]
    index = np.searchsorted(prefixes, threshold, side="left")
    return float(ordered[min(int(index), len(ordered)-1)])


def calculate(frame, case, *, enforce_task=True):
    data = frame[VARIABLES].to_numpy(dtype=float)
    if not np.isfinite(data).all() or (enforce_task and len(data) != 3000):
        return None
    a, f, b, g, h = data.T
    if np.any((f != 0) & (f != 1)) or np.any(np.floor(a) != a) or np.any(data[:, 2:] <= 0):
        return None
    values = {}
    if case == "CHNS2009":
        if np.any(a < 35) or np.any(a > 74):
            return None
        designs = [("E1", [a, f, b], 3), ("E2", [a, f, g], 3), ("E3", [f, b, g, a], 4)]
        for ident, predictors, index in designs:
            beta, _ = qr_fit(np.column_stack([np.ones(len(a)), *predictors]), h, np.ones(len(a)))
            values[ident] = None if beta is None else float(beta[index])
        for name, column in zip(VARIABLES, data.T):
            for stat, value in {"mean": np.mean(column), "sd": np.std(column, ddof=1),
                                "q10": np.quantile(column, .1, method="linear"),
                                "median": np.quantile(column, .5, method="linear"),
                                "q90": np.quantile(column, .9, method="linear")}.items():
                values[name + "_" + stat] = float(value)
        for name, left, right in [("pearson", g, h), ("spearman", pd.Series(g).rank(method="average").to_numpy(), pd.Series(h).rank(method="average").to_numpy())]:
            left, right = left-left.mean(), right-right.mean()
            denominator = np.linalg.norm(left) * np.linalg.norm(right)
            values["glucose_hba1c_" + name] = float(left @ right / denominator) if denominator > 0 else None
    elif case == "ENSANUT2018":
        if np.any(a < 25) or np.any(a > 79) or np.any(g >= 126):
            return None
        bands = np.searchsorted([40, 55, 70], a, side="right")
        cell = 2 * bands + f.astype(int)
        counts = np.bincount(cell, minlength=8)
        if np.any(counts == 0) or (enforce_task and np.any(counts != 375)):
            return None
        weights = 1.0 / (8 * counts[cell])
        design = np.column_stack([np.ones(len(a)), (a-50)/10, f, (b-25)/5, (g-100)/10])
        full, rms = qr_fit(design, h, weights)
        reduced, _ = qr_fit(design[:, :4], h, weights)
        glucose, _ = qr_fit(design[:, [0, 1, 2, 4]], h, weights)
        if any(x is None for x in (full, reduced, glucose)):
            return None
        values.update(Q1_age10=float(full[1]), Q2_bmi5=float(reduced[3]), Q3_bmi5=float(full[3]),
                      Q2_minus_Q3_bmi5=float(reduced[3]-full[3]), glucose10_age_sex=float(glucose[3]), q1_residual_rms=rms)
        for name, column in zip(VARIABLES, data.T):
            avg = float(np.sum(weights*column) / weights.sum())
            values[name+".mean"] = avg
            values[name+".sd_population"] = float(np.sqrt(np.sum(weights*(column-avg)**2) / weights.sum()))
            for label, probability in (("q10", .1), ("q50", .5), ("q90", .9)):
                values[name+"."+label] = inverse_weighted_quantile(column, weights, probability)
    else:
        raise ValueError("Unknown case")
    return values


def close(a, b):
    if a is None or b is None:
        return a is None and b is None
    return bool(np.isclose(a, b, rtol=1e-9, atol=1e-9))


def lookup(document, keys):
    for key in keys:
        if not isinstance(document, dict) or key not in document:
            return None
        document = document[key]
    return document


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def sign(value):
    return None if value is None else ('positive' if value > 0 else 'negative' if value < 0 else 'zero')


def average(values):
    return math.fsum(values) / len(values) if values else None


def quantile_id(case, ident):
    return ident.endswith(('_q10', '_median', '_q90')) if case == 'CHNS2009' else ident.endswith(('.q10', '.q50', '.q90'))


def independent_summaries(identities, ledger_slots, endpoint_rows, bindings):
    """Aggregate trusted effective values, independently of primary summaries.

    Values remain unavailable after a recorded provider failure even when this
    audit can compute a separate diagnostic value. No replacement is made.
    """
    summaries = []
    for identity in sorted(identities, key=lambda x: x['constructor_id']):
        cid = identity['constructor_id']
        slots = sorted((x for x in ledger_slots if x['constructor_id'] == cid), key=lambda x: x['seed'])
        endpoints = []
        for definition in bindings['cases'][identity['case_id']]['analyses']:
            rows = [endpoint_rows[(cid, s['seed'])][definition['id']] for s in slots]
            values = [r['value'] for r in rows if r['value'] is not None]
            deviations = [r['absolute_discrepancy'] for r in rows if r['absolute_discrepancy'] is not None]
            complete = len(deviations) == 3
            endpoints.append({
                'id': definition['id'], 'unit': definition['unit'], 'scheduled_seeds': 3,
                'available_values': len(values), 'available_discrepancies': len(deviations),
                'complete': complete, 'mean_absolute_discrepancy': average(deviations) if complete else None,
                'available_value_mean_absolute_discrepancy': average(deviations),
                'mean_effect': average(values), 'seed_effect_range': [min(values), max(values)] if values else None,
                'seed_directions': [sign(r['value']) for r in rows],
                'summary_status': 'complete' if complete else 'incomplete_available_values_only',
            })
        summaries.append({**identity, 'scheduled_final_slots': 3,
            'successful_executions': sum(s['execution_status'] == 'success' for s in slots),
            'complete_analysis_slots': sum(endpoint_rows[(cid, s['seed'])]['__analysis_status__'] == 'complete' for s in slots),
            'endpoints': endpoints})
    contrasts = []
    for case, definitions in bindings['cases'].items():
        for endpoint in definitions['analyses']:
            arms = {}
            for arm in ['E0', 'E1']:
                people = [x for x in summaries if x['case_id'] == case and x['information_condition'] == arm and x['constructor_kind'] == 'agent']
                details = [next(r for r in x['endpoints'] if r['id'] == endpoint['id']) for x in people]
                available = [r['available_value_mean_absolute_discrepancy'] for r in details if r['available_value_mean_absolute_discrepancy'] is not None]
                complete = len(people) == 5 and all(r['complete'] for r in details)
                arms[arm] = {'scheduled_constructors': 5, 'represented_constructors': len(people),
                    'constructors_with_complete_endpoint': sum(r['complete'] for r in details),
                    'constructors_with_any_discrepancy': len(available), 'complete': complete,
                    'mean_constructor_mean_absolute_discrepancy': average(available) if complete else None,
                    'incomplete_available_value_mean': average(available) if available and not complete else None,
                    'available_value_mean': average(available)}
            complete = all(x['complete'] for x in arms.values())
            a, b = arms['E1']['available_value_mean'], arms['E0']['available_value_mean']
            difference = a-b if a is not None and b is not None else None
            contrasts.append({'case_id': case, 'endpoint': endpoint['id'], 'unit': endpoint['unit'], 'arms': arms,
                'status': 'complete_descriptive_comparison' if complete else 'incomplete_no_complete_arm_advantage_claim',
                'E1_minus_E0_mean_absolute_discrepancy': difference if complete else None,
                'incomplete_available_value_contrast': difference if not complete else None,
                'complete_arm_comparison_available': complete,
                'interpretation': 'Added supplied-information descriptive contrast; no equivalence or isolated algorithmic superiority inference.'})
    return summaries, contrasts


def review_report(report, identities, ledger_slots, calculations, references, bindings):
    """Pure report audit. Arguments may be invented fixtures; no filesystem I/O.

    ledger_slots and calculations must come from verified session events/output
    bytes in production, never from the report's claimed execution status.
    """
    errors, provider_failures, checks = [], [], 0
    effective = {}
    def issue(kind, location, detail):
        errors.append({'kind': kind, 'location': location, 'detail': detail})
    def compare(expected, actual, location, *, exact=False):
        nonlocal checks
        checks += 1
        if isinstance(expected, dict):
            if not isinstance(actual, dict) or set(expected) != set(actual):
                issue('structure', location, 'Object keys differ')
                return
            for key in expected:
                compare(expected[key], actual[key], location+'/'+str(key), exact=exact)
        elif isinstance(expected, list):
            if not isinstance(actual, list) or len(actual) != len(expected):
                issue('structure', location, 'List length/type differs')
                return
            for i, (left, right) in enumerate(zip(expected, actual)):
                compare(left, right, location+'/'+str(i), exact=exact)
        elif expected is None or isinstance(expected, (bool, str, int)):
            if type(expected) is not type(actual) or expected != actual:
                issue('value', location, {'expected': expected, 'actual': actual})
        elif not finite(actual) or (expected != actual if exact else not close(expected, actual)):
            issue('value', location, {'expected': expected, 'actual': actual, 'exact': exact})

    def indexed(rows, key, expected_keys, location):
        nonlocal checks
        checks += 1
        if not isinstance(rows, list):
            issue('inventory', location, 'Expected a list')
            return {}
        result = {}
        try:
            for row in rows:
                ident = key(row)
                if ident in result:
                    issue('inventory', location, 'Duplicate identity: '+str(ident))
                result[ident] = row
        except (KeyError, TypeError) as exc:
            issue('inventory', location, type(exc).__name__)
        if set(result) != set(expected_keys):
            issue('inventory', location, {'missing': sorted(map(str,set(expected_keys)-set(result))), 'extra': sorted(map(str,set(result)-set(expected_keys)))})
        return result

    expected_keys = {(x['constructor_id'], x['seed']) for x in ledger_slots}
    required_keys = {(x['constructor_id'], seed) for x in identities for seed in (5101,5102,5103)}
    if len(identities) != 24 or len(required_keys) != 72 or len(ledger_slots) != 72 or expected_keys != required_keys:
        raise ValueError('Trusted inventory must contain exactly 24 constructors and 72 prescribed slots')
    declared = indexed(report.get('all_scheduled_slots'), lambda x:(x['constructor_id'],x['seed']), required_keys, 'all_scheduled_slots')
    numeric = 0
    max_difference = 0.0
    for ledger in ledger_slots:
        key = ledger['constructor_id'], ledger['seed']
        location = str(key)
        slot = declared.get(key)
        if slot is None:
            continue
        for field in ('constructor_id','case_id','information_condition','constructor_kind','seed','scheduled','closure_status','candidate','run_id','execution_status','output_sha256'):
            compare(ledger[field], slot.get(field), location+'/'+field)
        case = ledger['case_id']
        spec = bindings['cases'][case]
        independent = calculations.get(key, {}).get('values')
        calculation_error = calculations.get(key, {}).get('error')
        provider_failed = ledger['execution_status'] == 'success' and slot.get('analysis_status') == 'provider_error'
        if provider_failed:
            if not isinstance(slot.get('error'), dict) or not slot['error'].get('type') or not slot['error'].get('message'):
                issue('failure_record', location, 'provider_error requires a retained typed error')
            provider_failures.append({'constructor_id':key[0], 'seed':key[1],
                'classification':'preserved_primary_provider_failure',
                'independently_computable': independent is not None,
                'independent_calculation_error':calculation_error,
                'primary_values_validated':False, 'primary_failure_reproduced':False})
        elif calculation_error and ledger['execution_status'] == 'success':
            issue('independent_calculation_error', location, calculation_error)
        if ledger['execution_status'] != 'success' and not isinstance(slot.get('error'), dict):
            issue('failure_record', location, 'Unattempted/failed execution needs a retained error')
        if ledger['execution_status'] != 'success' and ledger.get('expected_error') is not None:
            compare(ledger['expected_error'],slot.get('error'),location+'/error')
        if ledger['execution_status'] != 'success' or provider_failed:
            compare(None,slot.get('quality'),location+'/quality')
            compare(None,slot.get('n'),location+'/n')
        values = None if provider_failed or ledger['execution_status'] != 'success' else independent
        rows_for_summary = {}
        complete = True
        for category in ('analyses','diagnostics'):
            definitions = {x['id']:x for x in spec[category]}
            rows = indexed(slot.get(category), lambda x:x['id'], definitions, location+'/'+category)
            for ident, definition in definitions.items():
                value = values.get(ident) if values is not None else None
                if value is not None and not finite(value):
                    issue('independent_nonfinite', location+'/'+ident, str(value))
                    value = None
                status = 'computed' if value is not None else 'unavailable'
                complete = complete and status == 'computed'
                ref = references[case][ident]
                deviation = value-ref if value is not None and ref is not None else None
                rows_for_summary[ident] = {'value':value, 'absolute_discrepancy':abs(deviation) if deviation is not None else None}
                row = rows.get(ident)
                if row is None:
                    continue
                compare(definition['unit'], row.get('unit'), location+'/'+ident+'/unit')
                compare(status, row.get('status'), location+'/'+ident+'/status')
                compare(value, row.get('value'), location+'/'+ident+'/value', exact=quantile_id(case,ident))
                compare(ref, row.get('reference_value'), location+'/'+ident+'/reference_value', exact=True)
                compare(sign(value), row.get('generated_direction'), location+'/'+ident+'/generated_direction')
                compare(sign(ref), row.get('reference_direction'), location+'/'+ident+'/reference_direction')
                compare(deviation, row.get('signed_discrepancy'), location+'/'+ident+'/signed_discrepancy')
                compare(abs(deviation) if deviation is not None else None, row.get('absolute_discrepancy'), location+'/'+ident+'/absolute_discrepancy')
                compare('computed' if deviation is not None else 'unavailable', row.get('comparison_status'), location+'/'+ident+'/comparison_status')
                if value is not None and finite(row.get('value')):
                    numeric += 1
                    max_difference = max(max_difference,abs(value-row['value']))
                if status == 'unavailable' and not row.get('reason'):
                    issue('failure_record', location+'/'+ident, 'Unavailable endpoint lacks reason')
        analysis_status = 'provider_error' if provider_failed else ('complete' if complete else 'incomplete') if ledger['execution_status']=='success' else 'unavailable'
        compare(analysis_status, slot.get('analysis_status'), location+'/analysis_status')
        rows_for_summary['__analysis_status__'] = analysis_status
        effective[key] = rows_for_summary

    required_contrasts = {(case, r['id']) for case, spec in bindings['cases'].items() for r in spec['analyses']}
    if len(required_contrasts) != 6:
        raise ValueError('Expected six prescribed case/endpoint contrasts')
    actual_contrasts = indexed(report.get('agent_information_contrasts'), lambda x:(x['case_id'],x['endpoint']), required_contrasts, 'agent_information_contrasts')
    actual_summaries = indexed(report.get('construction_summaries'),lambda x:x['constructor_id'],{x['constructor_id'] for x in identities},'construction_summaries')
    # Missing endpoint/slot structures already fail; do not invent summaries.
    if set(effective) == required_keys:
        expected_summaries, expected_contrasts = independent_summaries(identities,ledger_slots,effective,bindings)
        for row in expected_summaries:
            if row['constructor_id'] in actual_summaries:
                compare(row, actual_summaries[row['constructor_id']], 'construction_summaries/'+row['constructor_id'])
        for row in expected_contrasts:
            key = row['case_id'],row['endpoint']
            if key in actual_contrasts:
                compare(row,actual_contrasts[key],'agent_information_contrasts/'+str(key))
        statistical = [x for x in expected_summaries if x['constructor_kind']=='statistical']
        compare(statistical, report.get('statistical_references'),'statistical_references')
    compare(24,report.get('planned_constructions'),'planned_constructions')
    compare(72,report.get('scheduled_final_slots'),'scheduled_final_slots')
    compare(sum(x['execution_status']=='success' for x in ledger_slots),report.get('successful_executions'),'successful_executions')
    compare(sum(x['__analysis_status__']=='complete' for x in effective.values()),report.get('complete_analysis_slots'),'complete_analysis_slots')
    compare(len({x['output_sha256'] for x in ledger_slots if x['output_sha256']}),report.get('unique_successful_table_contents'),'unique_successful_table_contents')
    unavailable_slots = [x for x in ledger_slots if x['execution_status'] != 'success' or effective.get((x['constructor_id'],x['seed']),{}).get('__analysis_status__') != 'complete']
    return {'status':'mismatch' if errors else ('matched_with_preserved_provider_failures' if provider_failures else 'matched_with_unavailable_slots' if unavailable_slots else 'matched'),
        'checks':checks,'numeric_statistics_compared':numeric,'maximum_numeric_difference':max_difference,
        'errors':errors,'provider_failures':provider_failures,'unavailable_slots':len(unavailable_slots),
        'complete_numerical_validation':not errors and not unavailable_slots,
        'quantile_comparison':'exact selected observed value; no numerical tolerance or adjacent-order-statistic allowance',
        'summary_scope':'All 24 construction summaries, four statistical references, six complete/incomplete constructor-first contrasts and exact 72-slot identities'}


def audit(release_path, result_path, output_path):
    release = control.READ(release_path)
    control.require_campaign_closed(release)  # Before result/reference/table access.
    manifest_path = Path(__file__).with_name('CODE_COMMIT_V2.json')
    manifest = control.READ(manifest_path)
    if control.SHA(Path(__file__)) != manifest['recompute_v2_sha256']:
        raise ValueError('Independent v2 code commitment changed')
    report = control.READ(result_path)
    if report['release_sha256'] != control.SHA(release_path):
        raise ValueError('Result release binding mismatch')
    binding_path = UNIT/'implementation/reference_bindings.json'
    if control.SHA(binding_path) != report['reference_binding_sha256']:
        raise ValueError('Reference binding mismatch')
    bindings = control.READ(binding_path)
    references = {}
    reference_mapping_errors = []
    if set(report.get('references',{})) != set(bindings['cases']):
        reference_mapping_errors.append({'kind':'reference_case_inventory'})
    for case,spec in bindings['cases'].items():
        path = (PROJECT/spec['artifact']['path']).resolve()
        if not path.is_relative_to(PROJECT.resolve()) or control.SHA(path) != spec['artifact']['sha256']:
            raise ValueError('Reference artifact binding mismatch')
        original = control.READ(path)
        references[case] = {}
        expected_ids = {d['id'] for category in ('analyses','diagnostics') for d in spec[category]}
        if set(report.get('references',{}).get(case,{})) != expected_ids:
            reference_mapping_errors.append({'kind':'reference_inventory','case':case})
        for category in ('analyses','diagnostics'):
            for definition in spec[category]:
                value = lookup(original,definition['value_path'])
                value = float(value) if finite(value) else None
                references[case][definition['id']] = value
                mapped = report.get('references',{}).get(case,{}).get(definition['id'],{})
                if mapped.get('value') != value or mapped.get('unit') != definition['unit'] or mapped.get('status') != ('available' if value is not None else 'unavailable'):
                    reference_mapping_errors.append({'kind':'reference_mapping','case':case,'id':definition['id']})
    identities, ledger_slots, calculations = [], [], {}
    for construction in release['constructions']:
        session = control.Session(construction['session_root'])
        identity = {'constructor_id':construction['id'], **{key:session.contract[key] for key in ('case_id','information_condition','constructor_kind')}}
        identities.append(identity)
        closed = session.selected('closed')[0]
        attempts = session.selected('attempt')
        results = session.selected('result')
        for seed in (5101,5102,5103):
            matches = [x for x in attempts if x['purpose']=='final' and x['seed']==seed]
            if len(matches)>1:
                raise ValueError('Duplicate trusted final slot')
            entry = {**identity,'seed':seed,'scheduled':True,'closure_status':closed['status'],
                'candidate':None,'run_id':None,'execution_status':'not_attempted','output_sha256':None}
            reason = 'Final slot not attempted: '+closed.get('reason',closed['status'])
            entry['expected_error'] = {'type':'unattempted_final_slot','message':reason}
            if matches:
                attempt = matches[0]
                outcomes = [x for x in results if x['attempt_index']==attempt['index']]
                if len(outcomes)>1:
                    raise ValueError('Duplicate trusted final result')
                outcome = outcomes[0] if outcomes else {'status':'missing_result','error':{'type':'missing_result','message':'Final attempt has no retained result'}}
                entry.update(candidate=attempt['candidate'],run_id=attempt['run_id'],execution_status=outcome['status'])
                entry['expected_error'] = None if outcome['status']=='success' else outcome.get('error') or {'type':'execution_failure','message':outcome['status']}
                if outcome['status']=='success':
                    path = session.bundle/'executions'/attempt['run_id']/'output/generated.csv'
                    entry['output_sha256'] = control.SHA(path)
                    try:
                        values = calculate(pd.read_csv(path),identity['case_id'])
                        calculations[(construction['id'],seed)] = {'values':values,'error':None}
                    except Exception as exc:
                        calculations[(construction['id'],seed)] = {'values':None,'error':type(exc).__name__+': '+str(exc)}
            ledger_slots.append(entry)
    result = review_report(report,identities,ledger_slots,calculations,references,bindings)
    result['errors'].extend(reference_mapping_errors)
    if reference_mapping_errors:
        result['status']='mismatch'
        result['complete_numerical_validation']=False
    result.update(generated_rows_regenerated=0,reference_raw_data_recomputed=False,
        scope='Independent arithmetic on retained outputs after global closure; frozen aggregate mapping only, no clinical raw-data recomputation or unavailable-primary-value substitution.',
        result_sha256=control.SHA(result_path),audit_code_sha256=manifest['recompute_v2_sha256'],
        code_commit_sha256=control.SHA(manifest_path))
    control.require_campaign_closed(release)
    if control.READ(release_path)!=release or control.SHA(Path(__file__))!=manifest['recompute_v2_sha256']:
        raise ValueError('Release or audit code changed during audit')
    with Path(output_path).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write('\n')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--release',required=True)
    parser.add_argument('--results',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    print(json.dumps(audit(args.release,args.results,args.output)))


