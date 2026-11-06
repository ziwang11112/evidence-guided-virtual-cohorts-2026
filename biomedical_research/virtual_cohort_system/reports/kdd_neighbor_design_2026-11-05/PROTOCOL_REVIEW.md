# Independent scientific and feasibility review of design v1

5 November 2026. **Status: PASS_DESIGN. Execution release: NOT APPROVED / not assessed.**

Refreshed review of the final design artifacts:

| Artifact | SHA-256 |
|---|---|
| `PROTOCOL.md` | `ad76b14a361dfc6ace6bebf6f44d2907a42aef622f41b463f190d0d941621bb2` |
| `DESIGN_CONTRACT.json` | `4137782124f71406c00c45067974c91259dadd20f6c141b15fe06dbba6b00bb5` |
| `build_design_contract.py` | `ad8472f3b6e573b56fc0e693ad631f5ad7b7108943a24edb0e28fa146a631e3f` |

Compared these with the local readiness audit, current LLMSynthor implementation audit, frozen cross-task request/endpoint definitions and completed-summary-comparison records. Read the builder statically without running it. Independently parsed the design metadata to check schedule/count arithmetic and recomputed the 17 bound metadata/code/aggregate-file checksums: all matched, and the contract's protocol hash matched the final protocol. This is a metadata consistency check, not scientific execution. No fixtures, model calls, generators, evaluators, patient reads or reference refits were run. The reviewed protocol, contract and builder were not edited.

This refreshed review supersedes the earlier review of protocol hash `ba6e45f923a79ba1e507faf2804cb5f585f6df1dbd529e11ce326f831e70619c`. The old 232-request ceiling is also superseded by 234 including scientific review.

The design is a defensible small comparison of two evidence-to-data workflows. The cases, information boundary, native episode unit, six scientific estimands, full diagnostics and claim limits are coherent. No scientific design revision is required before the implementation phase. The release gates below must be resolved and independently checked before biomedical execution; this is not approval of a baseline implementation that does not yet exist.

## What passes

**Matched information and adapter fairness.** Both arms receive the same curated evidence, source qualifications, population metadata and analyses without individual inputs or target answers. Common preprocessing does not infer a law or target macros. LLMSynthor-E retains its own meaningful evidence-to-macro interpretation and missing-joint approximation; EVC retains its source-to-law interpretation. This preserves an honest comparison of adapted workflows rather than hiding our completed law inside the baseline. Both have partial or unavailable source feedback. Assumption-based macro fit is explicitly separated from empirical source fit, so neither method is falsely credited with an unavailable numerical source oracle.

**Comparator identity.** The protocol accurately calls LLMSynthor-E a paper-based reimplementation with a biomedical extension, rather than official author code or an unmodified replication. The paper-to-code review occurs before performance; invented fixtures and bounded short live checks are separate from biomedical evidence. The grouping-schedule and proposal-schema ambiguities are disclosed. Failure of an adapter or local implementation is not treated as published-method inferiority.

**Native iteration and replication.** Ten LLMSynthor episodes preserve 100 adaptive rounds and native cumulative final outputs. Ten EVC episodes preserve fresh law construction and one final delivery each. There is no frozen-proposal replay falsely counted as new construction. Five episodes per method/request are computational repetitions under one model service, not independent clinical datasets. Method ordinals or matching seed labels are not used to invent pairing.

**Row quotas.** Exact eight-cell ENSANUT quotas are legitimate supplied design constraints, not target biological relationships. Restricting a proposal to one allowed age/sex cell does not force BMI, glucose or HbA1c associations. Within-cell biomarker values and proposal splits remain model decisions. The final design resolves the earlier reachability issue with 96 single-cell rounds cycling through eight cells twelve times, followed by four rounds splitting 15 rows into each of two cells. Each cell receives 12 × 30 + 15 = 375; the total is 96 × 30 + 4 × 30 = 3,000. Every round has exactly 30 rows and at most two demographic cells, compatible with at most five proposals. I independently checked all 100 metadata schedule entries and all eight totals. This schedule is openly labelled as a biomedical adaptation; it neither requires final downsampling nor imposes a biological coefficient. The cell-index-to-sex/age-band binding and runtime enforcement remain release checks.

