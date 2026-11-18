"""Write bounded scientific interpretation from the complete aggregate record."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
j=json.loads((R/'PRIMARY_SUMMARY.json').read_text())
review=json.loads((R/'review/INDEPENDENT_NUMERICAL_REVIEW.json').read_text())
labels={'bmi':'BMI','total_cholesterol':'TC','hdl_cholesterol':'HDL'}
rows=[]
for x in j['summary']:
    vals=[x['constructors'][ep]['estimate']['mean'] for ep in ['LIFESTYLE_A1','LIFESTYLE_A2']]
    rows.append(f"| {labels[x['trait']]} | {x['contrast'].replace('_',' ')} | {x['estimate']:.3f} [{x['lower']:.3f}, {x['upper']:.3f}] | {vals[0]:.3f} | {vals[1]:.3f} |")
text='''# Lifestyle application: real and Agent-generated data in the same analysis

11 November 2026. Completed new whole-cohort generation, final-data comparison and independent recomputation. [Interactive report](report/index.html), [all 189 contrasts](ANALYSIS_CONTRASTS.csv), [frozen protocol](PROTOCOL.md).

## Decision

This is a useful, bounded application result for the project's mainline. Two fresh GPT Agents constructed lifestyle-labelled virtual cohorts from permitted published evidence and their own additional literature searches. The generated tables preserve the central urban BMI contrast and urban-versus-pastoralist TC elevation when passed through the same analysis as the released real data. They do not preserve every group difference or the full biomarker variability. Keep this as evidence-to-data reconstruction with scientific-use evaluation, not independent target confirmation, workflow superiority, equivalence, or proof that the whole published study was reproduced.

## What was actually done

1. Audited Lea et al., Science Advances2020 (DOI10.1126/sciadv.abb1430), its available Methods and publication tables. Retained source inconsistencies and the failure to recover supplemental spreadsheets S1/S2. No source numbers were fabricated from inaccessible files.
2. Froze the visible scientific request, seven-column output contract, information policy, resources and shared evaluator. Original published findings were legal input. New real lifestyle fits and old project generators were not given to the authors. No root-authored relationship parameters or expected numerical coefficients were supplied.
3. Ran two independent fresh contexts using gpt-6.1-sol/high/default. Each made two explicit literature_search calls, read the original study and chose a different additional paper, submitted one candidate, ran one generated-only diagnostic trial, and retained that candidate. A1 had11 read_source calls (including index/section retrieval), A2 had10 including an explicit source-version retry; these are tool reads, not independent papers. Total API calls31; recorded tariff estimate USD0.3746075, zero unknown-usage calls. No further model call occurred after finalization.
4. Both authors chose conditional-mean models with lifestyle, age and sex terms; bounded age distributions; correlated lognormal innovations; and TC=HDL+positive non-HDL. They independently chose how to rescale the inconsistent printed demographic cells to the requested1226 rows. Some BMI parameters were algebraically derived from published descriptive percentage differences; many conditional effects, dispersion and dependence terms remained explicit assumptions. Published marginal summaries were not silently called adjusted coefficients. The programs/specifications match the original API submission bytes; the host did not rewrite their scientific structure.
5. Closed both histories and generated all three predeclared final seeds per selected law: six successful complete tables, each1226 rows. There were no missing generated cells, excluded18-year-olds or HDL>TC rows. There was no target-informed revision or reselection. Inspection found finite first/second moments in these fixed laws; that does not certify the assumed scientific parameters.
6. Applied the same frozen age/sex-adjusted lifestyle operator to the released real data and every generated table. All7 datasets yielded all27 predefined contrasts and3 interaction tests, giving189 contrasts and21 LRT results. A separate implementation independently recomputed them.

## Complete primary results

Effects below are outcome SD units, scaled separately within each dataset as specified by the source procedure. Author columns are means of three final draws, not additional independent authors. The reference column includes its classical95% OLS t interval. All nine contrasts are retained, without a post-hoc quality threshold.

| Outcome | Adjusted contrast | Real reference [95% CI] | A1 mean | A2 mean |
|---|---|---:|---:|---:|
'''+ '\n'.join(rows)+'''

## Scientific interpretation

- **BMI urban pattern is preserved.** Urban-minus-pastoralist BMI is1.882kg/m² [1.368,2.397] in the real reference; six generated draws span1.700–2.251kg/m². The standardized effect is0.666 in the reference versus0.672–0.844 across draws. Urban-minus-rural is also positive in all six draws. These descriptive findings support this specific downstream use; the group differences were already discussed in the permitted source paper.
- **TC urban-versus-pastoralist direction and standardized scale are similar, but raw magnitude remains lower.** Reference0.475SD, A1mean0.451, A2mean0.496. In mg/dL the reference is20.342, whereas generated draws span13.732–18.907. Standardization alone would hide part of this discrepancy because virtual TC SD is31.85–34.06 versus42.81 in the real sample.
- **Rural blood-lipid relationships are not reconstructed well.** Rural-minus-pastoralist TC is9.493mg/dL in the reference versus−0.695 to1.943 in the draws. The analogous HDL difference is4.446mg/dL versus−1.833 to0.015. The real intervals are wide and nearly include zero; this prevents a strong population-effect claim but does not erase the observed discrepancy. Agent-assumed near-zero differences should not be called evidence of biological equivalence.
- **HDL is a partial-use result.** The reference's three additive95% intervals include zero. Five of six generated tables likewise have all three nominal intervals include zero; A1 seed64001 instead detects an urban-minus-rural HDL contrast and selects a sex-specific branch (LRTp0.02457). All corresponding sex-specific outputs remain available. The actual reference has no detected interaction for any of the three traits. Virtual HDL SD14.39–15.10 is below the reference20.23.

## How to read the figures

In [the standardized plot](report/lifestyle_contrasts_standardized.png), navy diamonds/lines are the real sample estimate/95%CI. Purple/orange points are A1/A2 final draws; their connecting ranges are Monte Carlo variation, not confidence intervals. Each row is one fixed comparison and each panel one biomarker. The [raw-unit plot](report/lifestyle_contrasts_raw.png) uses the identical fits transformed back into kg/m² or mg/dL, making scale differences visible. CI overlap is not an equivalence test.

The real deposit has1226 rows; the frozen age>18 rule excludes9. Trait-specific available-case counts areBMI1189, TC400, HDL405. Virtual measurements are complete, so each trait has1226. Smaller virtual p-values can arise from this larger usable n and smaller generated variability; they are not independent clinical evidence or a quality score. No new missingness simulator was introduced merely to reproduce p-values.

## Implementation verification and limits

- Independent numerical review:5846 checks,4690 numerical comparisons, maximum absolute difference8.52e-13; code, original reference, frozen candidates and sampled input hashes unchanged. See [review receipt](review/INDEPENDENT_NUMERICAL_REVIEW.json).
- The analytical core passed six invented-fixture tests; runtime passed seven mocked boundary tests; a separate LRT fixture matched statsmodels. These were not rerun without need. Independent fixed-law review checked mathematical support, physiological construction and actual submission provenance. A minor rural-BMI derivation transcription difference is recorded for A1; a later reviewer attribution correction is preserved separately, with no change to the model or outcomes.
- Original author code was unavailable. The study Methods were reimplemented with explicit choices: one3-category fit, full-covariance pairwise contrasts, trait-specific pooled scaling, Gaussian ML interaction LRT. Pilot BH9 is not the paper's11-outcome FDR family. This is not a claim to reproduce the entire original paper.
- Original-study findings were allowed inputs, this target family had historical exposure, and the new fit is another analysis of a released sample rather than a known population truth. Do not label the result unseen-target validation.
- Two authors on one model do not establish broad repeatability or comparative superiority. Three seeds measure conditional sampling variability only. The generator law and source evidence have additional uncertainty not represented by the generated OLS intervals.
- The optional feedback opportunity produced two retain decisions. The experiment supports delivered-data use, not a feedback-improvement claim.
- A pre-API documentation race was caught by the integrity gate. Both rejected launches occurred before credential loading or payment. Original receipts are preserved under launch_attempt_01; stable reviewed inputs were rebound before the31 actual calls. Scientific settings and budgets did not change.

## Next decision

Integrate this bounded source-rich application alongside the earlier request-only and fixed-evidence studies, keeping their information settings separate. The concrete capability is that an Agent can construct all seven variables, including meaningful lifestyle groups, and support a recognizable adjusted biomedical analysis with the generated data. Do not tune these laws against the now revealed reference. If a later method revision targets weak group-specific lipid magnitudes or spread, define the source-evidence improvement and evaluation purpose first; retain this completed result as its historical record. No broader batch, new data collection, new model or third constructor is launched by this unit.

Raw and generated individual rows, complete retrieved sources and API payloads remain local. The HTML/plots contain aggregate results only. No GitHub synchronization was performed in this unit. Scientific PNGs were visually inspected; whole-page browser rendering is not claimed.
'''
(R/'RESULTS.md').write_text(text,encoding='utf-8')
insert='''# Proposed manuscript addition: source-guided lifestyle analysis

Placement: application study after the request-only construction results. Preserve the distinct information setting; this is not another independent validation cohort. Existing manuscript v0.30 is not overwritten by this insert.

**A common biomedical analysis on real and generated cohorts.** To evaluate direct scientific use, we asked two fresh GPT Agents to construct complete fictional cohorts containing age, sex, lifestyle category, BMI, total cholesterol and HDL cholesterol. Both received the study citation and approved published aggregate evidence from Lea et al.2020 and could retrieve additional literature. Each independently authored and tested one generator and retained it. After closing both construction histories, we sampled three predeclared seeds per law. The reference data and all six virtual tables were passed to the same Methods-guided analysis: standardized outcomes regressed on three-level lifestyle, age and sex, with all pairwise contrasts and a predeclared sex-interaction check retained. This is source-rich reconstruction; published results were legitimate inputs, whereas the newly computed reference fits were unavailable during construction.

The generated cohorts preserved the central urban BMI and urban-versus-pastoralist total-cholesterol patterns. The adjusted BMI contrast was1.882kg/m² in the real reference and1.700–2.251 across the six draws. The standardized total-cholesterol contrast was0.475 in the reference, compared with three-draw means0.451 and0.496 for the two constructions. However, lower virtual biomarker variability partly masked raw-scale differences: the TC contrast was20.342mg/dL in the reference versus13.732–18.907 in the virtual tables. Rural-versus-pastoralist lipid contrasts were attenuated or reversed, and one HDL draw selected a sex-specific interaction absent in the real reference analysis. Thus, the same generated data supported recognizable adjusted analyses while retaining analysis-specific limitations, rather than reproducing every result.

The real available-case sample sizes were1189 for BMI,400 for TC and405 for HDL, versus1226 complete virtual records per trait. Reported virtual regression intervals are conditional on the selected law and simulated row count, and exclude uncertainty in evidence and model choice. We therefore compare direction, raw and standardized magnitude, and branch behavior rather than interpreting a smaller virtual p-value as better scientific validity. All189 contrasts and21 interaction tests were independently recomputed with maximum absolute numerical difference8.52e-13. Original author code and full supplemental numerical tables were unavailable; the explicit reimplementation choices and complete results are retained in the supplement.

**Figure proposal.** Three panels show all nine age/sex-adjusted group contrasts, with real estimates/95% intervals and the three draws for each author. A second view in raw units demonstrates the effect of differing outcome scales. Connecting virtual points denotes draw range, not confidence intervals. Keep all nine contrasts and the HDL interaction exception visible.

**Contribution supported.** Published evidence can be converted by an Agent into a whole-cohort joint generator whose data support a concrete biomedical application. This case does not identify an advantage from review, multiple Agents, or the workflow over ordinary generation, and does not establish equivalence or target-population validity.
'''
(R/'MANUSCRIPT_INSERT.md').write_text(insert,encoding='utf-8')
print('Complete results and proposed manuscript insert written from aggregate data')
