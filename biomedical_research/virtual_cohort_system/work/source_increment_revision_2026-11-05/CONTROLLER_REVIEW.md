# Controller mechanics review

Status: accepted for the currently implemented three first-attempt slots, subject to the separate scientific candidate review. The focused local checks passed. This is not a generator execution result, scientific acceptance, sandbox availability certification, or independent numerical result review.

The reviewer read `run_unit.py`, updated `prepare_bundle.py`, and `PROTOCOL_CLARIFICATION_01.md`. Only `test_run_unit_guards.py` and this review were written in this pass. Controller fixes were reported to the root, who owns and edited those scripts. No generator or real evaluator was launched, no source was downloaded, and no target file, participant row, or generated row was parsed. All test writes were temporary fixtures under this unit directory; cleanup targets were resolved and confirmed beneath it. Existing harness tests were not rerun.

## Fixes requested and inspected

1. Require a native integer scheduled seed before any I/O. Membership alone admitted `5301.0` by Python's numeric equality. The root added `type(seed) is int` and kept the exact schedule.
2. Verify the complete new closure before any reference file access. The earlier implementation trusted a `scientific_authoring_closed` flag without checking exact scheduled slots or all committed artifacts. The root added `verify_commit()`, `verified_run()`, and `verify_closed_unit()`, checking three ordered unique scheduled slots, exact run IDs, candidate/route/seed/freeze identity, reservation/result hashes and identities, attempt count, receipt bytes, table bytes, and frozen controller/protocol/clarification/review commitments.
3. Require the adapter's verified receipt to identify the requested candidate, seed, generator route, and freeze. These checks now run during execution verification and closure/evaluation verification. Successful generator identity is also enforced inside the reused `execution.verify_execution` implementation.
4. Preserve all scheduled analyses when a source-feedback or generated-provider step raises. The root added per-slot error records and unavailable endpoint payloads, while leaving provenance-binding failures as hard failures. This branch was inspected statically; the focused tests below deliberately stop before actual reference access and do not run numerical evaluation.

The initial duplicate-reservation behavior was already correct: exclusive reservation creation happens before adapter invocation. The adapter's actual output layout is `executions/<run_id>/execution.json` and `executions/<run_id>/output/generated.csv`, matching the controller.

## Focused fixture tests

Command, run from this directory:

```powershell
python -B -m unittest test_run_unit_guards -v
```

Result: **13 tests passed**, reported duration 0.106 seconds. Tests cover:

* Missing/open, incomplete, and duplicate-seed closures reject before any reference read or hash.
* A complete artificial three-slot closure passes its mechanical checks and reaches only a deliberately failing reference-hash sentinel. It never opens or parses a real or fixture reference.
* A changed closed result is rejected before reference access.
* Unscheduled seeds, floats, strings, Booleans, and NumPy integer scalar inputs are rejected before file I/O; native scheduled integers are accepted.
* A duplicate reservation cannot invoke the mocked adapter a second time.
* Wrong-candidate and wrong-seed execution receipts are rejected.
* Receipt/table paths and their byte hashes match the controller's recorded paths. Table files contain only inert marker text, never rows, and are never parsed.
* NumPy real scalar endpoint values are accepted and normalized to native floats; legitimate unavailable values are accepted. Boolean, nonfinite, and string values are rejected.
* Missing, duplicate, unexpected, or wrong-unit endpoints are rejected.
* `inspect.signature(...).bind(...)` confirms that the actual lower-level freeze, execution, verification, semantic preflight/collection/verification entry points accept the controller's planned arguments. No such adapter function was executed against the real bundle.

## Preparation and clarification review

`prepare_bundle.py` now sets administrative `revisions: 2`; source-query and source-download budgets remain zero and scientific task fields remain copied from E01. This permits the underlying immutable lineage to express two potential mechanical versions, without authorizing a second scientific law. The new source registry uses the expected exact schema and curator admission under the same source ID. The script has no reference or patient-data reader.

`PROTOCOL_CLARIFICATION_01.md` preserves the original protocol and manifest and explicitly acknowledges that the static recipes/source-only probe records could already have been read. It does not recast the expanded file list as the original pre-access boundary. This resolves the earlier documentation mismatch prospectively and transparently; this mechanics reviewer did not inspect those scientific files' contents in this review.

The current `run_unit.py` supports **only three first attempts**, one per scheduled seed. It does not implement retries or the optional two mechanical repairs. The root explicitly chose this stricter initial implementation. A failed slot can remain failed and be reported. A repair would need a separately reviewed immutable controller extension and equivalence decision before target access; no repair can be inferred from the administrative task allowance alone. Do not change this frozen controller silently to add a retry.

## Reviewed artifact identities

SHA256 hashes recorded immediately after the successful focused run:

| Artifact | SHA256 |
| --- | --- |
| `run_unit.py` | `0042fc4c0902600225f7da856056538c89d02281ee8942215073eec328b51789` |
| `prepare_bundle.py` | `42fb3beee552dc9b8ab49c9f49eae60ee965a12174134a882d61c1965aeb03d4` |
| `PROTOCOL_CLARIFICATION_01.md` | `0c90dc2616814ceb025663130dd98645ac19d5556372b7c65ec378646c9d5564` |
| `test_run_unit_guards.py` | `bb90d39ffc38f8b40038916bfc8b3768949e3e49c5f75c39f49731ae8c3cd3b5` |

Remaining validation belongs to the authorized actual run: candidate/source scientific review, static candidate contract/preflight, adapter runtime launch and receipts, then generated-only evaluation and independent recalculation after closure. The fixture tests do not substitute for these stages.
