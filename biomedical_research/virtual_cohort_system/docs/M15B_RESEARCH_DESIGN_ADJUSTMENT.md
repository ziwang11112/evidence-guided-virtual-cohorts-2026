# M15-B: literature-enabled generation for scientific analysis

30 October 2026. Active design adjustment following the user's clarification. **Status: design and reusable builder instructions prepared; case admission, literature collection and a new biomedical run are not yet completed.** This document supersedes the no-retrieval policy of M15-A for future tasks only. Historical inputs, candidates, evaluations and archives remain unchanged.

## Research question and intended output

Can an Agent use published evidence and available observations to construct more complete virtual biomedical data that support useful subsequent analyses?

The output is a usable table plus its evidence, assumptions and construction record. The table may contain more fictional people or more indicators than any single source. No requirement says that each generated cell must have appeared in a paper. The scientific requirement concerns the supported population, measurement definitions, relationships, variation and analytical uses. Actual empirical validation is specific to the tested uses and populations.

An ordinary capable scientific Agent is a valid implementation. Direct literal output remains the next route of interest. An Agent-authored program remains available as a separately identified route; direct output must not silently become programmatic sampling. Multi-Agent collaboration, a new loss and training are not prerequisites or current claims.

## Decisions changed by this review

| Earlier M15-A choice | Future design |
|---|---|
| Only a screened one-paper marginal excerpt; retrieval forbidden | Agent identifies evidence gaps, searches primary literature, reads permitted full texts/supplements, and selects applicable evidence. |
| Four source SDs intentionally withheld | Useful published SDs and relationships may be inputs. Once exposed they are construction evidence, not unseen validation. |
| Marginal discrepancy as the available numerical feedback | Check source relationships, spread, subgroup quantities and distributions where the original operators and source context can be represented. Retain unsupported or noncomputable checks explicitly. |
| Positive pairing invented from marginal information | Agent may choose dependence, but records its actual evidential basis or assumption; no sign, slope, correlation, symmetry or tail law is dictated by the controller. |
| Small table as an interface demonstration | Select an analytical use and a measured reference before generation; freeze one release and reuse it across the scheduled analyses. |
| Source matching presented as the main measured result | Source fidelity, target transfer and uncalibrated analytical reuse are reported separately. None requires exact patient-level reconstruction. |

M15-A remains useful evidence that direct submission works and that close marginal matching can coexist with unsupported joint structure. Its limited information contract does not establish failure of a literature-enabled Agent.

## Three supported purposes, separate task contracts

| Purpose | What can grow | What must stay fixed | Validation target |
|---|---|---|---|
| Whole-cohort generation | Number of fictional people and declared variables | Population/measurement definition and frozen generation specification | Population and analysis properties in a compatible measured reference. |
| Unmeasured-variable enrichment | Declared generated indicator columns | Existing people, identifiers, rows and observed values | Hide measured outcomes from construction, then compare analyses after freeze. |
| Missing-cell completion | Values in the declared missing mask | All originally observed cells | Masking experiment with a stated missingness mechanism; later real missingness may differ. |

Ten source summaries, ten source participants and ten variables are different information conditions. Generating 100 fictional rows from any of them is possible as a construction task; it does not multiply independent biological evidence. Added indicators may be supported by different studies, provided their joint use and transfer assumptions are explicit. A model-only indicator without a measured comparator remains an assumption-dependent extension rather than a validated biomarker.

Do not mix extra fictional rows into an enrichment task whose contract preserves actual participants. Use a separate whole-cohort task for population-size expansion. Do not treat finite direct-table outputs as iid samples from a known stochastic law. Repeated direct submissions and program residual draws have different interpretations and should be recorded separately.

## Minimal Agent workflow

