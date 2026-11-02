# Prospective scientific-use review: measured TC/HDL case

2 November 2026, America/Chicago. Independent advisory review of the existing campaign, state and Turkana/Greiner method reviews. No browser, participant file, new source, target statistic, generator or experiment was accessed. This note proposes a concrete protocol; it is **not admission, freeze or execution approval**.

## Feasibility judgment

**Yes: the evidence can justify a bounded prospective generation-and-transfer experiment without identifying the complete joint distribution.** Unambiguous geometric means, threshold proportions, age quantiles and BMI summaries constrain useful parts of the law. Reported joint relationships provide contextual evidence even when their exact executable transformations are unresolved. Remaining dependence, distribution-family and transport choices can be made by the constructor and recorded as assumptions.

Requiring every target conditional relationship and residual SD to be known before construction would remove the research problem we intend to test. The relevant question is whether a transparently evidence-informed, partially specified construction yields analytically useful joint data on an independent reference. It is not whether partial aggregate evidence mathematically determines the unique real joint distribution.

This does not license inventing source certainty. Unresolved Table 3 raw/log slopes cannot become exact source-feedback targets. Source geometric means and threshold rates can be checked only under their declared source context; a target-population statistic is not source replay. An Agent may choose a lognormal or other distributional scenario, but the resulting variance is assumption-dependent, not a reported SD. Numerical comparison with Turkana remains target evaluation, not feedback for construction.

## Exactly three proposed primary analyses

Use the same common analytic subset and the same five substantive variables for all three. Let X contain an intercept, age in years, recorded sex and BMI in kg/m². Fit unweighted OLS in the recorded mg/dL lipid units; do not use data-dependent transformations or select a model from target fit. Sex coding must be resolved from metadata before implementation. No expected coefficient direction or target value is stipulated here.

| ID | Prespecified statistic | Scientific use | Evidence classification |
|---|---|---|---|
| K02-HDL-BMI | Fit HDL ~ age + sex + BMI; report 5 times the BMI coefficient, in mg/dL per 5 kg/m² higher BMI | Quantify the adiposity–HDL association after age/sex adjustment, using an ordinary analysis researchers can reuse | Related source relationships are supplied as contextual evidence. This exact pooled raw-scale age/sex-adjusted operator is not supplied and is not algebraically implied; its magnitude and transport depend on assumptions. |
| K02-TC-BMI | Fit TC ~ age + sex + BMI; report 5 times the BMI coefficient, in mg/dL per 5 kg/m² higher BMI | Test whether the same generated table supports a second measured-lipid association, rather than only the HDL relationship highlighted in sources | Marginal TC and BMI evidence is supplied. The required conditional TC–BMI relationship is neither directly supplied nor determined by those marginals or the HDL source regressions; it is assumption-dependent. |
| K02-LIPID-RESIDUAL | From those same two regressions, compute Pearson correlation between TC and HDL residuals | Test whether the virtual table preserves lipid co-variation beyond measured adiposity and demographics; this assesses a joint-data reuse property | Source HDL–non-HDL relationships are relevant context, with algebraic coupling through non-HDL = TC − HDL. They do not identify this adjusted residual correlation. It is assumption-dependent and is not another independently measured assay. |

All three are descriptive associations. They do not establish causal effects, CVD risk prediction or individual recovery. In particular, the third is not a newly discovered biological mechanism. The two BMI effects alone do not determine the residual correlation, so the third is a substantive check on joint construction rather than a duplicate endpoint.

These are candidate analysis IDs, not certified unexposed analyses. Existing broad lifestyle and generic residual-correlation exposure remains disclosed. An independent reviewer must assess semantic overlap with those exposures; changing an adjustment set or an ID does not itself restore independence. None of the target paper's result-bearing material enters the constructor packet.

## Population and information boundary

The target is the **released participating adult sample with the five measurements available**, under the study's recorded measurement protocol. It is not Kenya's population, all Turkana adults, or an established fasting-laboratory population. The 397-row schema intersection is only availability; final eligibility may be smaller.

Before any target-effect calculation, fix an executable inclusion rule: adult age under a declared boundary consistent with the study description, valid documented sex coding, and finite nonmissing age/BMI/TC/HDL, with positive BMI and positive lipid values. Resolve any release-specific invalid codes from documentation. No post-hoc winsorization, outlier deletion or choice of common versus endpoint-specific denominator is allowed. Nonphysical or questionable combinations should follow a frozen measurement rule, not be deleted because they worsen agreement.

The whole-cohort constructor must generate age, sex and BMI as well as both lipids. It receives no participant covariates, reference lipid SDs, target effects or target-outcome-informed mixture weights. Released-sample selection, composition and assay transfer are construction assumptions unless independent permissible evidence supplies them. Missingness counts establish availability, not missing-at-random sampling or the mechanism of the measured subset.

Lifestyle remains a material omitted context in this five-variable proposal. The estimands are pooled age/sex-adjusted descriptive projections; they are not lifestyle-adjusted effects and are not invariant to lifestyle composition. Do not add lifestyle merely to copy the target paper's exposed conclusions. If a six-variable alternative is scientifically chosen before freeze, it needs a separately stated task/operator and source-composition assumption, not silent insertion during evaluation.

## A concrete research-resolution assessment

