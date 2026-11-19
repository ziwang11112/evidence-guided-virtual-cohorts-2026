# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

English working manuscript v0.35, 19 November 2026.

[Read the paper](paper.pdf) · [Download the Overleaf project](overleaf_v35.zip) · [Edit the main source](main.tex) · [Build and numerical checks](BUILD_CHECK.json)

## Reading the results

- **Figure 1, page 2.** The scientific agent interprets articles, chooses the joint law and writes the sampling program. An execution service draws the records, and a separate evaluator applies the requested analyses.
- **Figure 2, page 3.** Compare each constructor's three-draw range with the Brazilian blood-pressure or US iron-status estimate. Table 1 on page 4 reports all six controlled comparisons after adding a joint block to the source evidence.
- **Figure 3, page 5.** Two laws have the same five blood-pressure moments but imply joint screening rates of 11.94% and 15.09%. The released Freetown estimate was 44.21%. Section 5 gives the prespecified finite-draw result and the reference-field audit.
- **Figure 4, page 6.** The matched-size Turkana experiment compares discrepancies between real resamples with those between virtual and real resamples. The appendix reports all nine lifestyle contrasts.

## Editing and compilation

Import the ZIP using **New Project → Upload Project** in Overleaf. The root file is `main.tex`. Choose **pdfLaTeX** and compile. BibTeX uses the standard `ACM-Reference-Format` style. In a TeX installation with `acmart`, a local build runs `pdflatex main`, `bibtex main`, then `pdflatex main` twice.

The source follows the ACM SIG Proceedings sample with the KDD Research class options `sigconf,anonymous,review`. The eight-page PDF includes the references and a two-column appendix. The main text ends on page 6. The ZIP uses the ACM class and bibliography style supplied by the TeX installation. A clean local extraction compiled with MiKTeX and acmart 2.20. [KDD Research instructions](https://kdd2027.kdd.org/research-track-call-for-papers/) · [Official ACM Overleaf template](https://www.overleaf.com/latex/templates/association-for-computing-machinery-acm-sig-proceedings-template/bmvfhcdnxfty)

## Evidence and verification

The manuscript integrates the [original-paper constructions](../../work/original_paper_capability_2026-11-17/RESULTS.md), [pressure](../../work/pns_evidence_content_control_2026-11-16/RESULTS.md) and [iron](../../work/iron_evidence_content_control_2026-11-16/RESULTS.md) evidence controls, [matched-size lifestyle comparison](../../work/matched_size_utility_2026-11-17/RESULTS.md), and [prospective Freetown test](../../work/prospective_bp_freetown_2026-11-18/RESULTS.md). Another original-paper prospective test in a different biomarker family remains future work.

The [typeset-table check](../../reproducibility/check_v35.py) compares all 89 entries in the three manuscript tables with archived experimental estimates and checks the two exact scenario probabilities and finite-draw decision. The [earlier numerical replay](../../reproducibility/check_v34.py) verifies the original-paper and lifestyle result figures. The [prospective replay](../../work/prospective_bp_freetown_2026-11-18/replay_public.py) verifies freeze chronology, program hashes, moments and integrals. All three ran using saved scientific outputs. This writing release used no new paid constructions or participant data.
