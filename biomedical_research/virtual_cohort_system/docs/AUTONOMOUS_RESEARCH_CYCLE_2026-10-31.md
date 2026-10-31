# Autonomous research cycle: evidence to analytically useful virtual data

Started 31 October 2026 following the user's explicit request to set up an Agent that continues discussion, implementation and improvement. This plan authorizes a bounded first cycle of the continuing project. It is not a frozen scientific protocol or a report of new performance.

## Stable objective

Turn published biomedical evidence, a target-population specification and optional observed measurements into virtual data that support useful scientific analyses. Complete-cohort generation with no individual records remains a core capability. Unmeasured-variable enrichment and partial missing-cell completion remain additional regimes; do not collapse the project to one missing column.

An ordinary scientific Agent is a valid method. Multi-Agent organization, a new loss, training, beating another Agent, and exact agreement with every reference statistic are not requirements. Test a comparison when a particular improvement claim needs it. Agent discussion, source fit and implementation success are not substitutes for analytical validation.

## Starting evidence and next question

[M17-B](../MILESTONE_17B_RESULTS.md) demonstrated selected adjusted-relationship agreement in six complete virtual cohorts, with mixed magnitudes, unresolved reference curvature/interaction, and no revision gain because both builders retained their models. Its measured reference is exposed and closed to tuning. The [interpretation clarification](M17B_REFERENCE_INTERPRETATION.md) distinguishes measured sample statistics from unknown population quantities.

The next question is: **Which downstream analytical conclusions are supported by the available study-conditioned evidence, and which depend on untested joint-distribution or transport assumptions?** Answer this through one independently admitted real biomedical case and, if it resolves a concrete mechanism question, one small controlled experiment. Do not create a broad benchmark merely to produce more rows or tables.

A read-only independent reviewer recommended testing source-population interpretation and identifying weakly constrained relationships. Adopt that question, not an automatic obligation to build every suggested arm. A controlled result cannot establish biomedical transport; the real-case validation remains necessary for the scientific-use claim.

## Work sequence and deliverables

1. **Design and admission.** Review existing failures and audited results; compare at most three new candidate data sources on metadata, accessibility, population/measurement definitions, joint/conditional evidence and independence. Prefer a distinct study family or biomarker. Read at most twelve new primary studies during this cycle. Choose one case before inspecting its held-out outcomes. Deliver `CASE_ADMISSION.md`, `EVIDENCE_REGISTER.json` and a prospective protocol in `work/autonomous_research_2026-10-31/`. Reject or defer cases for evidence/data reasons, never because inspected results are unfavorable.
2. **Scientific protocol and independent review.** Define target population, estimand, actual intended use, variables and units, available individual-data regime, permitted source evidence, overlap/exposure ledger, source operators, assumptions and unresolved quantities. Prespecify about three primary analytical questions plus limited relevant distribution diagnostics. Distinguish source-constrained relations, unprovided analyses and weakly identified quantities. Use defensible practical tolerances when available; otherwise report estimates and uncertainty without claiming equivalence. Record generation/revision/seed schedules and reference access boundaries before execution. A separate reviewer checks statistical definitions, executable source mappings and feasibility.
3. **Implementation and evidence-only generation.** Fix only real implementation defects, preserve historical artifacts, and run meaningful focused checks. Fresh-context builders receive the admitted task and sources, not prior hidden-target results or evaluator answers. They select scientific structures and parameters from evidence or explicit assumptions; the root must not insert desired relationships. Default to the existing Agent-authored program route with isolated execution. The direct-row route remains available if it answers a concrete question within the same budget. No host-execution fallback for Agent-generated code.
4. **Frozen evaluation and interpretation.** Use the same frozen outputs for all declared analyses. A separate custodian evaluates the newly reserved real data; an independent checker recomputes results. Report useful relationships, mismatches, uncertainty, dependence on assumptions, retentions and failures. No post-release tuning or endpoint-specific regeneration. Save the complete result and an evidence-based continue/simplify/stop decision; sync approved code, documents and aggregate results to the existing private GitHub.

Design, implementation and dependent execution may proceed within the same work period once their substantive prerequisites pass. A thirty-minute heartbeat is recovery cadence, not a delay between steps. Do not spend successive work units rewriting plans without resolving an evidence, implementation or evaluation question.

## Optional controlled mechanism check

Use this only if source-condition handling remains the concrete mechanism to test. A separate custodian can construct a known joint population and finite-sample published-style summaries under compatible versus heterogeneous source compositions. Builders receive those summaries and their sampling uncertainty, not the exact hidden generative parameters.

