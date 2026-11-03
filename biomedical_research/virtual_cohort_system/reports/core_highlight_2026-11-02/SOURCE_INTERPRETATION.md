# Qualified source projection candidates and the E0/E1 boundary

2 November 2026. **Source-only conditional-admission proposal, pending independent review.** These definitions use retained Jansen, Bao and MIND source audits. They authorize no source generation, target admission, target analysis or release. No original paper was reopened; no web request, patient/generated row, target effect or new quota was used. Existing packets and frozen files remain unchanged.

The companion [SOURCE_PROJECTION_CANDIDATES.json](SOURCE_PROJECTION_CANDIDATES.json) is a coordinator specification, not an existing harness input. It contains both information regimes and must never itself be mounted into E0. Its provenance records bind the retained authored audits by relative path and SHA-256. It includes no original article body or quarantined coefficient bundle.

## The two Jansen projections are separate executable candidates

The retained [independent original-source audit](../autonomous_research_cycle2_2026-10-31/evidence/INDEPENDENT_SOURCE_AUDIT.md) verifies Table 2 as two separate age/gender-adjusted projections, with native HbA1c IFCC outcome units. The [retained projection summary](../chns_admission_2026-11-01/f2/evidence/sources/JANSEN_2013.md) preserves their incomplete uncertainty and source context.

| Candidate | Declared fitted equation for the comparison | Reported focal coefficient | Preserved interval |
|---|---|---:|---|
| `R_JANSEN_BMI` | `HbA1c_IFCC = b0 + b_age*age + b_gender*gender_binary + b_BMI*BMI + residual` | `b_BMI = 0.13 mmol/mol per kg/m2` | 0.10-0.16; confidence level unconfirmed |
| `R_JANSEN_FPG` | `HbA1c_IFCC = c0 + c_age*age + c_gender*gender_binary + c_FPG*FPG + residual` | `c_FPG = 2.29 mmol/mol per mmol/L` | 2.07-2.51; confidence level unconfirmed |

Each candidate minimizes the unweighted residual sum of squares with an intercept, raw covariates, no interactions and no penalty, returning only its focal slope. Require finite values, both declared binary categories, full column rank and positive residual degrees of freedom. Reject unavailable inputs instead of silently deleting rows, adding terms, changing units or imputing values. The two fitted intercepts and nuisance coefficients are unrelated unknowns; they are not additional source constraints.

The explicit intercept is a conventional comparison assumption, not a claim that the original audit recovered the exact intercept convention or its numerical value. Likewise, equal weights are a declared scenario choice; original analytic weighting stays `not_reported`. The proposal therefore makes the mathematics executable while preserving the gap between a qualified comparison and the unavailable exact published-estimator replay.

**Do not fit one equation containing both BMI and FPG and compare its two slopes to these numbers.** Conditional coefficients change when the conditioning set changes. Do not construct a generative HbA1c equation by pasting 0.13 and 2.29 together. A constructor may choose a coherent joint model whose two separate projections can be inspected, but its covariance, intercept, residual law and unreported dependencies remain model assumptions.

## What binary nuisance relabelling does and does not solve

For these full-rank, unpenalized OLS models with an intercept and no interactions, replacing `gender_binary = g` with `1-g` preserves the nuisance design span `[1, age, g]`. On the same observations, with all other columns unchanged, the BMI or FPG coefficient is therefore unchanged. The intercept and gender coefficient change. This removes the need to guess which of the same two source categories was coded 1 when comparing only the focal slope.

This claim is narrow. It does not establish the original coding, identify the source gender coefficient, repair a different or misclassified category partition, justify a source-to-target sex/gender mapping, or preserve a prevalence after categories are mislabeled. It does not apply as stated without an intercept, under penalization, or to a focal main coefficient in a model containing gender interactions. Missingness/row changes invalidate the same-observation condition. Source-context code must declare its own two-category map; the reported male count remains tied to the male category regardless of its numeric code.

## Unknown precision is different from unknown meaning

A qualified point comparison needs the response, focal predictor, units, adjustment set, raw-versus-transformed functional, source context, declared weighting/intercept convention and input/denominator rules. These are explicit in the candidate definitions. Jansen's IFCC outcome is not percent HbA1c; FPG is fasting plasma, not serum or random capillary glucose. No unit or assay bridge is silently applied.

The following remain unknown: regression-row n, coefficient SE, interval confidence level, exact row processing and original weighting. No 95% label, SE, precision weight or sampling interval is manufactured. The numerical source intercept and nuisance coefficients are not needed to compute the two selected focal slopes. A missing complete conditional response law or predictor covariance does not prohibit defining or evaluating these separate functionals.

For strict replay, the source-weight, processing/context and intercept-convention gaps remain material, so the JSON retains `strict_replay.status = not_computable`. For the separate equal-weight, complete-analysis-value source scenario, they can instead be explicit qualifications subject to independent admission. The report would retain the calculated value, reported point, raw difference and assumptions, without a combined source loss, confidence-interval-membership pass or transport claim. This is not changing unknown source weights to `none` in an old semantic record.

