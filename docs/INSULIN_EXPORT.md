# Insulin enrichment export and reproduction boundary

The completed pilot is under `biomedical_research/insulin_feature_enrichment_2026-10-27/`. The export contains 66 exact reviewed files: protocol and interface documents, public-source acquisition and parser-repair code, the clean Agent's external-study ledger and generator, construction and evaluator code, artificial-fixture tests, metadata-only commitments, all final aggregate results, and independent audit records. The four CSV files contain 168 endpoint summaries, 8 draw summaries, 8 scientific-interpretation rows, and 168 independently recomputed endpoints. The PNG and PDF show aggregate effects and uncertainty summaries only.

No observed, reference, linkage, survey-design-spine or enriched participant table is exported. Source XPTs, original paper/codebook downloads, approved search response artifacts and fulltexts, the quarantined initial search context, credentials, runtime files and caches are omitted. The clean search log records queries and retrieval metadata, without search-response snippets. The redacted `review/INCIDENTS.md` preserves the stopped search, parser repair and other preparation failures. The executed construction is in `agent_clean/`; the source README's general `agent/` description does not imply that the quarantined directory is exported.

## Integrity and transformations

The source `delivery_manifest.json` seals 49 final code and aggregate artifacts. Its SHA256 is `584ed8bb43b47a0966570671dfdaa308d6837a395519a45e30257e06863aa40b`. All 49 source commitments were checked during export. The original outputs-freeze source SHA256 remains `aee9d3b44df52b59a754cdcfd88629eddf414f4e8b2c7e23c4ce102ba271f4c4`.

Seven files have explicit, non-scientific path transformations:

- `agent_clean/SEARCH_LOG.md` and `review/GATEWAY_REVIEW.md`: replace the local Python executable path with `python`.
- `review/initial_source_code_checks.json`, `runs/initial_v1/pre_execution.json`, `runs/initial_v1/execution.json`, `freeze_v1/outputs_freeze.json`, and `freeze_v1/evaluation_manifest.json`: normalize workspace paths and dictionary keys to repository-relative paths.

Their original source digests remain in scientific freeze/delivery records. `sync/EXPORT_MANIFEST.json` and `sync/INSULIN_EXPORT_RECEIPT.json` bind each source digest to its exported digest. Hash verification of a transformed artifact must use that mapping; comparing its exported bytes directly with an original freeze hash is expected to differ. Omitted data-file names and opaque digests remain as provenance metadata; the export auditor never follows those entries to open participant files.

The source `review/postrun/report_v3_checks.json` records a RESULTS.md snapshot from its review time. Subsequent link/readability-only prose updates are sealed by the final delivery manifest. Both records are preserved. Report versions 1 and 2 are omitted; the final version 3 report and audit prose retain their layout and labeling history. The eight numerical endpoints and frozen evaluation were not changed by those reporting revisions.

Original Stage 1 artifacts, its delivery manifest and `sync/CURRENT_SCOPE_REVISION.json` are unchanged. `sync/INSULIN_PILOT_REVISION.json` records only the later framework README revision linking this pilot.

## What can be reproduced from this checkout

The final numerical evaluation, interpretation tables, code, parameters and audit outcomes can be inspected directly. Export verification is `python -B sync/audit_export.py`; it checks file identities, exact inventory, aggregate schemas, the original and transformed commitment mappings, and recorded draw/fit/endpoint accounting. It does not rerun the scientific evaluation or the independent numerical audit. The 4,237 passing checks are the recorded original independent audit, not newly executed study analyses in this export.

Full clinical replay requires separately obtained public inputs and the local data preparation/provenance structure. `custodian/source_manifest.json` records official CDC URLs and source hashes; `custodian/acquire_sources.py`, `build_packet.py`, `verify_and_adapt.py`, and `parser_repair.md` document acquisition, eligibility, the XPT zero-conversion repair, and the evaluator adapter. Their local workflow uses `custodian/raw/` for XPTs, `custodian/documentation/` for official documentation, `custodian/locked/` for the reference/design/linkage and metadata, `shared/observed.csv` for visible covariates, and `runs/initial_v1/` for enriched tables. These data and download directories are intentionally absent here.

A newly built packet has new random pseudonyms and newly recorded commitments. Exact replay of the original frozen run needs the separately retained original packet, mappings and outputs; this checkout alone cannot recreate those original identities or hashes. Preserve the failed initial parser as historical code, rather than executing it as the current packet builder.

The source/role audit scripts also require the omitted approved literature artifacts; the final report verification script expects omitted historical report_v2 files. Do not run original source scripts over the archived export expecting a self-contained replay or overwrite existing frozen reports. Any future experiment needs new versioned outputs and a separate reviewed allowlist.
