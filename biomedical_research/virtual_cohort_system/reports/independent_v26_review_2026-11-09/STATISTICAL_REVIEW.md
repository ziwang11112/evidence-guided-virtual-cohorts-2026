# Independent statistical and scientific-use review of v0.26

Reviewed 9 November 2026. Manuscript: `manuscript/DRAFT_v0_26.md` (542 physical lines). I read the methods, results and S1–S15 before consulting linked experimental reports, protocols and aggregate tables. I did not consult earlier review judgments, open participant or generated row tables, refit a participant analysis, generate cohorts, or tune a model. The only new calculation was the explicitly post hoc, aggregate-only Q1 robustness check reproduced below. Paths below are relative to the project root `biomedical_research/virtual_cohort_system`.

## Overall judgment

The numerical results support a useful methods demonstration: agents can turn external evidence and a specified analysis request into executable joint models, and some resulting point estimates and multivariable patterns agree with selected reference samples. They also support a descriptive information contrast: the sampled E1 construction arms have lower mean absolute error on five of six Q1 endpoints. The paper does not establish that an investigator can obtain a sufficiently accurate new scientific answer, or calibrated uncertainty for that answer, when the target records are unavailable.

Most of the obvious statistical objections have already been handled responsibly. The manuscript distinguishes constructions from seeds, preserves unfavorable endpoints, discloses reference exposure, avoids treating confidence-band overlap as equivalence, and does not claim universal comparator superiority or a demonstrated feedback benefit. I found no material arithmetic contradiction in the numerical quantities traced. The important remaining problems are claim scope, consequences of the observed errors for actual use, and enough design detail to interpret the references. These are mostly writing remedies for a developmental methods paper. A stronger prospective utility claim would require a genuinely new confirmation, not more seeds on these laws.

A defensible headline would be: **“The workflow repeatedly produced executable cohorts with partial agreement on prespecified regression point estimates and adjustment patterns; additional relationship evidence was associated with smaller errors in five of six sampled developmental comparisons. Reliable inference for a new population remains unestablished.”**

## Prioritized findings

### 1. Major: “scientific utility” needs a specified use and an accuracy claim of matching strength

**Locations:** abstract line 7; lines 13–17, 105, 133–137, 185, 273. Numerical evidence: lines 315–326, 373–377, 398–406.

The text moves between three different achievements: an analysis executes; its point direction or adjustment pattern agrees; its magnitude is accurate enough to support a scientific decision. The first two are demonstrated, while the third is asserted through “useful associations,” “supports a specified analysis,” and “analysis-specific use” without identifying the decision or an acceptable discrepancy. This is consequential, rather than merely terminology. In Q4, CHNS age means are approximately 62% and 31% below the reference, ENSANUT age means approximately 37% and 30% above it, and E01's glucose-adjusted BMI mean approximately 33% above it. These are deviations from uncertain sample estimates, not known population biases; nevertheless they are substantial relative to the displayed reference uncertainty. For example, both CHNS age seed ranges remain below the CHNS reference interval, and both ENSANUT age ranges exceed the empirical stability band. These comparisons are descriptive, not a new pass/fail rule.

The observed attenuation is a real result but does not resolve this gap. E01's BMI reduction is about 0.01656 pp per 5 kg/m² versus 0.02701 in the reference; E02's is about 0.02407. Thus the qualitative pattern survives while its size differs. Q5 is more striking: all lipid signs match, yet HDL slopes are roughly half the reference magnitude and the residual correlation is 0.108–0.141 versus 0.512. Those tables could support a code demonstration or an assumption-based scenario, but agreement of signs alone is weak evidence for quantitative lipid research.

**Artifacts checked:** `work/core_workflow_replication_2026-11-04/display/PRIMARY_SUMMARY.csv`; `work/core_workflow_replication_2026-11-04/display/DIAGNOSTIC_SUMMARY.csv`; Q5 Table S5 and `work/evidence_use_cross_task_2026-11-05/evaluation/ALL_ENDPOINTS.csv` as the manuscript's complete-result pointer.

