# M12-C invented actual-Agent integration archive

30 October 2026. All data are invented. There are no patient records, real study claims or hidden target outcomes in this archive.

`run/` is a complete portable bundle containing:

- `sources/` and `allowed_inputs/`: two admitted study summaries, source covariates and fixed controller settings, prepared before Agent construction. No generator formula was supplied.
- `agent_exchange/`: initial-input hashes, actual construction request and response, a schema-only interface amendment, receipt of Agent files, later source-review request/response/decision, dispatch records and completion summary.
- `candidates/initial/`: the actual scientific Agent's frozen generator, specification, source recipes, proposed calibration plan and pre-execution checks.
- `cal/initial_fit/`: the one evaluated initial vector, all eight actual isolated source executions, verified statistics, pre-replay selection and completed result. No parameter change occurred.
- `calibration_budget/`: the original permanent numerical reservation ledger; unused reserved capacity is not refunded.
- `scientific_loop/`: the fixed review/promotion allowance and request → decision → promotion reservation → finish event chain.
- `candidates/source_reviewed/`: the promoted development candidate with exact selected generator/specification bytes, source feedback and scientific decision. It is not a target release.

`summary.json` gives the measured outcomes. The Agent retained its structure after a fit discrepancy of 0.0040170478 and separately scheduled replay discrepancy of 0.0020033815, under the predetermined engineering tolerance 0.04. These are source-fit diagnostics, not biomedical accuracy or independent-population validation. Shared seeds correlate simulated errors across the two equal-sized contexts.

`integration_audit.json` independently recomputes all eight generated tables and verifies promotion, lineage and budgets. `pytest.xml` and `pytest_output.txt` retain 502 passes and two Windows symbolic-link privilege skips. Unit tests that mock execution are distinct from the real runs in this bundle.

`historical_preservation.json` checks all earlier engine bytes and M11/M12-A/M12-B curated manifests. `file_manifest.json` binds the complete archive except itself. `curation_script.py` is copied from `work/m12c/package.py` and retains the original source-location assumptions; it is an archival record, not a relocatable entry point.

Verify the bundle using the preserved project engines with `scientific_loop.verify_loop(bundle)` and `calibration.verify_calibration(bundle, "initial_fit")`. On Windows, deeply nested Git checkouts can require extended-length copy paths and `git -c core.longpaths=true`; these do not change frozen relative paths or file bytes.

Only the retention/promotion branch was demonstrated by the actual Agent. Automatic literature retrieval and structural revision are not provided by the new controller. The source-only result leaves target transport, nonlinear shape, residual distribution and scientific analysis utility unvalidated.
