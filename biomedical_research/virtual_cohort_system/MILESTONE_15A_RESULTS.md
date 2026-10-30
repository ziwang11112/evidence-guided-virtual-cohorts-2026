# M15-A: direct Agent-authored rows, source-only pilot

30 October 2026. **A fresh Agent directly wrote 128 fictional rows without a statistical sampling program. The table closely matched the supplied marginal summaries, but all four withheld urate SDs were too small. After one numerical feedback pass the Agent retained its table unchanged.** This establishes an actual direct-table path and a feedback/retention cycle; it demonstrates neither successful data repair nor independent biomedical analytical validity.

The user asked whether direct Agent generation followed by direct revision was worth trying. This small run tests that route separately from the previous Agent-authored-program route. The M13-B body-fat target was not reopened, and no new target or patient records were acquired. Broad urate target admission remains unresolved; this experiment is explicitly a narrow source-summary illustration.

## Inputs, authorship and actual schedule

The evidence is Yun et al. (2021), Bogalusa nondiabetic adults aged 20-56, [DOI 10.1038/s41366-021-00810-9](https://doi.org/10.1038/s41366-021-00810-9), Table 2 Adult cohort. Original EuropePMC full-text XML and methods were checked. The four original group counts are 1,012 White men, 1,209 White women, 509 Black men and 672 Black women. The pilot's 38/46/19/25 allocation approximates those proportions at 128 rows; it is not a sample of those participants.

One fresh-context builder received a screened excerpt with exactly 20 moments: age mean/SD, BMI mean/SD and urate mean in each group. All four urate SDs were withheld from its packet and feedback. No BMI-urate coefficient, curvature, interaction or conditional dispersion estimate was supplied. The entire generated table, including age and BMI, is fictional; this is whole-cohort direct authorship rather than enrichment of real observed covariates.

The actual sequence was:

1. Freeze the task, source excerpt, evaluator, prompts and four same-source holdouts; independently inspect the information boundary.
2. The Agent writes a literal `generated.csv` via `apply_patch`, a model specification and a concise decision. It chooses positive BMI-urate ordering with crossovers, mixed ages and bounded urate spreads as explicit assumptions.
3. Validate and freeze the initial candidate. The existing direct-row adapter copies and validates the submitted bytes; both execution receipts state `generator_executed: false` and `backend: direct_rows_validation`.
4. Return one numerical report containing only the 20 supplied moment discrepancies and technical validity checks.
5. The same Agent decides **retain**. It accepts the remaining age/BMI discrepancies and does not claim that correcting them would establish the unsupported joint structure. The controller copies the unchanged CSV/model bytes, binds the actual feedback, and freezes the final child.
6. Only after both freezes and their lineage verify, evaluate the four withheld SDs and the fixed exploratory analyses. These results are not returned to the builder; no further attempt is made.

There is one unique directly authored table and two frozen lifecycle versions, not two independently generated populations. The controller did not populate, sample, rescale, optimize or repair data values. Literal authorship is supported by the builder's submission route/declaration and absence of a generation program; lifecycle hashes alone cannot prove an LLM's internal computation. No claim is made about an inaccessible exact model backend identifier, token cost or reproducibility of a future LLM call.

## Supplied statistics: close agreement

Errors are absolute relative discrepancies from the printed source values. SD uses n-1. These are descriptive engineering summaries, not clinical equivalence measures.

| Supplied set | Number of summaries | Mean absolute relative error |
|---|---:|---:|
| Age means and SDs | 8 | 1.12% |
| BMI means and SDs | 8 | 1.63% |
| Urate means | 4 | Approximately zero, within floating-point precision |
| All supplied moments, equal-weight descriptive aggregate | 20 | 1.10% |

The largest acknowledged errors include White male BMI SD 5.558 rather than 6.0, Black female age SD 11.169 rather than 11.8, and Black female BMI SD 8.329 rather than 8.7. The four urate means are 6.1, 4.5, 6.2 and 4.6 mg/dL as supplied. Many values were deliberately paired around group centers. Exact centers therefore reflect authored construction, not recovery of patient measurements or exceptional scientific accuracy.

## Withheld source SDs: systematically narrow in this table

| Source group | Reported urate SD, mg/dL | Directly authored SD | Relative error |
|---|---:|---:|---:|
| White men | 1.30 | 0.8571 | 34.07% |
| White women | 1.20 | 0.9843 | 17.97% |
| Black men | 1.50 | 1.0536 | 29.76% |
| Black women | 1.70 | 1.0824 | 36.33% |

Mean absolute relative error is **29.53%**. The final values equal the initial values because no revision occurred. These four summaries share a source and a single construction; they are not four independent clinical validations. They show that matching the visible means does not ensure the withheld marginal dispersion in this example. They do not show that every direct Agent table will underdisperse, or that its scientific associations must be wrong.

## Scientific-analysis use remains unvalidated

The same table can be analyzed, but no admitted independent reference is available for its joint relationships. The prespecified regression `urate ~ age + BMI + male + Black` gives age coefficient 0.008397 mg/dL/year, BMI coefficient 0.120103 mg/dL per kg/m2, and descriptive R-squared 0.873877. The centered/scaled quadratic BMI coefficient is 0.007839 and the separate male-by-BMI interaction is 0.028220, with BMI scaled per five units in those models. These coefficients arise from the authored joint structure. R-squared is not a measure of clinical prediction accuracy here.

The fixed within-sex quartile descriptions and all regression outputs are retained. They have no correctness labels, p-values or clinical confidence intervals: 128 authored rows do not create 128 independent empirical observations. We did not compare the BMI slope to Yun's differently adjusted/standardized coefficient or invert the overlapping Bogalusa paper's reverse regression.

The withheld SD discrepancy is useful for checking distributional breadth, but it does not answer the user's main question of whether generated data support similar scientific conclusions. That requires a separately designed measured-data comparison with compatible analyses and a frozen information boundary. If previously exposed data are used for development, they must be labeled development, followed by fresh confirmation for stronger claims.

## What this run establishes and does not establish

- Direct data authorship is implemented and actually exercised. Every scientific cell in the unique table came from the Agent's literal submission, rather than a fitted sampling program.
- Source-summary agreement can be very close while a withheld property remains wrong. More direct authoring does not remove the need for evidence about joint dependence and variation.
- A real feedback review occurred, but the scientific decision was retention. This run supplies **no evidence of a repair benefit**, and it would be incorrect to describe it as a successful correction loop.
- No conventional-generator comparison, independent cohort validation, clinical substitution, causal recovery, cross-model replication or novelty claim is established.
- Parent/controller Agents knew the holdouts; the builder's separation was procedural, not a filesystem sandbox, and pretraining recall cannot be excluded. The holdouts are internal source summaries, not external validation.

Stop this one-feedback pilot at its frozen budget. Keep direct generation as a viable implementation route. The next useful experiment would test a small number of actual scientific analyses against measured data, with evidence appropriate to those analyses and explicit development/confirmation status. Adding more controls or forcing this builder to change an already revealed table is not part of this run.

Independent post-run review recomputed all 20 supplied and four withheld summaries for both frozen versions using a separate csv/math implementation. Its 214 numeric comparisons agreed to a maximum discrepancy of 7.11e-15. Candidate identity, both direct-row receipts, feedback lineage and all 20 precommitted artifacts plus 17 harness files verified. The optional exploratory regressions were not independently recomputed; their outputs remain descriptive and have no empirical correctness claim.

Detailed local artifacts are in `work/m15a_direct_rows_2026-10-30/`: frozen protocol/evaluator, screened input, initial/final candidates, one feedback, direct-row receipts, full aggregate evaluation and independent review. Generated row tables and the original source full text stay local. No core harness module, training job, HPC job or recurring automation was added.
