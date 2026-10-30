# M13-B independent pre-access scientific and code review

30 October 2026. Reviewer: `/root/m13b_audit`. **Pre-access code/arithmetic review passed; no unresolved blocking issue was found in the reviewed implementation.** This is a recommendation to proceed under the frozen protocol, not target-access authorization or a target-validity result. Root must freeze the final bytes and supply the separate authorization bound to that freeze before acquisition.

## Information boundary and scope

No real target participant rows, body-fat measurements, target-derived associations, prior target results, or NHANES body-fat scientific results were acquired or read. The reviewer read the admitted M13-A milestone and proposed protocol, current M13-B protocol/roster, evaluator, controller, custody code and preparation records. All numerical audit inputs were invented in `independent_fixture_checks.py`. The displayed sample sizes below refer only to those invented fixtures. Original published-source extraction was not repeated; this review uses the admitted source equations and M13-A provenance.

External reads were restricted to official NCHS survey-method guidance and established R survey documentation. No body-fat codebook frequency table or target outcome summary was consulted. Importing the inspected evaluator/custody modules performs no target I/O. No candidate generator was imported or executed by this reviewer.

Reviewed final evaluator SHA256: `50e3a0dd925544e7a12262877ee258fac0a554dfdc3278193aa0691770065fef`.

Reviewed final custody `prep.py` SHA256: `5ed37c5529b4f487429c81200162a79afb435ea56c9f302e5652590722b9127c`.

The controller's pre-access manifest supplies the final hashes for the protocol, roster, controller, tests and this audit. The audit does not certify files edited after its checks.

## Fixed scientific specification

The exact schedule is two builders, each initial and source-reviewed candidate, at seeds 33101, 33102 and 33103: 12 Agent tables. It is an initial/final source-revision comparison with one structural scenario per builder, not two newly chosen scenarios. One deterministic Gallagher Equation-1 reference and three Gallagher-plus-Gaussian references make 16 scheduled tables. Every table is reused for all 62 endpoints; missing/failed tables and sparse cells remain in their scheduled positions. There is no aggregate success score or target-based retention rule.

The primary estimand is the MEC-weighted, complete-covariate, valid-scan domain aged 20–59, non-Hispanic White/Black, BMI 18.5–<30. BMI 30–35 inclusive is a separate extension. The whole positive-weight, complete-design DEMO frame is retained for variance; scan completion must equal `DXAEXSTS=1`, and the endpoint must be present and finite. Code 2 is excluded. Out-of-range body-fat values cause an integrity failure, not outcome trimming. No additional health, medication, regional DXA or post hoc subgroup restriction was added.

Generator inputs are an exact whitelist of opaque ID, age, BMI, sex, the fixed `asian=0` flag and five deterministic source-equation columns. Race, SEQN, survey design, weights, scan flags and the entire DXA measurement family remain outside generator inputs. The evaluator retains the Black indicator for the prespecified adjusted projections. Current column checks reject extra DXA variables, corrupted derived covariates, changed observations and mismatched/duplicate row keys; valid row permutations are realigned by opaque key.

The scheduled estimands are means; age/BMI weighted projection coefficients; the primary-domain curvature contrast `1.28*beta_B2`; and weighted inverse-ECDF quartiles/IQR in the frozen sex/age/BMI cells. The root decision to omit Woodruff and IQR intervals is correctly implemented. It avoids any claim that those unverified intervals were validated. Quartile discrepancies are descriptive point differences.

## Independent numerical checks

`python work/m13b/audits/independent_fixture_checks.py` completed **51 independent checks, all passing**. Machine-readable evidence is in `independent_fixture_results.json`; the fixture and independently computed coefficients/covariances are retained in `invented_fixture.csv` and `independent_expected.json`. The script's inline construction is authoritative and contains no target file reads.

The independent reference obtains weighted least-squares coefficients through an SVD least-squares solve. It computes observation influence vectors using the pseudoinverse of the weighted design and then aggregates them by nested PSU. For two-PSU strata the covariance contribution is computed directly from the outer product of the difference of PSU influence totals. This is algebraically equivalent to the intended survey estimator, but does not copy the evaluator's normal-equation and centered-score implementation.

| Check | Evidence |
|---|---|
| Exact mean and full-frame domain variance | An invented four-PSU fixture with one empty-domain PSU has mean `85/3` and variance `13525/162 = 83.4876543209877`; both implementations agree. Domain df is 1, and the public sparse gate is deliberately bypassed only for this arithmetic check. |
| Independent WLS and sandwich | Main invented fixture: 96 full-frame rows, 88 domain rows, 12 full PSUs, 11 domain PSUs, 6 strata, domain df 5. Maximum coefficient discrepancy is `8.88e-15`; maximum covariance discrepancy is `3.47e-16`. |
| Domain design | Reused PSU labels are nested within strata. Empty-domain PSUs and an entirely empty-domain stratum remain in the full-frame variance. A separate three-PSU stratum checks the general `m/(m-1)` factor. Full-design singleton strata fail explicitly. |
| Invariance | Weight scaling by `1e-12` and `1e12`, and row permutation, preserve coefficients and covariance. Non-domain covariates/outcomes may be NaN without contaminating zero contributions. |
| Curvature | Direct predicted values at BMI 20, 24 and 28 equal `1.28*beta_B2`; its standard error and t interval agree independently. |
| Paired differences | Fitting generated-minus-measured rows equals the difference of fitted coefficients. Paired covariance/intervals agree independently and differ from the incorrect sum of independent variances. |
| Quantiles | Exact tied-weight thresholds, endpoints, permutation and extreme common weight rescaling return the prescribed observed values; no interpolation occurs. Invalid weights fail. |
| Gates and leakage | Rank deficiency, sparse n/Kish/PSU/df, invalid scan, physical support, domain boundaries, added DXA columns, changed covariates and unknown row IDs behave as specified. All 62 endpoint slots are retained. |
| Whole interface | Invented DEMO/BMX/DXX components pass through custody into the evaluator with the same eligible rows and exact whitelist. A zero-domain PSU is retained; opaque identifiers have the expected random-token form. |
| Scheduled release | All 16 declared failed tables remain a valid roster. Dropping a comparison or replacing initial candidates with an unscheduled candidate is rejected. |

