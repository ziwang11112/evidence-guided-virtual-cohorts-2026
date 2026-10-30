# M14-A independent scientific source audit

Date: 2026-10-30. Reviewer: independent agent `/root/m14a_independent_audit`.

**Conditional GO to a single source-supported conditional-mean structural sensitivity specification. NO GO to an identified source-to-target measurement correction, a repaired conditional residual law, or automatic execution.** This is an audit of evidence and identifiability. No candidate was executed; no participant rows, target outcomes, or generated rows were read. The admitted M13-B narrative report supplied development context only. No new primary study beyond the six allocated by the controller was introduced.

## Actual checks and their limits

Read the M14-A contract, admitted M13-B narrative, evidence-cohort-generation skill and its interface guidance. Independently checked cached complete relevant text and table images for Pasco, Deurenberg and Hull; Gomez methods/results in the original full-text XML; Shepherd methods/results/Tables 1-4 at the official Wiley article; and Diessel methods/results/Table 1 and Figure 1-4 captions in the author's uploaded article transcription. The direct Diessel journal retrieval returned HTTP 403, after which the already-selected study's author-uploaded source was successfully read. No claim is made that a failed local XML or HTML response is a source copy, or that Diessel figure pixels were inspected.

| Check | Evidence locator | Result | Status |
|---|---|---|---|
| Pasco Model 3 coding, centering, coefficients and CIs | `relationships/cache/pasco2012_p6.png`, PDF p.6 Table 4 and footnote; text pp.2-3 methods/results | Exact formula below visually verified, including minus signs that text extraction corrupts | Resolved |
| Pasco outcome and source support | PDF p.2 Subjects, Measures, Statistics; p.6 Discussion | Body fat percentage uses DXA fat/(fat+lean+BMC); source 99% white Australian adults, mixed DPX-L/Prodigy Pro, substantial scan exclusions | Resolved extraction; transport unresolved |
| Pasco residual information | Table 4 Model 3 and footnote | S=4.07 pp is standard error of regression, pooled; not coefficient SE, marginal SD, or a sex-specific conditional residual law | Resolved interpretation; law unresolved |
| Deurenberg adult coefficients | `relationships/cache/deurenberg1991_p4.png`, printed p.108 Table 5; methods printed p.106 | Adult combined fit age >=16; coefficients, individual SE and SEE below | Resolved |
| Gomez prediction-error statistics | `relationships/cache/gomez2012.xml`, Research Design and Methods and Results | Air displacement plethysmography/Siri endpoint; equations and errors are not DXA transport correction | Resolved main-text extraction; overlap/supplement unresolved here |
| Hull bridge direction and units | `measurement/local_sources/hull2009_table4.png`, manuscript p.15 Table 4; pp.2-3 and 6 methods/caution | DPXL or Prodigy component kilograms predict iDXA component kilograms, sex dependent | Resolved extraction; unavailable inputs/version bridge unresolved |
| Diessel human versus phantom equation | Author-uploaded article transcription, printed pp.600-602, Table 1 and Figure 4 caption | Paired human DPX-IQ to QDR-4500 differs from phantom calibration | Resolved text/direction check; no PDF/figure-pixel check |
| Shepherd bridge and denominator | [Official article](https://onlinelibrary.wiley.com/doi/full/10.1002/jbmr.1654), Scan analysis; Data conversion; Tables 2-4 | Genuine paired-scanner relationship exists; target-compatible composition remains unidentified | Resolved direction; denominator/version transport unresolved |

## Pasco is actionable as a structural alternative

Let `m=1` for men and `m=0` for women, `x=BMI-26.37` (BMI in kg/m2), and `a=age` in years. The reported Model 3 conditional mean in percentage points is:

`mu = 37.8 - 16.7*m + 1.62*x - 0.06*x*x + 0.02*a - 0.17*m*x + 0.03*m*x*x + 0.04*m*a`.

| Term | Reported estimate | Reported 95% CI |
|---|---:|---:|
| Intercept | 37.8 | 37.0, 38.7 |
| Male indicator | -16.7 | -17.8, -15.6 |
| x | 1.62 | 1.56, 1.69 |
| x squared | -0.06 | -0.07, -0.05 |
| Age | 0.02 | 0.01, 0.04 |
| Male times x | -0.17 | -0.26, -0.08 |
| Male times x squared | 0.03 | 0.01, 0.04 |
| Male times age | 0.04 | 0.03, 0.06 |

Reported R2=.825 and pooled regression S=4.07 pp. This adjustment set contains sex, centered BMI and its square, age, and the listed sex interactions. Model 5 additionally conditions on lean mass and BMC and drops age; its coefficients cannot replace Model 3 terms when those inputs are absent. The age term is not centered. The BMI center is the reported source 26.37; recomputing it in a target while retaining the intercept changes the equation.

Algebraic checks on the published rounded coefficients give women `37.8+1.62*x-.06*x*x+.02*a`, men `21.1+1.45*x-.03*x*x+.06*a`. Local BMI derivatives at x=0 are 8.10 and 7.25 pp per 5 kg/m2, respectively; age derivatives are 0.20 and 0.60 pp per decade. The symmetric 5-unit BMI second differences are -3.00 and -1.50 pp. These features follow from the source equation; they are neither the adjusted linear slope under a new target covariate distribution nor target validation. In particular, this equation cannot be advertised as necessarily lowering the target BMI error.

The formula is an implementable alternative using the available predictors, with a relevant DXA percentage outcome. It can change model-implied levels, BMI association, curvature, age association and sex contrasts. It cannot establish conditional spread, tails, unmeasured-variable associations, subgroup transport, scanner correction, or valid scientific confidence intervals. Source coefficient CIs do not supply their joint covariance. Adding CI endpoints or drawing coefficients independently is not a valid joint uncertainty model; rounding adds further limits to exact reconstruction.

The source scan subset is 1,299 men and 855 women; prevalence sample counts are larger and should not be mistaken for the regression sample. The authors report broad ages 20-96, near-exclusively white population, female follow-up/supplementary recruitment and male baseline recruitment. Scan eligibility excludes large or difficult-to-scan participants. These features distinguish it from an age20-59 White/Black US target; non-Asian coding does not resolve ethnicity or population transport.

**Preferred residual decision:** isolate the mean substitution. Retain a prespecified incumbent residual mechanism unchanged as an inherited assumption, or use deterministic means for association-use testing. Carry S=4.07 only as a source pooled diagnostic in this specification. A homoskedastic Normal(0,4.07^2) alternative would be permissible as an explicitly assumed sensitivity, but introduces a second scientific change and must not be called source-established conditional noise. This review recommends leaving residual repair unidentified in the one compact revision.

## Other relationship checks

Deurenberg Table 5 final adult combined row visually reports n=747, BMI coefficient 1.20 (SE .04), male coefficient -10.8 (SE .3), age .23 (SE .01), intercept -5.4 (SE 1.0), SEE 4.1 pp, R2 .79. The total paper n=1,229 includes children and must not be used as the adult fit n. The article gives age >=16 for adults; the combined-row n differs from the sum of displayed subgroup counts, so preserve the table's value rather than silently repairing it. Densitometry with Siri/age-related adjustments is not the same endpoint as the admitted DXA target. This fit is evidence that another conditional structure exists, not an independent scanner bridge or a reason to pool unrelated coefficients.

Gomez's original XML confirms CUN-BAE predicts ADP/Siri body-fat percentage. Comparison errors in 6,510 participants are SEE 4.66 overall, 5.20 men and 4.36 women; reported separate validation n=1,149 has SEE 4.62/5.53/4.13. They are errors for that estimator and source selection. They do not identify a target sex-specific residual SD. The comparison mean and predicted mean, observed and predicted marginal SDs, SEE, and Bland-Altman spread are distinct. The reported difference trend with mean adiposity (R2=.07) further precludes treating the data as evidence for a universal zero-centered constant Gaussian error. Earlier derivation and current comparison overlap is not established by this independent check; the cardiometabolic 634 is a subset, not another replication. No referenced additional primary article was opened.

## Why the measurement chain is not identified

Diessel Figure 4 caption independently confirms 45 paired human scans with QDR-4500 percentage=3.68+.807*DPX-IQ percentage; phantom=-2.35+.966*DPX-IQ. The methods use linear regression without supplied covariate adjustments. Results reject equivalence of the phantom and human regression lines (p<.05). Table 1 comparison counts are not a unique cohort count. This constrains only its compared instruments; no bridge onward to the later target is demonstrated. [Source: author-uploaded primary article, pp.600-602](https://www.researchgate.net/publication/12393120_Evaluation_of_a_new_body_composition_phantom_for_quality_control_and_cross-calibration_of_DXA_devices).

Hull's same-person study of 99 adults (47 men/52 women) used DPXL4.7e, Prodigy8.80 and iDXA10.40 within three hours. Table 4 predicts iDXA from the older scanner. For total fat kilograms, Prodigy gives iDXA=.944*Prodigy+1.171 women or +1.829 men (SEE .968 kg); DPXL gives 1.003*DPXL+2.032 women or .925*DPXL+5.073 men (SEE1.090 kg). Those intercepts and SEEs are not percentage points. The separate lean/BMC equations and sex effects mean a percentage-only outcome does not supply the components needed for an exact transformed percentage. Reversing a predictive regression algebraically does not create an independently validated reverse conditional model.

Shepherd's Table 3 reports Hologic PFAT=1.943+.894*GE PFAT and GE=-2.173+1.119*Hologic; these are reversible Deming relationships for Prodigy enCORE14.0 and Discovery/Delphi Apex3.0. Table 4 gives internal bootstrap RMS-CV .0478 Hologic-to-GE and .0359 GE-to-Hologic, not pp SDs or coefficient SEs. Independent validation was unavailable. The methods define TM as LSTM+BMC+FM, but Table 2 Hologic adult means satisfy 38973.4+19564.9=58538.3, while GE means satisfy 35984.5+20794.5+1936.1=58715.1. Both pediatric strata repeat this manufacturer-specific pattern. The derived LSTM formula also omits BMC. Thus the Hologic LSTM label or mass definition is ambiguous; this does not prove that its PFAT denominator is soft tissue. [Source: official Methods and Tables 2-4](https://onlinelibrary.wiley.com/doi/full/10.1002/jbmr.1654).

The failure of composition is an identifiability issue, not simply imprecision: Pasco's mixture does not identify which scanner generated a given conditional response; no source software mapping is supplied; no component vector is available; Hull ends at iDXA rather than the enCORE14 Prodigy input to Shepherd; and the selected target software/BCA state is not demonstrated compatible. Neither a generic Lunar label nor an NHANES BCA adjustment closes these missing links. A correction assembled by chaining these estimates would require unsupported assumptions on outcome definition, scanner/version interchangeability and error dependence. No such correction should enter this revision.

## Release conditions and unresolved scientific issues

1. The specification must name the change as source-supported structural sensitivity and retain contradictory/no-useful evidence. It must not imply target improvement, measurement equivalence or clinical substitution.
2. Fix source coding, source centering, adjustment set and rounded coefficients exactly. Do not infer covariance from separate CIs or treat further seeds as source/transport uncertainty.
3. Fix the incumbent residual mechanism if retained; disclose it as inherited and unvalidated. Do not substitute S=4.07 as an identified target law.
4. A later testing unit must separately admit one reserved, unexposed target with matching predictor/outcome definitions, population support, survey/selection documentation and a predeclared estimand panel. The candidate, execution roster, estimator and confirmation protocol must be frozen before any new target outcomes. The current review neither chooses nor accesses that target.
5. Stop this bounded unit after decision/specification review. The six-study audit does not authorize extra primary studies, new target download, generation, source-loss tuning or execution.

## Final specification review

Read `work/m14a/revision_specification.md` and the named initial parent's `model_spec.json` and `generator.py`, without executing either. The complete source equation, sex coding, centering, units, unchanged parent residual parameters and guards, and future freeze-before-outcome boundary agree with this review. Its BMI contrast uses step 4, so `mu(28)-2*mu(24)+mu(20)=32*q`, giving -1.92 pp for women and -0.96 pp for men; these values are correct and distinct from the step-5 illustrative contrast above. Eight source-only arithmetic checks passed; they are recorded in `actual_checks.json` with the inspected artifact hashes and read/retrieval limits.

No blocking scientific amendment to the specification is required. The parent's base SD4.31, female ratio1.10, scale1.0, shifts0, mean guards0.5/99.5 and variance cap.95 were verified from the artifact. Selection by registration order is a controller assertion not independently established by this artifact read. No claim of code execution or target validation follows from this review.

Subsequently reviewed the final relationship evidence table/revision scope and measurement narrative/JSON extraction. Their retained equations, units, orientations, no-go decisions and access limits agree with this audit. The relationship branch correctly separates Pasco's preceding BMI25/30 predicted means from fixed-age Model 3: those text means cannot be added as Model 3 calibration constraints. The corrected measurement record preserves the manufacturer-specific component-label ambiguity rather than asserting a proved denominator mismatch.

**Final disposition: conditional GO for the specification only; no-go for exact measurement correction, residual repair or automatically starting another experiment.** Current unresolved issues are scientific limits, not requests to relax the information boundary.

### Amendment review and milestone check

Re-read the amended specification with SHA256 `B00CD0C6AA6CF1991CD669A559EB228372F558C161F12738CA3DDEAFFA5AEA3F`. It replaces the unverified registration-order statement with a designated fixed parent, and states the numeric guards explicitly. The earlier review hash is preserved in `actual_checks.json`; an appended amendment record binds this version. The source formula and scope are unchanged. Registration-order concern: resolved by removal of the unsupported assertion, not by a claimed verification of it.

Read `MILESTONE_14A_RESULTS.md`. No blocking scientific overclaim found: it calls the output a specification, preserves no-go decisions on the measurement chain and residual law, distinguishes known equation transport from discovery, and states the absence of execution/new target access. This review covers scientific content and does not independently certify controller-only historical integrity checks or authorization for a private export. The earlier direct Diessel publisher failure and subsequent successful independent author-text/caption check are both retained; no figure-pixel or complete independent study certificate is claimed.
