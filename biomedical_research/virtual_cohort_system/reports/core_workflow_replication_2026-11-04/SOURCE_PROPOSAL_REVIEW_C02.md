# C02 independent source and proposal review

2026-11-04. **Decision: PASS_TO_IMPLEMENT_WITH_SOURCE_FLOW_NOTE.** No source-value transcription, unit, model-algebra or finite-moment defect was found in the proposed construction. Add the Singapore paper's unresolved participant-flow arithmetic discrepancy to the candidate's source-quality notes; it requires no change to the chosen law or reported analytic N. This releases implementation only, not freeze/execution or a claim of target validity.

## Materials and boundaries

Reviewed C02 task/request metadata, source request, proposal and search ledger; inspected the admitted original XML methods, results and cited tables for PMC5078665.1, PMC3504343.1, PMC5009131.1 and PMC7272077.1. All seventeen registered artifacts match their hashes. Gateway state confirms six query credits and four original downloads, exhausting the original-read allowance. These are Pinggu, Singapore Prospective Study Program, Changchun REACTION and Hoorn populations; none is a CHNS or ENSANUT participant study. Original-text alias scans found no excluded-cohort mention. Unreported overlap cannot be disproved by this check.

No new source, old model, target outcome or participant/generated row was read. No author script or candidate code was executed. Independent calculations used only the cited summary numbers and proposed equations, without random sampling. Frozen controller files were not modified. The reviewer has historical project-result exposure and provides no target-directed coefficient or desired sign.

## Source findings

- **Pinggu P1:** Table `tab1` matches the reported two exhaustive DR strata (40 and 3,084), all BMI/FPG/HbA1c mean/individual-SD pairs, male percentages and age summaries. The footnote distinguishes means/SDs from medians/IQRs. The main analysis retained known diabetes; the later exclusion of 165 known cases is a separate analysis. Sampling/response/exclusion counts and delegation of detailed assay methods to the unadmitted reference are represented correctly. The unverified age eligibility/assay details remain unavailable.
- **Singapore P2:** Table `tbl2` contains the three quoted coefficients and their SE/CIs. Chinese is the glucose reference group, with ethnicity-by-glucose interactions; age/sex effects are shared. The complete listed adjustment set is materially broader than the proposed five-variable model. Results explicitly identify Pearson age–HbA1c 0.208, **log-BMI**–HbA1c 0.21 and FPG–HbA1c 0.79. Table 1 values are SEs/adjusted means and have not been used as individual SDs. The ten-hour fast, plasma assay, HPLC and known-diabetes exclusion are accurately represented.
- **Concrete source-flow note:** The Singapore paper states 5,157 examinations and exclusions of 325, 932 and 2, which arithmetically leave 3,898, while its reported analytic N and ethnic-group counts total 3,895. Preserve reported N=3,895 and flag the unexplained three-person difference; do not invent another exclusion or silently rewrite source counts. No model parameter depends on resolving this discrepancy.
- **Changchun P3:** The age >=40/residence/clinical exclusions, 7,611-person analytic sample, venous glucose versus fingertip HbA1c, 8–14-hour fast and cited means/SDs match. Using its sex differences as a warning about the model's simplifying independence is appropriate; diagnostic cutoffs are not regression coefficients.
- **Hoorn P4:** The two samples, exclusion schemes, differing assays, multiple imputation, Spearman correlations 0.32/0.42, age effects per 7.3/6.7-year SD, female effects and quartile BMI terms match. Dividing age coefficients by the named source SD gives the stated per-year context. The admitted response indeed warns about correlated body-size predictors. These are correctly retained as context rather than pooled as task-equivalent slopes or raw Pearson coefficients.

## Independent arithmetic and joint law

Pooled Pinggu moments, using within-stratum `(n-1)` variance and between-stratum sums, reproduce:

| Variable | Derived mean | Derived individual SD |
|---|---:|---:|
| BMI | 26.1961587708 | 3.7995413169 |
| Glucose | 5.9320102433 | 1.5485844068 |
| HbA1c | 5.6204865557 | 0.9294965154 |

The female probability is 0.5207042254. These digits reflect arithmetic on rounded published inputs, not extra source precision. The unused pooled age summary also reproduces; it was not substituted for the task's age design.

Independent deterministic integration/bisection of the discretized latent-normal age law gives `Cov(A,G)=3.1754476999`, latent `rAG=0.1908002627`, `rBG=0.2679885345`, determinant 0.8917774051 and minimum correlation-matrix eigenvalue 0.6710279725. The exponential-tilting integral for age–glucose covariance and lognormal identity for glucose–log-BMI covariance are valid. They reproduce the stipulated model correlations 0.208 and 0.21; the latter remains a log-BMI correlation.

Residual variance is 0.26031528394, uniform half-width 0.88371140755 and conservative HbA1c lower bound 2.9030342391. Thus variance is positive and positivity follows from support, not clipping. The derived E1 coefficient is 0.05153367947. E2 and E3 equal the assigned conditional coefficients by the specified conditional mean and residual orthogonality. These are mathematical consequences of author choices and transported information, not independent target findings.

Bounded age/sex/residual, finite-order lognormal moments and the affine HbA1c relation establish the required second/fourth mixed moments. The nonsingular latent law, nondegenerate age/sex and continuous predictor variation support full-rank population designs. Actual finite output, numerical endpoints and finite-sample rank remain implementation/execution checks.

## Meaning to retain during implementation

Preserve the omitted-covariate/reduced-model transfer assumption for all P2 coefficients; the zero direct BMI term and allocation through glucose are structural assumptions, not a reported null or causal mediation. Keep P1 moment transfer, uniform age composition, age–BMI independence, predictor/sex independence, lower glucose shift and tail/residual choices explicitly identified. Do not label matching of the transported correlations as recovery of the actual Singapore joint population.

For semantic feedback, `Corr(log BMI,HbA1c)` cannot become a raw-BMI Pearson check, nor can the rich P2 adjustment set be silently replaced by a task regression. Unsupported transform/adjustment operators remain unavailable; allowed all-row source comparisons are explicitly approximate target-population comparisons. P4 Spearman values cannot be substituted as Pearson. The source standard errors are evidence precision, not residual SDs.

Apart from recording the source-flow discrepancy, no new acquisition, coefficient selection or scientific redesign is requested. Preserve the current proposal and proceed to candidate implementation with the existing two-round mechanical/source-review limit.

## Reviewed identities

- Source request: `ae77702672ad24b4e2b2261667a7fd8a538cd8d199f25c60503c1ad93df75a15`
- Proposed construction: `f9d357bcfc44e797460ab14275995f1d079f95d0ba454875366ddf47ea763d54`
- Search ledger: `86ed34f88a2e39928e281ac751b6354f508606545e1e1383f1136ad15ad97252`
- Task/request hashes match C02's protocol bindings. Original identities are the admitted hash-named XML paths in the reviewed request/registry.
