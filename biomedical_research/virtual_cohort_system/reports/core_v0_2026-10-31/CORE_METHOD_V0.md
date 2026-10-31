# Core method v0: evidence-guided virtual data for scientific analyses

Status: proposed version for an implementation freeze. The accompanying manifest and independent closeout, not this heading, establish whether freeze prerequisites were completed. This document defines a procedure; it does not assert novel algorithms or biological accuracy.

The research object is a reusable virtual dataset produced from study-level evidence and a specified population, with optional real observations. Its intended use is subsequent scientific analysis. The entry regimes are complete-cohort generation with no individual inputs, enrichment of unmeasured variables, and missing-cell completion. Evidence and observed information differ across regimes, so their evaluations must remain separate.

## Inputs and outputs

Each case supplies a task contract: population and estimand; variable definitions, measurements and units; information regime and permitted observations; eligible literature and overlap exclusions; approximately three intended scientific analyses; execution, retrieval and revision budgets; and a separately held evaluation plan. Target measurements and evaluation answers are excluded from builder feedback. Published source results may be supplied, including relevant joint evidence; their use is disclosed rather than artificially prohibited.

Admitted source artifacts have stable locators and hashes. Evidence records retain population/selection, variable and measurement definitions, statistic type, adjustment set, reported value, uncertainty and shared-cohort identifiers. Parameters cite reported evidence, explicit derivations or named assumptions. A missing dependency is unknown, not automatically independent. Individual SD, standard error, uncertainty about population effects and variation between studies remain distinct.

The scientific Agent returns an evidence ledger, a model specification and assumptions, a program or direct table, a concise decision record, and actual check records. The implemented program interface is `generate(observed, spec, seed) -> DataFrame`; `observed=None` for complete-cohort generation. Output includes the frozen scientific artifacts, generated data, provenance, diagnostics, revision/retention decision and scoped analytical-use claims. Virtual measurements are possible values under evidence and assumptions, not recovered measurements of individual participants.

## Minimal procedure

1. **Admit and specify.** The coordinator/custodian checks source access, population and measurement compatibility, source/target overlap, information boundaries and budgets. The Agent may identify gaps and seek permitted literature through the fixed task session. Approval records come from the supplied intake, not the builder. Case selection must precede target-effect inspection.
2. **Construct.** The Agent chooses distributions, dependence structure, parameters and transfer assumptions. Every parameter has a recorded basis. The coordinator supplies the research request and execution controls, not coefficients selected to match an exposed target. A competent ordinary Agent is an eligible implementation.
3. **Preflight and freeze.** Validate task, evidence, specification, candidate and statistical recipe. Review the actual statistic, units, selection and adjustment set; schema acceptance alone cannot establish semantic equivalence. Freeze scientific bytes before execution. Keep inputs and previous candidates immutable.
4. **Execute and check sources.** The controller executes a frozen candidate using the existing isolated backend and evaluates the predeclared operators. Verify successful status as well as receipt integrity. Retain every discrepancy and non-computable statistic. Generated rows and source checks are not independent clinical evidence.
5. **Decide once within budget.** Give the Agent verified source feedback. It may re-extract, seek permitted evidence, revise, retain or stop. It must explain the issue addressed and remaining limitations without claiming unsupported uncertainty calibration. Copy and bind the authentic feedback into the next candidate. Do not force a numerical improvement or a change. Freeze the decision and any new candidate; retain the parent.
6. **Release and assess use.** Commit the prescribed output set before real-target disclosure. Run the same prespecified analysis code on the real reference and virtual releases. Report direction, relevant effect scale, uncertainty and diagnostics, including failures and unresolved questions. Reusing a released dataset does not permit endpoint-specific regeneration.

## What is actually implemented in v0

The core is existing `cohort_harness` contracts, lifecycle, isolated execution and statistical tools with external session orchestration. The session launches the scientific Agent; there is no standalone LLM service or Agent-wide filesystem sandbox. Exact model identifier, temperature and token cost are recorded only if exposed by the runtime. The present scientific author uses inherited session settings; unavailable metadata must remain unavailable.

The **reference integration profile** is program-based whole-cohort generation followed by verified identity-measurement feedback and one bounded retention/revision opportunity. This profile is the subject of the accompanying integration replay. Other contract modes and direct-row execution exist and have development records; this replay is not new validation of all those modes.

`whole_cohort_feedback` calculates source operators on a successful already generated whole-cohort output. It does not reconstruct each study population or transform measurements. A mismatch of source and generated populations must be an explicit approximation or an unavailable check; it must not silently become an exact calibration constraint. Existing `source_replay` executes the same frozen enrichment generator under builder-declared, frozen covariate-only source contexts; it does not reconstruct those covariates. General whole-cohort multi-study population replay is not implemented by this adapter. Case-specific source-context and target-evaluation adapters must be documented and bound before use.

Supported source operators currently include arithmetic mean, sample SD, proportion, Pearson and Spearman correlations, explicitly defined quantiles, and full-rank OLS coefficients. Survey-weighted estimation, arbitrary nonlinear effects, measurement conversion and calibrated transport uncertainty are not supplied by these operators. Unsupported statistics are retained as unavailable, not replaced by a convenient statistic. This version adds no statistical estimator or universal scalar loss.

## Control and interpretation rules

- Preflight the whole-cohort recipe explicitly: ordinary candidate validation/freezing does not currently validate its semantics. The integration uses the existing `_read_plan` validator plus independent operator review.
- Require the exact initial feedback bytes in the final candidate, with their original linkage verified. Merely supplying a correctly hashed arbitrary file is insufficient.
- A `retain` decision must preserve program and specification bytes. The reference replay also fixes evidence and recipe, preventing apparent improvement by dropping checks. Real extraction corrections require an explicit scientific revision and an unchanged record of prior checks.
- The controller separately fixes execution counts and seeds; the native task budget covers queries, downloads and revisions, not generator calls. Failed runs remain recorded; no host execution fallback, seed replacement or unrecorded optimizer trials are allowed.
- Individual residual variation, alternative model structures, uncertain source estimates and population transport require different accounting. More rows reduce simulation noise, not source uncertainty. Sensitivity scenarios are not confidence or credible intervals without a justified probability model.
- Hash commitments and procedural source restrictions support inspection; they are not externally attested timestamps, authorship certification or isolation of all Agent tools.

Dynamic variable extension from C5 is optional. Extra Agents, selectors, numerical calibration, model training and a user interface are optional implementations rather than core contributions. A one-Agent configuration is valid. Comparisons are required for specific superiority claims; a direct-analysis Agent is not a mandatory opponent for a data-generation feasibility claim.

## Freeze and next-case conditions

Bind this specification, actual role/task prompts, code, interfaces, dependency records and the bounded integration plan. Complete one real execution/feedback/decision chain and independent recomputation. A source-only artificial replay establishes implementation linkage, not publication readiness or scientific transfer.

Before any fresh real evaluation, separately freeze population/estimand, evidence and exposure register, source applicability, approximately three analyses, use-specific interpretation rules, reference uncertainty, row/seed/execution/query limits and failure handling. Default to zero-individual-input generation; choose enrichment only when justified by the use. Screen at most three candidate dataset families and six new primary studies for that case, without inspecting target effects to choose a favorable case. If no case qualifies, record the admission failure.

The manuscript can be drafted now with historical results explicitly labelled as development evidence. F1 is the method implementation freeze; F2 is real-case admission and prerelease evaluation design; R1 is the complete result and claim lock. A favorable result is not required to freeze a method, and an unsuccessful prospective case must not be replaced silently. C5 and this integration cannot stand in for F2 or R1.
