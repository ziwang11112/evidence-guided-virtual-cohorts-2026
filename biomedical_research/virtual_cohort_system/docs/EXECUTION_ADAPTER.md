# Generator execution adapter

This M2 component runs frozen candidates in the existing Ubuntu-24.04 WSL distribution. It is not a standalone LLM application or a scientific validation result.

## API

    from cohort_harness.execution import run_candidate, verify_execution
    receipt = run_candidate(
        bundle, "candidates/initial", "run_001", seed=17,
        timeout_seconds=30, memory_mb=1024,
        output_bytes=20_000_000, log_bytes=100_000,
    )
    assert receipt["status"] == "success"
    verify_execution(bundle, "run_001")

Candidate freeze/verification is required. Outputs go to bundle/executions/<run_id>, outside the frozen candidate. Run IDs cannot be reused or traverse paths. Initial contract errors raise. An attempted run normally returns success, failed or timeout with a preserved receipt; always inspect status.

Only the inspected task-specific runtime is currently supported:

- Distribution: Ubuntu-24.04.
- Venv: /home/zwang/.cache/evidence-cohort-runtime/m2/venv.
- Bubblewrap: /home/zwang/.cache/evidence-cohort-runtime/m2/bubblewrap/usr/bin/bwrap.
- Inspected versions: Python 3.12.3, NumPy 2.4.5, pandas 3.0.3, bubblewrap 0.9.0.
- No fallback to unsandboxed local execution.

Runtime paths are trusted administrator configuration. A future portable adapter should use reviewed deployment configuration rather than let a biomedical builder choose arbitrary executables or mount roots.

## Actual boundary

Only the generated program process is sandboxed. The orchestrator, collaboration Agent, literature adapter and other tools remain outside this boundary. This does not establish that an LLM Agent cannot read target data through other tools.

Staged input contains only task, specification, observed data when applicable, generator, request and worker. Sources, the whole project, other candidates and real targets are not mounted. System mounts are read-only /usr, /lib, optional /lib64, dedicated venv at /runtime and optional loader cache. /mnt and /home are absent inside.

Bubblewrap requests user/mount/PID/network and other namespaces, disables nested user namespaces, drops capabilities, clears environment, creates a new session and remounts root/proc/input/runtime read-only. The only writable host mounts are two existing files: generated CSV and worker report. The output directory itself is not writable. /tmp is a 64 MiB tmpfs; the minimal /dev tmpfs is 1 MiB.

The worker sets per-process CPU, address-space, file-size, process-count and descriptor limits before candidate import. Linux timeout bounds wall time; a longer host timeout also applies. Logs are drained with bounded retained prefixes.

These are not cgroup-wide aggregate CPU/RAM limits. Process trees can distribute work among allowed processes. A timeout status with exit 137 denotes time/resource termination, not reliable attribution of wall time versus CPU versus another kill. Tested namespace behavior is not a proof against every kernel/runtime vulnerability.

## Output and integrity

Inputs are checked against the frozen candidate before launch and after execution. Exact staged bytes, runtime-file manifest, worker, command, logs and outputs are bound in the execution receipt. The host applies a bounded streaming CSV scan before pandas: exact expected header/order, row count and field count, physical lines and individual fields capped at 1,000,000 characters. Worker reports are capped at 64 KiB, type-checked, and malformed/deep JSON produces a preserved failure rather than an accepted result.

Host output validation enforces original columns, types, bounds, finite values, row order and preserved cells, including measured generated-variable cells in completion mode.

Worker reports remain writable by the candidate and are not trusted authentication. generator_executed reflects the worker entry report, may be null after abnormal termination, and is not proof against an adversarial program. Successful runs additionally require process completion and host data validation. Receipts are hashes relative to recorded bytes, not signatures; a host user rewriting both files and receipts can forge provenance.

verify_execution rechecks artifact sets/hashes, candidate freeze, input binding, seed/limits, scope and successful output contracts without rerunning code. Failed runs retain their evidence. Direct-row submissions never launch code: the frozen CSV is copied and validated with generator_executed false. The seed identifies that receipt but does not resample direct data.

## Verification

Unit tests use invented data. Mocked backend tests establish behavior of contracts, path checks, mutation handling, missing backend, malformed reports/receipts, host CSV bounds, output preservation, timeout/failure records and artifact binding. They do not prove isolation. Real subprocess pipe tests use trusted test commands only.

Actual isolated smoke: work/execution-smoke-8aa0fc1e. A newly frozen seven-row invented generator ran twice in WSL/bubblewrap with the same seed. Both outputs passed preservation/receipt verification and were byte-identical. Inside-program probes confirmed absent host mount paths, denied input/extra-output writes, and failed external TCP access.

Actual failure smoke: work/execution-failure-smoke-8c94996b. Invented candidates raised an error, modified observed cells, or looped forever. Results were failed, failed and timeout; all preserved receipts verified.

The separate runtime-readiness report records additional mount, capability and nested-namespace probes. No patient data, biomedical effect estimation, model training or new scientific validation was performed by these tests.

