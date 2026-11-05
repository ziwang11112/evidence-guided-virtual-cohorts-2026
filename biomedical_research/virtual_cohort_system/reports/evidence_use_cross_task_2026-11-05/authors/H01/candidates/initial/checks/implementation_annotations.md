# H01 implementation clarifications

The reviewed proposal and source-review request remain unchanged. No numerical law is redesigned.

Independent source review requires one provenance correction: Finland supplement Tables S1/S2 name outcomes and print coefficients without explicitly printing their response units. The interpretation S1=mmol/L and S2=HbA1c percentage points is an inference from the main-text Table 1 scales and fitted intercepts, not a directly labelled regression unit. Candidate evidence preserves the original coefficient numbers with unit `not_reported`; assumption `A_FIN_UNIT` records the inference and 18.0 mg/dL/mmol/L conversion. No exact source-semantic match is claimed.

Hoorn context retains standardized continuous predictors, BMI quartile contrasts, multiple imputation pooled using Rubin's rules, and the backward-selected expanded adjustment set. It cannot provide a five-variable continuous-BMI replay.

Source feedback recipes retain unavailable weighting, missingness and operator definitions as `not_computable`. All numerical implications already calculated are deterministic model integrations, not source reproduction or target validation. The root controller alone performs freezing and isolated execution.

First semantic preflight failed because the `uncertainty_role` annotation for two SD evidence items described the statistic itself rather than its uncertainty field. The SD values remain estimates of individual marginal dispersion; their sampling uncertainty is not reported. The annotation was corrected to `not_reported` for the uncertainty of each SD estimate, with no value/model change. The original failure receipt is retained.
