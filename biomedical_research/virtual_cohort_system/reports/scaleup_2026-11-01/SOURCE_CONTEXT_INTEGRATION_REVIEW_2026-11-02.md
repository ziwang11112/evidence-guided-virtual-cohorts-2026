# K02 source-context integration: independent design review

2 November 2026. Metadata/code/evidence review only. No target rows or outcomes, source participant data, searches, scientific execution, generator parameters or old-file changes. No old test suite was rerun.

**Recommendation:** add one case-local collector over already verified source-context generator executions. Keep `semantic_feedback_v1` mandatory and unchanged; add separate geometric-mean/threshold diagnostics through the reviewed `operators/contextual_statistics.py`. Do not add a generator runner in this unit. Execution awaits the frozen campaign source-run budget.

## What is ready, and what remains conditional

The packet supplies six sex/site contexts and 30 explicit point-statistic candidates: 24 geometric means (BMI, TC, HDL and derived non-HDL) and six strict-threshold low-HDL percentages. Its 18 age quantiles and 12 regression records remain contextual. Candidate extraction is verified; active checks are still empty.

All 30 numerical candidates retain original source weighting as `not_reported`. Consequently, **the current utility cannot authorize exact reproduction of their published estimators**, even for a well-declared source-context simulation. Equal-weight arithmetic is exact for the supplied synthetic values; equivalence to the published estimator is a separate, unresolved claim. Keep these meanings distinct:

| Result | Allowed meaning |
|---|---|
| `strict_status: not_computable` | The unchanged strict source check remains unavailable. |
| `diagnostic_available: true` | The specified unweighted formula is defined on a verified synthetic source-context output. |
| `scenario_status: conditional_computed` | A separately approved equal-weight source-context interpretation permits a raw comparison with the reported point estimate. |
| `exact_source_check_allowed: false` | Required for current Greiner records; original weighting is not established. |
| `task_population_proxy` | A different, separately approved target-context use; not enabled by this source collector. |

Do not change `source.weights` to `none` to make the utility return true. Preserve `reported_source_weights: not_reported` and a distinct equal-weight assumption ID. An independently reviewed assumption is a permitted interpretation, not newly established source truth. Even a future positive exact-check flag would certify consistency with a declared contract, not actual population reconstruction or biological transport.

## Reuse the existing mechanical linkage

The frozen ENSANUT bridge `work/autonomous_research_cycle2_2026-10-31/method/run_source_contexts.py` already demonstrates the useful pattern: `_common_spec` removes only `parameters.active_context`; `_child_bindings` verifies the exact child specification differs only in that selector; generator and remaining candidate artifacts remain bound to the parent; source tasks and feedback recipes are already frozen in the parent; successful execution receipts bind the resulting output.

Reuse that **mechanical rule**, without editing or claiming new capability for the old bridge. Its `_supports` preserves column identities, categories and units; its collector uses legacy `whole_cohort_feedback`, not semantic v1. `source_replay_v2` is also not a drop-in replacement: it is enrichment-only and uses supplied covariates. The new source collector should be restricted to declared whole-cohort source children with no `observed.csv`.

The Agent must author and freeze the common scientific model, every context's parameters/assumptions and the `active_context` mapping. Root may mechanically select a frozen context and validate its output; it must not tune a source-specific scientific parameter, rewrite a common model, or silently repair a failed source output. No global joint-distribution identification is required before this prospective feasibility work.

## Minimal additive schema

Use a frozen sidecar such as `source_context_feedback_v1.json`; do not widen old evidence/operator schemas. The following is a proposed field contract, not an executable case plan or approval:

