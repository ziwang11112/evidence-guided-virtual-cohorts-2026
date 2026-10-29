# s1: final source-only revise

One source-conditioned sensitivity revision relaxes the common BMI slope into sex-specific slopes. It addresses excessive Bansal BMI dependence while retaining an algebraic anchor to the pooled Oh slope and marginal moments. This does not identify true sex-specific effects.

Only the BMI slopes and their moment-derived residual CVs change; age slopes, assay handling and all common source definitions remain fixed.

The final male/female BMI slopes are 9.557309727577666 and 5.2 mg/dL per kg/m^2. With w = (1029 * 3.1^2) / (1029 * 3.1^2 + 1643 * 3.2^2) = 0.37018254401132633, male slope = (6.813 - (1-w)*5.2)/w. This is a variance-weighted population approximation under the declared independent source covariates, not an exact finite-sample or family-weighted identity. Final residual CVs are 0.7153743796657551 and 0.5468139785420796.

The model retains an arithmetic conditional mean m: TG = m * exp(sigma*Z - sigma^2/2), sigma^2 = log(1+CV^2), so the residual multiplier has expectation one. Changing residual CV therefore does not turn the arithmetic mean into a log median or move E(TG|age,sex,BMI) on its own. It does change conditional log variance and conditional median m/sqrt(1+CV^2), and can alter ranks and threshold fractions. The source moment decomposition assumes the unregularized additive mean and independence; the positive floor and finite source construction can prevent exact marginal agreement.

All 46 initial checks reviewed: 12 covariate-only checks and 34 outcome-related checks. Input-only agreement is construction fidelity, not TG validation.

Bansal BMI Spearman 0.439490 versus 0.33; first/third TG-tertile BMI means 23.4466/28.3857 versus 24.2/27.6. These persistent discrepancies motivate a lower assumed female BMI response.

Oh pooled BMI OLS 6.83398 versus 6.813 and sex-specific mean/SD summaries were already close. Preserve the published pooled slope analytically by balancing the unreported male/female slopes using published within-sex BMI variances and counts; recalculate residual CV from the same source moment formula.

Keep age slopes unchanged. Bansal age Spearman 0.140326 versus 0.18 does not imply a uniquely larger conditional age effect: TG-tertile age mean separation already approximates the source and conditional age SDs differ.

Female slope 5.2 and derived male slope are unreported, assumption-dependent coefficients. Unknown age-BMI dependence, omitted variables and selection may cause the shared rank discrepancy; the change does not resolve that ambiguity.

Reducing the female BMI slope lowers Bansal-context arithmetic location by approximately 4.68 mg/dL before floor/residual effects. Initial quantiles 79.039/115.560/168.450 were close to 81/115/169; location/quantile agreement may worsen.

Oh threshold discrepancies, particularly the male tail, remain. Exact fitting of the single original female >500 observation is not justified.

No final numerical compatibility claim before controller replay. All original source/assay/context/transport limitations remain.

All three source portfolios arrived together and were reviewed in full. audit.json retains every model-specific check without a mixed-unit score; f1/f2/f3.json bind the exact received portfolios, all0.json the complete compact feedback, and r1/r2/r3.json the exact own initial replay reports. Twelve marginal covariate checks are construction checks, not TG validation. Repeated statistics share participants; repeated seeds quantify generator draw variation, not source or structural uncertainty.

Common extraction distinctions remain fixed: Oh Table 1 means versus individual SDs, Table 3 reduced conditional slope, unreplayed fully adjusted/mixed/co-twin estimands, and unresolved arithmetic/geometric Table 2 interpretation. Bansal quantiles, marginal Spearman and reverse-conditional covariate summaries are distinct estimands. Source assay equivalence remains assumed and the task assay equation remains technical metadata only.

This is the single permitted retain/revise round, parent-linked to s1_initial. All final structures will be evaluated under the precommitted schedule; none is selected as a winner. Final execution is controller-only. No target outcomes, target evaluation feedback, or prior candidates outside this own new case were accessed. Static validity is not numerical compatibility or target validity.
