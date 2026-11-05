# Feedback from a verified whole-cohort output

M17-A, 2026-10-31. `cohort_harness.whole_cohort_feedback` calculates permitted source statistics from an **already successful, verified whole-cohort execution**. It accepts program and direct-table routes. It does not execute or revise a generator, reconstruct another source population, transform measurements, calibrate parameters or read reference outcomes.

This fills the small provenance gap between existing whole-cohort execution and source-statistic calculation. Existing enrichment-only source-replay modules are unchanged.

## Frozen recipe

Before freezing the candidate, add `whole_cohort_feedback.json` with this schema:

```json
{
  "schema_version": 1,
  "population": "EXACT population string from task.json",
  "measurement": {
    "mode": "identity",
    "description": "State the same-variable/unit assumption and any source applicability limitation."
  },
  "assumption_ids": ["A_population"],
  "checks": [
    {
      "id": "mean_y",
      "evidence_id": "E_mean_y",
      "status": "approximate",
      "operator": {
        "kind": "mean",
        "unit": "y_unit",
        "selection": [],
        "missing_policy": "error",
        "column": "y"
      },
      "assumption_ids": [],
      "reason": "Compare this cohort's generated mean with the admitted source estimate under the declared applicability assumption."
    },
    {
      "id": "unsupported_statistic",
      "evidence_id": "E_other",
      "status": "not_computable",
      "operator": null,
      "assumption_ids": [],
      "reason": "The required analysis cannot be represented by the available variables/operator."
    }
  ]
}
```

This is a schema example, not an admissible scientific evidence packet. Replace IDs and descriptions with actual declared evidence and assumptions. Every ID must exist in the frozen candidate's evidence/model specification. Check IDs are unique ignoring case. An approximate check must carry an assumption at the plan or check level; a computed check must carry neither. The shared source-replay metadata validator also checks kind/unit and variable/adjustment alignment. Numeric operator fields are checked by the shared statistical engine.

Plan population must equal the executed task population. This forces the report to identify the population actually generated; it does **not** prove that the source paper studied an equivalent population. Differences must be declared as assumptions. No alternate input CSV or transformation expression is accepted.

Explicitly unsupported checks are retained with `operator: null`. Runtime undefined statistics, such as an empty selected group or a rank-deficient regression, are retained as `not_computable` with the original declared status and reason. Invalid operators, unknown evidence, unit/kind mismatches and malformed metadata cause collection to fail; they are not silently dropped.

## Interface

From the project root, after a candidate is frozen and its execution completed:

```powershell
python -m cohort_harness.whole_cohort_feedback collect --bundle BUNDLE --candidate initial --run-id RUN_ID --feedback-id FEEDBACK_ID
python -m cohort_harness.whole_cohort_feedback verify --bundle BUNDLE --candidate initial --run-id RUN_ID --feedback-id FEEDBACK_ID
```

`--candidate` accepts a simple name, `candidates/NAME`, or the absolute candidate path inside the bundle. Run and feedback IDs use the existing portable-name contract. The API is:

```python
from cohort_harness.whole_cohort_feedback import collect_feedback, verify_feedback

report = collect_feedback(bundle, "candidates/initial", "run01", "feedback01")
verified = verify_feedback(bundle, "feedback01", candidate="candidates/initial", run_id="run01")
```

Feedback is written exclusively to `BUNDLE/whole_cohort_feedback/FEEDBACK_ID/feedback.json`, outside the frozen candidate. Existing feedback IDs cannot be reused. Initial contract errors do not create an accepted report; if post-write verification detects a change, the attempted report is retained for inspection rather than overwritten.

Collection and verification both call the existing candidate and execution verifiers. The execution must be successful, whole-cohort and for exactly the requested frozen candidate. Whole-cohort tasks reject observed-column roles and an `observed.csv` file. A failed execution can have an intact execution receipt but cannot supply accepted numerical feedback.

The report binds hashes of the task, candidate freeze, recipe, evidence, model specification, execution receipt and generated CSV. It also binds the collector and shared implementation files and calculator versions. Verification recomputes all statistics and differences from the verified execution output, checks the expected candidate/run, and rejects altered report contents or extra feedback files. Reverification requires compatible recorded calculator/code versions; it is not a cross-platform floating-point equivalence service.

## What the report means

- `status: complete` means collection finished, including any explicitly not-computable checks. It does not mean the source constraints fit.
- `output_link_verified: true` links the evaluated table to the retained verified execution output.
- `generator_execution_recorded` is inherited from that execution: true for a successful program route, false for a direct table copied and checked without code execution.
- `agent_authorship_verified: false` remains explicit. These receipts do not establish which model authored a table/program.
- A check's `difference` is generated minus reported statistic, in its stated unit. There is no acceptance threshold, universal loss, or pooled scientific score.
- Original source uncertainty is preserved for interpretation; this module does not turn it into calibrated transport uncertainty.
- Source applicability, measurement equivalence and the absence of individual records inside admitted evidence require substantive review. No Agent-wide filesystem isolation is supplied.
- Hashes are relative commitments, not signatures against a host user rewriting the record; the recorded creation timestamp is not externally attested.

After reviewing feedback, an Agent may retain or revise under the task's budget. Bind the actual feedback in a new candidate's auxiliary check artifacts. Never insert a new report into an old frozen candidate.

## Artificial preparation-only example

`examples/m17a_whole_cohort.py` writes a new whole-cohort bundle with synthetic aggregate evidence, fictional variable names/units, a seeded NumPy/pandas test program and a recipe-bearing candidate. It writes **no individual table**, runs no generator, and does not freeze or execute the candidate automatically.

```powershell
python examples/m17a_whole_cohort.py --destination NEW_BUNDLE_PATH --n-rows 128
python -m cohort_harness validate --bundle NEW_BUNDLE_PATH --candidate initial
python -m cohort_harness freeze --bundle NEW_BUNDLE_PATH --candidate initial
```

The program is trusted mechanical test code with explicit invented coefficients. It is not an Agent-authored scientific result, biomedical generator or independently validated new method. A controller may subsequently use the established isolated `execute` adapter after review. This documentation does not claim such a run occurred.

## Focused verification

`tests/test_whole_cohort_feedback.py` uses invented direct tables and a mocked program backend. It checks no-observed staging, route semantics, frozen-byte preservation, independent known arithmetic, wrong mode/candidate, failed execution, invalid recipe metadata, undefined/unsupported statistics, report/output/recipe tampering, append-only IDs and CLI round trips.

The first focused run had 32 passes and one failure because a test expected a different error-message wording; the implementation correctly rejected the extra operator field. The test expectation was corrected. Final test results are recorded in the readiness note after execution. Mocked program execution tests do not establish actual OS isolation or scientific performance.