```text
schema_version: 1
scope: source_context_diagnostics_only
bindings:
  source_packet_sha256
  evidence_sha256, model_spec_sha256, source_context_plan_sha256
  strict_recipe_sha256, strict_semantics_sha256
  operator_engine_sha256, adapter_engine_sha256
contexts[]:
  id                         # one of the six packet context IDs
  frozen_source_task_ref     # path + SHA256; whole_cohort, no observed input
  active_context            # must equal this context's frozen selector
  population_ref, measurement_ref
  assumption_ids[]          # Agent-authored definitions, including equal weights
checks[]:
  id, source_record_id, context_id, strict_check_id
  operator                  # exact reviewed utility schema, not legacy schema
  use: diagnostic_only | approved_source_context_scenario
  assumption_ids[]
  uncertainty_role: estimator_confidence_interval
  precision_weighting: false
approval_ref: null | {path, sha256}  # independent approval of exact scenario plan
inactive_record_ids[]        # explicit age/regression records and any omitted candidates
```

All references, field sets, unique IDs and required records must be validated before arithmetic. Check IDs must map one-to-one to packet records, source contexts and strict checks; no lookup by display label. The plan must disposition the full packet so omission cannot silently become selection of favourable constraints. Current coverage is 30 potential numerical checks plus 18 inactive age records and 12 separate inactive regressions; activation can be explicit and bounded rather than automatic.

For compatibility with strict v1, encode geometric means as `reported_other` with `statistic_name: geometric_mean`, retaining value, units, CI and locator. Their strict recipe has `status: not_computable`, `operator: null`; semantic definition is `unsupported`, never an arithmetic `mean`. Threshold percentages may use the existing `proportion` definition, but unknown source weights leave their strict result unavailable. The supplemental operator retains its extra `selection_missing_policy`; do not pass that extended object to v1 as if it were its old schema. Prefer the packet's explicit error policies rather than inventing complete-case deletion.

The minimal collector sequence is:

1. Run strict metadata preflight; reject malformed declarations. Verify the frozen parent/child linkage and a successful `generator.py` receipt for the named source child. Do not accept a caller-supplied CSV, direct-row route or target execution as a source replay.
2. Require and reverify the strict-v1 feedback for the **same child/candidate/run**, preserving every strict status, reason and null discrepancy. The collector must not fall back to the old approximate collector after a strict rejection.
3. Read only that execution's generated output through its frozen source task contract. Bind output bytes, execution receipt, task, parent/child freezes, common specification, source packet, sidecars and all calculation engines in the new report.
4. Derive non-HDL row by row as TC minus HDL in a separate in-memory frame; do not mutate the receipt-bound output. Commit the derivation and relevant scalar-table hash. Call the reviewed utility using the unchanged reported-source descriptor. Retain its availability/eligibility reasons and counts.
5. Return calculations descriptively. Only an explicitly approved source-context scenario may add `calculated − reported` as an unstandardized raw difference. Keep strict differences null, exact-source eligibility false, and target performance/uncertainty calibration unassessed. No combined loss, pass threshold, CI membership score or precision weighting is needed.

The utility's approval binds a complete contract including supplied values. A frozen **plan** approval must not be automatically re-labelled as that data-bound approval for each new seed. For Greiner the diagnostic/scenario route can leave utility approval absent and report why exact eligibility remains false; it does not need a fabricated positive flag. Independent scenario-plan approval is a separate record, analogous in principle to the existing conditional interpretation interface. That existing interface itself only supports Pearson/Spearman task proxies and must not be called as if it supports these new source summaries.

Keep source-context arithmetic in explicit native units: age years, BMI kg/m² and lipids mmol/L. The reviewed utility performs no conversion. A mg/dL source execution therefore cannot silently enter a mmol/L check. Either the Agent's frozen context produces source units through a reviewed lineage path, or a separately declared deterministic unit map must be bound and checked before calculation. The minimal collector may simply reject unsupported conversion. Unit conversion would still not establish assay, fasting or specimen equivalence. The historical bridge's invariant unit rule must not be claimed to solve this mismatch automatically.

## Assumptions the Agent must declare; genuine integration blockers