**Strongest counterargument:** The authors deliberately avoid inventing retrospective equivalence margins, give the actual numbers, and make no universal validity claim. A methods paper can report partial quantitative agreement without a formal acceptance rule. This is correct. I am not asking for a post hoc cutoff, a global quality score, or agreement on every statistic.

**Minimal remedy — writing:** Define “support” explicitly as successful execution and the reported point-estimate/association properties. State the demonstrated uses as scenario exploration, analysis prototyping, and reconstruction where inputs identify the relevant relationship. Replace unqualified utility assertions with the particular property established. If practical quantitative research use is central, identify the scientific decision and explain why the observed discrepancy would not change it; the present data do not establish that proposition by themselves.

**New confirmation only for the stronger claim:** Prespecify one concrete downstream scientific decision or estimand with a domain-justified tolerance on a reference not used to develop/select the workflow. More generated rows or seeds cannot establish that accuracy.

### 2. Major: the limitation on inference is stronger than the limitation on individual variability

**Locations:** lines 13, 105–107, 137, 171, 195; S3 line 309; S5 lines 377–381; S6 line 434.

The manuscript correctly explains that seeds do not capture source, model or transfer uncertainty. However, the practical implication is not carried into the advertised use of “ordinary regression.” The regression coefficient is only part of an inferential analysis. Synthetic standard errors, confidence intervals, tests and power calculations conditional on one authored law would not automatically quantify uncertainty about the target scientific effect. Increasing the synthetic sample size could make these intervals arbitrarily narrow while the source information is unchanged.

The observed dispersion errors affect this issue directly, not only studies of tails or individual heterogeneity. Q4 ENSANUT residual RMS values are 0.2950 and 0.3238 versus 0.4885, about 40% and 34% low. Q5 H03 has residual RMS 0.3006 versus 0.4885 despite its close conditional BMI coefficient. These facts do not permit a numerical claim about the standard-error ratio, because predictor distributions and weighting also differ. They do establish that a close slope cannot be read as validation of inferential precision. The existing CHNS diagnostics reinforce the issue: C02's HbA1c SD is close to the reference (0.9435 versus 0.9536), but its glucose–HbA1c Pearson/Spearman correlations are 0.8375/0.7686 versus 0.6610/0.3615. Correcting or matching marginal variance alone would not certify the joint model.

**Artifacts checked:** Q4 `display/DIAGNOSTIC_SUMMARY.csv`; manuscript Table S5/Figure S2 and S6 interval caption. No source-uncertainty propagation was claimed or supplied in these artifacts.

**Strongest counterargument:** Lines 107 and 434 already state the uncertainty distinction, and main figures use seed ranges rather than misleading synthetic confidence intervals. This is an acknowledged limitation, not an undisclosed statistical error.

**Minimal remedy — writing:** Add the consequence next to the intended-use description: the reported validation concerns selected point estimates and patterns, not calibrated tests, confidence intervals, power or patient-level prediction. Explain in line 171 that underdispersion also limits inferential use. This requires no new analyses. A short table separating “demonstrated point property” from “unvalidated inferential use” would help more than another generic disclaimer.

**New work only if inferential utility is claimed:** A method for source/structural/transport uncertainty and a coverage or decision-error assessment would be needed. Three-seed ranges, more independently sampled rows, and between-author spread alone are not substitutes.

### 3. Major for stronger claims, otherwise a framing issue: retrospective local agreement is not a prospective selection or reliability result

**Locations:** abstract line 7; lines 127, 141, 157–165, 177, 185, 191, 195; S3 lines 299–309; S7 lines 442–459.

The paper's evidence hierarchy should determine the headline. Q1–Q5 reuse exposed project references; fresh author contexts and sealed final deliveries protect against direct post-generation changes but do not erase development-stage choices about cases, packets, analyses, or the version of the method emphasized. The earlier prospective gate failed in both cases. The iron study sealed new biomarker access but both laws missed its primary odds-ratio comparison: 4.835–6.565 versus 17.79, with every delivered value below the reference lower confidence limit of 9.28.

