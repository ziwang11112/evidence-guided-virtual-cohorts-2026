"""Post-seal, additive independent results audit. Never executes a generator.

Run only after RESULTS.json exists. Reads the eight frozen source fields, applies
eligibility with a separate scalar implementation, and uses the frozen pure-
Python FWL oracle. It does not call evaluator, select_rows or summarize.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

import pandas as pd

import controller
from independent_check import independent_estimate

HERE = Path(__file__).resolve().parent
U = HERE.parent
PROJECT = U.parents[1]
FIELDS = ['C008', 'Z001', 'z004', 'z005', 'P005', 'W00407', 'W00408', 'peso_lab']
ARCHIVE = PROJECT / 'work/analysis-utility-preparation-2026-10-29/pns_hba1c/custodian/raw/PNS2013_Exames.zip'
ARCHIVE_HASH = 'd31544efdad138f3292ab86c9606cd722bf091781cc86ef371354ba63c9994bb'
MEMBER = 'EXAMES-PNS-2013-FINAL_05052023.xlsx'
MEMBER_HASH = '80222fa535524829d531504109ac4b49d44e4e6d0c04c3c281ff972bd332d1f7'
SHEET = 'EXAMES-PNS-2013-FINAL_com-ponde'
EXPECTED_BATCH_HASH = '1f3f8137ad282a4844f5c27ff1219fd5827164e720fafc1c71d417bbb27f3acd'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def numeric(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return float('nan')


def independent_reference():
    assert sha(ARCHIVE) == ARCHIVE_HASH
    with zipfile.ZipFile(ARCHIVE) as archive:
        members = [n for n in archive.namelist() if Path(n).name == MEMBER]
        assert len(members) == 1
        payload = archive.read(members[0])
    assert hashlib.sha256(payload).hexdigest() == MEMBER_HASH
    # Shared Excel parser only; selection and estimation do not use production code.
    frame = pd.read_excel(io.BytesIO(payload), sheet_name=SHEET, usecols=FIELDS, engine='openpyxl')
    counts = [0] * 8
    selected, selected_source, indices = [], [], []
    for index, record in enumerate(frame[FIELDS].itertuples(index=False, name=None)):
        age, sex, kg, cm, pregnancy, sbp, dbp, weight = values = list(map(numeric, record))
        rules = [20 <= age <= 79, sex in (1, 2), 30 <= kg <= 200, 120 <= cm <= 210,
                 pregnancy != 1, 60 <= sbp <= 290, 30 <= dbp <= 200,
                 math.isfinite(weight) and weight > 0]
        for stage, keep in enumerate(rules):
            if not keep:
                break
            counts[stage] += 1
        if all(rules):
            selected.append(dict(age=age, female=int(sex == 2), bmi=kg / (cm / 100) ** 2,
                                 sbp=sbp, dbp=dbp, weight=weight))
            selected_source.append(values)
            indices.append(index)
    labels = ['age20to79', 'sex1or2', 'weight30to200kg', 'height120to210cm',
              'not_reported_pregnant', 'sbp60to290', 'dbp30to200', 'positive_finite_labweight']
    prior = len(frame)
    stages = []
    for label, count in zip(labels, counts):
        stages.append(dict(rule=label, remaining=count, excluded_at_step=prior-count))
        prior = count
    keys = [tuple(None if math.isnan(x) else x for x in row) for row in selected_source]
    audit = dict(raw_rows=len(frame), common_eligible_rows=len(selected), sequential_exclusions=stages,
                 both_sexes_present=len({row['female'] for row in selected}) == 2,
                 unknown_or_inapplicable_pregnancy_retained=sum(row[4] not in (1, 2) for row in selected_source),
                 duplicate_required_field_rows=len(keys) - len(set(keys)),
                 selected_zero_based_workbook_indices_sha256=hashlib.sha256(json.dumps(indices).encode()).hexdigest())
    return selected, audit


def extra_diagnostics(rows):
    weights = [float(r.get('weight', 1)) for r in rows]
    total = math.fsum(weights)
    means, sds = {}, {}
    for field in ('age', 'female', 'bmi', 'sbp', 'dbp'):
        mean = math.fsum(w * float(r[field]) for w, r in zip(weights, rows)) / total
        means[field] = mean
        sds[field] = math.sqrt(math.fsum(w * (float(r[field]) - mean) ** 2 for w, r in zip(weights, rows)) / total)
    covariance = math.fsum(w * (float(r['sbp']) - means['sbp']) * (float(r['dbp']) - means['dbp'])
                          for w, r in zip(weights, rows)) / total
    return dict(means=means, sds=sds, raw_correlation=covariance / (sds['sbp'] * sds['dbp']),
                n_eff=total * total / math.fsum(w*w for w in weights),
                below_fraction=math.fsum(w for w, r in zip(weights, rows) if float(r['sbp']) < float(r['dbp'])) / total)


def compare(label, rows, production):
    independent = independent_estimate(rows)
    assert independent['n'] == production['n'] == len(rows), label
    assert independent['status'] == production['status'] == 'estimable', label
    assert production['rank'] == 4, label
    extra = extra_diagnostics(rows)
    differences = {}
    mapping = {'bmi_sbp':'sbp_bmi_per5', 'bmi_dbp':'dbp_bmi_per5', 'residual_correlation':'residual_correlation'}
    for actual, expected in mapping.items():
        differences[actual] = abs(production['estimates'][actual] - independent[expected])
    for outcome in ('sbp', 'dbp'):
        differences['residual_sd_' + outcome] = abs(production['diagnostics']['residual_sd'][outcome] - independent[outcome + '_residual_sd'])
    for field in ('age', 'female', 'bmi', 'sbp', 'dbp'):
        differences['mean_' + field] = abs(production['diagnostics']['margins'][field]['mean'] - extra['means'][field])
        differences['sd_' + field] = abs(production['diagnostics']['margins'][field]['sd'] - extra['sds'][field])
    differences['raw_correlation'] = abs(production['diagnostics']['raw_sbp_dbp_correlation'] - extra['raw_correlation'])
    differences['n_eff'] = abs(production['n_eff'] - extra['n_eff'])
    differences['below_fraction'] = abs(production['diagnostics']['sbp_below_dbp_fraction'] - extra['below_fraction'])
    assert max(differences.values()) < 1e-9, (label, differences)
    return dict(label=label, n=len(rows), independent=independent,
                maximum_absolute_difference=max(differences.values()), differences=differences)


def main():
    assert (U/'RESULTS.json').is_file(), 'Wait for the one production evaluation to finish.'
    assert not (U/'INDEPENDENT_RESULTS_REVIEW.json').exists(), 'Do not overwrite a completed audit.'
    verified = controller.verify_batch_seal()
    assert verified['batch_seal_sha256'] == EXPECTED_BATCH_HASH
    results = read(U/'RESULTS.json')
    assert results['batch_seal_sha256'] == EXPECTED_BATCH_HASH
    assert results['reference_archive_sha256'] == ARCHIVE_HASH
    assert results['reference_member_sha256'] == MEMBER_HASH
    assert results['all_attempted_output_count'] == verified['all_attempted_output_count'] == 15
    assert results['selected_output_count'] == len(verified['selected_outputs']) == len(results['generated']) == 15
    assert len(results['author_outcomes']) == 5
    reference, eligibility = independent_reference()
    for key, value in eligibility.items():
        if key != 'selected_zero_based_workbook_indices_sha256':
            assert results['eligibility'][key] == value, (key, results['eligibility'][key], value)
    checks = [compare('reference_weighted', reference, results['reference_weighted']),
              compare('reference_unweighted', [dict(r, weight=1) for r in reference], results['reference_unweighted_sensitivity'])]
    generated = []
    for output, sealed in zip(results['generated'], verified['selected_outputs']):
        for key in ('author_id', 'candidate', 'run_id', 'seed', 'path', 'sha256', 'status'):
            assert output[key] == sealed[key], key
        assert sha(output['path']) == output['sha256']
        with Path(output['path']).open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 3000
        record = compare(output['author_id'] + '/' + output['run_id'], rows, output['analysis'])
        record.update(author_id=output['author_id'], seed=output['seed'], output_sha256=output['sha256'])
        generated.append(record)
        checks.append(record)
    # Independently check all plotted differences and four dispersion ratios.
    reference_est = checks[0]['independent']
    comparison_difference = 0.0
    for pair, generated_record in zip(results['comparisons'], generated):
        assert pair['author_id'] == generated_record['author_id'] and pair['seed'] == generated_record['seed']
        independent = generated_record['independent']
        for key, oracle_key in (('bmi_sbp','sbp_bmi_per5'), ('bmi_dbp','dbp_bmi_per5'), ('residual_correlation','residual_correlation')):
            signed = independent[oracle_key] - reference_est[oracle_key]
            for field, expected in [('generated', independent[oracle_key]), ('reference',reference_est[oracle_key]),
                                    ('signed_difference',signed), ('absolute_difference',abs(signed))]:
                comparison_difference = max(comparison_difference, abs(pair['estimates'][key][field] - expected))
            assert pair['estimates'][key]['same_sign'] == ((independent[oracle_key] > 0) == (reference_est[oracle_key] > 0))
        for outcome in ('sbp','dbp'):
            for label, suffix in (('marginal','_sd'), ('residual','_residual_sd')):
                expected = independent[outcome+suffix] / reference_est[outcome+suffix]
                comparison_difference = max(comparison_difference, abs(pair['dispersion_ratios'][label+'_'+outcome]-expected))
    assert comparison_difference < 1e-9
    # Each final decision binds all source reports and analyses, never a chosen seed.
    decision_audit = []
    for author in ('A04','A05'):
        b = HERE/'sessions'/author
        final = read(b/'host/final_decision.json')
        seal = read(b/'AUTHOR_SEAL.json')
        receipt = read(HERE/'reviews'/f'{author}_final.json')
        assert receipt['decision_sha256'] == sha(b/'host/final_decision.json')
        assert final['final_candidate'] == seal['final_candidate'] == 'candidates/initial'
        assert len(final['source_feedback_used']) == 6 and len(final['generated_analysis_used']) == 3
        for mapping in (final['source_feedback_used'], final['generated_analysis_used']):
            for rel, digest in mapping.items(): assert sha(b/rel) == digest
        assert sorted(r['seed'] for r in seal['selected_outputs']) == [271,409,557]
        decision_audit.append(dict(author_id=author, final_decision_sha256=receipt['decision_sha256'],
                                   final_candidate=final['final_candidate'], source_reports=6, generated_reports=3,
                                   final_receipt_sha256=sha(HERE/'reviews'/f'{author}_final.json'),
                                   review='Retention and all descriptive discrepancies acknowledged; no revision or exact source replay claimed.'))
    stability = results['reference_row_resampling_stability']
    assert stability['repeats'] == 500 and stability['seed'] == 73991
    assert stability['nonestimable_replicates'] == 0
    assert all(item['estimable_replicates'] == 500 for item in stability['intervals'].values())
    assert 'not design-based' in stability['interpretation']
    limitations = [
        'PASS concerns reproduction and implementation integrity, not a data-quality pass for five authors. No preregistered quality threshold or equivalence/superiority test exists.',
        'All 15 outputs retained initial models. This case demonstrates no improvement from revision or additional retrieval, and no exact source-population replay.',
        'Reference is a weighted selected analytical sample, not known population truth. PNS is an already exposed study family; this is a qualified new BP task.',
        'Reference intervals are conditional IID row-bootstrap stability with row/weight pairs resampled. They ignore complex survey strata/PSU design, missingness, selection and source/transport uncertainty; not national confidence intervals.',
        'The 500 reference bootstrap values were not recomputed on patient data in this audit; their frozen algorithm and quantiles were independently tested on invented fixtures before release. This audit rechecks settings, counts and interpretation.',
        'Three stochastic seeds and five model authors are not 15 independent clinical studies. Their spread is not calibrated epistemic or transport uncertainty.',
        'Matching association signs alone is not sufficient for all scientific uses. Differences in effect size and residual dependence remain visible and must not be hidden by an all-pass label.'
    ]
    report = dict(status='PASS_INDEPENDENT_RESULTS_RECOMPUTATION', reviewer_id='/root/pns_final_review',
                  created_utc=datetime.now(timezone.utc).isoformat(), remaining_blockers=[],
                  method='Independent scalar eligibility; frozen pure-Python weighted orthogonal projection / Frisch-Waugh-Lovell. No production select_rows or summarize calls.',
                  results_sha256=sha(U/'RESULTS.json'), batch_seal_sha256=EXPECTED_BATCH_HASH,
                  bindings={str(p.relative_to(PROJECT)).replace('\\','/'):sha(p) for p in [Path(__file__), HERE/'independent_check.py', HERE/'evaluator.py', HERE/'analysis_tools.py', U/'SELECTION_LOCK.json']},
                  reference_archive_sha256=ARCHIVE_HASH, reference_member_sha256=MEMBER_HASH,
                  eligibility=eligibility, selected_outputs=15, attempted_outputs=15, authors=5,
                  generated_rows_per_output=3000, generated_rows_total=45000,
                  estimate_sets_compared=len(checks), numerical_values_compared=sum(len(r['differences']) for r in checks),
                  maximum_absolute_difference=max(r['maximum_absolute_difference'] for r in checks),
                  maximum_comparison_difference=comparison_difference, recomputations=checks,
                  final_author_audit=decision_audit, limitations=limitations,
                  generators_executed=0, evaluator_rerun=False, patient_tables_written=0)
    with (U/'INDEPENDENT_RESULTS_REVIEW.json').open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    lines = ['# Independent PNS BP results review', '', '**PASS: independent numerical and selection recomputation.**', '',
             f"Results SHA256: `{report['results_sha256']}`.", f"Batch SHA256: `{EXPECTED_BATCH_HASH}`.", '',
             f"Independently selected {len(reference):,} of {eligibility['raw_rows']:,} rows from the fixed eight workbook fields; all sequential exclusion counts, pregnancy handling and retained duplicate counts match.",
             f"Recomputed weighted/unweighted reference and all 15 sealed outputs using the frozen pure-Python FWL oracle: {report['numerical_values_compared']} numerical comparisons; maximum absolute difference {report['maximum_absolute_difference']:.3g}. All 45 focal comparison records and 60 dispersion ratios agree within {comparison_difference:.3g}.",
             'No generator executed, evaluator rerun, patient table persisted, or sealed/frozen file modified.', '',
             '| Analysis | Weighted reference | Unweighted reference | Generated range, all 15 |', '|---|---:|---:|---:|']
    for label,key in [('BMI–SBP, mmHg per5 kg/m²','sbp_bmi_per5'),('BMI–DBP, mmHg per5 kg/m²','dbp_bmi_per5'),('Adjusted residual BP correlation','residual_correlation')]:
        vals=[g['independent'][key] for g in generated]
        lines.append(f"| {label} | {reference_est[key]:.6f} | {checks[1]['independent'][key]:.6f} | {min(vals):.6f}–{max(vals):.6f} |")
    lines += ['', 'The SBP association is in a similar numerical range to the reference across constructions. DBP associations are systematically higher, while residual correlations are systematically lower. These are descriptive observations, not post-hoc pass/fail thresholds or claims of population bias.', '',
              'A04/A05 final records independently checked: both kept the initial candidate and all three seeds, bound all six feedback and three analysis reports, and acknowledged mismatched descriptive source statistics. No target-based revision occurred.', '', '## Interpretation limits', '']
    lines += ['- '+item for item in limitations]
    with (U/'INDEPENDENT_RESULTS_REVIEW.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    print(json.dumps({k:report[k] for k in ['status','selected_outputs','estimate_sets_compared','numerical_values_compared','maximum_absolute_difference','maximum_comparison_difference','results_sha256']},indent=2))


if __name__ == '__main__':
    main()
