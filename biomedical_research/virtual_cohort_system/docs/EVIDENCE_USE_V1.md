# Optional evidence-use decision gate

`cohort_harness.evidence_use_v1.validate_evidence_use` checks whether an Agent's declared evidence-use decision is reflected in the actual submitted specification and check artifacts. It is a small optional controller API, separate from retrieval/action planning. Existing validators, freezing, replay and historical controllers are unchanged. The optional candidate sidecar is `evidence_use_v1.json`; its presence alone does not invoke this gate.

The gate takes exact artifact bytes supplied by the new controller. It does not read files, search, execute generators, inspect targets, choose parameters or assess scientific truth. No new evidence ledger or rationale ledger is created: evidence IDs, analysis links/comparisons/gaps, assumptions, provenance derivations and check records remain in their existing objects.

```python
from cohort_harness.evidence_use_v1 import validate_evidence_use

report = validate_evidence_use(
    manifest,                      # parsed evidence_use_v1.json
    artifacts,                     # {portable_bundle_path: exact_file_bytes}
    required_analysis_ids=request_analysis_ids,
)
```

The result is deterministic and the inputs are not modified. Invalid bindings or declarations raise `ContractError`. `contract: structurally_valid` never means scientific certification or improved generated data.

## Artifact bindings

The sidecar has exactly `schema_version: 1`, `bindings` and a nonempty `decisions` list. Each binding is `{ "path": "...", "sha256": "..." }`. Hashes are of exact file bytes, including whitespace. Paths are portable, forward-slash bundle-relative names; traversal and case aliases are rejected. JSON is parsed with duplicate-key and nonfinite-constant rejection after hashing.

Required binding roles are `task`, `evidence`, `model_spec`, `analysis_evidence`, `checks` and `generator`. The five candidate roles must name `evidence.json`, `model_spec.json`, `analysis_evidence.json`, `checks.json` and `generator.py` in the same candidate directory. The generator is opaque bytes, never parsed or executed by this gate.

For a new construction omit every baseline binding. For a revision provide all three roles: `baseline_evidence`, `baseline_model_spec`, `baseline_generator`, naming their respective files in a distinct baseline candidate directory. Both evidence/spec contracts are checked under the task. No historical candidate is modified or automatically upgraded.

Every existing `checks.json.artifacts` file must also be supplied in `artifacts`, resolved relative to the candidate directory; its own declared hash is verified. Metadata, generator files and `evidence_use_v1.json` cannot masquerade as auxiliary check results. The API reads no source-document bytes and does not check source admission; the normal candidate validation/freeze registry checks remain necessary.

## Decision entries

Each decision has exactly these fields:

```json
{
  "id": "use_source_relation",
  "analysis_id": "existing_requested_analysis_id",
  "evidence_ids": ["existing_linked_evidence_id"],
  "choice": "relationship",
  "parameter_paths": ["/parameters/existing_parameter_name"],
  "assumption_ids": ["existing_analysis_assumption_id"],
  "check_names": ["existing_checks_record_name"],
  "check_artifact_paths": ["checks/existing_source_review.json"]
}
```

This is a field illustration; its identifiers are placeholders, not evidence. Decision IDs are unique; reference lists are duplicate-free. The controller supplies the required analysis IDs from the intended request, and every required analysis needs a decision. Multiple decisions may apply to one analysis. The gate does not require mapping every evidence item or every initial nuisance parameter.

| Choice | Initial construction | Revision |
|---|---|---|
| `relationship` | Evidence and/or explicit assumptions linked to existing finite numerical parameter paths and provenance | Same bindings; report derives whether each exact path changed or was retained |
| `dispersion` | Same numerical binding, with the Agent declaring the dispersion role | Same derived changed/retained status |
| `check_only` | Evidence linked to existing check records; no parameter paths | Same, with no parameter change attributed to this decision |
| `scenario` | Explicit assumptions, optional evidence and existing scenario/population parameter paths | Exact changed or retained paths, including explicitly removed parameters; no probability or applicability claim |
| `retain_assumption` | Existing parameter paths and evidence and/or assumptions retained in the submitted specification | Claimed paths must be unchanged, including their descendants |

