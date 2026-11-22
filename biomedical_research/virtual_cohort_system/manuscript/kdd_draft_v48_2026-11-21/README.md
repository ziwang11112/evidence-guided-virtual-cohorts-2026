# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript, v0.48, 21 November 2026.

[External review PDF](external_review.pdf) · [Anonymous PDF](paper.pdf) · [External review Overleaf project](overleaf_external_review_v48.zip) · [Anonymous Overleaf project](overleaf_v48.zip)

The agent selects a dependence model for measurements described in a paper, writes its sampler and generates participant records. We hold the component measurements fixed to isolate how the agent pairs them, then run the same biomedical analysis on measured and generated records.

| Where to look | Question answered |
|---|---|
| Figure 1 and Table 1, p. 2 | Which choices does an iron-status table leave open? Where were the six domains evaluated? |
| Figure 2, p. 4 | Do the nine adjusted Kenyan lifestyle comparisons carry over when only the input records change? |
| Figure 3, p. 5 | With marker values held fixed, how much does the agent's pairing contribute to the Chinese iron and Kenyan lifestyle analyses? |
| Figure 4, p. 6 | How well does a virtual cohort recover between-hand differences in each demographic group and the fraction exceeding 5 kg? |
| Figure 5, p. 8 | How widely can the virtual lipid screening fraction change under pairings consistent with the same source evidence? |
| Figure 20, p. 25 | With lung volumes held fixed, what happens to three scientific uses when the agent receives a published within-sex correlation and regressions? |

The lung-function comparison was registered before reading two measured samples. Supplying joint evidence moved the estimated fraction below a pre-bronchodilator FEV1/FVC of 0.70 from 25.50% to 16.26%, closer to the US (13.37%) and rural Malawi (13.81%). Agreement worsened for the mean individual ratio and correlation. A statistical rule given the same evidence predicted 16.26% below the cutoff. The frozen predictions already bounded the attainable median advantage on the primary mean-ratio comparison to 0.000101 percentage points. [Protocol](../../work/spirometry_pairing_2026-11-21/PROTOCOL.md) · [Results, uncertainty and audit](../../work/spirometry_pairing_2026-11-21/RESULTS.md) · [Independent check](../../work/spirometry_pairing_2026-11-21/verify.py)

The inventory distinguishes 17 domain-by-sample comparisons, 15 distinct recruitment samples or periods, 13 study families and ten countries. Thirteen construction experiments comprise 67 initial authoring sessions and 252 seeded agent outputs. The two model conditions in the new experiment reused the same source cohort. The US target period also supplied handgrip. [Counting details](../../work/spirometry_pairing_2026-11-21/COVERAGE.json)

[Related work and direct comparisons](RELATED_WORK.md) · [Earlier handgrip analysis](../../work/kdd_v47_scale_2026-11-21/RESULTS.md) · [Original Kenyan regression checks](../../work/kdd_v45_build_2026-11-21/ANALYSIS_REPLAY.md) · [Build verification](BUILD_CHECK.json) · [Linked-edition check](EXTERNAL_REVIEW_CHECK.json)
