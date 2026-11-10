# Method text prepared for v0.27

Prepared from retained study instructions, controllers, reviews and execution notes. This file proposes text only; no historical artifact or manuscript was changed and no generator was executed.

## Main-text insertion

**Table 1. Operational stages of evidence-to-cohort construction.** Required review stages and trial budgets differ by study and are specified in Supplement S12.

| Stage | Responsible actor | Decision or output |
|---|---|---|
| Define the request and evidence boundary | Researcher and host coordinator | Fix population, measurements, analyses, admitted inputs and retrieval budget. |
| Propose the scientific construction | Agent author | Select studies where permitted; choose distributions, dependencies, numerical mappings and explicit assumptions. |
| Review and freeze the candidate | Source/code reviewers and host coordinator | Check source meanings, derivations, finite moments and agreement between specification and code; record the approved program version. |
| Inspect a trial and select a law | Isolated numerical worker, then Agent author | Produce permitted diagnostics; retain or revise within the study budget and record the reason. |
| Deliver and evaluate | Host coordinator and separate evaluator | Draw the fixed deliveries, bind program and output identities, and compare the requested analyses after the study's closure condition. |

The externally dispatched language-model author chooses the scientific law and writes its sampler. The host coordinates the task and review gates; numerical tools sample the selected law and calculate its analyses.

Q4 and Q5 required source/proposal review followed by an independent review before each candidate freeze and final selection. Q1 required an independent readiness review before final selection; its exploratory trials were optional. The iron pilot used a separate source-only review and version-locking process. Pre-freeze source or implementation corrections are distinct from a scientific revision after trial feedback. Thus retention of an “initial” model means retention of the first frozen, reviewed law. Review established readiness to execute, not target validity.

## Supplement insertion

**Table S10. Implementation records for the principal construction studies.** Each controller manages a study-specific execution process around externally dispatched authors; it does not provide a reproducibly specified model-service invocation.

| Study and authors | Recorded model identity | Evidence and required review | Trial budget and executed decisions |
|---|---|---|---|
| Q1: 20 Agent authors; 4 prescribed constructions | Dispatches record an inherited host model; exact backend and token costs unavailable. | Curated condition-specific packets; no retrieval. Separate reviewers checked numerical uptake and finite moments before final selection. Source calculations were analytic, without simulated source populations. | At most two exploratory attempts, one scientific revision and three final draws per construction; 3,000 rows per draw. Seven authors inspected a trial and retained; thirteen finalized without exploration. All 72 final tables followed common closure. |
| Q4: 4 Agent authors | Fresh context IDs and timestamps retained; exact backend/inference configuration not specified. | Up to eight query credits, including fetch metadata, and four originals per author. Source/proposal review preceded implementation; up to two source/mechanical review rounds per stage. Independent review required before freeze and final selection. | One initial and at most one revised trial; three final draws, each 3,000 rows. All four retained the first frozen law. Generated diagnostics included qualified source comparisons, without source-population replay. Twelve unchanged final tables were analyzed by the corrected evaluator. |
| Q5: 6 Agent authors | Shared model service and external author IDs recorded; exact backend/inference configuration not specified. | Reviewed packets; optional four query credits and two new originals per author before freeze. Source/proposal, candidate and final-decision reviews required. | One initial and one optional revised/repair trial, sharing the second slot; three final draws, each 3,000 rows. All retained. All 132 source comparisons were unavailable; generated diagnostics and reviewed derivations remained available. Reference reading followed six closures. |
| Iron: 2 Agent authors | Candidate stages and hashes retained; exact author-model snapshot/inference configuration not recorded in admission files. | Shared packet and pre-author source clarification. Host source-only review and hash locks; the compact adapter did not implement Q4/Q5 review-state gates. | One initial source review and one retain/revise opportunity; 100,000 rows at seed 4101 per source run. A repaired its upper tail and repeated the source check; B retained. Three 5,000-row final tables per law at seeds 5101–5103 were sealed before target biomarker access. |

