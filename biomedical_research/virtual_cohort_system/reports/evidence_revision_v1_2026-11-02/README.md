# Source evidence revision implementation

This additive implementation connects evidence-use declarations, per-context moment checks, reviewed source-only dispatch, preserved semantic feedback and qualified relationship comparisons. It does not yet contain a new biomedical Agent construction or a released target experiment. The old CHNS generators and their results remain unchanged.

## Implemented components

- [Evidence-use declaration](implementation/evidence_use_SCHEMA.md): every evidence item has an explicit numerical, qualified, contextual or unused role. Metadata hashes and parameter/operator references are checked. A declaration is not an execution certificate.
- [Declared-law validity](implementation/scientific_validity_SCHEMA.md): conservative analytical moment checks for supported distributions and compositions, including the exponential-lognormal defect and gamma thresholds. Unsupported compositions remain unresolved. Each source and target context requires its own declaration. Independent code correspondence and nondegenerate analysis-design review remain necessary.
- [Qualified relationships](implementation/qualified_relationships_SCHEMA.md): original weights remain unknown and strict v1 results remain unavailable. Separately reviewed equal-weight OLS, Pearson and Spearman comparisons retain their assumptions. Read-only aliases connect original evidence labels to generated columns; the supported HbA1c unit mapping transforms generated values, not the reported estimates. Unit/assay applicability still needs review.
- [Source revision controller](implementation/revision_controller_v1.py): reuses immutable bridge preparation/sealing and isolated execution. Only source slots can be dispatched. Verified feedback, failure details, qualified labels and one retained revise/retain/stop decision are bound to the actual artifacts. It exposes no target dispatcher.

No optimizer, additional dataset, model training, paid API or new scheduler is introduced. The statistical engine has no desired BMI, glucose or age effect hard-coded into it. Unit conversions and toy test values are not generated biomedical model parameters.

## Candidate and review interface

Use the existing whole-cohort candidate and `context_bridge_v1.json`. Add these files before its first freeze:

1. `analysis_evidence.json`, using the existing analysis-evidence contract.
2. `evidence_use_v1.json`, using the evidence-use schema linked above.
3. `scientific_validity_v1.json`, with `{schema_version: 1, context_laws: {context_id: <assess_law manifest>}}`. Every bridge context must occur, and every context's declaration must cover the same intended analyses. In this entrypoint their operands must cover all generated numeric output columns; identifier columns are excluded. This conservative v1 supports OLS/Pearson point analyses, not interval inference.
4. Optional `qualified_plan_v1.json`, with `{schema_version: 1, contexts: {source_context_id: <qualified declaration>}}`. Each authored declaration has empty `bindings`; preparation fills only artifact hashes. Its relations must match qualified evidence-use records. Conversion evidence cannot be declared unused.

The review request contains the frozen candidate commitment, sidecar hashes, new engine hashes, mathematical results and required review fields. Reviewers inspect actual code correspondence, each context's analysis design, shared dependency paths, source assumptions and point-estimate scope. A boolean review record is a retained declaration, not proof that an Agent's general file tools were isolated or that extraction/transport is correct.

```python
# PROJECT and this implementation directory must be on sys.path.
import context_bridge as bridge
import revision_controller_v1 as revision

# Candidate already frozen, using the existing lifecycle.
bridge.prepare(bundle, candidate)
binding_requests = bridge.binding_requests(bundle, candidate)
# Obtain real independent binding reviews; this code supplies no approval.
bridge.seal(bundle, candidate, binding_reviews)

science_request = revision.science_request(bundle, candidate)
qualified_requests = revision.qualified_requests(bundle, candidate)
# Obtain independent science and qualified-comparison reviews.
revision.open_source_phase(bundle, candidate, science_review,
                           qualified_reviews=qualified_reviews)
revision.dispatch_sources(bundle, candidate)
feedback = revision.source_feedback_packet(bundle, candidate)
# Give this source-only packet to the scientific Agent.
revision.record_decision(bundle, candidate, agent_decision)
```

The bridge remains incomplete because its target slots have not run. The separate source phase can be complete. Do not call the historical bridge's `execute` function for this workflow: it dispatches all slots. Do not create an old bridge completion receipt after running only sources.

An Agent's revised scientific submission would be a separately frozen candidate, not an edit to the initial one. A campaign-level budget and final target-release controller are still required before the planned paired experiment. Recording `revise` is not the same as constructing, executing or validating that revision.

## Verification and scope

The new suites use invented declarations and arrays. Process calls and networking are forbidden/mocked in execution tests; real lifecycle, source operators, execution-receipt verification and semantic feedback logic run on retained invented artifacts. A compatibility test also reads the already admitted E1 evidence definitions and the old task schema, then evaluates all four relationship definitions on eight artificial rows. It reads no patient records and does not establish a biomedical fit.

From the project root, with this folder on `PYTHONPATH`, run the four new test modules with a short fresh `--basetemp` directory on Windows. Deep nested paths can exceed Windows path limits. Do not reuse or delete previous run directories to conceal a failed check. [Verification history](RESULTS.md) distinguishes the final test run from earlier failures and repairs.

## Actual-case integration still required

The old task fixes ages to 35–74 in every derived context. MIND's source population includes ages through 80, and other sources also differ. Changing only a population label while retaining that support is inadequate. The next source-only integration needs a separately reviewed common variable schema that can represent source supports, together with explicit per-context eligibility and target-range checks. Broader common support must not silently relax the target's 35–74 eligibility. This is a metadata/measurement design decision, not permission to tune target effects.

Original source joint distributions, weighting and some row-processing details remain unavailable. The new qualified calculations expose consequences of stated assumptions; they do not reconstruct original participants or identify a unique target joint distribution.

## Failure boundaries

Ordinary failed executions consume their source slots. Worker interruption after an intent exists preserves successful earlier feedback and permits a truthful stop decision. Invalid partial feedback from a failed component is retained as invalid and is never used for arithmetic. Successful receipt verification failures remain hard errors.

This is not a transactional crash-recovery service. A host interruption between creation of an attempt directory and its intent, or between a decision and its commitment receipt, fails verification and requires manual artifact inspection. No automatic retry, record deletion or budget reset is provided. Coherent malicious rewriting of all host files is outside the hash-commitment guarantee. These limits must not be described as complete automatic recovery.
