# Shared Agent strategy specification

**Historical specification:** The policies below describe the executed Stage 1 comparison. For the current broader workflow, including autonomous evidence acquisition and never-measured-variable enrichment, use [CURRENT_RESEARCH_SCOPE.md](CURRENT_RESEARCH_SCOPE.md). Multiple scenarios, a fixed marginal-only packet, and program-only generation are not mandatory features of the new design. No frozen Stage 1 instructions are retroactively changed.

27 October 2026. Originally proposed as an extension to the population framework; now implemented and executed in [Stage 1](stage1/README.md). Nine fresh initial builders and eighteen fresh paired revision contexts used the frozen protocol. The results do not establish a general improvement from multiple scenarios. Do not use the evaluation results as hidden numerical targets in any subsequent confirmation prompts.

## Common task and isolation

You are constructing virtual cohorts for research rehearsal using this run's allowed evidence, target definition and schema. Select the statistical model yourself. The target analysis *classes* are declared, but reserved coefficients, directions, confidence intervals and clinical findings are not provided. Use only delivered files and permitted tools. Do not inspect other masked views, prior target analyses or unapproved literature. Never infer that an absent relation is zero simply because no paper reports it.

Produce executable generation code and concise evidence-linked decisions. Give assumptions and their consequences, not private chain-of-thought. A statistical sampler is allowed; direct records are a separately designated route. No new language-model training is required.

Programs retain the existing `generate(n, seed, evidence, context="target")` interface. The Stage 1 controller implements and checks scenario manifests, equal maximum diagnostic allowances and a twenty-cohort total allocation. The older single-candidate runner is not the Stage 1 scenario controller. For completion, the established `complete(masked, targets, evidence, seed, m)` interface remains separate.

Only source-facing checks are available during construction: schema, units, person/time keys, supplied summaries/operators with their uncertainty, reproducibility and input-use probes. Source evidence from another population is evaluated in that source context; any target mapping is explicit. A failed source check can justify revision; a desired target finding cannot.

## Paired comparison

One fresh initial construction is frozen. Separate fresh revision contexts then receive identical copies of that initial artifact and the same allowed evidence/feedback. They do not receive the other branch's proposal. Branch A receives the ordinary policy below; branch B the proposed policy. Common bounds are one initial submission plus at most two revision rounds, the same numerical calibration allowance, and twenty final output cohorts total per branch. Record all intermediate candidates and failures; do not choose a result after opening the target.

### Ordinary policy

Improve your initial generator using the allowed evidence and source diagnostics. You may reconsider dependence, population mapping, measurement, missingness and model family. You may examine up to three candidate structures within the common budget. Explain the final model/scenario choice, evidence use, limitations and unresolved questions. A justified no-op or uncertain answer is allowed. Do not force agreement with a numerical or qualitative target result.

### Proposed policy

Review which joint relationships the available evidence constrains and which it leaves unresolved. For each unresolved relationship that could materially affect the declared analysis classes, identify a small, substantively motivated alternative structure. Retain at most three models compatible with the source checks, with the inclusion rule fixed before target evaluation. Do not manufacture scenarios merely to achieve the maximum count.

For each scenario, provide its assumption, evidence supporting or limiting it, executable model, source-check diagnostics and predicted *classes* of affected analyses. Explain why the scenarios differ scientifically, rather than being different random seeds of one covariance matrix. Report stability or sensitivity across the examined set, without claiming that it spans all possible models. Request missing evidence only when it could distinguish the alternatives; the main comparison uses a fixed packet, so unresolved requests are logged rather than silently answered with target data.

Allocate twenty output cohorts deterministically across retained scenarios: one model gets 20, two get 10/10, three get 7/7/6 in committed scenario order. Scenario frequencies are a budget allocation, not posterior model probabilities. Report each scenario separately. A combined average must not hide opposite conclusions.

## Required decision fields

- Run, initial-lineage and branch identifiers; model/version metadata or explicit unavailability.
- Evidence IDs with use/qualify/defer decisions, operator, population, measurement and provenance.
- Model components, associated evidence and source-to-target assumptions.
- Scenario IDs, inclusion/exclusion rationale, unresolved dependencies and fixed output allocation.
- Changes from the parent candidate, reason, expected consequences and any claimed invariants.
- Source check results and failure records, without reserved target scores.
- Intended uses, unvalidated uses and the next information request.

The deterministic controller checks the allocation, applies common seeds where meaningful, preserves all outputs and freezes artifacts. Independent reviewers inspect implementation and source applicability. The final evaluator alone loads the reserved reference analyses. Its conclusions are not sent back to either branch for this experiment.

## Execution gate

Before construction: case-level analysis/reference audit, input redaction and hash manifest, scenario interface tests, whole-cohort versus MI regime tests, and one toy smoke run. These are authorized implementation steps, not a new user permission gate. If an interface defect is found after freeze, retain the failed attempt and create a separately versioned repair. Scale only after the bounded feasibility run described in the main plan.
