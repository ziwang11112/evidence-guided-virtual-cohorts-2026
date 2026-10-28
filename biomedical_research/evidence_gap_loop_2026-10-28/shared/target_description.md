# Masked HDL cholesterol enrichment packet

Generate the wholly withheld serum HDL cholesterol feature, `hdl`, in mg/dL for each random `row_id`. The observed inputs are BMI measured in kg/m^2, age at screening in years, and source sex code (1 male; 2 female). Preserve observed numeric values exactly; return only row_id, bmi, age, sex and hdl.

The case is a U.S. national health-examination probability sample collected in 2013-2014. Eligibility was fixed from metadata: ages 20-79; positive examination weight; valid sex code; finite positive BMI and an available valid HDL result. Women aged 20-44 require documented nonpregnancy; reported pregnancy is excluded for other women, but public ascertainment outside ages 20-44 is limited. There are no disease, smoking, alcohol, lipid-therapy, or fasting exclusions. This is a paired complete-case benchmark; remaining item nonresponse is not automatically corrected by source weights.

The source documents a direct serum HDL enzymatic assay with magnesium/dextran sulfate and PEG-modified enzymes; Roche Modular P and Cobas 6000 instruments were used in this cycle. The reported lower detection limit is 3 mg/dL. These are measurement facts, not target cohort summaries.

Original survey IDs, the full HDL column, all target-outcome summaries, survey weights and design variables are withheld. Use only this packet and independently obtained external aggregate evidence. Do not retrieve the source individual-level data, match participants, inspect custodian files, or infer record identity from covariates. Role instructions enforce this blinding; the shared filesystem is not an access-control sandbox.

No synthetic value is an observed patient measurement. The comparison concerns scientific analysis utility in a small prospective pilot, not individual outcome recovery or unconditional national population estimation.
