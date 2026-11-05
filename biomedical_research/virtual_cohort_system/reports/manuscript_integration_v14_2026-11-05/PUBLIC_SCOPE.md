This release includes all 380 exact experiment/interface/code/provenance candidates, including complete optional session-chain and aggregate-feedback groups, plus the reviewed v0.14 manuscript package and navigation. It excludes all individual records and third-party originals. The final staged manifest and independent release review bind public bytes; this document alone is not a remote sync receipt.

# Public release scope: manuscript v0.14 and the completed cross-task experiment

This is a release-scope recommendation, not a publishing receipt or final approval. No Git object/ref was written and no experiment, generator, evaluator or test was run for this audit. No real/generated individual row table, full third-party original, codebook or gateway credential/config was opened. The two audit deliverables are this file and `SAFE_EXPORT_CANDIDATES.json`.

The v0.13 receipt records published commit `e923fab06ee02d9a00e890fa3599c9d49f624026` and 62 byte-verified files. The current export checkout is `3ceafd0d8b4755e662cc9d524dd73286629a24b6`; the parent independently confirmed the same remote head. The v0.13 exporter is useful as a review-gated pattern, but its old base SHA and manuscript-only allowlist must not be reused unchanged.

## Exact release boundary

`SAFE_EXPORT_CANDIDATES.json` is the exact file-level candidate allowlist. Every entry records local source, proposed public destination, original SHA-256, byte count, group and whether it is required for this recommended scope. It contains 380 files (284 required, 96 optional lineage/feedback records). It does not authorize recursive directory export. Its hashes describe bytes read in this audit; final publication must rehash the exact staged bytes and record every permitted Markdown navigation change separately.

Map `work/evidence_use_cross_task_2026-11-05/<path>` to `reports/evidence_use_cross_task_2026-11-05/<path>` under `biomedical_research/virtual_cohort_system/`. Map each workspace-root `evcUse{H01,H02,H03,L01,L02,L03}` bundle to `reports/evidence_use_cross_task_2026-11-05/authors/<author>/`, preserving `candidates/initial/` and its `checks/` subdirectory. Do not flatten the candidate: its evidence-use sidecar binds `task.json`, `candidates/initial/...` and exact bound check artifacts. Source filenames/hashes in provenance remain historical pointers; they do not cause the referenced contents to be exported.

The required groups contain:

- New evidence-use implementation, documentation and tests, with the evidence-action implementation/test fixtures required for test import.
- Frozen protocol, endpoint contract, closure, completion, source/technical reviews, all completed aggregate results, both audit-attempt outcome records and the corrected complete independent endpoint reconstruction.
- Original controller, runner, generated-only provider, evaluator, preparation/derivation/reporting scripts and their original tests. These are archived implementation evidence, with the portability limits below.
- Seven exact constructor interface snapshots, two metadata profiles, the lipid task metadata/admission record and exactly three original curator fact extractions. The 67-kB Greiner extraction is structured source statistics/definitions and original qualifications, not a copied article or supplement. All source originals remain excluded.
- All six authors' original task/request/instructions, source proposals and choices, source-ID/hash registry, extracted evidence facts, executable generator, model specification, analysis-evidence/evidence-use declarations, semantics, feedback definition, decisions, freeze, and exactly the check artifacts named by `checks.json`.
- Original experimental PNG/SVG figures and their layout review, the cross-task manuscript insert, and the new portable aggregate-only plotting entry point.

Optional groups retain each complete 12-event session hash chain, its contract/input commitments and initial aggregate feedback, plus each original semantic-feedback aggregate report. If omitted, document that the public package offers selected provenance rather than a complete local session-chain audit. Never select individual favorable events or authors.

## New code required in the public tree

The current public checkout lacks all six paths below. Publishing only v0.14 prose and figures would leave the new implementation and test imports missing:

- `cohort_harness/evidence_use_v1.py`
- `cohort_harness/evidence_actions_v1.py`
- `tests/test_evidence_use_v1.py`
- `tests/test_evidence_use_controller.py`
- `tests/test_evidence_actions_v1.py`
- `docs/EVIDENCE_USE_V1.md`

