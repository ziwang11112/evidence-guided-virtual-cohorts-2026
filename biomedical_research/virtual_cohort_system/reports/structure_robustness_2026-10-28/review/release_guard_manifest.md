# Release guard manifest requirements

Entrypoint: `release_guard.verify_release(commitment_path: Path) -> dict`. The custodian must hash-verify the guard before importing it and call it before reading the hidden outcome table. Passing returns `status: "passed"`, counts of six candidate freezes, eighteen source replays, fifteen target outputs, and audit hashes. Errors fail closed. The guard does not run a generator or fit any target analysis.

The guard lives at the experiment root. It derives all paths from its own location and the release manifest location, without a machine-specific root. Manifest paths may be absolute or relative to the manifest directory, but they must resolve to the specified experiment artifacts. Links, junctions, path traversal, alternate bundles, and alternate artifact locations are rejected.

## Independent anchor

`protocol_commitment.json` must sit beside `release_guard.py` and contain:

```json
{
  "schema_version": 1,
  "kind": "structure_robustness_protocol_commitment",
  "created_utc": "UTC ISO-8601 timestamp",
  "files": {
    "protocol.json": "lowercase SHA-256",
    "release_guard.py": "lowercase SHA-256"
  }
}
```

Additional file bindings, such as `structure_plan.json`, are allowed under `files` and are verified. They must remain inside the experiment. This anchor is read from its fixed location, not supplied or redefined by the release manifest.

`protocol.json` must contain `structures: ["s1", "s2", "s3"]`, three unique integer `source_seeds`, five unique integer `target_seeds`, and `source_feedback_round_max: 1`. Source and target schedules must be disjoint. Extra scientific protocol fields are allowed. The agreed experiment schedules are 76101–76103 and 76201–76205; the separately committed protocol supplies their values to the guard.

## Release manifest

Required fields:

- `authorize_target_evaluation: true` and `all_structures_and_seeds_committed: true`.
- `custodian_lock_sha256`: lowercase SHA-256. The custodian verifies the actual lock; this guard checks digest syntax.
- `structures` and `seeds`: identical, in order, to protocol structures and target seeds.
- `bundle_path`: resolves exactly to the experiment's `agent_bundle` directory.
- `experiment_protocol: {path, sha256}`: the experiment's `protocol.json`.
- `controller_guard: {path, sha256, function: "verify_release"}`: this guard file.
- `builder_observed: {path, sha256}`: `agent_bundle/observed.csv`.
- `candidate_commitments`: all six unique records `{structure, stage, candidate_name, path, sha256}`. Stages are `initial` and `final`; names are `<structure>_<stage>`; paths point to the corresponding `candidates/<name>/freeze.json`.
- `source_replays`: all eighteen unique records `{structure, stage, replay_id, seed}`. Replay IDs are distinct simple portable names. The guard derives report paths under the single bundle.
- `outputs`: all fifteen unique final records `{structure, seed, path, sha256, run_id, candidate_name}`. Candidate names are `<structure>_final`; run IDs are distinct simple portable names. Paths must point to `agent_bundle/executions/<run_id>/output/generated.csv`.

Every candidate must be a verified program submission. Each initial has no parent and revision index zero. Each final has its corresponding initial parent and revision index one. The task revision budget must be one. All candidates must share exact evidence and source recipe bytes and identical definitions for the assumptions used in source contexts/checks. Candidate models can otherwise differ.

The guard invokes the actual harness candidate, execution, and source-replay verifiers. It additionally checks successful program status, exact candidate and seed binding, output digest agreement with execution receipts, and complete grids. Source report child paths and protocol/candidate/receipt timestamps are checked. All initial freezes precede every initial source execution; all initial source reports precede every final freeze; all final freezes precede every final source execution; all final source reports precede target generation.

These checks enforce the retained procedural record. They do not authenticate the host, prove external chronology, isolate outer Agent tools, choose a scientific winner, or calibrate synthetic uncertainty.
