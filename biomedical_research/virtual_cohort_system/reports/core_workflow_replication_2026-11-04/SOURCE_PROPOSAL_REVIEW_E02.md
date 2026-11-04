# E02 independent source and proposal review

2026-11-04. **Decision: PASS_TO_IMPLEMENT.** The selected source numbers, explicit derivations and finite-moment argument reproduce. No source transcription or mathematical defect requires changing the scientific parameters. Before freeze, the proposed unbounded-BMI/conditional-truncated-normal combination requires a stable, terminating implementation review as detailed below. This is implementation guidance for the existing law, not a new source or distribution choice.

## Materials and boundaries

Reviewed E02 task/request metadata, source request, proposed law and search ledger, and the admitted original methods/results/tables for PMC8038122.1, PMC2551641.1, PMC6371438.1 and PMC5398507.1. All seventeen registered artifacts match their hashes. Gateway state reports five query credits and four original downloads; the original-read limit is exhausted. Taiwan Biobank, FOS/NHANES, SHIP and the Italian samples are the generating sources. None is a CHNS or ENSANUT participant study; selected-text alias scans found no excluded-cohort mention. Pani and Huang are byte-identical to originals already inspected in the preceding source audits; E02's own registered copies were verified.

No new source, old model, target outcome or participant/generated row was read, and no author script or generator was executed. The independent arithmetic below contains constants and analytic equations only, with no random draws. Frozen controls were not modified. The reviewer has historical project-result exposure and supplies no target-directed parameter or desired sign.

## Source findings

- **Huang S1:** The age/sex-only regression in Table `ijerph-18-03390-t001` contains male 0.08301, SE0.01725, and age0.01401, SE0.00081. Nonuniversal fasting, broader glycemic eligibility, the female-count inconsistency and sex-specific/nonlinear-age caveats are accurately represented. Transferring its sex contrast into a BMI/glucose-adjusted mean is explicitly an assumption.
- **Pani S2:** The NHANES adjusted age coefficient0.010/year, BMI mean28.01, qualitative BMI-age finding and approximate eight-mg/dL glucose age contrast are correctly identified. The main text establishes boronate-affinity HPLC for NHANES and hexokinase plasma glucose, but not every target eligibility restriction. The source weights, mean/SE versus individual-SD distinction, overlapping FOS subsets and unadmitted supplement remain appropriately separate. The proposed glucose-age coefficient is not falsely attributed to this paper.
- **Masuch S3:** Table `Tab1` explicitly labels SHIP-Trend BMI27.5 (24.5;31.0) as median/25th/75th percentiles. The original confirms nonoverlapping recruitment, age20–79, primary samples4,263/4,402 retaining diabetes, and narrower healthy subsets817/987. Main versus healthy selection, fasting status, assay and spline-age distinctions are correct. Only the quartile ratio sets the proposed lognormal spread; the source median is not converted into an empirical mean or SD.
- **Marini S4:** The original confirms sample1 n=2,055, age47.8±14.6, glucose93±11, HbA1c5.4±0.4, r=.55 and equation `HbA1c=4.0311+.0158*FPG`. It also confirms sample2 n=387, its parent-diabetes/risk selection, 12-hour fast and the stated assays. Table `pone.0175547.t001` contains the three129-person HGI groups and the exact BMI/age/HbA1c/glucose summaries used in the ecological calculation. The table's adjusted P-values are not adjusted group means or an individual BMI regression coefficient.

The proposal correctly retains S4's reporting inconsistencies: the equation predicts5.5005 at glucose93, while its stated mean is5.4; reported r/SDs imply slope0.020 rather than0.0158; and the sample2 narrative's530 males conflicts with both n387 and the table's147 males. These discrepancies cannot all be resolved as exact moment constraints. Prioritizing particular reported quantities under a declared scenario is allowed; neither the omitted intercept/correlation nor the inconsistent sex count may later be claimed reproduced. No substitute corrected empirical coefficient is inferred by this review.

## Independent model arithmetic

