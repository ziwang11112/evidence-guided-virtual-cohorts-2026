# Source-statistic semantic feedback v1

Status: additive implementation after the November 2026 independent reviews. This is a check of declared source meaning, not a new biomedical result. Existing collectors, controllers and frozen receipts retain their original behavior. Future controllers must explicitly select this entrypoint; failure must not fall back to the legacy collector.

## Why this exists

Numerical code can correctly compute the wrong scientific quantity. An adjusted regression coefficient cannot be checked by a different coefficient or by a regression with reversed outcome and predictor. A prevalence in a selected population cannot use a denominator silently conditioned on the event. Unit labels on two recipes can agree while the input column has a different unit. Allowing an `approximate` comparison does not make these mismatches acceptable.

The new collector validates the complete declared recipe before any numerical source operator is called. It then computes from the verified output of the frozen candidate. It does not execute a generator, inspect a target reference, fit parameters, or infer a measurement conversion.

## Candidate sidecar

Add `source_semantics_v1.json` before freezing a new candidate. It is automatically included by the existing candidate-file hash commitment. Do not add it to old frozen candidates.

Top-level fields are `schema_version: 1`, SHA256 hashes of the exact `evidence.json` and `whole_cohort_feedback.json` bytes, and a `bindings` array. There must be one binding for every feedback check, including checks declared not computable, with no extras or duplicates.

Each binding has the following required fields:

| Field | Meaning |
|---|---|
| `check_id`, `evidence_id`, `source_locator` | Bind the check to one evidence item and its exact recorded source locator. The evidence hash binds the source record and reported estimate. |
| `definition_status` | `specified`, `not_reported`, or `unsupported`. |
| `source_operator` | The declarative statistic as reported in the source. Null for unreported/unsupported definitions. Record outcome, coefficient term, adjustment set, intercept, filtering, missingness handling, event/denominator and quantile convention where relevant. |
| `source_variable_units` | Map every variable referenced by that source operator, including filtering, event and adjustment variables, to its source unit. Empty only for a null source operator. Identity measurement requires exact equality to task-column units. No automatic conversion is performed. |
| `weights` | `none`, `weighted`, or `not_reported`. Only `none` is computable in v1. |
| `transform` | `identity`, `nonidentity`, or `not_reported`. Only `identity` is computable in v1. |
| `source_n` | `{"status":"not_reported"}` or `{"status":"reported","value":123,"scope":"source analysis population"}`. The positive integer is source metadata, never the generated row count. |
| `uncertainty_role` | For a source SE/CI: `estimate`. For source SD: `individual_dispersion` or `unresolved`. For missing uncertainty: `not_reported`. |
| `reason` | A substantive explanation of the source interpretation or its unresolved status. |

Source operators use the existing declarative operator schema. Matching ignores predictor order and conjunction order, treats correlation arguments symmetrically, and normalizes set membership order. Boolean predicates are rejected because the task schema has no Boolean type; True must not silently mean numeric 1. It does not prove arbitrary logical equivalence. Duplicate or differently represented predicates may be conservatively rejected.

Means, SDs and quantiles must use their variable's unit. Correlations have unit `1`. An OLS coefficient must be explicitly unstandardized and per one predictor unit: `outcome_unit/predictor_unit`; if the denominator unit is `1`, `outcome_unit` is also accepted, and equal units can use `1`. Per-ten-unit effects and standardized coefficients require a separately reviewed conversion implementation; do not relabel them. Every source and recipe operand must name an existing task column before feedback arithmetic.

## Outcomes of validation

1. **Known mismatch or malformed binding:** reject the entire feedback request before any source statistic is calculated. Approximation does not bypass this rule.
2. **Unknown/unsupported essential definition, weighting or transformation:** return `not_computable`, a reason, and null calculation/difference. Do not invent a substitute.
3. **Matched declarations:** calculate with the established operator, retaining any old exact/approximate status and assumptions. The difference is an **unstandardized raw discrepancy**, not a calibrated significance test or a valid inverse-variance objective.

Missing source sampling precision alone need not block raw feedback. SE/CI of an estimate, individual SD, unresolved dispersion and unestimated Monte Carlo uncertainty occupy separate fields. Source n is not used to convert SD into SE. This version cannot represent both estimator precision and individual dispersion in one legacy evidence annotation. It also does not resolve cluster/observation/participant n, SD estimation conventions, source sampling design, or transport uncertainty. A sample-SD operator uses the existing ddof=1 implementation; faithful applicability must be reviewed separately.

## CLI and integration

Run from the project root; placeholders below refer to a new candidate and an existing verified execution:

```text
python -m cohort_harness.semantic_feedback_v1 preflight --bundle BUNDLE --candidate candidates/initial
python -m cohort_harness.semantic_feedback_v1 collect --bundle BUNDLE --candidate candidates/initial --run-id RUN --feedback-id FEEDBACK
python -m cohort_harness.semantic_feedback_v1 verify --bundle BUNDLE --candidate candidates/initial --run-id RUN --feedback-id FEEDBACK
```

Preflight reads declarations only and can run before freezing. Collection requires the frozen sidecar and a successful verified execution. New reports go to `semantic_feedback_v1/FEEDBACK/feedback.json`, separate from the legacy folder. Existing IDs cannot be overwritten. Verification recomputes the report and checks exact equality including its source/output/runtime bindings. Hashes are commitments, not host-security signatures.

A new revision controller should give the Agent only these approved source diagnostics, preserve unavailable checks, and bind the selected entrypoint/version in its protocol. This document does not claim that an old controller has been upgraded or that a live Agent revision has already used v1.

## Scientific boundary

The sidecar must be authored from the actual source and independently reviewed; copying the recipe into it would test self-consistency only. Agreement does not certify source extraction, population matching, correct assay definitions, or transferability. Current collection still evaluates a whole-cohort output under the task conditions; it does not reconstruct each source population. Generating scientifically useful data, including whole cohorts without individual input, remains the research goal. This gate prevents one class of invalid feedback from confusing that evaluation.

Tests use invented direct rows only. Passing them supports software correctness for the tested cases, not superior synthetic biomedical data or patient-level recovery.
