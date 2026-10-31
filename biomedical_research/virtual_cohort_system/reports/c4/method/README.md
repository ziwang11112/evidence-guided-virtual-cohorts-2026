# C4 source-only selection controller

`controller.py` is a small wrapper around the existing trusted harness. It never
imports an Agent generator. Candidate structural validation and freeze use
`cohort_harness.lifecycle`; execution uses only the existing
`cohort_harness.execution.run_candidate` WSL/bubblewrap route. There is no local
fallback. The caller/Agent itself is not sandboxed. Hash receipts are procedural
integrity checks, not signatures or protection against a host user rewriting all
artifacts and approvals.

Only invented fixtures are used by `test_controller.py`. Its backend mock writes
a predetermined table, while the candidate source raises if imported. Those
tests exercise controller/harness bindings, not scientific generation or proof
of runtime isolation. All test artifacts remain under this method directory.

## Staged API

Run trusted Python from the virtual_cohort_system project directory with
`work/c4/method` on `sys.path`. `root` means the absolute `work/c4` directory.
The source custodian's `visible/task_a/source_contract.json` and corresponding
`task_b` file are the only source inputs; the controller never reads custody.

1. Root calls `setup_bundle(root, case)` for each case. This admits the exact
   artificial source into `b/<case>/sources/source_contract.json`, creates the
   harness registry/task, and returns the bundle path. No candidate is authored
   or executed. Source IDs are the source contract's `task_id` values.
2. The fresh author writes and harness-freezes `b/<case>/candidates/c0`.
   Root calls `freeze_plan(root, {"task_a": "c0", "task_b": "c0"})`.
   This exclusively creates `method/plan.json`, binding code, trusted harness,
   source, task, initial freezes, and all fixed seeds.
3. Root writes the exact feedback release described below, then explicitly calls
   `run_phase(root, "feedback", release_path)`. Only two initials × three seeds
   run. The returned records are trusted source diagnostics and may be supplied
   to the author as initial feedback.
4. The author writes and harness-freezes up to three revisions per case. Retain
   proposals may duplicate bytes but must retain distinct candidate labels.
   Each proposal must descend from c0 under the existing harness lineage rules.
   Root calls `freeze_pool(root, {"task_a": ["c0", "c1", "c2", "c3"],
   "task_b": ["c0", "c1", "c2", "c3"]})`. No election/test observations may
   inform these proposals. The complete per-case pool and feedback digest seal
   into `method/pool.json`.
5. Root writes the election release and explicitly calls
   `run_phase(root, "election", release_path)`: four labels × three seeds × two
   cases, 24 slots. Then `seal_selections(root)` verifies the complete election
   and exclusively creates `method/selection.json` before any test execution.
6. Root writes the test release, including the selection hash, then explicitly
   calls `run_phase(root, "test", release_path)`: the same four frozen labels ×
   three test seeds × two cases, 24 slots. Test data cannot change selections.

No API creates an execution approval. Root must create each release separately.
Feedback release is exactly:

```json
{"approved_by":"root","decision":"authorized","phase":"feedback","plan_sha256":"<method/plan.json SHA256>"}
```

Election changes `phase` to `election` and adds `pool_sha256`. Test changes phase
to `test` and adds both `pool_sha256` and `selection_sha256`. Extra/missing fields,
wrong phases, stale hashes, missing elections, and altered selections are
rejected. A root release is authorization by the root coordinator, not a claim
of a cryptographically authenticated identity or a hidden-evaluator approval.

## Fixed statistical and selection rules

- Feedback seeds: 24101, 24103, 24107. Election: 24203, 24209, 24223.
  Test: 24301, 24307, 24317. Exactly 54 planned slots; no deduplication.
- Trusted NumPy arithmetic mean, sample SD (`ddof=1`), and Pearson correlation
  are computed from the harness-verified generated CSV. No model parameters or
  Agent-reported diagnostics substitute for observed generated-table values.
- Every fixed mean/SD check uses absolute scale 0.10; every admitted Pearson
  correlation uses 0.05. They are engineering tolerances, not source SEs or CIs.
  Full source error is the arithmetic mean of squared errors divided by squared
  fixed scales. Every admitted check remains in the denominator (8 or 9 per
  table; three election seeds per candidate).
- The source numeric qualification requires every source check on every
  election seed to pass. Protected qualification requires every provided
  correlation on every election seed to pass; it does not adopt a new band.
- Retain-initial always selects index 0. Minloss minimizes mean full-source
  error over all four labels with lowest-index tie breaking, so a revision wins
  only on strict improvement over initial. The protected selector chooses the
  lowest-loss revision among those with strict loss improvement over initial
  and full protected qualification. Otherwise it retains initial and reports
  initial's own protected qualification, including `false` when appropriate.
- A failed or nonfinite draw invalidates the entire candidate, without averaging
  surviving seeds. JSON `null` mean loss means positive infinity; failed slots
  are listed. If all candidates are invalid, both selectors retain initial and
  protected qualification is false. This is a failure manifest, not success.

Each diagnostic binds case, phase, seed, index, candidate freeze/code/spec,
source, plan, execution receipt, and output-table hashes. Reading a phase
re-verifies harness artifacts and recomputes the trusted statistics. Run IDs
are deterministic and must be absent before the phase starts. Every scheduled
slot is attempted at most once; failures remain preserved and never trigger
automatic retries. Any interruption requires root review; restarting the same
phase is intentionally refused. Selection sealing also refuses any existing
test execution attempt, even a failed one.

## Unit verification

```text
python -B -m pytest work/c4/method/test_controller.py -q -p no:cacheprovider --basetemp work/c4/method/qa --junitxml work/c4/method/test_results.xml
```

Tests cover baseline retention, aggregate/protected tradeoff, strict improvement,
ties, single-seed failure, all-invalid fallback, finite statistics, frozen bands,
incorrect phases/seeds/cases, missing elections, approval and artifact tampering,
candidate byte/provenance binding, all 54 mocked slots, test-seal preservation,
and refusal to retry existing runs. See `test_results.xml` and `test_log.txt`.
