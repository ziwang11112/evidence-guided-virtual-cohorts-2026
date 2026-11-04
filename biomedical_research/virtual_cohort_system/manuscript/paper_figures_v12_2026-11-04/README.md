# Scientific figures, v12

This edition replaces dashboard styling with native-unit scientific comparisons and a concrete implementation trace. It changes presentation only; all frozen results and negative findings remain.

- [Chinese figure-reading guide](READING_GUIDE_ZH.md): axes, points, intervals, interpretation and actual strengths/limitations.
- [Figure 1: implementation](fig1-agent-framework.drawio.svg): one closed evidence-to-copula construction, with the numerical transformation and declared dependency.
- [Figure 2: external evidence](fig2-evidence-results.svg): all six coefficients, constructors and seeds.
- [Figure 3: supplied summaries](fig3-summary-results.svg): five analyses with their original units.
- [Figure 4: longitudinal use](fig4-longitudinal-use.svg): both interactions, both constructions and every seed interval.
- [Figure 5: scientific analyses](fig5-analysis-use.svg): seven native effects and the two previously computed sensitivity scenarios.
- [Captions 2–3](CAPTIONS_23.md), [captions 4–5](CAPTIONS_45.md), [numeric bindings 2–3](NUMERIC_BINDINGS_23.json), [numeric bindings 4–5](NUMERIC_BINDINGS_45.json).
- [Manuscript](../DRAFT_v0_12.md), [reading PDF](../conference_draft_v12_2026-11-04/paper.pdf), [Overleaf bundle](../conference_draft_v12_2026-11-04/overleaf_v12.zip).

Each figure is also available as PDF and PNG. Figure 1 SVG, PNG and PDF embed the editable draw.io model; `build_framework.py` recreates native XML. Run the repair pass in the associated work/report directory before exporting through draw.io with embedded XML and cropped PDF output. Then remove the standalone XML, retaining the builder and embedded exports. Exported equations and table placeholders are schematic representations of the audited implementation, not invented participant records.

`render_evidence_results.py` and `render_scientific_use.py` consume only SHA256-pinned aggregate records, support local work/public reports layouts and accept `--output` for a separate reproduction folder. No new generation or scientific fit occurs. Blue/violet distinguish conditions, coral highlights the declared assumption/scenario, and slate denotes references. None is a pass/fail certification color.

Primary visual references: [G-Sim](https://proceedings.mlr.press/v267/holt25b.html), [LLMSynthor v4](https://arxiv.org/html/2505.14752v4), [SPADA](https://aclanthology.org/2025.emnlp-main.525/). All figure artwork here is original.
