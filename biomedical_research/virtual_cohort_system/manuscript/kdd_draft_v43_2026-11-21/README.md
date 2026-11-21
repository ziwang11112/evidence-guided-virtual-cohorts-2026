# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript v0.43, 21 November 2026. Scientific agents turn published biomarker summaries into executable cohorts. The same downstream analysis can be run on the virtual and measured participants. This edition asks whether adding historical national marker means improves a later screening estimate, and how the answer changes when the agent assigns the same two measurements to different virtual people. [External review PDF](external_review.pdf) · [Anonymous PDF](paper.pdf) · [External review Overleaf source](overleaf_external_review_v43.zip) · [Anonymous Overleaf source](overleaf_v43.zip)

## Where to look in the paper

| Page | Figure or table | Scientific question and result |
|---|---|---|
| 2 | Figure 1 | Four published iron counts imply the threshold odds ratio. Agents still choose how continuous measurements are paired inside each cell, which changes the rank correlation. |
| 3 | Figure 2 | In Kenya the virtual urban BMI contrast was on the scale of real-sample variation. The rural lipid contrasts departed more substantially. |
| 6 | Figure 3 | Re-pairing values within hemoglobin bands worsened correlation accuracy in all six original CHNS laws. Re-pairing age and outcomes within sex and lifestyle groups barely moved the Kenyan BMI contrast. |
| 6 | Figure 4 | The original lipid agent and the statistical generator estimated screening at 25.53% and 25.52%. Four authors then constructed pairs of alternative laws with the same input evidence. Within-author screening differences ranged from 16.37 to 29.35 percentage points. |
| 7 | Figure 5 | Four advisers shown the scenario ranges placed the largest subsequent Virginia discrepancy last. A statistical rule gave the same ranking. The top two uses did not clear their planning tolerances. |
| 8 | Figure 6 | Four fresh agents chose the same proportional update from two historical US marginal means. The estimated screening fraction rose from 25.53% to 34.25% on the original pairing, increasing error in both later survey periods. Across all eight earlier alternatives, four point predictions improved and four deteriorated in each period. |
| 20 | Table 8 | All six original and updated analyses are shown with the measured survey intervals. The original mean individual TC/HDL ratio of 3.659 was within the prespecified ±0.30 margin across the full reference intervals in both periods. |

The new panel compares two non-overlapping later periods of the NHANES family with a historical source from that same family. The 10,435 eligible individuals and 12 measured endpoints were checked with a separate data reader and estimator. The eight alternative pairings were prespecified. Ordering them within author by their starting rate was a retrospective diagnostic. Only one of the four improvements held throughout both survey intervals. All four deteriorations did. Four new authors returned one numerical transformation, also attained by a statistical rule. [Protocol](../../work/lipid_population_anchors_2026-11-21/PROTOCOL.md) · [Predictions archived before scoring](../../work/lipid_population_anchors_2026-11-21/PREDICTIONS.json) · [Complete comparison and clinical references](../../work/lipid_population_anchors_2026-11-21/RESULTS.md) · [Independent checks](../../work/lipid_population_anchors_2026-11-21/VERIFICATION.json)

## Reproduce the release

The anonymous archive contains the manuscript, bibliography and 15 vector figures. Compile its root `main.tex` with pdfLaTeX and BibTeX. The linked archive adds a reviewer header containing the public repository, frozen protocol, sealed predictions and results. The scientific pages of both PDFs are identical below the header. The reference list begins on page 8 and the appendix begins on page 9. [Build and archive checks](BUILD_CHECK.json) · [Linked-edition checks](EXTERNAL_REVIEW_CHECK.json) · [Editable overview](figures/evidence-and-pairing.drawio)

From the virtual cohort project root, run `python -B work/lipid_population_anchors_2026-11-21/verify.py --public-only` to check the public numerical results. The aggregate release includes the authors' code and decisions, the common statistical transformation and all pairing results.
