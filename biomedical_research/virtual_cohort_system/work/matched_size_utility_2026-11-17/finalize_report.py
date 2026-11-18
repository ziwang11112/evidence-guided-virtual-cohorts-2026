"""Complete the interpretation from saved, reviewed aggregates; no participant reads."""
from pathlib import Path
from datetime import datetime, timezone
from html import escape
import hashlib
import json
import re
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TRAITS = ['bmi', 'total_cholesterol', 'hdl_cholesterol']
NAMES = {'bmi': 'BMI', 'total_cholesterol': 'Total cholesterol', 'hdl_cholesterol': 'HDL cholesterol'}
CONTRASTS = ['rural_minus_pastoralist', 'urban_minus_pastoralist', 'urban_minus_rural']
LABELS = dict(zip(CONTRASTS, ['Rural − pastoralist', 'Urban − pastoralist', 'Urban − rural']))

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def new_text(path, text):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)

def new_json(path, value):
    new_text(path, json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')

def span(values, places=3):
    return f'{values.min():.{places}f} to {values.max():.{places}f}'

def main():
    for name in ['RESULTS.md', 'MANUSCRIPT_INSERT.md', 'STATE.json', 'DELIVERY_QA.json']:
        assert not (HERE / name).exists(), 'Do not overwrite a completed interpretation'
    run, review = read('RUN_RESULT.json'), read('INDEPENDENT_REVIEW.json')
    assert run['status'] == 'complete' and run['computed'] == 12000 and run['unavailable'] == 0
    assert review['status'] == 'pass' and review['v33_delivery_files_unchanged'] == 28
    df = pd.read_csv(HERE / 'CONTRAST_SUMMARIES.csv')
    sd = pd.read_csv(HERE / 'SD_SUMMARIES.csv')
    est = pd.read_csv(HERE / 'ESTIMATES.csv')
    assert len(df) == 63 and len(sd) == 24 and len(est) == 12000
    assert (est.status == 'computed').all()
    assert not df[['signed_mean', 'absolute_mean']].isna().any().any()

    rows = []
    for t in TRAITS:
        for c in CONTRASTS:
            g = df[(df.trait == t) & (df.contrast == c)]
            r = g[g.comparison == 'real_real'].iloc[0]
            v = g[g.comparison == 'virtual_real']
            assert len(v) == 6 and len(g) == 7
            rows.append([NAMES[t], LABELS[c], f'{r.original_real:.3f}',
                         f'{r.signed_q025:.3f} to {r.signed_q975:.3f}',
                         span(v.signed_mean), f'{r.absolute_mean:.3f}', span(v.absolute_mean)])
    columns = ['Outcome', 'Adjusted contrast', 'Original real effect', 'Real–real 95% difference range',
               'Virtual–real mean signed difference (six-table range)', 'Real–real mean absolute difference',
               'Virtual–real mean absolute difference (six-table range)']
    full_table = '| ' + ' | '.join(columns) + ' |\n|' + '|'.join(['---'] * len(columns)) + '|\n'
    full_table += '\n'.join('| ' + ' | '.join(row) + ' |' for row in rows)

    sdrows = []
    for t in TRAITS:
        r = sd[(sd.trait == t) & (sd.stream == 'R_B')].iloc[0]
        v = sd[(sd.trait == t) & sd.stream.str.startswith('LIFESTYLE_')]
        sdrows.append([NAMES[t], f'{r.original_sd:.3f}', f'{r.sd_mean:.3f}',
                       f'{r.sd_q025:.3f} to {r.sd_q975:.3f}', span(v.sd_mean),
                       f'{v.sd_q025.min():.3f} to {v.sd_q975.max():.3f}'])
    sdcolumns = ['Outcome', 'Original real SD', 'Mean real-resample SD', 'Real-resample SD 95% range',
                 'Mean virtual-resample SD (six-table range)', 'Outer endpoints of six virtual SD 95% ranges']
    sdtable = '| ' + ' | '.join(sdcolumns) + ' |\n|' + '|'.join(['---'] * len(sdcolumns)) + '|\n'
    sdtable += '\n'.join('| ' + ' | '.join(row) + ' |' for row in sdrows)

    urban = df[(df.trait == 'bmi') & (df.contrast == 'urban_minus_pastoralist')]
    ur, uv = urban[urban.comparison == 'real_real'].iloc[0], urban[urban.comparison == 'virtual_real']
    virtual_means = est[(est.trait == 'bmi') & est.stream.str.startswith('LIFESTYLE_')].groupby('stream').urban_minus_pastoralist.mean()
    real_mean = est[(est.trait == 'bmi') & (est.stream == 'R_B')].urban_minus_pastoralist.mean()

    results = f'''# Matched-size scientific-use comparison

17 November 2026 · KDD Paper 1 · Completed existing-data evaluation

## Finding and decision

The strongest supported use in this case is reproducing the positive, age/sex-adjusted urban BMI contrasts at an approximately useful effect scale. Matching sample size and lifestyle-by-sex composition also places several urban lipid comparisons on a discrepancy scale similar to real–real sampling variation. This improves the interpretation of existing data quality; it does not improve the frozen generators themselves.

Two problems remain visible across the six saved tables: the rural–pastoralist lipid effects are too small, and both lipid distributions are underdispersed. Similar group contrasts therefore do not establish adequate individual variability. Close the planned P0 diagnostic with an analysis-specific use profile, retaining every prespecified contrast and diagnostic. No additional sampling, parameter change or new cohort is needed for this unit.

## What was compared

This is the source-rich Turkana lifestyle application already evaluated on 11 November, not a new target. Two independent Agent constructions supplied three saved seeded tables each (six tables, 1,226 complete rows per table). The measured reference has trait-specific available-case counts of 1,189 for BMI, 400 for total cholesterol, and 405 for HDL after the frozen adult/availability rule.

Each of 500 repetitions draws two independent real resamples and one resample from each saved virtual table, with replacement within six lifestyle-by-sex strata. For a given trait, all eight resamples have exactly the real available-case sample size and stratum counts. The virtual comparisons share the repetition's real B reference. Age and outcome distributions are not forced to match. These are independently drawn resamples of the same empirical real pool, not two independently recruited cohorts.

The original frozen analysis operator is used unchanged: age/sex-adjusted lifestyle comparisons from OLS. Its outcome-standardized coefficients are converted back to raw units using the same sample's SD. All nine pooled contrasts are reported. Standard deviations are necessary companion diagnostics. Original unmatched point estimates are retained in the complete CSV and HTML.

## Main results

For the urban–pastoralist BMI contrast, the six matched-resample mean effects are {span(virtual_means)} kg/m², compared with {real_mean:.3f} in real B resamples (original measured estimate {ur.original_real:.3f}). The real–real mean absolute discrepancy is {ur.absolute_mean:.3f} kg/m²; the six virtual–real values range from {span(uv.absolute_mean)}. This supports using these virtual cohorts to prototype and reproduce the principal urban BMI group comparison, with uncertainty about precision and other uses.

Total-cholesterol urban–pastoralist mean absolute discrepancies are 8.556–9.479 mg/dL, compared with 8.848 mg/dL for real–real. That is a materially less pessimistic assessment than judging the original point estimates alone. However, rural–pastoralist total-cholesterol effects remain lower by 7.800–9.545 mg/dL on average, and HDL effects by 4.074–6.208 mg/dL. Weak urban HDL comparisons are particularly uncertain: overlapping sampling ranges cannot establish the correct direction or equivalence.

The table below includes all nine contrasts. Ranges across virtual tables are descriptive, not independent-model confidence intervals. BMI uses kg/m²; both cholesterol outcomes use mg/dL. A signed difference is the first sample's adjusted contrast minus real B's adjusted contrast. The real–real range is an empirical sampling reference, not a pass threshold.

{full_table}

## Dispersion and the scope of scientific use

{sdtable}

For total cholesterol and HDL, even the largest upper endpoint of the six virtual-resample SD ranges is below the real-resample lower endpoint. Their shortfall therefore remains clear under this matched analysis. The last table column reports outer endpoints across six separate ranges, not a pooled interval.

| Intended analysis or use | What this unit supports |
|---|---|
| Age/sex-adjusted urban BMI group comparisons | Useful source-rich reconstruction/prototyping of the positive contrasts and approximate effect scale. |
| Urban total-cholesterol comparisons | Sampling-context agreement is encouraging, but small real urban groups and narrow virtual dispersion limit the inference. |
| Rural–pastoralist lipid comparisons | Not adequately reproduced: effects remain systematically too small in these saved tables. |
| Weak urban HDL contrasts | Uncertain; wide real–real variation is not evidence that the generated direction is correct. |
| Individual heterogeneity, variance-dependent precision or power calculations | Current lipid tables are insufficiently dispersed; these uses are not established. |
| Clinical equivalence, individual recovery or new-population transport | Not tested by this same-pool, source-rich diagnostic. |

The measured urban lipid groups contain only 37 participants for total cholesterol and 38 for HDL. Their wider real–real ranges make some urban discrepancies less distinguishable, but do not erase consistently weak rural effects. An underdispersed generator may also look favorable on an effect-only discrepancy, which is why the SD panel accompanies the contrast panel.

## Implementation and audit

- The scientific plan predates this run; the implementation, approved input bindings, invented-fixture checks and complete random-stream map were frozen before resampling. All 28 bound files remained unchanged.
- All 12,000 planned trait-sample evaluations completed: 3,000 real-resample fits and 9,000 virtual-resample fits. There were zero unavailable/failed slots and no replacement runs. Runtime for this execution was {run['elapsed_seconds']:.3f} seconds, excluding setup, rendering and review.
- The six wrapper tests passed before freezing. They cover units, immutability, cell matching, reproducibility, eligibility, non-computable fits and duplicate identifiers. They were not repeated after success.
- A separately implemented raw-outcome, centered-age QR regression reproduced 21 original trait fits and 72 preselected resampled fits. Across {review['numerical_fields_checked']} checked numerical fields, the maximum discrepancy was {review['max_abs_numeric_difference']:.3g}. This is an independent formula check by the root agent, not external statistical review.
- All 31,500 contrast differences and 900 aggregate summary fields were independently checked. All 28 v0.33 delivery files remained unchanged.
- No new Agent/API calls, downloads, generated cohorts or participant-level resample files were created. New API cost was $0. The 12,000 evaluations are computational repetitions, not 12,000 independent studies; evidence still comes from two constructions and one real study family.

## Interpretation limits

The empirical reference is an observed sample, not known population truth. The conditional bootstrap conditions on available cases, lifestyle/sex counts and the bound empirical pools. It omits household/site clustering, source-study estimation uncertainty, population transport and missingness uncertainty. Its central 95% ranges are neither cluster/survey-valid population intervals nor clinically meaningful equivalence margins. Sample size and composition were matched together, so changes from the unmatched result cannot be attributed solely to sample size. No tolerance or pass rate was selected after looking at the results.

This same-paper, previously exposed setting establishes a reconstruction use profile; it does not reset target exposure. Two authors with three saved seeds each do not provide six independent modeling decisions. Matching to the observed target composition is an evaluation standardization, not part of a newly blind generation protocol.

## Contribution to the KDD paper

Use this as evidence that generated-cohort usefulness must be evaluated through the requested scientific analyses and real sampling variation, with dispersion checked alongside effects. The positive result is a concrete use of final virtual data, not a new claim that feedback, more agents or this workflow outperform alternatives. The full nine-analysis profile belongs in the paper/supplement together; the urban BMI example can lead the narrative without suppressing the lipid limitations.

The planned next priority remains P1: verify original-paper-to-model capability on existing cases under the KDD-first plan. This unit launches no such experiment and makes no generator change. The supplied manuscript insertion is ready for the next reading edition; v0.33 is intact.

## Files

- [Offline visual report](report/index.html)
- [All nine scientific contrasts](figures/matched_scientific_contrasts.pdf) and [dispersion diagnostic](figures/matched_dispersion.pdf)
- [Manuscript insertion and figure captions](MANUSCRIPT_INSERT.md)
- [Complete contrast summaries](CONTRAST_SUMMARIES.csv) and [SD summaries](SD_SUMMARIES.csv)
- [Frozen protocol](PROTOCOL.md), [execution receipt](RUN_RESULT.json), [independent numerical review](INDEPENDENT_REVIEW.json)

Only aggregate estimates and original documentation appear in this report. Participant-level source and virtual tables remain in their existing local locations.
'''
    new_text(HERE / 'RESULTS.md', results)

    manuscript = f'''# Ready-to-integrate text: matched-size scientific-use evaluation

Prepared 17 November 2026. This insertion does not modify the frozen v0.33 reading edition. Numbers are bound to the completed matched-size unit, with all nine contrasts retained in its complete result table. Position it after the source-rich lifestyle application; describe it as an evaluation of final generated data, not an improvement to the generator or a prospective transport test.

## Methods

We contextualized virtual–real analysis discrepancies using matched-size real–real comparisons in the existing lifestyle case. For each trait, we drew 500 pairs of real bootstrap samples and 500 bootstrap samples from each of six frozen virtual tables, preserving the reference's six lifestyle-by-sex cell counts. Available-case sizes were 1,189 for BMI, 400 for total cholesterol and 405 for HDL cholesterol. All samples were evaluated using the same frozen age/sex-adjusted OLS operator; effects were expressed in original units. Each virtual comparison used the same real B resample as its corresponding real–real comparison. We report the complete signed and absolute difference profiles for all three pooled contrasts per trait, with sample SD as a companion diagnostic. No generator was revised. The conditional empirical ranges describe sampling variation within these fixed tables; they are not population-valid equivalence intervals.

## Results

At matched sample size and group composition, the virtual cohorts reproduced the principal urban BMI group comparisons at a useful approximate scale. For the urban–pastoralist contrast, matched-resample mean effects across the six virtual tables ranged from {span(virtual_means)} kg/m², compared with {real_mean:.3f} kg/m² in the real reference resamples. Mean absolute virtual–real discrepancies were {span(uv.absolute_mean)} kg/m², versus {ur.absolute_mean:.3f} kg/m² for real–real. Urban–pastoralist total-cholesterol discrepancies were also similar in scale (8.556–9.479 versus 8.848 mg/dL), although the small measured urban group limits precision. This did not extend to every analysis: rural–pastoralist effects remained lower by 7.800–9.545 mg/dL for total cholesterol and 4.074–6.208 mg/dL for HDL. Mean virtual-resample SDs were 31.486–32.674 and 14.496–14.889 mg/dL, respectively, compared with original measured-sample SDs of 42.811 and 20.228 mg/dL. Thus, selected group-comparison uses are supported more strongly than variance-dependent uses; agreement on a contrast is insufficient to establish adequate population heterogeneity.

## Figure caption: scientific contrasts

**Matched-size comparisons of scientific analyses.** Each panel shows one age/sex-adjusted lifestyle contrast, evaluated by the unchanged analysis operator. Gray rows compare two independently drawn real bootstrap samples; blue and purple rows compare each of the three saved tables from Agent authors A1 and A2 with the corresponding real B sample. All samples match the real trait-specific size and lifestyle-by-sex counts. Points denote medians, thick segments the middle 50%, and thin segments the middle 95% of 500 empirical difference estimates. The gray background band is the corresponding real–real 95% range. Zero indicates identical estimated contrasts. These bands provide conditional sampling context, not acceptance margins or population confidence intervals. All nine prespecified contrasts and all six saved tables are shown.

## Companion figure caption: dispersion

**Dispersion remains a separate requirement for scientific use.** Sample SD distributions use the same matched samples and show all six frozen virtual tables alongside real B. Points and segments have the same empirical-quantile interpretation as in the contrast figure. Dashed lines mark original measured-sample SDs. Total cholesterol and HDL remain underdispersed despite approximate agreement on some group contrasts. The two Agent authors are the independent modeling units; seeds and bootstrap samples are within-model repetitions.

## Editorial boundaries

- Lead with the useful urban BMI analysis and the actual effect scale; retain the complete contrast and SD profiles beside it.
- Call the study source-rich reconstruction on an exposed reference. The published source and measured reference belong to the same study family.
- Do not label overlap with the gray range as a pass rate, equivalence, validation of individual values, or new-population accuracy.
- Report 12,000 resampled trait evaluations, not 12,000 independent experiments or newly generated cohorts.
- Keep the existing method and target results frozen. This addition improves evaluation and interpretation only.
'''
    new_text(HERE / 'MANUSCRIPT_INSERT.md', manuscript)

    # The initial render receipt remains an immutable historical receipt. Preserve its HTML.
    report = HERE / 'report/index.html'
    old_html_bytes = report.read_bytes()
    old_html = old_html_bytes.decode('utf-8')
    assert 'id="findings"' not in old_html
    assert sha(report) == read('FIGURE_BINDINGS.json')['artifacts']['report/index.html']
    with (HERE / 'report/index.initial.html').open('xb') as f:
        f.write(old_html_bytes)
    finding = f'''<section class="card" id="findings"><h2>What these data can support</h2>
<p><b>The clearest supported use is the positive urban BMI group comparison.</b> Matching sample size and group composition also makes some urban lipid discrepancies comparable in scale to real–real sampling variation. Rural lipid relations and lipid dispersion still need improvement.</p>
<div class="scroll"><table><thead><tr><th>Scientific use</th><th>Result</th><th>Interpretation</th></tr></thead><tbody>
<tr><td>Urban − pastoralist BMI</td><td>Mean effects: {span(virtual_means)} virtual; {real_mean:.3f} real (kg/m²)</td><td>Useful approximate group-comparison scale</td></tr>
<tr><td>Urban − pastoralist total cholesterol</td><td>Mean absolute difference: 8.556–9.479 virtual–real; 8.848 real–real (mg/dL)</td><td>Encouraging sampling-context agreement; small urban reference</td></tr>
<tr><td>Rural − pastoralist lipid effects</td><td>Mean shortfall: TC 7.800–9.545; HDL 4.074–6.208 (mg/dL)</td><td>Persistent relation mismatch</td></tr>
<tr><td>Lipid variability</td><td>Mean virtual SD: TC 31.486–32.674; HDL 14.496–14.889 (mg/dL)</td><td>Lower than original measured SDs 42.811 and 20.228</td></tr>
</tbody></table></div><p class="note">The data need not be identical to be useful. Here, usefulness is specific to an analysis: approximate group effects do not establish accurate individual variability, power estimates or weak-effect directions.</p></section>
'''
    page = old_html.replace('<section class="card"><h2>How to read the comparison</h2>', finding + '<section class="card"><h2>How to read the comparison</h2>', 1)
    page = re.sub(r'<\?xml.*?\?>\s*', '', page, flags=re.S)
    page = re.sub(r'<!DOCTYPE svg.*?>\s*', '', page, flags=re.S)
    page = page.replace('<b>12,000</b> analyzed samples', '<b>12,000</b> resampled trait fits')
    page = page.replace('Independent raw-outcome QR replays and complete aggregate recomputation passed.',
                        'A separately implemented raw-outcome QR replay and complete aggregate recomputation passed; this is numerical review, not external expert review.')
    report.write_text(page, encoding='utf-8', newline='\n')

    focus_path = ROOT / 'docs/CURRENT_RESEARCH_FOCUS.md'
    focus_before_sha = sha(focus_path)
    focus_old = focus_path.read_text(encoding='utf-8')
    marker = '## Matched-size scientific-use comparison completed — 17 November 2026'
    assert marker not in focus_old
    block = f'''{marker}

The [matched-size P0 diagnostic](../work/matched_size_utility_2026-11-17/RESULTS.md) is complete: 500 repetitions, all nine adjusted lifestyle contrasts, six frozen virtual tables from two authors, 12,000 computed trait fits and zero failures. A separate QR implementation reproduced the original and prespecified sampled fits; v0.33 remains unchanged. [Offline figures and reading report](../work/matched_size_utility_2026-11-17/report/index.html).

Urban BMI contrasts have useful approximate scale (urban–pastoralist mean absolute discrepancy 0.314–0.428 kg/m², real–real 0.316). Some urban lipid comparisons are also similar to real–real sampling variation, but rural lipid effects and both lipid SDs remain too low. These empirical ranges are sampling context, not equivalence margins. This is the same exposed, source-rich Turkana case; no new family, API calls, generated tables or parameter changes. The [manuscript insertion](../work/matched_size_utility_2026-11-17/MANUSCRIPT_INSERT.md) is ready for the next edition. Next priority is P1 original-paper-to-model capability under the existing KDD plan; it has not started in this unit.

'''
    title, rest = focus_old.split('\n', 1)
    focus_new = title + '\n\n' + block + rest.lstrip('\n')
    focus_new = focus_new.replace("Next is the existing matched-size diagnostic's preflight and implementation review. This priority decision starts no new experiment and leaves v0.33 and frozen results unchanged.",
        'The matched-size diagnostic has now completed as described above. The original priority decision did not change v0.33 or frozen results.')
    focus_path.write_text(focus_new, encoding='utf-8', newline='\n')

    exposure_path = ROOT / 'docs/DATASET_EXPOSURE_REGISTRY.md'
    exposure_before_sha = sha(exposure_path)
    exposure_old = exposure_path.read_text(encoding='utf-8')
    marker2 = '## Turkana matched-size scientific-use diagnostic — 17 November 2026'
    assert marker2 not in exposure_old
    title, rest = exposure_old.split('\n', 1)
    exposure_note = f'''{marker2}

The user authorized [matched-size real–real and virtual–real comparisons](../work/matched_size_utility_2026-11-17/RESULTS.md) of the existing 11 November lifestyle case. All 500 repetitions of the three trait-specific, six-cell matched analyses completed. Nine previously exposed pooled lifestyle contrasts and three SD diagnostics were summarized; no new target family, outcomes or independent cohort was admitted. Six saved virtual tables and the original operator were unchanged. Reference composition was used only for explicitly documented evaluation standardization. No Agent saw new target feedback and no generator was revised. Bootstrap repetitions of the same empirical source do not reset exposure or supply prospective confirmation.

'''
    exposure_path.write_text(title + '\n\n' + exposure_note + rest.lstrip('\n'), encoding='utf-8', newline='\n')

    new_json(HERE / 'STATE.json', dict(
        status='complete', created_utc=datetime.now(timezone.utc).isoformat(),
        decision='close_P0_with_analysis_specific_scientific_use_profile',
        case='previously_exposed_source_rich_Turkana_lifestyle',
        agent_constructions=2, saved_virtual_tables=6, resamples_per_trait_stream=500,
        resampled_trait_fits=12000, failed_or_unavailable=0, original_verification_fits=21,
        independent_replay_fits=72, new_api_calls=0, new_api_cost_usd=0,
        new_data_downloads=0, new_generated_tables=0, individual_resamples_saved=False,
        generators_changed=False, v33_delivery_changed=False,
        next='P1 original-paper-to-model capability under existing KDD-first plan; not started here',
        authoritative_execution_receipt='RUN_RESULT.json',
        progress_note='PROGRESS.json is the final in-flight snapshot; RUN_RESULT.json and this state confirm completion',
        interpretation='conditional empirical sampling context; not equivalence or prospective confirmation'))

    # Delivery-only checks: do not repeat fitting, bootstrap sampling, or passed tests.
    link_targets = re.findall(r'href="([^"]+)"', page)
    local_targets = [v for v in link_targets if not re.match(r'^(https?:|#|data:)', v)]
    assert all((report.parent / v).resolve().is_file() for v in local_targets)
    assert page.count('<svg') == 2 and '<?xml' not in page and '<!DOCTYPE svg' not in page
    assert page.count('id="findings"') == 1
    for name, expected in read('SUMMARY_RECEIPT.json')['files'].items():
        assert sha(HERE / name) == expected
    initial = read('FIGURE_BINDINGS.json')
    for name, expected in initial['artifacts'].items():
        if name != 'report/index.html':
            assert sha(HERE / name) == expected
    assert sha(HERE / 'report/index.initial.html') == initial['artifacts']['report/index.html']
    assert sha(HERE / 'ESTIMATES.csv') == run['estimate_sha256']
    delivered = ['RESULTS.md', 'MANUSCRIPT_INSERT.md', 'STATE.json', 'report/index.html',
                 'report/index.initial.html', 'finalize_report.py']
    new_json(HERE / 'DELIVERY_QA.json', dict(
        status='pass', created_utc=datetime.now(timezone.utc).isoformat(),
        checks={'completed_trait_fits':12000, 'complete_contrast_summary_rows':63,
                'complete_sd_summary_rows':24, 'contrast_figure_panels':9, 'sd_figure_panels':3,
                'embedded_svg_count':2, 'html_local_links_resolve':True,
                'initial_html_preserved':True, 'estimate_and_summary_hashes_unchanged':True,
                'initial_figure_hashes_unchanged':True, 'final_html_has_actual_findings':True},
        visual_inspection='Both final PNG figures inspected; all panels/rows readable without clipping',
        html_browser_inspection='Not performed; offline structure, SVG embedding and links checked',
        numeric_review='INDEPENDENT_REVIEW.json',
        initial_render_receipt='FIGURE_BINDINGS.json; its initial HTML is preserved as report/index.initial.html',
        artifacts={n:sha(HERE/n) for n in delivered},
        living_documents={str(p.relative_to(ROOT)): {'before_sha256': before,
                          'after_file_sha256':sha(p)}
                          for p,before in [(focus_path,focus_before_sha),(exposure_path,exposure_before_sha)]}))
    print(json.dumps({'status':'complete', 'results':'RESULTS.md', 'html':'report/index.html',
                      'manuscript_insert':'MANUSCRIPT_INSERT.md', 'delivery_qa':'pass'}))

if __name__ == '__main__':
    main()
