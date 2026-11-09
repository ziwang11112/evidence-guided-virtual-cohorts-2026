# Independent result review

**Passed integrity, endpoint-coverage and arithmetic checks. No overall improvement claim is supported.** This review used sealed generated tables and the already retained reference aggregate after author closure. It did not run a generator, access patient rows, change the closed bundle/design/evaluation, or rerun test suites.

## Closure and complete coverage

All **176** sealed bundle files and the complete inventory match `AUTHOR_CLOSED.json`; prospective design hashes, execution receipt/output hashes, evaluation/reference bindings and the retained recomputation binding agree. The session completed with `candidates/initial` selected. There was one candidate, no submitted revision, and three distinct successful 3,000-row program outputs at seeds 9501/9502/9503. Current initial-to-final changes are therefore zero.

Every run retains three primary analyses and 23 diagnostics: **78/78 computed endpoint records**, no omitted endpoints, failed executions or unavailable generated endpoints. Five endpoints per run have existing-sample references; the other 21 are generated-only diagnostics.

The retained independent recomputation checks all 78 values, with maximum absolute difference **5.33×10⁻¹⁴**. I audited its formulas, finite/rank handling, coverage and provenance gates. A further implementation independently residualized BMI and each lipid on intercept, age and female indicator using QR, applied the Frisch–Waugh–Lovell slope identity, and correlated the full-model residuals. Together with independent sample-SD calculations, all **15/15 additional checks** agree, maximum difference **1.78×10⁻¹⁴**. These tolerances concern floating-point arithmetic, not clinical equivalence.

All 26 current stage means/ranges, the previous selected-stage means/ranges for the five comparable endpoints, reference values/units, and cross-run absolute-distance changes were verified.

## Mixed scientific comparison

| Endpoint | Previous selected mean | Current mean | Existing sample estimate | Change in absolute point distance |
|---|---:|---:|---:|---:|
| HDL BMI slope, mg/dL per 5 kg/m² | -1.1898 | -0.9882 | -4.6230 | +0.2016 |
| TC BMI slope, mg/dL per 5 kg/m² | 10.6997 | 8.1278 | 5.6831 | -2.5720 |
| Residual TC–HDL correlation | 0.1383 | 0.1517 | 0.5121 | -0.0134 |
| TC sample SD, mg/dL | 46.1168 | 31.5290 | 42.8466 | +8.0474 |
| HDL sample SD, mg/dL | 14.5611 | 17.8231 | 20.1756 | -3.2620 |

Negative distance change means closer to that sample point estimate. The TC slope and HDL SD are closer. TC SD is farther away and numerically lower than the comparator; the HDL slope is weaker and farther away. Residual correlation changes little and remains low. These endpoint-specific differences do not establish an overall gain, and the mixed units must not be pooled into an undeclared score.

## Source feedback and retained limitations

Per seed, strict feedback has **0 computed / 29 unavailable** checks. Descriptive feedback has **26 computed / 3 unavailable**: 22 assumption-labelled definitions, four known weighting mismatches and three unsupported definitions. Known mismatches have null source differences; no strict result is promoted. These source diagnostics are not population replay, independent validations or proof of target transport.

Recomputed retained measurement counts agree exactly. TC is below 100 mg/dL in 60/65/53 rows and above 400 mg/dL in 1/0/0 rows. HDL is outside 20–120 mg/dL in 23/19/15 rows; the alternative 15–100 range gives 68/59/64 rows. The manufacturer ranges describe product measurement limits, not biological bounds. Separately, HDL>TC occurs in **6/2/3 rows, 11/9,000 in total**. This is a component-consistency defect for the intended concentration interpretation, distinct from the device-range exceptions. All such rows remain in the analyses. Historical strip identity/censoring, assay transport and joint-distribution validity remain unresolved.

Three operational failures are retained in the action record: one excluded-alias search, one invalid search-argument request and an early preflight error. They occurred before generation; the corrected candidate subsequently completed all scheduled executions. Retrieval used 2/32 query units, 3/32 shared downloads and 22/64 controller actions. The native discovery log is outside those transport counters, so these are not total network/model costs. The stop was an author retention decision, not budget exhaustion.

The existing aggregate was already exposed in earlier development; this is not new independent clinical confirmation. Seed ranges describe finite Monte Carlo variation, not clinical confidence intervals. Supplied reference slope intervals retain their conditional HC3 sensitivity interpretation and are not equivalence margins. There is no real-versus-real variability benchmark here. Author, evidence, model construction, feedback interface and seeds differ across the two sessions, preventing causal attribution of changes to one feature. Procedural closure and hashes do not establish OS-level isolation or cryptographic authentication against a host user.

No critical integrity or numerical finding remains. The detailed checks, bindings and per-run recomputations are in `INDEPENDENT_RESULT_REVIEW.json`.


## Final report and figure claim review

`RESULTS.md`, the plotting code and the regenerated PNG were checked against the verified results. The figure correctly shows all five previous/current endpoint means and seed ranges, with readable labels, the correct units and existing-sample reference lines. Shaded bands are confined to the supplied slope intervals and explicitly distinguished from equivalence margins. The report accurately states mixed outcomes, the one current HDL seed outside its supplied interval, the lack of overall gain, and the separate 11/9,000 component-consistency defect. No material report or figure error was identified. Exact hashes of the reviewed report, plot code, PNG and PDF are retained in the JSON.
