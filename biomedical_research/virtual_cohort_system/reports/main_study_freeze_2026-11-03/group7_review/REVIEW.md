# Group 7 independent implementation review

Reviewer: `/root/main_review_g7`. All three assigned frozen initial candidates are **ready**, with their `initial_final` decisions bound below. This is implementation and trace readiness, not favorable scientific performance, clinical validity or source/target transport certification. No exploratory trial is required for this review. No session was closed or delivered.

| Candidate | Result | Non-marginal uptake |
|---|---|---|
| ENSANUT2018_E0_A04 | Completed; ready | Empty list is correct for E0 |
| ENSANUT2018_E1_A04 | Completed; ready | 3 model constraints, 8 contextual age-band means |
| ENSANUT2018_E0_A05 | Completed; ready | Empty list is correct for E0 |

## Independent method and integrity

Read the assigned tasks, profiles, inputs, registered scoped source artifacts, candidate files and decisions, plus the evidence-cohort-generation skill, its harness interface, the harness contract/lifecycle interfaces and the allowed session interface. The retained `independent_algebra.py` uses closed-form distribution identities, finite age-band sums, interval arithmetic and small covariance linear systems. It never imports or executes any generator, samples rows, uses random draws, performs quadrature, or reads clinical target references/results. Its actual successful output is `independent_algebra_results.json`.

`lifecycle.verify_candidate(bundle, 'candidates/initial')` passed independently for every candidate before and after the algebra. Generator syntax/signature was parsed only. Every candidate evidence item exactly matches an admitted source-extract record and the supplied input evidence: 17 items for each E0 candidate and 30 for E1. Registered hashes, frozen candidate commitments, decision author/candidate/action, complete operation coverage and unavailable target-as-source declarations were checked. All source comparisons on the target table are `not_computable` with null operators. No frozen file or decision was modified.

| Candidate | freeze.json SHA256 | decision.json SHA256 |
|---|---|---|
| ENSANUT2018_E0_A04 | `625ec54364270e1064f15ba5168ad9896571cfa70feb5dea057cc48c368a59d5` | `5c7c23aa429489f98e9a9a8b6563a9fdeb24f08eb73e4cd7b5352b6378863dfe` |
| ENSANUT2018_E1_A04 | `5220246b588485f12500645bb6ec53ae57ed4c0235b89b9d2375d768e7282b94` | `e1ef96c993e3cdbdbb31153f1bedaec43264d3c883af9edd4ee4aa2c3692c3ce` |
| ENSANUT2018_E0_A05 | `2ae333dd30ffad7726c7f178f90e721b9d88a3cb4be784a3435c839651f23d59` | `d320e2f67aae808dc611e1f42e408192db3be776a0c8d1c8359670cbdb516826` |

The independent script initially stopped on two reviewer-script bookkeeping errors: the semantic declaration key is `bindings`, not `checks`; and the E0_A05 loading variable temporarily shadowed the bundle-path variable at final reverification. Both were corrected before producing the retained successful results. These were review-script errors, not candidate failures, and no generated rows were involved.

## ENSANUT2018_E0_A04

The code implements independent BMI/HbA1c gamma marginals and a glucose beta marginal scaled to (0,126), independent of the fixed demographic allocation. The derived BMI gamma shape/scale are 41.7757287329/0.6343396226; HbA1c shape/scale are 348.4444444444/0.0160714286; glucose beta shapes are 27.5108571429 and 10.2491428571. All are positive. For a gamma variable, E[X^r] = theta^r Gamma(k+r)/Gamma(k); thus the unbounded positive marginals have finite first and second moments. Glucose and demographics are bounded. Independent calculations reproduce BMI second moment 719.06, glucose 8508.24 and HbA1c 31.45.

Exactly 375 rows are allocated to every female-by-age-band cell, with integer ages drawn on the specified inclusive bands. The permutation preserves quotas and the six-column schema. The random-row age mean is 53.875 and variance 270.359375; the finite table does not force empirical biomarker moments. Numerical gamma/beta support violations cause explicit failure rather than clipping or silent replacement. This is compatible with a mathematically valid ideal law and does not assert successful future execution.

The gamma shapes, tails, product dependence and cross-population marginal transfer are identified as assumptions. The implied zero population slopes follow from the product law and are not evidence of absent clinical association. The E0 non-marginal operation list and uptake list are both empty. This is complete uptake accounting, not a missing E1 analysis.

## ENSANUT2018_E1_A04

