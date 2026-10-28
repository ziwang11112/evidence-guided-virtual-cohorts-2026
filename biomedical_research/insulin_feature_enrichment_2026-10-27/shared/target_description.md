# Blinded fasting-insulin feature enrichment packet

This packet contains adults from a U.S. national health-examination probability sample collected in 2017-2018. Each row has measured BMI, screening age, and the source's sex coding. The fasting-serum-insulin column is entirely withheld. Generate it in uU/mL (microIU/mL), retaining each random row_id.

Eligibility was fixed before inspecting outcome distributions: age 20-79; positive fasting-subsample weight (the source's 8 to less than 24 hour fasting criterion); finite positive BMI and a reserved valid insulin measurement; male/female source code; no self-reported diagnosed diabetes (borderline status retained); and no reported current insulin use. Women aged 20-44 must have documented nonpregnancy at examination. Other women have identified pregnancy excluded, but public pregnancy ascertainment outside ages 20-44 is limited. No exclusion based on reported diabetic pills was applied.

The serum assay used a Tosoh AIA two-site immunoenzymometric method. Concentration is expressed in uU/mL; the reported detection limit is 1.0 uU/mL. The reference preserves the source's released handling of results below detection. These are assay facts, not summaries of this target cohort.

Use the observed.csv and schema.json files plus your independently retrieved external aggregate literature. Original record identifiers, hidden outcome data, target outcome summaries, and survey design variables are unavailable for generation. Do not search for participant matches, retrieve source individual-level insulin data, inspect custodian files, or infer record identity from covariates. This blinding is enforced by task instructions; a shared local filesystem is not a technical access sandbox.

This is a paired complete-case pilot of scientific-analysis utility. The source weights do not automatically repair remaining item nonresponse. Do not interpret the packet alone as an unconditional population estimate or use unobserved disease states as known covariates.
