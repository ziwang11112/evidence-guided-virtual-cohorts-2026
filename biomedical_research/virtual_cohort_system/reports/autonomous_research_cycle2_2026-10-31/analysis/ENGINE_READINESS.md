# Fixed analytical engine readiness

Date: 2026-10-31. Scope: analytical implementation and artificial arithmetic validation only. No reference participant records, target effects, scientific generator outputs, or generated.csv were read or created. No existing project module was changed. All fixtures were constructed in memory and are test inputs, not biomedical candidate cohorts.

**Current result: 28 of 28 tests passed; bounded independent review PASS.** Test execution took 0.567 seconds; subprocess wall time was 1.1531050000339746 seconds. The independent post-correction arithmetic check took 0.342 seconds. This supports engine readiness for hash-bound integration. It does not release the target reference, establish preparation readiness, or authorize candidate generation/evaluation. Independent code review and arithmetic are recorded separately below.

## Files and public interface

- `analytical_engine.py`: pure pandas/NumPy functions with no file/network I/O.
- `test_analytical_engine.py`: artificial factorial, arithmetic, invalid-input, and resampling checks.
- `logs/test_run_04.log`: final full-suite result.
- `logs/engine_verification_manifest_final.json`: final implementation/test hashes and runtime environment. The earlier manifest is retained as an intermediate record.

`analyze_cohort(frame)` returns the questions, secondary glucose coefficient, all five fields' standardized descriptive summaries, Q1 residual RMS, model coefficients/rank diagnostics, and eight demographic counts. `demographic_weights(frame)` returns the exact prescribed row-weight formula. `cluster_stability(frame, attempts=399, seed=18301)` returns the point result, all 31 reported estimands' stability bands, attempted/valid/failed counts, failure categories and attempt indices, and valid replicate estimates. `draw_cluster_indices(frame, rng)` exposes the represented-cluster draw for arithmetic verification.

Required fields are `age`, `female`, `bmi`, `glucose`, and `hba1c`. Every value must be finite; age must be an integer from 25 through 79; female must be 0 or 1; BMI, glucose, and HbA1c must be strictly positive; glucose must be below 126 mg/dL. Any invalid row rejects the input table: there is no silent filtering, clipping, imputation, or data-dependent repair. Resampling additionally requires nonmissing `lab_est_dis` and `lab_upm_dis` identifiers. Extra columns are not analyzed.

The engine accepts unbalanced cell sizes for the reference. Exact generated cell counts (250 in each cell), reference execution floors (at least 30 per cell and at least 400 total), upstream diagnosis/fasting/pregnancy/measurement eligibility, and candidate/source release are separate controller/custodian checks. Source-context feedback uses its separate harness, not this target-population input operator.

## Frozen arithmetic

The eight cells cross age intervals `[25,40)`, `[40,55)`, `[55,70)`, `[70,80)` with female 0/1. Each row receives `1/(8*n_h)`; every cell must be represented. Reference and generated tables use this same estimator.

The full model is HbA1c on intercept, `(age-50)/10`, female, `(bmi-25)/5`, and `(glucose-100)/10`. Q1 is its age coefficient and Q3 its BMI coefficient. Q2 omits glucose and reports the BMI coefficient. Q2 minus Q3 is the descriptive BMI coefficient change after glucose adjustment, with no causal interpretation. The secondary model omits BMI and reports its glucose coefficient. HbA1c coefficients are in percentage points per stated predictor unit.

Fits use square-root-weighted `numpy.linalg.lstsq`. An explicit SVD requires full column rank under `max(n,p)*epsilon*s0`; the corresponding relative cutoff is passed to least squares. Cluster multiplicity is represented by actual duplicate rows, so n is the expanded replicate's row count. Exact and near-singular designs are rejected.

Means divide weighted totals by total weight. SDs use the weighted population second central moment with no degrees-of-freedom correction. The 0.1/0.5/0.9 quantiles are inverse-CDF values: the smallest observed value whose cumulative weight reaches the requested mass, with no interpolation. Original sorted row weights use Neumaier compensated cumulative summation; tied masses are not rounded separately. The threshold is q times the final cumulative mass, without an added tolerance. Q1 residual spread is the weighted residual RMS, also without a degrees-of-freedom correction.

## Fixed empirical stability scheme

Clusters are pairs `(lab_est_dis, lab_upm_dis)` among the rows supplied to the engine. Within each represented lab stratum with c represented eligible PSUs, draw c PSUs with replacement and carry every row of each selected cluster, including duplication. A singleton cluster appears exactly once and consumes no random-number draw. Strata and PSUs use first appearance order in the input table; the frozen input row order therefore fixes random-stream assignment.

