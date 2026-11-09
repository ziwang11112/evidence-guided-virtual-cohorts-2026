# Method refinement: actionable scientific checks before more agents

8 November 2026. Design proposal grounded in the existing-case audit. No new generator, controller upgrade or performance improvement is claimed by this document.

## Decision

Keep the scientific author responsible for constructing the virtual data. Improve the connection between the requested analysis, the evidence, the executable checks and the next action. A bounded independent reviewer can participate, but adding reviewers is not itself a demonstrated remedy for missing evidence or population transport. The product remains scientifically useful virtual data, including complete cohorts without individual inputs.

## What already exists

The project already has separate source-proposal, candidate-code and numerical reviews. In particular, the [H03 review](../reports/evidence_use_cross_task_2026-11-05/review/H03_CANDIDATE_REVIEW.md) independently checked the declared law, including moments, projections and support, while all 32 numerical source comparisons remained unavailable. The [H02 review](../reports/evidence_use_cross_task_2026-11-05/review/H02_CANDIDATE_REVIEW.md) similarly recorded 18 unavailable source comparisons. These are records for those candidates, not an assertion that every experiment lacked source checks.

The [semantic feedback implementation](../cohort_harness/semantic_feedback_v1.py) validates declared meanings and calculates supported operators. It does not authenticate extraction or establish source-population applicability. The [analysis-use](../cohort_harness/analysis_evidence.py) and [evidence-use](../cohort_harness/evidence_use_v1.py) interfaces already record analyses, assumptions and parameter references. Repeating those schemas as a new component would not address the current gaps.

The [existing-case diagnosis](../reports/analysis_use_diagnosis_2026-11-08/READOUT.md) found that prominent residual discrepancies are consistent with declared model choices. The prior exact-compatible-summary trial compared instructions; it was not a test of independent multi-agent review.

## Proposed changes

### 1. Turn each unavailable check into a specific next decision

For an intended scientific analysis, the author and reviewer should identify the exact missing input or capability. Extend the current workflow with a short, evidence-bound finding rather than another generic approval label.

| Reason | Appropriate action | What remains unproven |
|---|---|---|
| A necessary operator is unsupported, but the definition and required inputs are available | Implement and independently test that operator; then execute the specified check | Source applicability and target usefulness |
| The paper omits a required quantity, definition or source-population description | Retrieve a supplement or compatible study; otherwise retain a named assumption or restrict the use claim | Missing quantities cannot be recovered by voting |
| Populations, measurement, selection or adjustment differ | Reconstruct the source context when feasible; make the transfer assumption explicit and examine justified alternatives | Source replay does not validate target transport |
| Code contradicts its declared model or a derived identity | Make a minimal reproducible correction and rerun the affected checks | A code repair need not improve every scientific analysis |
| The code implements the law, but the law has unsuitable implications | Reconsider the source-supported scientific construction | Target disagreement alone does not identify a uniquely correct replacement |

The reviewer finding should contain the affected analysis, source/code locator, evidence or calculation, reason, permitted action and observable recheck. A correct retain decision is allowed. Do not require all checks to become computable by silently changing their meanings.

### 2. Check the generated law in addition to its declared parameter names

For program construction, evaluate implications of the full law for requested regressions, variation, dependencies and subgroup structure. Use analytical calculation where available, otherwise isolated numerical diagnostics with their own simulation uncertainty. The author chooses the model; the harness does not insert desired slopes or target values.

Keep three assessments distinct:

- Does the executable program implement its specification?
- Under a defensible source context, does it reproduce the adopted source quantities?
- Does its virtual data support the requested analysis against an external reference?

H03 demonstrates why this matters: a correct conditional association can coexist with insufficient overall spread. Lipids demonstrate that plausible margins and marginal rank correlations do not establish adjusted dependence. Existing independent algebra already checks some of these implications; the proposed improvement is to make the relevant findings actionable within construction, while recognizing absent evidence.

Directly authored tables remain permitted. Their realized analyses can be checked, but a finite table alone cannot certify the tail moments of an unspecified population generator.

### 3. Review scientific uncertainty without manufacturing diversity

Separate individual variation, uncertainty in estimated evidence and uncertainty in model/transport assumptions. More random seeds only address variation between sampled tables. An alternative dependence or dispersion structure must be justified by evidence or labeled as a sensitivity scenario. A small set of scientifically distinct candidates may be useful when evidence leaves multiple possibilities, but their unweighted mixture is not automatically a posterior distribution or a more accurate cohort.

For the current glycemia and lipid cases, prioritize compatible conditional-scale and conditional-dependence evidence. The eight available age profiles do not by themselves repair H03 dispersion, as the completed sensitivity shows. Do not enlarge residual noise to match the disclosed target.

## Minimal collaboration configuration

Use one scientific author, one bounded independent scientific reviewer when useful, and deterministic statistical/execution tools. These are roles; separate paid models or many simultaneous agents are unnecessary. Reuse the existing review capability rather than describe it as newly invented.

The author reads permitted literature, selects the construction and decides how to respond. The reviewer inspects original permitted evidence and actual diagnostic outputs, submits specific findings, and can request focused supplementary evidence. The tools calculate and bind results. The author may revise, retrieve, state a sensitivity or retain. No majority-vote scientific truth or mandatory cosmetic revision is required. New reviewer context is not proof of statistical independence between models.

The existing host coordinates roles; this proposal does not create a standalone model launcher or claim that a prompt creates technical file isolation.

## Small development test before adoption

First use copies of the existing glycemia and lipid artifacts to test whether the improved diagnostic process yields correct, actionable findings. Preserve all original frozen records. Distinguish source-supported corrections from issues that legitimately remain unresolved. No new clinical success threshold is introduced.

If an independent reviewer is then tested, fork an identical starting construction into two conditions: self-review and fresh-context review followed by author response. Both receive the same diagnostic checklist, numerical tools, source packet and total review/revision budget. Record actual token, tool and execution use. Allow one response cycle and no forced revision. Hold evidence fixed in this comparison; study evidence acquisition separately so an improved result is not automatically attributed to reviewer independence.

Inspect final-data scientific analyses, newly introduced failures, preserved previously supported analyses and cost. Findings/format coverage are secondary engineering outcomes. A better review checklist alone is not better virtual-data quality. These exposed cases can establish developmental improvement only; they cannot establish fresh population transport. If collaboration provides no material benefit, retain the simpler implementation.

## Relation to prior work

[G-Sim](https://proceedings.mlr.press/v267/holt25b.html) already combines LLM simulator construction with numerical calibration. [Multiagent Debate](https://arxiv.org/abs/2305.14325) studies improvements in language-model reasoning and factuality; it does not establish biomedical virtual-cohort quality. These support testing specific mechanisms rather than treating agent count as a novelty claim. Our proposed changes remain unproven until the relevant data-use outcomes are evaluated.
