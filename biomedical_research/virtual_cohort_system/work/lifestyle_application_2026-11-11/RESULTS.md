# Lifestyle application: real and Agent-generated data in the same analysis

11 November 2026. Completed new whole-cohort generation, final-data comparison and independent recomputation. [Interactive report](report/index.html), [all 189 contrasts](ANALYSIS_CONTRASTS.csv), [frozen protocol](PROTOCOL.md).

## Decision

This is a useful, bounded application result for the project's mainline. Two fresh GPT Agents constructed lifestyle-labelled virtual cohorts from permitted published evidence and their own additional literature searches. The generated tables preserve the central urban BMI contrast and urban-versus-pastoralist TC elevation when passed through the same analysis as the released real data. They do not preserve every group difference or the full biomarker variability. Keep this as evidence-to-data reconstruction with scientific-use evaluation, not independent target confirmation, workflow superiority, equivalence, or proof that the whole published study was reproduced.

## What was actually done

1. Audited Lea et al., Science Advances 2020 (DOI 10.1126/sciadv.abb1430), its available Methods and publication tables. Retained source inconsistencies and the failure to recover supplemental spreadsheets S1/S2. No source numbers were fabricated from inaccessible files.
2. Froze the visible scientific request, seven-column output contract, information policy, resources and shared evaluator. Original published findings were legal input. New real lifestyle fits and old project generators were not given to the authors. No root-authored relationship parameters or expected numerical coefficients were supplied.
3. Ran two independent fresh contexts using gpt-6.1-sol/high/default. Each made two explicit literature_search calls, read the original study and chose a different additional paper, submitted one candidate, ran one generated-only diagnostic trial, and retained that candidate. A1 had 11 read_source calls (including index/section retrieval), A2 had 10 including an explicit source-version retry; these are tool reads, not independent papers. Total API calls 31; recorded tariff estimate USD 0.3746075, zero unknown-usage calls. No further model call occurred after finalization.
4. Both authors chose conditional-mean models with lifestyle, age and sex terms; bounded age distributions; correlated lognormal innovations; and TC=HDL+positive non-HDL. They independently chose how to rescale the inconsistent printed demographic cells to the requested 1226 rows. Some BMI parameters were algebraically derived from published descriptive percentage differences; many conditional effects, dispersion and dependence terms remained explicit assumptions. Published marginal summaries were not silently called adjusted coefficients. The program text matches the original submission, and model specifications preserve the submitted values; the host did not rewrite their scientific structure.
5. Closed both histories and generated all three predeclared final seeds per selected law: six successful complete tables, each 1226 rows. There were no missing generated cells, excluded 18-year-olds or HDL>TC rows. There was no target-informed revision or reselection. Inspection found finite first/second moments in these fixed laws; that does not certify the assumed scientific parameters.
6. Applied the same frozen age/sex-adjusted lifestyle operator to the released real data and every generated table. All 7 datasets yielded all 27 predefined contrasts and 3 interaction tests, giving 189 contrasts and 21 LRT results. A separate implementation independently recomputed them.

## Complete primary results

Effects below are outcome SD units, scaled separately within each dataset under the declared Methods-guided reimplementation. Author columns are means of three final draws, not additional independent authors. The reference column includes its classical 95% OLS t interval. All nine contrasts are retained, without a post-hoc quality threshold.

| Outcome | Adjusted contrast | Real reference [95% CI] | A1 mean | A2 mean |
|---|---|---:|---:|---:|
| BMI | rural minus pastoralist | 0.086 [-0.061, 0.232] | 0.047 | 0.063 |
| BMI | urban minus pastoralist | 0.666 [0.484, 0.848] | 0.746 | 0.779 |
| BMI | urban minus rural | 0.580 [0.434, 0.726] | 0.699 | 0.715 |
| TC | rural minus pastoralist | 0.222 [-0.009, 0.452] | 0.032 | 0.026 |
| TC | urban minus pastoralist | 0.475 [0.104, 0.846] | 0.451 | 0.496 |
| TC | urban minus rural | 0.253 [-0.077, 0.584] | 0.420 | 0.470 |
| HDL | rural minus pastoralist | 0.220 [-0.003, 0.443] | -0.053 | -0.062 |
| HDL | urban minus pastoralist | 0.087 [-0.271, 0.444] | -0.007 | -0.031 |
| HDL | urban minus rural | -0.133 [-0.452, 0.186] | 0.046 | 0.031 |

## Scientific interpretation

