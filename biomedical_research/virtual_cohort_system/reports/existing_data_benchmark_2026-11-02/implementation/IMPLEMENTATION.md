# One-pass existing-CHNS benchmark runner

`run_benchmark.py` supplies the new finite inventory and comparison wrapper. It reuses the unchanged candidate lifecycle, WSL/bubblewrap executor, full Wave A runtime fingerprint and CHNS pure analysis functions. It does not construct scientific models, import submitted generator code on the host, acquire data or decode patient reference files. Implementation alone does not release the experiment.

The fixed constructors are `E0_A01` through `E0_A05` and `E1_A01` through `E1_A05`. Each uses `candidates/initial`, 3,000 generated rows, and execution IDs `initial_1701`, `initial_1702`, `initial_1703`. Limits are 180 seconds, 1,024 MiB, 2,000,000 output bytes and 10,000 log bytes per attempt. There are 30 reserved slots; the executor has no host fallback.

## Release and candidate-review schemas

Every binding is exactly `{"path": "absolute file path", "sha256": "64-character digest"}`. Root produces and independently reviews the release; this module does not manufacture approval.

```text
schema_version: 1
kind: existing_chns_benchmark_release
status: released
bundle_root: absolute W/evcB directory
artifacts: [bindings for frozen implementation, runtime, design and constructor inputs]
evaluation:
  analysis_module: binding to unchanged f2/evaluation/chns_f2_evaluation.py
  analysis_plan: binding to unchanged f2/analysis_plan.json
  reference_report: binding to unchanged f2/evaluation_results/REPORT.json
  independent_reference_report: binding to unchanged f2/independent_results/REPORT.json
runtime_check: binding to unchanged Wave A runtime/runtime_check.py
runtime_identity: binding to its RUNTIME_IDENTITY.json
approval:
  decision: approved
  independent: true
  reviewer_id: nonempty, distinct from producer after strip/casefold
  producer_id: nonempty
  approved_sha256: release_digest(release)
```

`release_digest` is SHA-256 of canonical UTF-8 JSON excluding `approval`: sorted keys, compact separators, `ensure_ascii=False`, no nonfinite numbers. The complete release file hash is separately committed by ledger initialization. Reference aggregate reports are deferred evaluation bindings and must not also appear in `artifacts`: their bytes are not opened or hashed before inventory closure. Designated module, plan and runtime bindings must point to the unchanged existing files. No original reveal entrypoint is invoked.

Mandatory artifact bindings include this runner; the existing executor/lifecycle/contracts/worker; the designated analysis module and plan; the Wave A runtime checker and identity; and, for all ten bundles, `task.json`, `registry.json`, `sources/evidence_packet.json`, `sources/NGSP_UNITS.md` and `input/compiled_evidence.json`. Root should additionally pin the reviewed preparation manifest, prompts/guidance, design/reviews and relevant scientific/runtime dependencies. The mandatory list is a minimum, not a transitive dependency scanner. All ten task bytes must be identical, whole-cohort, 3,000-row and free of `observed.csv`.

Each constructor review has:

```text
schema_version: 1
constructor: E0_A01  # the exact reserved ID
decision: approved
independent: true
reviewer_id: nonempty, distinct from producer
producer_id: nonempty
files:
  task.json: SHA256
  registry.json: SHA256
  candidates/initial/generator.py: SHA256
  candidates/initial/model_spec.json: SHA256
  candidates/initial/evidence.json: SHA256
  candidates/initial/decision.md: SHA256
  candidates/initial/checks.json: SHA256
```

`candidate_review_files(bundle)` returns that exact seven-file hash mapping. Only the five standard candidate artifacts may exist before freezing; candidate evidence must equal the release-bound compiled arm evidence. The review file is then itself bound by the runner's `FROZEN.json`. Standard `freeze.json` is created by the unchanged lifecycle. A schema failure before a successful freeze can be corrected under the external authoring policy; frozen candidates cannot be edited or replaced.

The coordinator's prefreeze policy permits an initial submission and at most two interface-only correction returns, preserving originals in archives and supplying no target/scientific-output feedback or numerical scientific suggestions. That authoring exchange is outside this execution wrapper and must be recorded by the coordinator's reviews/archives. The wrapper begins with the final independently reviewed five files and supplies no correction or scientific-retry interface.

## Commands and state transitions

