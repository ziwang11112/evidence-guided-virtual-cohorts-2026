# Mechanical execution and evaluation plan

This is a read-only infrastructure review for `PROTOCOL.md`, followed by this new planning document. No generator, test suite, reference preparation, evaluation, source download, or old-session mutation was performed. No participant rows, generated rows, or numeric target results were opened. Runtime availability was inspected using `stat` only. The plan does not select a scientific structure, coefficient, residual scale, sign, or distribution.

## Reuse boundary

Let `P = D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system` and `D = P/work/source_increment_revision_2026-11-05`.

The existing `work/core_workflow_replication_2026-11-04/runner.py` is not a general single-case runner. Its `protocol()` requires exactly four authors, two specified cases, five original seeds, a 20-attempt batch, and one feedback revision; its `initialize()` requires old gateway accounting and its evaluator closes all four old sessions. Do not run, reset, monkeypatch, or copy that old workflow to create this new unit. In particular, `evaluator_v2.evaluate()` targets the old evaluation directory and old batch closure. Reuse its simple endpoint validation/comparison behavior in a new controller under D, with the new unit's own closure gate.

The minimal reusable primitives are:

| Purpose | Exact existing callable |
| --- | --- |
| Static task/spec/program contract | `cohort_harness.__main__.validate_bundle(bundle, candidate_path)` |
| Registry/artifact commitments | `cohort_harness.lifecycle._registry(bundle_path)`; checked again by freeze |
| Source semantics before freeze | `cohort_harness.semantic_feedback_v1.preflight(bundle, candidate)` |
| Exclusive candidate freeze | `cohort_harness.lifecycle.freeze_candidate(bundle, candidate, parent_receipt=None, revision=None)` |
| Frozen candidate verification | `cohort_harness.lifecycle.verify_candidate(bundle, candidate)` |
| Isolated execution | `cohort_harness.execution.run_candidate(bundle, candidate, run_id, seed, *, runtime=None, timeout_seconds=30, memory_mb=1024, output_bytes=20000000, log_bytes=100000)` |
| Execution verification | `cohort_harness.execution.verify_execution(bundle, run_id)` |
| Explicit semantic feedback | `cohort_harness.semantic_feedback_v1.collect_feedback(bundle, candidate, run_id, feedback_id)` |
| Feedback verification | `cohort_harness.semantic_feedback_v1.verify_feedback(bundle, feedback_id, candidate=..., run_id=...)` |
| Generated-only E01 estimators | `generated_feedback.generated_statistics(frame, expected_rows=3000, expected_per_cell=375)` from the pinned provider below |

Lower-level freeze/execution calls do not enforce independent review, a one-scientific-candidate budget, the three seeds, or a reference barrier. A small append-only controller in D must enforce these rather than relying on the adapter alone.

## New bundle assembly

Create a previously absent directory such as `D/bundle` only after an admissible proposal passes independent scientific review. Never copy the complete old bundle. Assemble an exact allowlist:

1. Copy `request.json` byte-for-byte from `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcRepE01/request.json`.
2. Derive `task.json` from that E01 bundle. Retain the scientific population, six columns, units, constraints, 3,000 rows, and whole-cohort mode. Give it a unique new ID such as `source-increment-2026-11-05-E01`. Record every changed administrative field explicitly. New source-query/download permissions should be zero and literature tools removed for this no-acquisition unit. The repair-lineage issue below must be resolved prospectively if two possible postfreeze mechanical repairs will be supported.
3. Copy each allowed source file referenced by the E01 `registry.json`, maintaining its relative `sources/...` path and original bytes. The registry has four original literature source IDs and search artifacts; copying original registered artifacts does not grant new acquisition. Do not copy `executions`, `semantic_feedback_v1`, old feedback/evaluation, sessions, or old candidate freezes.
4. Add only the admitted supplement extraction and original converted text named in the controller's allowed-file manifest, under new `sources/...` paths. Bind both to the existing parent source ID `PMC6458679`, or to an explicitly documented supplement source ID used consistently in the author's evidence. The source registry entries for newly admitted local artifacts use `origin: "curator"`, not a fictitious new gateway download.
5. Keep the static initial evidence, model specification, generator, and proposal in a distinct allowed-input location for author inspection. Do not carry old checks, feedback, frozen receipts, or generated data into the new candidate by directory copy.
6. The new scientific author supplies the candidate files and source mapping. Record exact hashes of every allowed input before author access; commit the final new bundle task/request/registry/source hashes before execution.

