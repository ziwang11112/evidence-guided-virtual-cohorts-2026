# HRS native analysis evaluator

This directory owns evaluation and its local runtime only. It does not choose, fit or execute either cohort generator. Formal HRS generation and model fitting require the parent unit's frozen release. Preparation used invented inputs only.

## Entrypoints

`native_evaluate.R INPUT.csv OUTPUT.json` fits the native HRS longitudinal model once, with `REML=TRUE`, `optimizer="bobyqa"` and `optCtrl=list(maxfun=2e8)` as in the recipient analysis of `RCTSim2` lines 315–320. An error or unestimable coefficient writes a failed aggregate result. Warnings and singularity are retained; there is no automatic refit or optimizer retry. `run_r.py` enforces the protocol's 300-second subprocess limit and returns 124 on timeout; the supervising controller must preserve any failed or timed-out slot, including absent output.

The exact 12 columns are:

```text
id,subject_id,visit_time,baseline_age,age,age60,sex,race,educ,cses,hba1c,mem_s
```

Each of 11,509 subjects must have visits 0, 2, 4 and 6. Visit IDs are unique, and subject-level covariates stay constant. Canonical lower-case sex/race values become Female/Male and White/Black factors with explicit treatment contrasts. Education levels are College/HS/LessThanHS. The fixed references are Female, White and College. HbA1c must be positive, baseline age lies on the published [50,100] support, and all numerical fields must be finite. These are schema/support checks, not effect-size selection criteria.

The formula is:

```r
mem_s ~ age60 * (hba1c_U65 + hba1c_O65 + race + educ + sex + cses) +
  (1 + age60 | subject_id)
```

Here `age60=(age-60)/10`, `hba1c_U65=pmin(hba1c-6.5,0)`, and `hba1c_O65=pmax(hba1c-6.5,0)`. All 16 fixed coefficients, model SEs and model-conditional Wald intervals are retained. The evaluator also returns random-effect covariance/SD/correlation, residual variance/SD, REML log likelihood and criterion, convergence information, optimizer evaluations, warnings and singularity at tolerance 1e-4. Neither `computed` nor a narrow synthetic-data interval certifies biological validity or independent patient information.

The diagnostic block uses one baseline row per subject. It includes counts, age, overall HbA1c and threshold strata, all sex/race/education categories, childhood SES and baseline memory. Means use denominator n; sample SDs use denominator n-1. Pinned `RCTSim2` lines 383–403 select one first-visit row per ID for these checks. Its lines 220–221 and the original HRS code lines 40–41 define below as `<6.5` and above as `>=6.5`. A baseline row selected by explicit visit time avoids dependence on CSV ordering while preserving the native statistic.

`independent_gls.py` independently constructs the design matrix and checks coefficients and SEs conditional on native fitted variance components. It binds the input CSV hash and preserves all 16 term comparisons. Its pass verifies conditional fixed-effect arithmetic, not the optimizer, variance estimates or clinical truth. See [INDEPENDENT_GLS.md](INDEPENDENT_GLS.md).

## Local runtime

Run from WSL Ubuntu-24.04 with `python3 run_r.py native_evaluate.R INPUT.csv OUTPUT.json`. `run_r.py` prepends only the extracted project libraries and local NLopt shared library for that subprocess. It does not mutate the system library, shell profile or global environment.

The preparation uses the already installed R 4.3.3 and Ubuntu binary packages: lme4 1.1-35.1, Matrix 1.6-5, minqa 1.2.6, nloptr 2.0.3, RcppEigen 0.3.4.0.0, jsonlite 1.8.8, MASS 7.3-60.0.1, nlme 3.1-164, boot 1.3-30 and libnlopt0 2.7.1. Existing system Rcpp 1.0.12, lattice and statmod satisfy the remaining runtime imports. The original repository reports R 4.0.1/lme4 1.1-23; this is a compatible current native-method analysis, not a bitwise historical-runtime rerun.

Exactly 14,514,632 dependency bytes were downloaded across ten archives (about 13.84 MiB; limit 200 MiB). `runtime/DEPENDENCY_DOWNLOADS.json` records every actual size and SHA256, matched against apt metadata. No `apt install`, sudo, account, system-package change, patient data, source fitting, model training or HPC was involved. One initial shell invocation did not expose the project library to R; the dedicated subprocess wrapper corrected that mechanical environment issue before the successful load check.

Keep `runtime/debs`, `runtime/extracted` and `invented*_local` directories local. The runtime ledger and version metadata may be shared separately. The extracted distribution files are not original research code.

## Preparation checks

- Independent GLS's five invented-array checks passed, including deliberate coefficient perturbation, scale/covariance rejection and reference-category coding.
- One distinct end-to-end fixture used 120 invented subjects and 480 visits. All ten native schema/fit checks passed: duplicate ID, bad time, changing baseline attribute, noncanonical factor and missing value were rejected. A single native lme4 fit returned all 16 coefficients, no warnings and no singularity.
- The independent GLS checker passed on that same invented fit; see `INVENTED_GLS_CHECK.json`.
- Direct reading of the pinned recipient code then identified its explicit bobyqa optimizer, which differs from the source-data export's default optimizer. The evaluator was corrected before release. A new invented-only check under the native recipient setting is recorded separately; the earlier default-optimizer check is retained as preparation history, not a scientific result. No formal HRS table was generated or fitted in preparation.

Source alignment, clinical release and actual-result evaluation remain separately recorded by the parent unit. Do not rerun successful preparation tests without a substantive implementation change.
