# HbA1c construction ha, initial

Use SHIP-Trend because it provides contemporaneous whole-population, sex-specific HbA1c quartiles and age coefficients adjusted for the available BMI covariate, in the admitted adult age range. The two SHIP cohorts are independent; the earlier wave is a temporal sensitivity check, not another fit objective. This is curated evidence use, not autonomous literature discovery.

The generator adds a sex-specific reference location, linear age term, explicitly assumed saturating BMI term, and independent right-skewed residual. All parameters and missing-identification choices are traced in model_spec.json. Residual scales allocate the reported IQR approximately between age and residual dispersion. The exact joint source covariates and conditional residual distribution are unknown. No healthy-reference limits, restricted Hoorn coefficients or prospective DIRECT coefficients are used. Hoorn and DIRECT also share first-wave Hoorn participants; they would not be independent confirmations.

One frozen invented source context checks all 12 admitted SHIP sex/wave quantiles and three admissible age slopes. Approximate population reconstruction, identity measurement mapping and quantile convention are explicit. The three fixed source seeds only vary residuals. Selection is committed in the bundle selection_rule.json before diagnostics; successful source agreement does not certify target utility.

This output supports inspection of an evidence-informed hypothesis about age association. BMI association, skew, extreme tails, subgroup and nonlinear analyses are assumption dependent. Clinical, causal and nationally representative interpretations, imputation accuracy, calibrated parameter uncertainty and measurement replacement remain unassessed. Target HbA1c answers and reserved evaluations were not read.


## Final retention decision

The three committed source seeds completed successfully and all 45 diagnostic evaluations were inspected. SHIP-Trend primary mean quantile discrepancies range from about -0.0573 to +0.0755 percentage points; age-slope discrepancies are about -0.0000303 and +0.00000615 percentage points per year. These satisfy the predeclared source-only engineering thresholds. Earlier SHIP-0 differences remain in the feedback, including a male upper-quartile deficit of about 0.157 points.

Retain the scientific model, source recipe and evidence bytes. The source approximation and assumed BMI/residual structure prevent an inference that small source differences warrant further tuning. Bind the actual three reports, portfolio, initial integrity checks and source-only selection rule. This is a no-op scientific revision, not an improvement claim. Execute the full fixed source schedule again for this final freeze, then record selection before final seeds 92101-92103.