The evidence-use tests import `routing_inputs` from `test_evidence_actions_v1.py`; that file imports `cohort_harness.evidence_actions_v1`. Including these dependencies does not mean the action planner performed the six constructions. The published constructor interface snapshot describes the planner separately. The full current `docs/EVIDENCE_ACTIONS_V1.md` is not in this exact scope because its later historical links target other unpublished work; export it only with separately resolved/allowlisted dependencies, without deleting scientific references merely to satisfy a link checker.

Also publish `controller_evidence_use.py`, `runner.py`, `lipid_provider.py`, `evaluator.py`, the original review/test/derivation code and all six frozen author `generator.py` files in the explicit inventory. Existing harness Python files otherwise match the public checkout byte-for-byte. Two unrelated changed CHNS test files are outside this release scope.

## Reproducibility: what the package supports

The new `manuscript/paper_figures_v14_2026-11-05/render_cross_task_aggregates.py` is the portable plot entry. It takes explicit `--results` and `--out`, verifies aggregate RESULTS SHA-256 `8cb8a5107181ca462d80ea38152420512052d7daf15ede7ddb8ddf8d57d95672`, and has no harness import or row-data dependency. Final reproduction/visual review is the parent's gate. The historical `report_results.py` is not this portable entry: it calls `runner.closure_gate()` and uses original author/gateway/session paths.

Frozen controllers, test source and provider code retain original `work/` and absolute Windows/WSL layout assumptions. For example, the loader test imports from `work/evidence_use_cross_task_2026-11-05`, and the lipid provider loads `work/scaleup_2026-11-01/analysis/k02_analysis.py`. A public scientific rerun therefore requires explicit path/layout mapping, the original runtime dependencies, separately authorized source acquisition and the protected source-admission material. This audit does not patch archived code or claim that the unmodified exported tests run in a clean checkout.

The existing public tree already contains byte-identical `reports/main_study_freeze_2026-11-03/cases/ENSANUT2018/generated_feedback.py`, `reports/scaleup_2026-11-01/analysis/k02_analysis.py`, and `reports/autonomous_research_cycle2_2026-10-31/analysis/analytical_engine.py`. Keep these as pinned dependencies rather than copying third-party or raw inputs. The package permits inspection of all six constructions and aggregate arithmetic, and portable reproduction of the new plots. It does not provide independent clinical reproduction, full source-byte freeze verification, complete Agent contexts or participant-level data.

## Aggregate and binding checks performed

`evaluation/ALL_ENDPOINTS.csv` has 513 endpoint rows; `PRIMARY_SUMMARY.csv` has 18 author/analysis rows; the corrected independent endpoint CSV has 513 endpoint rows. Their fields identify author/case/seed/category/endpoint and numerical summaries. They do not contain subject-level rows. Author names H01–H03/L01–L03 and seeds are construction identifiers, not patient identifiers.

The six `checks.json` files bind 35 auxiliary artifacts: H01 15, H02 4, H03 6, L01 4, L02 2 and L03 4. All current auxiliary hashes matched. The candidate scan found no credential-token/private-key patterns, copied article markup or arrays matching the screened individual age/BMI record schema. These are supplemental checks of specifically named file classes; JSON extension alone is never evidence that a file is safe.

The final independent numerical review reports 18 final tables, 24 physical attempts, 513 reconstructed outputs, 324 available reference comparisons and 189 generated-only diagnostics. The first audit parser failure and its correction remain visible; neither a participant table nor a generated table is included in this public inventory. The completed result stays developmental and assumption-dependent, with no additional run requested or authorized by packaging.

## Exclusions and final v0.14 gate

Exclude every real/generated individual table, every execution `output/`, all raw gateway/search/fetch responses, full articles/supplements/codebooks, gateway configuration/session cache, Agent contexts, test temporary outputs, runtime environments, caches, logs, transport payloads and credentials. Only the three named curator extractions are allowed beneath the experiment's `admission/sources`; never generalize that exception to `sources/**`. Experiment figure PDF copies are omitted here. Original figure PDFs needed by the authored reading/Overleaf paper belong in the separately reviewed paper allowlist.

