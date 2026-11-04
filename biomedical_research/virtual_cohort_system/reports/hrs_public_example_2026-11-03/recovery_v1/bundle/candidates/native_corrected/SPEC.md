# Recovery v1 correction

The initial native preflight PASS was overturned after a CRLF section-boundary extraction defect was discovered. This package corrects only the seven Gamma HbA1c coefficients and SEs/provenance from the original pinned source. The generator bytes and scientific law are unchanged. See repair_audit.json and the recovery incident record.

# Published HRS recipient-law adapter

This is an original NumPy/Pandas implementation of the HRS recipient-stage rules in Filshtein et al. (2021), using the public parameter export at commit `6708e43d5e342fa76d57b31d5a6d0bfcc2979539`. It is the HRS pre-imputation component, with no ARIC generation, pooling or MICE. It does not recreate the unavailable fitted R objects or the source individual records. It is a reconstruction of the published rounded law, not bitwise reproduction of the authors' simulation.

## Inputs and evidence

`sources/SOURCE_MANIFEST.json` binds five exact original files by SHA256 and Git blob SHA1. `parse_sources.py` verifies these hashes, then parses all numerical generation parameters from the printed export; age bounds and time transformations come from the original R text. It neither imports nor executes R code. Source-file line locators accompany each parameter in `sources/HRS_SOURCE_EVIDENCE.json`. Values are never fitted to the target diagnostics. Standard errors in that packet document reported uncertainty; the fixed native law does not resample its coefficients.

The evidence packet and `HRS_DATA_SCHEMA.json` are source-facing artifacts. `generator.py`, this specification and its math tests are native-reference implementation artifacts, and do not belong in the fresh Agent common packet. Coordinator registration/approval is separate from this preparation.

## Native probability law

1. Sample each subject's age-category/sex/race cell independently with replacement using public cell counts divided by their total. Generate continuous baseline age uniformly within the source cell bounds. The oldest source-code bin is [80,100], while the other six span five years. Do not force exact category quotas.
2. Set baseline age60 to (baseline ageâˆ’60)/10. Generate CSES from the conditional normal linear model with its printed residual SD.
3. Form multinomial education probabilities from the two printed coefficient vectors and a zero College logit. Use stable softmax and one categorical draw; College is the reference, followed by HS and LessThanHS.
4. Generate HbA1c from Gamma(shape=1/phi, scale=exp(X beta)*phi), where phi is the printed Gamma dispersion. Its conditional variance is phi times squared conditional mean.
5. Draw a zero-mean bivariate Gaussian random intercept and random slope. The covariance off-diagonal is printed intercept SD times printed slope SD times printed correlation; diagonal entries are squared printed SDs. This follows the RCTSim1 covariance construction. Separately printed rounded variances are retained as provenance and are not substituted.
6. Expand to visits 0,2,4,6 years. Set age=baseline age+visit time and age60=(ageâˆ’60)/10. Form HbA1c branches min(HbA1câˆ’6.5,0) and max(HbA1câˆ’6.5,0). Memory equals the complete 16-term fixed predictor plus subject intercept plus age60 times subject slope plus independent normal visit residual with printed SD.

All coefficients, SDs, correlation, dispersion, counts and bounds are read from `spec['parameters']`, shaped exactly like `HRS_SOURCE_EVIDENCE.json`. No scientific parameter is embedded in `generator.py`. It has no fitting, posthoc moment matching, clipping, truncation or search. Helpers are explicit NumPy math, not an invocation of an author model object.

## Contract and interpretation

`generate(observed, spec, seed)` is synchronous and returns a DataFrame. Whole-cohort input may be None or an empty DataFrame. The seed controls a local NumPy Generator; there is no shared random state, network access or runtime file read. NumPy and R streams need not agree. The unused original `age70` random jitter is omitted because neither native memory generation nor the evaluated model uses it.

The required 12 fields are `id`, `subject_id`, `visit_time`, `baseline_age`, `age`, `age60`, `sex`, `race`, `educ`, `cses`, `hba1c`, `mem_s`. IDs are strings, with one unique visit ID and one repeated subject ID; factor levels are female/male, white/black and College/HS/LessThanHS. Baseline covariates remain constant across a subject's four visits. Native design is 11,509 subjects and 46,036 observations; the source fitted model used 43,500 observations. Balanced follow-up is a published generation choice, not recovery of the original missingness pattern.

The native analysis is the source Gaussian REML mixed model with all seven predictors interacted with age60 and correlated subject intercept/slope, using lme4 bobyqa and maxfun=2e8. Focal terms are the two HbA1c-by-age60 interactions. All fixed effects and baseline diagnostics remain reportable; this adapter does not evaluate or select itself. Published Tables 2/3 are rounded author-reported references, not newly recomputed real-data truths. Three new seeds cannot reproduce the paper's 5,000-iteration Monte Carlo precision.

The conditional families, dependencies, normal residuals and uniform-within-bin ages are the predecessor's supplied scientific modeling choices. Treating these as the common permitted input is an explicit rich-summary recipient-stage task. Performance on this task establishes consistency and utility within that exposed information regime; it does not establish independent discovery of those choices or heterogeneous-literature transport.

## Validation boundary

`test_analytic_helpers.py` only evaluates deterministic invented softmax, Gamma moments, named linear terms and random covariance; it never calls `generate`, draws random values, fits a model or uses HRS clinical parameters. Complete generator execution, including an invented fixture, belongs to the coordinator's isolated backend. No HRS generator call or clinical fit was performed during adapter preparation.

Original repository artifacts have no explicit license and stay local; this adapter is new implementation code. Do not redistribute or relicense the original source files as part of project code.
