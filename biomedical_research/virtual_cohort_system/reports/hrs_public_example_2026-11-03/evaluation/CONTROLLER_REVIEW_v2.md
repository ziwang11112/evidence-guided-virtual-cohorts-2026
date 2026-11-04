# Controller review v2

3 November 2026. **PASS for the revised controller code; final release-record verification remains separate.**

Controller SHA256: `bbb101c263c084c7bdffbc57f7d83c67f3cd838c47e942e18dba3103a0fa547a`. This version preserves the original blocking review and records its resolution. Review was read-only: no controller import, experiment, clinical fit, clinical table read or test run.

## Resolved before release

1. **Failure closure:** every reserved evaluation is protected by a per-slot `try/except/finally`; launch, JSON and native errors are retained. GLS errors have their own closure fields. An error does not trigger another native fit or prevent ordinary continuation to remaining fixed slots.
2. **Identity and receipt binding:** evaluation requires the exact six expected identities, current attempt hashes, reservation identities and release hash. Successful execution receipts match their recorded hash, candidate arm and fixed seed before outputs are used.
3. **Stale output prevention:** fresh unreserved evaluation rejects existing native/GLS/log artifacts. Native output must match the table SHA, and a nonzero native process cannot be credited as computed.

## Preserved controls

The native/Agent allocation and three fixed seeds still define exactly six generation attempts. Exclusive reservations retain failed/interrupted slots. All generation closes before evaluation, with no output-driven reauthoring or replacement. The native wrapper has a 300-second cap, the host command 325 seconds, and the independent GLS check 120 seconds. No automatic optimizer retry, refit or fallback execution was introduced.

## Nonblocking integration note

The GLS process return code and JSON status are both retained. The result collector must require **returncode 0 plus JSON status pass** when asserting independent numerical verification. Optionally the controller can explicitly relabel a nonzero/JSON-pass combination as `process_failed_with_partial_result`; the current checker normally returns zero only for pass.

## Release boundary

This pass covers the reviewed code bytes. Final release must separately bind source/task files, both frozen candidates, controller, native and independent evaluators, wrapper and runtime metadata. Existing reservations remain non-rerunnable. No actual experiment was run by this review.
