# Same Evidence, Different Estimates

**How Modeling Choices Shape Analyses of Agent-Generated Biomedical Data**

KDD Research working manuscript v0.52 · 25 November 2026

[External-review PDF](external_review.pdf) · [Anonymous PDF](paper.pdf) · [Editable anonymous source](overleaf_v52.zip) · [Editable external-review source](overleaf_external_review_v52.zip)

## What does the agent decide?

An article can give the distributions of two measurements without saying precisely how they go together in individuals. The agent reads the article, identifies the quantities it reports, chooses a joint model and writes a sampling program. A matched experiment holds each column of measurements fixed and gives the agent control over how to pair the columns. The change in the requested analysis then measures the consequence of that decision. [Article-to-program audit](../../work/original_paper_capability_2026-11-17/SOURCE_MODEL_AUDIT.md) · [Three-article design and results](../../work/article_portfolio_2026-11-22/RESULTS.md)

## Read the figures

| Location | Question | Result |
| --- | --- | --- |
| Figure 1, p. 1 | Does fixing both lipid distributions and the published mean individual TC/HDL ratio determine the fraction above a non-HDL cutoff? | Two assignments preserve all three quantities. Both give a mean non-HDL of 128.77 mg/dL. At 160 mg/dL, 9.80% and 26.17% cross the cutoff. This was the smallest gap among four authors. |
| Figure 2, p. 4 | Can the agent deliberately find a source-compatible assignment that changes the analysis? | Out of 12 matched starts per article, ordinary and targeted follow-ups gave a material change in 0 and 11 lipid blocks, 6 and 11 lung blocks, and 12 and 12 iron blocks. |
| Figures 3–4, pp. 4–5 | Which results persist when the measured records replace the virtual data? How much depends on pairing? | In Kenya the same adjusted BMI contrast was 1.88 kg/m² in measured data and 2.05 and 1.97 in virtual data. The same generators underestimated the urban total-cholesterol contrast. Re-pairing measurements within groups isolates the contribution of their individual pairing. |
| Section 4 and appendix | How well does a frozen choice transfer to another sample? | A mean absolute between-hand difference of 3.81 kg compared with 3.30 and 3.78 kg in two measured samples. In the Nigerian iron study, both the agent and a statistical model overestimated the association. |

The first panel documents two feasible constructions. The measured-sample comparisons test the accuracy of particular analyses. The 315 scored tables in the matched experiment include repeated seeds for 105 eligible programs from 36 assigned starts. [Handgrip transfer](../../work/bilateral_grip_transfer_2026-11-21/RESULTS.md) · [Iron dependence](../../work/prospective_iron_dependence_2026-11-20/RESULTS.md) · [Conventional lung solver](../../work/lung_pairing_numerical_control_2026-11-22/RESULTS.md)

## Reproduce the lead figure

With Python, NumPy and Matplotlib, run `python lipid_pairing_figure.py` from the script directory. The default reads the public aggregate and writes the figure under this release's `figures/` directory. The aggregate contains binned rank counts, screening curves and summary statistics. [Plotting script](../../work/kdd_v52_editorial_2026-11-25/lipid_pairing_figure.py) · [Figure input](../../work/kdd_v52_editorial_2026-11-25/lipid_pairing_figure_data.json) · [Vector figure](figures/lipid-pairing-overview.pdf)

Both manuscript packages use the ACM template. Import either ZIP into Overleaf and compile `main.tex`. The external copy identifies the public evidence archive. [Build record and checksums](BUILD_CHECK.json) · [External-review build record](EXTERNAL_REVIEW_CHECK.json)
