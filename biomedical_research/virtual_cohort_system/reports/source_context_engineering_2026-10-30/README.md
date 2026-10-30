# M12-A engineering record

All rows in `invented_fixture/` are artificial arithmetic fixtures. This folder contains no participant records or new target biomedical results.

- `pytest_output.txt`, `pytest.xml`: full suite, 384 passed and one Windows-privilege skip.
- `historical_compatibility.json`: byte preservation of 14 old engines and 228 M11 artifacts.
- `development_checks.json`: focused counts, review corrections and intermediate failures.
- `curated_verification.json`: verification of the copied fixture.
- `invented_fixture/`: task/domain declarations, frozen generator, actual isolated execution and source checks.
- `file_manifest.json`: SHA256 inventory, excluding itself.

Verify from the project root:

```powershell
python -m cohort_harness.source_replay_v2 verify --bundle reports/source_context_engineering_2026-10-30/invented_fixture --candidate candidates/initial --replay-id independent_source
```

For a new run on a configured WSL/bubblewrap installation, use `examples/m12_source_domain.py` as described in `docs/SOURCE_CONTEXT_V2.md`. Historical log paths identify the original machine. They are records, not a claim of a universally installed runtime. Verification can use the archived fixture without rerunning the generator while its pinned engine versions are available.

On Windows, use a short checkout or fixture location. Deeply nested export paths can exceed filesystem path limits even when the staged Git blobs are correct. The original curated fixture was verified successfully; a short reconstruction from staged Git blobs is also used for export verification. No frozen files are shortened or rewritten to work around this environment limit.

Source mean and slope agreement is deliberately hand-checkable arithmetic. It does not demonstrate biomedical usefulness or Agent performance.
