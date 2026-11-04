# Real-versus-real context for an existing virtual cohort

This new developmental evaluation responds to the user's concern that two real samples also disagree. Its question is: how large are the frozen virtual-data discrepancies beside community-disjoint resplits of the same selected CHNS sample?

The generator, its three delivered 3,000-row tables and all previous results remain unchanged. No new candidate, source search, data acquisition or clinical confirmation is part of this unit. The prior sample and synthetic results were already visible before this protocol; the repeated-split design is specified before these new calculations.

## Fixed work

1. Independently review this design and its implementation before reading patient values.
2. Reuse the exact four local CHNS files and existing eligibility/measurement rules. Verify the pinned input hashes and the 6,631-person, 218-community selection.
3. Use 100 fixed random seeds. Randomly divide communities into two groups of 109; accept using group sizes only, then sample 3,000 people per side without replacement. People and communities cannot occur on both sides of a split. No outcome matching or selection of favorable splits is permitted.
4. Apply the same two regressions and complete diagnostic set to both real halves and each frozen synthetic table. Report all nine coefficients (seven non-intercept), 21 marginal quantities and six correlations.
5. Retain each split's real-real and synthetic-real signed and absolute discrepancies, plus the symmetric synthetic discrepancy averaged over the two real sides. Summarize medians and 10th/90th percentiles in original units.
6. Independently recompute the sampling, numerical summaries and input invariance. Publish authored code, summaries and the decision; keep all participant-level data local.

## Interpretation fixed before calculation

- Real-real differences are a descriptive scale, not a learned pass threshold. No ratio, win rate, p-value, equivalence test or composite quality score will be added.
- Disjoint real halves are dependent pieces of a finite sample. Synthetic tables are fixed and do not share that dependence; matching row count does not make the discrepancy distributions interchangeable.
- These resplits preserve community separation but do not recreate CHNS's original sampling design. They do not measure differences between countries, years or clinical populations.
- A small discrepancy supports a bounded use; a large one identifies where this particular reference comparison still needs explanation. Neither proves universal validity or invalidity.
- One law with three random draws remains one scientific construction. There will be no generator retuning, replacement seeds or outcome-dependent eligibility changes.

The machine-readable [protocol](PROTOCOL.json), independent [design review](DESIGN_REVIEW.md), implementation review and freeze receipt determine the actual execution. This plan supplements historical interpretations rather than overwriting frozen findings.
