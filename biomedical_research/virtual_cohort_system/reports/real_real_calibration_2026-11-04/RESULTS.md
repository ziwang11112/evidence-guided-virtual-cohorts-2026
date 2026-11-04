# Existing virtual data in the context of real-sample variation

The user's concern was justified: discrepancy from one observed sample is not, by itself, a failure criterion. This completed descriptive analysis finds that several useful relationships in the frozen virtual cohort are on a similar numerical scale to differences between real subsets. Other discrepancies remain substantially larger than the observed within-CHNS resplit scale. The result supports analysis-specific utility, not a single verdict on the whole table.

## What was actually done

The [fixed protocol](PROTOCOL.json) was independently reviewed, then the code was reviewed and [frozen](FREEZE.json) before this unit's patient-value decoding. The exact historical four-file CHNS linkage and eligibility rules recovered 6,631 selected adults aged 35–74 in 218 communities. No new dataset was obtained.

For each of 100 prescribed seeds, the communities were randomly divided into two disjoint groups of 109. After a size-only eligibility check, 3,000 people were sampled without replacement on each side. All 100 first proposed partitions were size-feasible; there were no replacement partitions, unavailable metrics or discarded analyses. A and B always used the same selected individuals.

The three already frozen virtual tables, each containing 3,000 people, were reused without modification or regeneration. Their source-derived scientific model, parameters, trial, historical results and manuscript v0.8 remain unchanged. The two regressions were:

- A: HbA1c ~ 1 + BMI + age + female.
- B: HbA1c ~ 1 + BMI + glucose + age + female.

All nine coefficients, 21 marginal quantities and six Pearson/Spearman correlations were evaluated. The [complete table](COMPLETE_METRIC_TABLE.md) and [aggregate report](REPORT.json) retain all 36 metrics, all 100 splits and all three fixed generated draws. Signed differences and the original matched-R2 comparison are retained alongside the symmetric display below. No significance labels, pass threshold, effect-ratio score or success count was introduced.

## Scientific-analysis results

The real-real column is the median of |T(R1)−T(R2)| over the 100 splits. The generated column gives the range across the three fixed G tables of their median symmetric discrepancy, (|T(G)−T(R1)|+|T(G)−T(R2)|)/2. All values are in the original coefficient or correlation units. These different sampling constructions are not exchangeable; the columns provide context rather than a calibrated win/loss test.

| Analysis quantity | Real-real median absolute difference | Generated symmetric median difference, range across 3 draws |
| --- | ---: | ---: |
| A: BMI coefficient | 0.007239 | 0.004383–0.012727 |
| A: Age coefficient | 0.001705 | 0.001055–0.002387 |
| A: Female coefficient | 0.025909 | 0.014178–0.020021 |
| B: BMI coefficient | 0.005797 | 0.004436–0.018340 |
| B: Glucose coefficient | 0.023839 | 0.079642–0.109154 |
| B: Age coefficient | 0.001192 | 0.000707–0.002667 |
| B: Female coefficient | 0.021398 | 0.077716–0.117915 |
| BMI–glucose Pearson correlation | 0.025768 | 0.062791–0.077943 |
| BMI–glucose Spearman correlation | 0.025903 | 0.015363–0.024806 |

The A coefficients, B age coefficient and BMI–glucose rank correlation have discrepancies on broadly similar numerical scales to the resplit variation. This strengthens the bounded interpretation that the generated data preserve some useful associations. It does not show that a synthetic table is more realistic when its symmetric discrepancy is smaller than the real-real median.

After conditioning on glucose, the BMI coefficient varies more across the three generated draws: one is close on this descriptive scale while the other two are farther away. All three glucose and female coefficients in B remain farther from the real estimates than typical real-real differences in this design. Matching a sign, or changing which confidence interval includes zero, would not resolve those magnitude differences.

The BMI–glucose finding also depends on the scientific summary: rank correlation is closer than Pearson correlation. Neither should be chosen retrospectively as the sole quality score. Both were prescribed and both are reported. Distribution shape is a possible contributor, but this evaluation does not isolate the cause.

## Distributions: some agreement and some remaining differences

The same distinction is visible in the distributions. Glucose mean differences have a real-real median of 0.048830 mmol/L versus generated symmetric medians of 0.024415–0.045521; HbA1c mean differences are 0.032683 percentage points versus 0.018560–0.042692. These are useful examples of why exact mean equality should not be demanded.

Other summaries do not have the same agreement. Female proportion differences are 0.005333 for real-real versus 0.098167–0.105500 for generated-real, and glucose q90 differences are 0.060000 mmol/L versus 0.676156–0.811237. HbA1c upper quantiles, BMI dispersion and several rank relationships also remain different; all are retained in the complete table. This is a mismatch with the selected CHNS reference, not proof that the generator cannot describe any biomedical population.

## What this changes in the paper

Use scientific-analysis agreement together with a descriptive real-sample context. The central claim remains that published evidence can be converted by an Agent into virtual data with useful properties for specified analyses. The data are not required to duplicate every observed value or every sample coefficient.

The current results justify reporting useful A relationships, age-related B behavior and BMI–glucose rank behavior, together with the conditional-relation and distribution limits. They do not justify universal recovery, independent population validation, a revision benefit, or a newly invented equivalence criterion. This evaluation refinement is not itself claimed as a novel statistical method.

Suggested manuscript wording:

> We contextualized discrepancies using 100 prespecified community-disjoint resplits of the already exposed CHNS reference, with 3,000 participants per side. Several associations in the frozen virtual cohorts had discrepancies on a similar numerical scale to real-sample resplit variation, whereas glucose-adjusted relationships and selected distributional features retained larger discrepancies. Because the real halves were dependent parts of a finite sample and the virtual tables were fixed, these comparisons were descriptive and did not define equivalence thresholds or independent-cohort validation.

## Verification and scope

Six invented-data tests passed. [Independent implementation review](IMPLEMENTATION_REVIEW.md) found and resolved one failure-log issue before freezing; it did not change the sampling or scientific estimands. The separate [numerical review](INDEPENDENT_REVIEW.md) documents the independent calculation, a metadata-scanner false positive and its metadata-only continuation. Production calculations and the original aggregate report were not changed to address that reviewer tooling issue.

The [figure](REAL_REAL_CONTEXT.svg) contains all seven non-intercept coefficients. Lines show split-distribution 10th–90th percentiles, not confidence intervals. Figure generation reads only the aggregate report.

This remains one previously exposed, unweighted complete-case CHNS reference. Community-disjoint resplits measure conditional within-sample variation, not between-country, between-year or between-cohort heterogeneity. Matching row count does not match effective sample size or the original survey design. Three generated draws are one law, not three clinical studies. No new generator execution, source search, data download, training, HPC job or paid API call occurred.

Decision: retain the frozen model and its historical results; incorporate this bounded evaluation context into the paper. Do not retune against these new split results or turn a descriptive percentile into a retrospective pass line. Any future method change should address a scientific evidence/model gap under a separate prospective design.
