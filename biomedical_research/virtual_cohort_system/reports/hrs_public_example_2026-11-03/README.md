# HRS longitudinal published-example experiment

Start with [RESULTS.md](RESULTS.md), [independent result review](FINAL_RESULT_REVIEW.md) and the [manuscript addendum](../../manuscript/SUPPLEMENT_HRS_PUBLIC_EXAMPLE_2026-11-03.md).

This package compares one Agent-authored generator with a reconstruction of the public HRS recipient-stage law from Filshtein et al. It is a source-model reconstruction task with supplied scientific coefficients. It is not an independent HRS participant-data validation, the full ARIC/HRS pooling pipeline, or a new-method superiority test.

The completed record contains nine physical generation attempts: the original six plus a separately reviewed three-attempt comparator repair. Three initial comparator outputs were invalid because our parameter parser crossed model boundaries. Six valid comparison outputs remain (three per construction), each with11,509subjects and46,036visits. All original failure artifacts and the source-only correction are retained. The Agent outputs never changed. See [incident and correction](recovery_v1/INCIDENT_AND_CORRECTION.md).

## Contents

- `bundle/candidates/agent/`: independently authored generator, scientific specification, evidence and frozen preparation record.
- `bundle/candidates/native/`: original invalid comparator specification, retained explicitly as an incident artifact. **Do not use it as the intended published law.**
- `recovery_v1/bundle/candidates/native_corrected/`: corrected source-bound comparator and separate freeze.
- `evaluation/`: the native R/lme4 mixed-model evaluator, independent conditional GLS checker and runtime/setup metadata.
- `results/`, `recovery_v1/results/`, `attempts/`: aggregate fits, verification, execution and failure accounting.
- `summary/`: all96fixed-coefficient estimates withSEs and162baseline diagnostic values, plus per-construction summaries. No individual records.
- `figures/`: complete16-effect display and the two prespecified scientific relationships, with numeric source binding.
- `sources/`: original-source metadata and numeric extraction records. The original `HRS_SOURCE_EVIDENCE.json` is retained as faulty historical evidence; the corrected packet is under `recovery_v1/sources/`.

## Reproduction boundaries

Third-party source files, package binaries, and all generated row-level tables remain local and are excluded from GitHub. `fetch_public_sources.py` can retrieve the five pinned public source artifacts and verify their byte counts/SHA256; it does not run an experiment. Original source URLs and Git blob hashes are in `sources/SOURCE_MANIFEST.json`. The source repository has no explicit license, so its complete files are not redistributed here. Reported numeric facts, our original code and our aggregate results are included with attribution.

The generator runtime is the existing WSL/bubblewrap harness. The evaluator uses R4.3.3/lme4 1.1-35.1, rather than the historical R4.0.1/lme4 1.1-23. The local extraction setup and14,514,632-byte package ledger are provided; extracted libraries are not published. Do not overwrite a frozen candidate or historical execution receipt to reproduce results: use a separate working copy and explicit new run IDs. Released controllers reject duplicate reservations and do not automatically repeat failed runs.

The completed experimental allocation is closed. The reproduction code and audits do not authorize an additional research campaign or outcome-guided tuning. The next project task is manuscript integration of the supported longitudinal capability and its limits.
