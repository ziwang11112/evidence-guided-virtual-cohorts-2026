# Draft readiness and core method freeze checklist

31 October 2026. Planning checkpoint after C4; no new experiment or method freeze is declared by this document. This is the current writing and method-consolidation decision record. Historical protocols, results and freezes remain unchanged.

**Decision: start a provisional manuscript now; consolidate and freeze a minimal method before viewing a new target; freeze the resulting claims after the complete planned evaluation, including unfavorable results.** A favorable target result is not a prerequisite for freezing the method. These are project milestones, not acceptance rules for any journal or conference.

**The scientific core is useful generated data.** Published study-level evidence, a target-population description and optional observed measurements are translated by a scientific Agent into a documented generation process. The same generated data are then used for prespecified scientific analyses. Complete-cohort generation with zero individual inputs remains a central capability; enrichment and missing-cell completion remain supported information regimes.

Provisional working title: *Evidence guided generation of virtual biomedical data for reusable scientific analyses*. The title describes the question, not a proven universal capability. The final novelty claim remains subject to comparison with the closest published implementations.

| Decision | Current status | Required next artifact |
|---|---|---|
| D0: begin a provisional draft | Ready | Write the problem, current implementation, evaluation design, historical findings and limitations with unresolved claims marked |
| F1: freeze the minimal core method v0 | Partially ready; not yet frozen | A compact method specification, bound code/prompts/configuration and a verified source-only end-to-end replay |
| F2: freeze the next case before target access | Not ready; no new case selected here | Admitted case, evidence/exposure register, estimands, interpretation rules, budget and an independent pre-outcome review |
| R1: lock the next results and manuscript claims | Pending future evaluation | Complete planned analyses, independent recomputation and a claim-to-evidence decision, whether positive, mixed or null |

**D0 can be satisfied without another successful experiment.** The current project already has the following writing material:

- [x] A concrete data-access and measurement-coverage problem, with specified inputs and outputs.
- [x] A generation objective that includes zero-individual-input complete cohorts.
- [x] Implemented generation contracts, Agent-authored programs and a separately exercised direct-table route.
- [x] Audited real-data pilots with both useful associations and failures.
- [x] Source-side calibration and artificial mechanism results whose limited evidential roles are explicit.
- [x] A separation between source consistency, independent target transfer and reuse for analyses not directly calibrated.

Write Introduction, the implemented Methods skeleton, evaluation definitions, historical exploratory Results and limitations now. Keep the abstract conclusion provisional. Do not describe the pilots as confirmation of an as-yet unfrozen v0, and do not put predicted improvements into Results.

**Freeze a small method, with five scientific components.** Default to one scientific Agent plus deterministic tools and external orchestration. An ordinary competent Agent is a valid implementation.

| Component to retain | What the version must specify |
|---|---|
| Study-conditioned evidence | Original locator, population and selection, measurement and units, statistic and adjustment set, uncertainty, overlap, and reported/derived/assumed status |
| Agent construction | How permitted evidence and the target specification are used to choose distributions, dependencies, parameters and explicit transfer assumptions |
| Execution and source feedback | The actual generation route, supported statistical operators, source-context approximations, output integrity and failure handling |
| Bounded revision | When to re-extract, seek evidence, revise, retain or stop; fixed budgets and complete initial/final lineage; retention is valid |
| Analytical reuse | One frozen release evaluated by the same prespecified analysis code across approximately three uses, without endpoint-specific regeneration |

The frozen method is a procedure, not one universal disease equation. Agent-selected structures, coefficients, admissible source material and target descriptors can differ between cases under the same declared rules. Each scientific configuration must be frozen before its target outcomes are accessed. Root-written relationships chosen to match an exposed target are not permitted scientific configurations.

Keep direct row authorship, numerical calibration, extra Agents and specialized revision selectors optional. C4 provides no demonstrated selector benefit, so that selector is not required in the minimal core. Automated evidence-gap resolution is a testable extension rather than an already established capability. Training, a new loss, HPC, all three generation modes, multiple model brands and a one-click product are not prerequisites for drafting.