The final v0.14 authored-paper allowlist must be fixed after independent manuscript/numeric/visual review: draft, reviewed scientific figure exports, TeX/PDF, build source and input bindings, README/instructions, reviewed Overleaf archive with exact-member validation, integration audits and navigation. Reuse prior own figure blobs only after byte/hash comparison. Reject unlisted PDF/ZIP members, third-party documents and rendered review pages. Keep old frozen outputs unchanged.

Carry forward the v0.13 safeguards: bind final review decisions to current bytes, fail on missing/unresolved relative Markdown links, preserve BOM/CRLF and non-Markdown bytes, retain scientific local-path/hash identities, separately record public-byte hashes and navigation rewrites, and recheck remote head before the parent's authorized publication. This draft itself is not a replacement for that final export review.

## Candidate group counts

| Group | Files |
|---|---:|
| `aggregate_endpoints_and_receipts` | 8 |
| `constructor_interface_snapshots` | 7 |
| `engineering_review_receipts` | 2 |
| `exact_bound_candidate_check_artifacts` | 35 |
| `experiment_protocol_results_provenance` | 16 |
| `historical_experiment_code_tests` | 12 |
| `manuscript_cross_task_insert` | 1 |
| `new_harness_code_docs_tests` | 6 |
| `optional_aggregate_source_feedback` | 6 |
| `optional_exact_session_chain_and_feedback` | 90 |
| `original_experiment_figures` | 5 |
| `original_metadata_and_extracted_source_facts` | 8 |
| `original_scientific_and_numeric_review` | 64 |
| `portable_aggregate_plot_entry` | 1 |
| `six_author_frozen_candidates` | 60 |
| `six_author_original_artifacts` | 59 |

## Exact bound check-artifact appendix

These files must accompany their unmodified `checks.json` and evidence-use declarations. Paths below are relative to each public author bundle.

### H01

- `candidates/initial/checks/acquisition_ledger.json`
- `candidates/initial/checks/analytic_calculations.py`
- `candidates/initial/checks/analytic_outputs.json`
- `candidates/initial/checks/implementation_annotations.md`
- `candidates/initial/checks/source_integrity.json`
- `candidates/initial/checks/source_proposal_review.json`
- `candidates/initial/checks/specification_algebra.json`
- `candidates/initial/checks/static_inspection.json`
- `candidates/initial/checks/validation_contract_01.json`
- `candidates/initial/checks/validation_contract_02.json`
- `candidates/initial/checks/validation_evidence_use_01.json`
- `candidates/initial/checks/validation_evidence_use_02.json`
- `candidates/initial/checks/validation_semantics_01.json`
- `candidates/initial/checks/validation_semantics_02.json`
- `candidates/initial/checks/validation_semantics_03.json`

### H02

- `candidates/initial/checks/static_validation.json`
- `candidates/initial/checks/proposal_algebra.json`
- `candidates/initial/checks/source_proposal_review.md`
- `candidates/initial/checks/source_semantics_preflight.json`

### H03

- `candidates/initial/checks/proposal_algebra.json`
- `candidates/initial/checks/proposal_algebra.py`
- `candidates/initial/checks/source_proposal_review.md`
- `candidates/initial/checks/source_proposal_review.json`
- `candidates/initial/checks/independent_analytic_recheck.json`
- `candidates/initial/checks/generator_ast.json`

### L01

- `candidates/initial/checks/L01_SOURCE_PROPOSAL.json`
- `candidates/initial/checks/L01_ANALYTIC_RECHECK.json`
- `candidates/initial/checks/author_algebra.json`
- `candidates/initial/checks/STATIC_CONSTRUCTION_CHECK.json`

### L02

- `candidates/initial/checks/source_proposal_review.json`
- `candidates/initial/checks/analytic_recheck.json`

### L03

- `candidates/initial/checks/analytic_derivation.json`
- `candidates/initial/checks/controller_analytic_recheck.json`
- `candidates/initial/checks/controller_source_review.md`
- `candidates/initial/checks/static_inspection.json`