1. Read the target population, permitted variables, generation mode and intended analyses. Identify which information is missing: marginal distributions, conditional relationships, subgroup structure, measurement mapping, residual variation or transport assumptions.
2. Search for relevant original studies and obtain the actual tables/methods where possible. Record queries, retrieved versions, inspected locators and source overlap. Search metadata is not proof that a full paper was read.
3. Create an evidence map. For each adopted result retain the original value, statistic type, units/transform, population, selection, adjustment set, uncertainty and locator. Record conversions separately. Different papers need not contain every variable.
4. Choose and disclose a construction. Trace important features to compatible evidence, explicit derivation or an assumption. Unsupported correlations are not implicitly zero. Conflicts prompt examination of study conditions, not outcome-driven deletion of inconvenient evidence.
5. Submit the initial table or program and record its provenance. For the direct route, literal values are authored by the Agent; the controller only validates and computes checks. Statistical tools may report diagnostics; their calculations do not populate row values on this route.
6. Review allowed source feedback. The Agent may retrieve further evidence, correct extraction, directly revise the table, revise a program in its own route, retain or stop. A revision records what evidence prompted it and which other analyses could be affected. All versions and failures remain.
7. Freeze the release. The evaluator runs the same prespecified analysis definitions on generated and measured reference data. No target-outcome feedback is used to revise that release.

The reusable [builder prompt](templates/M15B_BUILDER_PROMPT.md) applies these decisions. It is a prompt template, not evidence that an Agent has already run. The controller supplies a concrete valid task bundle and permitted adapters before launch.

Use the existing `analysis_evidence.json` sidecar for analytical uses, evidence links, context differences and proposed gap searches; do not build a second competing analysis schema. The additional exposure template records what was accessible, which is different from the Agent's selected evidence.

## Evidence access and exposure accounting

All relevant statistics in an admitted source can be used, including SDs, quantiles, regression results and subgroup findings. Their inclusion is not a scientific problem. The problem would be calling their reproduction an independent test.

Record two things separately: **exposure** (what the builder could read in returned artifacts) and **use** (which items it says informed construction or checking). Conservatively treat all returned source content as potentially exposed. Do not label a result unseen just because it was absent from the initial prompt or omitted from the evidence JSON. No claim of protection against prior model training is possible.

The analyst/controller selects a reserved reference using metadata and exposure history, without choosing it from favorable outcomes. Exclusions concern the designated validation participants/studies. They are not a universal ban on an entire public database across every future project. For the old exposed M13-B target, the existing prohibition on reuse as independent confirmation remains in force.

Current alias screening is conservative and may reject an independent paper because the excluded cohort appears in its references. It is not proof of independence. Log the rejection and request a controller provenance review if the source is scientifically important; do not bypass the screen or silently narrow exclusions. An authorized local review does not require a new user approval at every step.

If relevant target answers are accidentally exposed, retain that fact. Classify those analyses as development/source-informed, or designate a genuinely new confirmation unit before further construction. Do not relabel exposed analyses as unseen after the fact. The broader experiment may continue as development even when a particular independence claim is lost.

## Evaluation centered on usefulness

The first admitted case should have a real question and a measured reference for at least one added/generated biomarker. Start with one primary relation, one reuse analysis not directly calibrated and one preservation check that matters to those analyses. Examples include an adjusted association, an age or sex subgroup relation, a nonlinear contrast, or a threshold prevalence; the case determines which are meaningful. Public evidence may mention a broad direction without supplying the exact target result. Record that distinction instead of requiring that all useful scientific knowledge be absent.

For every analysis define the population, unit, transform, adjustment, estimator and comparison rule before reference outcomes are opened. Report compatible effect sizes, direction and relevant shape or subgroup behavior. Reference uncertainty is part of interpretation; an imprecise real estimate can make the outcome inconclusive. A same-sign estimate alone and an input-matching score alone do not establish useful accuracy.

Use scientifically justified magnitude/shape tolerances where possible, with their rationale fixed in advance. Otherwise report descriptive discrepancies and explicitly avoid declaring equivalence from a convenient retrospective cutoff. Do not use synthetic-row count as the empirical sample size in an uncertainty or power claim. Confidence in a target conclusion must reflect source, construction and transport limitations, not just a small standard error inside the fictional table.

No universal requirement to beat an ordinary Agent is imposed. A feasibility claim requires credible generation and analytical validation. A later claim that evidence retrieval or revision improves results requires a suitable matched comparison, such as the frozen initial versus final versions under the declared feedback schedule, with no selection on target performance. Expansion to additional cases is for scope/robustness, not collecting only successful examples.

