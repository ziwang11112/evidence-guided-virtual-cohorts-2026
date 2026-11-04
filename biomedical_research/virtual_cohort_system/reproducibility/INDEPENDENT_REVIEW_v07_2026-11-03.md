# Independent public-aggregate reproduction review

**PASS — 3 November 2026.** The new [entrypoint](reproduce_manuscript.py) reconstructs the manuscript display values and renders the four quantitative figures from the public aggregate export. It does not rerun cohort construction or clinical analysis. The [machine-readable review](INDEPENDENT_REVIEW_v07_2026-11-03.json) records exact source, implementation and output hashes.

The reviewed implementation has SHA-256 `7094b8a5eaba06b05b90d37a564aed071e1e36dac62cbeb73b0dec27cd3d84fd`; the 21-file [input allowlist](public_inputs_v07.json) has SHA-256 `54072091acff475238a9011ce062c6f5084b897e09968ac6051b597fd9104f8d`. Inputs came from clean public commit `bec2041d1816432dd744cf875c649e9ea6142e67`. The runner was invoked from the local project against that public checkout; publication of the new reproduction files is a separate synchronization step.

## Executed checks

- `--verify-only` passed under `python -I -S -B`, with third-party site packages disabled and the working directory outside the source checkout.
- Two full rendering runs passed, one using the repository root and one the nested project root. All 24 output files, including SVGs, PNGs, numeric tables and the receipt, had identical hashes across the runs.
- All four freshly rendered quantitative PNGs matched the retained integrated PNGs byte-for-byte. The method schematic and editable draw.io source were verified unchanged copies. No new diagram was created.
- All 45 manuscript-rounded numeric cells in Tables 2–4 matched. Independent arithmetic checked the 61 underlying numeric values: 18 reference/bound values, 18 E0/E1 discrepancy values, and 25 supplied-summary reference/range values. Interval and range cells each contain two underlying numbers.
- The Table 3 calculation retained five Agent authors per condition, averaging absolute seed discrepancies within each author and then across authors; prescribed statistical constructors were excluded. Five of six contrasts favored E1. Table 4 retained ranges over three author means per condition.
- Three HRS summary CSVs were exact aggregate copies; the two focal terms were an exact 12-record selection. The standard-library and rendering modes produced identical numeric outputs.
- Six negative tests returned exit code 1: a nonempty output directory, output inside the checkout, output at an ancestor of the checkout, optimized Python, a tampered pinned input, and a missing pinned input. Existing output hashes were unchanged, and failed runs did not publish new output directories.
- All 21 public input hashes were unchanged after execution, and `git status --porcelain --untracked-files=all` remained empty.

The runner additionally verified the 306 cross-sectional seed pointers, 102 constructor means/ranges, plotted references and intervals, 96 unique HRS coefficient records, 32 HRS coefficient summaries, 54 distribution summaries and retained Wald-interval arithmetic. Existing independent-audit records were read and bound by hash; the scientific audits themselves were not repeated.

## Boundary and provenance assessment

The explicit input allowlist, source-escape rejection, separate-output requirement, temporary staging and post-run input hashes support the documented read/write boundary. Static inspection found no generator, evaluator or `cohort_harness` import in the entrypoint or its two pinned plotters. The only restored bytes were the two documented LF-to-CRLF historical JSON transformations inside temporary staging; both recovered their exact original hashes and byte counts while preserving parsed JSON identity.

Table 1 prose and editorial labels are retained manuscript content; its numeric scope is separately exported. Figure 1 is copied. Tables 2–4 numeric cells and Figures 2–4/S1 are rebuilt from aggregates. These distinct operations are correctly described in the [reproduction guide](../docs/REPRODUCING_MANUSCRIPT_v07.md).

## Scope limits

Execution was tested on Windows 11, Python 3.12.10, Matplotlib 3.10.9, NumPy 2.4.5, Pillow 12.2.0 and FreeType 2.6.1. No installation, Linux/macOS run, clinical execution, participant/generated-subject table access, new fit, literature reaudit or final journal-layout review occurred. Repeated byte identity is established for this environment; portability does not require historical image-byte identity. The command does not reproduce inaccessible clinical rows or certify scientific validity or submission readiness.

The reviewed output and test harness are retained locally in `biomedical_research/v07_reproduction_independent_2026-11-03/`; `render_a/` is the final reviewed rendering output. Their hashes are recorded in the JSON review, so those local test artifacts need not be included in the public export.