From the project root, prefix each command with `python work/existing_data_benchmark_2026-11-02/implementation/run_benchmark.py --release ABS_RELEASE_JSON`:

```text
init
freeze E0_A01 --review ABS_CANDIDATE_REVIEW_JSON
run E0_A01
close E0_A01 --reason "All scheduled attempts retained"
# Repeat freeze/run/close for the other reserved constructors.
# An authoring failure may instead close directly without freeze/run.
close-inventory
evaluate
```

The equivalent Python functions are `init`, `freeze_constructor`, `run_constructor`, `close_constructor`, `close_inventory`, and `evaluate`, with the release path as first argument. Each operation rechecks the release commitments. State lives exclusively in `W/evcB/benchmark_control`; a second initialization cannot reset it.

`run` writes a durable three-slot allocation before runtime verification or dispatch. It then calls the unchanged Wave A `runtime_check.verify(RUNTIME_IDENTITY.json)`. Runtime unavailability records all three consumed slots without fallback. Each dispatched slot receives an exclusive intent; a shell failure, timeout, invalid output or interrupted dispatch consumes its allocation. A completed attempt stores verified receipt/output hashes and the retained artifact inventory. One failing slot does not erase the other scheduled slots. A second `run` fails before any new dispatch. An interrupted constructor has no resume path; close it with its partial artifacts and unrun-consumed slots retained.

`close` may record three unrun slots for a constructor that never froze/executed. Closing does not invent a successful output. The trusted coordinator must await a running process's termination before closing its constructor; the wrapper does not kill external caller processes. `close-inventory` requires all ten closures, verifies their bindings and all 30 identities, and then writes the immutable final inventory. Scientific evaluation cannot begin before that file exists and matches the independently reverified closures. No output statistics are computed during execution or closure.

## Evaluation and reporting

`evaluate` reserves a new evaluation directory before opening reference aggregates. It verifies the exact primary and independent report hashes and reads only the old primary report's already computed reference object. It never calls `evaluate_released`, `summarize_slots`, the reference decoder or the old reveal controller.

For every verified successful new output, it validates the full task and applies existing `analyze(..., reference=False)` and `compare_estimates`. Failed/unrun/withheld outputs remain among all 30 report entries. A table-level analysis error is retained and makes its constructor incomplete; it does not select a smaller denominator or fall back to an old output.

For each estimand, the constructor statistic is the mean of the three absolute seed-wise discrepancies from the fixed reference point. Only a complete constructor has that statistic. Arm means average all five constructor statistics, and the contrast is E1 minus E0. A complete-arm positive claim requires completeness for all three endpoints and negative contrasts for both designated first endpoints. Available survivor results remain visible but cannot establish that claim. The third endpoint is always reported.

Sensitivity repeats these same summaries at the existing reference interval's lower and upper endpoints. It is descriptive endpoint sensitivity, not whole-interval robustness, equivalence margins or a joint confidence region. The output does not give artificial-row sampling intervals or treat seeds as clinical replications.

Outputs are `benchmark_control/evaluation/INTENT.json`, `REPORT.json`, and `COMPLETION.json`. Failure after reservation produces `FAILURE.json`; evaluation cannot automatically retry. The report retains independent recomputation as pending for the separately designated reviewer. It is a reused-benchmark result, not new independent confirmation.

## Focused author checks

The new `test_run_benchmark.py` uses invented metadata, aggregate estimates and output-byte fixtures. Process/runtime/lifecycle boundaries are explicitly mocked where needed. It does not launch WSL, execute a biomedical generator, decode patient files or rerun an old software suite.

The initial run had 15 passes and one assertion failure: the missing-final-inventory guard correctly raised the lifecycle's `ContractError`, whereas the test had expected raw `FileNotFoundError`. The test expectation was corrected; two further success/output-binding composition checks were added. The final new suite completed **18 passed in 4.57 seconds**. Coverage includes complete-slot identities, correct mean-absolute aggregation, opposing primary effects, missing third endpoints, all-unrun closure, preclosure reference nonaccess, exclusive evaluation, release/candidate/output mutation, runtime and shell failures, interruption/no-resume, and all 30 new analysis calls.

These checks support the tested orchestration/arithmetic boundaries, not scientific validity or an actual runtime execution. No scientific table was generated by implementation or its tests. All old source, code, protocol, candidate, outcome and failure files remain unchanged.
