# K01 source integration

`k01_sources.py` compiles the committed K01 metadata and collects descriptive source feedback from an authenticated, completed bridge execution. It never fits a model, executes a generator, searches a source, opens a target reference file or accepts an arbitrary CSV/context argument. All changes are additive; the frozen bridge, operators, request and case implementations remain unchanged.

## Assembly API

```python
compiled = compile_committed()
stage_sources(new_destination)
templates = bind_context_assumptions(compiled, {
    "source_mind_china_2019": ["agent_authored_assumption_id"],
    "source_ayele_dire_dawa_2017": ["another_agent_assumption_id"],
})
declaration = build_declaration(compiled, assumption_ids_by_context, model_spec=model_spec)
request_for_independent_review = declaration_digest(declaration)
```

`compile_committed()` verifies the exact `REVIEWED_DESIGN_COMMITMENT.json` hash and every committed metadata/code dependency. Its result includes `evidence`, `record_provenance`, `source_context_templates`, `descriptive_plan`, `registration_requirements`, `engine_sha256`, the design/artifact hashes and disposition counts. The lifecycle evidence retains all34 selected records, including16 contextual records; its source artifact is the exact sanitized request JSON at `sources/k01_selected_source_evidence.json`. Eighteen recipe gates are split7/11 across MIND/Ayele. Every gate is unavailable in semantic_feedback_v1 with null source operator and unknown original weighting; no strict source discrepancy is computed. Contextual adjusted ORs retain their reported adjustment headings and CIs, and cannot become continuous glucose coefficients. The original full selected source metadata and record remain hash-bound provenance.

`stage_sources(destination)` exclusively creates that artifact plus `compilation.json`, `evidence.json`, `source_context_templates.json` and `registration_requirements.json`. It does not change a registry or create `screening=approved`. The root assembler supplies its independently admitted curator registration and binds the exact source artifact. Write the candidate evidence with `encoded(compiled["evidence"])`; this explicit encoding is part of the frozen declaration's byte commitment.

The constructor supplies the actual context assumption IDs and model specification. Bind the two source templates verbatim into the bridge plan with policy `semantic_v1` and no old supplemental declaration. Target feedback policy must be `none`. The declaration returned by `build_declaration` has `review=None` and commits the complete `encoded(model_spec)` SHA256, including assumption prose; write those exact model bytes. An independent reviewer must approve its digest, with the established decision/independent/reviewer_id/producer_id/reviewed_utc/reason/approved_sha256 fields. Freeze that actual review in candidate auxiliary file `k01_descriptive_declaration.json` before bridge preparation. The existing bridge copies it unchanged into each child. The compiler never invents reviewer identities, approvals or scientific parameters.

## Collection and verification

```python
report = collect_descriptives(parent_bundle, parent_candidate, source_trial_id)
verified_report = verify_descriptives(parent_bundle, parent_candidate, source_trial_id)
```

Both calls derive child/context/output only from the verified frozen parent plan and retained bridge ledger. They require a completion commitment, exact committed5000-row task, the three fixed contexts, source seeds3101/3102 and target seeds2101–2103, and a successful generator-backed source slot. Other failed slots do not become successes; the controller still owns case failure/delivery policy. No target trial is collectable. The independently reviewed candidate-local declaration, assumptions, compiled evidence and source templates must agree exactly. The collector re-verifies the child task/spec/freeze, generator linkage, actual execution, output hash and typed semantic-v1 receipt; all strict gates must remain unavailable with null differences.

Only then does it parse the execution's fixed `output/generated.csv`, call committed `validate_generated_context(..., context_id=...)` on all rows, and call committed `compute_source_descriptives`. It compares the exact committed source comparison values using unnormalized raw differences. Means/individualSDs retain their roles; printed percentages and derived count fractions remain separate; all Boolean events retain the entire5000-row denominator. Original uncertainty and source-selection/measurement caveats are included, with no conversion into standardized scores or residual SDs. These are approved assumption-defined descriptive comparisons, not strict source-estimator replication or proof of transport.

Reports are exclusive at `parent_bundle/k01_source_descriptives/<parent_candidate_name>/<trial_id>/feedback.json`, **outside** the completed bridge inventory. Each binds the parent/child freeze, design, compiled plan, declaration, source artifact/evidence, code, actual output, execution and semantic receipt. Verification recomputes the report and compares canonical typed JSON, rejecting Boolean/numeric substitutions and extra report artifacts. A failed guard or input verification produces no report and never repairs/filters rows. Existing reports cannot be overwritten. The pure guard's own receipt truthfully says it is not an execution authenticator; the surrounding collector supplies that separate binding.

## Limits and validation

This is source integration, not a clinical release switch or cross-stage campaign ledger. Root assembly must obtain the global release, freeze real candidate declarations, enforce retained/revised budgets and feedback delivery, and withhold target outputs/logs from constructors. A completed bridge mechanically links generator/spec bytes; it does not prove scientific compliance, source truth, participant independence or assay transport. Hashes are retained-byte commitments, not authentication against a malicious host rewriting every commitment. A failed collector cannot justify another generation attempt.

The new suite uses changed invented source records and invented5000-row tables. It mocks runtime command construction/process capture, not lifecycle, bridge freeze/seal/verification, semantic-v1 arithmetic gating or collector checks. No generator code or network is executed. Tests cover both source contexts, full-row denominators, contextual uncertainty/units, inaccessible target/unknown/path-like trials, changed execution/output bytes, incomplete completion, typed report tampering, an invalid source-age row before arithmetic and exclusive staging/report paths. Use a fresh explicit pytest base directory on Windows; extended paths are needed in this long workspace, and the mocked command boundary intentionally avoids the real adapter's UNC/extended-path restriction. No old passed suite is rerun.

Only source files, README, review, `TEST_RESULTS.json` and the metadata-only `compiled/` directory are prospective public artifacts. `.test_tmp/` contains clearly invented fixture bundles and receipts and is not part of any source packet or public allowlist.

`test_combined_integration.py` adds a separate three-check composition with the root assembler and guarded stage runner. It substitutes a changed invented admitted package and mock ledger authorization, then uses real compiler/assembly/freeze/seal/runner/semantic/collector logic with mocked OS execution. All18 descriptions are exercised; wrong-context rows must stop before semantic-v1 collection; changing assumption prose must invalidate the declaration approval. The full earlier11-test suite was not rerun for the narrow model-binding addition. `COMPILED_REVERIFICATION.json` records that the earlier actual metadata compile is unchanged except current engine commitments; it does not relabel the old compiled receipt as a new run.
