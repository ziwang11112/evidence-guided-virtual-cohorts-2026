"""Aggregate every closed HRS attempt without selecting seeds or model terms."""
from pathlib import Path
import csv
import hashlib
import json
from statistics import mean

UNIT = Path(__file__).resolve().parent
ARMS = ['native', 'agent']
SEEDS = [6101, 6102, 6103]

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def csv_out(path, rows):
    if not rows:
        return
    with path.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def summaries(rows, group_keys, value_key, reference_keys):
    groups = {}
    for row in rows:
        key = tuple(row[k] for k in group_keys)
        groups.setdefault(key, []).append(row)
    result = []
    for key, entries in groups.items():
        values = [x[value_key] for x in entries]
        out = dict(zip(group_keys, key))
        out.update(available_seeds=len(values), mean_estimate=mean(values),
                   min_estimate=min(values), max_estimate=max(values))
        for ref_key in reference_keys:
            reference = entries[0][ref_key]
            assert all(x[ref_key] == reference for x in entries)
            out[ref_key] = reference
            out['signed_mean_discrepancy_' + ref_key] = mean(values) - reference
            out['mean_absolute_discrepancy_' + ref_key] = mean(abs(v-reference) for v in values)
        result.append(out)
    return result

def diagnostics(native, paper):
    d = native['table2_diagnostics']
    refs = paper['table2']
    rows = [{'metric': 'subjects', 'estimate': d['subjects'],
             'original_reference': refs['subject_count']['original'],
             'published_synthetic_reference': refs['subject_count']['synthetic']}]
    for observed, reference in [('age','baseline_age'), ('hba1c_overall','hba1c'),
       ('hba1c_below_6_5','hba1c_below'), ('hba1c_at_or_above_6_5','hba1c_above'),
       ('cses','cses'), ('baseline_memory','baseline_mem_s')]:
        for statistic in ['mean', 'sd']:
            rows.append({'metric': reference + '_' + statistic,
                         'estimate': d[observed][statistic],
                         'original_reference': refs[reference]['original_' + statistic],
                         'published_synthetic_reference': refs[reference]['synthetic_' + statistic]})
    for observed, prefix in [('female_male','sex'), ('white_black','race'), ('education','educ')]:
        for cat in d[observed]['categories']:
            key = prefix + '_' + cat['category']
            for metric, source in [('count','count'), ('percentage','percent')]:
                rows.append({'metric': key + '_' + metric, 'estimate': cat[metric],
                             'original_reference': refs[key]['original_' + source],
                             'published_synthetic_reference': refs[key]['synthetic_' + source]})
    assert len(rows) == 27
    return rows

def main():
    assert read(UNIT / 'GENERATION_CLOSED.json')['attempts_spent'] == 6
    source = read(UNIT / 'sources/HRS_SOURCE_EVIDENCE.json')
    paper = read(UNIT / 'sources/HRS_PUBLISHED_REFERENCES.json')
    coefficients = source['memory']['coefficients']
    effects, distributions, statuses, bindings = [], [], [], {}
    for arm in ARMS:
        for seed in SEEDS:
            run_id = f'{arm}_{seed}'
            path = UNIT / 'results' / (run_id + '.evaluation.json')
            receipt = read(path)
            bindings[str(path.relative_to(UNIT))] = sha(path)
            statuses.append(receipt)
            if receipt['status'] != 'computed':
                continue
            native_path = UNIT / 'results' / (run_id + '.native.json')
            native = read(native_path)
            assert sha(native_path) == receipt['native_json_sha256']
            bindings[str(native_path.relative_to(UNIT))] = sha(native_path)
            for row in native['fixed_effects']:
                term = row['term']
                effects.append({'arm': arm, 'seed': seed, 'term': term, **{k: row[k] for k in
                    ['estimate','se','wald_lower','wald_upper']},
                    'exported_coefficient': coefficients[term]['estimate'],
                    'exported_source_se': coefficients[term]['standard_error'],
                    'published_original_coefficient': paper['table3'][term]['original'][0],
                    'published_synthetic_coefficient': paper['table3'][term]['synthetic'][0]})
            distributions.extend([{'arm': arm, 'seed': seed, **row} for row in diagnostics(native, paper)])
    summary = {
        'scope': 'Published HRS recipient-stage aggregate/model reconstruction; six fixed attempts; no new source participant data or independent target validation.',
        'counts': {'attempts': 6, 'computed_fits': sum(x['status']=='computed' for x in statuses),
                   'gls_passes': sum(x.get('gls_status')=='pass' for x in statuses),
                   'subjects_per_successful_table': 11509, 'visits_per_successful_table': 46036},
        'statuses': statuses,
        'fixed_effects': summaries(effects, ['arm','term'], 'estimate',
                                  ['exported_coefficient','published_original_coefficient','published_synthetic_coefficient']),
        'distributions': summaries(distributions, ['arm','metric'], 'estimate',
                                   ['original_reference','published_synthetic_reference']),
        'bindings': bindings,
        'reference_definitions': 'Exported coefficient is higher-precision reported model parameter. Published original/synthetic are rounded paper references; synthetic averages 5000 repetitions. Our three seeds estimate neither patient uncertainty nor the full source-model uncertainty.'
    }
    folder = UNIT / 'summary'
    folder.mkdir(exist_ok=True)
    with (folder / 'AGGREGATE_RESULTS.json').open('x', encoding='utf-8') as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
        stream.write('\n')
    csv_out(folder / 'fixed_effects_all_seeds.csv', effects)
    csv_out(folder / 'fixed_effects_summary.csv', summary['fixed_effects'])
    csv_out(folder / 'distributions_all_seeds.csv', distributions)
    csv_out(folder / 'distributions_summary.csv', summary['distributions'])
    print(json.dumps(summary['counts']))

if __name__ == '__main__':
    main()
