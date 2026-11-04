# Independent protocol review

Reviewed on 2026-11-04. Scope: the new evidence acquisition unit only. This review performed no network access, source search, candidate construction, generation, fitting, source replay or clinical-row read, and did not modify the bundle. Old work folders, results, manuscript content and candidate contents were not read.

## Verdict

Proceed with retrieval and independent source audit under the explicit retrieval-only instructions. No forced scientific answer or preselected bibliography was found. Two procedural inconsistencies require the interpretations below; neither supplies scientific evidence or permits expanded scope. This is a protocol review, not source admission or scientific validation.

## Materials inspected

- Bundle `request.json`, `task.json`, `RESEARCH_RULES.json`, `AUTHOR_TASK.md`, `adapters.json`, and `intake_receipt.json`.
- This work unit's `PLAN.json`.
- Interface implementations `cohort_harness/request_intake.py` and `cohort_harness/literature.py`.
- The project-supplied `skills/evidence-cohort-generation/SKILL.md` and its `references/harness-interface.md`, for information-boundary and provenance requirements only. Their candidate and execution instructions are outside this unit.
- Current gateway configuration and state for read-only budget semantics/context. No article or search-result text was reviewed at this protocol stage.

## Question and permitted scientific choices

The specified analysis is `hba1c ~ 1 + bmi + glucose + age + female`, with interest in the BMI association conditional on glucose, age and sex. It specifies a question, not a coefficient, sign, significance threshold, probability family, dependence structure or desired result. The empty source-seed list is consistent with gap-directed search. The five-study limit is a resource ceiling, not a requirement to find five supportive studies.

The future population is community-dwelling Chinese adults aged 35–74, both sexes, around 2009, with complete measurements and no diabetes/treatment exclusions. This is explicitly a selected analytical population rather than a nationally representative sample. No diabetes prevalence, treatment mix, sex proportion, BMI distribution, or fasting-contamination rate is supplied. These must remain unknown unless supported or later declared as assumptions; none can be inferred from the task label.

Units agree across the task materials: HbA1c percent, BMI kg/m², age years, female indicator 0/1, central serum glucose mmol/L. Studies reporting plasma glucose, verified fasting glucose, HbA1c mmol/mol, transformed variables, standardized effects, or a different adjustment set need explicit applicability and transformation notes. A marginal correlation, odds ratio, adjusted coefficient and mean difference are not substitutes. The model question is associational and does not by itself justify causal interpretation.

The task's `n_rows=3000`, generated column roles, integer age and nonnegative bounds belong to a future output contract. They are not source-study sample sizes or estimated biological parameters. They do not authorize generating those rows now.

## Scope inconsistency and controlling interpretation

`request.json` purpose, `RESEARCH_RULES.json`, `PLAN.json` and the dispatch limit this unit to evidence acquisition and audit. However, the generic `AUTHOR_TASK.md` also says to submit candidate artifacts, use whole-cohort source feedback and return a data artifact or executable generator. Inspection of `request_intake.py` shows these are generic packet-template clauses rather than a task-specific scientific choice.

For this unit, those candidate, parameter-choice, source-feedback, replay and generator-delivery clauses are inapplicable. `adapters.json` lists possible interfaces; it does not establish authorization, execution, a created candidate or a validated runtime. Deliver only acquisition evidence, applicability decisions, gaps, actual audit results, accounting and stop reason. Source replay is not a prerequisite to admitting inspected original evidence, and no candidate or model specification should be constructed to enable it here.

## Exclusion and access boundaries

The task consistently excludes CHNS / China Health and Nutrition Survey numerical evidence. The explicit rules require recording source overlap, exclusions and incidental target exposure; they prohibit changing routes to evade a cohort-exclusion rejection. Gateway alias screening is conservative text screening, not proof that a source has no target-derived content. Independent scientific screening remains necessary, including overlapping cohorts and reviews that repeat excluded numerical material.

The allowed literature actions are search, fetch, list-supplements and fetch-supplement. The explicit task rules also allow web search/open of primary publishers, PubMed/PMC, official institutional author repositories and original supplements for availability gaps. No account, payment or access-control bypass is authorized. A web-rendered original can be inspected evidence, but it must remain visibly distinct from a gateway-approved and registry-admitted artifact. Do not manufacture a gateway approval or treat a saved hash as scientific admission.

## Budget semantics and enforcement gap

The applicable ceilings are 12 combined queries across routes, five seriously reviewed original studies, 20 web-page opens, 50 MiB newly saved bytes, 10 MiB per saved file, zero generated tables and zero new clinical reads. Count attempted access and failed or rejected retrievals as actually recorded; do not erase them or start another session to recover budget. Supplements and multiple versions do not create independent study confirmations.

The task schema separately sets `source_downloads=5`. `literature.py` binds that value to the fixed gateway's download-operation budget; it is not an implementation of the five-serious-studies rule. Retain both caps. A literature fetch may consume query budget through metadata lookup. Native gateway counters do not combine web-route queries or enforce the external study/open/byte limits. Use one shared ledger for acquisition plus audit; reviewers receive the remaining budget rather than a reset.

The gateway configuration permits a 16 MiB response, exceeding the external 10 MiB per-saved-file ceiling. It also does not enforce the 50 MiB total saved-byte ceiling. The tighter task limits are procedural: inspect available size metadata, avoid knowingly requesting an oversized file, and track actual saved lengths and any breach without deleting its record. No additional code enforcement was demonstrated. Count actual newly saved copies, including gateway artifacts and registered copies, when assessing total bytes; source text plus XML and manifests may create more than one file per study. This review does not authorize changing or resetting the bound gateway configuration. The mismatch is a documented limit of enforcement, not an extra approval gate for permitted small-source inspection; no actual byte-limit violation was established here.

A read-only snapshot during this review showed gateway usage of four queries and two downloads. Acquisition was ongoing, so these are neither final totals nor remaining-budget values. The acquisition ledger and final gateway state must settle the final accounting. This review itself consumed no search, open, download or serious-source-review allowance.

## Required source audit handoff

For each selected original, preserve URL, source version, artifact/hash where available, precise table/figure/text locator, population and selection, sample size, measurement and units, transforms, exact adjustment set, effect type, point estimate and uncertainty, source overlap, admission route, applicability and unresolved assumptions. Distinguish reported values, calculations and assumptions. Record inaccessible full text or supplements as gaps, without filling them from inference.

The independent source review will compare the acquisition ledger against the saved originals after handoff. It should retain conflicts, neutral findings, partial leads and unusable evidence, and should not require a favorable BMI coefficient or a complete parameterization. Stopping at a ceiling or at an unresolved evidence gap is a valid outcome. Protocol approval alone does not establish that any source supports the requested conditional relationship.

## Scope clarification received for source audit

The subsequently supplied `EVIDENCE_ASSIGNMENT.md` explicitly resolves the generic author-packet clauses in favor of evidence acquisition only, preserves the intake packet, separates gateway download operations from serious-study counts, and describes the tighter byte ceilings as procedural tracking. It also distinguishes unmetered browsing traffic from saved-byte accounting. These clarifications are consistent with this review and do not force scientific parameters, reset budgets or authorize a generator.