Compare condition-aware and pooled-summary handling only when making that mechanism claim, with the same evidence, structure and computational budget. Preserve a compatible-source condition so the comparison does not artificially disadvantage pooling. An unreported relationship is not automatically identifiable: explicitly test or defer assumptions needed to recover it. These data are invented engineering/mechanism cases, not patient evidence or independent biomedical studies.

Maximum controlled schedule: two evidence packets per source condition, two paired handling variants and three fixed draws, yielding at most twenty-four final tables. Prefer no iterative revision in this isolation test. Define the exact schedule in a separate protocol before running; this ceiling is not an instruction to consume the full budget. Controlled results may guide the still-unopened real-case protocol; disclose that development history and freeze the real-case protocol separately before target access.

## Real-case ceiling and interpretation

One fresh real case in this first autonomous cycle; at most two independent Agent constructions, one source-feedback revision opportunity each, and three fixed analytical draws per stage. There are at most twelve distinct scheduled outputs; retained initial/final files are shared identities rather than extra independent evidence. Track source-feedback executions separately and cap them in the prospective protocol. No automatic second real case after an unfavorable result.

Define whether the target is a finite cohort, standardized population or survey population. Reference uncertainty must match that design; reference means and effect estimates are not known population truth. Conditional variation across generated seeds is not evidence, parameter, structural or transport uncertainty. Additional generated rows do not create additional measured participants. Mere interval overlap, a shared sign or a nonsignificant difference is not equivalence.

The primary success question is whether frozen virtual data support prespecified scientific analyses under stated conditions. Marginal diagnostics matter where they affect those uses; do not turn all discrepancies into a universal loss or dismiss them merely because references are uncertain.

## Ownership, resources and stop rules

- Root owns scientific decisions, shared continuation state and automation. Delegate source review, method critique, fresh builders and independent checking with explicit file/knowledge boundaries. Do not call role agreement an empirical result or promise that all filesystem tools are technically isolated.
- Before resuming, check actual agent/process/session state and recorded output bindings. Reconcile interrupted work before relaunching it. Only actual scheduler events count as scheduled continuations; this setup and foreground work do not.
- Use existing local CPU/runtime and available subagents. No new paid API, model training, HPC launch, controlled-data application, publication, external messages or system changes. The user's availability of HPC does not mean a job has been requested.
- Public, legally accessible article and processed-table acquisition is allowed within the case admission: at most 250 MiB newly downloaded in this cycle, at most 100 MiB per file; record sources, actual size and integrity. Do not fetch imaging/sequencing raw archives or bypass access restrictions. If necessary resources exceed these limits, save a concrete request rather than silently expanding them.
- Keep real and generated participant-level tables, full paper copies and credentials local. GitHub receives only reviewed code, original documentation, metadata and aggregate results through the existing bounded export process. Do not overwrite old receipts or frozen experiments.
- M13-B, M15-B, M16, M17-B and all other revealed targets remain closed to tuning and fresh-confirmation claims. Keep all failures and incidental-exposure records. Target results may inform future explicitly developmental questions, not be disguised as independent inputs.
- A technical fault can receive one documented, justified repair with failed attempts retained. A scientific null is not an execution fault. Simplify when added machinery has no demonstrated benefit. Stop a mechanism at its fixed budget rather than searching until it wins.
- End this autonomous cycle after its independently reviewed real-case result, a justified admission failure within the source budget, or a concrete resource/access barrier. Also stop starting new work after fourteen calendar days from setup (2026-11-14); checkpoint safely if work is in flight. Deliver a substantive outcome and next recommendation, then pause the same heartbeat. Do not create a replacement schedule or automatically expand the cycle.

## Resume entry points

Read the user's newest message first, then this plan, `work/autonomous_research_2026-10-31/STATE.json`, the latest active artifacts it names, [M17-B](../MILESTONE_17B_RESULTS.md), [reference interpretation](M17B_REFERENCE_INTERPRETATION.md), and the [roadmap](IMPLEMENTATION_ROADMAP_2026-10-30.md). Historical continuation files describe completed milestones and are not current run instructions.

Discuss choices when they change the scientific scope or need unavailable resources. Routine decisions already authorized here do not require repeated user confirmation. Every substantive unit records the question, actual work, evidence, implementation checks, results or failure, interpretation, resource use and the next discriminating action. This ongoing record supports discussion without replacing actual research.
