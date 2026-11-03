# Evidence-use declaration v1

`assess_evidence_use(manifest, evidence, model_spec, *, recipe_check_ids=None)` returns a JSON-compatible report or raises `ValueError`. It uses only the standard library, changes no inputs, and performs no filesystem, network, generator, source-statistic, or target-data access.

The caller must first validate/admit the existing evidence and model contracts, including task-specific restrictions. This narrow validator checks the reference-bearing metadata and model-provenance domains; it does not replace full evidence validation. `model_spec.parameters` is an object: `parameter_names` refers to its **top-level keys**, including names such as `shared` and `contexts`, never invented dotted paths. Assumptions are IDs from `model_spec.assumptions`.

Every field below is required; unknown fields are rejected. Strings must be nonempty except existing evidence-unit strings. Reference lists have no duplicates. Exactly one manifest item must exist for every admitted evidence item, including contextual/unit guidance and unused evidence. No numerical role or minimum number of constraints is forced.

| Object | Fields |
|---|---|
| Manifest | `schema_version: 1`, `evidence_sha256`, `items: []` |
| Item | `evidence_id`, `role`, `source_reference`, `context_id`, `check_ids: []`, `parameter_names: []`, `structure_names: []`, `code_references: []`, `assumption_ids: []`, `gaps: []`, `rationale`, `source_comparison` |
| Source reference | `source_id`, `source_sha256`, `item_sha256` |
| Code reference | `path`, `symbol` |
| Gap | `id`, `dimension`, `description`, `assumption_ids: []` |

`canonical_json_sha256(value)` hashes UTF-8 JSON produced with sorted keys, compact separators, `ensure_ascii=False`, and no nonfinite numbers. `evidence_sha256` binds the complete supplied evidence document; `source_sha256` binds the full matching object in `evidence.sources`; `item_sha256` binds the full matching object in `evidence.items`. Thus population, measurement, cohorts, artifact declarations, selection, statistic, reported value, units, uncertainty, adjustment, and locator remain bound without duplication. **These are canonical metadata hashes, not raw frozen-file hashes.** The controller must bind and verify actual raw artifacts separately. Load serialized JSON using a duplicate-key-rejecting loader before this in-memory API; overwritten duplicate object keys cannot be recovered here.

| Role | Rules |
|---|---|
| `numerical_constraint` | Numerical evidence estimate, nonempty `context_id`, `check_ids`, and `code_references`; at least one parameter or structure reference. `source_comparison: "declared_strict"`; no declared gaps or assumptions. This is a submitted declaration, never a fidelity certificate. |
| `qualified_numerical_comparison` | Same numerical reference requirements; at least one assumption. `source_comparison: "qualified"`; unresolved gaps remain visible. Strict replay claims are rejected. |
| `qualitative_context` | `source_comparison: "not_applicable"`; empty `check_ids`. Parameter/code/structure references may explain an influence. |
| `unused` | `source_comparison: "not_applicable"`; empty check, parameter, structure, and code references. The rationale explains omission/incompatibility. |

Nonnumerical records may use `context_id: null`. Each record independently names its relevant parameters, source metadata, and code; a numerical structure-only use may have empty `parameter_names`. Every `structure_names` entry must match a `symbol` in that same record's `code_references`. Paths/symbols and contexts are declarations: they are not opened, executed, or independently resolved. A code reference alone does not establish influence or dependency.

`check_ids` names executable recipe checks. They must be unique within and across item records. Optional `recipe_check_ids` is a duplicate-free **list** from the actual recipe; when supplied it verifies membership only. The controller must still bind each check to its actual evidence ID, operator, active source context, frozen execution, and authenticated feedback.

Gap IDs are unique per item; gap assumptions must also occur in that item's `assumption_ids`. Dimensions are `estimand`, `population`, `measurement`, `selection`, `conditioning`, `adjustment`, `scale`, `joint_distribution`, `interaction`, `uncertainty`, or `other`. Assumption/gap completeness and scientific truth cannot be inferred from declarations.

The report sets `declaration_valid: true`, `scope: "declarations_and_references_only"`, `executed_uptake: "not_verified"`, and `source_fidelity: "not_verified"`. Its separate `verification_needed` list retains artifact/provenance verification, operator/evidence binding, context and measurement review, code dependency review, and authenticated source execution. Numerical counts or matching hashes never turn this declaration report into proof of execution, faithful source extraction, transport, or scientific validity.