Registry schema is exact; no extra top-level or per-artifact keys are accepted:

```json
{
  "artifacts": [
    {
      "source_id": "PMC6458679",
      "path": "sources/admitted/supplement_converted.txt",
      "sha256": "<actual lowercase SHA256>",
      "origin": "curator",
      "screening": "approved"
    }
  ]
}
```

The registry shown is a schema example, not the complete proposed registry. Paths must be safe bundle-relative paths under `sources/`; files must exist and match the hashes. Every `evidence.json` source artifact must match a registry triple `(source_id, path, sha256)`. Hashes assert retained-byte identity, not scientific validity or source authenticity.

For a generator candidate, `candidates/increment/` needs at least `evidence.json`, `model_spec.json`, `generator.py`, `decision.md`, and `checks.json`. Its `generate` function must have exactly three positional arguments `(observed, specification, seed)`; static validation parses its AST without importing it. The execution adapter stages only `task.json`, `model_spec.json`, `generator.py`, and trusted worker/request files for whole-cohort generation. A generator must not require sibling source files or undeclared helper modules at runtime.

Computed records in `checks.json` require actual bound auxiliary result artifacts. A truthful static-only/not-computable record is preferable to claiming a computation that did not occur. Do not install an old `source_check_report.json`: freeze recomputes any such report through a separate legacy source-check route. This unit's generated source-statistic comparisons must use semantic v1 explicitly.

## Source semantics and review before execution

The semantic route requires two additional candidate files, both frozen:

* `whole_cohort_feedback.json`: exact keys `schema_version`, `population`, `measurement`, `assumption_ids`, `checks`. Population equals the actual new task population. Measurement is `{mode: "identity", description: ...}`. Each check has `id`, `evidence_id`, `status`, `operator`, `assumption_ids`, and `reason`. A `not_computable` check has `operator: null`.
* `source_semantics_v1.json`: exact keys `schema_version`, `evidence_sha256`, `recipe_sha256`, `bindings`. Each binding has `check_id`, `evidence_id`, `source_locator`, `definition_status`, `source_operator`, `weights`, `transform`, `source_variable_units`, `source_n`, `uncertainty_role`, `reason`. It must cover every feedback check exactly; evidence and recipe hashes must be current.

For unsupported/unreported source definitions, keep the source operator null, variable-unit mapping empty, and the check unavailable. Unknown/weighted estimators, nonidentity/unknown transformations, and missing quantile conventions cannot produce a discrepancy through v1. Its regression operators support explicit unstandardized per-unit nonintercept OLS coefficients with specified outcome, predictors, term, intercept, selection, missingness policy, and units. A source SD cannot become estimator uncertainty or residual noise merely by changing its label. An author's explicit working unit interpretation is still an assumption; a v1 pass does not verify the source's true unit or transport validity.

The external prefreeze review should bind every candidate file hash and explicitly approve code/spec agreement, finite-moment support, source semantics, and use of no target outcomes; identify distinct author/reviewer identities. Store review outside the candidate. Recheck these hashes immediately before freeze. `lifecycle.freeze_candidate` by itself does not enforce this independent review.

## Runtime and execution

The adapter accepts only the following inspected administrator configuration:

```json
{
  "backend": "wsl_bubblewrap",
  "distribution": "Ubuntu-24.04",
  "venv_root": "/home/zwang/.cache/evidence-cohort-runtime/m2/venv",
  "bwrap": "/home/zwang/.cache/evidence-cohort-runtime/m2/bubblewrap/usr/bin/bwrap"
}
```