Clinical equivalence margins are not established by the present evidence. An operational **research-screening resolution** can nevertheless be declared prospectively and assessed transparently. The following default is a design proposal for the root to adopt or revise **before any target coefficients are seen**; it is not a clinical fact or a universally accepted accuracy threshold.

For each construction c and seed s, retain the raw effects and calculate:

- e_H(c,s) = abs(5 beta_H(c,s) − 5 beta_H(reference)) / SD_H(reference).
- e_T(c,s) = abs(5 beta_T(c,s) − 5 beta_T(reference)) / SD_T(reference).
- e_R(c,s) = abs(r(c,s) − r(reference)).

Both virtual and reference contrasts use the **same reference outcome SD** for evaluation scaling. Using each generated table's own SD could hide reduced variability. These reference SDs are evaluation-only and never disclosed to builders. Zero/invalid reference SD or rank-deficient analysis is an evaluability failure, not a convenient success.

Publish the complete tolerance grid **0.05, 0.10, 0.20 and 0.30**, using outcome-SD units for e_H/e_T and correlation units for e_R. Designate **0.10** as the working research resolution before outcomes: a discrepancy of one tenth of observed individual outcome variation for the chosen BMI contrast, and one tenth of the correlation scale. This is an explicit coarse association-screening choice, useful for testing whether conclusions survive more than sign matching. It does not certify clinically interchangeable measurements or a ten-percent relative-error guarantee. The entire grid exposes how the conclusion depends on that design choice; a later favorable threshold must not replace the declared one.

Keep raw mg/dL errors and effect ratios where well defined beside the normalized errors. A near-zero reference effect makes relative error unstable, so relative error cannot be the sole endpoint or a reason to remove an analysis. Direction agreement is reported separately and does not substitute for magnitude agreement. Neither virtual p-values nor significance agreement defines success: 5,000 sampled rows are not 5,000 independent measurements informing the generator.

## All-five-constructor rule and prospective continuation

1. A construction satisfies the proposed resolution bundle only when **all three planned seeds meet all three margins** at the declared working resolution. Seeds are Monte Carlo checks within one construction, not separate biological votes. A missing/failed construction fails the operational bundle; retain its failure category instead of dropping it from the denominator.
2. A case satisfies procedural reproducibility at that resolution if **at least four of the five prespecified constructions** satisfy the full bundle. Four-of-five deliberately allows at most one construction failure; it is an operational reliability criterion, not an estimated 80% population success probability or an equal-search-budget superiority result. Report all five constructions, all seed ranges and the conventional reference.
3. Include a **zero-association diagnostic anchor** for each endpoint: its errors are abs(5 beta_H(reference))/SD_H(reference), abs(5 beta_T(reference))/SD_T(reference), and abs(r(reference)). This is an interpretation anchor, not a data-generation baseline. If zero already lies within the working resolution on all three, agreement is non-discriminating for recovering joint signal and cannot by itself justify automatic Wave B expansion. Correctly preserving weak/null relations can still be reported.
4. Retained final models reference their initial outputs. Initial-to-final change is assessed for every constructor; retention is zero improvement, not a new draw. Source-fit gain and target analytical gain remain separate.
5. If the root adopts this research-resolution bundle, it must be explicitly described as **empirical-reference analytical agreement**, replacing any implication of clinical equivalence before release. It can provide a concrete prospective Wave A decision under the existing all-construction requirement. If the intended scientific use still requires a clinically justified margin, or source/measurement/evaluability concerns make adequacy unresolved, report Wave A descriptively and **do not automatically release Wave B**. Do not invent a new favorable criterion after disclosure.

The fixed statistical construction receives the same evidence and is evaluated identically. The proposed case feasibility rule does not require superiority over it. An Agent may be a useful method even when a conventional construction also works; comparative improvement is a separate claim.

## Reference uncertainty and interpretation

The reference is an observed study sample, not known population truth. For the finite released-sample descriptive comparison, its point estimates define the stated empirical comparator. No field permits design-based weighting or known-cluster inference. Lifestyle categories must not be relabelled as clusters.

HC3 intervals for the regression contrasts or an iid participant bootstrap can be prespecified as **assumption-conditional uncertainty sensitivity**. They do not correct unknown within-location dependence or certify population coverage. Record the inference assumptions and any computational budget before evaluation. Do not use a wide reference interval to turn poor agreement into success, and do not present synthetic-row standard errors as source/transport uncertainty. Construction differences, simulation variation and reference-sampling uncertainty need separate reporting.

If those limitations prevent the intended population or clinical claim, narrow that claim to the defined empirical analytic sample. They do not force abandonment of every descriptive transfer experiment. Conversely, agreement in this selected sample must not be advertised as demonstrated national-population fidelity.

## Bounded handoff

Proceed toward a case contract and approved evidence packet using the unambiguous summaries, contextual relations and explicitly recorded joint/transport assumptions. Do not keep searching merely to identify every unknown parameter. The remaining admission decisions are concrete: resolve coding/eligibility, source-context implementation, scoped independence, and adopt a pretarget analytical-use rule such as the proposal above. No target effect, mean, expected sign, slope or generator parameter was supplied by this review. The existing global-freeze and two-wave boundaries remain in force; this advisory does not execute or amend them.
