# Independent review of qualified source projections

2 November 2026. Reviewer: `/root/highlight_existing_mechanism`; producer: `/root/highlight_evidence_admission`. **Approve the 15 common marginal-record roles, the proposed E0/E1 partition, and each of the four qualified source-context point-comparison definitions. No material source-interpretation error was found.** The companion `SOURCE_PROJECTION_APPROVAL.json` binds the exact reviewed files and this review. This is source-interpretation admission only, not an execution or target release.

The reviewed proposal files retain their original pending labels. This separate decision admits their stated definitions without rewriting them. A later change to either file requires renewed review of the changed bytes.

## Evidence and byte commitments

The review read the seven retained authored provenance records listed by `SOURCE_PROJECTION_CANDIDATES.json`: the original independent Jansen audit, two retained Jansen summaries, Bao and MIND source audits, the independent MIND arithmetic review, and the earlier independent source-package review. Their seven SHA-256 values all match the proposal. Original publications, patient records, generated records and target effects were not opened; no network request was made.

| Reviewed file | SHA-256 |
|---|---|
| `SOURCE_PROJECTION_CANDIDATES.json` | `8c33ce2f3770a1d5176d2d1e24ae1bc0ca3ab45320cfb2ca6a413b2240e1f8d7` |
| `SOURCE_INTERPRETATION.md` | `44f4531b922181ca666c4081c07b1f15db06baae01e6c72a56fffc557b9752df` |

Static metadata checks verified three source records, 15 unique grouped marginal records, four unique E1 relationships, exact E0/E1 ID coverage, the three count divisions, the selected numerical transcriptions and all seven provenance commitments. These checks are not a software-suite run, a new source extraction or a generated-data experiment.

## Common marginal evidence

Each source supplies four numerical marginal records and one sex-category count record. A mean/SD pair or median/quartile set is one grouped record; the count of 15 is not a count of 15 independent scalar observations.

| Source | Verified four variable records | Verified count record |
|---|---|---|
| Jansen | Age 55.5/9.9 years; BMI 26.5/4.1 kg/m2; FPG 5.1/0.5 mmol/L; HbA1c 38/3 mmol/mol, each mean/individual SD | Male 1176/2921 = 0.40260184868195825 |
| Bao | Age 49.4 [37.9,57.7] years; BMI 23.5 [21.4,25.9] kg/m2; FPG 5.2 [4.8,5.6] mmol/L; HbA1c 5.6 [5.3,5.9] percent, each median [Q1,Q3] | Female 3058/4886 = 0.6258698321735571 |
| MIND | Age 69.5/4.2 years; BMI 25.0/3.6 kg/m2; FSG 5.2/1.4 mmol/L; HbA1c 6.1/1.0 percent, each mean/individual SD | Female 2049/3547 = 0.5776712714970398 |

These values match the retained audits. The fractions are derived from reported counts, not verified weighted population proportions. SD divisor, quantile algorithm and estimator uncertainty remain unknown where appropriate. Individual SDs are not SEs, and quartile endpoints are not confidence bounds. Jansen's Table 1 sample is not silently asserted to equal the Table 2 regression rows. Its rounded percent presentation is appropriately omitted rather than counted as independent evidence.

The source contexts preserve the material selection and measurement differences: Jansen's selected diabetes/anemia-excluded Lifelines population and IFCC/plasma measurements; Bao's exclusion of previously diagnosed diabetes while retaining screen-detected diabetes, unresolved age-20 boundary and fasting plasma measurement; and MIND's selected older rural population, included known diabetes, prior-year anthropometry, later serum measurement and reported imputation. FPG and FSG remain distinct.

## Four separate interpretation decisions