It requires a local Windows drive bundle path, not UNC. The prior runtime metadata reports Python 3.12.3, NumPy 2.4.5, and pandas 3.0.3. Read-only `wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/stat` during this review confirmed the named venv Python link/config and executable bubblewrap and `/usr/bin/timeout` files exist. This is file-availability evidence only; no new sandbox launch was performed. The adapter itself inspects runtime package/file hashes when an authorized execution starts and fails closed if unavailable.

Use the old E01 mechanical resource limits explicitly: 30 seconds, 1,536 MiB memory, 20,000,000 output bytes, 100,000 log bytes. Run only seeds 5301, 5302, 5303. The adapter uses no-network/unshared bubblewrap, read-only input/runtime mounts, bounded output mounts, resource limits, and preserved receipts. It isolates the generator process, not the author/controller. The direct-CSV route does not execute a generator and should not be substituted for the required isolated generator route in this unit.

Concrete intended calls, after the new controller records independent review and schedule commitments:

```python
from pathlib import Path
from cohort_harness import lifecycle, execution, semantic_feedback_v1 as semantic
from cohort_harness.__main__ import validate_bundle

bundle = Path(D) / "bundle"
candidate = "candidates/increment"
validate_bundle(bundle, bundle / candidate)
preflight = semantic.preflight(bundle, candidate)
# Persist preflight and independently checked candidate hashes in D.
frozen = lifecycle.freeze_candidate(bundle, candidate)
assert frozen["route"] == "generator.py"

# Reserve each attempt in an exclusive append-only controller ledger first.
receipt = execution.run_candidate(
    bundle, candidate, "increment_5301_a1", 5301,
    runtime=execution.DEFAULT_RUNTIME,
    timeout_seconds=30, memory_mb=1536,
    output_bytes=20_000_000, log_bytes=100_000,
)
verified = execution.verify_execution(bundle, "increment_5301_a1")
# Record success/failure, receipt hash, and table hash only if successful.
```

The other scheduled slots use the same frozen candidate and seeds 5302 and 5303. The example is a plan, not a statement that these calls ran. If a call raises before a verifiable receipt exists, preserve the reserved attempt, exception type/message, any partial directory, and any unverified receipt rather than deleting/replacing it. Never use `import generator`, a host-side call to `generate`, or a local execution fallback.

Equivalent direct CLIs from P are available, but a controller is still needed for budgets/reviews:

```powershell
python -B -m cohort_harness validate --bundle "$D/bundle" --candidate increment
python -B -m cohort_harness.semantic_feedback_v1 preflight --bundle "$D/bundle" --candidate increment
python -B -m cohort_harness freeze --bundle "$D/bundle" --candidate increment
python -B -m cohort_harness execute --bundle "$D/bundle" --candidate increment --run-id increment_5301_a1 --seed 5301 --runtime "$D/runtime.json" --timeout-seconds 30 --memory-mb 1536 --output-bytes 20000000
python -B -m cohort_harness verify-execution --bundle "$D/bundle" --run-id increment_5301_a1
```

The authoring phase must close before target statistics are made available. For the simplest implementation, resolve all scheduled slots, record closure and all table/receipt hashes, then collect semantic feedback and generated-only diagnostics. Each successful run uses `semantic.collect_feedback(bundle, candidate, run_id, run_id + "_source")`; the CLI is `python -B -m cohort_harness.semantic_feedback_v1 collect --bundle ... --candidate increment --run-id ... --feedback-id ...`. Do not call legacy whole-cohort feedback, `source-checks`, or `source-replay` as a fallback. Source discrepancies are qualified target-context comparisons under declared assumptions, not reconstruction of the source population.

## Evaluation using cached summaries only

