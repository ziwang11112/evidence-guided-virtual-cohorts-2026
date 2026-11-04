# Reproduce the v0.7 manuscript displays from public aggregates

The entry point reconstructs the numeric cells of manuscript Tables 2–4 and
renders Figures 2–4 and S1 from retained public aggregate statistics. It copies
the verified Figure 1 schematic and its editable draw.io source. This is offline
display reproduction, not a rerun of cohort construction, clinical analysis,
reference estimation or scientific validation.

From the public repository root, with an existing Python environment containing
the rendering dependencies, run one command:

```console
python biomedical_research/virtual_cohort_system/reproducibility/reproduce_manuscript.py --repo-root . --output ../manuscript-v07-reproduced
```

The destination must be new or empty and outside the source checkout. The
command refuses to overwrite prior outputs. `--repo-root` also accepts the
public repository's `biomedical_research/virtual_cohort_system` directory.
Absolute paths allow invocation from any working directory. There is no
fallback to private `work/` inputs.

## Requirements and a standard-library-only route

The tested environment is Python **3.12.10**, Windows 11, Matplotlib **3.10.9**,
NumPy **2.4.5**, Pillow **12.2.0**, and Matplotlib's FreeType **2.6.1**. The
observed rendering package versions are recorded in
[`requirements-render.txt`](../reproducibility/requirements-render.txt).
Use an already prepared environment; the entry point does not install packages,
download data, invoke APIs, or launch external executables. Linux and macOS have
not been exercised by this delivery. Rendering-library and font differences can
change image bytes without changing the verified numerical payload.

To validate the public input hashes and rebuild the numeric tables without any
third-party dependency:

```console
python biomedical_research/virtual_cohort_system/reproducibility/reproduce_manuscript.py --repo-root . --output ../manuscript-v07-verified --verify-only
```

This mode does **not** render or package figures. Both modes fail under `python
-O` or `PYTHONOPTIMIZE`: assertions in the retained plotting implementation must
remain enabled. The runner's own essential checks raise explicit errors.

## What the command produces

| Output | Operation and scientific meaning |
|---|---|
| `figures/fig1_method.drawio`, `.svg`, `.png` | Byte-identical copies of the existing explanatory schematic. No claim of a newly rendered diagram. Omitted with `--verify-only`. |
| `figures/fig2_external_evidence.svg`, `.png` | Fresh rendering using `build_utility_figures.py`: 6 panels, 216 seed statistics, 72 constructor means. |
| `figures/fig3_summary_assisted.svg`, `.png` | Fresh rendering using the same source algorithm: 5 data panels, 90 seed statistics, 30 constructor means. |
| `figures/fig4_longitudinal.svg`, `.png` | Fresh rendering using `plot_results.py`: 12 seed coefficient estimates and 2 source estimates, with the retained model-conditional Wald intervals. |
| `figures/figS1_longitudinal_all_effects.svg`, `.png` | Fresh rendering of the same HRS comparison tables: 96 seed estimates across 16 effects, 32 means. This supplement does not add replicates. |
| `tables/MANUSCRIPT_TABLES.md` | Table 1 prose retained from the frozen manuscript; Tables 2–4 numeric cells reconstructed and checked against all 45 manuscript-rounded cells. Editorial labels are preserved. |
| `tables/table1_numeric_scope.csv` | Numeric scope of the three settings: 24/72, 6/18, and 2/6 constructions/valid final tables; table sizes and visit counts. |
| `tables/table2_sample_references.csv` | Six retained sample estimates and their original case-specific reference bounds, at full precision. No reference model is refitted. |
| `tables/table3_information_contrasts.csv` | Six E0/E1 discrepancy contrasts. The runner independently checks the mean of within-author mean absolute seed discrepancies over five Agent authors per condition; prescribed statistical constructors are excluded. |
| `tables/table4_summary_assisted.csv` | Five sets of reference values and L/R ranges over three **author means** per condition, rather than ranges over individual seeds. |
| `tables/cross_sectional_plotted_values.csv` | All 306 retained seed statistics with source JSON pointers. |
| `tables/hrs_all_fixed_effects.csv`, `hrs_fixed_effect_summary.csv`, `hrs_distribution_summary.csv` | Verified unchanged aggregate CSV copies: 96, 32, and 54 records. These are model estimates and distribution summaries, not participant or generated subject rows. |
| `tables/hrs_focal_plotted_values.csv` | Exact 12-record selection for the two focal HRS terms. |
| `cross_sectional_aggregate_source.json` | Retained plotting payload; original audit-era `work/` provenance labels are preserved. Actual public `reports/` input paths and hashes are bound in the reproduction receipt. |
| `CAPTIONS.md` | Retained figure captions, copied only in rendering mode. |
| `REPRODUCTION_RECEIPT.json` | Input and output hashes, counts, operations, environment, mode and scope limitations. The receipt excludes its own hash. |