Source reproduction remains useful even if no independent target is available, but the deliverable must then say source-consistent and assumption-dependent. It cannot be advertised as validated replacement for real measurements or as demonstrated savings in patient recruitment.

## Concrete next unit and bounded work

The next unit is **case admission and evidence planning**, followed by generation only once the case and evaluation contract are concrete. Do not reuse M15-A's known SDs as a new hidden test or reopen body-fat tuning. Urate may be retained if compatible evidence and a usable reference justify it; neither urate nor a new disease is mandatory.

Admission must answer:

- What scientific analysis becomes possible through generating or adding the indicator?
- Is the public reference actually obtainable with its required variables, units, selection and design information?
- Do external studies constrain a relevant joint/conditional relation and variation, rather than only unrelated marginal means?
- Can study differences be represented with available variables or a stated, examinable integration assumption?
- Which reference information has already been exposed, and which comparisons remain independent?
- Which parts remain uncertain, and is a small sensitivity construction more honest than one unqualified table?

Working budget for the first complete case: 24 adapter query attempts and 12 artifact downloads across construction and revision, with at most eight primary full texts deeply extracted. These are engineering caps, not evidence sufficiency criteria; they become binding only in the concrete task. Supplement and metadata requests count according to the adapter. Use one initial candidate and at most two source-feedback revisions, with explicit retention allowed. Fix row count, generated columns, repetition schedule and analysis rules based on the admitted use before generation. Do not reset the total budget when a new task is needed for a documented schema change.

These parent-level working caps reconcile the smaller illustrative budgets in the independent reviews: retrieval can consume queries for metadata and downloads for supplements, so eight papers are not eight total requests. Admission searches also enter the case usage record. The adapter enforces a single initialized bundle's budget; carrying totals across planning or a declared new task is currently controller bookkeeping, not an implemented global cross-task limiter.

If compatible relation evidence or an evaluable public reference cannot be found within the bounded admission work, record the reason before selecting a different case. Do not produce another marginal-only table and call it the full framework test. If target results fail after freeze, preserve that failure and use it only as development information for a separately designed next test.

## Implementation changes and limits

The current harness already supports `published_evidence`, task-bound literature access, registered evidence, direct rows, enrichment/completion preservation, source checks and immutable versions. M15-A disabled retrieval through its allowed-tool list, zero budgets and prompt. No core engine change is required merely to enable these existing capabilities in a new bundle.

The concrete new task must allow `literature.search`, `literature.fetch`, `literature.list-supplements` and `literature.fetch-supplement`, with nonzero source budgets. Initialization binds exact task bytes and location. Output columns and row count cannot silently change afterward. Agent-proposed additional indicators therefore belong in admission/planning before binding; a later expansion requires a separately declared task carrying prior exposure and usage records.

The existing gateway handles its documented Europe PMC/PMC article and supported supplement paths; it is not a general PDF reader. A needed PDF-only source is an access limitation requiring an explicit controller-assisted acquisition/provenance path, not proof that the evidence does not exist. Such assistance must be recorded and must not be described as already automated. Neither the gateway nor prompt provides OS isolation of the builder's general tools.

For direct rows, the existing source-check operators can inspect the submitted table, but execution-backed source replay is currently restricted to enrichment programs. A target-shaped table cannot be compared indiscriminately against every source population. Where a different source context is needed, either provide a separately declared Agent-authored source-context table and disclose the unverified shared-construction assumption, use an appropriate subset/operator, or report that quantitative check as unavailable. Such a check must never be labeled verified program replay. Case admission should prefer a few interpretable source checks over pretending every source statistic applies to one target table.

Exposure and analytical-use records below are **documentary templates**, not new core schemas or automated validators. Current source registration records bytes and provenance; it does not automatically certify cohort independence, scientific suitability or every content exposure. The controller and independent reviewer must check those claims. No new training, HPC, paid API, full framework rewrite or recurring automation is part of this adjustment.

See [interface review](M15B_INTERFACE_REVIEW.md) and [scientific review](M15B_SCIENTIFIC_REVIEW.md). Completion of this document means the next design has been corrected; it does not mean a new case, virtual cohort, performance result or publication claim has been obtained.