Model-use choices require linked evidence and/or explicit assumptions, plus nonempty parameter paths. Scenario choices require assumption IDs; retention may be directly evidence-backed without inventing an assumption. Assumptions must belong to the existing analysis. Every parameter's existing top-level provenance must contain the decision's evidence and assumption IDs. For a removed scenario path, provenance is taken from the bound baseline. A numerical-use choice cannot remove a parameter. The report labels `support_origin` as `evidence_only`, `evidence_and_assumptions` or `assumption_only`, so assumption-only updates cannot be mistaken for recovered source evidence.

The names `relationship` and `dispersion` are Agent declarations. The validator checks finite numerical values, not whether a value really is a slope, residual SD, SE or scientifically appropriate conversion. It never supplies a value, sign, distribution, conversion formula or uncertainty calculation.

Every nonmatching/unknown context comparison on selected evidence links, except `estimand`, requires a bridge assumption shared by the selected link and an existing unresolved gap of that dimension. Those bridge IDs must also appear in the decision and affected parameter provenance. This catches declared but unmarked population/measurement/selection/conditioning/adjustment/scale assumptions. It cannot detect omissions hidden in prose or false `declared_match` judgments. Existing analysis-evidence validation still checks explicit statistic, variable, unit-label and adjustment contradictions. Gaps remain unresolved.

Each decision names at least one existing check record. If any selected record is `pass` or `fail`, it must name at least one bound auxiliary artifact. `fail` is permitted and reported unchanged. An entirely `not_computable` decision may have no result artifact; its status remains non-computable. The existing check schema does not encode a machine-verifiable record-to-result relation, so those name/artifact associations remain declarations. Bound bytes do not prove check execution or numerical correctness.

## Exact change semantics

Parameter paths use canonical JSON Pointer escaping (`~1` for `/`, `~0` for `~`) and start with `/parameters/`. Dictionaries are compared recursively. Equal-length lists are compared by index; a changed list length is one change at the list path. Added/removed dictionary subtrees are one change at the added/removed key path. An unchanged ancestor cannot be claimed to conceal multiple changed descendants. A boolean is not the numeric value 0 or 1; formatting `1` as `1.0` alone is not a numerical change.

In revision mode every actual parameter change must be covered by a model-use decision. A shared parameter can support several requested analyses and can appear in several decisions; the union of covered changed paths must equal the exact actual diff. Unchanged relationship/dispersion/scenario use is valid, and `parameter_effects` reports it truthfully as `unchanged`. Check-only/retention entries cannot hide unrelated changes. This is scoped to `model_spec.parameters`; assumptions and provenance may be re-reviewed without changing numerical values. The report independently exposes `specification_bytes_changed` and `generator_bytes_changed`. A retained numerical model plus changed generator code is **not** an unchanged candidate.

In initial mode there is no invented baseline, no claimed improvement and no before/after difference. The report says `initial_values_bound`; change fields are null. Initial construction may author its own generator and specification without copying an earlier candidate.

## Explicit controller integration

The controller, not the sidecar, selects the actual candidate, allowed baseline, task and request analysis IDs. Before freezing a new candidate:

1. Load the sidecar with `cohort_harness.lifecycle.read_json`. Build the expected role-to-path mapping from controller state and require exact agreement with `manifest.bindings`; do not trust manifest paths to select another task or baseline.
2. Read only the expected role files plus `checks.json`-declared auxiliary results using the controller's safe-root/no-symlink file loader. Supply their exact bytes. Do not gather arbitrary workspace files, source targets or outputs. The gate itself has no filesystem permissions or isolation mechanism.
3. Call `validate_evidence_use(manifest, artifacts, required_analysis_ids=...)` before freeze. Preserve the returned statuses and limitations. Store its report outside the candidate if it would introduce a circular self-hash. Bind both the sidecar hash and report hash to the **new controller version's** freeze event, alongside its existing candidate commitment.
4. Normal candidate validation/freeze still checks registry admission and freezes all candidate bytes. Do not replace it with this gate. Before execution/delivery and during `Session.verify`, re-read the same committed paths, reject changes, rerun the gate and compare its report commitment. Reject code edits even when parameter values are unchanged.

This module installs no CLI hook and changes no old controller's behavior. Controller integration and a fresh empirical comparison remain separate work. Passing this gate does not demonstrate parameter use by the generator, transport validity, identified joint distributions, calibrated uncertainty, independent target performance or better data.
