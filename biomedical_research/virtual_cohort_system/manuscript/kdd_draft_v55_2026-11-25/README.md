# KDD working manuscript v0.55

**Same Evidence, Different Estimates — How Modeling Choices Shape Analyses of Agent-Generated Biomedical Data**

[Read the manuscript](paper.pdf) · [Editable source for Overleaf](overleaf_v55.zip) · [Build verification](BUILD_CHECK.json)

The method now spells out what the scientific agent receives, what it chooses and how its executable output is checked. The system first returns virtual individual measurements for a specified analysis. A targeted alternative construction can then reveal how much that analysis depends on a particular assignment of measurements to people.

The two system/mechanism diagrams are on page 3. Algorithm 1 is on page 4. The method text spans pages 2–4. The complete working manuscript has 31 pages with references beginning on page 8.

## Read the method

- Section 2.1 connects reported values, algebraic derivations and assumptions to the model specification and sampling program. The whole-record examples allow the agent to choose distribution families, dependence and parameters.
- Section 2.2 defines the conditional pairing experiment. The investigator supplies marginal conventions and source checks. The agent extracts the relevant numerical values and authors an assignment of measurements.
- Section 2.3 and Algorithm 1 describe the initial program, a fresh targeted author that seeks a consequential alternative, frozen submissions, isolated execution and scientific evaluation. The matched experiment additionally evaluates an ordinary follow-up from the same initial artifact. Actual lipid programs illustrate constrained HDL exchanges and circular rank shifts.
- Section 2.4 describes independent measured-reference evaluation in the units of the requested scientific analysis.

[Overall system figure](figures/evidence-to-analysis-system.drawio.pdf) · [Editable overall figure](figures/evidence-to-analysis-system.drawio) · [Pairing mechanism figure](figures/analysis-conditioned-generation.drawio.pdf) · [Editable pairing figure](figures/analysis-conditioned-generation.drawio)

## Trace the method to the implementation

The appendix subsection *Executable components and authorship* names the responsible functions and records which decisions belong to the investigator and the agent.

| Component | Source |
|---|---|
| Article projection, prompt construction and matched dispatch | [Lipid experiment](../../work/article_pairing_2026-11-22/experiment.py) |
| Exact requested interface and source fields | [Author request](../../work/article_pairing_2026-11-22/REQUEST.txt) |
| Extraction checks, deterministic columns, isolated execution and contrast | [Lipid evaluator](../../work/article_pairing_2026-11-22/evaluation.py) |
| Returned programs, specifications and decision records | [Authored lipid programs](../../work/article_pairing_2026-11-22/PROGRAMS.json) |
| Three-article protocol and complete outcomes | [Matched comparison](../../work/article_portfolio_2026-11-22/RESULTS.md) |
| Agent-selected source constraint in a whole-record model | [Australian BMI trial](../../work/evidence_choice_apss_2026-11-25/RESULTS.md) |

The paired-column experiment used one submission per context and supplied no execution feedback to follow-up authors. A qualifying alternative exhibits a change possible under the selected source checks and marginal conventions. Measured-reference comparisons assess whether a particular generated table supports the intended use. The manuscript reports unsuccessful constructions and comparisons alongside successful ones.

This revision changes the method presentation, figures and implementation description. Experimental outputs are those reported in v0.54. Compile `main.tex` from the portable archive with pdfLaTeX and BibTeX.

