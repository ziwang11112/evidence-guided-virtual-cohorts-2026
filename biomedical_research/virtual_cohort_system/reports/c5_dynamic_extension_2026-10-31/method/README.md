# C5 variable-transition adapter

`adapter.py` is trusted plumbing around the unchanged `cohort_harness` contracts, lifecycle and execution APIs. It records an optional natural-language request together with an externally Agent-authored structured decision. It does not parse natural language, choose scientific formulas, infer missing evidence, select relationships, approve sources, or import a generator on the host.

## Controller and Agent inputs

The Agent decision has these exact fields:

```python
decision = {
    "schema_version": 1,
    "action": "extend",  # reuse | extend | new_population | revise | clarify
    "raw_request_sha256": adapter.request_digest(raw_request),
    "population": parent_task["population"],
    "row_id": parent_task["row_id"],
    "n_rows": parent_task["n_rows"],
    "requested_variables": prospective_native_column_definitions,
    "reason": "Agent rationale",
    "evidence_refs": ["approved_source_id"],
    "unresolved_evidence": ["Explicit remaining gap"],
}
```

`requested_variables` contains native task column objects, not names alone. For an extension it is the complete prospective output schema: every parent column in its original order, with identifier role retained and other old roles changed to `observed`, followed by new `generated` columns. All other old column attributes must match exactly. A reuse may request a subset, but each requested definition must exactly match its parent definition. Population, identifier and row count must match for reuse, extension and revision; population/row identity changes require `new_population` or `clarify`. The adapter compares the supplied population text exactly; scientific equivalence/applicability remains a controller/Agent judgment.

The controller supplies a separate authorization and pins its canonical digest before calling:

```python
authorization = {
    "schema_version": 1,
    "authorization_id": "controller-chosen-id",
    "destination": "new-transition",  # relative to the trusted workspace
    "max_extensions": 1,
    "parent": {"bundle": "parent-bundle", "run_id": "verified_run",
               "execution_sha256": parent_execution_file_sha256},
    "source": {"bundle": "approved-source-intake",
               "registry_sha256": approved_registry_file_sha256},
    "decision_sha256": adapter.digest(decision),
    "child_task_id": "explicit-new-task-id",
    "child_budget": {"source_queries": 0, "source_downloads": 0, "revisions": 0},
}
record = adapter.prepare_transition(
    workspace, authorization["destination"], raw_request=raw_request,
    decision=decision, authorization=authorization,
    authorization_sha256=adapter.digest(authorization))
```

`digest` hashes canonical JSON objects; `sha256` from the native lifecycle module hashes files. These are different commitment formats. Keep the expected authorization and subsequent `transition.json` file hash in the controller's record. Approval authority is procedural and external: an Agent must not author its own source approval or transition authorization.

The exact destination is bound to authorization and must not already exist. This admits one child at that destination, does not overwrite earlier work, and rejects overlap with source/parent directories. All referenced paths stay below the supplied trusted workspace; native path guards reject traversal, symlinks and Windows junctions. This is not a signature service or protection against an administrator changing all files and commitments.

## Result and execution

All five actions produce `raw_request.txt`, `agent_decision.json`, `authorization.json` and `transition.json`. `reuse`, `new_population`, `revise` and `clarify` are explicit routing records only: they do not create a child, mutate the parent or execute anything. A caller must handle the routed action explicitly.

Only `extend` creates `child/task.json`, `child/registry.json`, copied approved `child/sources/` artifacts and `child/observed.csv`. The parent must pass `verify_execution` **and** have status `success`; an intact failed receipt is insufficient. Parent output CSV bytes are copied exactly, and native input validation checks the enrichment schema. `input_provenance.json` binds parent/output/input hashes and identifies synthetic columns. Its `observed` role means fixed input, not a real patient measurement. Unknown parent input origins stay unknown; completion inputs distinguish original preserved cells from synthetic fills using zero-based row positions. No claimed real-patient provenance is invented.

The new task is an explicitly authorized extension, not a revision of the old candidate. It does not consume or reset the parent's revision index. C5 is sealed to already admitted fixture evidence and explicitly zero task budgets. This C5 policy is not a method-wide retrieval prohibition: the existing literature adapter still supports retrieval for separately authorized tasks with a fixed session and global accounting. This small adapter intentionally does not create a replacement session or solve cross-task retrieval accounting.

The Agent then independently authors the native candidate evidence/model/generator/check artifacts under `child/candidates/<name>/`, and the controller freezes it with the unchanged native lifecycle. Scientific packet fields use the native schemas; this adapter adds no scientific parameters.

```python
pin = sha256(workspace / "new-transition/transition.json")
adapter.verify_transition(workspace, "new-transition", transition_sha256=pin)
report = adapter.execute_extension(
    workspace, "new-transition", transition_sha256=pin,
    candidate="candidates/initial", run_id="new_run", seed=17)
adapter.verify_preservation(workspace, "new-transition", "new_run", transition_sha256=pin)
```

Execution uses only the native fixed WSL/bubblewrap backend, requires a frozen generator route and accepts only native resource-limit options. There is no runtime substitution or local fallback. Failed native execution receipts remain intact. A separate `preservation/<run_id>.json` report is written outside the native execution directory so it does not invalidate native artifact hashes. Verification recomputes that report from the verified execution and native `validate_output`, checking old cells, row identity/order, row count and schema. `preservation_status: not_verified` on a failed run is not a diagnosis that every old value changed. Success establishes contract preservation, not scientific validity or isolation of the calling Agent's tools.

## Focused tests

`test_adapter.py` uses three explicitly invented `subject_id, x1, x2` rows, then an `x3` extension. Parent direct-row execution is real native validation without generated-code execution; child backend calls are mocked. Tests cover action routing, raw-request binding without parsing, definitions/units/population/row changes, hash tampering, path safety, source approval references, budget refusal, failed parent rejection, exact synthetic input copying, completion provenance, preservation failures, failed execution, report recomputation and unavailable-backend behavior. A generator containing a top-level exception ensures no host import occurs. These tests prove plumbing behavior, not biomedical validity or actual sandbox operation.

Run from the harness project root using a **new** explicit temporary directory each time:

```text
python -B -m pytest work/c5/method/test_adapter.py -q -p no:cacheprovider --basetemp work/c5/method/NEW_TEMP_NAME --junitxml work/c5/method/NEW_RECEIPT.xml
```

The first recorded invocation (`test_receipt_t01.xml`) failed in fixture setup because its requested temporary parent directory did not exist; no tests ran. `test_receipt_t02.xml` records the first 35 passing cases. The later receipt includes the additional provenance and raw-request tests. Test directories and receipts are retained, with no old harness, data, source or result files changed.
