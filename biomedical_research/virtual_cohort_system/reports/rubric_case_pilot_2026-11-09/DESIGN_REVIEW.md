# Independent design review

Decision: **PASS_TO_AUTHOR_DISPATCH**. No blocking findings. This decision binds the exact 101 input records copied into DESIGN_REVIEW.json from the current DESIGN_LOCK.json. It approves the six predeclared author submissions; it does not approve execution independently of the implementation review.

## Checks

- **locked_inputs — PASS.** All 101 current DESIGN_LOCK.records SHA-256 bindings recomputed and matched. bound_inputs copies those records exactly.

- **prospective_amendment — PASS.** DESIGN_LOCK.v0.json preserves the original 99-record lock. Changes relative to v0 are only six REQUEST.md files and prepare.py; added bindings are DESIGN_LOCK.v0.json and PRE_AUTHOR_AMENDMENT.md. Sources, tasks, scientific requests, registries, metadata, rubrics and skills are unchanged. All six author output directories are empty.

- **within_case_information — PASS.** Within H and within L, task JSON is identical after removing task_id; request.json and registry.json are byte-identical. Each registry exactly matches the curated list and every source file is registered with matching bytes. H has 15 source artifacts across four source IDs; L has three artifacts across three source IDs. Lipid methods-only metadata is identical across arms.

- **treatment_contrast — PASS.** Normalized REQUEST.md is identical across arms except author ID and the additional-guidance allowlist. All arms must apply supplied guidance. A uses common base skill; B adds supplied rubric; C adds the identical rubric plus reusable procedures. C must not derive a replacement rubric. Common base skill matches the installed skill byte-for-byte.

- **rubric_integrity — PASS.** H B/C TASK_RUBRIC.md files are byte-identical to rubrics/GLYCEMIA.md; L B/C files are byte-identical to rubrics/LIPIDS.md. No target outcome estimates or desired target directions appear in inspected author-facing criteria/task/request/metadata. Numerical rubric values are task invariants, design/coding definitions or unit conversions.

- **source_definition_spot_checks — PASS.** Verified rubric source-definition examples against admitted files: Pani complex-survey analysis; Skogberg adjusted coefficients versus predictive margins and R-squared; Agongo univariate unresolved-log-scale coefficients; Greiner geometric means and unresolved regression substitution; Obirikorang unadjusted community-specific Spearman correlation.

- **endpoint_coverage — PASS.** All three H analyses and all three L analyses exactly match the request IDs and ENDPOINT_CONTRACT. Contract predeclares 28 H and 23 L numerical diagnostics. Evaluation specification also requires invalid/duplicate and uncomputable findings, all scheduled draws and failures, discrepancy and direction with available uncertainty, and no pooled score or winning-seed selection.

- **author_boundary — PASS.** No participant inputs, target outcome summaries or new literature acquisition are authorized. Reference binding metadata was inspected; referenced numerical files were not opened. Shared requests prohibit other bundles, old results and protocol/review files. Boundary is procedural rather than filesystem isolation.

- **construction_and_retention — PASS.** One fresh author per arm/case; exactly four author artifacts; no trial sampling or post-submission repair. Inline deterministic algebra is allowed only with exact commands and results retained in DECISION.md, with no extra bundle files and no host import/execution of the generator. Three fixed draws per sealed construction, at most 18 physical attempts including failures. No result-dependent retry or favorable-seed selection; infrastructure defects stop the batch.

- **limitations_and_claims — PASS.** Protocol and evaluation specification explicitly acknowledge author-by-arm confounding, draw versus author replication, unavailable token telemetry and unequal prompt lengths, prior reference exposure, minimal-interface scope, and no test of autonomous rubric induction or feedback revision. Results remain developmental and do not establish general superiority.


## Limitations and scope

- One author per arm and case cannot separate instruction condition from author/model sampling variation; three seeds quantify draws from one law only.

- Response count and execution schedule are matched, but actual model token/compute use is neither instrumented nor enforced; this is not a strict compute-matched comparison.

- The root has historical exposure to the previously used references. Methods-only target metadata is admitted prospectively; measured target outcome summaries remain evaluator-only. This is not a new clinical confirmation.

- This pilot tests supplied rubric and procedure guidance during source-only construction under a shared minimal four-artifact interface, not exact replay of the complete older workflow, autonomous rubric induction, retrieval improvement or iterative feedback.

- Information separation for authors is procedural. Dispatch must use fresh contexts and the fixed visible inputs; model/backbone settings and actual tool usage should be recorded without inventing token telemetry.

- The copied lipid metadata retains a historical draft-status label and row-count deferral. Current task.json, request.json and PROTOCOL.json are the authoritative frozen 3000-row contract; no target sample count or composition is supplied.

- Source hashes establish identity, not truth or transportability. This review checked source-definition examples and registry integrity; it did not re-adjudicate every published numerical extraction.

- Numerical reference aggregates, evaluator implementation correctness, generator execution integrity and final data usefulness are outside this design-only review. Execution still requires the separately bound implementation review.


## Review boundary

The reviewer read the locked protocol, endpoint contract, evaluation specification, source registries and curated manifest, author requests and task definitions, common and experimental skill instructions, case rubrics, methods-only lipid metadata and the reference-binding metadata. Source-definition checks used only admitted source files. All locked file bytes were hashed for integrity. A broad filename listing initially included engineering fixtures, but no fixture output, old candidate/result content, numerical target-reference file or new author output content was opened.

No patient data were read and no clinical generation was performed. The reviewer changed only DESIGN_REVIEW.json and DESIGN_REVIEW.md. All six author output directories were empty at the final integrity check.

The earlier ambiguity about guidance application was resolved prospectively: all six requests now require application of their supplied guidance; the supplied rubric remains unchanged, and C applies its procedures to that rubric. The original lock and amendment record are preserved. No source, task, request.json, registry, rubric or skill content changed in that amendment.