The selected Lifelines source excludes diabetes, specified anemia and specified missingness, with unrelated western-European GWAS participants and an oldest-family-member preference. A generated eligible-source context may be declared under those conditions without fabricating a population of disease flags. It cannot claim to reconstruct exact source participants or regression-row membership. Table 1 margins describe the marginal sample of 2,921 and must not be treated as certified Table 2 model-row moments. No exact intercept or residual variance may be recovered by combining those potentially different samples.

## Traceable common evidence and added relationships

The prospective partition has **three common source metadata records and 15 common marginal records**, then four added relationship records. It is an evidence-information contrast. It does not by itself test a particular fitting algorithm, and no clinical benefit is presumed.

| Information | Common E0, also supplied unchanged to E1 | Added only in E1 |
|---|---|---|
| Jansen/Lifelines | Source identity, selection/measurement caveats; age 55.5/9.9, BMI 26.5/4.1, FPG 5.1/0.5, IFCC HbA1c 38/3 (mean/individual SD); male count 1,176/2,921. | The two separate Table 2 focal coefficients and their faithfully qualified intervals/definitions. |
| Bao/SHDS II | Source identity and plasma/selection caveats; overall age 49.4 [37.9,57.7], BMI 23.5 [21.4,25.9], FPG 5.2 [4.8,5.6], HbA1c percent 5.6 [5.3,5.9] (median [Q1,Q3]); female count 3,058/4,886. | Unadjusted Pearson FPG-HbA1c, 0.619, with equal-weight complete-analysis-value interpretation explicitly separated from original unknown weighting/processing. |
| MIND-China | Source identity, older selected population, imputation/timing and serum/assay caveats; age 69.5/4.2, BMI 25.0/3.6, FSG 5.2/1.4, HbA1c percent 6.1/1.0 (mean/individual SD); female count 2,049/3,547. | Unadjusted Spearman FSG-HbA1c, 0.529, under declared equal weights and average ranks for ties. |

The numeric margins are from the [retained Jansen independent audit](../autonomous_research_cycle2_2026-10-31/evidence/INDEPENDENT_SOURCE_AUDIT.md), [Bao audit](../chns_admission_2026-11-01/evidence/BAO_2010_SOURCE_AUDIT.md), [MIND audit](../chns_admission_2026-11-01/evidence/MIND_2024_SOURCE_AUDIT.md), and [independent source-package check](../chns_admission_2026-11-01/f2/review/SOURCE_PACKAGE_REVIEW.md). Every JSON record has a source context, locator and provenance IDs. Counts produce count fractions, not weighted population composition. Individual SDs are not mean/coefficient SEs; quartile endpoints are not confidence intervals. Unknown SD divisor and quantile method remain explicit. These source margins are not target-population calibration values.

The JSON proposes exactly these four E1 relationships: two primary conditional Jansen records and two supporting unadjusted records. Sources remain separate contexts, with no pooled coefficient or averaged Pearson/Spearman objective. Additional MIND paired-plasma relationships, Bao OGTT-dependent groups and Jansen Table 3 are outside this finite addition. If a later reviewer changes the E1 set, that change must precede constructor release and remain visible in the information comparison; it cannot follow target results.

The existing CHNS approval for Bao/MIND correlations was a task-proxy decision for that closed case. It supplies an example of a defensible qualified functional, not automatic admission of these new source-context comparisons. Original unknown weights remain unknown. MIND rank association does not become a Pearson covariance; its source imputation and timing remain limitations. The [independent MIND arithmetic audit](../chns_admission_2026-11-01/evidence/MIND_2024_INDEPENDENT_ARITHMETIC_REVIEW.md) preserves the incompatible HbA1c agreement bundle; none of its conflicting or dependent calibration quantities enters E0 or E1.

## Preventing E0 leakage and keeping target transport separate

This combined JSON, this interpretation note and the retained audit documents are coordinator-only. Several retained audits contain E1 coefficients, omitted relationships or old case references. Linking them as provenance does not authorize mounting them into E0 or exposing their full text to a constructor. Later sanitized arm files must be compiled from the exact allowed ID lists, with E0 free of relationship values, intervals, sign claims and reconstructible relationship summaries. No original full body, broad source packet, wider workspace, historical fitted model or target-result material belongs in either arm.

Both arms should receive the same short source identities, selected metadata/margins, uncertainty and measurement caveats, and separately frozen task/budget. Public source identities cannot prove pretraining non-exposure; the procedural contrast concerns the supplied task evidence. Browsing or retrieving source papers is not authorized for constructors. Audit paths/hashes remain in the coordinator manifest rather than providing a backdoor to the broader source collection.

Source-only conditional admission would approve particular qualified point-comparison definitions and their limitations. It would not validate a new target's eligibility, glucose specimen/fasting protocol, HbA1c assay/scale, binary category meaning or transport assumption. A future target and its intended analyses must be reviewed independently before any release. No target moments, target coefficients, target success cutoffs or desired target directions are supplied here.

The immediate finite decision is to approve or decline each of the four source-context interpretations separately, preserving strict unavailability and the exact E0/E1 boundary. Missing precision is not a reason to demand further literature by default. A request for more evidence should name a semantic ambiguity that changes the selected functional or a necessary target applicability condition. No new family or original-study quota is consumed by these files.
