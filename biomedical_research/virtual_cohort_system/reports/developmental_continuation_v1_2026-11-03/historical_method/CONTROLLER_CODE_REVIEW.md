# Independent controller code review

Status: approved for the scoped additive controller contract at the exact hashes below. No remaining controller release blocker was identified in this static review. This is not an approval of a scientific candidate, the final release/input packet, clinical validity or target execution.

Reviewed UTC: 2026-11-03 05:24:33 UTC.

| Reviewed artifact | SHA-256 |
|---|---|
| `implementation/pilot_controller_v1.py` | `5a1507e374a6d5e1e74645c371a1f28e42a209c4aab8f7f7e7fd243c2d8e1e7d` |
| `implementation/PILOT_CONTROLLER_SCHEMA.md` | `e12e85aa0c7e1b721393ed61d68fcde7fc606a5bc22e726a36aae6138a7cec1f` |

The producer declared these files final after its bounded test batch completed. The reviewer reread the changed code/schema and independently rehashed both final files. The producer reported 10 tests passed in 177.71 seconds, using invented fixtures with process capture mocked. This reviewer did not execute or independently reproduce those tests.

Reviewer: support_selection_design. Controller producer: pilot_controller_audit. The reviewer did not author the controller. The support-selection module was authored by this reviewer and requires the root's separate review; this document is not an independent approval of that module.

Scope: static review of `implementation/pilot_controller_v1.py` and `implementation/PILOT_CONTROLLER_SCHEMA.md`, with narrowly selected frozen lifecycle, bridge and source-controller functions read to establish their inherited guarantees. No candidate generator was imported or executed, no clinical or target/reference rows were accessed, no network access occurred, and no test suite was rerun. The only reviewer-owned output is this document.

## Findings reported during development

1. **Active-dispatch closure race — resolved.** The initial reviewed implementation released its ledger lock while target execution was live; recovery finalization could close that allocation and evaluation could be authorized before the dispatch loop resumed its remaining attempts. Final code holds a separate nonblocking execution-phase lock throughout each live source/target dispatch and its internal finalization; public recovery finalization requires the same lock. Target attempts also explicitly reject closed/authorized state. Therefore the public recovery API cannot prematurely close a live dispatcher.

2. **Interrupted source artifact commitment gap — resolved.** A frozen bridge attempt lacking an outcome returns an interrupted status without output/receipt hashes. Final pilot closure independently captures full source bridge and source-controller file inventories, complete authenticated feedback, and raw output/receipt hashes when files exist. `_inventory` recomputes and compares the whole closure object before and after parent target execution. Incomplete/failed source bytes can no longer change unnoticed merely because no inherited source-completion record exists.

3. **Retained failed-source support reporting gap — resolved.** Final code collects support counts for every retained source table identified by its output hash, including tables left by failed/interrupted slots. Unreadable tables retain a hash-bound unavailable report and reason. The all-nine-success condition remains separate, so successful row checks cannot rehabilitate a failed source attempt. Target closure also stores and rechecks support reports for every retained target table.

4. **Initial input identity — resolved by the requested narrow binding.** The release now designates one initial packet manifest. Both constructors must name that manifest hash and match its exact task, evidence and registry byte commitments. Manifest files are bound and copied to both branch packets. Registration no longer accepts an arbitrary public-artifact hash as the initial packet. Source admissibility and absence of forbidden content in the reviewed packet remain substantive release-review responsibilities; extensions are not inferred from filename suffixes.

5. **Incomplete packet artifact coverage — resolved.** Packet construction, abort and scientific freeze now share the execution-phase lock. Scientific freeze commits the complete retained packet-file inventory, including partial packets from aborted deliveries; later verification compares it exactly. Delivered packets additionally retain their role-specific reconstructed manifest checks.

## Static guarantees observed

The plan enumerates exactly two constructors, three versions, nine source slots and three target slots per version, yielding 72 total slots. Intents debit whole allocations before dispatch, and explicit abort/stop/ineligible dispositions preserve slots rather than replacing authors or generating extra attempts.

Branch registrations directly parent their own accepted initial freeze, preserve task/evidence, bind the delivered packet and cannot reuse a registered candidate/context identity. Inherited lifecycle verification checks whether retain/revise agrees with scientific code/specification changes. The initial common correction is explicitly recorded and bounded to one parent step.

Branch packets use an allowlist of the initial candidate and admitted source bytes. Only the numerical-feedback packet adds authenticated initial source feedback. The self-review packet does not copy source execution folders, runtime diagnostics or final-branch feedback. This is a procedural delivery boundary, not OS isolation of author tools or a proof against prior exposure.

The global scientific freeze requires all six version outcomes and prevents further author registrations, source dispatch, packet delivery and choices. Parent target execution is separate from the frozen source bridge. Inherited bridge preflight already requires the parent's active context and task to be the declared target; target recipes/feedback are prohibited. Evaluation authorization is downstream of target closure and rechecks frozen release/inventory bindings.

Target eligibility is recomputed from all nine successful source executions, all four required qualified relationships available across three seeds, and retained source support/eligibility checks. Numerical closeness to a published point is not an admission condition. The support assessment is recomputed from candidate, release contract and module bytes and requires separately bound independent review of the actual law/code; declared support is not treated as proved.

## Limits of this approval

The controller provides a procedural delivery and execution boundary. It does not isolate an author's general filesystem tools, establish absence of pretraining/prior exposure, authenticate a human reviewer's identity, prove an asserted mathematical support law, or measure unavailable model-call/token usage. Those claims are not granted by a passing hash check. Candidate scientific reviews, required native-map/qualified-operator consistency, source admissibility and the final input protocol still require the separately bound release review.

Malformed or changed trusted control artifacts stop verification rather than being silently repaired. Such a stop does not authorize another constructor, execution, seed or expanded budget. The reviewed implementation preserves all scheduled failure slots and retained artifacts for the supported completion/interruption paths.

No broader framework, additional biomedical parameter choices or additional experiment was requested by this review. Approval applies only to the two hashes above; later code/schema changes require corresponding review.