**F1 requires an executable, reviewable method version, not an attractive accuracy score.** Existing modules should be reused; implement only missing connections needed for the chosen case.

- [ ] F1.1 Write one compact core specification: scientific claim, inputs/outputs, roles, evidence policy, assumptions, generation route, revision/retention decisions and stopping rules. Current components exist, but a single paper-version contract is not yet bound.
- [ ] F1.2 Bind the actual code commit or manifest, Agent/task prompts, available tools, dependencies, execution settings and budgets. Record the model identity/settings exposed by the runtime and any unavailable metadata; do not invent them.
- [ ] F1.3 Make case-specific inputs explicit configuration. Document all remaining source-context and evaluator adapters. A documented minimal callable sequence is sufficient; a new user interface or fully autonomous model launcher is not required.
- [ ] F1.4 Give every scientific parameter an evidence, derivation or assumption reference. Unknown dependencies must remain visible; absence from a paper is not zero correlation or independence.
- [ ] F1.5 Demonstrate one source-only end-to-end replay of this exact assembled version, from permitted inputs to actual generated output and computed feedback/decision. Use an approved development fixture or source package, not a revealed target for new tuning. Prior module tests alone do not satisfy this item.
- [ ] F1.6 Independently recompute the small set of critical source operators and check preservation/isolation/lineage behavior actually used. No unresolved implementation defect may change the scientific interpretation. Additional testing is needed only for changed or uncertain behavior.
- [ ] F1.7 Record independent review and the frozen version. Changes that alter scientific decisions create a new version; retain the previous record. Cosmetic changes do not silently relabel scientific outputs.

**F2 locks a scientifically informative case before the answer is known.** It follows F1 and precedes target-dependent scientific choices or disclosure of held-out results to the builders.

- [ ] F2.1 Select the case from access, population/measurement definitions, precision information available without target-effect inspection, and relevant source evidence. Review dataset aliases, previous exposure and source/target cohort overlap. Do not select for favorable inspected effects.
- [ ] F2.2 Define the intended use and estimand: finite cohort, standardized reference or survey population. Prespecify eligibility, weighting, transformations, units, missingness handling and reference-uncertainty calculation.
- [ ] F2.3 Fix approximately three scientific analyses and only the distribution diagnostics needed to interpret them. Include one analysis not directly fitted, without pretending that an algebraically implied quantity is new biological discovery.
- [ ] F2.4 For every analysis, separately record whether its structure is fitted, implied by supplied evidence, assumption-dependent or unassessed, and whether it is evaluated in an independent target. Withholding an analysis name does not remove equivalent information from the evidence or the model's prior knowledge.
- [ ] F2.5 Define useful agreement before disclosure: direction, effect scale, a curve contrast or subgroup conclusion, as appropriate to the actual use. State a scientific basis for any practical tolerance. If no defensible tolerance exists, report discrepancies and uncertainty without claiming equivalence. No universal 10% error or 80% pass-rate rule is imposed.
- [ ] F2.6 Specify source and target uncertainty separately from simulation variation. Multiple rows or seeds do not create new measured evidence. Sensitivity scenarios are not probability intervals unless their probability interpretation is justified.
- [ ] F2.7 Freeze initial/final schedules, seed list, row counts, queries/revisions/execution budgets, failure rules and the complete analysis set. Preserve unresolved and unfavorable analyses. If a primary bundle is defined, its success rule cannot be changed after results are seen.
- [ ] F2.8 Independently review the case contract, evidence access and target-release sequence. Commit all required candidate/output artifacts before the corresponding target reveal. Any incidental target exposure changes the stated validation status.