## Inputs, identity checks and read boundaries

[`public_inputs_v07.json`](../reproducibility/public_inputs_v07.json) is an
explicit **21-file** allowlist pinned to the clean public export at `bec2041`.
It includes only the required aggregate reports, existing audit/figure manifests,
two plot implementations, the frozen manuscript, captions and schematic assets.
The reproduction additions may be committed after that export; the reference
commit identifies the input snapshot, not a requirement that `HEAD` remain at
that commit. No unrelated repository files are recursively opened.

Every allowlisted file must match its exact SHA-256 and byte length. A missing
file or hash mismatch stops the run before publishing an output directory.
There is no search for another copy that happens to match. Symlinks escaping
the public project are rejected. The source hashes are checked again after
rendering. Temporary staging receives only the allowlisted files; the source
checkout and frozen inputs are never modified.

The checks include all 306 cross-sectional seed pointers, 102 constructor
means and seed ranges, all plotted references and reference intervals, the
72-table/24-construction main counts, and historical 42 attempts/24 distinct
tables. HRS checks include the 6 valid comparisons, 9 physical generations,
3 invalid initial comparator tables, 96 unique coefficient records, 32
coefficient summaries, 54 distribution-summary records, and the retained Wald
interval arithmetic. Existing independent audits are read and hash-bound; they
are **not** rerun, and their historical row-read counts are not activity by this
command.

Two historical public JSONs were exported with CRLF changed to LF:
`information_revision_ablation_2026-11-03/COMPLETE_RESULTS.json` and
`INDEPENDENT_RECOMPUTE.json`. These are the only permitted byte transformations.
Their public hashes are pinned, restoration must recover the exact original
hash and byte count in `PUBLIC_PACKAGE_MANIFEST.json`, and parsed JSON equality
must hold. The original CRLF bytes are reconstructed **inside temporary staging
only** so the unchanged plotting implementation can enforce its original hash
bindings. No general whitespace normalization or alternative-source substitution
is accepted.

## Rendering and limits of reproduction

The default command executes the existing aggregate-only plotting algorithms in
temporary staging. Figures 2 and 3 rebuild their plotting payload from the
retained reports and compare all values with the frozen payload before drawing.
Figures 4 and S1 render the 96-record HRS coefficient export. No generator,
evaluation script or `cohort_harness` package is imported; no participant or
generated subject tables are opened. There are zero new constructions, fits,
generator evaluations or network calls.

SVG timestamps and SVG identifier salts are fixed. Repeat runs in the tested
environment are expected to produce the same figure and table bytes; a fresh
output directory is required for each run. Image hashes are recorded separately
from numeric fidelity. Historical image-byte identity is not a portability
requirement. The receipt records Python/platform versions and rendering-library
versions, so any later rendering difference can be inspected without silently
changing scientific values.

The three study settings retain their different permitted information and
interpretations. HRS reference coefficients were construction inputs, R received
target summaries, and the external-evidence settings are developmental studies.
This route does not establish clinical validity, reproduce inaccessible source
rows, generate new results, pool protocols, compile the Word/PDF manuscript, or
establish final journal-layout readability.