**Resource scope.** The per-round grouping schedule implies 100 group plus 100 proposal calls per LLMSynthor episode, not 101 calls and not 500 calls. The per-episode ceiling is correctly 100 + 100 + 2 + 20 + 10 + 2 = 234 logical requests, including two scientific-review requests. Ten LLMSynthor episodes imply 2,000 primary planning requests and at most 2,340 logical requests including all listed extras. EVC has the same ceiling but no obligation to spend unused calls on a new search. The old 120-call proposal and intermediate 232-call ceiling are superseded. Actual call metering, per-response caps and an active-time limit remain execution-release conditions.

The audit states 2,048 generated tokens for the published local-inference configuration, not a universal verified cap for every service or main-paper model. If every one of 234 requests used that cap, the arithmetic upper bound would be 479,232 visible generated tokens per episode; the protocol's one-million-token overall ceiling does not itself preserve per-call caps. The protocol appropriately requires those caps to be separately declared for the chosen service. Hidden reasoning/input usage cannot be counted as measured equal compute when the service does not expose it.

**Evaluation and accounting.** The following counts are correct conditional on every scheduled table being valid:

| Count | Arithmetic | Result |
|---|---|---:|
| End-to-end episodes/final tables | 2 cases × 2 methods × 5 episodes | 20 |
| Final fictional rows | 20 × 3,000 | 60,000 |
| Primary estimates | 20 × 3 | 60 |
| Glycemia outputs | 10 tables × 31 endpoints | 310 |
| Lipid outputs | 10 tables × 26 endpoints | 260 |
| Total endpoint values | 310 + 260 | 570 |
| Matching cached-reference comparisons | 310 + (10 × 5) | 360 |
| Generated-only diagnostics | 10 × 21 | 210 |

These are scheduled output counts, not independent observations for hypothesis tests. Failures and unavailable analyses remain in their scheduled denominators, and summaries over evaluable outputs disclose their denominator. Native-unit discrepancies, signed differences, all episode points, spread and dependence are appropriate. The protocol neither invents a universal score nor treats reference estimates as known population truths.

**Claim scope.** The experiment addresses the user's intended contribution: complete scientific data produced from existing evidence and consequential Agent construction decisions. The direct-analysis-Agent contest and an unlimited bespoke statistical competition are unnecessary. The design can support a relative workflow result and an analysis-specific usefulness statement. It cannot establish a causal component contribution, universal superiority, calibrated transport uncertainty or fresh clinical confirmation. The current KDD-facing goal therefore does not require an extra comparator or an unexposed cohort in this unit. Acceptance or a sufficiently novel mechanism is not established by passing this design review.

## Actionable execution gates

### G1 — Quota reachability resolved in design; verify runtime enforcement

The earlier protocol left a possible final-round dead end: remaining quotas `(4,4,4,4,4,4,3,3)` would need eight single-cell proposals despite a five-proposal cap. The final protocol and machine-readable schedule remove this ambiguity through the fixed 96-plus-four-round design verified above. No general biological optimization or inferred target relation is introduced by this repair.

Before release, bind cell indexes 0–7 to the exact original female/age-band cells and implement enforcement of each scheduled cell count. Test the full 100-round trace, rounds 96–100, wrong-cell/invalid count or age-range proposals, bounded repair handling and no post-hoc row replacement. The LLM must retain scientific range/count choices within these admitted quota constraints. This is a contract implementation gate, not an outstanding scientific design defect or evidence that LLMSynthor is inadequate. The schedule can influence interim demographic discrepancies, so preserve and disclose it in runtime logs and prompts as the stated adaptation.

### G2 — Macro commitment resolved in design; verify isolation and validation

The final Section 4 now explicitly freezes every empirical, derived and assumed numerical target after admission. It restricts new-target inference to a separate context containing admitted source evidence, schema and admitted targets, excluding generated frequencies and evaluation results. It requires normalized nonnegative tables compatible with declared margins/quotas, records repairs within the fixed inference allowance and excludes unresolved groups rather than substituting current synthetic rows. `DESIGN_CONTRACT.json` records the immutable-target and restricted-inference rules. These changes resolve the earlier design ambiguity.

