# Existing-case analysis-use diagnosis

Start with [READOUT.md](READOUT.md), then inspect [USE_MAP.csv](USE_MAP.csv) or the structured [USE_MAP.json](USE_MAP.json). The map contains 24 analysis families from existing experiments, not 24 independent datasets or 24 successful validations. Full values and provenance remain in the linked case audits.

[PROTOCOL.md](PROTOCOL.md) states the retrospective boundary. [STATE.json](STATE.json) records completion. The [cross-review](CROSS_REVIEW.json), [scientific-use review](FINAL_USE_REVIEW.json) and [independent mathematical checks](INDEPENDENT_CHECK.json) document what was independently verified and their limits.

The scripts perform deterministic calculations from archived specifications and published summaries. They do not import candidate generators or sample participant records. Some input archives are intentionally local and are not distributed with this report. Running the scripts requires the documented original archive arrangement and Python with NumPy, SciPy and pandas as used by the relevant script; this folder is not a self-contained clinical-data release.

For public copies, the export index distinguishes local-original SHA256 values from public-derivative SHA256 values. Absolute archive locations are replaced with `project/` and `local_archive/` identifiers. These identifiers are provenance references, not a claim that every input is publicly distributed. Scientific-review input hashes continue to identify the reviewed local originals; the export index links them to the public derivatives. Markdown links are adapted to the repository layout. Numeric findings and scientific judgments are not changed by export.

No real or generated participant tables, third-party articles, private external reviews or credentials are included.
