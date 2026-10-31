# Independent initial-candidate review

31 October 2026, before reference release. Scope: both builders' stable `candidates/initial/` artifacts, the M17-B protocol, the admitted source packet, and the relevant harness interface. No reference records, reference outcomes, previous-case contents, or generated rows were read. No candidate program was imported or executed. No candidate was edited.

**Verdict: no blocking implementation, provenance, quota, or source-check semantic error found in either initial candidate.** This is a static implementation review, not a finding of scientific validity or successful execution. Root remains responsible for structural validation, freezing, isolated execution, and the one source-feedback opportunity.

## Original-source verification

- Bogalusa original XML adult Table 1: subgroup counts, BMI and urate means/SDs agree with the construction inputs. Table 2 labels BMI as a dependent variable, with raw adult coefficients 1.38, 2.59, 1.29 and 2.14 in the reported sex/race strata, and 1.87 for All. The table footnote and Results paragraph establish BMI-on-urate direction and age adjustment. Neither candidate reciprocates these coefficients or uses the standardized coefficients as Pearson correlations.
- Korean original XML Table 1: the BMI difference 23.7 minus 22.9 is 0.8 kg/m2. Both candidates label carrying that pooled, cross-sectional age-group difference into US sex-specific conditional moments as an assumption. They do not relabel it a measured continuous age effect or transfer the Korean absolute BMI level as a target requirement.
- CHS original HTML Table 1 and section 3.1: inputs use the pre-match n=3956/1505 groups, BMI 26/28 with SD 4/4, female counts 2268/874, and urate 5.0/7.5 with SD 1/1. The later matched columns are not substituted. Neither candidate presents the threshold-defined groups as observed sex-specific marginal distributions.
- Independently recomputed the young count-pooled means and sample SDs, count-weighted raw slopes, and b1 latent correlations from the admitted reported statistics. These agree with both specifications to numerical precision. b2's implied latent correlations across every allowed integer age are approximately 0.266–0.315 for men and 0.281–0.389 for women, within the declared family's feasible interval. This was parameter arithmetic, not generator execution.

## Code and provenance

Both programs explicitly reject a non-None observed input and only import numpy/pandas. Static inspection found no file, network, target-table, or external-data access. Each loops over two sex levels and four specified age intervals, takes 40 integer ages in each cell, constructs all BMI/urate values, assigns unique fictional identifiers, and permutes rows without changing quotas. Lognormal transformation produces positive values without clipping or outcome-based trimming. Realized numerical/output validity still requires the isolated execution receipt.

The code matches the declared parameterization: b1 holds the young sex-specific latent correlation constant over age; b2 interpolates the assumed raw BMI-on-urate projection slope and calculates the corresponding lognormal correlation at each age. The lognormal covariance identity is implemented in the stated direction. Marginal-to-conditional transport, race pooling, age interpolation, absent middle-age US evidence, old sex allocation, common old BMI moments, unreported distribution family, and absent parameter/transport uncertainty are all explicit assumptions. b2's old slope of 0.8 is explicitly labeled an ecological-contrast extension; its scientific plausibility is not an implementation defect to repair by choosing different parameters.

## Source-check semantics

b1 declares 21 approximate and 8 non-computable checks; b2 declares 18 approximate and 14 non-computable checks. Mean/SD operators preserve arithmetic means versus sample SDs, their units, and the intended age/sex selections. Approximation references are supplied either by each check or by the feedback plan's population-level assumptions, which the supplied adapter unions. All comparisons acknowledge population mismatch.

b1's All-adult BMI-on-urate check uses BMI as outcome and urate plus age as predictors. The source does not explicitly resolve additional All-column sex/race adjustment; b1 discloses this ambiguity and labels the check approximate. b2 instead leaves this check non-computable. These are defensible, different treatments of the source ambiguity and do not support treating either as exact source replication.

b1's older sex-specific exceedance checks correctly use age at least 65, female=0 with urate at least 7, and female=1 with urate at least 6. Their source ratios are 631/2319 and 874/3142. Both candidates leave CHS pooled threshold-union group checks non-computable because the available exact output/AND-only filter cannot express the sex-specific union. Race-specific coefficient checks also remain non-computable; no surrogate race group or coefficient direction is substituted.

## Interpretation and audit limitations

Both constructions use essentially the same marginal anchors and age knots, including the assumed one-unit older sex gap. Their main structural difference is dependence transport. Two fresh constructions therefore do not establish broad model-family diversity or independent biomedical corroboration. Similarity alone does not establish cross-reading, and no such evidence was found in the reviewed artifacts.

No scientifically preferred parameter, sign, or source fit was imposed by this reviewer. No target result was available. Static code inspection cannot certify the builders' complete external access history. An initial broad filename search returned historical artifact names; no historical candidate/result contents were opened. A source-printing command failed on console encoding after printing Bogalusa Table 1; rerunning with explicit UTF-8 completed the original-table review. This was an inspection failure, not a candidate execution failure.

The independent recomputation script is separate from both candidates and the custodian evaluator. It uses statsmodels formula OLS with HC3 and patsy prediction contrasts. Its first invented arithmetic self-check exposed a statsmodels 0.15 internal formula-metadata compatibility difference; the implementation now rebuilds the numeric formula RHS with patsy. The repeated invented-only self-check passed all eight known linear effects, the quadratic finite difference, and sex-interaction contrasts. No candidate generator or real reference was involved in this correction.
