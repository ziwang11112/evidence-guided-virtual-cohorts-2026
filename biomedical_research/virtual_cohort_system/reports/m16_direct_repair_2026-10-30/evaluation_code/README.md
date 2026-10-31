# M16 locked target evaluator

This wrapper evaluates initial and final outputs of all three scheduled direct-Agent constructions. No target outcome is read at module import. Execution requires an explicit controller release after all constructions have closed. No evaluation output is returned to builders, and it does not authorize further repair.

`frozen_m15b_estimands.py` is a byte-identical copy of the prior evaluator, SHA-256:

`4181cfbd8ae37df58699558196ca241f2bd60e4d895b9a18de40a42cbaffce12`

Only its pure validation/estimation functions are called. Its old M15-B CLI and release gate are never called. The M16 wrapper validates native `WTMEC2YR` metadata, then selects only the unchanged base and survey-design columns for those functions. This does not change any estimator or apply weights.

## Fixed estimands and records

The estimands are the protocol's four global coefficients, four group reverse-regression coefficients and 16 group summaries. They retain all statuses, rank failures and nonfinite failures. Reference estimands and leave-one-joint-PSU-out sensitivity are calculated once. The actual number of available joint PSU groups is determined from the locked cohort; no count from an older experiment is imposed.

Each available initial/final table gets 24 comparison records. When all three constructions complete there are six scheduled table-stage records and 144 comparison rows, even if a retained table has identical initial/final bytes. Hash counts and numeric changed-row counts identify duplicate constructions; stage counts must not be described as independent tables. Initial/final changes comprise 72 rows when all three pairs exist, using `abs(final - reference) - abs(initial - reference)` in each estimand's native units. Both improvements and degradations remain.

A failed construction stays in `builder_outcomes`. An initial table, if it exists and was frozen, remains evaluated, but a nonexistent final table is not invented or replaced. There is no best-run selector, composite quality score, hidden threshold or inferential equivalence claim.

## Release schema

Every binding shown as `BINDING` is exactly `{"path": "absolute path", "sha256": "64 lowercase hex"}`. The controller assertions are trusted procedural records, not signed authorization or OS security.

```json
{
  "schema_version": 1,
  "kind": "m16_target_evaluation_release",
  "evaluation_authorized": true,
  "protocol": "BINDING to R/PROTOCOL.md",
  "controller": "BINDING to R/controller.py",
  "prelaunch": "BINDING to R/prelaunch.json",
  "self_checker": "BINDING to P/cohort_harness/self_consistency.py",
  "evaluator": "BINDING to this evaluator.py",
  "estimands": "BINDING to frozen_m15b_estimands.py",
  "reference": "BINDING to the previously committed reference under R/private",
  "reference_weight_column": "WTMEC2YR",
  "controller_checks": {
    "all_builders_closed": true,
    "preauthorship_verified": true,
    "feedback_binding_verified": true,
    "source_exposure_verified": true,
    "preservation_verified": true,
    "budgets_verified": true,
    "independent_code_review_complete": true
  },
  "builders": [
    {
      "id": "b1",
      "bundle_path": "absolute path to b1 bundle",
      "task_sha256": "exact b1 task hash",
      "observed_sha256": "shared observed byte hash",
      "status": "complete",
      "initial": {
        "candidate": "candidates/initial",
        "freeze_sha256": "initial freeze hash",
        "table_sha256": "initial CSV hash",
        "preauthoring": "BINDING to R/commitments/b1/initial.json"
      },
      "final": {
        "candidate": "candidates/final",
        "freeze_sha256": "final freeze hash",
        "table_sha256": "final CSV hash",
        "preauthoring": "BINDING to R/commitments/b1/final.json"
      }
    }
  ]
}
```

The actual `builders` list must contain b1, b2 and b3, in that order. Their task IDs may differ to bind separate literature sessions; all other task semantics must be identical. Their observed CSV bytes must match. For a failed builder set `status` to `failed`, add `failure_record: BINDING`, omit `final` and preserve `initial` if available.

Each preauthoring receipt requires:

- `builder`, matching b1/b2/b3;
- `candidate`, matching `candidates/initial`, `candidates/revision1` or `candidates/final`;
- `generated_exists: false`, a controller assertion recorded before CSV existence;
- timezone-aware `created_utc`, no later than the candidate freeze;
- `prelaunch_sha256`;
- `files` mapping the four candidate-relative scientific files to their hashes: `evidence.json`, `model_spec.json`, `audit/construction.json`, `audit/revision_plan.json`.

The canonical receipt must be byte-identical to the candidate's `audit/preauthoring_commitment.json`, and both this copy and scientific files must be bound by the lifecycle freeze. Any intermediate revision1 ancestor receives the same verification. Receipt chronology cannot prove author cognition; it prevents silent artifact rewrites and records the visible file sequence.

The prelaunch record supplies `files` as run-relative paths and `engine_files` as absolute Python-file paths, each mapped to SHA-256. Every builder's task/X must be included in that map. It also supplies `registry_prefixes` for b1/b2/b3, `reference: BINDING` and `reference_weight_column`; the released reference binding must exactly match this pre-generation commitment. The reference is not opened while verifying these commitments. Current source registry prefixes must preserve those seed records. Feedback/research audits remain additional required controller checks; a hash alone does not establish the scientific comparability of evidence.

## Invocation and outputs

```powershell
python evaluation_code/evaluator.py --execute --release-manifest private/evaluation_release.json --output-dir results
```

Run from R. The output directory must not exist. Without `--execute`, the CLI stops without reading inputs. The gate verifies all public and candidate commitments before opening reference bytes; those bytes are loaded once and then parsed from memory. Expected outputs:

- `evaluation.json`: all reference/candidate estimands, construction status, changes and sensitivity fits.
- `estimands.csv`: aggregate table-stage comparison records.
- `initial_final_changes.csv`: aggregate changes in absolute discrepancy; no participant rows.

Patient and synthetic row files remain local. These aggregate files do not establish biological accuracy by themselves; interpret them with provenance, declared assumptions and the complete results.

## Tests

`test_evaluator.py` uses invented engineering records only. It exercises real lifecycle freezes, known linear coefficients, exact comparison equality to the frozen module, all six stage records, degradation retention, duplicate-stage accounting, reference-read ordering, prelaunch/commitment failures, native weight-column handling, failed builder retention, schema errors and exclusive outputs. It never opens a real reference or generated cohort.
