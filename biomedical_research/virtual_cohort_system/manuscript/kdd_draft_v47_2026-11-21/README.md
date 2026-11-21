# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript, v0.47, 21 November 2026.

[External review PDF](external_review.pdf) · [Anonymous PDF](paper.pdf) · [External review Overleaf source](overleaf_external_review_v47.zip) · [Anonymous Overleaf source](overleaf_v47.zip)

The agent reads published evidence and writes a joint sampling model for a requested analysis. We substitute its virtual records for measured records in the same estimator. Holding the individual measurements fixed and changing their pairing isolates which results depend on the agent's modeling choice.

| Where to look | Scientific question |
|---|---|
| Page 2, Figure 1 and Table 1 | Which aspects of a generated cohort does a source table determine? Which five analyses and twelve study families does the paper evaluate? |
| Page 4, Figure 2 | Does replacing measured Kenyan participants with virtual participants preserve all nine adjusted lifestyle contrasts in their original units? |
| Page 5, Figure 3 | With both iron-status columns fixed, what changes when the values are paired differently in the same individuals? |
| Page 6, Figure 4 | How well does the same handgrip cohort estimate a mean difference in four demographic groups and the fraction exceeding a specified threshold? |
| Page 8, Figure 5 | When the lipid margins are compatible with different pairings, how stable is a screening conclusion? |
| Page 24, Table 11 | What are the measured subgroup sizes and intervals, each agent comparison and the matched statistical control in all three grip settings? |

The new subgroup analysis uses previously frozen models and disclosed sites. The primary pooled handgrip predictions were sealed before the paired measurements were opened. The scale inventory separates measured recruitment samples, study families, initial construction sessions and seeded program outputs. [Subgroup results, figure, code and counting receipts](../../work/kdd_v47_scale_2026-11-21/RESULTS.md) · [Original prospective comparison](../../work/bilateral_grip_transfer_2026-11-21/RESULTS.md)

[Related work and direct comparisons](RELATED_WORK.md) · [Kenyan reanalysis checks](../../work/kdd_v45_build_2026-11-21/ANALYSIS_REPLAY.md) · [CHNS held-out community results](../../work/chns_iron_conditional_holdout_2026-11-19/RESULTS.md) · [Build verification](BUILD_CHECK.json) · [External edition checks](EXTERNAL_REVIEW_CHECK.json)