Use the existing provider at `P/work/main_study_freeze_2026-11-03/cases/ENSANUT2018/generated_feedback.py`. Its pinned provider hash in the core profile is `1a5a3cd6126211dc2e24f2d1c7fa58e4afdbc980e29c6fdccb6b637c7cf4e551`. It imports only a pinned pure analytical engine, `P/work/autonomous_research_cycle2_2026-10-31/analysis/analytical_engine.py`, with hash `1799c017b60f8fd3a9af409a524d3ebd9e54c81016e52da760aeafaefe03289d`.

Do not call `evaluate_generated(..., profile)` with the core `open_evidence` profile: that older wrapper permits only `E0`/`E1` and would reject the profile. Follow the core runner's existing method: verify the new execution, load only its new output with `lifecycle.read_table(output, task, output=True)`, then call `generated_statistics(frame)` directly. Importing the pinned provider/engine is safe from reference reads; calling it on the old patient rows is outside scope.

The full endpoint contract is `P/work/core_workflow_replication_2026-11-04/ENDPOINT_CONTRACT.json`, `cases.ENSANUT2018`. It has three analyses and 28 diagnostics: Q2-minus-Q3, adjusted glucose coefficient, Q1 residual RMS, and five summaries (mean, population SD, q10, q50, q90) for each of age, female, BMI, glucose, HbA1c. Preserve every declared endpoint and unit, even when unavailable. Retain provider quality information, eight-cell counts, duplicate counts, and model ranks. `evaluator_v2.finite/validate/missing/add_reference` are useful reference implementations; if reused directly, import the module without invoking `evaluate()` or old runner methods. Use the numeric-scalar-corrected `numbers.Real` validation, excluding Booleans and accepting NumPy real scalars before converting them to Python `float`.

The cached summary file is already bound by the old protocol:

* Path: `P/work/main_study_freeze_2026-11-03/final_evaluation/RESULTS.json`.
* SHA256: `1fbc32d2f982d31c649d9217e644a34c02b81e08c093380fba8f3aaec9e4c2cb`.
* Data selector, only after new closure: `read_json(path)["references"]["ENSANUT2018"]`.

The reference file and its numeric contents were not opened in this review. The new evaluator should verify that hash, read the cached reference branch only after the new closure commitment, compare matching IDs/units, and retain signed/absolute differences and direction descriptively. It must not call historical custodian/reference-preparation paths or `run_evaluation.py`, which can re-read or refit patient rows. Do not derive a new reference by reading the source cohort. Avoid copying the entire old RESULTS document to author-accessible D input folders: it contains other cases and historical outcomes beyond the allowed scientific packet.

The exact E01 estimator definitions are:

* Eight sex-by-age strata, equal weight 1/8 each; row weight `1/(8*n_h)`; new tables must have exactly 375 rows per stratum.
* Full design: intercept, `(age-50)/10`, `female`, `(bmi-25)/5`, `(glucose-100)/10`; Q1 is the age coefficient and Q3 the BMI coefficient.
* Reduced design: the first four columns; Q2 is its BMI coefficient.
* Secondary glucose model: intercept, age10, female, glucose10.
* Full-rank square-root-weight least squares; SVD relative tolerance `max(X.shape)*eps(float64)`; rank-deficient results unavailable.
* Weighted population SD and inverse-CDF weighted quantiles with the existing engine's compensated cumulative mass; no interpolation.

The independent numeric reviewer must recompute all three primary coefficients on each new successful table using an independently written calculation, plus Q2-minus-Q3, full-model residual RMS, full/reduced design rank, singular values/condition information, and conditional BMI/glucose variability. New generated-only descriptive checks should be fixed before reference exposure and labeled as additional diagnostics; they must not replace the 28 existing diagnostics or become a new favorable target-comparison endpoint. Reusing `generated_statistics` alone is not an independent recomputation. No independent target refit is necessary or authorized.

