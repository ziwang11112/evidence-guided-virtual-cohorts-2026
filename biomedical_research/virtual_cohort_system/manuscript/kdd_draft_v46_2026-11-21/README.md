# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript v0.46, 21 November 2026. We ask a scientific agent to build a virtual biomedical cohort from published evidence and a research request. We evaluate which analyses of that cohort agree with measurements and how much of that agreement depends on the way the agent pairs observations. [External review PDF](external_review.pdf) · [Anonymous PDF](paper.pdf) · [External review Overleaf ZIP](overleaf_external_review_v46.zip) · [Anonymous Overleaf ZIP](overleaf_v46.zip)

## What the literature adds

Eight published papers and one ongoing YODA proposal were added. The introduction credits prior clinical reanalysis on synthetic data. The related-work section distinguishes the inputs to patient agents, results already determined by statistical summaries, and analyses that can vary with the generator. The accompanying comparison identifies each study's construction inputs, its reference and the quantity the authors evaluated. [Related-work comparison and primary sources](RELATED_WORK.md)

## Where to find the scientific evidence

| Question | Manuscript | Supporting records |
|---|---|---|
| If the scientific analysis stays fixed, do the results carry over to virtual records? | Figure 2, p. 3. The Kenyan urban BMI difference was 1.88 kg/m² in measured participants and 2.05 and 1.97 in the two agent constructions. The urban total cholesterol difference was smaller on both virtual cohorts. | [Analysis replay and all nine contrasts](../../work/kdd_v45_build_2026-11-21/ANALYSIS_REPLAY.md) |
| What does the evidence determine, and what does individual pairing contribute? | Figures 1 and 3, pp. 2 and 5. Threshold counts anchor the odds ratio. Continuous associations still depend on how measurements are coupled within a band. | [CHNS community holdout](../../work/chns_iron_conditional_holdout_2026-11-19/RESULTS.md) · [Within-band pairing comparison](../../work/chns_statistical_comparator_2026-11-19/RESULTS.md) |
| How much can that choice matter in a second scientific use? | Figure 4, p. 7. Constraints on the same lipid measurements admit different screening fractions at the same threshold. | [Matched lipid constructions](../../work/kdd_v40_pairing_review_2026-11-20/REVIEW.md) |

This edition revises the introduction, the contribution wording and the related-work section. The numerical results come from the v0.45 experimental record. The 23-page anonymous manuscript and the linked external edition compile from the supplied archives. [Build checks](BUILD_CHECK.json) · [External-edition checks](EXTERNAL_REVIEW_CHECK.json) · [Previous manuscript](../kdd_draft_v45_2026-11-21/README.md)
