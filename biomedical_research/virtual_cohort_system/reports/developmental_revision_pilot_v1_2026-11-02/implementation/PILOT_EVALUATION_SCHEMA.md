# Developmental pilot evaluation v1

This additive wrapper preserves the three CHNS focal OLS analyses and frozen reference uncertainty. It does not decode patient data, execute a generator, amend an old release, or supply target feedback to an author. CHNS was researcher-exposed; all results are developmental and descriptive.

## Entry points and release bindings

`pilot_evaluation_v1.evaluate(ledger_directory)` writes the primary report. `independent_pilot_recompute.recompute(ledger_directory)` checks it by separate CSV parsing, QR OLS, diagnostic calculations and summary arithmetic. CLI forms accept only the ledger path. Imports perform no study-data reads.

Both normally call `PilotController.open(ledger_directory).verify_evaluation(release.evaluator.sha256)`. The primary computes its own file hash and verifies its binding. The independent script verifies its own release binding and hashes, but never imports, the primary evaluator. Trusted callable seams `controller_gate` (primary) and `verified_controller_gate` (independent) exist for invented fixtures; they are not unverified-inventory entry points or an alternative scientific release mechanism.

The controller returns an authenticated closed inventory with `schema_version: 1`, `kind: developmental_pilot_closed_inventory`, `status: closed`, `scientific_closed: true`, `release_sha256`, `scientific_freeze_sha256`, `inventory_sha256`, `authorization`, `scientific_annotations`, and `slots`. The controller verifies the complete 72-slot source-plus-target accounting, release and scientific freeze, and receipts. The evaluator separately verifies all 18 target identities, row/context declarations, scientific annotation bindings and successful target output/receipt hashes before reading reference aggregate bytes.

`release_sha256` is the SHA256 of the complete release serialized as UTF-8 JSON
with `sort_keys=True`, `ensure_ascii=False`, `separators=(',', ':')`, and
`allow_nan=False`, including its review. Both wrappers independently compute this
same canonical identity; it is not the hash of the pretty-printed release file.

The release must contain `evaluator: {path, sha256}` and exactly these seven `evaluation` bindings:

| Key | Bound file |
|---|---|
| `analysis_module` | Unchanged `work/chns_admission_2026-11-01/f2/evaluation/chns_f2_evaluation.py` |
| `analysis_plan` | Unchanged `work/chns_admission_2026-11-01/f2/analysis_plan.json` |
| `reference_report` | Existing F2 `evaluation_results/REPORT.json` |
| `independent_reference_report` | Existing F2 `independent_results/REPORT.json` |
| `independent_recompute` | This version's `independent_pilot_recompute.py` |
| `policy` | A JSON serialization of the exact exported `pilot_evaluation_v1.POLICY` object |
| `analysis_environment` | JSON matching the actual host `analysis_environment()` object described below |

All bindings use an absolute `path` and SHA-256. The two reference bindings are deferred: the controller freezes their declared metadata but does not open or hash their files. The evaluator opens them only after scientific closure, successful output/receipt checks, and exclusive reservation of its output directory. Other evaluation bindings are verified before reference access. The release must also freeze applicable transitive dependencies through the controller's runtime/artifact bindings.

The `analysis_environment` file contains exactly `schema_version: 1`, `kind: developmental_pilot_analysis_environment_v1`, and string values for `python`, `numpy`, `pandas`, `scipy`. Both wrappers independently call `analysis_environment()` to read their actual loaded library versions and Python version, compare the entire object to the frozen file before reference access, and retain it in INTENT/report commitments. This is the Windows host analysis environment; the WSL generator runtime remains a separate identity. A static environment declaration alone is insufficient.

The release provides three distinct integer `target_seeds`, `target_context`, and `n_rows: 3000`. Constructors are exactly `A01` and `A02`; versions are exactly `initial`, `self_review`, `source_feedback`. Each slot provides `constructor`, `version`, `role`, `context_id`, `run_id`, `seed`, `n_rows`, `bundle`, `candidate`, `status`, `output_sha256`, `execution_sha256`, `error`. Success uses `<bundle>/executions/<run_id>/output/generated.csv` and `execution.json`. Every unsuccessful or unavailable slot remains in the denominator.

