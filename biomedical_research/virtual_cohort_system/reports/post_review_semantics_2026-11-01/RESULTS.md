# S1 result: declared source semantics gate implemented

1 November 2026. **Decision: adopt the additive semantic collector for a future, separately frozen case; resume existing CHNS admission.** No new biomedical dataset was generated or evaluated in this unit. Method efficacy, faithful extraction and source-to-target transfer remain unproven by these tests.

## What changed and why

Three-model review adjudication identified that the legacy generic checker could accept a wrong coefficient term, reversed regression roles or an omitted filter while correctly calculating the resulting wrong statistic. Rather than alter a hash-bound historical engine, S1 adds `cohort_harness/semantic_feedback_v1.py` and a frozen `source_semantics_v1.json` candidate sidecar. New feedback has a separate folder and explicit entrypoint; old controllers have not automatically been upgraded.

Before calculating any source statistic, the new entrypoint checks all declared evidence/operator bindings: outcome/predictor roles, coefficient term, exact adjustment set, selection, event/denominator, quantile definition, units and required task operands. Unsupported weighting, transforms and unknown essential definitions yield unavailable feedback rather than substituted numbers. Source SD, estimate SE/CI, unknown source n and unestimated Monte Carlo precision remain distinct. Numerical differences are explicitly raw and unstandardized.

Independent review found further gaps in the initial implementation despite its 36 new passing tests: source and recipe unit labels could agree while task-column units differed; nonexistent filter columns could fail only after earlier arithmetic. Review also identified Boolean and string/numeric predicate coercion. These were fixed before adoption. Source-variable unit mappings now bind all referenced operands to the task, only explicit per-unit unstandardized OLS units are supported, task-column existence is checked, and incompatible predicate/operand types are rejected. No conversions or desired biological relationships were introduced.

## Verification and its limits

| Check | Actual result |
|---|---|
| Independently authored new test file, initial version | 36 passed; this did not cover the later review findings. |
| Root initial related regression | 98 passed in 10.87 seconds before the unit/type fixes. |
| Independently expanded tests on final code | 46 passed in 4.27 seconds. |
| Root final regression on final code | **108 passed in 11.43 seconds**, comprising the 46 new cases and 62 related legacy cases. No failures, errors or skips. |
| Independent static review | Passed for module SHA256 `9599e57e1e77f43fd34c249c420e1ef37da755abc13530a6f1a25a215b3393b7`; reviewer did not execute tests or inspect patient data. |
| Legacy preservation | All 38 exported legacy Python modules/tests matched their pre-unit export and local baseline. All 2,306 pre-existing `work` freeze-manifest hashes were unchanged. This count includes engineering fixtures and is not an experiment count. It checks manifest bytes, not every historical payload. |

The final command was:

```text
python -B -m pytest tests/test_semantic_feedback_v1.py tests/test_whole_cohort_feedback.py tests/test_source_checks.py tests/test_source_replay.py -q --tb=short --basetemp <new-local-test-directory> --junitxml <local-report>
```

Tests used invented rows and mocked program boundaries. No Agent-written generator was executed, no clinical target was opened, no new API was used, and no HPC or training was started. The test Agent's first two setup attempts encountered a default temporary-directory permission issue and a missing temporary parent; it then used a fresh explicit workspace test directory. These were setup failures, not omitted product-test failures. All fixture output remains local.

The gate checks consistency of declarations. It cannot detect a source copied incorrectly into both declarations, certify population applicability, estimate transport uncertainty, or reconstruct each source population. Source n remains metadata with prose scope; the legacy uncertainty item holds only one annotation, and sample-SD convention requires substantive source review. See the implementation guide and independent review for remaining limits. Passing S1 does not establish higher-quality virtual data, an Agent advantage, or a new scientific contribution by itself.

## Data and continuation progress

The wang Chrome extension opened CHNS's official UNC Dataverse successfully. Biomarker Version 1.0, file ID 7505013 (`biomarker_09.sas7bdat`), the publisher checksum, Public access and CC0 terms were verified. The companion individual dataset is Version 1.0 with custom terms. The earlier browser-access barrier is therefore superseded; actual compatible covariate files, schema, measurement mapping and source evidence remain unresolved. No participant file was downloaded and no target effect was calculated.

The existing three-family/six-new-original-study limits remain intact; zero new original studies were deeply audited during S1. CHNS is not yet admitted, and F2 is not frozen. Next work follows `docs/POST_REVIEW_CONTINUATION_2026-11-01.md`: establish the data/assay schema and genuinely external evidence, select approximately three scientific uses from those inputs, independently review and freeze, then construct and evaluate once under the bounded protocol.

The existing chat heartbeat was updated to this continuation and its ACTIVE state verified. No duplicate schedule was created. This foreground turn is **not** a verified scheduled run; that count remains zero for this unit. New work stops no later than 14 November 2026. Public export includes only allowlisted code, fixture test code, original documentation, metadata and summary checks; patient rows, fixture output, full papers and detailed local manifests are excluded.
