# Measurement-only target context

Target: reference-method serum triglycerides, LBXTR in TRIGLY_F, NHANES 2009-2010. Units are mg/dL. The enzymatic Roche Modular P method includes glycerol blanking. The official conversion to mmol/L is multiplication by 0.01129. Generate native mg/dL values; no later-cycle assay conversion is applied.

The analysis domain uses age40-79, morning examination, positive WTSAF2YR and food fast at least 8.5 and below 24 hours; complete observed BMI and reference TG. Age40+ was chosen from source applicability before target outcomes were downloaded or inspected. Standard biochemistry-profile TG is a different measurement and is not the reference. Nonfasting source evidence requires an explicit transport assumption.

[CDC TRIGLY_F measurement and analytic notes](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles/TRIGLY_F.htm). This link establishes measurement metadata only; builders must use this supplied excerpt rather than retrieve target data or use target-derived relationship evidence. No target means, distributions, signs or coefficients are disclosed.