The favorable iron secondary results belong to different laws: A is closer for joint prevalence and B for continuous ranks. That is informative evidence that usefulness depends on the endpoint; it does not demonstrate that one cohort is jointly adequate for all three uses. It also does not establish a way to choose the better law before seeing target outcomes. The latter is only a problem if the paper implies prospective deployment reliability. A retrospective claim about analysis-specific outcomes does **not** require an oracle selection procedure or a single universal winner.

**Artifacts checked:** Q4 `PROTOCOL.json` and `RESULTS.md` (explicit developmental purpose and prior reviewer/coordinator exposure); `work/iron_breadth_2026-11-05/PROTOCOL.md` and `RESULTS.md`; manuscript S7 and the linked `work/scaleup_2026-11-01/production_release/CLAIM_LOCK.md` as the frozen decision pointer. No allegation of leakage or hidden tuning follows from exposure alone.

**Strongest counterargument:** The manuscript labels developmental exposure and the prospective failures repeatedly, and does not explicitly claim a rule that predicts reliability without target comparison. That disclosure substantially reduces the concern. The question is whether the remaining abstract/discussion language still asks those results to establish more than retrospective partial agreement.

**Minimal remedy — writing:** Make the hierarchy explicit in the abstract's conclusion: developmental partial agreement plus informative sealed failure, with prospective reliability unresolved. Preserve the iron result as a scientifically useful contrast rather than describing its selected secondary closeness as general validation of iron-cohort use. Do not pool study or seed counts into a success rate.

**New confirmation only if needed:** If the authors want to claim reliable target-free use, evaluate a frozen construction procedure on genuinely new target analyses with a prespecified rule for evaluating or selecting its output. Re-running these exposed references, adding seeds, or testing a renamed controller on the same participants would not answer that question.

### 4. Moderate: essential target eligibility and reference estimands are too compressed for a standalone methods paper

**Locations:** Table 3 lines 117–125; line 127; lines 161, 367, 440–442, 477.

The reader gets age ranges and sample sizes for the lead glycemia cases but not the restrictions that materially determine the regression targets. The retained ENSANUT binding includes fasting/diagnosis and original anthropometry restrictions, positive-value selection, glucose below 126 mg/dL, and exactly equal weights for eight age-by-sex cells. The manuscript mentions equal-cell weighting but leaves most eligibility details in linked historical artifacts. Calling this “ENSANUT” or a population request without a compact complete estimand definition makes the age/glucose/BMI comparisons harder to interpret; these are not ordinary nationally weighted population regressions. CHNS is an unweighted selected analytical sample, while the lipid reference has only 397 participants and an uncertain TC direction; those facts matter more than the much larger count of synthetic rows.

**Artifacts checked:** `work/main_study_freeze_2026-11-03/cases/ENSANUT2018/README.md`, `case_card.json`, `reference_aggregate_binding.json`; manuscript S5/S7; `work/autonomous_research_cycle2_2026-10-31/analysis/analytical_engine.py` and its saved aggregate schema through targeted text inspection. The ENSANUT stability procedure had 399 valid attempts out of 399; it is correctly not advertised as a national confidence interval.

**Strongest counterargument:** The full protocols and earlier extended manuscript are linked, and exact reference values are honestly described as selected-sample estimates. This is a reporting-completeness issue, not evidence that the actual analyses used the wrong population or weights.

**Minimal remedy — writing from existing artifacts:** Add one compact reference-definition table or paragraph: eligibility, complete-case restrictions, sample size, target weighting/standardization, model formula and interval method for each reference. Include all eight ENSANUT cells and its glucose/fasting/diagnosis restrictions. State explicitly that cross-case results address distinct estimands rather than country-level comparisons. No participant refit is needed.

### 5. Moderate: retain real–real context, but make its algebraic asymmetry explicit

**Locations:** lines 143, 430, 436.

