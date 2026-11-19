# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript v0.37, 19 November 2026. [Paper and supplement](paper.pdf) · [Editable Overleaf project](overleaf_v37.zip) · [Build and numerical verification](BUILD_CHECK.json)

## Reading the results

**Figure 1, page 2.** Each blue circle is the estimate from one agent-authored law. The orange diamond is the estimate from measured participants, with the uncertainty calculation used for that dataset. Read across the two iron panels to compare the threshold odds and continuous ranks on the same records. The US comparison used a development sample. Burkina Faso had no low-ferritin participant from whom to estimate an odds ratio. CHNS B was evaluated once after the final models were sealed. [Blood-pressure study](../../work/prospective_bp_freetown_2026-11-18/RESULTS.md) · [External iron study](../../work/original_paper_iron_sensitivity_2026-11-19/RESULTS.md)

**Figure 2, page 3.** The agent interprets published quantities, selects a joint distribution and writes a generator. The isolated execution service draws its records. A separate evaluator applies the requested scientific analysis to the virtual and measured data.

**Figure 3, page 6.** Read each row from the open marker to the filled marker. A move to the left means lower absolute error against the held-out communities. Six final CHNS generators met the planning tolerances for the two scientific analyses. The additional A statistic improved the prespecified whole-cohort rank estimate for one of the six authors. A descriptive analysis after disclosure found improvement in the middle Hb band's weighted contribution for all six. Table 2 on page 9 gives the six paired comparisons. [CHNS results and protocol](../../work/chns_iron_conditional_holdout_2026-11-19/RESULTS.md)

## Rebuilding the draft

Upload the ZIP as a new Overleaf project. Select pdfLaTeX and compile `main.tex` with the standard ACM class. The paper and appendix occupy 12 pages. The main text ends on page 7. Compiling a fresh extraction produced identical text on all pages. The figure code and numerical check use saved aggregates. The verification covers 141 numbers in five tables and the distinction between uptake of the A statistic, global accuracy in B and the post hoc component result. [Figure source](../../reproducibility/plot_v37.py) · [Numerical check](../../reproducibility/check_v37.py) · [KDD format](https://kdd2027.kdd.org/research-track-call-for-papers/)

The CHNS study supplied an external article and original aggregate tables from a separate set of communities in the same survey. Its conclusions apply to the two declared group analyses on this split. [Archived v0.36 manuscript](../kdd_draft_v36_2026-11-19/paper.pdf)
