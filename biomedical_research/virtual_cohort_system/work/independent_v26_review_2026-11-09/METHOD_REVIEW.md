# Independent review of the v0.26 Agent method

Reviewed 9 November 2026. Scope: current manuscript plus selected actual Q1/Q4/iron inputs, controllers, submitted programs, and release documentation. This is an independent reading of implementation evidence, not an adoption of the method-coverage audit's conclusions. No participant/generated table was opened, and no generator, evaluator, test, or new experiment was run. Only this review file was written.

## Overall assessment

The method is now identifiable: an externally dispatched language-model author turns a task and admitted evidence into a conventional joint probability model and executable sampler; a host coordinates admission, scientific/implementation review, trial execution, selection, and closure; deterministic programs generate and analyze the records. The contribution is the evidence-to-model authoring procedure and its documented applications, rather than a new statistical family or one uniform autonomous runtime. The manuscript largely says this accurately (`manuscript/DRAFT_v0_26.md:31`, `:41`, `:91`, `:187`).

The iron example clearly distinguishes investigator-supplied extraction/qualification from author discretion. The packet already supplies counts, unit conversion, the crude versus adjusted odds-ratio distinction, and the contextual status of corrected ferritin (`work/iron_breadth_2026-11-05/admission/SOURCE_PACKET.md:3`–`:8`). A then chooses reweighting and decoupling: these are literally the 2/3 weight and 0.2 branch in its final code (`work/iron_breadth_2026-11-05/candidates/A/final/generator.py:66`, `:83`–`:88`). B chooses within-band dependence and retains one law for both contexts (`work/iron_breadth_2026-11-05/candidates/B/final/generator.py:47`–`:68`, `:71`–`:77`). Those distinctions match manuscript Table 1 and Sections 3.2–3.3. Arbitrary but disclosed transfer assumptions are a scientific limitation to evaluate, not by themselves an implementation defect.

The main remaining weakness is reproducibility of the *authoring procedure*, contrasted with inspectability and potential replay of the *frozen programs*. I found no new numerical or generator bug in the selected paths. The three findings below are operational reporting/reproducibility issues; they do not warrant regenerating the published studies.

## 1. High priority: identify the authoring system per study and state precisely which part can be reproduced

**Affected manuscript:** `manuscript/DRAFT_v0_26.md:195`, `:203`, `:471`, `:481`, `:503`.

The manuscript already acknowledges incomplete historical model identities and incomplete reproduction of model-authoring sessions. The issue is therefore not an absent disclaimer. It is that the reader still cannot identify the actual model/service/configuration behind the central Agent evidence, or distinguish a recoverable authoring recipe from an immutable record of what happened.

**Direct implementation evidence:**

- The central Q1 dispatch records explicitly give `model_identity` as “inherited host model; exact backend identity not exposed by dispatch tool,” with null token metering, for both first E0/E1 authors (`work/main_study_freeze_2026-11-03/FIRST_PAIR_DISPATCH.json:5`–`:22`). Thus this problem affects the central evidence contrast, not only a peripheral historical pilot.
- The Q1 controller says it has **no model launcher** and that authors are externally dispatched (`work/main_study_freeze_2026-11-03/implementation/main_session_v1.py:1`–`:7`). The Q4 controller also says **no model launcher** (`work/core_workflow_replication_2026-11-04/runner.py:1`). Executing these files is not a recipe for recreating the scientific Agent.
- Q4's dispatch state records author IDs, fresh-context flags, and timestamps, but no model or inference configuration (`work/core_workflow_replication_2026-11-04/STATE.json:10`–`:38`); its C01 contract similarly binds the external author and files, not a model invocation (`work/core_workflow_replication_2026-11-04/sessions/C01/contract.json:2`–`:9`).
- A substantial operative author task is available (`work/core_workflow_replication_2026-11-04/prepare_batch.py:49`–`:69`), which is useful evidence. However, public scope explicitly excludes Agent conversation contexts (`work/core_workflow_replication_2026-11-04/PUBLIC_SCOPE.md:5`). The task text alone does not identify subsequent host dispatches and follow-up instructions as a reproducible session specification.

