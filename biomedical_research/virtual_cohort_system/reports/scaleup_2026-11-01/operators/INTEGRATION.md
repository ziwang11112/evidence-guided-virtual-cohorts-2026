# Supplemental diagnostics bound to a verified execution

2 November 2026. `execution_feedback.py` is one additive collector. It uses an
already recorded, successful **whole-cohort `generator.py` execution**, the
frozen candidate's evidence/specification and an independently reviewed frozen
context declaration. It never launches a generator, imports candidate code,
builds source/target models or accepts a comparison-table path. Existing harness
modules and `contextual_statistics.py` are unchanged.

The result is a separately versioned
`supplemental_context_execution_feedback_v1` receipt. It does not replace or
extend the frozen `semantic_feedback_v1` schema. A geometric mean remains
`reported_other` with `statistic_name: "geometric_mean"` in the evidence and
unavailable in v1. A supported prevalence can retain its own v1 result; the
supplement never overwrites it.

## Lifecycle and proof boundary

1. Read and validate the task as whole-cohort with no `observed.csv`.
2. Use the existing candidate verifier, require the `generator.py` route, run
   `semantic_feedback_v1.preflight`, and validate the new frozen declaration.
   All declaration/review/type failures occur before either collector writes.
3. Use the existing execution verifier; require success, a recorded generator
   entry, the exact candidate and freeze hash. Direct-row and wrong-run routes
   are rejected. No execution is initiated by this step.
4. Explicitly call `semantic_feedback_v1.collect_feedback` if requested, then
   `semantic_feedback_v1.verify_feedback`; otherwise verify a named existing
   v1 receipt. A v1 failure is fatal, with no legacy collector fallback. Its
   retained report also receives a typed canonical JSON recomputation check,
   following the existing conditional collector's protection against `True == 1`.
5. Read only `executions/<run_id>/output/generated.csv` through the existing
   lifecycle reader and validate its output contract. Its byte hash, execution
   receipt, frozen candidate, task, evidence, model specification, semantic
   declaration, new declaration and v1 report are bound in the supplement.
6. Compute the small utility's descriptive values. Write a new exclusive
   `context_feedback_v1/<feedback_id>/feedback.json`, then reverify/recompute.
   Verification checks typed JSON equality; it does not execute a generator.

The module depends on the existing verifier's lifecycle guarantees. Hashes and
review identities are procedural commitments, not authenticated signatures or
protection against a host user coherently rewriting all records. They do not
certify source extraction, true population membership, absence of target
contamination, Agent authorship, scientific validity or portability of a model.

`cross_context_generator_linkage` is always `not_supplied_or_verified`. This
unit cannot establish that a source-context and target-context run use one
scientific model; no such claim should be inferred from compatible schemas or
from this collector's name. There is no campaign controller integration here.

## Frozen declaration contract

Add **before candidate freeze** the candidate-local `context_feedback_v1.json`:

```text
schema_version: 1
task_sha256: SHA256 of bundle/task.json
evidence_sha256: SHA256 of candidate/evidence.json
model_spec_sha256: SHA256 of candidate/model_spec.json
semantics_sha256: SHA256 of candidate/source_semantics_v1.json
table_context: {kind, context_id, population, measurement,
                variable_units, variable_scales}
assumption_ids: [existing model_spec assumption IDs, nonempty]
checks: [{id, evidence_id, semantic_check_id, operator, source, proxy}]
context_review: <independent review record below>
```

Every field is required; unknown fields fail. Check IDs must be unique portable
names. `table_context` has the same meaning as in the [utility contract](README.md),
but its units/scales cover the union of all operands and selection variables.
Its population must exactly equal `task.population`; measurement must exactly
equal the frozen whole-cohort feedback recipe's identity-measurement description.
Every unit must match the corresponding task column. Only original numeric
scales and explicit categorical scales are supported. The context kind is
explicitly `source_context_simulation`, `target_context_generated` or
`analytic_fixture`. Fixture contexts may have descriptive values but no proxy.

Each check's `operator` and `source` use the unchanged utility schema.
Geometric mean and threshold `proportion` are the only operators. Every operand
must already be a numeric frozen task column; filtering uses declared task
types, units, scales and the utility's explicit selection/missing rules.
Ordered categorical/string filtering is unsupported. No unit, log-scale,
threshold, missing-value or population transformation occurs.

Source binding is more than an evidence ID:

- `source_id` and exact locator must match the frozen evidence item; population
  and measurement must match the **full evidence source record**.
- Original estimate, kind, `statistic_name`, unit, full uncertainty, selection,
  applicability and variable roles are read from `evidence.json`, preserved in
  `reported_evidence`, and never supplied as replacement comparison numbers.
- `source.weights` must match the linked frozen v1 semantic binding. Unknown
  weighting cannot be relabelled `none`; weighted sources are not reweighted.
- The original uncertainty kind and v1 role determine the allowed utility role.
  CI/SE remain estimator uncertainty; SD is not substituted for a CI or derived
  from sample size. No precision weighting, estimated uncertainty, standardized
  residual or acceptance score is calculated.
- Source operand scales must be original; source selection scales must be
  original or categorical. Unknown/log scales fail before comparison. Units
  must match task units, including selection columns.
