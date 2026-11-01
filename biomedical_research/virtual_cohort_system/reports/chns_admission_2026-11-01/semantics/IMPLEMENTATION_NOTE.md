# Conditional correlation diagnostics: implementation note

1 November 2026. New additive [module](../../../cohort_harness/conditional_feedback_v1.py) and [invented-row tests](../../../tests/test_conditional_feedback_v1.py). Pending the parent's independent code review before scientific use. No old collector, frozen candidate, receipt, state or export artifact was changed. No participant data, biomedical generator, source-context replay or new scientific table was used.

## Implemented scope

Only an independently approved conventional equal-weight interpretation of a source explicitly declared as Pearson or Spearman is supported. Original weighting must remain `not_reported`; known weighted and already-unweighted items cannot enter this interpretation path. Definitions and transforms must be specified/identity, source and recipe operators must match, units and variable types must match the task, and the strict recipe must already be explicitly approximate. Other missing semantic information cannot be repaired by this layer.

The module calls `semantic_feedback_v1.preflight` unchanged. Collection requires an existing strict feedback ID and calls `semantic_feedback_v1.verify_feedback` for the exact candidate/run. The original check must still be `not_computable` with null calculation and difference. No strict report is created, overwritten or relabelled, and there is no legacy fallback.

After that explicit strict verification, the new wrapper additionally compares canonical typed JSON against a fresh strict computation, preserving the existing timestamp. This rejects Boolean/integer-equivalent alterations that the inherited verifier's Python equality can accept, before conditional arithmetic. The old strict implementation remains unchanged.

The conditional report evaluates only the existing verified task-generated table, using `source_checks.apply_operator`. Its scope is `conditional_source_interpretation_target_proxy`, and each difference is an assumption-defined, unstandardized raw diagnostic. Source reproduction is explicitly not established; target performance is not assessed; uncertainty calibration is not provided. Runtime-undefined correlations retain a reason and null result.

Every conditional row now also includes the actual bound equal-weight assumption record, applicability assumption records, full original evidence-source record and full evidence item. Their existing population, measurement, selection and applicability text accompanies the number; no missing fields are invented. The model/evidence hashes bind these records. A revision prompt must retain this context rather than extract only the numeric discrepancy.

## Approval and freeze contract

Before candidate freeze, author `conditional_interpretations_v1.json` and an approval JSON inside the candidate. The plan binds task/evidence/strict-recipe/strict-sidecar/model-specification hashes, actual task population and builder ID. Each interpretation binds one unique strict check/evidence item, exact source identifier and locator, named estimator, matching operator, a declared equal-weight assumption, distinct declared task-applicability assumptions and a reason. There are at most 12 interpretations.

The plan's `approval` contains the approval file's relative path and SHA256. The approval contains the exact plan payload **excluding that approval reference**, avoiding a circular hash. It records an approved decision, different reviewer/builder IDs, explicit independence, review time, rationale, and a disposition for every evidence item. The approved item set must equal the requested interpretation set; quarantined and unapproved items cannot enter. The candidate freeze binds both files, and reports bind their hashes. Approved-payload equality and final report equality use canonical typed JSON so Boolean/numeric substitutions do not compare equal accidentally.

See the test fixture for the complete schema; it deliberately uses artificial sources and invented coefficients. Approval identities and source authenticity remain procedural declarations. Hashes are not signatures against a host rewriting all records, and this module does not prove that a reviewer actually read a paper or that the paper named the recorded method. Independent review must supply that substantive judgment.

## Invocation and validation

```python
from cohort_harness import conditional_feedback_v1 as conditional

conditional.preflight(bundle, "candidates/initial")  # declarations only; no table reads
# Freeze the candidate, execute through the existing adapter, and collect strict
# semantic_feedback_v1 separately before this call.
conditional.collect_feedback(
    bundle, "candidates/initial", "run01", "conditional01",
    strict_feedback_id="strict01",
)
conditional.verify_feedback(
    bundle, "conditional01", candidate="candidates/initial", run_id="run01",
    strict_feedback_id="strict01",
)
```

Reports occupy only `conditional_feedback_v1/<new-id>/feedback.json`. Existing IDs and extra files are rejected. Verification repeats semantic/approval/freeze/strict-report checks and arithmetic against the retained verified output. All interpretation gates run before strict re-verification or conditional arithmetic. No new controller or command-line entrypoint is installed; callers must explicitly select this API.

Validation: the independently authored conditional suite passed **33 new tests**. A subsequent combined invocation repeated these 33 tests plus **79 previously passed tests**, reporting 112 passes in 11.30 seconds with a fresh short workspace pytest base. This rerun was an **unnecessary scope deviation** from the heartbeat instruction not to repeat passed checks; it earns no additional new-test or scientific-evidence credit. An earlier combined invocation hit a default temporary-directory permission failure during fixture setup; no scientific check ran in that attempt. No implementation change was needed to resolve the environment issue. No further test run is warranted absent an actual code failure or fix.

The tests independently calculate tied Pearson/Spearman results from invented vectors, preserve strict null results and bytes, require explicit strict verification, reject approval/identity/semantic errors before arithmetic, and cover frozen-artifact/report tampering, typed JSON equality, no overwrite and undefined correlations. These checks support only the tested software behavior, not clinical validity, source-population correspondence or target utility. Whole-cohort and direct-table routes retain their existing provenance limits; this module never claims seed-controlled generation for a direct-row submission.

There is no controller or real-candidate integration yet. The earlier `SOURCE_USE_CONTRACT_PROPOSAL.md` remains a historical proposal, including its unimplemented optional source-context adapter; this implementation note records only the narrowly implemented conditional task-population report.

Following the two independently identified hardening changes above, **only the changed conditional suite** was rerun: **34 passed in 4.77 seconds**. The added regression demonstrates that a Boolean schema version can pass inherited strict Python-equality verification but is rejected by the new wrapper before conditional arithmetic. Context assertions compare the emitted records with the exact bound source/model content. No old suite or biomedical execution was repeated for this hardening step.
