# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript v0.38, 19 November 2026. [External review PDF](external_review.pdf) · [External review Overleaf ZIP](overleaf_external_review_v38.zip) · [Anonymous manuscript](paper.pdf) · [Anonymous Overleaf project](overleaf_v38.zip)

The external review copy adds four clickable first-page links. Its reviewer guide, experiment index and table checker point to the same fixed Git commit. The scientific text, tables, figures and page numbers match the anonymous manuscript. Compile `external_review.tex` beside `main.tex` for this edition, or compile `main.tex` in the external review ZIP. [Linked-edition verification](EXTERNAL_REVIEW_CHECK.json) · [Scientific build verification](BUILD_CHECK.json)

## Reading the paper

**Table 2, page 6.** Given the same A tables, six original-evidence agents estimated the continuous Hb–ferritin rank correlation at 0.293–0.320 in a survey split where the measured value in B was 0.317. A statistical law fitting the A summaries under within-band independence gave 0.237 (population value 0.241). Both passed the planning margin. Within-band re-pairing of the six agents' own records reduced their expected ranks to 0.244–0.249 while preserving the four threshold counts. The A counts directly imply an odds ratio of 5.083. The comparison was specified after B had been revealed. [Protocol, per-parent scores and verification](../../work/chns_statistical_comparator_2026-11-19/RESULTS.md)

**Figure 3, page 6, and Table 3, page 10.** This is the original paired experiment. Each author revised its parent law with and without an extra within-band A contrast. The prespecified whole-cohort rank estimate improved for one of six parents. An exploratory calculation localized improvements to the middle Hb band for all six. The new Table 2 uses only the original-evidence controls. [CHNS holdout and paired results](../../work/chns_iron_conditional_holdout_2026-11-19/RESULTS.md)

**Figures 1 and 2, pages 2 and 3.** Figure 1 compares estimates from virtual and measured records across the blood-pressure and iron studies. The Freetown joint percentage refers to the deposited field pairing. Figure 2 follows an agent from the research request to its probability law, the generated records and the common scientific analysis. [Pressure study](../../work/prospective_bp_freetown_2026-11-18/RESULTS.md) · [External iron study](../../work/original_paper_iron_sensitivity_2026-11-19/RESULTS.md)

## Reproduction

Upload the ZIP into Overleaf, select pdfLaTeX, and compile `main.tex` with the standard ACM class. The 13-page PDF has seven figures and six tables. The main text ends on page 7. A clean build from the ZIP reproduced the text on every page. The numerical audit covers 155 populated cells across all six tables. The three new virtual tables reproduced byte for byte on the recorded installation. The public replay requires Python, NumPy, pandas and SciPy. Run the comparator's `run.py replay` and then `python reproducibility/check_v38.py` from the project root using the relevant script paths. [Comparator replay](../../work/chns_statistical_comparator_2026-11-19/run.py) · [Table checker](../../reproducibility/check_v38.py) · [Figure source](../../reproducibility/plot_v37.py) · [Previous manuscript](../kdd_draft_v37_2026-11-19/paper.pdf)
