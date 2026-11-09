# Adaptive controller implementation review

Date: 2026-11-09. Independent reviewer: `/root/rubric_reuse_audit`.

**PASS_TO_HOST_SESSION_CREATION_AND_DISPATCH. No blocking findings remain.** Root may activate the reviewed controller and let the author choose actions within the declared protocol. This is an operational review, not a source-transfer, scientific-validity or efficacy certificate.

The decision binds controller SHA-256 `e5cc9ebe8801856b43c77bd1ca102d2aa97ec83d0b26042ca7fce480ff805f71` and SESSION_CONFIG SHA-256 `a720743f956350ae6b2d34af3011b1074693ada17552d93c0e174b04c505cb4d`. [IMPLEMENTATION_REVIEW.json](IMPLEMENTATION_REVIEW.json) records the controller, tests, interface and all three generated-analysis code hashes.

Three findings were corrected before this decision:

1. Completed finish now checks every submitted stage's scheduled attempts and success-dependent feedback/analysis. Abandonment remains explicit and records each stage's disposition.
2. Failed runs now receive trusted staging checks: submitted freeze, candidate identity, scheduled seed/limits, complete staged request, input/output inventory, worker hash and exact launch bindings. A mismatch halts the session and takes precedence over a worker failure. Unknown or pre-entry execution failure also halts; it does not silently consume future seeds.
3. The session now binds admitted metadata, skills and setup instructions by both bytes and inventory. These are checked before and after actions. Author candidate drafts remain editable until freeze; source additions and gateway activity use separately verified history.

The generated-only analysis path was inspected through `generated_analysis.py`, `lipid_provider.py` and `k02_analysis.py`; all configured hashes match. It supplies the verified generated table to the in-memory estimator with `role='generated'`, keeps the requested units/contrasts and same-row residual calculation, and implements all 23 diagnostics. It does not load a reference file. SETUP_NOTES resolves the older empty-registry and metadata-draft wording.

The final focused suite reports **30 passed, 0 failed**. Its source includes tests for failed-worker tampering, pre-entry infrastructure failure, omitted older-stage schedules, fixed-seed/no-retry behavior, gateway budget-state mutation, immutable result/source/adapter commitments, and metadata/skill/instruction mutations or added context. The owner's earlier related regression reports 107 passed; it predates the final additive static-context patch. This independent review inspected code, tests, recorded QA and hashes without rerunning already-passed tests. The program tests use a mocked backend; the generated-estimator smoke uses artificial orthogonal residuals. They are not clinical generation or a new live sandbox proof.

The reviewed configuration retains 48 actions, three candidate stages, nine execution attempts, nine feedback reports, nine analyses, and seeds 9401/9402/9403. Literature has six shared queries and three downloads; fetch metadata consumes query allowance. Scientific model/parameter choices, source choice, retrieval timing and voluntary retain/revise/stop remain with the author. The controller requires semantic_feedback_v1 and does not substitute the legacy collector.

Source feedback remains a descriptive comparison on target-context generated data, not source-population replay. Initial source weighting and other essential definitions may remain unknown, so unavailable checks are legitimate. Newly computable interpretations need focused source verification. No target payload, generated clinical table, old candidate/result or newly retrieved clinical literature was read by this reviewer. No generator was executed and no implementation was edited.

One author and repeated seeds cannot establish general efficacy, clinical uncertainty or causal benefit of the adaptive method. Runtime availability was separately reported by root; this review adds no independent OS-isolation claim. Any change to the bound controller/configuration requires renewed review before further dispatch.