The new evaluator should output all three scheduled slots, failure/not-attempted reasons, all primary/diagnostic values and comparisons, table/receipt/freeze hashes, and accounting. Store evaluation-start and evaluation-completed/failure markers exclusively. Do not silently rerun an existing evaluation directory. Summaries over successful slots must retain scheduled denominator three and count unique table hashes; three seeds quantify this candidate's sampling variation, not uncertainty over scientific structures.

## Protocol issues to resolve in the new controller, before any execution

1. **Mechanical repairs versus old lifecycle budget.** The copied E01 task permits one revision, whereas the new protocol permits up to two mechanical repairs. `lifecycle` counts changed generator bytes as a `kind: "revise"` regardless of scientific equivalence and requires all parent freezes inside the same new bundle. If postfreeze repaired versions are supported, set the new task's administrative revision allowance to two before freezing and separately enforce one unchanged scientific law with independent repair review. Report these as mechanical versions of one scientific candidate; do not reuse or modify the historical freeze. Otherwise adopt the stricter one-repair limit explicitly. A parent receipt from the old bundle is invalid.
2. **Attempt accounting.** The adapter has no schedule cap. Interpret three scheduled seeds plus at most two failed-attempt replacements as at most five physical executions, no more than one accepted successful table per scheduled seed and three overall. Reserve before launch, retain every failure, and never replace a successful output. A repair must be justified by a concrete execution/format failure, not any unfavorable endpoint.
3. **Freeze wording.** One scientific law must be fixed before every scheduled run. A later format repair that alters code bytes needs a new immutable mechanical version and a review that the law is unchanged. If uncertainty remains about scientific equivalence, stop rather than consume a new scientific candidate. Keep target comparison closed throughout repair resolution.
4. **No reference exposure through convenience preparation.** Loading old runner sessions or invoking broad historical preparation/evaluation can traverse old outputs or reference rows. Implement the new unit directly from the low-level calls above; a new-unit gate must not borrow the old batch's already-completed gate.
5. **Unlabelled source units.** Semantic v1 checks declaration consistency, not whether inferred source units are true. The scientific reviewer must explicitly classify unit/transport choices; where a defensible operator cannot be established, retain unavailable checks and stop generation if the author/reviewer retains the original scientific candidate.

Only this plan was written by the infrastructure reviewer. It does not authorize generation absent the new proposal/review decision and does not claim that isolated execution has succeeded.

## Review of the subsequently supplied `prepare_bundle.py`

Read-only review found that the proposed actual destination is `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcIncE01`, candidate `source_increment`; substitute those paths/names for the illustrative `D/bundle` and `increment` above. This preparation script had not been run when reviewed. Its copied E01 scientific task fields, unique task ID, zero source acquisition budget, removed literature tools, retained source hashes, and three converted supplement artifacts admitted as `PMC6458679` curator entries are mechanically compatible with the harness. Its separate proposal/review hash gate is appropriate for a controller-author separation, provided the controller has actually inspected review acceptance.

Two concrete reconciliation items remain:

* The script sets `budget.revisions` to zero. This supports the unmodified initial freeze but makes any postfreeze lineage repair impossible. If the protocol's two possible mechanical repairs are to remain available, provision the administrative allowance prospectively and independently enforce unchanged scientific law; do not mutate task.json after freezing.
* Inspection of `INPUT_MANIFEST.json` filename keys (not file contents) found initial `source_semantics_v1.json` and `whole_cohort_feedback.json`, and the supplement probe's `SCIENCE_REQUEST.json` and `SCIENCE_DECISION.md`, in addition to the exact scientific-input list stated in PROTOCOL.md. Static recipe files do not automatically contain old numerical feedback, but they exceed the protocol's stated initial candidate file allowlist. The controller should reconcile the documented intended boundary with actual author access before reporting it. If access already happened, record it transparently; do not describe an amended list as the original pre-access protocol.

For additional mechanical robustness, validate the original registry's safe source paths before copying, deduplicate supplement triples if two converted artifacts share a hash and suffix, validate the final task and new registry before admitting the bundle, and exclusively create controller receipts. These are static preparation checks, not new biomedical or generator tests.
