# Real-versus-real design review

Date: 2026-11-04. Scope: independent statistical design review before this unit's new reference evaluation. This reviewer read definitions, existing code and published aggregate reports only; no individual clinical values were decoded or inspected, no historical campaign was rerun, and no frozen artifact was modified. This document is the reviewer's only new file.

## Decision

**Proceed with a narrowly descriptive comparison.** The proposed design is executable and answers a useful question: how much can the declared statistics differ between two community-disjoint, equally sized subsets of this already selected CHNS sample? It gives context for the frozen generated tables' discrepancies. It does not establish a reference distribution under which generated-versus-real and real-versus-real discrepancies are exchangeable, and it cannot yield a calibrated pass/fail decision, equivalence claim or ranking of clinical validity.

Retain the proposed 100 prespecified community splits and the three existing 3,000-row delivery tables. Do not add generation, tune the generator, search for favorable partitions or expand to a new benchmark. The smallest useful addition is a symmetric generated discrepancy, computed from the same fitted statistics and requiring no extra sampling or fits.

## Frozen scope to retain

- The existing linkage, cleaning, 2009 wave, age 35–74 and common complete-case definition must be reused exactly. The existing aggregate report identifies 6,631 eligible individuals in 218 communities. Both A and B must use the same sampled individuals; do not silently enlarge A by allowing missing glucose.
- For each prespecified seed, randomly assign the 218 communities to labeled groups of 109 and 109. Accept a proposed assignment solely when both groups contain at least 3,000 eligible people, then sample 3,000 individuals without replacement from each group. Never split a community across R1 and R2.
- G consists only of the three frozen physical delivery tables from `evidence_to_generation_2026-11-04`, seeds 7401, 7402 and 7403. Retained final aliases are not additional tables or samples.
- Fit A, `hba1c ~ 1 + bmi + age + female`, and B, `hba1c ~ 1 + bmi + glucose + age + female`, by the same unweighted OLS definition. Report all nine coefficients; identify the seven nonintercept coefficients as the core scientific coefficients without hiding the two intercepts.
- Report mean, sample SD (`ddof=1`) and linear q10/q50/q90 for age, BMI, glucose and HbA1c; female proportion; and Pearson/Spearman correlations for BMI–HbA1c, glucose–HbA1c and BMI–glucose. This gives 36 distinct metrics: 9 coefficients + 20 continuous summaries + 1 proportion + 6 correlations. BMI–glucose correlation is a prespecified extension of the older evaluation's joint diagnostics, not a claim that the old definition already included it.

## Minimal changes before execution

1. Freeze seeds 8400–8499, at most 1,000 count-based assignment attempts per seed, the RNG family, deterministic ordering of the sampling frame, explicit stream convention, and the rejection procedure before new reference decoding. The specified convention of one PCG64 stream per seed, first consuming community-partition attempts and then sampling R1 followed by R2, is reproducible when the input ordering and selected-index sorting are fixed. A seed should identify its complete deterministic procedure, not just the final accepted assignment. Log every rejected assignment's reason and aggregate counts; counts may decide acceptance, clinical values may not. An input-schema or bound-input-hash mismatch must halt execution.
2. Record the eligible count in each assigned half, the number of assignment attempts, selected row counts, assigned community counts and community counts actually represented after individual sampling. The assigned halves each have 109 communities; the selected 3,000 rows could represent fewer. Verify community disjointness, person disjointness, within-side uniqueness and a total of 6,000 distinct selected individuals. Keep the 631 unselected individuals in the fixed source-frame accounting.
3. For metric m and split s, retain the raw statistic values and signed differences as well as these absolute discrepancies:

   - `dRR[s,m] = abs(T(R1[s],m) - T(R2[s],m))`.
   - `dGR2[g,s,m] = abs(T(G[g],m) - T(R2[s],m))`, preserving the requested matched-R2 comparison.
   - `dGsym[g,s,m] = (abs(T(G[g],m) - T(R1[s],m)) + abs(T(G[g],m) - T(R2[s],m))) / 2`.

   The symmetric quantity makes the generated comparison insensitive to swapping the labels R1 and R2. It is an additional descriptive view, not a correction for dependence or a formal null calibration. Keep all three G seeds separate.
4. Report distributions in each metric's original units, preferably median and q10–q90 with the 100 split-level records available for audit. Label these as empirical split-distribution quantiles, not confidence intervals. Min/max can remain in machine-readable output. Avoid normalized ratios, percentile ranks, win rates, thresholds, pooled scores and p-values. In particular, a metric with a zero or near-zero real-real difference is not a sound denominator.
5. Count/eligibility acceptance and analysis availability must remain separate. A singular fit, constant-variable correlation or other numerical failure is an explicit unavailable result for that scheduled split and metric, with its reason and denominator shown. It must not cause a favorable replacement split. Freeze the failure policy and quantile/tie conventions. Do not add cluster-robust or synthetic intervals merely to describe split discrepancies; point-statistic comparisons are sufficient for this unit.

If the finite attempt limit is exhausted, report the incomplete scheduled slot and stop or preserve a clearly incomplete output according to the frozen policy. Do not lower the row count, alter community balance, change seeds or add attempts in response to observed clinical results.

