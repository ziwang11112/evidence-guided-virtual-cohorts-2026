# Top-venue strategy: a claim-changing capability, not a formatting change

Assessment date: 3 November 2026, America/Chicago (4 November UTC). This is an independent strategy review of the completed [v0.8 manuscript](DRAFT_v0_8.md), its [remaining claim gaps](KEY_EXPERIMENT_GAPS_v07_2026-11-03.md), [existing-reference feasibility](EXISTING_REFERENCE_FEASIBILITY_v07_2026-11-03.md), and earlier C3/C4 results. It supersedes PLOS-as-default planning for this user's current aspiration; it does not invalidate the completed draft or the fallback venue assessment.

**Recommendation: make the next research decision around a use-inspired AI-method capability. Keep Nature Communications as a distinct scientific-methods ambition rather than an interchangeable destination for the same evidence.** First test whether a concrete extension changes the usefulness of generated biomedical data. A positive pilot would justify further development, not establish top-venue readiness.

## What the official criteria actually say

Only three official pages were selected and read for this check. The assessments in the next sections are our judgments, not promises from editors.

| Source | Verified criterion, paraphrased | Implication for this project |
|---|---|---|
| [NeurIPS 2026 Reviewer Guidelines](https://neurips.cc/Conferences/2026/ReviewerGuidelines), General and Use-Inspired sections | Use-Inspired work can frame or design methods around a genuine external need. Originality can arise from an appropriate combination or problem framing, rather than a wholly new algorithm. Evaluation should fit the use, explain effective/ineffective choices and consider relevant non-ML approaches. | A biomedical evidence-to-data problem can be a legitimate main-track contribution. A new training loss, foundation model or wet laboratory is not a universal requirement. The contribution still needs a consequential insight/capability and evidence. |
| [ICLR 2027 Reviewer Guidelines](https://iclr.cc/Conferences/2027/ReviewerGuidelines), reviewing steps | The central questions concern the specific problem, motivation and literature position, rigor of the claims, and new knowledge/value for the community. State-of-the-art benchmark results are not necessary. | We need a clear, generalizable finding about scientific data generation. Neither “Agent” branding nor a universal leaderboard win is the defining requirement. |
| [Nature Communications aims and scope](https://www.nature.com/ncomms/aims) | The multidisciplinary journal seeks important advances significant to specialists in the relevant field. | A scientific-methods contribution is possible, but the paper must show why the new capability matters substantially to its research community. Scope alone does not provide an acceptance test. |

The NeurIPS and ICLR pages were directly opened. The Nature page's official indexed content was read; direct opening encountered an inaccessible identity-provider redirect. No dates, submission availability, impact factors, acceptance probabilities or future policy continuity were inferred. The year-specific guidelines inform the scientific comparison; a future submission cycle would need a separate check.

## Two different paper arguments

| | Use-inspired AI / ML methods argument | Nature Communications scientific-methods argument |
|---|---|---|
| Central question | Can an Agent perform a difficult, reusable evidence-to-model operation that improves the usefulness of generated data under a defined information constraint? | Does the method enable a consequential class of biomedical/scientific analyses that was materially difficult before, with convincing evidence of that benefit? |
| Persuasive unit of evidence | Requests, evidence configurations, operator families and independent constructions; analysis results from the generated cohorts | Scientifically meaningful use cases, coherent source/target evidence and analyses that establish the advance's value beyond implementation |
| Role of biomedical cases | Motivate a genuine need and test whether the formalized capability matters in practice | Demonstrate the specialist significance of the methodological advance |
| Current strength | Complete-cohort authorship, a concrete numerical-translation example and several usable analysis results | A real access/measurement problem, useful reconstruction, a complete longitudinal data product and inspectable evidence |
| Current gap | No isolated, repeatable advantage or new insight attributable to a specific operation beyond close agentic/aggregate-generation predecessors | Current evidence largely shows developmental transfer and source-rich reconstruction; it does not yet establish a consequential change in biomedical research capability |

These are strategic interpretations, not journal rules or a demand that every paper invent a new algorithm. A new biomedical discovery is one possible NC route, not a universal requirement. A strong broadly enabling computational method could also qualify. Conversely, a successful new held-out cohort is useful evidence but does not by itself establish a distinctive AI method.

The immediate choice should be the AI-method capability question because it can be falsified using the available infrastructure without reopening revealed clinical references. PLOS/JBI remain valid fallback choices for the existing bounded paper. Selecting a more ambitious target should change the evidence question, not merely the title or template.

## The most useful next question

The candidate developed from the project record is **query-directed acquisition of missing joint evidence**:

> Given partial published evidence and a requested analysis, can the Agent identify which additional observed study result would resolve a consequential ambiguity, acquire that result within a fixed budget, and generate data that support the requested analysis better?

This keeps virtual data as the output. Its potential value is that evidence acquisition is guided by the downstream scientific use, with population, measurement and adjustment meanings retained.

The distinction remains narrow. Active design, disagreement-based acquisition and informative missing-joint selection are established ideas. The [neighbor audit](TOP_VENUE_NEIGHBOR_AUDIT_2026-11-03.md) identifies important overlap in LLMSynthor and G-Sim. “Find a missing statistic and revise” cannot be presented as a new general mechanism. The potentially valuable capability is choosing and using an **actually observed external result in its own study context**, rather than inventing a missing joint table or treating every source statistic as a target-population constraint.

## What the existing experiments rule out as a new headline

[C3](../docs/C3_SOURCE_CONSTRAINED_GENERATION_RESULTS_2026-10-31.md) already executed source-context replay and scalar calibration, with gains for one structure and regression/profile trade-offs for another. Adding another aggregate fitting objective is not automatically a new capability.

[C4](../docs/C4_REVISION_ACCEPTANCE_RESULTS_2026-10-31.md) already showed that two source-compatible joint laws can imply opposing adjusted analyses. That is an intentionally constructed identification example, not a new discovery that partial statistics fail to identify a distribution. Its selector comparison was nondiscriminating because all policies received retained identical scientific models.

A new controlled semantic test would be useful if it isolates a previously untested operation. By itself, recognizing that adjustment sets, selection or measurement transforms matter demonstrates correctness on the fixture; it does not establish new statistical theory, clinical transport or a contribution beyond the predecessors. Genuine alternative laws and an informative new observation are needed for an acquisition mechanism to have something to do.

## A fair discriminating pilot

The final protocol belongs to the root decision. The following defines what a useful small pilot must distinguish; it is not an execution release.

1. **Commit real alternatives.** Construct at least two genuinely different, source-compatible model completions that imply different requested analyses. Freeze them before revealing any candidate evidence values. Record the source of the alternatives; their disagreement is a heuristic, not calibrated uncertainty.
2. **Use one fixed candidate corpus and information budget.** All policies receive the same source records, candidate metadata, requested analysis and initial model pool. Candidate numerical results are not visible before selection. Every policy can obtain one additional observed result and has the same opportunity to update/generate.
3. **Include finite competent controls.** Compare the proposed source/context-aware acquisition with a capable ordinary Agent and an appropriate generic disagreement-based acquisition rule. Use the same update and generation stage after selection. This targets the claimed operation without demanding a custom optimal statistical generator for every biomedical dataset.
4. **Avoid an obvious-answer fixture.** If one item is simply labelled as the exact requested regression and others are unrelated, the test mostly measures label matching. Plausible candidates should differ in what they constrain because of study context or operator meaning. Those differences must be representable by all policies; the comparator cannot be deliberately denied the metadata.
5. **Measure the generated data's analysis.** Primary evidence is improvement in a prespecified effect/association computed from the delivered virtual cohort, together with retained compatibility with existing source information. Retrieval accuracy, source-fit loss and attractive generated marginals are intermediate diagnostics.
6. **Keep the hidden law out of choices and repair.** A truth-known constructed world is useful for this mechanism question. It must not be described as patient validation. Research questions can be visible; the reference law/results remain evaluation information.

An illustrative bound is two task configurations × three acquisition policies × two independently constructed initial pools × two sampling seeds = **24 final tables**. The scientific units are tasks and initial pools, not 24 independent biomedical studies. The protocol must separately cap initial completions, all model calls, feedback/evidence queries and any temporary outputs so the final-table count does not hide an open-ended search. This design is for triage, not a claim of stable general performance.

A metadata-deleted arm can diagnose whether context matters, but is not a sufficient main comparator because it changes the information available. An all-evidence or oracle arm can diagnose information sufficiency; it is not an attainable competitor under a one-item budget.

## Go, simplify or stop

**Go to a larger frozen capability study** only if the added operation produces a reproducible analytical gain under the prescribed budget, while the complete results exclude a mere source-fit or simulation-noise explanation. At least one discriminating task should involve meaningful source/operator context rather than exact-label matching. A favorable small result warrants a new, separately held-out task distribution and then a suitable real-evidence use; it does not retroactively make development cohorts unseen.

**Simplify** if ordinary Agent selection or generic acquisition achieves the same benefit. Useful data generation can remain the contribution, but the new acquisition policy is not the explanation. Report that result rather than adding more selectors.

**Stop this extension** if the finite corpus contains no evidence capable of reducing the ambiguity, if the proposed policy merely invents the missing relation, if only source-fit improves while the requested analysis worsens, or if all policies make indistinguishable choices. A known absence of identifying evidence is not a failure that a stronger Agent can necessarily overcome.

These are proposed decision principles. Numeric tolerances and success thresholds must follow the specific task and be fixed before evaluation; no retrospective “almost equal” rule is supplied here.

## What greater scale should mean

More generated rows mainly reduce Monte Carlo variation. More seeds describe one law's sampling variation. Neither establishes broader reasoning or clinical knowledge. For this claim, useful expansion would vary the **scientific request, operator/adjustment context, evidence availability and source-population conditions**, while preserving a fixed construction protocol and adequate controls.

More real cases would become valuable when they test those capabilities in genuinely different evidence settings. A stack of nearly identical glycemic tasks would provide less new information than a smaller study that shows when the proposed operation works, when it fails and why. No new cohort acquisition is recommended in this review, and the existing feasibility audit remains unchanged.

The objective is a stronger, testable data-generation contribution. The pilot is a decision tool for reaching it, not a substitute for the final scientific paper.
