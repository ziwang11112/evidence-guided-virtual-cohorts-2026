# H02 proposed construction — not implemented

This is one fully specified conditional joint law for fictional rows. It retains the requested Q1/Q2/Q3 analytical uses while keeping their source and transport limitations visible. The proposal uses the admitted sources only, without additional retrieval. It is subject to controller review before implementation.

## Law and parameters

Write A=age in years, F=female (0/1), B=BMI in kg/m², G=fasting serum glucose in mg/dL and H=HbA1c in percent. HbA1c differences are percentage points. All coefficient values below concern this law; they are not results from target individuals.

**Design.** Create exactly 375 rows in each of the eight F by age-band cells [25,39], [40,54], [55,69], [70,79]. Within each cell A is discrete uniform on all inclusive integer ages. Sex and cell counts come from the task; uniformity within bands is an assumption. IDs will be deterministic unique strings. Equal cell WLS weights are constant because all cell counts match.

**BMI.** Let U_B ~ Beta(4,8), independently of A and F, and B=14+42 U_B. Mean=28 and marginal SD=5.491251784 kg/m². The mean is a rounded level anchor from NHANES 28.01. The beta shape, support (14,56), SD and independence are assumptions; the 0.14 quantity reported beside NHANES BMI is not a person-level SD. A bounded right-skewed law provides variation and a moderate obesity tail without allowing implausibly huge moments. It omits genuine age/sex heterogeneity because no target joint law is admitted, not because that heterogeneity is known absent.

**Glucose conditional mean.**

`mG = 94 + (3.573/17.5)*(A-50) - 4.4496*F + 0.432*(B-28)`.

The BMI and sex differences derive from Finnish S1 after the explicit 18 unit conversion. The continuous age coefficient **0.2041714285714286 mg/dL/year** uses the Finnish older–younger contrast divided by the midpoint gap 54.5-37=17.5 years; replacing the binary effect by a linear gradient and extrapolating to 25–79 are assumptions. The intercept 94 mg/dL is a rounded location choice, close to the displayed Finnish S1 prediction 93.8844 at older male BMI 28, but is not a claimed fasting-time-adjusted prediction. H02 has already selected an eligible population; this is a law for its selected G, not a preselection law later conditioned on G<126.

Let `p=(mG-55)/71` and `U_G | A,F,B ~ Beta(8.5*p, 8.5*(1-p))`. Set `G=55+71*U_G`. Thus E(G|A,F,B)=mG exactly and Var(G|A,F,B)=(mG-55)(126-mG)/9.5. The precision **8.5**, lower support **55** and distribution family are assumptions. They produce a conditional SD of approximately 11.4 mg/dL at mG=94, comparable in order to the distinct Kerman marginal SD 12.4; they are not estimated conditional dispersion or a requirement to reproduce 12.4. The task upper bound 126 is represented directly. The lower support omits severe low glucose as an explicit limitation; no clinical rule is asserted. Since mG is between 78.398114 and 112.016971 throughout the design, both beta shapes are positive without clipping a scientific mean.

**HbA1c conditional law.**

`cG = 0.23 * 0.73 / 12.4 = 0.013540322580645161`

`cB = 0.0125 - cG * 0.432 = 0.006650580645161291`

`cF = 0.023 - cG * (-4.4496) = 0.08324901935483871`

`mH = 5.45 + 0.010*(A-50) + cB*(B-28) + cF*F + cG*(G-94)`.

Let U_H ~ Beta(3,3) independent of the previous draws, and `H=mH + 0.40*sqrt(7)*(2*U_H-1)`. The innovation has mean zero and **conditional SD 0.40 percentage points**, with finite bounded support. This residual scale is explicitly chosen, not computed from any source SE, CI, marginal SD, R² or a confidence score. It is intermediate in order between narrower outcome-selected Taiwanese marginal SDs and broader Kerman marginal SD; that observation does not statistically estimate a conditional SD. Biological variation, unobserved glycemia and assay effects are pooled in this innovation without independently assigning measurement-error fractions. Homoscedasticity, symmetry and independence are structural assumptions.

The location 5.45% is a rounded anchor near the Finnish S2 older male BMI 28 prediction 5.4551%; it is not an attempt to reproduce a balanced Mexico mean. The coefficient 0.010/year is the NHANES adjusted age coefficient under transport assumptions. The number cG is first a marginal Kerman simple-projection derivation. Using it as a conditional coefficient is an explicit **marginal-to-conditional bridge**, despite adjustment and selection differences. The Finnish HbA1c BMI coefficient excludes glucose. Under a coherent linear mean law, the reduced-model coefficient equals cB+cG*0.432. Therefore cB is an assumption-dependent omitted-variable decomposition, not a separately observed effect or a causal direct effect. The sex coefficient is decomposed similarly from the Finnish reduced-model female–male difference 0.023. A nonsignificant source sex coefficient is retained as reported, without replacing it with zero or claiming a demonstrated sex effect.

