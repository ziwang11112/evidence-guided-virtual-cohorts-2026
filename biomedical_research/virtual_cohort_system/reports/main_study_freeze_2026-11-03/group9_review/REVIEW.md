# Independent frozen-candidate review: ENSANUT2018_E1_A05

**Status: ready. No readiness blockers found.** Reviewer: `/root/main_review_g9`. This is an artifact, probability-law, finite-moment and numerical-uptake review. It does not certify runtime success, source-population authenticity, clinical target validity or favorable fit.

The reviewed configuration is `candidates/initial`; the decision is `initial_final`. The candidate freeze SHA256 is `5987f903d1ecbc265d89fc97664da28206698b2e1f235d4a7b4ff921a2e62de6`. The decision SHA256 is `6a623bc6ac9b58e31b23a60ac9a2e7c2794a25cfed8573c70a2ac859c8584a97`.

`lifecycle.verify_candidate(bundle, 'candidates/initial')` passed before and after the independent calculations. Frozen files and the decision were not edited. Only assigned task/input, registered sources, profile, candidate, decision, the skill/interface and explicitly authorized harness/controller modules were consulted. No target clinical data/results, other candidates, generated rows, trial outputs or coordinator outcome documents were used. No generator import or execution, row sampling, Monte Carlo, numerical quadrature, close or delivery action occurred.

## Actual law, design and moments

The implementation creates eight fixed demographic cells: female 0/1 crossed with integer ages 25–39, 40–54, 55–69 and 70–79. Each contains exactly 375 rows, giving 3000 unique sequential identifiers. Ages are discrete uniform within cells. A randomly chosen output position follows the equally weighted stratum mixture; the table is a stratified collection rather than an iid nationally representative sample.

The actual AST expressions were compared to the independently reviewed affine equations. Three independent Beta(3,3) variables become standardized residuals through `Z=(2U-1)sqrt(7)`. The beta normalizer is 1/30, E(Z)=0, Var(Z)=1, and the support closure is [−sqrt(7),sqrt(7)]. Age and sex and all residual components are bounded. Every output is affine, so absolute first moments, second moments and all cross-moments exist. There is no clipping, rejection, exponentiation or fitting to realized rows.

Independent variance calculations yield positive residual variance budgets 16.61468944 for BMI, 78.626292 for glucose, and 0.06593754656495755 for HbA1c. The affine loading matrix is lower triangular with positive diagonal and the independent component variances are positive, so the population covariance and the required predictor covariances are nonsingular. Independently computed means, covariances and raw second moments agree with the retained results in Lifelines, Pani and the task-design contexts.

Independent interval propagation of the expanded affine equations gives these task support bounds:

| Variable | Lower | Upper |
|---|---:|---:|
| BMI, kg/m² | 14.2568212010 | 38.3855787990 |
| Glucose, mg/dL | 57.9162537702 | 125.2317462298 |
| HbA1c, % | 4.1874081911 | 6.9359370466 |

All supports meet the task restrictions, with glucose strictly below 126. The Lifelines and Pani source-law glucose upper bounds are 124.4694225892 and 125.8317462298. These bounds are consequences of an assumed residual law, not established clinical cutoffs. Limited extreme-obesity and glycemic tails are disclosed limitations. Diagnosis, fasting, anthropometric and routed pregnancy/lactation criteria are membership premises; unprovided eligibility flags are not represented as measured observations.

## Source mapping and all numerical operations

All 30 candidate evidence items exactly equal the input and parsed registered source extracts. Source hashes verified. Units, source populations, selection and conditioning are retained. Jansen's original BMI coefficient converts by 0.13×0.09148; the glucose coefficient converts by 2.29×0.09148/18. HbA1c offsets apply to levels, not slopes or dispersions. Original/converted representations count as one quantity. Reported percentage-scale HbA1c moments are chosen instead of imposing the alternative rounded IFCC representations as independent constraints.

The three source constraints were recomputed independently with FWL formulas and independently formed covariance solves:

| Operation | Source context and conditioning | Recomputed coefficient | Use |
|---|---|---:|---|
| Jansen BMI | Lifelines; age, female | 0.0118924000000 % per kg/m² | Model constraint |
| Jansen glucose | Lifelines; age, female | 0.0116382888889 % per mg/dL | Model constraint |
| Pani age | NHANES approximation; female, BMI, glucose | 0.0100000000000 % per year | Model constraint |

The Jansen slopes are separate population projections. With residual scales sB, sG and assumed correlation rho, the actual model implies `tB=bB+bG*rho*sG/sB` and `tG=bG+bB*rho*sB/sG`. The solved joint coefficients are bB=0.004722025662320084 and bG=0.0109870927539898. Thus the separately adjusted source slopes were not assigned directly to the joint equation. The joint glucose-adjusted BMI coefficient, and therefore Q3, remains dependent on the assumed residual correlation 0.30 and the other completion assumptions.

Every one of the eleven non-marginal operations has one uptake record with correct source/evidence identifiers, resolving parameter/result paths, declared source law, uncertainty and overlap treatment. The remaining eight operations are analytic checks. Their conditional means follow directly from `E(H|band)=h0+kA*(E(A|band)-a0)+kF*(0.5-f0)`. The review recomputed each band probability, numerator E(H I_band), conditional mean and discrepancy:

| Pani reported band | Approximate support | Model mean, % | Reported mean, % | Difference, percentage points |
|---|---|---:|---:|---:|
| <40 | 25–39 | 5.331525976 | 5.20 | +0.131525976 |
| 40–44 | 40–44 | 5.446599297 | 5.28 | +0.166599297 |
| 45–49 | 45–49 | 5.504135958 | 5.37 | +0.134135958 |
| 50–54 | 50–54 | 5.561672619 | 5.40 | +0.161672619 |
| 55–59 | 55–59 | 5.619209280 | 5.44 | +0.179209280 |
| 60–64 | 60–64 | 5.676745940 | 5.46 | +0.216745940 |
| 65–69 | 65–69 | 5.734282601 | 5.50 | +0.234282601 |
| >=70 | 70–84 | 5.849355923 | 5.51 | +0.339355923 |

These discrepancies are correctly retained as unresolved. No favorable source fit is required for readiness. Pani's uniform age 25–84 distribution, sex probability 0.5 and upper bound 84 are unreported completion assumptions. The open-ended >=70 source category is explicitly approximated by 70–84, not silently replaced with the task cutoff 79. Neither original survey weights nor the older tail are reconstructed. Lifelines' uniform demographic completion and the equivalence of its Table 1 and Table 2 analysis populations are also explicit assumptions; row-specific Table 2 sample sizes remain unknown.

Jansen's printed coefficient interval levels are unknown and Pani's age P value provides no SE; no inferential precision was invented. The Pani band SEs remain uncertainty in survey means, not individual SDs. Within-cohort evidence and unit duplicates are not treated as independent replication. Individual residual variation, external-estimate uncertainty, structural uncertainty and transport uncertainty are distinguished. Source ancestry/recruitment, serum versus plasma, assays, fasting and eligibility differences remain unverified.

## Boundary and retained verification

All 29 numeric target-as-source recipe checks are `not_computable` with null operators. All corresponding source semantic definitions are unsupported with null operators, and all retained preflight statuses are `unavailable`; the evidence and recipe hash bindings match. Separately declared source demographic laws are propagated through the actual conditional equations. The candidate does not use a target table as source-population replay.

The independent calculation was run successfully with `python -B independent_algebra.py` (exit code 0). It retains the full moments, all eleven numerical operations, support calculations, hash bindings and zero-sampling declaration:

- Script: `group9_review/independent_algebra.py`, SHA256 `7a3034a88d25c09eace1365c4e69b95481376746bd906ad570cff7d7fa244858`.
- Result: `group9_review/independent_algebra_results.json`, SHA256 `3ad1edeac58c882f4f2e5fb1866fb17a98fa34e8116b55d9d322e74ffafb615e`.
- Machine-readable readiness: `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcMS/ENSANUT2018_E1_A05/independent_review.json`.

No changes or additional source calibration are required for this review's readiness gate. Runtime behavior and target utility remain unassessed and must not be inferred from this ready status.
