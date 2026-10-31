# Final independent M17-B audit

31 October 2026. Actual-table audit performed only after explicit root release in `TARGET_RELEASE.json`.

**Numerical verdict: PASS.** The frozen auditor raw result remains `review_required`; its four schedule flags are explicitly adjudicated route-label false alarms, not silently erased. The separate adjudication establishes that all six actual receipts use the harness route `generator.py`, whereas the frozen schedule classifier recognized only `program`. The frozen script, raw result, reference, candidates and retained outputs were not edited.

The independent calculation used statsmodels formula fits with HC3 and patsy prediction contrasts, not the custodian array-fit functions. All 1,482 primitive fields (including labels and counts) matched the custodian evaluation; the largest numeric absolute difference was 3.68594044175552e-14, below the predeclared relative 1e-8 / absolute 1e-10 tolerances. No regression analysis failed. The 96 comparison rows and 32 realization-range rows independently match the exported custodian CSVs.

The release-bound pre-release snapshot was hash-verified: 57 files and three directory memberships. The companion checked 147 immutable paths before and after, including release/results, snapshot files, all receipt-listed assets, final-versus-initial code/specification identities, and execution output bindings. Every actual table has 320 rows and 40 records in every sex-by-age cell.

There are 12 scheduled initial/final entries, six unique generated paths, six unique generated content hashes, and six successful seeded execution receipts: seeds 17111, 17112 and 17113 for each builder. Each initial entry explicitly reuses the corresponding final execution because generator and specification bytes are identical. All 48 paired endpoint differences (final minus initial) and all 48 changes in absolute target difference are zero. This is retention, not a measured repair benefit.

## All eight analyses

Ranges below span the three prespecified draws, not uncertainty intervals. Differences are generated minus reference. Reference intervals are normal 95% HC3 intervals. BMI effects use mg/dL per 5 kg/m2; age uses mg/dL per decade; female contrast and curvature use mg/dL; the interaction uses the female-minus-male difference in the BMI effect. Reverse effect uses kg/m2 per mg/dL.

| Endpoint | Reference estimate [95% CI] | Reference HC3 SE | b1 estimate range | b1 signed-difference range | b2 estimate range | b2 signed-difference range |
|---|---:|---:|---:|---:|---:|---:|
| Adjusted BMI effect | 0.272 [0.182, 0.362] | 0.046 | 0.308 to 0.468 | 0.036 to 0.196 | 0.256 to 0.327 | -0.016 to 0.054 |
| Adjusted age effect | 0.148 [0.069, 0.228] | 0.040 | 0.143 to 0.210 | -0.005 to 0.061 | 0.161 to 0.180 | 0.013 to 0.031 |
| Adjusted female contrast | -1.282 [-1.550, -1.014] | 0.137 | -1.571 to -1.333 | -0.290 to -0.051 | -1.495 to -1.229 | -0.213 to 0.053 |
| BMI curvature | -0.039 [-0.127, 0.048] | 0.045 | -0.196 to -0.104 | -0.157 to -0.065 | -0.017 to 0.007 | 0.022 to 0.046 |
| BMI-by-sex interaction | -0.000 [-0.198, 0.198] | 0.101 | -0.190 to 0.118 | -0.189 to 0.118 | -0.071 to 0.082 | -0.071 to 0.083 |
| Male BMI effect | 0.272 [0.108, 0.437] | 0.084 | 0.240 to 0.584 | -0.033 to 0.311 | 0.252 to 0.339 | -0.021 to 0.067 |
| Female BMI effect | 0.272 [0.163, 0.381] | 0.056 | 0.358 to 0.394 | 0.085 to 0.122 | 0.259 to 0.363 | -0.013 to 0.091 |
| Reverse urate effect | 1.528 [0.847, 2.208] | 0.347 | 1.303 to 1.873 | -0.225 to 0.346 | 0.977 to 1.395 | -0.551 to -0.133 |

## Substantive interpretation and boundaries

The forward adjusted BMI relationship illustrates mixed transfer: b1 overestimates it in all three draws (difference +0.036 to +0.196), while b2 is closer in this particular comparison (−0.016 to +0.054). That pattern does not establish overall superiority: the reverse urate relationship is lower than reference in every b2 draw (−0.551 to −0.133), whereas b1 straddles it (−0.225 to +0.346). Cross-builder random streams and dependence assumptions both differ, so this is not an isolated causal comparison of one modeling component. No builder or seed should be selected after seeing these results.

Reference intervals for curvature and the BMI-by-sex interaction span zero. Their point-estimate signs cannot establish reliable directions. b1 consistently induces a more negative curvature estimate; b2 is near zero. The reference uncertainty and assumption-induced structure prevent turning this comparison into evidence of equivalent curvature or discovery of a new biological mechanism. No composite success threshold or equivalence margin was introduced.

Both builders reproduce the directions of the reference age and female contrasts, but the demographic directions were encoded through reported sex differences and assumed age/sex interpolation. The forward BMI and subgroup relationships were not directly fitted target values, yet they are derived from source-supplied reverse slopes, margins and dependence assumptions. The pre-release exposure classification correctly treats this as transfer and analytical reuse, not an uninformed discovery.

Distribution diagnostics help explain limitations: reference mean BMI is 29.182 kg/m2, while the six generated means range from 27.137 to 27.780. The deficit is especially clear in women: reference mean 29.610 and SD 7.999 versus generated means 26.815–27.868 and SDs 6.037–6.730. Reference mean urate is 5.581 mg/dL, versus 5.408–5.507 generated. These results are compatible with imperfect transport of the declared source anchors; this case cannot identify which source-selection, age-shape, or distribution assumption caused each discrepancy. No parameter was changed to address them.

Both fresh constructions use nearly the same marginal anchors and age knots; dependence transport is their main scientific difference. Three seeds measure realization variability conditional on fixed assumptions, not evidence uncertainty or three independent studies. The quota cohort is unweighted and not a national population estimate. HC3 describes the selected sample/model, not NHANES complex-survey or transport uncertainty. This is one temporal validation within a survey family, not a new independent study family.

**Recommendation:** report this unit as an audited feasibility result with mixed relationship transfer and clear distribution mismatch; modify the scientific validation design before making general utility claims. Any future case should prospectively define its comparison criteria and structural sensitivity scope before new outcome access. End this unit after reporting; do not tune on this released reference or begin another target automatically.

## Auditor implementation limitation

The pre-release frozen checker used the route label `program`, while the actual harness serializes `generator.py`. This produced four false direct-table alarms in the preserved raw audit. The post-release `adjudicate_audit.py` performs no fits and runs no generator: it checks the actual route/seed receipts, explicit retention lineage and identical initial/final bytes, compares the previously computed CSVs, and records the adjudication. It also explicitly verifies the snapshot hash against the release and receipt-listed asset hashes, closing checks that the original script did not itself bind through those manifest fields. This interface limitation does not affect the independently computed numerical results; it is disclosed rather than rewriting the frozen auditor or claiming its raw status was PASS.

Audit files: `results/independent_audit.json` (unchanged raw audit), `results/numeric_comparison.json`, `results/comparisons.csv`, `results/realization_ranges.csv`, `results/paired_initial_final.csv`, and `AUDIT_ADJUDICATION.json`. Patient-level rows remain local and are not reproduced in this report.
