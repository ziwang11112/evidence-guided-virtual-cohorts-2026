# Independent pre-acquisition protocol review

Date: 2026-11-04. Reviewer role: independent design auditor, not a scientific author.

**Decision: PASS_FOR_SOURCE_ACQUISITION_ONLY.** The four fresh scientific-author slots may begin the bounded gateway acquisition and proposal phase. This review does not release candidate generation, trial execution, final delivery, or target-reference evaluation. Those stages still require source/model review and runner review under the frozen protocol.

Current reviewed protocol SHA-256: `9f2589e1e5b51218d50d55698f300a412b45b159de2ed0ff9a1937d3efd08206`. The initial reviewed version, preserved as `PROTOCOL_v0_acquisition.json`, has SHA-256 `2cc3004b009ae6897f6f43f58b4e896b38ed73a70d1836412c3e4d525d768bb1`; see the metadata-only amendment review below.

## Scope and evidence

Read only the new protocol, both case profiles, and the four bundles' task/request/author instructions, gateway configuration/binding/session metadata, empty registry and search ledger. Verified task/request hashes against the protocol and provider hashes against the case profiles. Compared the two author tasks within each case after normalizing slot identifiers; they match. All four author instruction documents match after normalizing identifiers and bundle paths.

At this review snapshot, all four gateway states recorded zero queries, downloads and HTTP attempts; all registries and search ledgers were empty. This is a pre-acquisition review, not proof of later compliance or a functional network test.

No reference report, individual data, generated table, scientific source paper or candidate was opened in this review. No literature request, generation, fit or scientific test was executed. The reviewer had historical result exposure during the preceding scope audit and is not represented as a blinded scientific author; no result values or scientific parameter choices are supplied here.

## Design findings

1. **The experimental purpose is bounded and useful.** A common acquisition/construction/review policy is applied to two existing requests with two authors per case. This addresses repeated execution of the current workflow and variation among independently authored constructions. It is not a controlled search-effect experiment, a requirement to replace closed historical results, or new clinical confirmation. Four authors, two exposed reference families and up to twelve final draw tables remain separate counting units.

2. **The acquisition condition is explicit and symmetric.** All authors use the existing Europe PMC/PMC gateway with self-selected queries and no supplied DOI seeds. Eight query credits include fetch metadata; four original-study downloads/serious reads is the maximum. Failed and rejected actions consume their actual gateway budgets and remain in logs. Gateway configuration also fixes 96 auxiliary requests, ten results per search page and a 16 MiB response limit. These are bounded accessible-primary-literature searches, not unrestricted web retrieval. The gateway may conservatively reject papers; the contract correctly requires recording that limitation instead of bypassing it.

3. **Source and target boundaries are appropriate.** Both CHNS and ENSANUT participant-based studies are excluded as generating evidence for every slot. Authors receive the population, measurements, intended analyses and process rules without target numerical answers, a desired direction, a named paper or a prescribed probability family. Author instructions forbid other authors' material, old constructions, manuscripts, target results and individual records. The boundary is procedural rather than OS isolation. Acquisition may continue during proposal/model preparation within the original budget, but closes at first candidate freeze; any newly proposed source still needs review before its use is frozen.

4. **The six focal estimands are unchanged.** CHNS preserves BMI adjusted for age/sex; glucose adjusted for age/sex; and age adjusted for BMI/glucose/sex, with intercepts, raw units and OLS. ENSANUT preserves full-model age10, age/sex-adjusted bmi5 and full-model bmi5, with the original transformations and eight age/sex cells receiving equal mass. Its task requires 375 fictional people per cell and retains the selection/measurement restrictions. It is not national-survey estimation. No additional CHNS conditional-BMI target endpoint has been inserted.

5. **Feedback is qualified correctly.** Semantic feedback may provide explicitly approximate source comparisons calculated on generated target-population data under stated transfer assumptions. That is not source-population replay. Unsupported operators remain unavailable. The generated-only case provider must not read reference values. There is no biological-agreement gate or universal quality threshold, and no pooled cross-unit score or retrospective equivalence threshold.

6. **Adaptation and stopping are bounded.** Each slot has at most one initial trial, one scientific revision and its trial, then a final model choice before the three fixed final draws. Selection between the retained initial candidate and the one revised frozen candidate is allowed using the permitted trial feedback. A second scientific revision, quota reset, final-draw model selection, replacement author or replacement seed is not allowed. Failed physical attempts remain charged within the total cap of twenty. Terminal failures may close without deliverable rows. Up to two mechanical/source-review rounds before each freeze is an explicit preparation limit, not an allowance to redesign repeatedly in response to target values.

7. **Evaluation remains behind the common closure barrier.** The pinned existing aggregate reference may be read for this batch only after all four slots close and scheduled final attempts are resolved. No new target fits are authorized. All prespecified analyses, provider diagnostics, failures and unavailable quantities must be retained regardless of agreement. Same-seed draws across authors do not turn author differences into independent clinical replications or quantify evidence/transport uncertainty.

## Required gates after source-only dispatch

- Review each actual source-selection record, numerical extraction and proposed construction before candidate implementation proceeds. Evidence scarcity and unsupported joint relationships may be reported; they must not trigger target inspection, supplied parameter values or an unbounded search extension.
- Before any row-producing execution, independently review the runner and candidate bindings, budgets, finite-moment claims, scientific transformations, specification/code agreement and generated-only feedback. Verify ENSANUT quota enforcement and equal-cell evaluation rather than merely substituting its path into a CHNS runner.
- Bind the actual runtime, controller/evaluator and frozen candidate/source identities before execution. The verified existing provider identities below do not certify a new runner or its environment. Record scientific versus mechanical interventions and retain earlier submissions.

These are the protocol's stage gates, not a request for a new user-permission round. No design defect requires blocking the source-only phase.

## Verified metadata identities

| Item | SHA-256 |
|---|---|
| CHNS generated provider | `aea016b2f3c607ad0a77b3e4a0f914d3bc436b0b7047c690b81606b10d179c12` |
| ENSANUT generated provider | `1a5a3cd6126211dc2e24f2d1c7fa58e4afdbc980e29c6fdccb6b637c7cf4e551` |
| CHNS new profile | `b414639637de3181f78db5b99eee547d67939a9f2aa734c6ffebf8ea6d03b245` |
| ENSANUT new profile | `31c0e5d19e2a19349da1d6ee31b286349c85acbf9e15dde75af338452d532ffa` |
| Common gateway configuration | `5fdc114451ebb91cb877a4f1baf6f46135ab36da73b85f0572b6c8399cb44676` |

All eight task/request hashes match their protocol bindings. The reference hash is a protocol binding only in this review; its target file was deliberately not opened or independently hashed.

## Pre-freeze dependency amendment review

The final integrity check detected a concurrent protocol change. Read `PROTOCOL_DEPENDENCY_AMENDMENT.json` and the new protocol; verified the preserved initial file's hash and compared parsed JSON after removing the new `dependencies` field. The resulting objects are identical. The sole change lists three existing case-provider import dependencies: the CHNS evaluation module, its analysis-plan metadata, and the ENSANUT analytical engine. No analysis, source allowance, task binding, trial/final allocation, information boundary or scientific input changed.

The amendment states zero scientific generations before its recording. This review did not run or inspect those dependency implementations and therefore does not certify their runtime behavior; they belong in the later runner review and execution manifest. The source-only decision above applies to the new protocol hash as well. The earlier zero-usage bundle observations remain explicitly a review-time snapshot, not a claim that no authorized source acquisition began afterward.
