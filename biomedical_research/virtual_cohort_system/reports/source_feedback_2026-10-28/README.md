# Source-feedback review package

This package contains aggregate analyses, source diagnostics, Agent-authored code/specifications/evidence decisions and exact method/controller scripts for inspection. It contains no real or generated participant tables, source covariate tables, hidden outcomes, ID mapping, downloaded publication full text, caches or runtime dependencies.

See [the full results report](../../MILESTONE_3_RESULTS.md). Plot intervals are real survey confidence intervals or simulated-draw ranges, as labelled; the latter are not confidence intervals.

The postrun audit records the manifest as it existed before adding this README and the audit copy. That exact manifest is preserved as `curated_file_hashes_at_audit.json`; `curated_file_hashes.json` covers the completed review package. The underlying scientific results and candidate specimens did not change.

Candidate specimens under `candidates/` are authored-artifact copies, not complete executable frozen bundles. Referenced source files, covariate CSVs, original check receipts and freeze manifests remain in the local study workspace. They must not be mistaken for newly validated submissions. Decision records are preserved as written: statements that a generator had not run refer to submission time, before controller execution.

Scripts under `methods/` are review copies retaining original local-study layout assumptions and paths. This is not a one-command portable reproduction package. A future reproduction needs a new workspace, official public data, version checks and the expected layout. Do not bypass frozen inputs or isolated execution by importing an Agent generator on the host.

The reusable adapter and tests are in `cohort_harness/source_replay.py` and `tests/test_source_replay.py`. Scientific choices in these case specimens are not generic framework defaults. New cases need their own evidence and target-analysis protocols.

Sources: [Oh 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6911291.1/), [Bansal 2007](https://jamanetwork.com/journals/jama/fullarticle/208018), [CDC TRIGLY_J](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/TRIGLY_J.htm). Full-text artifacts and participant data remain outside this package; evidence records retain source locators and hashes.
