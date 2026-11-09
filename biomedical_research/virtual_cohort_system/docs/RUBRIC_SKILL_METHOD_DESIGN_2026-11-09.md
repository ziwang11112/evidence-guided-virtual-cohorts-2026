# A rubric and procedural skills for analyzable virtual cohorts

Date: 9 November 2026. Experimental design, not an adopted frozen method or a demonstrated performance improvement.

Update after the first pilot: the [two-case experiment is complete](../reports/rubric_case_pilot_2026-11-09/RESULTS.md). It used a shared minimal construction interface and did not instrument or enforce token matching; its actual protocol/results supersede the original allowances and not-yet-launched status below. The remaining sections retain the pre-pilot design. The user's subsequent direction is captured in [Agent autonomy](AGENT_AUTONOMY_DESIGN_2026-11-09.md): fixed sources, fixed rubrics and zero revisions are experiment conditions, not general system restrictions.

## Why this change fits the project

The user asks for virtual biomedical data that support a research need. A task-specific rubric can turn that need into explicit scientific criteria before construction. Procedural skills can help the author select the relevant calculation, evidence search or revision. This keeps the method centered on the generated data and its analytical use.

The existing skill already covers provenance, declared assumptions and revision records. Existing reviewers also inspect source meanings and model algebra. The useful addition must therefore affect an actual decision: which missing quantity to retrieve, which joint construction to use, which check to execute or which analysis needs a sensitivity qualification. Merely reformatting those existing records does not establish a new method.

## Roles of the components

| Component | Function | What it must not be confused with |
|---|---|---|
| Task rubric | Defines the analyses, relevant data properties, comparison scope and available verification | A desired biological answer or an arbitrary overall quality score |
| Procedural skill | Supplies reusable ways to obtain/check quantities and act on a failure | A fixed clinical relationship, hardcoded outcome parameter or new model training |
| Tools | Execute supported statistics and bind checks to actual artifacts | Scientific truth established by an LLM's rating |
| Scientific Agent | Chooses evidence, model family, parameters, output route and response to findings | A role required to revise even when no justified improvement exists |

One author can use both rubric and skill. Independent review remains optional and is not varied in the initial rubric experiment. Preserve whole-cohort generation, variable enrichment and missing-cell completion; either programs or directly generated tables remain valid routes under the task contract.

## What varies with the research request

For regression, the relevant checks include adjustment, scale, usable covariate variation, conditional effects and residual behavior. For joint prevalence, threshold definitions and joint mass matter. For longitudinal analysis, subject identity, visit structure and within-subject dependence matter. For power planning, stronger variance and design evidence is needed than for exploratory direction checks. These requests should not all inherit the same 20-item rubric.

The rubric must include every requested analysis. It may not add a requirement to discover a novel disease mechanism or force all generated relationships to match an unavailable raw dataset. If reference statistics are supplied for generation, use them as permitted calibration inputs and report that scope. Independent references remain evaluation inputs when the task says so.

Criteria specify the observable scientific property, its basis, the matching calculation and an interpretation rule. Where no justified numerical margin exists, retain continuous results and uncertainties. No summed score can make a large joint-dependence failure disappear behind schema/provenance points. Process completion and data usefulness are separate outcomes.

## How it can improve construction

Before generation, criteria expose which quantities are necessary. During construction, the Agent loads only relevant procedures. After a check, it distinguishes an implementation contradiction, absent operator, absent source information, incompatible source context or unverified transfer assumption. It then corrects, retrieves, explores an alternative, retains or restricts the applicable claim. A change to dependence or dispersion triggers rechecks of previously supported analyses that it could affect.

Useful diversity means adequately representing the individual or subgroup variation required by the intended use, and keeping substantively different plausible hypotheses separate when evidence does not identify one law. Extra noise, more rows and more random seeds do not automatically provide useful diversity. Scenario spread is not a calibrated posterior uncertainty interval unless a weighting model is justified.

## Project-local prototype

The [experimental skill](../experimental_skills/analysis-guided-cohort/SKILL.md) contains a short entry point and two selectively loaded references: [rubric construction](../experimental_skills/analysis-guided-cohort/references/rubric.md) and [procedures](../experimental_skills/analysis-guided-cohort/references/procedures.md). It is not installed into the global skill directory and has not replaced a frozen clinical method. The current harness is not silently changed to accept new artifacts or implement missing estimators.

The prototype first undergoes the [bounded fictional forward check](../reports/rubric_skill_prototype_2026-11-09/PROTOCOL.md). It tests whether a fresh Agent adapts to marginal versus adjusted requests and informative versus irrelevant supplements. No participant tables are sampled. Correct behavior would support usability of the instructions, not superiority or biomedical quality.

## Minimal data-generation experiment after prototype review

Use copies of the existing glycemia and lipid case packets for development. Fix the evidence and task information, allowed tools, output route, total token/tool budget and evaluation before construction. Use the same backbone and authoring-count allowance across three conditions:

1. Current workflow.
2. Current workflow plus the task rubric.
3. Current workflow plus the identical task rubric and the procedural skill.

The same independently reviewed task rubric must be used for conditions 2 and 3; an external evaluator uses the same predeclared scientific endpoints for all three. Match total allowance including rubric preparation and skill loading, and report actual usage; longer instructions are not free compute. A first development test should fix literature access rather than also changing retrieval power. If evidence acquisition is later varied, report it as a separate intervention.

This comparison estimates the value of supplied rubric guidance and added procedures; it does not evaluate autonomous rubric induction. Before running it, freeze each arm's exact prompt, installed skill version, review access and allowed artifacts, including how rubric preparation/review cost is assigned. These construction trials have not been launched.

Primary results concern the final virtual data: requested analyses, effect magnitudes and directions, relevant spread and joint relationships, new failures, preserved strengths and cost. Report model/author variation separately from repeated random draws. Rubric completion, annotation coverage and reviewer confidence are secondary. A small pilot with no clear gain leads to simplification, not a new component by default.

The old exposed cases can show developmental differences; they cannot become new confirmations. Keep their original versions and failures unchanged. Only adopt a method change after the data-use results justify it. Do not announce an improvement in this design document.

## Closely related work checked on 9 November 2026

- [AutoSciRub](https://arxiv.org/html/2608.31076v1), an August 2026 preprint, develops task-grounded executable rubrics before scientific research and uses criterion-level feedback for revision. It is a direct conceptual neighbor; task-adaptive rubric guidance itself is not a first claim for this project.
- [SkillCoach](https://arxiv.org/abs/2607.01874), a July 2026 preprint, evaluates skill use with process rubrics while retaining an external outcome verifier. Its distinction between process and outcome is relevant; its reported setting does not establish biomedical synthetic-data utility.
- [Anthropic's Agent Skills description](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) describes reusable instructions/resources with progressive loading. We use this packaging idea, not a claim that a SKILL.md file by itself supplies new statistical evidence.

Potential contribution remains the biomedical evidence-to-data workflow and measured analytical usefulness under sparse, heterogeneous information. A rubric/skill component becomes an empirical method contribution only if it changes generation decisions and improves the relevant final-data outcomes with a clearly scoped comparison.