Accessible published source statistics may be used as inputs; do not artificially hide relevant evidence just to create an apparent test. Sources derived from the target cohort require explicit overlap treatment and cannot simultaneously serve as independent external evidence for that target. Fresh-context builders receive only their permitted package and interface, not result-bearing project overviews. This is a procedural knowledge boundary; generator sandboxing does not isolate all Agent tools.

**The next work unit should answer one question:** can an Agent use applicable joint or conditional published evidence to construct virtual data that support the declared analyses, including reuse beyond directly fitted statistics?

The proposed bounded sequence is:

1. Write the provisional draft and compact method specification; complete F1 with the existing tools.
2. Screen at most three candidate dataset families and audit at most six new primary studies for one fresh real case. These are ceilings, not collection targets. If none is suitable, close admission with reasons instead of inspecting more target outcomes until a favorable case appears.
3. Complete F2. Default to zero-individual-input whole-cohort generation. Select any different primary regime on scientific grounds before target access and retain the broader framework scope.
4. Allow at most two independent Agent constructions, one source-feedback/retrieval-and-revision opportunity per construction and three fixed output seeds per stage: at most twelve scheduled initial/final target outputs. Retained stages share output identities. The case contract must separately fix a source-execution cap before running; a limit of twelve target labels is not a cap on optimizer trials.
5. Evaluate every planned analysis once under the locked release procedure, independently recompute, then make the R1 decision. Do not automatically expand to another case after this result.

If comparing an initial evidence packet with added joint evidence, the contrast tests the value of the added information plus the declared reconstruction procedure. It does not isolate superiority of the Agent algorithm. If a specific algorithmic improvement is claimed, add a capable generation comparator with the same permitted information and comparable budget. Select the comparator after the case's information regime is known; methods requiring unavailable target training rows cannot be the only comparator. A direct-analysis Agent may answer a distinct usefulness question but is not a mandatory opponent for a data-generation claim.

These defaults are planning limits, not a frozen execution protocol or a launch of a new experiment. No target, new scientific job, recurring automation, paid API, training or HPC allocation is started by this checklist.

**R1 closes the result regardless of its sign; the result determines the claim.**

- [ ] All scheduled outputs, analyses, failures and retentions are accounted for; file labels, unique outputs, independent constructions and clinical cohorts are counted separately.
- [ ] Primary effects and relevant uncertainty/diagnostics are independently recomputed, and material discrepancies are resolved with the original records preserved.
- [ ] The same frozen dataset supports the declared analysis set without analysis-specific refitting or row changes.
- [ ] Each use is classified using the pre-outcome rule as supported, mismatched or unresolved; assumption dependence is recorded separately. An imprecise real reference is not counted as agreement merely because an interval includes zero or overlaps another interval.
- [ ] The claim table includes all primary endpoints, scope restrictions and failures. A failed prospective bundle is reported as failed; a favorable subset found afterwards remains exploratory rather than silently becoming a new primary claim.
- [ ] Actual retrieval, generation, feedback, human coordination and compute costs are recorded where observable, with missing metering stated. Generated row count is not a measured reduction in recruitment cost.
- [ ] The results snapshot and manuscript claim ledger are locked. A scientific null is not a software fault. Post-reveal methodological changes require a new developmental version and cannot requalify the exposed target as fresh confirmation.

| Outcome | Manuscript consequence |
|---|---|
| Prespecified scientific uses supported, including reuse | Describe bounded analytical feasibility in that population and information setting |
| Direction supported but relevant effect scale mismatched | Describe qualitative feasibility; do not claim quantitative recovery or overall bundle success |
| Source statistics fit but unprovided analyses fail | Report the failure of analytical reuse and examine explicit joint/transport assumptions |
| Added evidence or revision gives no improvement | Remove the improvement claim; retain the complete contrast and simplify unsupported machinery |
| Reference or external evidence cannot resolve the question | Report unresolved status and the information needed; do not force a success/failure label |
| Documented execution defect | Apply the predeclared repair rule and preserve the failure; distinguish post-exposure development from fresh confirmation |

