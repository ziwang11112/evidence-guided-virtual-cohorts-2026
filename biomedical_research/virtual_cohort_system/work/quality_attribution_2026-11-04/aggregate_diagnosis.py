"""Post-evaluation diagnostics from frozen specs and aggregate results only.

No candidate imports/execution, random generation, row-table reads, or parameter
fitting. Differences to references are descriptive, not causal attribution or
population-bias estimates. Only outputs in this new diagnostic folder change.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
from statistics import mean

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parent.parent
BATCH = PROJECT / 'work/core_workflow_replication_2026-11-04'
inputs = {}

def read(path, kind='json'):
    data = path.read_bytes()
    inputs[str(path)] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    text = data.decode('utf-8-sig')
    if kind == 'csv':
        return list(csv.DictReader(text.splitlines()))
    return json.loads(text)

rows = read(BATCH / 'evaluation_v2/ALL_ENDPOINTS.csv', 'csv')
assert len(rows) == 366
assert {r['author_id'] for r in rows} == {'C01', 'C02', 'E01', 'E02'}
specs = {a: read(WORKSPACE / f'evcRep{a}/candidates/initial/model_spec.json')['parameters']
         for a in ['C02', 'E01', 'E02']}
evidence = read(WORKSPACE / 'evcRepE02/candidates/initial/evidence.json')
items = {item['id']: item for item in evidence['items']}

def aggregate(author, endpoint):
    selected = [r for r in rows if r['author_id'] == author and r['endpoint'] == endpoint]
    assert len(selected) == 3, (author, endpoint, len(selected))
    assert all(r['execution_status'] == 'success' for r in selected)
    references = {float(r['reference_value']) for r in selected}
    assert len(references) == 1
    values = [float(r['generated_value']) for r in selected]
    return {'author': author, 'endpoint': endpoint, 'unit': selected[0]['unit'],
            'generated_mean': mean(values), 'seed_min': min(values), 'seed_max': max(values),
            'reference_sample_estimate': references.pop()}

def diagnostic(author, endpoint, law_value, interpretation):
    result = aggregate(author, endpoint)
    result.update(law_value=law_value, interpretation=interpretation)
    result['generated_minus_law'] = result['generated_mean'] - law_value
    result['law_minus_reference'] = law_value - result['reference_sample_estimate']
    result['generated_minus_reference'] = result['generated_mean'] - result['reference_sample_estimate']
    result['arithmetic_decomposition_residual'] = (result['generated_minus_law'] +
        result['law_minus_reference'] - result['generated_minus_reference'])
    assert abs(result['arithmetic_decomposition_residual']) < 1e-12
    return result

c = specs['C02']
e1 = specs['E01']
e2 = specs['E02']
diagnostics = [
    diagnostic('C02', 'E2', c['coefficient_glucose'], 'Conditional-mean implication; not a new source or target fit.'),
    diagnostic('C02', 'E3', c['coefficient_age'], 'Conditional-mean implication; not a new source or target fit.'),
    diagnostic('E01', 'Q1_age10', 10*e1['hba1c']['age_slope'], 'Conditional age term, per decade.'),
    diagnostic('E01', 'Q3_bmi5', 5*e1['hba1c']['bmi_slope'], 'Conditional BMI term derived under working source assumptions.'),
    diagnostic('E02', 'Q1_age10', 10*e2['hba1c_age_slope'], 'Conditional age term, per decade.'),
    diagnostic('E02', 'Q3_bmi5', 5*e2['hba1c_bmi_slope'], 'Conditional BMI term explicitly assumed, not identified by ecological groups.'),
    diagnostic('E01', 'Q2_bmi5', 5*(e1['hba1c']['bmi_slope'] +
        e1['hba1c']['glucose_slope']*e1['glucose']['bmi_slope']),
        'Reduced-model projection derived from the triangular conditional means; includes joint structure.'),
    diagnostic('E01', 'q1_residual_rms', math.sqrt(e1['hba1c']['variance']),
        'Population conditional residual SD; finite fitted RMS differs through sampling and estimated regression.'),
    diagnostic('E02', 'q1_residual_rms', e2['hba1c_residual_sd'],
        'Population constant arithmetic conditional residual SD; log-scale variance is not constant.'),
]

# Finite-rounding feasibility is NOT source sampling uncertainty or a CI.
source_values = {k: items[k]['estimate'] for k in [
    'S4_hba1c_mean', 'S4_hba1c_sd', 'S4_glucose_mean', 'S4_glucose_sd',
    'S4_equation_intercept', 'S4_glucose_hba1c_slope', 'S4_reported_correlation']}
mu_h = source_values['S4_hba1c_mean']
sd_h = source_values['S4_hba1c_sd']
mu_g = source_values['S4_glucose_mean']
sd_g = source_values['S4_glucose_sd']
intercept = source_values['S4_equation_intercept']
slope = source_values['S4_glucose_hba1c_slope']
r = source_values['S4_reported_correlation']
compatibility = {
    'population_context': items['S4_hba1c_mean']['selection'],
    'source_values': source_values,
    'equation_implied_mean_at_reported_glucose_mean': intercept + slope*mu_g,
    'reported_mean': mu_h,
    'slope_implied_by_correlation_and_sds': r*sd_h/sd_g,
    'reported_slope': slope,
    'correlation_implied_by_slope_and_sds': slope*sd_g/sd_h,
    'reported_correlation': r,
    'rounding_only_assumption': 'Conventional round-to-nearest at printed decimal precision; same intercept-containing OLS sample and weights, with r interpreted as Pearson. These common-context assumptions are not guaranteed by the paper; this is not an uncertainty interval.',
    'rounding_only_min_equation_mean': (intercept-.00005)+(slope-.00005)*(mu_g-.5),
    'rounding_only_max_reported_mean': mu_h+.05,
    'rounding_only_min_moment_slope': (r-.005)*(sd_h-.05)/(sd_g+.5),
    'rounding_only_max_reported_slope': slope+.00005,
    'conclusion': 'Cannot enforce all printed quantities as exact common-context OLS moments. Under conventional rounding, their ranges still do not meet. This does not identify which quantity is wrong or exclude different undocumented analysis contexts.',
}
compatibility['rounding_only_mean_ranges_disjoint'] = (
    compatibility['rounding_only_min_equation_mean'] > compatibility['rounding_only_max_reported_mean'])
compatibility['rounding_only_slope_ranges_disjoint'] = (
    compatibility['rounding_only_min_moment_slope'] > compatibility['rounding_only_max_reported_slope'])

source_sd_comparison = aggregate('E02', 'hba1c.sd_population')
source_sd_comparison.update(source_sd=sd_h,
    generated_minus_source=source_sd_comparison['generated_mean']-sd_h,
    source_minus_reference=sd_h-source_sd_comparison['reference_sample_estimate'],
    interpretation='Source SD is a transported surrogate setting, not an exact promise for the truncated target-design law. Closer source fit does not imply closer target agreement.')

result = {
    'scope': 'Post-evaluation deterministic calculations on frozen parameters and aggregate summaries; no new scientific validation.',
    'inputs': inputs, 'diagnostics': diagnostics,
    'source_compatibility': compatibility, 'source_sd_comparison': source_sd_comparison,
    'limitations': [
        'No attempt to allocate a causal percentage of error among sampling, structure, selection, measurement and transport.',
        'Generated seed range is not uncertainty about the law; reference sample estimate is not known population truth.',
        'Fitted sample RMS is not expected to equal the theoretical conditional SD exactly.',
        'Six direct conditional-mean cases are six of twelve author-endpoint combinations, not every primary analysis.',
        'No threshold for biological usefulness is invented by this diagnostic.',
    ]
}
for path, identity in inputs.items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == identity['sha256']
(HERE/'AGGREGATE_DIAGNOSIS.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
with (HERE/'LAW_AND_REFERENCE_COMPARISON.csv').open('w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=list(diagnostics[0]))
    writer.writeheader()
    writer.writerows(diagnostics)
print(json.dumps({'status': 'completed', 'diagnostics': len(diagnostics),
                  'source_rounding_ranges_disjoint': [compatibility['rounding_only_mean_ranges_disjoint'], compatibility['rounding_only_slope_ranges_disjoint']],
                  'input_files_unchanged': len(inputs)}, ensure_ascii=False))
