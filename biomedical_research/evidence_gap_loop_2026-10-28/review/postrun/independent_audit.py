"""Post-release audit only. No evaluator import and no participant-row export.

Fit by reduced weighted QR, retain raw weights, sum cluster scores using NumPy
index accumulation, transform cluster scores by triangular solves, then center
the transformed PSU totals within every full-spine stratum. This is separate
code and algebra from the evaluator's normal-equation inverse/sandwich routine.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import csv
import hashlib
import json
import math
import platform
import numpy as np
import pandas as pd
import scipy
from scipy.linalg import solve_triangular
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RELEASE_HASH = 'ff6f5dfedbca6565b694d3ea4929db7e392dbaa889f5e95808e16ca6e03ad046'
ABS_TOL, REL_TOL = 1e-9, 1e-10
RUNS = {'ordinary_1': 'ordinary', 'ordinary_2': 'ordinary',
        'gap_1': 'gap_policy', 'gap_2': 'gap_policy'}
observed_columns = ['row_id', 'bmi', 'age', 'sex']
checks, failures, inputs, comparisons = [], [], {}, []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def remember(path):
    inputs[relative(path)] = sha(path)


def read_json(path):
    remember(path)
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def check(condition, label):
    checks.append({'check': label, 'passed': bool(condition)})
    if not condition:
        failures.append(label)
    return bool(condition)


def essential(condition, label):
    if not check(condition, label):
        raise ValueError(label)


def safe_path(value):
    p = Path(value)
    p = p.resolve() if p.is_absolute() else (ROOT/p).resolve()
    essential(p.is_relative_to(ROOT), 'Committed path remains inside pilot')
    return p


def verify_map(mapping, label):
    canonical = {}
    for value, digest in mapping.items():
        p = safe_path(value)
        essential(p not in canonical, label+': canonical paths unique')
        essential(p.is_file(), label+': committed file exists')
        remember(p)
        check(inputs[relative(p)] == digest, label+': '+relative(p))
        canonical[p] = digest
    return canonical


def compare(actual, expected, location):
    """Compare the entire nested aggregate payload, recording only aggregate scalars."""
    if isinstance(expected, dict):
        essential(isinstance(actual, dict), location+': dict')
        check(set(actual) == set(expected), location+': keys')
        for key in expected.keys() & actual.keys():
            compare(actual[key], expected[key], location+'/'+key)
    elif isinstance(expected, list):
        essential(isinstance(actual, list), location+': list')
        check(len(actual) == len(expected), location+': length')
        for i, (a, e) in enumerate(zip(actual, expected)):
            compare(a, e, location+'/'+str(i))
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        essential(isinstance(actual, (int, float, np.number)), location+': numeric')
        error = abs(float(actual)-float(expected))
        tolerance = ABS_TOL+REL_TOL*abs(float(expected))
        equal = math.isfinite(float(actual)) and math.isfinite(float(expected)) and error <= tolerance
        comparisons.append({'location': location, 'official': float(actual),
                            'independent': float(expected), 'absolute_difference': error,
                            'tolerance': tolerance, 'passed': bool(equal)})
        if not equal:
            failures.append(location+': numeric discrepancy')
    else:
        check(actual == expected, location+': exact value')


def read_csv(path):
    remember(path)
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        fields = next(csv.reader(stream))
    essential(len(fields) == len(set(fields)), relative(path)+': unique columns')
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def match_y(frame, observed, label):
    essential(set(frame.columns) == set(observed_columns+['hdl']), label+': exact columns')
    essential(len(frame) == len(observed), label+': row count')
    essential(frame.row_id.is_unique and set(frame.row_id) == set(observed.row_id), label+': one-to-one row keys')
    aligned = frame.set_index('row_id').loc[observed.row_id]
    for column in observed_columns[1:]:
        a, b = aligned[column].to_numpy(float), observed[column].to_numpy(float)
        essential(np.array_equal(a, b), label+': exact observed '+column)
    y = aligned.hdl.to_numpy(float)
    essential(np.isfinite(y).all() and (y > 0).all(), label+': finite positive HDL')
    return y


def provenance(release):
    essential(sha(ROOT/'custodian/evaluation_release.json') == RELEASE_HASH, 'Authorized release SHA256')
    for field in ['all_four_constructions_frozen', 'root_authorized_evaluation', 'no_builder_access_to_target']:
        check(release[field] is True, 'Release assertion '+field)
    registered = verify_map(release['artifacts'], 'Release artifact')
    check(len(registered) == 189, 'All 189 release commitments verified')
    for field, name in [('analysis_spec_sha256', 'analysis_spec.json'), ('evaluator_sha256', 'evaluate.py')]:
        check(release[field] == sha(ROOT/'custodian'/name), 'Release '+field)
    packet = read_json(ROOT/'custodian/locked/freeze_manifest.json')
    verify_map({x['path']: x['sha256'] for x in packet['files']}, 'Custodian frozen file')
    seal = read_json(ROOT/'all_outputs_freeze.json')
    check(sha(ROOT/'all_outputs_freeze.json') == release['all_outputs_freeze_sha256'], 'All outputs seal digest')
    check(seal['artifacts'] == release['artifacts'], 'Seal and release artifact commitments identical')
    if 'outputs' in seal:
        check(seal['outputs'] == release['outputs'], 'Seal and release output slots identical')
    entries = release['outputs']
    slots = {(e['construction'], e['stage'], e['draw']): e for e in entries}
    expected = {(r, stage, draw) for r in RUNS for stage in ['initial', 'final'] for draw in range(1, 6)}
    essential(len(entries) == len(slots) == 40 and set(slots) == expected, 'Forty complete unique output slots')
    essential(len({safe_path(e['file']) for e in entries}) == 40, 'Forty distinct output paths')
    protocol = read_json(ROOT/'protocol.json')
    seeds = [281001, 281002, 281003, 281004, 281005]
    check(protocol['generation_seeds'] == seeds, 'Frozen seed schedule')
    n = read_json(ROOT/'shared/schema.json')['row_count']
    for name, policy in RUNS.items():
        folder = ROOT/'runs'/name
        run = read_json(folder/'run.json')
        check(run['policy'] == policy, name+': arm assignment')
        check(safe_path(run['observed']) == ROOT/'shared/observed.csv', name+': observed path')
        check(safe_path(run['literature_session']) == folder/'literature', name+': own literature session')
        run_map = verify_map(run['commitment'], name+': run commitment')
        check(set(run_map) <= set(registered), name+': run commitments release bound')
        receipt = read_json(folder/'review_receipt.json')
        check(receipt['execution_allowed'] is True and receipt['no_reference_feedback'] is True, name+': review/blinding assertions')
        receipts = verify_map(receipt['commitment'], name+': receipt commitment')
        initial_review_paths = set(receipts)-{folder/'initial/freeze.json'}
        essential(len(initial_review_paths) == 1, name+': one initial review')
        initial_review = read_json(next(iter(initial_review_paths)))
        final_review = read_json(folder/'final_code_review.json')
        for stage, review in [('initial', initial_review), ('final', final_review)]:
            stage_folder = folder/stage
            freeze = read_json(stage_folder/'freeze.json')
            check(review['execution_allowed'] is True, name+'/'+stage+': execution allowed')
            for field, filename in [('generator_sha256', 'generator.py'), ('model_spec_sha256', 'model_spec.json'), ('evidence_sha256', 'evidence.json'), ('candidate_freeze_sha256', 'freeze.json')]:
                check(review[field] == sha(stage_folder/filename), name+'/'+stage+': review '+field)
            check(freeze['version'] == stage and freeze['policy'] == policy, name+'/'+stage+': frozen assignment')
            check(freeze['run_sha256'] == sha(folder/'run.json'), name+'/'+stage+': frozen run hash')
            check(freeze['run_commitment'] == run['commitment'], name+'/'+stage+': frozen run commitments')
            candidate_map = verify_map(freeze['commitment'], name+'/'+stage+': candidate commitment')
            required = ['generator.py','model_spec.json','evidence.json','decision.md','gateway_snapshot.json']
            required += ['gaps.json', 'actions.json'] if policy == 'gap_policy' else []
            required += ['revision.json'] if stage == 'final' else []
            check({stage_folder/p for p in required} <= set(candidate_map), name+'/'+stage+': required candidate files bound')
            check(all(p.is_relative_to(folder) for p in candidate_map), name+'/'+stage+': candidate file scope')
            snapshot = read_json(stage_folder/'gateway_snapshot.json')
            audit_path = folder/'literature/audit.jsonl'
            audit = audit_path.read_bytes()
            remember(audit_path)
            extent = snapshot['audit_bytes']
            check(safe_path(snapshot['session']) == folder/'literature', name+'/'+stage+': snapshot session')
            check(snapshot['config_sha256'] == sha(ROOT/'tools/gateway_config.json'), name+'/'+stage+': gateway config')
            check(isinstance(extent, int) and 0 < extent <= len(audit), name+'/'+stage+': audit extent')
            check(hashlib.sha256(audit[:extent]).hexdigest() == snapshot['audit_prefix_sha256'], name+'/'+stage+': audit prefix commitment')
            execution = read_json(stage_folder/'outputs/execution.json')
            check(execution['version'] == stage, name+'/'+stage+': execution stage')
            for field, path in [('controller_sha256', ROOT/'loop_control.py'), ('run_sha256', folder/'run.json'), ('candidate_freeze_sha256', stage_folder/'freeze.json'), ('review_receipt_sha256', folder/'review_receipt.json')]:
                check(execution[field] == sha(path), name+'/'+stage+': execution '+field)
            check(execution['final_code_review_sha256'] == (sha(folder/'final_code_review.json') if stage == 'final' else None), name+'/'+stage+': final review binding')
            check(execution['observed_cells_preserved'] is True and execution['same_seed_reproducible'] is True, name+'/'+stage+': recorded execution assertions')
            check([x['seed'] for x in execution['draws']] == seeds, name+'/'+stage+': execution seeds')
            for i, draw in enumerate(execution['draws'], 1):
                slot = slots[(name, stage, i)]
                path = stage_folder/'outputs'/f'draw_{i:02d}.csv'
                check(safe_path(draw['path']) == safe_path(slot['file']) == path, name+'/'+stage+': draw path '+str(i))
                check(slot['arm'] == policy and slot['seed'] == draw['seed'], name+'/'+stage+': draw policy/seed '+str(i))
                check(draw['sha256'] == slot['sha256'] == sha(path), name+'/'+stage+': draw digest '+str(i))
                check(draw['n_rows'] == n, name+'/'+stage+': recorded row count '+str(i))
    return entries


def setup_design(observed, spine):
    essential(list(observed.columns) == observed_columns, 'Observed column allowlist')
    essential(observed.row_id.ne('').all() and observed.row_id.is_unique, 'Observed nonempty unique row keys')
    essential(spine.design_id.is_unique, 'Unique full-spine design keys')
    essential(np.isfinite(spine.weight.to_numpy(float)).all() and (spine.weight.to_numpy(float) > 0).all(), 'Full-spine finite positive weights')
    essential(spine.in_target_domain.isin(['0','1']).all(), 'Binary domain flag')
    essential(spine[['stratum','psu']].ne('').all().all(), 'Complete survey design codes')
    domain = spine[spine.in_target_domain == '1']
    essential(domain.row_id.is_unique and set(domain.row_id) == set(observed.row_id), 'One-to-one domain alignment')
    essential(spine.loc[spine.in_target_domain == '0','row_id'].eq('').all(), 'No out-of-domain row keys')
    domain = domain.set_index('row_id').loc[observed.row_id]
    b = (observed.bmi.to_numpy(float)-25)/5
    a = (observed.age.to_numpy(float)-50)/10
    f = (observed.sex.to_numpy(float) == 2).astype(float)
    intercept = np.ones(len(observed))
    designs = dict(A=np.stack([intercept,b],axis=1), B=np.stack([intercept,b,a,f],axis=1),
                   C=np.stack([intercept,b,b**2,a,f],axis=1), D=np.stack([intercept,b,a,f,b*f],axis=1))
    pairs = sorted(set(zip(spine.stratum,spine.psu)))
    index = {pair: i for i,pair in enumerate(pairs)}
    positions = np.array([index[p] for p in zip(domain.stratum,domain.psu)])
    groups = defaultdict(list)
    for i,(stratum,_) in enumerate(pairs):
        groups[stratum].append(i)
    essential(all(len(g) >= 2 for g in groups.values()), 'No full-spine singleton strata')
    domain_pairs = set(zip(domain.stratum,domain.psu))
    diagnostics = {'full_spine_n':len(spine), 'domain_n':len(domain), 'full_strata':len(groups),
                   'full_psus':len(pairs), 'domain_strata':len(set(domain.stratum)), 'domain_psus':len(domain_pairs)}
    diagnostics['design_df'] = diagnostics['domain_psus']-diagnostics['domain_strata']
    w = domain.weight.to_numpy(float)
    prepared, condition = {}, {}
    for model, X in designs.items():
        Z = X*np.sqrt(w)[:,None]
        Q,R = np.linalg.qr(Z, mode='reduced')
        rank = int(np.linalg.matrix_rank(Z))
        essential(rank == X.shape[1], model+': full model rank')
        diag = {**diagnostics, 'rank':rank, 'residual_df':diagnostics['design_df']-(rank-1)}
        prepared[model] = X,Q,R,diag
        condition[model] = float(np.linalg.cond(Z))
    return prepared,w,positions,list(groups.values()),diagnostics,condition,len(pairs)-len(domain_pairs)


def independent_analysis(y, observed, setup, spec):
    prepared,w,positions,groups,_,_,_ = setup
    fits, endpoints = {},[]
    for model,(X,Q,R,diagnostics) in prepared.items():
        beta = solve_triangular(R, Q.T@(np.sqrt(w)*y))
        residual = y-X@beta
        cluster = np.zeros((sum(map(len,groups)),X.shape[1]))
        np.add.at(cluster, positions, X*(w*residual)[:,None])
        # Each row of influence is (X'WX)^-1 times a cluster score.
        influence = solve_triangular(R, solve_triangular(R.T, cluster.T, lower=True)).T
        covariance = np.zeros((X.shape[1],X.shape[1]))
        for members in groups:
            values = influence[members]
            deviations = values-np.mean(values,axis=0)
            covariance += (len(members)/(len(members)-1))*np.einsum('ij,ik->jk',deviations,deviations)
        fits[model] = {'coefficients':beta.tolist(),'covariance':covariance.tolist(),'diagnostics':diagnostics}
        for endpoint in spec['endpoints']:
            if endpoint['model'] != model:
                continue
            c = np.asarray(endpoint['contrast'], dtype=float)
            estimate = float(np.dot(c,beta))
            variance = float(np.einsum('i,ij,j',c,covariance,c))
            essential(variance >= 0, 'Nonnegative independent contrast variance')
            standard_error = math.sqrt(variance)
            df = diagnostics['residual_df']
            margin = float(t.isf(.025,df))*standard_error if df > 0 else None
            endpoints.append({'endpoint':endpoint['name'],'model':model,'role':endpoint['role'],
                'estimate':estimate,'standard_error':standard_error,'ci95_low':estimate-margin if margin is not None else None,
                'ci95_high':estimate+margin if margin is not None else None,'df':df})
    mean = float(np.average(y,weights=w))
    sd = math.sqrt(float(np.average((y-mean)**2,weights=w)))
    order = np.argsort(y,kind='stable')
    sorted_y, sorted_w = y[order],w[order]/w.sum()
    cumulative = np.cumsum(sorted_w)
    quantiles = {}
    for q in [.1,.5,.9]:
        quantiles[str(q)] = float(sorted_y[np.flatnonzero(cumulative >= q)[0]])
    bmi = observed.bmi.to_numpy(float)
    bc,yc = bmi-np.average(bmi,weights=w),y-mean
    denominator = math.sqrt(float(np.average(bc**2,weights=w)*np.average(yc**2,weights=w)))
    correlation = float(np.average(bc*yc,weights=w)/denominator) if denominator > 0 else None
    return {'fits':fits,'endpoints':endpoints,'distribution':{'weighted_mean':mean,
        'weighted_sd_population':sd,'weighted_quantiles_inverse_cdf':quantiles,'weighted_bmi_correlation':correlation}}


def compare_csv(path, independent, keys):
    remember(path)
    official = pd.read_csv(path)
    essential(not official.duplicated(keys).any(), relative(path)+': unique aggregate keys')
    essential(set(official.columns) == set(independent.columns), relative(path)+': all aggregate fields')
    official = official.sort_values(keys).reset_index(drop=True)
    independent = independent[official.columns].sort_values(keys).reset_index(drop=True)
    compare(official.to_dict('records'), independent.to_dict('records'), relative(path))


def interval_class(low,high):
    if low is None or high is None or not np.isfinite(low+high):
        return 'unavailable'
    return 'positive' if low > 0 else 'negative' if high < 0 else 'unresolved'


def report_audit(reference, table):
    report_dir = ROOT/'report'
    status = {'available':(report_dir/'report_manifest.json').exists(), 'interpretation_findings':[]}
    remember(ROOT/'make_report.py')
    if not status['available']:
        return status
    manifest = read_json(report_dir/'report_manifest.json')
    check(manifest['input_release_sha256'] == RELEASE_HASH, 'Report input release binding')
    check(manifest['input_analysis_sha256'] == sha(ROOT/'custodian/results/analysis_results.json'), 'Report input aggregate binding')
    check(manifest['script_sha256'] == sha(ROOT/'make_report.py'), 'Report script binding')
    check(manifest['reporting_plan_sha256'] == sha(ROOT/'reporting_plan.json'), 'Report plan binding')
    for name,digest in manifest['files'].items():
        p = report_dir/name
        remember(p)
        check(sha(p) == digest, 'Report artifact digest '+name)
    references = {x['endpoint']:x for x in reference['endpoints']}
    rows = []
    for key,group in table.groupby(['construction','arm','stage','endpoint'],sort=True):
        construction,arm,stage,endpoint = key
        ref = references[endpoint]
        values = group.estimate.to_numpy(float)
        kinds = [interval_class(lo,hi) for lo,hi in zip(group.ci95_low,group.ci95_high)]
        rows.append(dict(construction=construction,arm=arm,stage=stage,endpoint=endpoint,role=ref['role'],
            reference_estimate=ref['estimate'],reference_ci95_low=ref['ci95_low'],reference_ci95_high=ref['ci95_high'],
            reference_interval_class=interval_class(ref['ci95_low'],ref['ci95_high']),
            generated_median=float(np.median(values)),generated_min=float(min(values)),generated_max=float(max(values)),
            positive_point_draws=int(sum(values>0)),negative_point_draws=int(sum(values<0)),zero_point_draws=int(sum(values==0)),
            positive_interval_draws=kinds.count('positive'),negative_interval_draws=kinds.count('negative'),
            unresolved_interval_draws=kinds.count('unresolved'),unavailable_interval_draws=kinds.count('unavailable')))
    compare_csv(report_dir/'all_analysis_interpretations.csv',pd.DataFrame(rows),['construction','stage','endpoint'])
    text = (report_dir/'ALL_ANALYSES.md').read_text(encoding='utf-8')
    text_checks = {
        'unresolved_interval_not_null':'unresolved, not an established null' in text,
        'no_universal_significance_success':'matching significance is not a universal success criterion' in text,
        'five_draws_not_five_agents':'not five independent Agents' in text,
        'no_inferential_workflow_winner':'do not establish superiority' in text,
        'all_eight_endpoints':all(name in text for name in references),
        'conditional_synthetic_uncertainty':'conditional on that generator' in text,
    }
    for name,passed in text_checks.items():
        check(passed,'Report interpretation: '+name)
    # Independently reconstruct the human-readable effect rows at reported precision.
    for endpoint,ref in references.items():
        cells = [endpoint,ref['role'],f"{ref['estimate']:.3f} [{ref['ci95_low']:.3f}, {ref['ci95_high']:.3f}]"]
        for construction in RUNS:
            values = table[(table.endpoint==endpoint)&(table.stage=='final')&(table.construction==construction)].estimate
            cells.append(f'{np.median(values):.3f} [{min(values):.3f}, {max(values):.3f}]')
        check('| '+' | '.join(cells)+' |' in text,'Report Markdown effect row '+endpoint)
    for row in rows:
        if row['stage'] != 'final':
            continue
        line = (f"| {row['construction']} | {row['endpoint']} | {row['reference_interval_class']} | "
                f"{row['positive_point_draws']} / {row['negative_point_draws']} | "
                f"{row['positive_interval_draws']} / {row['negative_interval_draws']} / {row['unresolved_interval_draws']} |")
        check(line in text,'Report Markdown interval row '+row['construction']+'/'+row['endpoint'])
    status['interpretation_checks'] = text_checks
    status['interpretation_findings'] = [
        'All eight final endpoints and all 64 initial/final construction-endpoint summaries are retained.',
        'Interval direction classifications are descriptive and are not used as a universal success score.',
        'Real intervals overlapping zero are called unresolved, never proof of a null.',
        'Five generated residual draws are explicitly distinguished from independent Agent constructions.',
        'No pooled endpoint score, aggregate winner, or inferential superiority claim appears in the reporting code or ALL_ANALYSES.md.',
        'The source uses the preregistered per-endpoint median and min/max; the figure labels those ranges as not confidence intervals.'
    ]
    # Verify the process summary against original aggregate model and retrieval metadata.
    process = read_json(report_dir/'process_summary.json')
    essential({x['construction'] for x in process} == set(RUNS), 'Report process includes four constructions')
    for item in process:
        name = item['construction']
        folder = ROOT/'runs'/name
        before,after = read_json(folder/'initial/model_spec.json'),read_json(folder/'final/model_spec.json')
        changed = sorted(k for k in set(before['parameters'])|set(after['parameters']) if before['parameters'].get(k) != after['parameters'].get(k))
        check(item['parameter_keys_changed'] == changed, name+': report changed parameters')
        check(item['generator_bytes_changed'] == (sha(folder/'initial/generator.py') != sha(folder/'final/generator.py')), name+': report code change')
        for stage in ['initial','final']:
            check(item[stage+'_source_count'] == len(read_json(folder/stage/'evidence.json')['sources']),name+': report '+stage+' source count')
            check(item[stage+'_usage'] == read_json(folder/stage/'gateway_snapshot.json')['usage'],name+': report '+stage+' usage')
        check(item['revision'] == read_json(folder/'final/revision.json'),name+': report revision')
        actions = read_json(folder/'final/actions.json') if (folder/'final/actions.json').exists() else []
        action_counts = {key:sum(a['action']==key for a in actions) for key in {a['action'] for a in actions}}
        check(item['action_counts'] == action_counts,name+': report action counts')
    return status


def custodian_aggregate_audit(reference,generated,summary,paired,noops):
    directory = ROOT/'custodian/results'
    path = directory/'aggregate_report.json'
    if not path.exists():
        return {'available':False}
    remember(ROOT/'custodian/summarize_aggregate_results.py')
    aggregate = read_json(path)
    names = [e['endpoint'] for e in reference['endpoints']]
    refs = {e['endpoint']:e for e in reference['endpoints']}
    check(aggregate['all_endpoints_reported'] == names,'Custodian aggregate all endpoints')
    final = summary[summary.stage=='final'].set_index(['construction','endpoint'])
    # Descriptive labels are inspected in the source; numeric fields are recomputed here.
    expected_rows = []
    for name in names:
        actual = next(x for x in aggregate['final_comparison'] if x['endpoint']==name)
        ref = refs[name]
        row = {'endpoint':name,'description':actual['description'],'unit':'mg/dL','role':ref['role'],
               'reference_estimate':ref['estimate'],'reference_ci95_low':ref['ci95_low'],
               'reference_ci95_high':ref['ci95_high'],'reference_df':ref['df']}
        for construction in RUNS:
            for column in ['generated_median','generated_min','generated_max','median_difference','median_absolute_difference']:
                row[construction+'_'+column] = float(final.loc[(construction,name),column])
        expected_rows.append(row)
    compare(aggregate['final_comparison'],expected_rows,'custodian/aggregate_report/final_comparison')
    full_table = pd.DataFrame(expected_rows)
    compare_csv(directory/'final_endpoint_comparison.csv',full_table,['endpoint'])
    concise_columns = ['construction','arm','endpoint','generated_median_initial','generated_median_final',
                       'median_absolute_difference_initial','median_absolute_difference_final','final_minus_initial_median_absolute_difference']
    concise = pd.DataFrame(paired)[concise_columns].sort_values(['construction','arm','endpoint']).reset_index(drop=True)
    compare_csv(directory/'initial_final_error_changes.csv',concise,['construction','arm','endpoint'])
    compare(aggregate['all_initial_final_changes'],concise.to_dict('records'),'custodian/aggregate_report/all_initial_final_changes')
    compact_columns = ['endpoint','reference_estimate','reference_ci95_low','reference_ci95_high']+[r+'_generated_median' for r in RUNS]
    compare_csv(directory/'compact_final_table.csv',full_table[compact_columns],['endpoint'])
    def flatten(d):
        return {'weighted_mean':d['weighted_mean'],'weighted_sd':d['weighted_sd_population'],
                'weighted_q10':d['weighted_quantiles_inverse_cdf']['0.1'],'weighted_q50':d['weighted_quantiles_inverse_cdf']['0.5'],
                'weighted_q90':d['weighted_quantiles_inverse_cdf']['0.9'],'weighted_bmi_correlation':d['weighted_bmi_correlation']}
    ref_distribution = flatten(reference['distribution'])
    dist_rows = []
    for metric,value in ref_distribution.items():
        row = {'metric':metric,'reference':value}
        for construction in RUNS:
            values = [flatten(g['distribution'])[metric] for g in generated if g['construction']==construction and g['stage']=='final']
            row.update({construction+'_median':float(np.median(values)),construction+'_min':float(min(values)),construction+'_max':float(max(values))})
        dist_rows.append(row)
    compare_csv(directory/'final_distribution_comparison.csv',pd.DataFrame(dist_rows),['metric'])
    expected_noops = {name:all(draw['file_bytes_identical'] for draw in checks) for name,checks in noops.items()}
    check(aggregate['initial_final_generated_output_hashes_identical']==expected_noops,'Custodian aggregate exact no-op outcomes')
    ordinary = concise[concise.construction=='ordinary_1']
    decreased = ordinary.loc[ordinary.final_minus_initial_median_absolute_difference<0,'endpoint'].tolist()
    increased = ordinary.loc[ordinary.final_minus_initial_median_absolute_difference>0,'endpoint'].tolist()
    check(aggregate['ordinary_1_error_changes']=={'decreased_endpoints':decreased,'increased_endpoints':increased},'Custodian aggregate endpoint revision directions')
    check(len(decreased)==5 and len(increased)==3,'Custodian narrative five smaller/three larger absolute differences')
    for filename,digest in aggregate['input_hashes'].items():
        source = directory/filename if (directory/filename).exists() else ROOT/'custodian'/filename
        check(sha(source)==digest,'Custodian aggregate input hash '+filename)
    negative_names = ['crude_bmi_per_5','adjusted_bmi_per_5','male_bmi_slope_per_5','female_bmi_slope_per_5']
    check(all(refs[e]['estimate']<0 and all(final.loc[(r,e),'generated_median']<0 for r in RUNS) for e in negative_names),'Custodian narrative negative BMI directions')
    curvature = 'bmi_slope_at_35_minus_25_per_5'
    check(all(0<final.loc[(r,curvature),'generated_median']<refs[curvature]['estimate'] for r in RUNS),'Custodian narrative positive smaller curvature')
    age_errors = {r:final.loc[(r,'adjusted_age_per_10'),'median_absolute_difference'] for r in RUNS}
    check(age_errors['ordinary_2']<min(v for r,v in age_errors.items() if r!='ordinary_2'),'Custodian narrative ordinary_2 closest age estimate')
    check(all(final.loc[(r,'adjusted_female_minus_male'),'generated_median']>0 for r in RUNS),'Custodian narrative positive female-minus-male medians')
    interaction = refs['female_minus_male_bmi_slope_per_5']
    check(interaction['ci95_low']<0<interaction['ci95_high'],'Custodian narrative unresolved reference interaction')
    return {'available':True,'four_csv_tables_and_aggregate_json_compared':True,
            'interpretation':'All six custodian interpretation statements are supported and remain descriptive; no composite or superiority claim.',
            'ordinary_1_endpoints_with_smaller_median_absolute_difference':decreased,
            'ordinary_1_endpoints_with_larger_median_absolute_difference':increased}


def main():
    release = read_json(ROOT/'custodian/evaluation_release.json')
    entries = provenance(release)
    observed = read_csv(ROOT/'shared/observed.csv')
    essential(len(observed) == 4885, 'Frozen observed domain count')
    reference_frame = read_csv(ROOT/'custodian/locked/reference.csv')
    y_true = match_y(reference_frame,observed,'Reference')
    spine = read_csv(ROOT/'custodian/locked/design_spine.csv')
    spec = read_json(ROOT/'custodian/analysis_spec.json')
    setup = setup_design(observed,spine)
    reference = independent_analysis(y_true,observed,setup,spec)
    generated,draw_rows = [],[]
    vectors = {}
    references = {e['endpoint']:e for e in reference['endpoints']}
    for entry in entries:
        path = safe_path(entry['file'])
        y = match_y(read_csv(path),observed,relative(path))
        metadata = {k:entry[k] for k in ['construction','arm','stage','draw']}
        vectors[(entry['construction'],entry['stage'],entry['draw'])] = y
        result = independent_analysis(y,observed,setup,spec)
        generated.append({**metadata,**result})
        for endpoint in result['endpoints']:
            ref = references[endpoint['endpoint']]
            difference = endpoint['estimate']-ref['estimate']
            draw_rows.append({**metadata,**endpoint,'true_estimate':ref['estimate'],'true_ci95_low':ref['ci95_low'],
                'true_ci95_high':ref['ci95_high'],'difference':difference,'absolute_difference':abs(difference)})
    noops = {}
    for name in RUNS:
        pairs = []
        for draw in range(1,6):
            initial,final = ROOT/'runs'/name/'initial/outputs'/f'draw_{draw:02d}.csv',ROOT/'runs'/name/'final/outputs'/f'draw_{draw:02d}.csv'
            byte_same = initial.read_bytes() == final.read_bytes()
            vector_same = np.array_equal(vectors[(name,'initial',draw)],vectors[(name,'final',draw)])
            pairs.append({'draw':draw,'file_bytes_identical':byte_same,'hdl_vector_identical':vector_same})
            expected_same = name != 'ordinary_1'
            check(byte_same == vector_same == expected_same,name+': expected initial/final draw identity '+str(draw))
        noops[name] = pairs
        for stage in ['initial','final']:
            distinct = len({vectors[(name,stage,i)].tobytes() for i in range(1,6)})
            check(distinct == 5,name+'/'+stage+': five distinct generated vectors')
    official_path = ROOT/'custodian/results/analysis_results.json'
    official = read_json(official_path)
    check(official['release_manifest_sha256'] == RELEASE_HASH,'Official result release hash')
    check(official['spec_sha256'] == sha(ROOT/'custodian/analysis_spec.json'),'Official result spec hash')
    compare(official['reference'],reference,'analysis_results/reference')
    compare(official['generated'],generated,'analysis_results/generated')
    table = pd.DataFrame(draw_rows)
    group_keys = ['construction','arm','stage','endpoint']
    summaries = []
    for key,group in table.groupby(group_keys,sort=True):
        summaries.append({**dict(zip(group_keys,key)),
            'generated_median':float(np.median(group.estimate)), 'generated_min':float(min(group.estimate)),
            'generated_max':float(max(group.estimate)), 'median_difference':float(np.median(group.difference)),
            'median_absolute_difference':float(np.median(group.absolute_difference)), 'true_estimate':float(group.true_estimate.iloc[0])})
    summary = pd.DataFrame(summaries)
    initial = {(x['construction'],x['arm'],x['endpoint']):x for x in summaries if x['stage']=='initial'}
    final = {(x['construction'],x['arm'],x['endpoint']):x for x in summaries if x['stage']=='final'}
    paired = []
    for key,a in initial.items():
        b = final[key]
        row = dict(zip(['construction','arm','endpoint'],key))
        for stage,data in [('initial',a),('final',b)]:
            row.update({k+'_'+stage:v for k,v in data.items() if k not in group_keys})
        row['final_minus_initial_median_absolute_difference'] = b['median_absolute_difference']-a['median_absolute_difference']
        paired.append(row)
    compare_csv(ROOT/'custodian/results/all_endpoint_draws.csv',table,['construction','stage','draw','endpoint'])
    compare_csv(ROOT/'custodian/results/endpoint_summary.csv',summary,group_keys)
    compare_csv(ROOT/'custodian/results/initial_final_changes.csv',pd.DataFrame(paired),['construction','arm','endpoint'])
    interpretation = report_audit(reference,table)
    aggregate_audit = custodian_aggregate_audit(reference,generated,summary,paired,noops)
    for name,digest in inputs.items():
        check(sha(ROOT/name)==digest,'Audit input unchanged at completion: '+name)
    independent = {'reference':reference,'generated':generated,'release_manifest_sha256':RELEASE_HASH,
                   'method':'Independent weighted QR and direct full-spine PSU influence covariance; no evaluator import.'}
    write_json(OUT/'independent_analysis_results.json',independent)
    pd.DataFrame(comparisons).to_csv(OUT/'aggregate_discrepancies.csv',index=False)
    pd.DataFrame(checks).to_csv(OUT/'provenance_and_structure_checks.csv',index=False)
    max_diff = max(comparisons,key=lambda x:x['absolute_difference'])
    max_fit_coefficient = max(c['absolute_difference'] for c in comparisons if '/coefficients/' in c['location'])
    max_fit_covariance = max(c['absolute_difference'] for c in comparisons if '/covariance/' in c['location'])
    stats = {'weighted_fits':len(reference['fits'])+sum(len(x['fits']) for x in generated),
             'endpoints':len(reference['endpoints'])+sum(len(x['endpoints']) for x in generated),
             'generated_cohorts':len(generated),'numeric_scalar_comparisons':len(comparisons),
             'exact_or_provenance_checks':len(checks),'numeric_mismatches':sum(not c['passed'] for c in comparisons),
             'failed_checks':len(failures),'maximum_absolute_difference':max_diff['absolute_difference'],
             'maximum_difference_location':max_diff['location'],'maximum_coefficient_absolute_difference':max_fit_coefficient,
             'maximum_covariance_absolute_difference':max_fit_covariance}
    summary_report = {'audit_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS' if not failures else 'FAIL',
        'scope':'Post-run independent numerical/provenance audit after root-authorized evaluation; no builder feedback.',
        'counts':stats,'design':setup[4],'weighted_design_condition_numbers':setup[5],
        'full_psus_without_target_members':setup[6],
        'model_residual_df':{k:v[3]['residual_df'] for k,v in setup[0].items()},
        'tolerance':{'absolute':ABS_TOL,'relative':REL_TOL,
            'justification':'Float64 QR and normalized normal equations have different summation/rounding paths. Tolerances are far below the 0.001 mg/dL report precision; all observed errors are reported, rather than rounded away.'},
        'no_op_and_changed_draw_checks':noops,'report_audit':interpretation,'custodian_aggregate_audit':aggregate_audit,'failures':failures,
        'limitations':['This audit verifies the committed artifacts and current outputs, not an OS-enforced blinding boundary or absence of pretrained exposure.',
            'Same-seed reproducibility assertions were provenance-checked; frozen generator execution was not repeated by this auditor.',
            'This numerical audit does not establish appropriateness of external evidence choices, transport validity, causality, individual outcome recovery, or workflow superiority.',
            'In this dataset every full-spine PSU contains target members; retention of empty-domain PSUs is independently implemented, but this released dataset does not itself exercise a zero-member PSU case.',
            'Synthetic survey intervals remain conditional on generated outcomes and are not calibrated uncertainty about the hidden true feature.'],
        'runtime':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__},
        'participant_rows_exported':False}
    write_json(OUT/'audit_report.json',summary_report)
    df_text = ', '.join(f'{k}={v}' for k,v in summary_report['model_residual_df'].items())
    lines = ['# Independent post-run audit','',f"Status: {summary_report['status']} for numerical and provenance verification only; this is not a scientific success score. No generator, evaluator, analysis specification, or rule was changed.",'',
        f"Recomputed 164 weighted fits and 328 endpoints for the real outcome and 40 scheduled generated dataset files. The 40 files occupy distinct paths/slots and have {len({e['sha256'] for e in entries})} distinct SHA-256 contents; they represent four Agent constructions, not 40 independent cohorts or Agents. All {len(comparisons):,} numeric aggregate scalars agree within absolute tolerance {ABS_TOL:g} plus relative tolerance {REL_TOL:g}. {len(failures)} failed checks.",'',
        f"Maximum absolute discrepancy: {max_diff['absolute_difference']:.6g}; coefficients: {max_fit_coefficient:.6g}; covariance entries: {max_fit_covariance:.6g}.",'',
        'The independent implementation uses weighted QR with raw weights and triangular solves for PSU influence totals. It does not import the frozen evaluator. Full-spine PSU groups are retained and centered within strata; all model ranks and residual degrees of freedom match the official results.','',
        f"Design: {setup[4]['full_spine_n']:,} full-spine records, {setup[4]['domain_n']:,} domain records, {setup[4]['full_strata']} full/domain strata and {setup[4]['full_psus']} full/domain PSUs. Model residual df: {df_text}.",'',
        'All 189 release commitments, 40 unique output paths/slots, nested candidate/review/execution commitments, the survey packet manifest, and gateway audit prefixes were independently verified. Every scheduled file retains exactly one row per observed key and exactly preserves BMI, age and sex. Only aggregate data, comparison errors and file hashes are exported.','',
        'Initial/final outputs are byte-identical for ordinary_2, gap_1 and gap_2 for every paired seed. All five ordinary_1 output pairs differ. These are three no-op output revisions and one changed construction; documentation activity alone is not numerical improvement.','',
        'All official fit, distribution, endpoint-draw, summary and initial/final change outputs were checked, including the four later custodian CSV tables and aggregate report. The root report also passes its aggregate, manifest and interpretation checks: all eight endpoints are retained, zero-overlapping real intervals remain unresolved, five draws are not five independent Agents, and significance matching is not a universal success criterion. No composite winner is calculated.','',
        '## Limits',''] + ['- '+s for s in summary_report['limitations']]
    if failures:
        lines += ['','## Failures','']+['- '+s for s in failures]
    (OUT/'AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write_json(OUT/'audit_hashes.json',{'authorized_release_sha256':RELEASE_HASH,
        'audit_source_sha256':sha(__file__),'inputs':inputs,
        'outputs':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='audit_hashes.json'},
        'participant_rows_exported':False})
    print(json.dumps({'status':summary_report['status'],**stats,'design':setup[4],'model_residual_df':summary_report['model_residual_df']}))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