**Why it matters:** A reader can study the final probability law and potentially replay it with its recorded seed. That is different from reproducing the process that selected the sources, law, and assumptions. The latter is the paper's main procedural contribution. “Some historical dispatches” is a weak substitute for a study-by-study accounting, especially when Q1 and Q4 carry the principal results. This is not evidence that those authors used target results, nor does it invalidate the frozen numerical outputs.

**Minimal remedy:** Add a compact implementation table for the principal studies listing the host/service, exact model snapshot if actually recorded (otherwise explicitly “not recorded”), fresh-context mechanism, externally supplied task/prompt and follow-up record locations, tool availability, and construction/review budgets. Identify Q1/Q4 specifically where information is unavailable. State three separate reproducibility claims: aggregate-display regeneration, frozen-generator replay, and reconstruction of original Agent authoring sessions. Do not invent missing model identifiers or private reasoning transcripts. Missing author metadata limits reproducibility; documenting that limit does not require a new experiment.

## 2. Medium priority: make the mandatory review phase and its actor explicit in the method being evaluated

**Affected manuscript:** `manuscript/DRAFT_v0_26.md:37`, `:39`, `:55`, `:133`, `:299`–`:303`, `:371`.

Section 2.2 says the coordinator “can request scientific or implementation review.” The supplement does correctly say Q4 and Q5 underwent independent review before execution. However, for Q4 this was a required, staged part of successful construction, not an optional adjunct to the author/worker feedback loop. A reproducible method needs to say who performed those judgments, when the author could amend a proposal/program, and which changes count as a scientific feedback revision.

**Direct implementation evidence:**

- Q4 first requires a source-use request and proposed law, prohibits candidate generation at that stage, and sends the author back to the controller for review (`work/core_workflow_replication_2026-11-04/prepare_batch.py:61`). It then permits up to two mechanical/source review rounds **before each freeze** (`:67`).
- Every candidate freeze requires an outside review bound to all candidate files (`work/core_workflow_replication_2026-11-04/runner.py:266`–`:296`). Required review flags include source semantics, finite moments, and scientific specification/code consistency (`:298`–`:303`). Final selection also requires a review binding the chosen freeze and decision (`:383`–`:404`).
- The executed C01 static reviewer is `root_static_review` (`work/core_workflow_replication_2026-11-04/C01_INITIAL_STATIC_REVIEW.json:18`), and the source review explicitly records prior project-result exposure while denying target-directed advice (`work/core_workflow_replication_2026-11-04/SOURCE_PROPOSAL_REVIEW_C01.md:9`).
- This was more than an empty signature: the E02 source addendum corrected two printed residual variances and instructed the author to retain the reviewed formulas (`work/core_workflow_replication_2026-11-04/SOURCE_PROPOSAL_REVIEW_E02_ADDENDUM.md:5`–`:12`). The recorded E01 path-name repair was separately mechanical (`work/core_workflow_replication_2026-11-04/E01_PREFREEZE_MECHANICAL_REPAIR.json:3`–`:10`). Neither is evidence of a target-directed scientific change.

**Why it matters:** A new user implementing “author a model, run one trial, retain/revise” would omit a required source/proposal/static-review stage of the headline Q4 procedure. Also, “all retained the initial model” refers to the first **frozen, already reviewed** model, not necessarily an untouched first response. The current wording is not false, but the operational unit and contribution attribution remain underspecified. The correct claim concerns an Agent author working within a host-reviewed workflow.

**Minimal remedy:** Add the proposal/review/freeze stage to the main method and identify the actor performing it (host Agent, other reviewer, or investigator, as the records support). Report the permitted review rounds and a short intervention classification, separating source/transcription corrections, implementation repairs, and post-trial scientific revisions. Preserve the current no-revision-gain qualification. This does not require adding multiple scientific authors or making multi-agent collaboration a methodological requirement; it simply describes the reviews actually required for these runs.

## 3. Medium priority: give outsiders a reproducibility entry point independent of the original host directory

**Affected manuscript:** `manuscript/DRAFT_v0_26.md:203`, `:467`–`:471`, `:481`, `:503`–`:505`.