The manuscript correctly says this comparison concerns an earlier single law, not Q4, and is descriptive. The remaining risk is treating “on a similar numerical scale” as evidence that a generator is as good as another real sample. Real–real compares two complementary, community-disjoint subsets of one finite sample; generated–real compares a fixed generated estimate with both subsets and averages the absolute errors. These have different variance and dependence structures. In the illustrative symmetric case R1 = m + d, R2 = m − d and G = m, the real–real discrepancy is 2|d| and the symmetric generated discrepancy is |d|. A smaller generated discrepancy can therefore arise from the comparison's geometry, without establishing a superior or equivalent cohort. This identity is illustrative, not an exact claim about regression estimates in the actual resplits.

The existing unfavorable results should remain equally visible: full-model glucose median discrepancy is 0.07964–0.10915 against 0.02384 real–real, and the female coefficient discrepancy is 0.07772–0.11791 against 0.02140. Complete marginal/rank results also prevent choosing only the favorable regressions.

**Artifacts checked:** `work/real_real_calibration_2026-11-04/PROTOCOL.json`, `RESULTS.md`, `COMPLETE_METRIC_TABLE.md`. All 36 metrics and all 100 fixed splits were retained.

**Strongest counterargument:** The paper already denies exchangeability, equivalence and independent-cohort interpretation. That is statistically appropriate. I do not recommend discarding the benchmark or requiring exact agreement with a noisy observed sample.

**Minimal remedy — writing:** Add one sentence explaining that the symmetric generated distance and the complementary real–real distance have inherently different scales, so closeness to their medians cannot validate a tolerance. Keep it as context for the size of discrepancies. No new participant analysis is necessary.

### 6. Moderate: the information contrast is credible descriptively, but its headline magnitude should show constructor variation

**Locations:** lines 125, 147–153, 258–273.

The mean-discrepancy comparison is correctly constructed at the law level, with E0/E1 unpaired. Its interpretation should remain about these sampled construction arms, not six independent experiments or a general probability of benefit. The six effects share two targets and related source evidence. The especially large CHNS glucose improvement (0.134019 to 0.024079) is magnified by one E0 constructor with mean absolute error 0.398237; the E0 median constructor error is 0.063720. This is not a reason to remove that constructor: it is a real outcome of the supplied-information arm.

A post hoc review check of the existing aggregate table provides a useful counterweight to excessive skepticism. Median constructor errors retain all six E1–E0 directions. Every contrast retains its sign under all 25 ways of deleting one constructor from E0 and one from E1. Thus five-of-six is not merely a one-author artifact. The improvement's size and its generalization uncertainty still deserve separation.

**Artifacts checked:** `work/main_study_freeze_2026-11-03/final_evaluation/ALL_ENDPOINTS.csv` and `RESULTS.json`. Exact review recipe and output follow below.

**Strongest counterargument:** Figure 4 already shows individual constructor means, and the draft labels contrasts descriptive. Formal significance testing with these few construction contexts and dependent endpoints would not magically create broad external evidence. I agree; no obligatory p-value or universal-baseline claim is warranted.

**Minimal remedy — writing or existing aggregate summary:** Retain the prespecified means and all constructors. Give a brief sense of the construction spread beside the large glucose change, or report the median sensitivity as explicitly post hoc. Do not replace the original endpoint or turn this robustness check into new confirmatory evidence. The fixed statistical comparator is informative about its particular completion assumptions; its 4/6 result need not be converted into a claim of general algorithmic superiority.

## What should not trigger more experiments now

- **Three seeds are not a hidden replication error.** Lines 107, 133, 141, 153 and 175 correctly identify the law as the construction unit. Three seeds give limited Monte Carlo description, but increasing seed count would not solve scientific model or transport uncertainty.
- **No obligatory feedback benefit.** Retention can be a legitimate scientific decision. The iron tail repair fixes mathematical behavior while preserving the registered threshold/rank quantities; that is worthwhile without a score increase. The draft correctly withholds an efficacy claim.
- **No universal baseline-superiority requirement.** A method may be useful while a fixed statistical construction wins particular endpoints. HRS and Q2 appropriately demonstrate reconstruction when the necessary relationship information is supplied.
- **Prospective failure is an informative result.** It should not be erased or “rescued” with a later threshold. The zero-effect HAALSI result shows that its original margin was not very discriminating; the paper already discloses this.
- **Iron missingness is already handled transparently.** The weighted and unweighted missing fractions and complete-case interpretation are clear. No compulsory imputation exercise follows merely from their existence; broader population claims would need more assumptions.
- **Arithmetic audits are valuable but have a bounded role.** Reproducing hundreds of numbers verifies implementation, not source applicability or the scientific truth of a joint law. The current draft mostly observes that distinction.

