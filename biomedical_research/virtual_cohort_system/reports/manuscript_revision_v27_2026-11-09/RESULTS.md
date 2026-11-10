# v0.27 editorial revision: completed

The 9 November 2026 revision implements the independent v0.26 review without changing the empirical record. The manuscript now makes the scientific use, actual actors, reference definitions and reproducibility boundary explicit. It remains a methods-development draft; an editorial PASS is not publication readiness.

## What changed

1. Main Table 1 identifies the researcher/host coordinator, scientific author, source/code reviewers, isolated numerical worker and separate evaluator. The text distinguishes required pre-freeze review in Q4/Q5, Q1 closure review and the iron study's separate host review. A retained first frozen law can already include pre-freeze corrections.
2. Main Table 5 distinguishes observed coefficient directions/magnitudes, threshold behavior and model reconstruction from uses not yet established, such as calibrated inference, power, clinical decisions and transfer to a new population.
3. Supplement S16/Table S9 records eligibility, measurement, weighting, estimands, uncertainty and prior exposure for the six measured-reference or published-model settings. ENSANUT's selected equal-cell analysis is not described as a national estimate. HRS is supplied-model reconstruction, not a fresh clinical validation.
4. Supplement S17/Table S10 and the [reproducibility guide](REPRODUCIBILITY_GUIDE.md) separate figure/aggregate regeneration, frozen-program replay and Agent-authoring reproduction. Missing author-model/inference metadata are stated rather than inferred.
5. Abstract, contribution, related work, results interpretation and limitations now use those distinctions. Positive findings remain visible; negative results, underdispersion, unresolved dependence and previous failed prospective criteria remain reported. No universal superiority or measured feedback benefit is claimed.

## Verification

- [Editorial scope checks](EDITORIAL_SCOPE_QA.json): all 11 existing numerical table blocks, all 11 figure assets and the bibliography are unchanged; four documentation tables were added; 65 local manuscript links resolve.
- [Independent integrated review](INDEPENDENT_REVIEW.md): PASS for editorial/novelty/claim scope, with no open material findings. One minor antecedent correction was requested and applied. The review is bound to the final manuscript SHA256.
- [Build QA](../../manuscript/methods_draft_v27_2026-11-09/BUILD_QA.json): 16 main-text pages, 42 total, 11 figures and 15 tables. The independently extracted Overleaf package compiles and matches the main PDF's text and external links. No detected TeX overflow, missing glyph or oversized float.
- All 42 PDF pages were inspected in contact sheets; new long tables received additional page-scale inspection. No material rendering defect was observed.
- v0.26 remains unchanged. An intermediate main-table renumbering error touching bibliography table text was caught by preservation checks and corrected before delivery; no historical artifact was changed.

The complete mapping from review concern to revision and remaining boundary is in [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md).

## Scope and decision

No participant-level table was opened for this revision. No generator was executed, clinical reference refitted, new data acquired, model trained, paid API invoked or HPC job started. The frozen-program guide is a statically checked recipe, not a newly executed clean-install reproduction. Post hoc aggregate sensitivity arithmetic from the independent review remains an audit finding, not a new confirmatory paper endpoint.

Freeze this editorial version for review. The next useful assessment is a biomedical review of whether the specified analysis tasks and observed magnitudes are informative for their intended use. Any stronger claim about new-population reliability, calibrated inferential uncertainty, autonomous operation or authoring reproducibility requires separately designed evidence; it cannot be obtained by wording changes. No additional experiment starts automatically in this unit.

## Deliverables

- [English manuscript](../../manuscript/DRAFT_v0_27.md)
- [Review PDF](../../manuscript/methods_draft_v27_2026-11-09/paper.pdf)
- [Standalone Overleaf ZIP](../../manuscript/methods_draft_v27_2026-11-09/overleaf_v27.zip)
- [Independent review](INDEPENDENT_REVIEW.md) and [machine-readable record](INDEPENDENT_REVIEW.json)

Public synchronization includes only reviewed original documentation/code, figures and aggregate records. Real or generated participant records, third-party full texts and credentials are excluded. The final synchronization receipt is maintained locally after the commit to avoid a self-referential receipt.
