# Independent audit v2 repair

The original blocked review remains in `CODE_REVIEW.md` / `CODE_REVIEW.json`. The original `recompute.py`, `test_recompute.py` and `CODE_COMMIT.json` are unchanged. The frozen primary evaluator, providers, original pure operators and analysis metadata are also unchanged: all 11 previously reviewed input hashes were checked again and matched. This repair changes the independent audit implementation; it does not change scientific estimands, the generation protocol, or primary results.

`recompute_v2.py` is ready for the separate review requested by the coordinator, before any common evaluation or result comparison. This author does not certify its own repaired code as independently reviewed. No clinical-reference artifact or retained generated output has been opened, no campaign evaluation has run here, and the new code has not been exercised on clinical results.

## Quantile convention

The new quantile arithmetic keeps original row weights and stable value order. It does not pre-normalize weights. For each sum `updated = total + mass`, `math.fsum((total, mass, -updated))` recovers the addition's lost mass; these residuals are accumulated separately, and each prefix is `total + lost`. The cutoff is probability times the same final compensated prefix. Search is left-sided, zero-weight entries are removed, and no tolerance, interpolation, midpoint or adjacent-order-statistic allowance is used.

This is independently written error-recovery arithmetic for the prescribed compensated-prefix convention. The generated weights remain exactly `1.0 / (8 * count_for_this_cell)`. Integer cell counts and products are exactly representable at the declared size, so the original engine's `8.0 * counts` denominator and v2's integer product produce the same raw weights. The tests deliberately retain these binary weights rather than replacing them with ideal rational probabilities or normalized weights.

Five quantile fixtures were independently authored by `/root/main_review_g8/v2_quantile_fixtures`. Their oracle sums exact binary float ratios as Fractions, converts each prefix to the prescribed floating representation, and cross-checks the declared pinned compensation semantics. Tests cover 3,000 equal quota weights, q=0.1/0.5/0.9, adjacent representable cutoff probabilities, eight uneven cell counts totaling 3,000, deterministic interleaved/reversed orders, ties and zero masses. Every selected observed value must match exactly. The report audit also checks quantile endpoint values exactly, while ordinary smooth regression/mean arithmetic retains the declared numerical comparison tolerance.

## Failure and summary audit

The audit now derives the expected 72 constructor/seed identities, execution statuses, candidate/run identities, closure statuses, failure records and successful output hashes from verified session events. It does not trust the result report's execution status to choose files. The complete endpoint ID set is required in every category, and all six prescribed case/analysis contrast identities are required.

A primary `provider_error` remains a failure with unavailable endpoints. Separate independent computability is recorded without replacing the failed primary values or claiming to have reproduced/validated that provider failure. Such an otherwise structurally matching report has status `matched_with_preserved_provider_failures` and `complete_numerical_validation=false`. Unattempted/execution-failed or analytically unavailable slots remain in every denominator and also prevent complete numerical validation. A matched report with those slots is labeled `matched_with_unavailable_slots`.

All 24 construction summaries and four statistical-reference summaries are independently rebuilt from effective available values. Three seed discrepancies are averaged within each constructor before averaging the five agent constructors in each arm. Complete and available-only counts, mean effects, ranges, directions, arm summaries and the six complete/incomplete contrasts are checked. The available-only incomplete contrast is explicitly audited; a missing constructor, endpoint or contrast cannot produce a match.

Global closure still precedes reading the code manifest, results, aggregate references or generated outputs. V2 checks its own commitment before reads and again before writing, rechecks closure, and writes its audit report exclusively. Reference aggregates are mapped by fixed IDs/paths and units only after the barrier; original clinical reference arithmetic and reference interval recomputation remain outside this audit's scope.

## Verification and commitments

Command actually run: `python -B -m unittest test_recompute_v2 test_recompute_v2_quantiles -v`. All **12 tests passed**. These are new deterministic fixtures for invented projections, rank failure, exact quantile boundaries, full report inventories, construction-first aggregation, provider/execution failure handling, summary corruption detection and the early closure barrier. The original three tests were not rerun.

`TEST_RESULTS_V2.json` retains the actual command/outcome, the tested file hashes and all preserved input hashes. `CODE_COMMIT_V2.json` was written only after those tests passed, binding the new code, test files and test record. The committed code hash is `6935190058ba2d201c35de84195c13a993627740e54126cc2a3f5247bca9189e`. External independent review is pending before any clinical comparison.
