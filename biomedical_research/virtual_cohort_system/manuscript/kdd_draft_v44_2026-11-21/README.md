# Which Scientific Analyses Can Agent-Generated Biomedical Cohorts Support?

KDD Research working manuscript v0.44, 21 November 2026. Holding each hand's observed-value grid fixed lets us measure exactly what changes when an agent assigns a left and right hand to each virtual person. We sealed eight programs and their predictions before comparing them with paired measurements from 4,321 adults across three settings. [External review PDF](external_review.pdf) · [Anonymous PDF](paper.pdf) · [External review Overleaf source](overleaf_external_review_v44.zip) · [Anonymous Overleaf source](overleaf_v44.zip)

## A short route through the evidence

| Page | Figure or table | What the comparison shows |
|---|---|---|
| 2 | Figure 1 | Published iron-status counts fix one odds ratio but leave the continuous pairing open. |
| 3 | Figure 2 | Re-running the same lifestyle regression on virtual records preserved the Kenyan urban BMI contrast more closely than the rural lipid contrasts. Real–real draws put those discrepancies in context. |
| 6 | Figures 3 and 4 | Restoring each agent's iron pairing improved rank-correlation accuracy in all six CHNS constructions. In lipids, four authors gave paired alternatives with the same published summaries and materially different screening rates. |
| 7 | Figure 5 | Giving authors two historical US means increased screening error on the original lipid pairing in both later periods. The effect of that same update varied across alternative pairings. |
| 7–8 | Figure 6 and main text | Four grip authors chose a common within-person pairing from separate Australian hand summaries. It predicted 3.81 kg for the absolute hand difference, compared with 3.30 kg in the US and 3.78 kg in rural South Africa. Independent pairing gave 7.93 kg. South African mean grip strength was overestimated by 7.81 kg. |
| 19–21 | Figures 15 and 16, Table 8 | The Virginia pre-disclosure decisions and all six later US lipid analyses are retained. |
| 22 | Table 9 and Figure 17 | All grip targets, the four requested analyses and a same-evidence statistical model appear together. The sensitivity curve shows how wide a range of correlations can support the primary use. |

The handgrip primary comparison covers 3,857 measured adults. An additional 464 Brazilian participants form the prespecified maximum-of-three measurement check. Only aggregate results and original code are distributed. [Full study report](../../work/bilateral_grip_transfer_2026-11-21/RESULTS.md) · [Study design](../../work/bilateral_grip_transfer_2026-11-21/PROTOCOL.md) · [Predictions before disclosure](../../work/bilateral_grip_transfer_2026-11-21/BEFORE_DISCLOSURE.md) · [Independent computation](../../work/bilateral_grip_transfer_2026-11-21/VERIFICATION.json)

Both Overleaf archives compile from their top-level `main.tex`. The anonymous edition contains no repository review header. The linked edition adds four repository links in the first-page margin. The scientific page images match below that header. The PDF has 22 pages, with references beginning on page 8 and the appendix on page 9. [Build and ZIP checks](BUILD_CHECK.json) · [Linked edition checks](EXTERNAL_REVIEW_CHECK.json) · [Editable overview](figures/evidence-and-pairing.drawio)

From the virtual cohort project root run `python -B work/bilateral_grip_transfer_2026-11-21/verify.py --public-only` to check all ten predictions, use margins, comparison extrema and the pairing-invariant mean. The private-data verification additionally recomputes the estimates and intervals from the original studies. The preceding manuscript remains available in the [v0.43 release](../kdd_draft_v43_2026-11-21/README.md).