- Source and diagnostic operator definitions must match, including sex/site
  selection, threshold boundary, denominator and missingness policies. For
  proportion, the frozen v1 source-operator signature must match as well.
  Geometric mean requires the original `reported_other` label and an
  unavailable v1 gate with no v1 operator.

The old evidence schema represents source selection in text. The prospective
review therefore remains responsible for the translation of that text into
explicit predicates and for source eligibility/assay meaning; a matching hash
cannot establish their scientific correctness. The original source artifact
and complete evidence/specification remain the authoritative record.

## Reviews and assumption-defined comparisons

A review record has exactly:

```text
decision: approved
independent: true
reviewer_id; producer_id; reviewed_utc; reason: nonempty strings
approved_sha256: <commitment described below>
```

Reviewer and producer names must differ. `declaration_digest(declaration)` is
SHA256 of sorted, compact, finite JSON after removing only `context_review`
and each `proxy.review`. It covers all task/evidence/spec/v1 hashes, context,
operators, source descriptors, assumption IDs and proposed proxy rationales.
The independent context review must approve that digest. The code supplies a
digest helper, **not an approval generator**.

`proxy` is either `null` or exactly:

```text
assumption_ids: [existing model_spec assumption IDs, nonempty]
reason: <explicit explanation of this unweighted comparison scenario>
review: <separate independent approval record>
```

Its approval must bind `proxy_digest(declaration, check_id)`, the canonical hash
of `{declaration_sha256, check_id, role: "assumption_defined_proxy"}`. This
separate decision cannot be replaced by context approval alone. Reviewers must
read the existing specification's assumption descriptions; the code verifies
their IDs and commitments, not their substantive justification. Original
unknown weights and any unresolved source issue must remain disclosed.

The utility is called with **`approval=None`**. The collector never fabricates
its value-bound `approved_contract`, so supplemental
`exact_source_check_allowed` is always false and `strict_source_difference` is
always null, including when weights are explicitly `none`. The inner utility
continues to report `collector_integrated:false` about its standalone API; the
outer receipt records the newly verified output linkage without changing that
old utility or its eligibility contract.

With a separate valid proxy approval and a defined statistic, the supplement
may report `calculated unweighted value − original reported estimate` in the
original unit, labelled
`assumption_defined_unweighted_raw_difference_not_strict_source_discrepancy`.
Without that approval it reports only the descriptive value. A target context
remains target context, even if a proxy has been approved. Relabelling a frozen
context invalidates its commitments; no declaration turns a target table into
strict source replay. Undefined arithmetic yields no proxy number.

## API and bounded use

With the project root importable and this directory on the module path:

```python
collect_feedback(bundle, candidate, run_id, feedback_id,
                 semantic_feedback_id="existing-or-new-v1-id",
                 collect_semantic=False)  # verify an already collected v1
verify_feedback(bundle, feedback_id, candidate=candidate, run_id=run_id)
```

Set `collect_semantic=True` only to collect a new v1 receipt first. IDs are
exclusive; existing outputs are never overwritten. The file also exposes a
CLI with `collect|verify`, `--bundle`, `--candidate`, `--run-id`, `--feedback-id`,
and, for collection, `--semantic-feedback-id` / optional `--collect-semantic`.
The command does not admit a case, release evidence or authorize an experiment.

The current Greiner packet is **not** converted or admitted by this unit. Its
original weights remain `not_reported`; strict supplemental comparison remains
unavailable. Packet uncertainty anomalies and table-specific denominator
differences must survive any separately reviewed future evidence conversion
(for example in original evidence applicability and retained source records).
This collector cannot recover flags discarded upstream.

No derived-variable engine is included. In particular, if non-HDL is absent
from the five frozen K02 task columns, the collector rejects a non-HDL operand;
it does not add a column or compute `TC − HDL` behind the task contract. Thus
this unit does **not** claim all 24 Greiner geometric means and six prevalence
quantities are integrated. Source/target context construction, unit/assay
transfer decisions, any declared rowwise derivation, and actual case admission
remain separate work. No clinical calibration or target-effect evaluation ran.

## Verification performed

Only `test_execution_feedback.py` ran. Its three-row invented fixtures use the
real v1 preflight, collector, verifier and arithmetic, but explicitly mock
candidate/execution verification with small retained-hash checks. They are
adapter tests, not a validation of WSL, sandbox isolation or the full lifecycle.
Generator/process/network calls and the legacy collector are trapped as errors.

The initial default temporary directory was inaccessible, so no fixture could
start. A fresh test-only location outside the project then gave **37 passed in
1.52 s**. Source-scale and typed-v1 review fixes added six cases; the affected
selection gave **11 passed, 32 deselected in 1.10 s**. Those runs cover unknown
weights, original uncertainty, known-weight nonpromotion, explicit v1 modes,
source/task/measurement/locator/operator/type mismatches, independent approval,
wrong/direct/failed execution, frozen-file/output/receipt tamper, absence of a
comparison-path argument, undefined geometry and threshold prevalence. No old
test suite or patient/scientific execution ran. Temporary test artifacts are
not campaign outputs.