The default is **399 attempted replicates, NumPy default_rng/PCG64 seed 18301**. The eight demographic weights are recomputed in each expanded replicate. An original row with cluster multiplicity m consequently contributes `m/(8*sum(cell multiplicities))`. Empty demographic cells and singular designs invalidate that replicate. No extra draw replaces a failed attempt. The failure record distinguishes these two categories and retains attempt numbers. An invalid original table or an unexpected error stops the call rather than being hidden as an expected replicate failure.

Bands use only valid replicates, at NumPy `percentile(..., [2.5,97.5], method="linear")`. If none are valid, every band is unavailable and the result explicitly reports that status. Outputs label these empirical cluster-resampling stability bands, conditional on the observed eligible reference, without a confidence-coverage or national design-based interpretation. No survey expansion weights or synthetic p-values are used. Seeds 18203, 18211 and 18223 are reserved as future generator analytical seeds and are not used to construct these fixtures.

## Validation evidence and retained failures

The suite checks equal-cell mass, an unbalanced eight-cell table against independent arithmetic, known full/reduced projection coefficients and scales, the analytically derived correlated-glucose BMI coefficient change, population SDs and an orthogonal-contrast residual RMS, inverse-CDF ties/endpoints, repeated-support quantile invariance, age boundaries, invalid values and missing cells, exact/numerical rank rejection, explicit SVD tolerance, pair-defined PSUs, complete duplicate clusters and singleton handling, recomputed multiplicity denominators, fixed failure counts, unavailable zero-valid bands, hand-interpolated percentile endpoints, reproducibility, and input immutability.

- `logs/test_run_01.log`: 25 tests ran; 23 passed and two failed because the initial test literals for expected random counts were incorrect. These failures were not removed from the record.
- `logs/independent_rng_enumeration.log`: direct enumeration of the seeded random choices, without importing the engine, established 193 unequal and 206 equal pairs across 399 attempts; the first nine have three unequal and six equal pairs. A two-sex-cluster fixture is valid exactly for unequal choices; a two-BMI-cluster fixture is full rank exactly for unequal choices. These independent counts corrected the test expectations.
- `logs/test_run_02.log`: all 25 tests passed after those test corrections.
- `logs/quantile_invariance_probe.log`: a separate repeated-support probe exposed ordinary cumulative-sum rounding at the half-mass boundary. The recorded failures include age, BMI, glucose, and HbA1c medians. The engine was corrected with compensated summation and a permanent invariance test.
- `logs/test_run_03.log`: all 27 then-existing tests passed after that correction and the added target physical-validity checks. This intermediate run was superseded by the independent review finding below.
- `logs/independent_review_report.md`, `logs/independent_review_arithmetic.json`, and `logs/independent_review_quantile_reproduction.json`: a separate agent audited the code and compared 80 artificial unbalanced tables with independent normal-equation fits and exact-Fraction quantiles. Maximum WLS coefficient disagreement was 3.91e-14. One of 1,200 quantiles exposed another half-mass boundary problem caused by separately rounded tied-value subtotals. The original finding and artificial reproduction are retained.
- `logs/test_run_04.log`: all 28 tests passed after accumulating original weights directly with Neumaier compensation and adding the independent review's precise regression case. This is the final full-suite result.
- `logs/independent_review_verification_after_fix.md` and `logs/independent_review_arithmetic_after_fix.json`: the independent agent repeated the same 80-table arithmetic check on the final implementation hash. All 1,200 exact-rational quantile comparisons agreed; independent WLS coefficient disagreement remained at most 3.91e-14. The bounded review reports PASS with no outstanding blocker. Original failed-review artifacts remain intact.

Environment: Python 3.12.10; NumPy 2.4.5; pandas 3.0.3; Windows. Execution command from this directory: `python -B -m unittest -v test_analytical_engine`. Test subprocess output and actual elapsed time are retained in the logs; no unperformed checks are claimed.

## Bound implementation

SHA-256 of `analytical_engine.py`: `1799c017b60f8fd3a9af409a524d3ebd9e54c81016e52da760aeafaefe03289d`.

SHA-256 of `test_analytical_engine.py`: `508d6ee0985897c831ed9af1750768b8d853330622742f6b8f52c714afa62e93`.

The module has no target data access and cannot certify custody, source evidence admission, generator isolation, or preparation correctness. Those remain separate release gates.