The Agent may choose an eligible-source conditional population model without simulating disease flags or adding them to K02. It must state the unresolved diabetes definition, pregnancy/HIV exclusions, age and sex/site composition, row-count choice, age distribution and joint dependence assumptions. Synthetic rows are not source participants; Table 1/2 counts are provenance, not forced synthetic N or precision weights. No invented health-mixture prevalence is needed. Marginal geometric means and thresholds do not identify the full joint law, but an explicit joint-model choice is sufficient to define a testable candidate.

Likewise, a lognormal inversion from geometric mean plus threshold prevalence is an optional Agent-selected distribution assumption, not reported fact; it may be incompatible with rounded inputs. CI endpoints cannot supply person-level or conditional residual SD. The anomalous Malawi urban female HDL interval and collapsed rounded intervals remain flagged metadata; no guessed correction or inverse-CI weighting. Age quantile conventions and regression raw/log mappings remain unresolved and inactive.

Actual blockers to a computable released check are absent or mismatched frozen context/receipt/plan bindings; unsupported units/scales; missing operands; failed output validation; nonpositive geometric-mean values; or an unapproved request for a numerical source discrepancy. Unknown weighting blocks an **exact published-estimator claim**, but need not block an explicitly approved equal-weight scenario. Unidentified dependence and unverified source-to-target assay/selection transfer are disclosed structural assumptions, not reasons to demand complete source identification or expand the literature quota.

## Independent failure cases for the new adapter

These are proposed focused implementation cases, not tests run in this review:

- A different candidate/run's valid receipt, changed output bytes, or manually supplied CSV must fail linkage; a failed/direct-row execution must not become source generation.
- Changing any common scientific parameter while preserving `active_context` must fail; switching only to the exact frozen context is permitted. Unknown/duplicate contexts and post-freeze source tasks must fail.
- A verified target output with source-looking sex/site labels must not acquire source replay status. Source and task proxy reports must remain distinct.
- `reported_other/geometric_mean` must stay strict-unavailable; renaming it `mean`, converting unknown source weights to `none`, or swallowing strict preflight errors must fail.
- Geometric mean of TC−HDL must use rowwise differences; an independently supplied inconsistent non-HDL column, nonpositive difference, missing operand or covert clipping must not yield an accepted result.
- Male `<1.03` and female `<1.29` mmol/L events must retain strict boundaries and an all-eligible-row denominator; `%` must not be confused with a fraction. A mixed-sex table cannot use one unstratified cutoff.
- A source CI must survive only as estimator-uncertainty metadata; any SD conversion, precision weight or silent anomaly correction must be rejected. Source group N must not overwrite synthetic N.
- Changed plan, packet, derivation, unit map, engine or approval must invalidate the bound report. A plan-only approval must not authorize the utility's distinct value-bound exact-check contract.
- Valid arithmetic with unknown source weighting may produce a diagnostic; without explicit scenario admission it must not produce an approved source discrepancy. Missing/unavailable records must remain visible, not disappear from summary counts.

## Reviewed identities

| File | SHA256 |
|---|---|
| `evidence/SOURCE_CANDIDATE_GREINER.json` | `34eeb0be18f7a9d015e9a7d2446beeb10beb134d389315c998a22199f7d7e753` |
| `operators/contextual_statistics.py` | `b2e899622802395124d22f6c74975bb3b286f49fe0633d46f1a61290c46d4b3f` |
| `cohort_harness/semantic_feedback_v1.py` | `9599e57e1e77f43fd34c249c420e1ef37da755abc13530a6f1a25a215b3393b7` |
| ENSANUT `method/run_source_contexts.py` | `a5d0acb50092e990c89e98eed58551b4c75365af5679bf08e1426364ae08aea2` |

Also read the Greiner operator/transcription reviews, utility README, and relevant source replay, conditional feedback, execution, lifecycle and contract interfaces. This recommendation approves neither a scientific generator nor a live check; it defines a narrow reviewable integration boundary. Only this new review file was written.