| Quantity derived from the author's proposal | Independent result |
|---|---:|
| BMI log-SD from SHIP IQR ratio | 0.1744385936673 |
| BMI variance / SD after setting mean28.01 | 24.2401699762 / 4.9234307120 |
| Untruncated-surrogate glucose residual variance / SD | 112.3254728038 / 10.5983712335 |
| Stated ecological BMI guide | 0.00964983119053 |
| Conditional HbA1c glucose coefficient | 0.01235619272806 |
| Surrogate marginal glucose slope after covariance addition | 0.0158 |
| Surrogate HbA1c explained variance | 0.05423408519094 |
| Conditional HbA1c residual variance / SD | 0.10576591480906 / 0.32521671975632 |
| Conservative HbA1c conditional-mean lower bound | 3.70126907629 |

These match the proposal. The ecological guide assumes zero within-HGI-group adjusted-outcome covariance and specified handling of group variances; it is not identified individual regression evidence. The surrogate covariance subtraction is valid under its stated age/BMI/sex independence and untruncated moments, not as a reconstruction of the source's actual selection or covariance matrix.

Age/sex are bounded, BMI has finite polynomial moments, and glucose is bounded after conditional truncation. The HbA1c arithmetic mean is bounded away from zero and grows at most linearly with BMI. For its conditional lognormal with fixed arithmetic variance `v`, the kth raw moment is `m^k*(1+v/m^2)^[k(k-1)/2]`; the positive lower bound on `m` and finite BMI moments therefore justify finite second/fourth and higher fixed polynomial moments. The proposed population Q1=.100 per decade and Q3=.050 per five-BMI units follow from its linear conditional mean. The proposal correctly leaves Q2 dependent on the post-truncation glucose projection rather than assuming it remains the untruncated value.

## Required implementation/interpretation checks before freeze

1. **Tail-stable glucose sampling.** Unbounded BMI makes the normal glucose location unbounded above even though the retained glucose interval is(0,126). For any finite covariate value the conditional distribution exists, but naive normal rejection may become effectively nonterminating and direct subtraction of tiny normal CDFs can underflow. The submitted sampler must preserve the declared conditional distribution with a numerically stable tail method and a defined termination/failure behavior. Do not silently clip glucose, introduce an endpoint mass, cap/resample BMI or switch the scientific law to hide a failed draw. Any bounded execution failure remains charged and visible. This asks for correct implementation, not different scientific parameters.
2. Preserve the explicit distinction between the untruncated analytic source surrogate and the selected target-design law. Target glucose mean/variance, marginal glucose–HbA1c slope and total HbA1c SD need not equal the surrogate constraints. Source-surrogate algebra is not source-population replay or a generated source cohort.
3. Tag the BMI direct term, glucose-age/BMI dependence, sex transfer, source covariate centers/independences, lognormal shape and conditional residual variance as assumed/derived where appropriate. Do not promote the HGI ecological guide or transported coefficient into a reported task-adjusted source estimate.
4. Source feedback must retain original statistic type, population, selection, weighting, measurement and adjustment. Unsupported transforms or rich conditional models remain unavailable; allowed target-row comparisons remain qualified approximations. Built-in conditional-mean coefficients are model-implication checks, not independent empirical validation.

No new literature, target inspection, parameter tuning or redesign is requested. Exact cell counts, row identities, open glucose bounds, numerical finite values and specification/program agreement remain for the normal candidate review and charged execution stages.

## Reviewed identities

- Source request: `6292958e01b0b65dc96b04b9d991c16a608f563c183d25a22cd0898c1e33168a`
- Proposed construction: `31585dd022d7566184eb285017f0a5e77becf270d1fe267037b3a36caf1e380c`
- Search ledger: `d96e672134e292d5c244a96ffaefb06089c3f3cd33ca1b18d2e1cd09d0e29f77`
- Task/request hashes match E02's protocol bindings. Original identities are the admitted hash-named XML files listed in the reviewed source request/registry.
