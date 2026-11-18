# Minimal integration recommendation

9 November 2026. Read-only interface/design review. No generated rows, new target payload or prior numerical target comparison was inspected. This recommendation does not prescribe a scientific effect, dependence parameter or repair algorithm.

## Recommended scope

Keep `adaptive_session_v2.py` and all old frozen modules unchanged. Add one host-reviewed analysis adapter, provisionally `analysis_use_v1`, and two small declaration files. Use the existing analysis-evidence validator instead of inventing a numerical evidence-quality score. The immediate unit should be a **controlled coherence-repair development exercise**, with a fixed source-only baseline and at most one optional Agent-selected repair. Compare coherence, requested generated analyses and source-feedback changes. Do not read or compare real-target estimates in this unit.

The repeated disclosed lipid case is adequate to exercise this integration, detect specified contradictions and show collateral changes after repair. It cannot establish new clinical accuracy or independent validation. Even perfect rule satisfaction establishes only the checked properties. Source matches and a fresh author/new seeds do not make the previously disclosed case an untouched clinical test.

## Actual reusable interfaces

- V2 accepts `analysis_adapters` entries with `path`, `function`, `sha256`, and optional `dependencies`. The host function is `analyze(output_path, task_path, request_path) -> dict`. It is trusted host code, not an arbitrary author program or a sandbox. Its finite JSON result is limited to 2 MiB.
- V2 completion already requires every configured analysis adapter for every successful execution in every submitted stage. With the existing generated-analysis adapter plus one new adapter, a maximum of two candidates and three seeds requires allowance for 12 analyses. Two full stages consume at least 27 actions before retrieval and extra preflights (two submissions, six executions, six dual-feedback actions, 12 analyses, one finish).
- `analysis_evidence.validate_analysis_evidence(manifest, task, evidence, model_spec)` and `summarize_analysis_evidence(...)` validate existing declared links, assumptions and gaps. Lifecycle validates an optional `analysis_evidence.json` and freezing commits its bytes. The present validator does **not** know every requested analysis, verify full semantic equivalence, or infer generator dependencies. The new adapter must enforce the exact requested ID set and exact canonical estimand templates from the host contract.
- Existing `analysis_evidence` retrieval actions permit the literature actions and `none`, not `web.fetch`. Keep that legacy enum unchanged. A sidecar action is a plan; actual v2 web freedom remains available separately and is documented in executed actions. Do not falsely encode an executed web fetch as a completed sidecar plan.
- `evidence_use_v1.validate_evidence_use(manifest, artifact_bytes, required_analysis_ids=...)` can bind declared parameter uses and actual specification changes, but it is not automatically invoked and currently requires `generator.py`. It is optional for this small unit, not a prerequisite that would silently exclude direct-row submissions. It cannot prove a generator actually uses the declared parameter.
- `self_consistency.py` supports enrichment with observed predictors only. Do not re-label it a whole-cohort cross-variable checker. `conditional_feedback_v1.py` is a specialized approved correlation-interpretation interface, not a general coherence engine.

## Small concrete contract

Before session creation, add `input/use_contract.json` to the fresh bundle; v2 binds the entire `input/` namespace. Its version-1 shape can be:

```text
schema_version: 1
analyses: [{id, estimand: <the existing exact analysis_evidence estimand schema>}]
coherence_rules: [{
  id,
  operator: {kind: "order", left, right, unit, tolerance}
            OR {kind: "sum", total, components, unit, tolerance},
  measurement_interpretation,
  basis: {kind: "source" | "algebraic" | "task", reference, locator}
}]
```

The host contract comes from the user's analysis request and reviewed measurement/task definitions, never from a desired target answer. Rule directions and any non-numerical tolerance interpretation must be justified before running the comparison. A purported physical inequality may depend on assay, timing or measurement error; an educational reference interval is not a universal subject-level restriction. For a source basis, resolve `reference` to an admitted source identity/artifact where possible. Free-text `reference`/`locator` alone is **declared basis**, not verified extraction or quantitative evidence support.

Require each candidate to contain the existing `analysis_evidence.json`, covering exactly the contract analyses, plus `coherence_v1.json`:

```text
schema_version: 1
use_contract_sha256: <exact byte hash>
rules: [{id, applicability: "applicable" | "unresolved" | "not_applicable",
         reason, assumption_ids: [existing model-spec assumption IDs]}]
```

The candidate must include every contract rule exactly once. Optional extensions should be omitted from this first unit unless they answer a concrete analysis need. Preserve the author origin of applicability judgments. Neither `applicable` nor `not_applicable` is an engine-certified scientific conclusion; the latter is not a way to obtain an automatic pass. Retain unresolved measurement assumptions and their consequences in the final decision.