The manuscript offers code and computational verification, and S10 usefully provides the iron ABI and execution-note link. The public artifact scope is nonetheless a research export with a host-specific execution/audit path. This distinction should be visible at the reproducibility entry point, not only after traversing historical folders.

**Direct implementation evidence:**

- `cohort_harness/execution.py:25`–`:29` fixes the runtime under `/home/zwang/.cache/evidence-cohort-runtime/m2` and the Ubuntu-24.04 WSL distribution. The runtime validator explicitly rejects any configuration different from that exact default (`:45`–`:48`). This is a deliberate original-run constraint, not a generic configurable runner.
- Q4's preparation uses preceding-study task/provider files (`work/core_workflow_replication_2026-11-04/prepare_batch.py:14`, `:26`–`:30`) and its author instructions name a specific Windows Python installation (`:57`). The retained protocol contains original absolute bundle/provider paths (`work/core_workflow_replication_2026-11-04/PROTOCOL.json:6`–`:9`).
- Q4 release documentation explicitly says unexported freeze dependencies and retained originals are necessary for a complete execution audit and that the export is not a turnkey portable clinical rerun (`work/core_workflow_replication_2026-11-04/PUBLIC_SCOPE.md:5`). Its documented runnable convenience regenerates the aggregate plot without invoking an Agent, generating rows, or refitting data (`:9`–`:15`).
- In contrast, the iron bridge is a compact, understandable reusable scientific interface: `generate(n, numpy.random.default_rng(seed), context)` (`work/iron_breadth_2026-11-05/iron_runner.py:27`–`:38`), with explicit source/target seeds and sizes (`:21`–`:24`). Its final generator is therefore substantially easier to replay than the complete historical audit pipeline.

**Why it matters:** A frozen model may be perfectly inspectable and reproducible by a knowledgeable reader who writes a small caller, even when the supplied controller cannot run unchanged on another host. These are different capabilities. The existing artifacts support the first more directly than end-to-end reproduction. I did not execute a clean-checkout reproduction, so this is a demonstrated portability constraint and documented release limitation, not a claimed reproduced runtime failure or numerical bug.

**Minimal remedy:** Supply one short, versioned reproducibility guide distinguishing (a) aggregate figures, (b) sampling one unchanged frozen generator with dependency versions, seeds, row count and ABI, and (c) restricted clinical-reference evaluation and original host audit. Explain which artifacts can be obtained separately and which are unrecoverable/unpublished. Preserve original commitments unchanged; a portable demonstration can have its own manifest. For the present paper, accurately scoping the release and documenting the standalone sampling recipe is sufficient; the review does not request new cohorts or a new validation study.

## What should not be raised as a new defect

- **Controller heterogeneity is disclosed.** Sections 2.2, limitations and S15 explicitly separate historical and later interfaces (`manuscript/DRAFT_v0_26.md:41`, `:195`, `:542`). A single rebuilt controller is not required for the current bounded claim.
- **Source feedback is qualified.** Q4's 29 approximate versus 39 unavailable checks and lack of true source replay are explicit (`:303`); Q5's 132 unavailable checks and absence of numerical source-fit feedback are explicit (`:383`). These reduce what the checks establish, but the manuscript does not silently call them passed constraints. Q4 runner feedback independently confirms this scope (`work/core_workflow_replication_2026-11-04/runner.py:367`–`:375`).
- **Author isolation is procedural; generator isolation is technical.** The Q1 dispatch and Q4 task explicitly record this difference (`work/main_study_freeze_2026-11-03/FIRST_PAIR_DISPATCH.json:26`; `work/core_workflow_replication_2026-11-04/prepare_batch.py:51`). No evidence inspected establishes author leakage; no leakage allegation is warranted.
- **No new causal revision or superiority experiment is needed.** The manuscript already denies retrieval/revision-effect identification, separates reconstruction controls, and bounds the fixed comparator. Multi-agent scientific voting, training, and comparison with an unspecified optimally designed statistician are not requirements of its present claim.

In sum, the strongest needed revision is an explicit operational specification and tiered reproducibility statement. The manuscript now exposes what the Agent chooses and what remains assumed; the historical records do not yet let an outsider reproduce the original Agent authoring sessions from the paper and exported code alone.
