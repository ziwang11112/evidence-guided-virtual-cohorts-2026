# Finite publication allowlist draft

9 November 2026. Draft only: no transport, mirror mutation, upload or remote access. Author quality and results are unknown. Every destination is under `biomedical_research/virtual_cohort_system/`; local `work/` maps to public `reports/`. The JSON companion enumerates each exact source/destination and currently observed source hashes.

The clean local mirror currently points to `2d20ec13e6edb1f67bc7230eeeb3de56bbf73382`. This is not a remote freshness claim. Any later authorized publication must check the then-current local and remote head; the old exporter's fixed parent must not be reused.

## Existing original files

- `cohort_harness/adaptive_session_v2.py`
- `cohort_harness/descriptive_feedback_v1.py`
- `cohort_harness/web_evidence_v1.py`
- `docs/ADAPTIVE_SESSION_V2.md`
- `docs/DESCRIPTIVE_FEEDBACK_V1.md`
- `docs/WEB_EVIDENCE_V1.md`
- `tests/test_adaptive_session_v2.py`
- `tests/test_descriptive_feedback_v1.py`
- `tests/test_web_evidence_v1.py`
- `work/adaptive_evidence_loop_2026-11-09/prepare.py`
- `work/adaptive_evidence_loop_2026-11-09/generated_analysis.py`
- `work/adaptive_evidence_loop_2026-11-09/close_author.py`
- `work/adaptive_evidence_loop_2026-11-09/evaluate.py`
- `work/adaptive_evidence_loop_2026-11-09/independent_recompute.py`
- `work/adaptive_evidence_loop_2026-11-09/test_evaluate.py`
- `work/adaptive_evidence_loop_2026-11-09/test_generated_analysis.py`
- `work/adaptive_evidence_loop_2026-11-09/EVALUATION_PLAN.md`
- `work/adaptive_evidence_loop_2026-11-09/PROTOCOL_REVIEW_DRAFT.md`
- `work/adaptive_evidence_loop_2026-11-09/IMPLEMENTATION_REPORT.json`
- `work/adaptive_evidence_loop_2026-11-09/IMPLEMENTATION_REVIEW.md`
- `work/adaptive_evidence_loop_2026-11-09/IMPLEMENTATION_REVIEW.json`
- `work/adaptive_evidence_loop_2026-11-09/DESIGN_LOCK.json`
- `work/retrieval_validation_analysis_2026-11-09/LOCAL_CHECK_AUDIT.md`
- `work/retrieval_validation_analysis_2026-11-09/OFFICIAL_KNOWLEDGE.md`
- `work/retrieval_validation_analysis_2026-11-09/PUBLISHED_VALIDATION_PATTERNS.md`
- `work/retrieval_validation_analysis_2026-11-09/RECOMMENDATIONS.md`

## Planned aggregate results

Each exact name below is conditional on creation after author closure and final content review. Missing files are reported, not replaced by a directory scan.
- `work/adaptive_evidence_loop_2026-11-09/EVALUATION.json`
- `work/adaptive_evidence_loop_2026-11-09/EVALUATION.md`
- `work/adaptive_evidence_loop_2026-11-09/RECOMPUTATION.json`
- `work/adaptive_evidence_loop_2026-11-09/RESULTS.md`
- `work/adaptive_evidence_loop_2026-11-09/ACTION_SUMMARY.json`
- `work/adaptive_evidence_loop_2026-11-09/SOURCE_REVIEW.json`
- `work/adaptive_evidence_loop_2026-11-09/SOURCE_REVIEW.md`
- `work/adaptive_evidence_loop_2026-11-09/INDEPENDENT_RESULT_REVIEW.json`
- `work/adaptive_evidence_loop_2026-11-09/INDEPENDENT_RESULT_REVIEW.md`
- `work/adaptive_evidence_loop_2026-11-09/scientific_analyses.png`
- `work/adaptive_evidence_loop_2026-11-09/scientific_analyses.pdf`

## Derived public metadata

These must be created from restricted fields; the original private records are excluded.
- `PROTOCOL_PUBLIC.json`: Selected protocol fields for case/purpose/mode/rows/seeds/budgets/analyses/diagnostics/limitations; replace local bundle path with neutral bundle label; no target estimates.
- `AUTHOR_CLOSED_PUBLIC.json`: Status, selected candidate name, stage names, run IDs and candidate/seed slots only; omit private file inventory and local absolute paths.
- `ACQUISITION_METADATA.json`: Bibliographic identifiers, public source URLs, artifact hashes/formats and actual aggregate retrieval costs; no source bodies, snippets, raw responses, local source paths, or raw discovery log.
- `PUBLICATION_MANIFEST.json`: Fresh base commit plus local/public hashes and exact file mappings for the reviewed export.
- `PUBLICATION_QA.json`: Checks actually performed on that export, exclusions and limits; no retrospective claim that this draft approved unseen results.

## Exclusions and review boundary

No bundle copy, generated/real rows (including inline JSON), full-text papers, abstracts, source tables/images, raw gateway or session responses, raw discovery logs, credentials, environment files, or private bundle inventories. Candidate artifacts are excluded from this small initial scope because they are not yet known or reviewed. Historical files and README edits require an explicit new allowlist entry.

Final export must inspect the actual bytes, preserve code commitments, map any transformed metadata to its local/public hash, resolve Markdown links, and verify figures contain aggregate output only. Research-note summaries remain original prose with primary-source links; no source content is embedded. A manifest and QA report must describe checks actually performed. The draft does not approve scientific conclusions or publish unseen future artifacts.

## Explicit exporter extension

The additive exporter also includes exactly `prepare_public.py`, `test_prepare_public.py`, `plot_results.py`, `summarize_actions.py`, `compare_previous.py`, `EXPORTER_REVIEW.md`, `EXPORTER_REVIEW.json`, and postclosure `PREVIOUS_COMPARISON.json`. It requires all final files rather than skipping missing results. The exporter review is fixture-based implementation evidence, not evaluation of author quality. No candidate artifacts were added.