Use one shared pure declaration preflight from the host driver and the new adapter. Run it before submit so malformed declarations can be corrected while unfrozen. No v2 engine change is needed. An absent or scientifically unresolved declaration discovered during analysis should return an explicit incomplete/unassessed report, not invent coverage or silently skip the rule. Reserve hard exceptions for integrity/path/hash violations; a late ordinary scientific finding should not become an infrastructure halt that prevents the permitted revision. A successful analysis action means its report was produced, not that the scientific criteria passed.

## Execution and report meaning

The adapter can derive the bundle from `task_path.parent`, check the supplied output is exactly under `executions/<run_id>/output/generated.csv`, verify that execution, and resolve the frozen candidate from its receipt. Verify the candidate and load only task/request, pinned use contract, candidate declarations/evidence/specification and this verified generated output. Do not search arbitrary sibling work folders or import the generator. Bind task, request, use-contract, candidate-freeze, sidecar, execution and output hashes in the report; pin every host-owned transitive adapter dependency in session configuration. This prevents a report from quietly using another candidate's declaration.

Keep distinct report tracks:

1. **Calculation:** operator and units; total, eligible, evaluated, unknown and violating row counts; violation fraction with its denominator; aggregate violation magnitude; explicit exclusions and tolerance. Zero evaluated rows is unavailable, never a pass. Do not publish IDs or offending individual rows.
2. **Rule basis and applicability:** admitted-source reference linkage when checked, declared interpretation and assumptions, and `applicable`/`unresolved`/`not_applicable` origin. Where arithmetic is computable but applicability is unresolved, report the arithmetic and withhold a scientific pass/fail claim.
3. **Use-specific evidence coverage:** exact requested-estimand coverage, linked evidence/assumption IDs, declared context differences, gaps and shared declared cohorts. The existing validator can detect explicit kind/unit-label/adjustment contradictions; population and measurement correspondence remain declared unless separately reviewed.
4. **Preservation:** baseline-versus-final differences in every requested generated analysis and diagnostic, all seeds and stages retained. Show unfavorable movements and unavailable values. Without a justified prespecified margin, report changes descriptively rather than awarding “preserved” or “improved”. Existing strict/descriptive source feedback remains a separate result and is not upgraded by coherence.

The residual-lipid analysis needs its exact residualization definition in the pinned estimand. A source's raw Pearson correlation is not direct evidence for residual Pearson correlation simply because both have unit `1`. Likewise, exposure/outcome direction, adjustment, eligibility and scale must not be reduced to matching analysis IDs or an unordered variable set. No summed quality/confidence score should combine evidence counts, structural compliance and scientific validity.

## Minimal failure tests

- Reject omitted, added or duplicate analysis IDs; detect an altered outcome, exposure, adjustment, scale, unit or estimator under an unchanged ID.
- Reject missing/duplicate coherence rules, unknown columns, incompatible task units, negative/nonfinite tolerances, `left == right`, duplicated sum components, or the total included among its own components.
- Preserve missing/nonfinite/unknown counts, empty eligible sets and all violations. Do not let exclusion filters, inapplicability declarations or a permissive tolerance manufacture success.
- Reject mismatched contract/candidate/execution hashes and paths; verify that a report cannot bind one candidate's rules to another candidate's output.
- Distinguish numeric rule violation, unresolved measurement applicability, structurally invalid evidence declarations and absent source information. Test an assumption-only interpretation without promoting it to evidence-backed validity.
- Verify a rule-satisfying fixture with deliberately changed requested associations is still reported as changed. Also retain a computation failure and a justified no-op; neither should disappear from the final record.

## Bounded exercise and claims

Copy only the reviewed source-only baseline generator/specification and required source artifacts. Preserve their exact baseline bytes, documenting sidecars as new annotations. Do not inherit prior target-result files or decisions containing such comparisons. Use the same new fixed seeds in baseline and repaired stages so generated changes can be described on paired draws. Let the Agent choose whether and how to repair from the declared rules, source evidence and generated-only checks. If a developer specifies the actual transformation, call it developer-directed repair rather than evidence of autonomous scientific selection.

Freeze both stages, retain failed attempts, all three requested analyses, all diagnostics and both feedback layers; seal final selection before reporting. Bind the actual rubric report into any revision's check artifacts. Use a new postclosure report that never opens the historical real-reference file. The result may demonstrate removal of a specified incoherence and quantify its cost to other generated properties. It does not show improved clinical usefulness, unbiased effects, calibrated uncertainty or the causal efficacy of a rubric component. Clinical usefulness remains unassessed in this unit.
