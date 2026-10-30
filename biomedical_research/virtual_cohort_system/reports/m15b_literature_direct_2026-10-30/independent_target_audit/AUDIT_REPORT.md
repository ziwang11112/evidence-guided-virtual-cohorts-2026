# Independent post-release numerical and dataflow audit

The independent audit was executed once after the root controller explicitly authorized the final freeze and evaluation release. All 24 reference/initial/final estimands and the four global reference sensitivity analyses were retained. The original evaluator implementation was never read or imported; only its documented release interface and released aggregate output schema were used.

The nine manifest hash commitments match, including both frozen candidate tables and the precommitted reference. All 200 identities, row order, race/sex values and exact decimal age/BMI values are preserved, with 50 people per group. Initial and final have **zero changed urate rows** and identical table hashes: they are **one unique candidate table**, not two cohorts or evidence replications.

The 72 labeled estimates (24 each for reference, initial and final), 116 joint-PSU deletion coefficient fits (29 groups by four endpoints), four full reference fits and eight range endpoints agree with the released evaluator up to ordinary floating-point roundoff. No sample-count, matrix-rank, status, null, sign-stability or deletion-identity discrepancies were found. The largest absolute discrepancy among estimates and PSU results is `4.440892098500626e-15`. All 24 released CSV rows and 576 checked fields agree exactly with the released JSON. All 48 generated-minus-reference differences were also checked: their largest absolute discrepancy is `7.105427357601002e-15`, and all reported comparison signs agree.

| Global estimand | Reference | Initial = final | Generated minus reference | Reference joint-PSU range |
|---|---:|---:|---:|---|
| BMI / 5 kg/m² | 0.335316349 | 0.345445580 | 0.010129231 | [0.316327915, 0.358386579] |
| Age / 10 years | -0.155459191 | 0.069342650 | 0.224801841 | [-0.179629609, -0.118876495] |
| Squared scaled BMI | -0.031675765 | -0.039251727 | -0.007575962 | [-0.036090499, -0.025591275] |
| BMI × male | 0.049715907 | 0.069171079 | 0.019455171 | [0.010227496, 0.143223250] |

All four reference coefficients retain their full-fit sign across all 29 deletions; no deletion fit or rank failures occurred. These ranges are descriptive sensitivity of the fixed quota subset, not confidence intervals or national-population uncertainty.

The age coefficient is negative in the measured reference and positive in the generated table; every reference age deletion estimate remains negative. The other three global signs agree, which does not establish general analytical usability. This audit supplies numerical/dataflow corroboration of the same fixed analyses, not a new validation dataset, experiment, scientific pass/fail criterion, candidate choice, or repair.

Complete aggregate results are in `released_audit_results/independent_audit.json` and `independent_estimands.csv`; comparisons, bindings and artifact hashes are in `released_audit_results/audit_checks.json`. `canonical_released_aggregate.json` retains the transparent output mapping and source aggregate hashes. No participant rows are exported in these artifacts. The 14 pre-release tests used invented data only.

The gate verifies committed bytes. Source review, lifecycle checks, reviewer identity and commitment timing remain controller assertions; no OS isolation or independent provenance proof is claimed.