The implementation must demonstrate this separate context, admitted-target hash/version binding, repeated-group reuse, compatibility validation and recorded exclusion after exhaustion. Preserve source facts, assumptions and computed self-consistency as distinct roles in reports. No scored-run exception may alter a frozen target to improve apparent fit. A substantive scientific target revision would change this design and require separate prospective review.

### G3 — Bind fidelity and common backbone before performance

Complete v4 prompt parity and the typed schema, interval/integer sampling conventions, empty-mass behavior, selected-group schedule and optional approximation route. Independently verify scripted 100-round controller behavior and the two bounded live fixtures before the biomedical release. The short live fixtures establish parsing/dispatch feasibility; they do not establish convergence or clinical accuracy. Freeze one chosen implementation afterward. Reimplementation-specific failures remain distinct from endpoint discrepancies.

### G4 — Meter the actual model operation and preserve native resource opportunity

The dispatcher must log logical operation, model/service/version, request/response identity, inference settings, visible token usage, elapsed time and all retries/repairs. It must distinguish a high-level host turn from an actual model request. At most 20 missing-joint, ten repair and two scientific-review requests are included in the 234 ceiling, not loopholes for more proposal rounds. New or repeated target inference must be counted consistently. Set and enforce response-specific caps, the overall token cap and a finite active-time ceiling before clinical generation. If the available service cannot supply auditable repeated calls, stop at implementation readiness rather than abbreviating the baseline's 100-round method.

### G5 — Freeze cumulative generation/row/repair ledgers

Bind each sampled batch and its parent cumulative-table hash; prove that rows are appended and earlier rows are unchanged. Exactly 100 successful scheduled rounds of 30 rows yield the final 3,000 rows. The implementation must resolve what a malformed/invalid round does before release: a counted bounded repair can recover the same logical round, but extra samples, discarded values, hidden round replacement or a second trajectory cannot be omitted from accounting. Budget exhaustion or an incomplete final trajectory is an episode failure, not permission for more rounds.

Likewise record EVC trial, optional revision and final draws separately. A common model ceiling is not equal actual sampled-row cost. The run manifest should state the method-specific sampled-row ceilings and retain partial/invalid rows in cost accounting without releasing them publicly. No final downsampling or forced biological correction is permitted.

### G6 — Prepare clean inputs and a separate evaluator

Rebuild packet folders from the original curated-input manifests rather than copying old H/L bundles. Independently check identical empirical information and permitted definitions across arms. Document actual author read boundaries, keeping old target reports/models and historical generated feedback out of all author sessions. Derive the new 20-episode controller and five-episode summaries without mutating the old six-author/three-seed controller. Preserve original estimator/provider logic, reference hashes/selectors, delayed reference access and the 21 unavailable lipid diagnostic mappings.

### G7 — Keep limitations visible in the result artifact

Display native-unit primary estimates with appropriate existing reference bands; preserve the TC slope interval crossing zero and the unavailable residual-correlation interval. Five episodes mix construction and internal sampling variation, so do not label their spread as pure Monte Carlo, population uncertainty or transport uncertainty. Keep the historical CHNS real-real results as separate context, never as a pass line for these two cases. Record human/host source-review interventions and prep effort alongside method calls; do not infer automated time savings from execution-adapter duration.

## Decision

Proceed to the bounded implementation and fidelity stage under this design. Do not launch biomedical episodes until an independent execution release binds the resolved gates above. No extra case, new patient analysis, richer target packet, G-Sim run, common-macro ablation or direct-analysis-Agent arm is needed to pass this design review. If the fidelity/interface gate cannot be satisfied, publish the restricted implementation finding and withhold the comparative headline.

This verdict applies only to the three final artifact hashes above. The contract contains 20 unique episode IDs and 20 unique RNG seeds, correctly binds all 17 listed existing artifacts, and retains `generation_released=false`. Static inspection of the builder is consistent with those metadata and does not introduce scientific execution. Subsequent scientific changes require a new design review; implementation-only resolutions should be recorded in the release manifest and checked against this design.
