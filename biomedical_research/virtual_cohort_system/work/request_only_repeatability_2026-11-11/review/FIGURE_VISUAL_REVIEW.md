# Independent figure visual and aggregate-binding review

**PASS.** Reviewer: `/root/repeatability_figure_qa`. Reviewed the two final figure families after the root replaced the four BMI arrow titles with explicit association labels. No remaining visual or reporting blocker was found.

## Actual files inspected

- `figures/primary_analyses.pdf`: actual one-page PDF rendered with Poppler `pdftoppm` at 160 dpi, then visually inspected; latest original PNG also inspected.
- `figures/delivery_resources.pdf`: actual one-page PDF rendered with Poppler at 160 dpi, then visually inspected; latest original PNG also inspected.
- Actual-PDF render files are in `review/figure_renders/`. Exact final PDF, PNG, SVG and render hashes are recorded in `FIGURE_VISUAL_REVIEW.json`.

This was local artifact review, with no browser, browser-policy workaround, API call, generator execution, patient-row reading, or new source retrieval.

## Visual findings

Both figures have legible titles, axes, units and footnotes, consistent blue/orange policy encoding, and no observed clipping, overlap or missing glyphs. All twelve assigned constructors remain visible. The primary figure shows all six prespecified analyses, with three constructor rows per policy within each request. Resource axes start at zero. The scientific estimates and resource counts are visually separated.

The original four BMI-to-outcome arrows could imply causality. The root changed them to BMI-SBP, BMI-DBP, BMI-TC and BMI-HDL association labels. Both resulting PDFs and PNGs were inspected again. Adjusted associations are now explicit.

## Data and interpretation checks

`verify_figure_bindings.py` completed **331 read-only aggregate checks**. All 36 constructor-analysis CSV rows exactly match `EVALUATION.json` for identifiers, units, seed availability, mean, minimum, maximum, mean absolute reference difference and reference value. There are 12 unique constructors, six primary analyses, 36 delivered final tables, 331 reserved model calls, USD 3.9851613 known tariff cost, and no unknown-usage calls.

The primary figure correctly distinguishes filled constructor means, open seed estimates and seed ranges. Its footnote states that ranges include encoded scenario draws and are not confidence intervals. This covers PNS_BASE_R3, whose per-seed shared parameters mean that its spread is not purely participant-sampling variation. The external caption preserves the distinction between saved reference uncertainty and known population truth; it does not define equivalence by interval overlap. Reference intervals retain their differing sampling conventions.

The resource figure and caption explicitly distinguish delivered tables from scientific validity. Dollar amounts are tariff estimates, not provider invoices or full research costs. Three seed tables are not three independent clinical validations. No overall policy-superiority claim or composite quality score is introduced.

## Boundary

This review validates plotting, aggregate bindings and rendering. It does not certify scientific transportability, source extraction, mathematical moments, or the usefulness of every generated analysis. Those require the separate scientific provenance and independent recomputation audits. The figure source files, production state, frozen methods, generated rows and manuscript were not modified by this reviewer.