Runtime: Python 3.12.10, NumPy 2.4.5, pandas 3.0.3, SciPy 1.17.1. WSL R 4.3.3 was available, but `survey` and necessary dependencies were absent. No package stack was installed. **This is independent formula/code verification, not an executed R survey cross-validation.**

The implementers separately report 22 evaluator tests, including an invented-file CLI evaluation with the full roster; 17 custody tests; and three controller tests including four real harness deployment freezes of invented qualification inputs. The controller tests also check deployment freeze/scientific-byte tampering before launch. Those are supporting implementation tests, distinct from the 51 checks executed by this reviewer. The temporary custody-directory workaround and retained invented test artifacts are documented in custody `validation.md`; the final top-level-only freeze enumeration excludes those temporary directories.

## Survey conventions and uncertainty

The estimator retains all full-frame PSUs and uses nested stratum/PSU identifiers. Its t denominator is the number of domain-represented PSUs minus domain-represented strata, separate from the full-frame PSU counts used in variance. These choices follow the [NCHS variance guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx). The fixed complete-case domain and absence of finite-population correction are explicit protocol choices consistent with the specified analysis.

[R survey's subset documentation](https://search.r-project.org/CRAN/refmans/survey/html/subset.survey.design.html) describes preserving original design information when restricting a survey design. [R survey's regression documentation](https://search.r-project.org/CRAN/refmans/survey/html/svyglm.html) describes model-robust design standard errors and explains that its default residual-df convention can differ from an explicitly supplied design df. This pilot deliberately uses its frozen domain-design df for all linear contrasts; it does not claim numerical identity to every software default. Full rank and positive observation residual degrees of freedom are also required. The sparse gates are pragmatic prespecified reporting safeguards, not universal NCHS reliability thresholds, and Kish n does not account for clustering.

All linear intervals are pointwise, conditional design intervals. Generated-table intervals condition on the frozen generator and realized draw; paired intervals account for shared rows and the common operator. They do not incorporate source coefficient uncertainty, source reconstruction, construction choice, transport, scanner/software differences or residual-seed variability. They are not individual prediction intervals. The three-seed mean/min/max are descriptions, not calibrated simulation intervals or multiple-imputation inference.

## Issues identified and resolved before target access

1. Initial controller/custody freeze schemas were incompatible. Custody now accepts the controller's schema, verifies relative file hashes, binds protocol/evaluator inputs and requires a separate authorization with valid chronology.
2. The initial evaluator manifest was incompatible with the controller manifest and admitted generic candidate group names. The final evaluator checks the exact frozen 16-table identities, current pre-access/protocol/evaluator bindings and complete-table content hashes. Failed tables retain endpoint slots.
3. The first controller recorded deployment identities without checking every deployment identity again immediately before generation. It now verifies the deployment freeze hash, original generator/specification hashes and harness candidate integrity before launching a run.
4. Rejection sampling at 0/100 changes the Gallagher stochastic reference's conditional mean near a boundary. The protocol now states this explicitly. The Gaussian SEE 4.31 remains an assumed individual residual law, not coefficient or transport uncertainty.

No unresolved blocking scientific or arithmetic defect remains in the reviewed implementation. The operational conditions still required are the final pre-access freeze, matching separate root authorization, preservation of every scheduled output/failure, and the single complete aggregate release. A technical repair after acquisition must retain the prior artifacts and be independently justified; it cannot change the scientific model, eligibility, comparison roster or estimand in response to target results.

## Limitations that remain, without blocking this bounded pilot

MEC weighting alone does not repair DXA nonresponse; conclusions concern the declared complete-covariate valid-scan domain. Device/software and population transport remain uncalibrated. The Thai source does not independently establish the BMI 30–35 extension; the admitted Gallagher support motivates that separate transfer test. White/Black category mapping is a transport convention, not ancestry equivalence. No Asian subgroup inference is licensed by setting the source Japanese flag to zero in the restricted domain.

The two builders largely inherit published age/BMI mean structure. Agreement in direction would test transport of that supplied structure, not demonstrate discovery of an unknown relationship. Initial-to-source-reviewed differences have limited, identifiable structural scope and must be reported along with worsening outcomes. All cell quartiles and IQR include residual covariate heterogeneity within their coarse bins and must not be described as pure residual variation.

The protocol specifies no clinical equivalence margin, calibrated utility threshold, omnibus hypothesis or simultaneous coverage. Target discrepancies can assess these particular analytical reuses; they cannot establish individual measurement recovery, clinical substitution, general biological realism, causal effects, proven measurement-cost savings, independent clinical replication or publication readiness. This is a new endpoint in an already used NHANES cycle, not a globally fresh cohort.