The generator implements a balanced binary common factor plus independent centered beta residuals for BMI and glucose, and an additive HbA1c equation with independent uniform residual. The actual factor loadings give Cov(BMI,glucose)=4.5; this covariance is assumed explicitly. Positive residual beta shapes reconstruct variances 14.56 and 72, giving total variances 16.81 and 81. The metabolic covariance determinant is 1341.36 > 0.

The two Jansen estimates are separate age/sex-adjusted projections. Independently solving their distinct normal equations gives joint coefficients 0.00890935652173913 for BMI and 0.01114332463768116 for glucose. These joint coefficients differ from the separate source estimates, as required. The residual HbA1c variance is 0.06791309171790308 > 0. Conservative target support is BMI [13,58], glucose [48.8,125.8] and HbA1c [4.2441858554,6.9458926403]; all target moments therefore exist. The artificial support limits are disclosed.

The qualified Lifelines context explicitly changes age to a continuous uniform law with mean 55.5 and SD 9.9 and sex probability to 0.597 while retaining the implemented conditional equations and primitive laws. Independent primitive-to-outcome covariance algebra reproduces both source-context moment matrices and the separately adjusted slopes 0.0118924 and 0.01163828888888889. These are law-derived quantities, not desired matrices disconnected from the generator. Equivalence of Table 1 margins with the Table 2 analysis populations remains an explicit assumption because row-specific sample sizes are unknown.

The Pani reference explicitly uses age = 25 + geometric failures with p=1/31 and independent sex probability 0.5, retaining the same conditional HbA1c equation. This reference has age mean 55 and variance 930. Its age tail is unbounded, but geometric first/second moments are finite and HbA1c is affine in age plus bounded terms. The adjusted age projection is independently recovered as 0.01 percentage points/year. This is a qualified population projection, not a reconstruction of survey weights or source demographic truth. The target age maximum 79 is not inserted into the source >=70 band.

All 11 non-marginal operations have records: three numeric constraints and eight context-only Pani age-band means. The contextual means are not fitted, not falsely claimed reproduced, and their SEs are not used as individual SDs. Their actual source population/measurement limitations, shared-cohort overlap and unknown precision are recorded. The absence of source age-band calibration is qualified and is not an implementation blocker.

## ENSANUT2018_E0_A05

The code implements an affine law in independent standardized age, balanced sex and three standardized Beta(3,3) factors. Residual variance radicands are positive, and the nonzero diagonal of the loading matrix proves a positive-definite joint covariance. Closed-form factor moments reproduce the intended marginal means/SDs and the retained covariance and second-moment matrices.

Exact affine support closures are BMI [14.5115721390,38.3762193877], glucose [59.0864397789,124.1440932967] and HbA1c [4.2666412740,6.9183063698]. They satisfy strict task support with numerical margins. All variables are bounded, so all first/second/cross moments and requested population projections exist. The 375-per-cell loop and final permutation preserve exact quotas. Independence, factor loadings and tail suppression are explicit E0 completion assumptions; they are not source dependence findings. Empty numerical uptake is complete for E0. Independently derived model-law projection coefficients agree with the author's calculation; they were not compared with target answers.

## Common source and interpretation qualifications

The six clinical source anchors are the selected Jansen BMI mean/SD 26.5/4.1, glucose 91.8/9 mg/dL and directly printed HbA1c 5.6/0.3 percent. Independently checked unit mapping uses glucose factor 18; NGSP levels use 0.09148*x + 2.152, whereas SDs and slopes use scale only. IFCC and percent representations are alternatives of the same quantity, not additional evidence or precision. For E1, the glucose regression slope also divides by 18. No eAG/fasting-glucose equation is inferred.

All candidates state the full task population as a conditional membership assumption. Their six fields cannot verify diagnosis history, fasting-hour documentation, pregnancy/lactation routing or anthropometry documentation. No medication/anemia exclusion is silently added. Source plasma versus target serum, assay, ancestry, age/sex and eligibility differences remain unverified transport assumptions. Repeated seeds would represent conditional synthetic variation only, not external estimate uncertainty or new clinical evidence. Readiness makes no statement about clinical validity, causal effects, measurement recovery or favorable eventual outcomes.

## Access incident

An initial filename-discovery command inadvertently included the wider harness project and emitted path metadata from other work directories. No contents of those files, clinical measurements, target statistics or outcome reports were read. The parent was informed immediately; subsequent access stayed within the three assigned roots and explicit interfaces. No such metadata informed the mathematical or readiness conclusions. `target_results_used` is false for every review.
