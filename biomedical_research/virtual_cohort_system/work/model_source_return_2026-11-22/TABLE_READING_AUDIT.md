# Independent audit of the selected agreement table

**Finding.** For the device pair the Agent requested, all three extracted estimates, their intervals, the subtraction order, and the unit agree with the original table image. The decision to revise followed this single read. The Agent did not request a second table.

## Material and check

A separate reviewer visually compared the original pixels with the saved reader response, then checked the article's agreement methods and the handoff record. The selected source is Hong et al., PMC3343442, version 1, Table 3. Its image SHA-256 is `c13b2153251a012a5055d5edbd0b99f7310d77a789173f2500e05bec8f33afbf`. The handoff records this digest and the exact response digest `fcd94bb877349429322344c4d14cfac9c7d4e6a7178c3c914727134bb15234f1`. [Original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3343442/)

| Requested row | Column | Printed estimate, µm | Printed 95% CI, µm | Check |
|---|---|---:|---:|---|
| Visante minus SL-US | Mean difference | −3.6 | −5.3 to −2.0 | Match |
| Visante minus SL-US | Lower limit of agreement | −14.9 | −17.7 to −12.1 | Match |
| Visante minus SL-US | Upper limit of agreement | 7.6 | 4.8 to 10.4 | Match |

Each confidence interval describes uncertainty in its own column estimate. None gives the percentage of eyes whose absolute difference exceeds 20 µm. The table has no population or visit label for this row. Leaving those fields empty in the table extraction was appropriate. The reader also correctly recorded the absence here of device-specific thickness means and SDs, a paired-difference SD, and an averaging-correction footnote.

## What the readings support

The article's methods separately state that the investigators averaged three measurements and corrected the SD because averaging reduced within-eye measurement error. They used the corrected SD for agreement limits intended to enclose 95% of differences. Under a symmetric normal-limit convention, the published endpoints imply an approximate corrected agreement SD of (7.6 + 14.9) / (2 × 1.96) = 5.74 µm. Their midpoint is −3.65 µm, compatible with the displayed mean after rounding. This SD is a derivation. Estimating the empirical SD of three-reading averages would require additional information.

The published signed mean and interval support a comparison of mean device readings under the study protocol. The two limits constrain the spread of disagreement. The article table supplies no observed exceedance count or denominator for the requested strict threshold. Generation under different tail shapes can demonstrate sensitivity of that proportion. This audit establishes extraction and interpretation accuracy for the one selected row.