For the present methods paper I would first tighten the scientific-use claim and reference definitions, then stop. A new confirmation is justified only if the intended claim remains that investigators can trust unseen-target scientific inferences from these cohorts. That confirmation should test the particular intended use, not simply demand that every endpoint beat every comparator.

## Reproducible post hoc review check: Q1 constructor robustness

This check is **new post hoc review arithmetic on already published aggregate outputs**. It is not a new trial, participant reanalysis, generation, method change, selected endpoint, uncertainty interval, or confirmatory result. The original arm means and frozen experiment files were not changed. Within each constructor, it averages the three existing absolute discrepancies. It then reports arm medians and the range of E1-minus-E0 mean contrasts under all 5 × 5 deletions of one constructor from each unpaired arm. The deletion range is a sensitivity range, not a confidence interval. All six endpoints are retained, each in its original units.

| Endpoint | Median E0 error | Median E1 error | Median E1−E0 | Range of mean E1−E0 after deleting one author per arm |
|---|---:|---:|---:|---:|
| CHNS BMI (E1) | 0.013369992 | 0.039795005 | +0.026425013 | +0.004904194 to +0.025550973 |
| CHNS glucose (E2) | 0.063719562 | 0.026037281 | −0.037682280 | −0.137940754 to −0.040889019 |
| CHNS age (E3) | 0.008078563 | 0.004647684 | −0.003430879 | −0.004346152 to −0.001117417 |
| ENSANUT age (Q1_age10) | 0.072916381 | 0.023914957 | −0.049001424 | −0.045144364 to −0.035599685 |
| ENSANUT BMI (Q2_bmi5) | 0.082068789 | 0.023092811 | −0.058975977 | −0.046245938 to −0.025581101 |
| ENSANUT adjusted BMI (Q3_bmi5) | 0.055033630 | 0.028345455 | −0.026688175 | −0.028189816 to −0.018187463 |

Exact Python recipe, run from the project root; standard library only; reads one aggregate CSV and prints results without writing anything:

```python
import csv
import statistics
from collections import defaultdict

path = 'work/main_study_freeze_2026-11-03/final_evaluation/ALL_ENDPOINTS.csv'
with open(path, encoding='utf-8-sig') as handle:
    rows = [r for r in csv.DictReader(handle)
            if r['category'] == 'analyses' and r['constructor_kind'] == 'agent']

by_constructor = defaultdict(list)
for r in rows:
    key = (r['case_id'], r['id'], r['information_condition'], r['constructor_id'])
    by_constructor[key].append(float(r['absolute_discrepancy']))

by_arm = defaultdict(list)
for key, values in by_constructor.items():
    assert len(values) == 3
    by_arm[key[:3]].append(statistics.mean(values))

for case, endpoint in sorted({key[:2] for key in by_arm}):
    e0 = by_arm[case, endpoint, 'E0']
    e1 = by_arm[case, endpoint, 'E1']
    assert len(e0) == len(e1) == 5
    deletion_deltas = [
        statistics.mean(e1[:j] + e1[j + 1:])
        - statistics.mean(e0[:i] + e0[i + 1:])
        for i in range(5) for j in range(5)
    ]
    m0, m1 = statistics.median(e0), statistics.median(e1)
    print(f'{case} {endpoint}: median_E0={m0:.9f}, median_E1={m1:.9f}, '
          f'median_delta={m1 - m0:+.9f}, delete1_each_delta_range='
          f'[{min(deletion_deltas):+.9f},{max(deletion_deltas):+.9f}]')
```

This is intentionally not a bootstrap or an estimate of uncertainty across clinical populations. It answers only whether the observed contrast directions depend on a single constructor in either sampled arm.
