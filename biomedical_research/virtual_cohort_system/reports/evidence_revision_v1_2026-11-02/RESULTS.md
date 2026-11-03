# Evidence revision implementation results

The next scientific entrypoint is implemented and has passed targeted synthetic verification. This checkpoint establishes software behaviour and catches specific modelling errors. It provides no new clinical-generation result, no source-fit improvement, and no new target validation.

## What changed

The controller now requires explicit evidence-use records, a separate declared law for every source and target context, and an independently reviewed correspondence between those laws and the actual code. Source execution invokes `semantic_feedback_v1` explicitly. A separately reviewed qualified collector can calculate the two native Jansen OLS projections, Bao Pearson and MIND Spearman under explicit assumptions without converting unknown source weights into known weights.

The actual source/target bridge is reused. Its frozen source slots execute first; target slots are untouched and this entrypoint offers no target-dispatch function. Feedback retains every source result, unavailability, calculation failure and valid partial result. Qualified and strict results remain separate. A retained Agent decision binds the complete feedback digest and has its own byte commitment.

## Meaningful checks

- Missing evidence items, invalid source metadata hashes, unknown assumptions, incompatible strict claims and missing numerical bindings are rejected.
- Positive exponentials of nondegenerate lognormal variables are flagged as having divergent required moments. Gamma moment thresholds, dependence/cancellation, finite alternatives and bounded discrete laws are checked conservatively. Unsupported mathematical cases remain unresolved.
- Native statistic identities, separate adjustment sets, units, measurement mappings and source contexts are checked before arithmetic. Original reports and uncertainties are retained.
- A genuine source-only dispatch path calls the existing receipt/statistical machinery on invented outputs. No target execution or legacy feedback fallback occurs.
- Success followed by interruption, ordinary failure, late supplemental failure and malformed partial feedback retain their distinct states. Stop decisions remain possible for the supported interrupted states.
- Changed scientific files, stale/self approvals, altered decisions, mismatched feedback digests and repeated dispatch are rejected.

## Review findings and fixes

Independent reviewers identified missing per-context law coverage, one-way evidence/operator bindings, omitted qualification labels, missing decision commitments, incomplete failure reporting and unsupported incomplete-phase stop decisions. These were corrected and corresponding tests added. The numerical collector's arithmetic boundary now catches plain `ValueError` from the existing operator library, preserving other available comparisons instead of aborting all feedback.

Further integration review found that evidence labels and actual output names differ, and that binary sex is an integer bounded to 0/1 in the current task rather than a categorical column. Read-only reviewed aliases and explicit bounded-integer handling were added. A compatibility check uses the actual admitted definitions and task schema on artificial arrays; their original files are unchanged.

Independent static review found no unsound moment pass/fail rule in the currently supported declared grammar. This does not certify arbitrary generator Python. Independent code/law and analysis-condition review remains mandatory.

## Verification history

The component suites reached 41 evidence-use, 62 declared-law, 39 qualified-relationship and 14 controller tests. These are 156 distinct tests, not accumulated counts over reruns. The final integrated run and exact code hashes are recorded in `VERIFICATION.json`.

Earlier development failures are retained: the first controller test location exceeded Windows path limits; the next run exposed a test worker's attempt to exclusively create a pre-created output file and a misplaced interruption assertion. Those fixture errors were corrected. Qualified-collector development also retained an initial temporary-directory permission failure and fixture/schema corrections. A nullable-output test was replaced by a reachable extreme-finite arithmetic case because the whole-cohort contract prohibits nullable generated columns. No failed biomedical candidate was repaired or removed in this work unit because none was constructed or executed.

## Decision and next work

Proceed to the already bounded source-only integration after resolving source/target age-support representation and reviewing the complete candidate/context declarations. The old task's 35–74 bounds cannot represent all admitted source age supports; a reviewed common schema plus context-specific eligibility checks is required. Neither aliases nor better numerical fitting solve that issue.

The integration allowance remains one construction and at most three 1,000-row source tables, with no target tables. Only after this check should the separately frozen two-constructor developmental pilot be prepared. Its original 18-target/54-source proposed limits are not enlarged by this implementation. No new dataset, paper retrieval, paid API, HPC, training or scheduler was used. Existing CHNS exposure and all historical negative results remain recorded.

The current evidence supports continuing method development, not a claim that virtual biomedical data are now more accurate or ready to replace measurements.