**Publication claims determine the additional evidence, not the number of components.**

| Claim under consideration | Evidence needed beyond an executable demo | Current gap |
|---|---|---|
| The framework can construct virtual data from study evidence | Bound evidence-to-model-to-output trail with a substantive real case | Supported in pilots; consolidated v0 provenance pending |
| The data support specified scientific analyses | Prospective, independently evaluated real reference and prespecified interpretation | Selected pilot uses supported; stronger claims and new v0 confirmation pending |
| The same method transfers across settings | The same frozen procedure applied in genuinely independent settings, with complete mixed results | Old cases used different versions; they cannot be relabelled as multi-case v0 confirmation |
| An added component improves generation | Information-matched, budget-aware comparison with effective distinct candidates and appropriate replication | C3 is mixed; C4 has no candidate contrast or selector gain |
| Additional literature improves usable evidence | Documented new applicable information and prospective analytical evaluation | Not established by a fixed-packet run or better source fit alone |
| Calibrated uncertainty, patient-measurement replacement or collection savings | Separate statistical, clinical or operational evidence matched to each claim | Not established and outside the initial core claim |

A single bounded fresh case can support a limited feasibility draft. Broader transfer claims require additional independent settings under the same frozen method, selected and registered before outcomes are inspected; there is no rule requiring a quota of positive cases. All completed eligible cases remain in the paper or supplement. Further cases require a separate scientific decision after the first closeout, not automatic scope expansion.

**The manuscript can be organized around four evidence-bearing displays.**

| Display | Content | Status |
|---|---|---|
| Figure 1 and method table | Inputs, three information regimes, Agent/tool roles, evidence conditions and the frozen generation procedure | Can draft now; final version binding pending |
| Figure 2 | All prespecified scientific analyses on the same virtual release versus the real reference, including uncertainty and unresolved outcomes | Historical exploratory panels available; new v0 case pending |
| Figure 3 | Evidence contribution or component comparison, only if actually tested; initial and final analytical effects together | C3/C4 may document limitations, not a positive superiority panel |
| Figure 4 and supplementary ledger | Scope of supported/assumption-dependent/unresolved uses, all failures, source overlap and reproducibility | Can structure now; final entries follow R1 |

Complete the closest-work comparison before asserting novelty: input information regime, access to target rows, study-condition representation, generation/revision route and downstream validation. Existing [G-Sim/LLMSynthor review](GSIM_LLMSYNTHOR_DEEP_REVIEW_2026-10-31.md) and [paper direction](PAPER_STORYLINE_AND_DIRECTION_2026-10-31.md) are starting material, not proof that a generic generate-check-revise loop is new. No venue-specific acceptance or novelty claim is made here.

**Historical evidence remains development evidence for the next version.** M13-B, M15-B, M16, M17-B and Cycle 2 used different configurations and exposed references. C3 is source-side development; C4 is an artificial identification/selection check. Preserve all of them, but do not pool their successes into retrospective confirmation of v0. Current engineering checks establish computational consistency, not biological validity.

Source records: [M13-B](../MILESTONE_13B_RESULTS.md), [M15-B](../MILESTONE_15B_RESULTS.md), [M16](../MILESTONE_16_RESULTS.md), [M17-B](../MILESTONE_17B_RESULTS.md), [Cycle 2](../reports/autonomous_research_cycle2_2026-10-31/results_report/REPORT.md), [C3](C3_SOURCE_CONSTRAINED_GENERATION_RESULTS_2026-10-31.md), [C4](C4_REVISION_ACCEPTANCE_RESULTS_2026-10-31.md). The [implementation roadmap](IMPLEMENTATION_ROADMAP_2026-10-30.md) retains the earlier stage history.

Readiness review: the planning gates were independently challenged against C3/C4 and the roadmap. The review agreed that drafting is ready, method/case freeze is incomplete, and claims must depend on the full new evaluation. This planning review does not satisfy F1's future executable-version review or F2's case review.
