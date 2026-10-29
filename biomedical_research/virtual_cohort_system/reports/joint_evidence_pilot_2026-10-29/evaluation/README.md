# M8 pre-release evaluator amendment

This directory copies M7's evaluator and protocol while preserving its frozen custody files. Main-model empty, rank-deficient and zero-design-df domains now retain explicit nonestimable endpoints. Other estimable models continue. Invalid full-design strata, invalid inputs and invalid outcomes still stop evaluation. No generalized inverse, dropped covariate, merged subgroup or altered survey calculation is introduced.

The TG >=150 diagnostic is **evaluation-only, for both synthetic and reference values after authorized release**. It is excluded from source fitting and builder feedback. Its definition is unchanged. The frozen 67 endpoint definitions, original tiers, weights, full-design domain linearization, occupied-domain degrees of freedom, contrasts, confidence intervals and generated-point-only reporting remain unchanged. The new campaign uses `baseline` and `joint_evidence`, target seeds 80101–80103 and source seeds 80201–80203. Source replay verification belongs to the controller guard. There is no ordinary-Agent comparison or required magnitude improvement.

`protocol_amendment.json` binds the M7 originals and every amended executable/protocol file. It also binds the invented validation receipt. M7 data stay at their original custody paths; this directory contains no participant table or copied outcome data.

## Validation

From the virtual_cohort_system project root:

```powershell
python -B work/joint-evidence-pilot-2026-10-29/evaluation/test_evaluator.py
```

Tests construct all numerical inputs in memory. CSV/XPT/SAS file IO and pandas CSV parsing are blocked. They compare all valid-fixture results exactly to M7, exercise partial/main-model rank failure, empty/zero-df domains, invalid full-design and outcome errors, unchanged protocol definitions, release denial, and amendment integrity. The receipt describes this limited validation, which is not independent survey-package replication. Re-running the test script updates its timestamped receipt; re-freeze the amendment before a later release if that receipt is changed.

## Later authorized invocation

```powershell
python -B work/joint-evidence-pilot-2026-10-29/evaluation/evaluate_committed.py --commitment <absolute-path-to-release-commitment.json>
```

The commitment uses the original M7 schema plus `evaluation_amendment`:

```json
{
  "authorize_target_evaluation": true,
  "all_candidates_and_seeds_committed": true,
  "custodian_lock_sha256": "SHA256 of unchanged M7 custodian_lock.json",
  "evaluation_amendment": {
    "path": "absolute path to this directory/protocol_amendment.json",
    "sha256": "SHA256 of that amendment"
  },
  "evaluation_design": {"path": "absolute path", "sha256": "SHA256"},
  "candidate_commitments": [
    {"variant": "baseline", "stage": "initial", "path": "absolute path", "sha256": "SHA256"},
    {"variant": "baseline", "stage": "final", "path": "absolute path", "sha256": "SHA256"},
    {"variant": "joint_evidence", "stage": "initial", "path": "absolute path", "sha256": "SHA256"},
    {"variant": "joint_evidence", "stage": "final", "path": "absolute path", "sha256": "SHA256"}
  ],
  "outputs": [{"variant": "baseline", "seed": 80101, "path": "absolute path", "sha256": "SHA256"}],
  "builder_observed": {"path": "absolute path", "sha256": "SHA256"},
  "controller_guard": {"path": "absolute path", "sha256": "SHA256", "function": "guard_function_name"}
}
```

The displayed output entry is a schema example; a real commitment must contain all six unique variant/target-seed combinations. `evaluation_design` must have `variants` and `seeds` exactly matching `analysis_protocol.json`. Initial and final entries may point to the same frozen candidate when no revision occurred. All paths should be absolute. The controller guard receives the resolved commitment path and must return a dictionary with `status: passed`; it remains responsible for candidate provenance, successful harness executions, source applicability and source-seed coverage.

Successful execution writes to `evaluation/results/`, which must not already exist. It validates every generated table and preserved covariate before parsing the original hidden reference. Results include comparison rows for mutually estimable endpoints and explicit reference/generated failure records in `nonestimable.json`. The amendment itself supplies no scientific evaluation authorization; none was issued or executed during preparation.

## Boundary record

Preparation read M7 custody Python code/protocol/receipts and its custody-audit files, the new files in this directory, and controller-authorized excerpts of M8 controller/guard source to check the import path. It did not parse or hash participant CSV/XPT files, run a generator, or evaluate the scientific target. One collaboration-agent inventory call unexpectedly returned other completed agents' historical aggregate-result summaries. That incidental exposure was immediately reported to the controller and was not used in code, tests, endpoint selection or model construction. Therefore this preparer does not claim complete absence of historical-result exposure.
