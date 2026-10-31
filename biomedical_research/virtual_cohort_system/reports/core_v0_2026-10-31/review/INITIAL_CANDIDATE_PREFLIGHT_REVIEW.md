# Independent initial-candidate preflight

Date: 2026-10-31. Decision: PASS for the planned seal and initial execution, subject to unchanged reviewed bytes. This is static and analytic review, not runtime or scientific validation. F1 readiness remains pending the actual execution/feedback/decision chain and independent output recomputation.

Reviewed the current controller, task/source identity, all eight initial candidate files and author disclosure. Read the generator as text only; no import, sampling, generator execution, test suite, literature retrieval, historical candidate or patient reference was used. Current file bindings are retained in INITIAL_REVIEW_BINDINGS.json.

Source extraction is faithful: at exact x=0,1,2 within group=0, the arithmetic means are 2,3,4 u and individual SDs are 1,1.5,2 u. Source locators, selection, units, unknown uncertainty and absence of sample sizes/family/tail information are preserved. The source is explicitly artificial. The copied source hash matches the admitted record.

Analytic population-moment review:

| x | Shape k | Scale theta, u | k*theta, u | sqrt(k)*theta, u |
|---|---:|---:|---:|---:|
| 0 | 4 | 0.5 | 2 | 1 |
| 1 | 4 | 0.75 | 3 | 1.5 |
| 2 | 4 | 1 | 4 | 2 |

The gamma choice is compatible with nonnegative y and finite supplied moments, but is not identified by them. Strictly positive continuous support, no point mass at zero, tail shape, row independence and plug-in treatment of source moments are explicitly named assumptions. No interpolation, causal law, group contrast or source-uncertainty distribution is inferred.

The generator's only top-level statements are a docstring, NumPy/pandas imports and generate. It rejects non-null observed input, reads scientific settings from the specification, initializes the supplied seed once and draws once per stratum. It contains no empirical centering/scaling, moment forcing, trial loop, sample rejection, seed search, file access or external lookup. The declared repeat/count logic yields 256 rows per x stratum, 768 in total, group=0 and sequential unique synthetic identifiers. Actual numeric output and runtime support still require the isolated run.

All six source operators use the matching evidence item, kind mean or sd, y column, unit u, exact group=0 and x-stratum equality filters, missing_policy=error and approximate status. SD checks additionally disclose the prescribed ddof=1 convention and unknown source divisor. Plan population equals task population. No threshold is introduced and no check is omitted.

All specification parameters have evidence/assumption provenance. The initial check ledger binds the two real static reports; their hashes match. The scientific-file hashes recorded by those reports match the reviewed files. The contract report intentionally records the earlier checks.json snapshot before that report was bound into the ledger, and states this scope; the different final ledger hash is not a stale scientific-artifact claim. Root also reported a completed native controller preflight on the final candidate with no sampling. This reviewer did not rerun it.

Both issues from CONTROLLER_PREEXEC_REVIEW.md are resolved in the reviewed controller. Preflight now checks exact mean/SD operator fields, missing_policy and exact integer filter fields before execution. Shared final_submission verifies the authentic initial report, initial receipt hashes, byte-identical copied report and checks binding, and unchanged evidence/recipe. The final run then verifies the frozen initial parent hash and exact revision record; native lifecycle verification establishes the revision index and retain/revise semantics. The fixed two-stage seed-26301 schedule, stage-start exclusivity and failure closure remain intact.

Technical invocation note reported by root: one preliminary controller import used an underscore folder spelling where the actual unit name contains hyphens and failed before any controller action. The invocation was corrected to importlib.import_module('work.core_v0_2026-10-31.run_integration'). This was a technical invocation correction, not an attempted scientific execution or sampling preview.

No further preexecution correction is required by this review. Bind the assembly before running; preserve initial bytes and both source-feedback stages regardless of discrepancies. This PASS does not establish biological validity, broader mode coverage, calibrated uncertainty, Agent-wide isolation or F1 completion.
