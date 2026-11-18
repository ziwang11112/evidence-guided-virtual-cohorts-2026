# Selected modeling decisions: why the generated relationships appear

This is an analysis aid assembled from the two frozen specifications and their
recorded code/source audits. It is not an exhaustive parameter inventory, a
confidence ranking, or a causal explanation of the observed discrepancies.
REPORTED, DERIVED and ASSUMED describe origins, not validated accuracy.

| Quantity | Recorded origin and Agent choice | What to review |
|---|---|---|
| Pastoralist BMI | Published mean 19.99 kg/m2 and SD 2.14. Both laws use these anchors. | Suitability of the source subset and applying its summary to generated demographics. |
| Lifestyle BMI means | Published descriptive differences 9.69% and 8.43% are interpreted as approximate marginal mean ratios. Urban mean 21.927031; rural about 20.2223. These are not reported adjusted regression coefficients. | Whether this interpretation is adequate for the intended adjusted analysis. |
| HDL spread | Published pastoralist mean/SD 72.69/14.72 mg/dL. A1 sets every group marginal SD to 14.72; A2 derives pastoral residual variance and reuses that residual SD across groups. | Extension from one lifestyle group to the others and its effect on variability and subgroup analyses. |
| TC group means | A1 combines HDL with non-HDL; its baseline non-HDL is reported LDL 60.89 plus an assumed 15 mg/dL remainder. A2 also uses a 148.58 TC baseline. Both introduce assumed lifestyle offsets; A1 implies TC means 148.58/150.98/163.58, A2 uses 148.58/150.08/163.58 mg/dL. | The qualitative urban increase is sourced; its numerical size, rural offset and component remainder are not newly measured target effects. |
| Sex effect on HDL | A1 assumes 4 mg/dL. A2 uses 3.87 mg/dL, numerically tied to 0.1 mmol/L times 38.67 from a raw external Maasai sex difference. | Raw external group difference is not a validated conditional coefficient in this population. |
| Age effects, interactions and joint dependence | Mostly explicit numerical assumptions. Positive lognormal innovations and TC=HDL+non-HDL are scientific modeling choices, not extracted full joint evidence. | Could these assumptions change the intended analysis despite plausible marginal values? |
| Demographic allocation | Printed age/sex/lifestyle cells rescaled from 1,360 to 1,226. Age bounds and treatment of the printed age-bin ambiguity are declared assumptions. | Whether the target mixture and support are sufficiently specified for the proposed use. |

A1 accounts for variance of the conditional mean when setting multiplicative
noise to its chosen group marginal SD. A2 uses group-specific additive residual
SD represented through lognormal sampling. This is a real implementation
difference, although both retain substantial assumptions.

The prior review records a small BMI derivation discrepancy for A1 (+0.000545
kg/m2) and A2 (-0.00000489). An early review narrative misattributed the larger
one; the correction is preserved. No generator, output or scientific result was
changed. These discrepancies do not explain the substantive lipid findings.

Questions for the domain reader: Which extension is defensible for exploratory
analysis? Which needs a better source or a sensitivity range? Which makes a
specific use uninformative? Please avoid ranking by the origin label alone.
