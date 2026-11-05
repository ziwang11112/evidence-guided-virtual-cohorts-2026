# H03 initial decision

Implement the reviewed bounded joint law unchanged. Exactly375 fictional rows per sex-age cell; uniform integer age within bands; bounded-beta BMI; conditional beta glucose with marginal variance correctly partitioned; conditional beta HbA1c with linear mean and constant conditional variance. All moments are finite.

Pani's NHANES adjusted age coefficient supplies Q1; the Finnish BMI-HbA1c coefficient supplies Q2 after explicitly inferred units and age/selection transport. Q3 is not directly reported: its coefficient follows from the joint moment solution using Kerman's marginal Pearson correlation and the assumed reference-age dispersion/covariates. The marginal correlation is never relabelled as a partial correlation. Printed Kerman Table2 slopes are declined because their raw-unit scaling is inconsistent with the paper's own r and SDs.

The proposal review passed with provenance annotations and no numerical change. Retained deterministic algebra and a separate nine-quantity recheck agree. The generator calculates the same solution from the specification; it never calibrates to realized rows. Required evidence-use entries map all three analyses to actual numerical settings, source links, bridge assumptions and performed preparation checks.

Finnish raw outcome units remain `not_reported`; inferred units/conversions appear separately in assumptions/provenance. Source weighting and all32 unavailable source-feedback checks remain visible. No unweighted statistic, new source population, continuous-age adjustment or target result substitutes for an unsupported source definition. See IMPLEMENTATION_CLARIFICATIONS.md.

Population, selection, assay, age coding, within-band distribution, BMI independence, conditional shape and cross-source compatibility remain strong assumptions. Particularly, transferring a marginal correlation across covariate distributions affects Q3. The normal reference-quantile approximation does not supply calibrated uncertainty. Repeated seeds measure simulation variation only.

Three task-gateway searches, zero new downloads, no useful new conditional relation; one query credit remains and no further acquisition is currently justified. This is not evidence that the literature has no such relation. Stop at static validation and independent code review. Root owns freeze and the fixed trial9100/revision9110/final9101-9103 execution schedule. No generator execution or target validation has occurred.