## Scientific annotations and complete source reporting

The authenticated inventory's `scientific_annotations` mapping has exactly six keys, one for every `constructor/version`. Each record has `candidate_binding` (`bundle`, `candidate`, `parent`, or null), `analysis_evidence` binding or null, `support_assessment` binding or null, `source_feedback` binding list, `source_feedback_format: pilot_source_closure_event_v1`, and `unavailable_reason` (string or null).

For a bound candidate, both wrappers verify and read its frozen `analysis_evidence.json` and independently reviewed support-assessment binding. Required analysis IDs map `E1 → A_BMI`, `E2 → A_GLUCOSE`, `E3 → A_AGE`. They preserve each entire declared analysis record, including assessment, rationale, assumption IDs, gaps, evidence links and planned actions when present. These labels are copied into every target slot and each endpoint's constructor/version summary. A numerically computed E3 can therefore remain explicitly unassessed. Numerical agreement never upgrades a scientific-support label. A failed or unbound version retains explicit unavailable labels and its reason.

Each source feedback binding points to an immutable `sources_closed` controller event. The event's `payload.key` must identify its version. The full payload is included with its binding, retaining the complete authenticated feedback packet, unavailable checks and assumptions, source slot dispositions and source-eligibility record. No source discrepancy is selected away. An empty source feedback list requires an explicit unavailable reason, including a registered but aborted version. The independent report separately rereads the bound sidecars/events and checks all labels and source-report content against the primary report. Both paths recheck these bindings before their final report.

## Preserved scientific analyses

Let H be HbA1c (%), A age (years), S female (0/1), B BMI (kg/m²), G central-serum glucose (mmol/L). All fits include an intercept and use unweighted raw OLS:

| ID | Formula | Reported coefficient |
|---|---|---|
| E1 | H ~ A + S + B | B, percentage points/(kg/m²) |
| E2 | H ~ A + S + G | G, percentage points/(mmol/L) |
| E3 | H ~ S + B + G + A | A, percentage points/year |

The F2 `analyze(..., reference=False)` and `compare_estimates` functions are imported from the hash-bound unchanged module. The historical common-complete-case reference, units, age restriction, cleaning policy and CR1/t community-clustered nominal 95% intervals remain unchanged. The wrapper reuses their frozen aggregate report; it does not rerun the reference read/reveal entrypoint. Scientific estimates remain withheld for invalid generated domains/nonfinite values, nonpositive glycemia, inadequate n, or rank/residual-df failure under the existing contract. The new generated task additionally requires integral age: either wrapper counts fractional ages and withholds all focal fits with `nonintegral_age_task_violation`. This does not change historical reference preprocessing. Rows are never deleted to rescue a fit.

CSV parsing in the primary uses pandas round-trip floating-point conversion, so serialized ties are preserved and agree with independent Python `float` parsing. The six columns must be exactly `row_id,age,female,bmi,glucose,hba1c`; all 3,000 row IDs must be present and unique.

## Diagnostic scope

The existing 27 reference-comparable diagnostics are mean, sample SD (`ddof=1`), q10, median and q90 for each of five variables, plus glucose–HbA1c Pearson and Spearman correlations. Linear quantiles and average Spearman ties retain the existing definitions. F2 analysis records include n, model rank and condition number.

The additions are explicitly **generated-only**, with `reference_status: unavailable_no_reference_supplement`:

- Linear q01/q99 for BMI, glucose and HbA1c.
- All ten unique Pearson pairs among the five variables. A constant-variable correlation is unavailable.
- Exact duplicated numeric five-variable rows after their first occurrence, excluding `row_id`; NaNs compare equal for this duplicate diagnostic.
- Nonfinite counts per variable, finite domain-violation counts per variable, a separate fractional-age count, union count of invalid rows and total n. Allowed domains are integral age 35–74 inclusive, female 0/1 and strictly positive BMI/glucose/HbA1c.

