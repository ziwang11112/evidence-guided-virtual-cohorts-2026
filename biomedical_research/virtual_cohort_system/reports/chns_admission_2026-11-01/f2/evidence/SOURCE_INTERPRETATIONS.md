# Proposed source interpretations and fixed feedback boundary

Coordinator review artifact; **not an admission, candidate approval or builder mount**. The task's age 35–74 range is a prospective design choice, not harmonization with Bao's age eligibility. No new original, target value or scientific output was read for this proposal.

## Proposed checks

| Fixed check | Original reported quantity | Original source scope and precision | Conditional task calculation |
|---|---|---|---|
| `bao_pearson_glucose_hba1c` | Bao Methods names Pearson; Results paragraph after Table 1 reports r=0.619 for fasting plasma glucose and HbA1c. | Selected SHDS II analysis n=4,886; pair n, SE and CI unknown; P<0.001 is not precision. Original weights and correlation missingness rule unreported. | Equal-weight Pearson of generated `glucose`/`hba1c`, unit 1, no additional row selection. Task glucose is central serum, not source plasma. |
| `mind_spearman_serum_glucose_hba1c` | MIND Methods names Spearman; full-sample glycemic-correlation Results report rho=0.529 for serum FSG and HbA1c. | Selected older rural sample n=3,547; pair n, SE and CI unknown; P<0.001 is not precision. Mean/mode imputation reported, affected fields/effects unknown; weights and tie convention unreported. | Equal-weight Spearman of the same generated columns, unit 1, ranking complete pairs with average ties. Target/source instruments, handling, population and timing remain different. |

The textual Bao locator is retained with the article URL. An unverified `#p-22` fragment from the older candidate JSON was removed; no new browsing was needed. The mathematical Pearson/Spearman labels are direct reports, while conventional equal weighting and MIND average ties are explicit interpretation assumptions.

Both operators use `selection: []` and `missing_policy: error` on the already complete generated task table. No source medical/age/diagnosis filters are simulated; the source-specific exclusions remain descriptive provenance and transport limitations. Empty selection means the entire generated target analysis population, not a claim that the original source study had no eligibility restrictions.

## The important missingness distinction

`source_semantics_v1.json` is a **proposed declaration of the named mathematical functional**, not a reconstructed source data-processing program. Its `definition_status: specified` and `transform: identity` identify the reported-variable correlation functional and no numerical scale conversion in this comparison. They do not certify every original preprocessing step. The original missingness facts stay unknown/qualified in the evidence and source summaries.

In particular, `missing_policy: error` is the generated-input guard: if the provided complete target table does not supply the required finite values, do not silently perform pairwise deletion or imputation. It does **not** assert that Bao or MIND raised an error on missing source records. The proposed interpretation compares a reported post-analysis-distribution correlation with the functional on generated complete target analysis values; it does not replay Bao's unknown deletion rule or MIND's unknown field-specific imputation effects. This assumption has to be accepted explicitly by independent scientific review. If original processing is judged essential and this interpretation inadequate, decline the affected proxy. Do not change unknown provenance into a known source implementation to make the check pass.

The identity arithmetic mode is likewise not a declaration of plasma/serum, instrument, population or sampling equivalence. No multiplication, unit conversion, source-context generation or source-specific resampling is implemented here. The supplied separate equal-weight, post-analysis-value, population/measurement and average-tie assumption records must retain their exact approved wording.

## Actual files and later candidate binding

- `whole_cohort_feedback.json` fixes exactly two `approximate` strict checks and the actual task population. It contains no held-out target coefficient or evaluation formula.
- `source_semantics_v1.json` binds the evidence and recipe bytes. Both original weights stay `not_reported`; pair-specific source n and estimator uncertainty stay `not_reported`. Therefore both strict rows must remain unavailable with null calculations/discrepancies.
- `FEEDBACK_POLICY.json` uses the controller's agreed exact schema: recipe hash, semantics hash, full required assumption records and the two allowed exact conditional interpretation objects.
- `SOURCE_FEEDBACK_REVIEW.json` retains the richer scientific qualifications and supplied-value scope separately from that machine policy.
- `SOURCES_ADMISSION.json` records all 16 source-item roles, dependencies, provenance, omissions and pending review status. It is not an automatic approval of the two optional interpretations or the remaining contextual items.

A candidate may accept zero, one or both policy entries after independent review. Omitted interpretations require approved reasons. The strict recipe remains unchanged; there is no obligation to fit either source or force a revision. Required assumption text is explicitly conditional on use of the corresponding optional proxy, so retaining it does not force source-based modelling when the proxy is declined.

The constructor still chooses the model and scientific parameter values. It must not edit the fixed source facts, recipe, sidecar or allowed interpretation objects. Its own `model_spec.json`, model hash, builder identity and candidate-dependent conditional plan/independent approval are not supplied here. The controller must bind them later, require strict verification before conditional arithmetic, and preserve source/evidence/assumption context in every returned report. No actual candidate is frozen by preparing these templates.

Only the two correlations are possible numerical source feedback. Bao medians/quartiles, MIND means/individual SDs, derived source female count ratios, Jansen native-scale separate coefficients, Pani's known weighted coefficient and NGSP unit guidance remain context without numeric checks. In particular, incomplete Jansen CI information stays incomplete; Pani is not admitted to the equal-weight correlation exception. The MIND conflicting agreement bundle and dependent derivatives remain quarantined and absent from builder numeric records.

These two numbers cannot identify or validate the whole target joint distribution. They must not be averaged into a source-loss score, used to infer source precision, or interpreted as independent target validation. The reports are assumption-defined target proxies with zero additional source-context tables. Final scientific evaluation remains outside this packet and outside revision feedback.
