# Corrected inherited-source setup review

Status: ready for fresh session creation. No remaining setup-code blocker was found. After creation, run the actual controller status/verification before returning control to the author. This review does not claim that the not-yet-created session has passed that check.

The failed `evcUseR01` setup remains preserved: all 53 files in its failure receipt still match their recorded hashes, no additional files were present, and there were zero controller events, candidate freezes or executions. The failure receipt SHA-256 is `8737828d9780889a8e454562611f69cbdc429fa583366d4837b2a4ce0fff856d`. The previous readiness review did not exercise fresh-session status and missed this setup invariant.

## Cause and correction

`web_evidence_v1` reserves `sources/web_evidence_v1/` for artifacts covered by that session's own approved retrieval registrations. Marking inherited entries as curator inputs does not satisfy that invariant. The adapter exposes initialization, fetch and verification, without a supported historical-import operation. Preserving historical sources in a distinct curated namespace is therefore appropriate; inventing current retrieval registrations would not be.

The fresh `evcUseR02` registry has the same 14 entries, source IDs, hashes, origins and approval labels. Its only registry changes are three paths from `sources/web_evidence_v1/` to `sources/curated/inherited_web_v1/`, all for `PTS_CardioChek_measurement`:

| Artifact suffix | SHA-256 (also the filename stem) |
|---|---|
| `.raw` | `54a2dd6d31deff9c968621b037ef994ae4a7519dfb8323f0b1f804bbbdb1e4d0` |
| `.txt` | `87d2ba6a6d90406f9a8fe6d89199929075b272ddaeb29a7774867be5d5b7a167` |
| `.json` | `a06c6e094c0922b20a77595d9058bf98448370b016fa9368f783089755bb117a` |

All 14 inherited source files are byte-identical. Historical manifests remain historical provenance, including any original locations within their unchanged bytes; they are not current-session approval records. `lifecycle._registry` accepted the new registry. The fresh bundle contained neither web state nor controller state at review time.

## Exact baseline and configuration differences

Recursive JSON comparison found only these baseline semantic changes:

- `evidence.json`: `sources[4].artifacts[0].path` and `sources[4].artifacts[1].path` relocate the text and manifest above. Its hash changes from `c46ebdf0fccc85c3b2437c2e3cbba616f7600baaf192da06625e9ee95d941bc7` to `86531931309abadbdea1ce4fc97c08186ab190cad5b696bfadc24947dbd60b06`.
- `source_semantics_v1.json`: only `evidence_sha256` changes to that new evidence hash; file hash becomes `eb6a06f643bed15cb65881532cf0077b9ad8a353efa54cbf994642ea986040bf`.
- `descriptive_feedback_v1.json`: only `evidence_sha256` changes to that new evidence hash; file hash becomes `0b6c9503b6c2744914f8d9d4784122fa6586754ce66e58ead501d009ff1592b9`.

The other six committed baseline files are byte-identical, including generator `622cb18b6225832ae754812ae80477a5783958603da1e8e2470202a046a655ef` and model specification `e469f7075314cce63ac9a3b1fb3d961c2770f96d9680e844bab43ad2abd36fa7`. No source statistics, assumptions or scientific law changed. The current commitments exactly agree across the rebinding record, baseline commitment file and protocol.

Task, request, use contract, interpretation note and rule basis are byte-identical between the two setups. The six inspected reporting/adapter/rule-basis work copies are also byte-identical. All seven configured module/dependency files exist and match their hashes. Both adapter paths use the corrected work directory; the contract dependency uses `evcUseR02`. Shared historical provider-code paths are intentional and unchanged. No stale failed-bundle/work path was found in the new config, adapter bridges or scanned fresh-bundle JSON/Markdown/Python files.

The author task accurately describes six unchanged baseline files and three provenance-only rebindings. It preserves the two-stage/three-seed limits, exact requested analyses, explicit concentration interpretation, author scientific freedom and prohibition on target comparison. Its session-exists sentence becomes true when the host completes the pending creation.

## Verification and limits

Inspected the two-case invented-source regression: a fresh web session rejects an inherited artifact in its reserved namespace, while the identical artifact in the curated namespace verifies with zero downloads and empty retrieval/registration history. The root reports both cases passed. No additional suite rerun was needed for this namespace-only setup correction. A future broader startup test can create a temporary controller session around such curated input and assert its first status succeeds; it must still reject the reserved-namespace variant.

Also inspected `start_session.py`: it requires this review's exact ready status and an empty `remaining_blockers` list, writes an exclusive finite design lock and initial-input inventory, creates the session, then calls `verify_session`. It records the verification result before declaring author readiness. Thus a verification exception cannot produce the ready state. Creation or verification failure leaves its receipts for diagnosis; the script does not silently reset or reuse a partially created session. Its two review-schema checks were aligned during review. The actual fresh-session invocation remains the host's next action.

This was a setup and provenance review. It did not run a clinical generator, read individual tables or target outcomes, evaluate scientific improvements, or alter engines, the failed bundle, prior reports or locks. Current-use author sidecars still require their own preflight in the new bundle; historical draft sidecars were preserved in the failed setup and were not silently imported.
