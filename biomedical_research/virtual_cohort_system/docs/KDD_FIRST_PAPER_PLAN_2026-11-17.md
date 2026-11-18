# KDD first-paper plan

Decision date: 17 November 2026, America/Chicago.
Authority: the user asked to pursue two papers while locking KDD as the first priority.

## Target and scope

**Paper 1 targets KDD 2027, the second submission cycle.** This is a venue and work-priority decision, not a claim of acceptance readiness, a submission receipt, or a freeze of unfinished scientific methods. The next cycle is described as February 2027 in the [official Research CFP](https://kdd2027.kdd.org/research-track-call-for-papers/); its exact abstract and paper deadlines have not been verified as published on this decision date.

Prepare one manuscript to the Research Track's technical-contribution standard. Final track selection remains a separate readiness decision: choose AI for Sciences only if the demonstrated domain contribution and substantive domain collaboration fit its [official criteria](https://kdd2027.kdd.org/ai4sciences-track-call-for-papers/). Do not prepare competing ACL, ICML and KDD versions in parallel.

Working title remains:

> From Fragmented Evidence to Analyzable Biomedical Cohorts with Scientific Agents

The paper's central question is whether a scientific Agent can translate a research request and fragmented published evidence into a joint generative model whose virtual records support the intended scientific analyses. Whole-cohort generation without individual target inputs remains in scope. Source interpretation, evidence composition, model authorship and analysis-level usefulness are the central capabilities. Retrieval and revision are available actions, with their actual use disclosed for each experiment.

## Contributions to establish

1. A concrete, executable evidence-to-data task and workflow: the Agent chooses the scientific structure and parameters; isolated tools execute and inspect its program.
2. Evidence composition for requested analyses: demonstrate actual interpretation and derivation, and test how relevant joint information changes downstream scientific results.
3. Analysis-level utility with traceable evidence and assumptions: use the same analysis implementation on generated and measured records, retaining complete endpoint profiles and uncertainty boundaries.

The present evidence supports limited feasibility and analysis-specific improvements. The 78.6% pressure and 46.8% iron improvements refer to their prespecified discrepancy measures, not overall dataset quality. Technical superiority, clinical equivalence, fully automatic source certification and reliable transport are not established by this plan.

## Existing results stay together in Paper 1

| Evidence block | Role in the KDD paper |
|---|---|
| Request-only autonomous construction, 11 November | Demonstrate actual retrieval, modeling and delivery; include the ordinary-Agent comparison and its mixed results |
| Lifestyle application | Illustrate the same scientific analysis with the data replaced; retain all nine contrasts and dispersion diagnostics |
| Controlled composition | Test algebraic composition under known compatible structure, separately from patient validation |
| Pressure and iron three-condition controls | Test joint-information increments beyond marginal-summary additions, including worsened endpoints |
| Source/model provenance and mathematical audits | Explain decisions and inspectability without claiming calibrated confidence or universal feedback benefit |

These blocks are not to be split into separate papers merely to increase publication count. Their information regimes and reference exposure remain explicit. Old results and frozen laws are not modified for the submission target.

## Remaining work, in order

The detailed designs remain in [the v0.33 audit recommendations](../work/v33_core_review_2026-11-17/NEXT_EXPERIMENTS.md). This plan changes priority, not their execution status.

### P0 — Interpret scientific usefulness with existing data

Complete the already designed matched-size real–real / virtual–real diagnostic on the six saved lifestyle tables. Preserve all nine contrasts, the three dispersion diagnostics, the empirical sampling interpretation and the original frozen generator laws. Use the existing [bounded protocol](../work/scientific_use_acceptance_2026-11-16/MINIMAL_VALIDATION_PROTOCOL.md); implement, review and freeze the wrapper before running it. No new API calls or datasets are needed.

### P1 — Connect original papers to the demonstrated modeling capability

Use the existing pressure and iron cases to test whether the Agent can locate and interpret the useful joint evidence in the original papers and construct a generator without coordinator-written numerical packets. Begin with the six-construction feasibility design in the audit recommendations. Record tool use, source exposure, omissions, derivations, manual intervention, all endpoints and costs. Root must not insert target relationships or repair submitted scientific laws using the known target estimates.

The completed request-only study provides background capability evidence. Old fixed-packet results provide context, not a randomized causal comparator for a different input/tool setting. Any stronger policy-effect claim needs a matched protocol and an actual implementation difference first.

### P2 — One faithful, compatible published-method comparison

First inspect whether LLMSynthor can be reproduced credibly for a shared input/output setting. Match permitted information and scientific analysis; disclose any biomedical adapter. Retain the paper's substantive dependence and correction capabilities. Do not rank our results against author-reported scores on a different dataset. If a faithful implementation cannot be established, record the concrete boundary rather than fabricate a weak substitute under the published method's name. Existing matched biomedical reconstruction and ordinary-Agent comparisons remain available evidence.

### Conditional extensions

A second-model repeat of the two content controls is considered only after P0–P2 clarify the contribution. A new population is considered only for a chosen new-population claim. No generic evidence-misuse benchmark, new multi-Agent architecture, model training, HPC run or broad dataset search is part of this priority decision.

## Internal milestones — not conference deadlines

| Working checkpoint | Intended deliverable |
|---|---|
| By 15 December 2026 | Review P0/P1 results and comparator feasibility; decide which contributions the evidence supports |
| By 31 December 2026 | Close the core experimental inventory and claim/evidence map, or explicitly document remaining blockers |
| By 15 January 2027 | Complete the submission-oriented manuscript, principal figures, reproducibility package and coauthor review |
| After the official second-cycle CFP is confirmed | Verify exact deadlines, track-specific requirements, author information, formatting and submission plan |

These dates guide work; they are not completion promises and do not authorize favorable-result selection or weaker checks. Preserve unfavorable and unavailable outcomes. If a milestone is missed, record the reason and revise the schedule openly.

## Paper 2: reserved, not launched

The user is open to two papers. The second paper's question, venue and experiment budget remain undecided. It should have its own central scientific question and substantive validation, with any shared system and prior results clearly identified. A later language/evidence-reasoning study or a deeper biomedical application may qualify, but neither is initiated here.

Paper 1 has first claim on current implementation, evaluation and writing effort. Do not remove evidence needed for KDD to save it for Paper 2. Do not divert the current project into an unrelated topic or a second manuscript merely because another deadline is earlier.

## Status and next concrete action

The [v0.34 KDD working manuscript](../manuscript/DRAFT_v0_34.md) integrates the matched-size application and original-paper construction, with LLMSynthor in related work. The [publication audit](../work/manuscript_integration_v34_2026-11-18/QA.json) reconciles figures and tables with saved estimates and verifies the self-contained Overleaf build. The older v0.33 scientific reading edition is preserved.

The next editorial decision is to review the proposed scientific-use claims and their scope with the authors, then complete the venue-specific submission metadata. The two completed rounds add evidence for specific analyses in exposed study families. Additional experimental work depends on a distinct claim requiring it.

## Execution update — P0 and P1 completed

The [P0 matched-size diagnostic](../work/matched_size_utility_2026-11-17/RESULTS.md) and [P1 original-paper experiment](../work/original_paper_capability_2026-11-17/RESULTS.md) are complete. P1 adds six actual original-paper-reading/modeling sessions and 18 final tables, with independently recomputed analyses and source/code audits. BP slopes are approximately reproduced; pressure dispersion/dependence and iron results retain material discrepancies. No new clinical holdout or revision advantage is claimed. The two studies are integrated in v0.34.

The [P2 feasibility audit](../work/llmsynthor_comparator_audit_2026-11-17/FEASIBILITY.md) is complete. The pinned author repository contains documentation and images. The published algorithm can use the existing iron threshold frequencies, while supporting the continuous iron and blood-pressure tasks would require new assumptions or discrepancy operators. Two deterministic checks illustrate these information gaps. The paper will carry forward the existing matched HRS reconstruction and ordinary-Agent comparisons, and cite LLMSynthor with its documented input and evaluation scope. [Draft text](../work/llmsynthor_comparator_audit_2026-11-17/MANUSCRIPT_INSERT.md).
