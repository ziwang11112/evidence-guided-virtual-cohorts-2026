# Analysis-use and coherence diagnostics v1

This additive adapter runs through the existing `adaptive_session_v2` analysis action. It introduces no controller, generator, target access or clinical coefficients. It links two distinct reports to an actual execution: complete declarations for the requested uses, and aggregate checks of required cross-variable relations. A structural check does not establish scientific support.

The host freezes `input/use_contract.json` before the author session. V2 loads adapter files outside package context, so point its adapter `path` at a small bridge containing `from cohort_harness.analysis_use_v1 import analyze`, with `function: analyze`. Do not point directly at the package module, whose relative imports require package context. Pin the bridge bytes and list `analysis_use_v1.py`, `analysis_evidence.py`, the use contract and all transitive source dependencies not already covered by engine commitments as dependencies. The author supplies `analysis_evidence.json` and `coherence_v1.json` with each candidate. Candidate freezing binds both. Keep scientific requested uses stable while allowing the author to search, change model structure, investigate a declared assumption, retain or stop.

## Host use contract

```json
{
  "schema_version": 1,
  "analyses": [
    {"id": "requested_id", "estimand": {"description": "...", "kind": "reported_other", "statistic_name": "...", "outcome": "y", "exposures": [], "conditioning": [], "adjustment": [], "scale": "...", "unit": "...", "population": "...", "measurement": "...", "selection": "..."}}
  ],
  "coherence_rules": [
    {
      "id": "component_order",
      "operator": {"kind": "order", "left": "component", "right": "total", "unit": "same_unit", "tolerance": 0},
      "measurement_interpretation": "Underlying quantities sharing the specified definition and specimen; separate assay noise is not assumed away.",
      "basis": {"kind": "algebraic", "reference": "Reviewed definition", "locator": "Exact section or derivation"}
    }
  ]
}
```

This example is schematic and must use actual task variables. Estimands follow the existing `analysis_evidence` schema. Exact IDs and normalized estimands are required: dictionary key order and order of the set-like exposure/conditioning/adjustment lists do not matter; definitions, unit, measurement, population and scale cannot silently change. Host review must check that this structured contract captures the user's request; the adapter does not translate natural-language requests.

`order` checks `left <= right + tolerance`. `sum` uses `{"kind":"sum","total":"total","components":["part_a","part_b"],"unit":"same_unit","tolerance":0}` and checks `abs(total - sum(components)) <= tolerance`. Tolerance is finite, nonnegative and absolute in the explicit unit. No implicit conversion or tolerance selection occurs. Variables must be distinct numeric nonidentifiers with identical task unit labels. Sum components are unique and cannot include the total. Positivity and single-column bounds remain in the existing task contract.

`basis.kind` is `source`, `algebraic` or `task`. Reference and locator are transparent host declarations, **not authenticated source support**. A source-based rule needs separate source review. There are no built-in cholesterol, BMI or other clinical-variable rules. A latent component identity and separately measured noisy values may require different interpretations; a device range is not automatically a biological bound.

## Candidate declarations

`analysis_evidence.json` reuses the existing structural validator and summary. All and only host-requested IDs must be present with matching estimands. Its evidence, assumptions, uncertainty gaps, overlapping-cohort declarations and proposed retrieval actions remain author judgments. A marginal relationship cannot automatically become an adjusted or residual relationship. This adapter does not inspect generator code to infer unreported dependencies.

The existing sidecar's proposed-tool vocabulary is unchanged: literature search/fetch/supplement actions or `none`. It is a declaration of proposed actions, not an executed trace. The separate session still permits the actual `web_evidence` action; this adapter does not disable it or claim that proposed searches occurred. The actual session record remains authoritative for executed retrieval.

`coherence_v1.json` contains every required rule ID exactly once:

```json
{
  "schema_version": 1,
  "use_contract_sha256": "SHA256_OF_EXACT_USE_CONTRACT_BYTES",
  "rules": [
    {"id": "component_order", "applicability": "applicable", "reason": "Why the stipulated relation applies to this candidate's modeled quantities.", "assumption_ids": []}
  ]
}
```

Applicability may instead be `unresolved` or `not_applicable`, with a reason. Assumption IDs must exist in the model specification. These declarations cannot remove the rule or change its operator. Numerical counts are still calculated when possible; unresolved/not-applicable declarations never become a consistency pass. Review any disagreement between required measurement scope and the author's interpretation.

## API, results and failure handling

`preflight(bundle, candidate)` reads declarations only and returns `ready` or `validation_error`. CLI:

```text
python -m cohort_harness.analysis_use_v1 --bundle BUNDLE --candidate initial
```

`analyze(output_path, task_path, request_path)` is the host entry point. Configure it as an additional v2 analysis adapter. The unchanged controller requires each configured analysis on every successful scheduled run before normal completion; budget its additional action and analysis count. The adapter verifies canonical paths, the successful execution receipt, frozen candidate and output, then reports `computed` or a structured author-plan `validation_error`. Configuration/path/provenance failures raise and halt. Existing lifecycle validation already rejects an invalid supplied `analysis_evidence.json` before freeze; a missing sidecar or malformed new coherence plan is reported if a legacy-compatible candidate reaches this analysis without it. The coordinator must inspect nested status; a controller action that returns the diagnostic is not a scientific pass.

Every rule reports total rows, evaluated rows, unknown rows, missing values, nonfinite inputs, arithmetic overflow, violations, satisfying rows, evaluated-row violation fraction and maximum raw discrepancy. Missing rows take precedence over other nonfinite values, so input-failure counts are disjoint. Arithmetic-nonfinite rows join the unknown count. `max_violation` is the maximum positive raw `left-right` for order, or maximum absolute sum residual, before subtracting tolerance; it is null with no evaluated rows. No rows are filtered, clipped, repaired or returned by this adapter.

`observed_consistent` requires declared applicability and all rows numerically evaluable with no violation. A numerical violation with applicable scope yields `contradicted`; missing/nonfinite rows prevent a full consistency assessment. A numerical result is conditional on the declared measurement interpretation. Evidence assessments remain `submitter_declaration`, source-population replay is false, and no global biomedical-quality score is produced.

Reports bind task, request, use contract, evidence, model specification, both sidecars, execution receipt, freeze and generated table hashes. They contain aggregate results only. Hashes are reproducibility commitments, not source authentication or protection against a host rewriting all records. The adapter is trusted host code, not a sandbox; only the existing generation worker provides process isolation.

## Validation scope

The tests use invented direct tables through actual candidate freeze and execution validation, plus separate invented arrays for missing/nonfinite arithmetic. They cover exact use/rule coverage, source-declaration scope, unit and tolerance rejection, sum/order boundaries, ambiguous applicability, missing plans, no target reads and output/freeze tampering. They do not validate a biomedical rule, a clinical population or a model's performance.