| Record | Decision and verified meaning |
|---|---|
| `R_JANSEN_BMI` | Approve the qualified unweighted, intercept-including HbA1c-IFCC-on-BMI projection adjusted for age and binary gender only. The focal point is 0.13 mmol/mol per kg/m2; printed interval 0.10 to 0.16, confidence level unconfirmed. |
| `R_JANSEN_FPG` | Approve the separate qualified HbA1c-IFCC-on-FPG projection adjusted for age and binary gender only. The focal point is 2.29 mmol/mol per mmol/L; printed interval 2.07 to 2.51, confidence level unconfirmed. |
| `R_BAO_PEARSON` | Approve the qualified equal-weight Pearson functional on complete source-scenario FPG and HbA1c-percent values, compared with the reported unadjusted 0.619. No covariate adjustment, slope or covariance is inferred. |
| `R_MIND_SPEARMAN` | Approve the qualified equal-weight Spearman functional on complete source-scenario FSG and HbA1c-percent values, using average ranks for ties, compared with the reported unadjusted 0.529. The rank statistic is not converted to Pearson. |

The two Jansen coefficients belong to separate equations. Combining both into one conditional HbA1c equation would change the conditioning sets and is not approved. For the declared comparison models, four columns including the intercept require full rank and more than four rows; the proposed minimum of five plus positive residual degrees of freedom is coherent. Correlations require finite, nonconstant columns; the proposed minimum of three pairs is conservative and consistent. Complete-value guards describe future generated analysis values, not recovered original missingness rules.

Equal weighting, the explicit Jansen intercept convention and MIND average-tie handling are declared comparison assumptions. They do not certify the original analytical programs. Original weighting stays `not_reported` for every source; model-row or pair-specific n and missing precision stay unknown. All four `strict_replay.status` values correctly remain `not_computable`. The qualified comparisons can report point values and raw discrepancies with assumptions, but this approval supplies no precision weighting, CI-membership pass, pooled cross-source loss, source reconstruction or target-parameter assignment.

The lack of a complete joint distribution, source intercept, residual law or covariance does not prevent defining these point functionals. It does limit what a fitted generator can claim. No further literature or full identification is demanded by this review.

## Binary nuisance recoding

The invariance claim is correct. For a fixed table and model `y = b0 + ba*a + bg*g + bx*x + residual`, write `g_new = 1-g`. The same fitted expression is `(b0+bg) + ba*a - bg*g_new + bx*x + residual`. This is an invertible reparameterization; full column rank makes the OLS coefficient vector unique, and the focal coefficient `bx` is unchanged. Equivalently, the nuisance spans `[1,a,g]` and `[1,a,1-g]` are equal.

This proves only the stated same-row, same-category-partition, unpenalized, intercept-including, no-interaction comparison. It does not recover original numerical coding, nuisance coefficient direction, a target sex/gender mapping or category prevalence after a mistaken remapping. The proposal preserves these limits. No simulated or patient rows were needed for this algebraic review.

## Information boundary and remaining implementation work

E0 lists exactly the three common source metadata records and 15 marginal IDs, with no relationship IDs. E1 inherits them unchanged and adds exactly the four reviewed relationships. The combined JSON, this interpretation note, original bodies and retained audits are coordinator-only because they contain E1 information or excluded numerical material. Actual sanitized arm packets do not yet exist and are not approved by this record. Their later review must verify that E0 feedback, recipes, caveats and paths also disclose no E1 values, intervals, signs or reconstructible relationship summaries.

The Jansen Table 3 bundle, conflicting MIND HbA1c agreement bundle and dependent derivatives, Bao OGTT-dependent groups, and other unselected relationships remain excluded. Their absence agrees with the retained audits; the MIND discrepancy is not repaired or replaced by a derived value.

This JSON is explicitly not a current harness schema. Mathematical operator availability is separate from an execution-bound qualified-feedback collector. The existing strict collector must continue to report unavailable for unknown source weights; the existing bridge does not by itself activate these new qualified interpretations. No unused collector is required or built now. Any later compiler/collector must bind these exact meanings, preserve strict unavailability and receive its own narrow implementation review.

No source generation, target admission, target transport, candidate generator, source-context reconstruction, execution schedule, evaluator or new scientific result is approved. Those are separate decisions if a fresh source/target pairing becomes available. This review consumed no candidate-family screen, original-study slot or download byte, and changed no proposal, historical audit, frozen code or receipt.