No HbA1c<6.5 restriction is imposed; H02 does not specify it. Bounded innovations still limit the unexplained HbA1c tail and cannot represent every anemia, hemoglobinopathy or medication pattern. No unobserved diagnostic histories, anemia or medication fields are invented to imply verified exclusion.

## Analytical implications and finite-moment rationale

With the specified linear means and independent mean-zero HbA1c innovation, the population projections implied by this law are Q1=10*0.010, Q2=5*(cB+cG*0.432), and Q3=5*cB. `PROPOSAL_ALGEBRA.json` records these algebraic implications and bounds. They are not desired target values or reference estimates and do not create evidence. Finite draws will vary naturally; the generator will not recenter outcomes, force sample coefficients or choose favorable seeds.

All inputs are bounded. The full support yields H strictly between approximately **3.52052% and 7.50106%**, so positivity holds without HbA1c clipping or rejection. BMI support is positive; glucose support is positive and below 126. Every joint moment is finite, including the second and fourth moments used in regression variability calculations. B, G and H retain continuous within-cell residual variation, so regressors are not deterministically collinear. Beta choices are distributional assumptions made for a valid bounded cohort, not inferred clinical families. Numerical endpoint protection, if needed in implementation, will only use the nearest interior floating-point glucose bound and will be documented.

Parameter uncertainty, structural uncertainty and transport uncertainty are not represented by the residual draw or repeated seeds. No probability is assigned to the proposed model being correct. A single law is frozen for delivery, subject only to the allowed review/one-revision schedule.

## Evidence-use decisions for every requested analysis

| Analysis | Proposal | Source role and remaining gap |
|---|---|---|
| Q1_age10, H ~ age10+F+bmi5+glucose10 | Relationship use of 0.010/year from NHANES; bounded residual dispersion assumption | Closest adjustment correspondence; country, serum/plasma, measurement, selected design and linearity through 79 still require transport. Taiwanese age slopes are context-only, not substituted. |
| Q2_bmi5, H ~ age10+F+bmi5 | Relationship use of Finnish 0.0125 per kg/m² through cB+cG*0.432 | Source uses binary age, stricter HbA1c/medication selection and another population. The result is model-implied after explicit transport, not a Mexican reported coefficient. |
| Q3_bmi5, H ~ age10+F+bmi5+glucose10 | Assumption-dependent relationship cB from Finnish reduced BMI slopes and moment-derived Kerman marginal glucose slope | No directly reported matching source coefficient. Cross-cohort consistency, marginal-to-conditional transfer, common scale and no omitted interaction are essential unresolved gaps. Label partial support; do not call it directly reported. |

All analyses also depend on the chosen covariate law, absent target joint evidence and finite support. Every parameter will be stored in the specification and used by the future generator, with provenance separating reported, derived and assumed values. No parameter will be silently encoded only in program constants.

## Planned checks after release and execution

Before freezing: schema validation, exact source/provenance binding, static entrypoint validation, reviewer-approved dimensional algebra, and evidence-use mapping for all three analyses. Only executed checks will be marked pass/fail. Current work has executed scalar algebra only; no candidate or rows exist.

After the controller's isolated initial trial: check task bounds, 3,000 rows, eight exact 375 cells, identifiers and finite/marginal/joint diagnostics. Source feedback will remain approximate: NHANES adjusted age slope; Finnish BMI–HbA1c coefficient without glucose; Finnish BMI–glucose coefficient in mg/dL if a declared unit-converted evidence item is supported; Kerman Pearson correlation and marginal means/SDs; appropriate selected age-band NHANES means. Age adjustment in the Finnish check differs from its binary source model and fasting-time cannot be represented, so matching them exactly is not claimed. Unsupported exact percentile/source-covariate operations will be retained as not computable rather than relabelled.

Kerman correlation is a check-only diagnostic in addition to its explicit scalar derivation; this model need not have marginal correlation 0.23. Taiwanese summaries are qualified contextual checks because fasting and HbA1c selection differ. No source summary is a hidden target constraint. A numerical difference will be assessed for sampling, source selection, transport or implementation origin before retaining or proposing the one permitted revision.

The prospective schedule remains trial 9100, at most one revision/repair trial 9110, and final draws 9101/9102/9103 from one frozen final candidate. The controller performs all generator execution. No search session is reset and acquisition closes at first freeze.