## Why equal row counts do not create an exact fairness calibration

The matched R2 is a useful design feature: both comparisons in a split use the same reference estimate. Community separation also avoids placing members of one observed community on both real sides. Nevertheless, the random mechanisms differ. R1 and R2 are disjoint pieces of one finite, selected frame and their composition is constrained jointly. Each G table is already fixed and has no complementary relationship to R2. Its repeated comparison does not resample the generator, its sources, its model or its parameters.

A simple analytic example makes the limitation concrete; it uses no patient values. Suppose an unclustered finite frame has size N and variance S² (denominator N−1), and two equal-sized samples of n are selected uniformly without replacement with no overlap. For their means:

`Var(mean(R1)) = (1 − n/N) S²/n`

`Cov(mean(R1), mean(R2)) = −S²/N`

`Var(mean(R1) − mean(R2)) = 2 S²/n`.

If a fixed G statistic happens to equal the finite-frame mean, then

`Var(mean(G) − mean(R2)) = (1 − n/N) S²/n`.

With N = 6,631 and n = 3,000, the signed real-real difference has about 1.91 times the standard deviation of that fixed-G-to-R2 difference in this illustrative design. This does not supply a correction factor for the actual clustered design, nonlinear quantiles, correlations or regression coefficients. It shows why a generated discrepancy below the real-real scale need not mean better realism, while a larger discrepancy may still be useful descriptive evidence of mismatch. The finite sampling fraction is material, and community clustering adds a further design difference. Standard sampling references describe the finite-population correction and the effect of clustering on variance: [Statistics Canada, Survey Methods and Practices](https://www150.statcan.gc.ca/n1/en/pub/12-587-x/12-587-x2003001-eng.pdf), [CDC, Variance Estimation](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx).

The symmetric generated discrepancy removes label arbitrariness but leaves this asymmetry intact. Equal n is therefore a useful size control, not matching of effective sample size, dependency, sampling design or uncertainty.

## Interpretation and reporting boundaries

The 100 results describe repeated allocations and subsampling of the same selected frame. Independent RNG streams do not create 100 independent clinical cohorts. Conditional randomization draws can be computationally independent while still supplying no additional independent source populations; do not use the split count as the clinical sample size or apply ordinary paired tests to claim scientific replication. The three G tables likewise describe conditional draw variation from one frozen model, not three independently developed populations.

The rejection condition is defensible because it is based only on eligibility counts, but it conditions the experiment on sufficiently balanced person counts. Community size can be associated with measured characteristics. Thus the result is specifically the accepted 109/109-community partition design, not unrestricted community heterogeneity. No weighting or stratification should be introduced after seeing results; the declared target remains the selected unweighted complete-case sample, not nationally representative CHNS inference.

The real-real distribution excludes differences between cohorts in geography, calendar time, recruitment, measurement, selection and underlying population composition. It cannot validate external transportability or estimate cross-cohort heterogeneity. This is also a development reference already exposed in earlier work, not new independent confirmation. Neither the reference nor a chosen partition is known population truth.

Absolute discrepancies conceal direction, so retain signed differences and the underlying fitted coefficients. The two intercepts are reported for completeness but refer to predictor-zero values outside the age-restricted scientific target; their discrepancies should not dominate scientific interpretation. The seven nonintercept terms are also dependent, and the 36 metrics should not be aggregated into a count of successes.

Suitable wording is: “Within the prespecified community-disjoint resplitting of the selected CHNS sample, this generated table's discrepancy was [reported value/distribution] alongside the observed real-real split scale.” Avoid wording such as “as realistic as independent cohorts,” “passed real-real validation,” “equivalent to real data” or “X% calibrated accuracy.”

## Simpler alternatives considered

The proposed design, with the small symmetric addition above, is the simplest defensible design for the stated question. A single partition would be easy but too sensitive to that partition. Comparing each subset to the full 6,631-person frame would introduce overlap between subset and reference and answer a different question. Independent community bootstrap samples would target a different resampling distribution, allow shared original communities and require additional choices about sample size and weights; they are not needed for this descriptive exercise. Holding out a permanent anchor or collecting a second cohort could address other questions but would change the present scope.

No further analyses are required to make this unit useful. Preserve the existing generator and deliveries, freeze the small procedural details, report the paired and symmetric discrepancy distributions, and make the finite-frame, clustering and repeated-use limitations explicit.

## Local materials inspected

- `work/agent_system_live_2026-11-03/evaluation/EVALUATION_DEFINITION.json`.
- `work/agent_system_live_2026-11-03/evaluation/evaluate_live.py` (read as text, not executed).
- `work/agent_system_live_2026-11-03/evaluation/RESULTS.md` (existing public aggregate summary).
- `work/evidence_to_generation_2026-11-04/PROTOCOL.json`.
- `work/evidence_to_generation_2026-11-04/evaluation/IMPLEMENTATION_NOTES.md`.
- `work/evidence_to_generation_2026-11-04/evaluation/evaluate_build.py` (read as text, not executed).

This is design approval with the explicit interpretation limits above, not implementation verification, new numerical results, or an audit of undisclosed patient records.