If any row is invalid, counts and duplicates remain reportable but added quantiles/correlations are withheld; no finite-row subsetting is performed. These diagnostics supply no new patient comparison, biological validity certificate or population-moment proof. There is no reference supplement in this version.

## Reporting arithmetic and outputs

Each of the 18 target slots retains its execution disposition, analysis, per-endpoint comparison, added diagnostics and any analysis error. All three endpoints receive separate summaries for every constructor/version. A version's mean absolute discrepancy is `sum(abs(seed_estimate - reference_point))/3`, only when all three prescribed seed estimates and the reference point are available. Signed mean discrepancy, each seed estimate, seed range and direction stability also remain visible. Available seed values are not promoted to a complete three-seed summary.

For each constructor and endpoint, report MAD changes for `self_review - initial`, `source_feedback - initial`, and `source_feedback - self_review`; a contrast is unavailable unless both versions are complete. There is no pooled endpoint score, across-constructor inferential interval, equivalence margin, or overall pass rule. The two constructions remain the scientific replication units. Neither 72 source/target tables nor their rows are independent replications of method performance. Retained unchanged branches remain paired repeats.

Reference point estimates and intervals, generated signs, supported/inconclusive reference direction, signed differences and descriptive interval membership remain available in the slot comparisons. No artificial-row inference is added. Source uncertainty, measured-reference uncertainty, conditional seed variation and transport uncertainty remain distinct.

Primary output is exclusively reserved at `<ledger>/evaluation/`: `INTENT.json`, then `REPORT.json` and `COMPLETION.json`, or `FAILURE.json`. Independent output uses `<ledger>/independent_evaluation/` with the same names. Existing directories cause failure; there is no overwrite or automatic retry. Analysis failures remain in their slots. Expected CSV parsing, layout and identifier failures receive distinct aggregate error codes without row values. No evaluator entrypoint can execute extra tables.

Artifact-identity errors are fatal integrity failures, never recoverable `analysis_error` entries. Both wrappers verify the target CSV and execution receipt before parsing; hash the exact CSV byte snapshot that will be parsed; and recheck both files after analysis and again before reporting. A detectable post-gate mutation raises `IntegrityError`, writes FAILURE after reservation, and produces no REPORT/COMPLETION. A late integrity failure does not erase the immutable closed 18-slot inventory or authorize a retry.

The independent implementation compares every slot's focal statistics, 27 existing diagnostics, added diagnostics, fit status/rank/conditioning, endpoint comparisons and paired summary arithmetic. It uses `csv.DictReader`, QR solves, independently written linear quantiles/moments, scipy correlations and independent summary code. It imports neither the new primary scientific helpers nor F2 analysis functions. It reuses reference uncertainty without re-estimating it. Its `rtol=1e-8`, `atol=1e-10` are numerical agreement checks, never scientific utility or equivalence thresholds. Disagreement produces an immutable disagreement report, not a repaired primary result.

## Invented-only verification

`test_pilot_evaluation_v1.py` verifies preclosure reference nonaccess, missing/duplicated slots, release/output/receipt mutation, all endpoints and 18-slot accounting, missing-seed denominators, absolute-before-average arithmetic, generated-only diagnostic scope, tie-preserving CSV parsing through independent agreement, duplicate/invalid-row behavior, rank deficiency, independent detection of changed report arithmetic, and exclusive failure/output handling.

The current completed targeted run was **31 passed**. Review regressions additionally cover all-six-version support/source-report preservation, unchanged unassessed labels on computed estimates, sidecar/source identity failures, live host environment mismatch before reference access, both CSV and receipt mutation before/after analysis in both wrappers, fractional-age withholding, and distinct aggregate output-error reasons. Earlier fixtures encountered Windows path length limits and exposed last-bit parser tie differences; short workspace-local test directories and round-trip parsing resolved those issues. No scientific generator, patient file, historical result table, source-feedback construction, or reference re-estimation was run by these tests. The controller seam was mocked; this test result does not claim live controller integration or a released pilot.
