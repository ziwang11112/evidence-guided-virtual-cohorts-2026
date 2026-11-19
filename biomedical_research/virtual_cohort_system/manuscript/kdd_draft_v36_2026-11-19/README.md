# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

English KDD Research working manuscript v0.36, 19 November 2026. [Paper and supplement](paper.pdf) · [Overleaf source](overleaf_v36.zip) · [Typesetting and numerical checks](BUILD_CHECK.json)

## Reading the new experiment

Figure 4 on page 6 applies two scientific analyses to each of the same prospective iron-status cohorts. Compare the marker shapes within a parent row. On the left the model estimates cluster around the source anemia odds ratio. On the right the continuous rank correlation changes, including a sign reversal under one assumed inverse within-band association. The measured row shows what the external survey could verify. Its rank estimate has a wide interval, and it had no low-ferritin participant from whom to estimate the threshold contrast. Table 3 gives every planned model request and both incomplete responses. [Full experimental report and scientific programs](../../work/original_paper_iron_sensitivity_2026-11-19/RESULTS.md)

The other figures trace original-paper construction (Figure 2), blood-pressure screening under compatible laws (Figure 3), and the real–real sampling variation in lifestyle comparisons (Figure 5). Table 1 gives all six controlled evidence effects, including the four companion discrepancies that increased. [Earlier working manuscript](../kdd_draft_v35_2026-11-19/paper.pdf)

## Editing and verification

Upload the ZIP through **New Project → Upload Project** in Overleaf. Select pdfLaTeX and compile main.tex. The document uses the official ACM acmart class with sigconf,anonymous,review and the standard ACM bibliography style. The 10-page PDF includes references and an appendix. The main text ends on page 7. Both an independent source build and a clean ZIP extraction produced identical page text. The 105 numerical cells in four manuscript tables were checked against the study records. [KDD Research instructions](https://kdd2027.kdd.org/research-track-call-for-papers/) · [Numerical check](../../reproducibility/check_v36.py)

The iron study used three independent parent sessions with one GPT configuration. Two of six alternative calls reached the output limit. The seven complete model programs required the same parameter-binding correction in the runner. The amendment was fixed before any scientific outputs or target effects were opened. The appendix presents the interface failures, real sampling uncertainty and assumptions behind the sign-reversing case. [Pre-execution amendment](../../work/original_paper_iron_sensitivity_2026-11-19/INTERFACE_ADDENDUM.md)
