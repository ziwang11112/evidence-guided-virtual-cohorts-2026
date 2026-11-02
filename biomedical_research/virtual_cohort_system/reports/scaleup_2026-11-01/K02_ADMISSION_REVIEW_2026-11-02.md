# K02 independent admission review

2 November 2026. **Advisory decision: the measured TC/HDL case can support a qualified prospective quantitative target evaluation; it cannot be described as a globally unexposed cohort or wholly unknown-relation discovery.** No scientific case is admitted or released by this note. No target effect, clinical mean, target sign, outcome distribution or patient outcome row was inspected.

The review used the current STATE, K02 prospective decisions, Turkana admission/method/schema/history reviews, the scientific-use advisory and the dataset-exposure registry. The newer five-variable K02 proposal supersedes the earlier methods review's optional lifestyle-adjusted candidate; the difference is an estimand decision, not a way to erase prior exposure.

## Narrow metadata recovery actually performed

The official [Dryad Usage notes](https://datadryad.org/dataset/doi:10.5061/dryad.2z34tmpjk#usage) were reopened in wang Chrome. They confirm literal NA for missingness, self-reported Age/Sex, BMI in kg/m² and TC/HDL in mg/dL. They provide no explicit sex-code legend or exact numeric adult cutoff. No preview, new download, new original study, target result table or expanded search was opened. The landing page repeated its already-disclosed qualitative lifestyle/early-life abstract; no new numerical outcome finding was exposed.

A subsequently authorized code-only custodial check read the exact previously acquired local file:

`private_data/22Jul20_for_Dryad_noIDs.txt`

SHA256: `7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9`.

The script first checked the complete file hash, decoded UTF-8-sig, and used Python `csv.DictReader` with a tab delimiter. The parser necessarily traversed records, but the only content field consulted was `Sex`; all other field values were ignored. Only a set of trimmed, nonmissing Sex tokens was collected. No values were cast to clinical numbers. It emitted **literal categories F and M; cardinality 2**, with no frequencies, identifiers, age values/counts, other covariate values, outcomes or summaries.

The missing-token predicate is None, a trimmed empty string, or exact uppercase `NA`. An invented-token check confirmed that ` NA ` is missing while `na` and `N/A` are not silently recoded. This establishes the parser rule, not that every possible undocumented sentinel in every field has been ruled out. No full clinical missingness audit was performed here.

## Concrete target contract recommended

| Field or rule | Prospectively fixed implementation | Interpretation |
|---|---|---|
| File identity | Exact named deposit and hash above; fixed tab/UTF-8 parser and header identities | Reacquisition or a new folder does not create a new target. |
| Sex adjustment | Use the released categorical factor with levels `F`, `M`; choose one indicator such as `sex_F = I(Sex=="F")` plus intercept. Reject an unexpected nonmissing token rather than silently collapsing it. | The proposed BMI coefficients and TC/HDL residual correlation are invariant to swapping these two nuisance-category labels. No sex-specific effect or biological code interpretation is needed for these three endpoints. |
| Age | Define the investigator-selected adult domain as finite self-reported age **at least 18 years**, with no new upper-age cutoff. | This is our prospective use-case boundary, not a claim that the paper specified exactly 18. No target ages, counts or range were read to choose it. |
| Common analytic subset | Require age, recognized Sex, BMI, TC and HDL jointly available; finite numeric values; BMI, TC and HDL strictly positive. | One common denominator for all three analyses, describing released adult complete records. The earlier 397 is only nonmissing availability, not the final N. |
| Numeric parsing | Parse documented units directly; do not convert the target TC/HDL again. Unknown nonnumeric tokens are a preparation error needing an explicitly documented technical resolution. | No generic 88/99 recoding, inferred fasting flag, guessed disease exclusion or imputation in the reference. |
| Invalid values and trimming | Apply only the fixed positivity/finite rules; preserve reasons/counts at eventual preparation. No winsorization, quantile trimming, observed-range tuning or clinical cutoffs added after inspection. Do not exclude TC<HDL solely to make a derived model identity hold. | Target preparation is a measurement-defined selection, not optimization of a favorable relation. |
| Other columns | Do not require TG, LDL, glucose, body fat or lifestyle to be complete; do not add them to the current primary models. | Excludes outcome-censored TG and calculated LDL from independent measured validation and preserves the intended five-variable task. |
| Population | Released study-protocol adult complete-case mixture from the Turkana/Laikipia recruitment frame, pooled across its recorded lifestyle composition | Neither all Turkana adults nor a representative Kenyan population. The pooled relationship may depend on unprovided composition. |
| Task regime | Generate all five substantive variables without target participant inputs, target moments, target sex proportions or outcome summaries | Actual target sex counts or age distribution must not be supplied as construction constraints. |

Using recorded levels F/M does not require inferring their meaning from biomarker values. If a human-readable male/female legend is later required for a separate purpose, obtain a documented code map; do not guess from distributions. It is not a blocker for these label-invariant pooled estimands.

The as-collected venous-EDTA CardioChek Plus endpoints are legitimate measured targets for this protocol. Unknown fasting status and absence of a source-to-device bridge limit transfer claims but do not make a descriptive protocol-specific test impossible. Released-data processing is inherited; do not claim exact replication of the publication's full filtering or access to unprocessed measurements.

After the contract is approved and frozen, a custodian can apply it and report final counts, parsing/eligibility failures, design rank and endpoint computability under the established evaluation gate. This note performs none of those calculations. Undefined residual variance, singular design or otherwise uncomputable analysis must remain a recorded failure, not cause a favorable substitution.

## Scoped exposure decisions

| Proposed quantity | Recorded prior exposure | Independent verdict |
|---|---|---|
| HDL BMI contrast adjusted for age and recorded sex | Broad published lifestyle/diet/early-life cardiometabolic conclusions; no exact TC/HDL/BMI/age coefficient documented as read or computed | Eligible for a first prospective quantitative comparison under the frozen definition. Not a globally blind biological discovery. |
| TC BMI contrast with the same adjustment | Same broad contextual exposure; no exact proposed coefficient documented as read or computed | Same qualified eligibility. Do not claim that all target lipid information was unknown. |
| TC–HDL residual correlation after both age/sex/BMI regressions | Supplement fragment gave generic age/sex-residualized biomarker correlation strength and proportion of weak/unassociated pairs. Pair-specific TC–HDL magnitude was not documented as read. | Quantitative value remains held out on the existing record, but generic joint-dependence knowledge is prior exposure. Additional BMI adjustment does **not** reset this knowledge or turn the question into an entirely unseen relation. Retain as an explicitly qualified joint-use test. |
| Lifestyle, urban/rural, early-life, LDL/TG contrasts; generic fraction of uncorrelated pairs | Published conclusions or numerical sensitivity statements already exposed | Ineligible as fresh withheld confirmations in K02. Exclude from construction evidence and new-success claims. |

The first three analyses were selected for measured-endpoint usability and reusable scientific analysis before inspecting their quantitative results, rather than by target effect size or success. That supports a prospective quantitative holdout, despite investigator knowledge of the study's general conclusions. The strongest defensible label is **“first prospective K02 quantitative evaluation with disclosed prior target-study context”**, not “completely unseen external confirmation.”

A fresh constructor context receives only the approved external-source packet and task. It must not receive the target paper, result-bearing method notes, this exposure review, target participant data or the generic residual-correlation finding. Context isolation controls the supplied information, not foundation-model pretraining. No record search proves absence of undocumented historical exposure; the conclusion remains scoped to the inspected history.

## What remains before an actual release

There is no remaining need to search indefinitely for a sex-code interpretation or a fully identified joint law. The immediate metadata decisions are explicit: approve the investigator adult boundary, categorical Sex adjustment, common validity rules and selected-sample claim. Final eligibility count and model computability are still unknown and must not be inferred from 397 available rows.

Separate release gaps remain: source-context/proxy interpretation, working feedback integration, exact frozen estimator and uncertainty conventions, statistical-reference definition, constructor information boundary, and the campaign's global freeze. The inherited 0.10/grid rule is a research resolution choice, not a clinical equivalence margin. These are bounded protocol/implementation tasks; this review changes none of the existing rules.

With no cluster identifiers or survey weights, point comparisons describe the selected released sample. HC3 or iid perturbations, if prospectively fixed, are assumption-conditional sensitivity summaries; they cannot certify cluster-aware population uncertainty. Do not fabricate clusters from lifestyle categories, turn simulated sample size into empirical precision, or use agreement to claim individual measurement recovery, cardiovascular prediction, clinical substitution or national-population fidelity.

This review adds no family, original-study or download quota and edits no STATE, source packet, old target or frozen file. The only authored artifact is this admission review.