- **BMI urban pattern is preserved.** Urban-minus-pastoralist BMI is 1.882 kg/m² [1.368, 2.397] in the real reference; six generated draws span 1.700–2.251 kg/m². The standardized effect is 0.666 in the reference versus 0.672–0.844 across draws. Urban-minus-rural is also positive in all six draws. These descriptive findings support this specific downstream use; the group differences were already discussed in the permitted source paper.
- **TC urban-versus-pastoralist direction and standardized scale are similar, but raw magnitude remains lower.** Reference 0.475 SD, A1 mean 0.451, A2 mean 0.496. In mg/dL the reference is 20.342, whereas generated draws span 13.732–18.907. Standardization alone would hide part of this discrepancy because virtual TC SD is 31.85–34.06 versus 42.81 in the real sample.
- **Rural blood-lipid relationships are not reconstructed well.** Rural-minus-pastoralist TC is 9.493 mg/dL in the reference versus −0.695 to 1.943 in the draws. The analogous HDL difference is 4.446 mg/dL versus −1.833 to 0.015. The real intervals are wide and include zero near their lower bounds; this prevents a strong population-effect claim but does not erase the observed discrepancy. Agent-assumed near-zero differences should not be called evidence of biological equivalence.
- **HDL is a partial-use result.** The reference's three additive 95% intervals include zero. Five of six generated tables likewise have all three nominal intervals include zero; A1 seed 64001 instead detects an urban-minus-rural HDL contrast and selects a sex-specific branch (LRT p=0.02457). All corresponding sex-specific outputs remain available. The actual reference has no detected interaction for any of the three traits. Virtual HDL SD 14.40–15.10 is below the reference 20.23.

## How to read the figures

In [the standardized plot](report/lifestyle_contrasts_standardized.png), navy diamonds/lines are the real sample estimate/95% CI. Purple/orange points are A1/A2 final draws; their connecting ranges are Monte Carlo variation, not confidence intervals. Each row is one fixed comparison and each panel one biomarker. The [raw-unit plot](report/lifestyle_contrasts_raw.png) uses the identical fits transformed back into kg/m² or mg/dL, making scale differences visible. CI overlap is not an equivalence test.

The real deposit has 1226 rows; the frozen age>18 rule excludes 9. Trait-specific available-case counts are BMI 1189, TC 400, HDL 405. Virtual measurements are complete, so each trait has 1226. Smaller virtual p-values can arise from this larger usable n and smaller generated variability; they are not independent clinical evidence or a quality score. No new missingness simulator was introduced merely to reproduce p-values.

## Implementation verification and limits

- Independent numerical review: 5846 checks, 4690 numerical comparisons, maximum absolute difference 8.52e-13; code, original reference, frozen candidates and sampled input hashes unchanged. See [review receipt](review/INDEPENDENT_NUMERICAL_REVIEW.json).
- The analytical core passed six invented-fixture tests; runtime passed seven mocked boundary tests; a separate LRT fixture matched statsmodels. These were not rerun without need. Independent fixed-law review checked mathematical support, physiological construction and actual submission provenance. A minor rural-BMI derivation transcription difference is recorded for A1; a later reviewer attribution correction is preserved separately, with no change to the model or outcomes.
- Original author code was unavailable. The study Methods were reimplemented with explicit choices: one 3-category fit, full-covariance pairwise contrasts, trait-specific pooled scaling, Gaussian ML interaction LRT. Pilot BH9 is not the paper's 11-outcome FDR family. This is not a claim to reproduce the entire original paper.
- Original-study findings were allowed inputs, this target family had historical exposure, and the new fit is another analysis of a released sample rather than a known population truth. Do not label the result unseen-target validation.
- Two authors on one model do not establish broad repeatability or comparative superiority. Three seeds measure conditional sampling variability only. The generator law and source evidence have additional uncertainty not represented by the generated OLS intervals.
- The optional feedback opportunity produced two retain decisions. The experiment supports delivered-data use, not a feedback-improvement claim.
- A pre-API documentation race was caught by the integrity gate. Both rejected launches occurred before credential loading or payment. Original receipts are preserved under launch_attempt_01; stable reviewed inputs were rebound before the 31 actual calls. Scientific settings and budgets did not change.

## Next decision

Integrate this bounded source-rich application alongside the earlier request-only and fixed-evidence studies, keeping their information settings separate. The concrete capability is that an Agent can construct all seven variables, including meaningful lifestyle groups, and support a recognizable adjusted biomedical analysis with the generated data. Do not tune these laws against the now revealed reference. If a later method revision targets weak group-specific lipid magnitudes or spread, define the source-evidence improvement and evaluation purpose first; retain this completed result as its historical record. No broader batch, new data collection, new model or third constructor is launched by this unit.

Raw and generated individual rows, complete retrieved sources and API payloads remain local. The HTML/plots contain aggregate results only. No GitHub synchronization was performed in this unit. Scientific PNGs were visually inspected; whole-page browser rendering is not claimed.
