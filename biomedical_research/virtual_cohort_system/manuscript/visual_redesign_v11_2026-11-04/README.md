# Integrated visual redesign, v0.11

Five original figures replace the simpler v0.10 presentation. The underlying experiments and scientific body are unchanged. Blue, violet, coral and slate replace green/teal; color identifies information conditions or graphic roles, not a universal pass/fail judgment.

Open the [figure gallery](index.html) to inspect the full set. Vector SVG/PDF, preview PNG, source scripts and numeric bindings are included. Figure 1's embedded draw.io SVG/PDF/PNG remain editable in draw.io; the native source is recreated by `build_framework.py` when needed.

| Figure | Purpose | Design |
|---|---|---|
| [1. Framework](fig1-agent-framework.drawio.svg) | Explain actual Agent scientific decisions | Three zones with evidence status, a model-dependence sketch, a worked projection identity, deterministic execution and optional review |
| [2. Evidence and analysis](fig2-evidence-results.svg) | Compare six prescribed analyses under E0/E1 | Cohort-grouped native effects plus endpoint-specific relative discrepancy changes |
| [3. Summary reconstruction](fig3-summary-results.svg) | See five analyses of each generated table together | Analysis-by-constructor matrix, native means, all seeds and explicit relative-deviation encodings |
| [4. Longitudinal use](fig4-longitudinal-use.svg) | Connect the data structure to its analysis | Actual four-visit schedule and all twelve interaction estimates in one display |
| [5. Scientific profiles](fig5-analysis-use.svg) | Connect useful analyses to a missing joint relationship | Seven effects in aligned reference-relative coordinates and two existing analytical sensitivity scenarios |

The supplied example image inspired the three-zone hierarchy and decomposition into meaningful operations. Its artwork, training mechanism and experimental curves were not copied. No new clinical analysis, generator execution or parameter change was needed.

For Figures 2/3 run `render_evidence_results.py`; for Figures 4/5 run `render_scientific_use.py`. Both accept `--output` to reproduce into a separate directory and pin their existing aggregate inputs. The [Figure 2/3 captions](FIG23_CAPTIONS.md) and [Figure 4/5 captions](FIG45_CAPTIONS.md) explain units, display transformations and uncertainty. Numeric bindings preserve native quantities even when a figure uses normalized display coordinates.

To rebuild Figure 1, run `build_framework.py`, repair the XML with the versioned `repair_drawio.mjs` in the review materials, then export through draw.io Desktop using `-x -f svg -e`, `-x -f png -e`, or `-x -f pdf --crop -e`. Use the diagram-size PDF, not a full letter-sized export. The overview is explanatory artwork; its placeholder table and dependency sketch are not patient observations or causal discoveries.