Fresh-context instructions restricted author inputs procedurally; the sampling program ran in a network-disabled isolated worker. Exact model snapshots, inference settings and per-construction token usage are incompletely recorded. These omissions limit reconstruction of the original authoring sessions, separately from inspecting and replaying the frozen statistical programs.

The [reproducibility guide](REPRODUCIBILITY_GUIDE.md) distinguishes aggregate-display regeneration, frozen-program replay and clinical-reference evaluation. Its iron example documents the existing isolated interface and numerical environment as an unexecuted reference recipe, not a verified clean-install reproduction. Complete original Agent sessions cannot be reconstructed from the incomplete or unpublished model and conversation records.

## Provenance notes — not manuscript prose

Paths below are relative to `biomedical_research/virtual_cohort_system`. They identify existing records rather than a new audit result. Do not insert this list into the main text.

| Proposed statement | Direct records |
|---|---|
| Author responsibility versus host/reviewer role | Q4 `prepare_batch.py:49–69`; Q5 `prepare.py:142–156`; iron `admission/TASK.md:3–7`. |
| Q1 known/unknown model metadata | `work/main_study_freeze_2026-11-03/FIRST_PAIR_DISPATCH.json:5–26`; `DISPATCH_GROUP_02.json:5–27`; `RESULTS.md:52`. |
| Q1 controller, budget and gates | `work/main_study_freeze_2026-11-03/implementation/main_session_v1.py:1–7`, `:23–25`, `:179–193`, `:256–272`; `AUTHOR_CONTRACT_TEMPLATE.md`; `RESULTS.md:9`, `:34–36`. Source-retrieval and revision limits also appear in each task budget; the author contract states two exploratory attempts. |
| Q4 metadata and actual roles | `work/core_workflow_replication_2026-11-04/STATE.json:10–38`; `sessions/C01/contract.json:2–9`; `C01_INITIAL_STATIC_REVIEW.json:18–29`; `C01_FINAL_DECISION_REVIEW.json`; `RESULTS.md:13`. |
| Q4 budgets and review stages | `work/core_workflow_replication_2026-11-04/prepare_batch.py:57–67`; `runner.py:266–303`, `:383–416`; `PROTOCOL.json`; `RESULTS.md:18–23`. |
| Pre-freeze correction is not post-trial revision | Q4 `SOURCE_PROPOSAL_REVIEW_E02_ADDENDUM.md:5–12` records two printed variance corrections; `E01_PREFREEZE_MECHANICAL_REPAIR.json:3–10` records the path-name repair. No target-directed parameter change is inferred. |
| Q5 inputs, service and budget | `work/evidence_use_cross_task_2026-11-05/prepare.py:126–154`; `PROTOCOL.json`; `PROTOCOL_CLARIFICATIONS.md`; `RESULTS.md:29`, `:68–72`; `sessions/H01/contract.json`. |
| Q5 required review actor and gates | `work/evidence_use_cross_task_2026-11-05/runner.py:276–319`; `review/H01_CANDIDATE_REVIEW.json:5–18` identifies a separate review Agent; `review/H01_FINAL_REVIEW.json:7–11` identifies the root coordinator and records retention review. |
| Iron source-only process and metadata scope | `work/iron_breadth_2026-11-05/PROTOCOL.md:5`; `admission/TASK.md:3–7`; `admission/SOURCE_PACKET.md:3–8`; `admission/SOURCE_CLARIFICATION.md:2`; `admission/A_initial.json`; `admission/A_final.json`; `lock_author.py:6–17`; `EXECUTION.md:3–14`; `RESULTS.md:21–23`; `BATCH_LOCK.json`. |
| Runtime boundary and incomplete public author-session reconstruction | `docs/EXECUTION_ADAPTER.md:18–34`; `cohort_harness/execution.py:25–48`; Q4 `PUBLIC_SCOPE.md:5–15`; Q1 `RESULTS.md:52`; current manuscript `DRAFT_v0_26.md:195`, `:471`, `:481`. |

Editorial caution: Q4/Q5/iron metadata statements refer to the retained study records inspected here. They do not infer a missing model identity from the currently running chat or retrospectively assign today's host model to historical runs. No new experiment, source acquisition or timing measurement is proposed or reported.
