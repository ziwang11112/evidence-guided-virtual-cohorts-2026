# Turkana methods review: measured-lipid evaluation candidate

Prepared 1 November 2026 (America/Chicago). Independent, methods-only assessment for the current scale-up intake. No participant data, target effect tables, generation, fitting or new experiment was inspected or run. This review covers the same original study already charged to the intake, not another literature-budget unit.

## Decision

**Retain conditionally as a measured total-cholesterol/HDL target; do not yet admit it as a general lipid-panel validation case.** The methods establish two directly measured lipid outcomes that can support a precisely defined, cross-sectional conditional-analysis target. They also establish firm reasons to exclude calculated LDL from independent measured-biomarker validation and to exclude triglycerides from an unrestricted full-population continuous target under the present information.

The suitable target is the released study's assay-defined measurements in an explicitly selected analytic sample. It is not fasting central-laboratory lipid truth, a representative population estimate, or a causal effect of lifestyle. This qualification follows measurement and sampling information, not whether any target association is favorable.

## Primary material actually inspected

- [Original study](https://doi.org/10.1126/sciadv.abb1430), through its [supplementary materials and methods](https://pmc.ncbi.nlm.nih.gov/articles/instance/7577730/bin/abb1430_SM.pdf), PDF pages 2–3 and 5–6. Inspected visually in a separately created wang Chrome tab. Pages 2–3 supplied population/interview context; pages 5–6 supplied anthropometry and lipid methods.
- [Dryad repository record](https://datadryad.org/dataset/doi:10.5061/dryad.2z34tmpjk), Methods and Usage notes. The record lists the text file `22Jul20_for_Dryad_noIDs.txt`, fourteen columns including an individual identifier, NA for missing values, and CC0 licensing. Neither preview nor download was opened.

The root separately reported the capillary OneTouch glucose method from page 6; that detail was not independently reread here and is not needed for the proposed TC/HDL target. No verified fasting protocol was obtained in this review. An attempted browser find produced no usable finding; absence of fasting instructions must not be inferred from that attempt.

## What the methods establish

| Item | Verified method or metadata | Consequence for admission |
|---|---|---|
| Total cholesterol and HDL | Supplement pp.5–6: approximately 8 mL venous blood collected into EDTA; 40 μL used immediately on CardioChek Plus following manufacturer instructions. TC, HDL and TG are measured. Dryad reports mg/dL. | TC and HDL can serve as measured outcomes. Preserve this specimen, instrument and timing definition; do not silently equate them with serum central-laboratory assays in external evidence. |
| LDL | Supplement p.6: calculated using the Friedewald relation, TC − HDL − TG/5. | It is a derived quantity, not an independent measured outcome. It may later be a declared deterministic consistency check, but must not count as another independently validated biomarker or joint relationship. The supplement overrides the repository's loose description of LDL as measured from blood. |
| TG lower limit and resulting missingness | Supplement p.6: the instrument cannot read TG below 50 mg/dL, and both TG and LDL are unrecorded for those participants. Dryad uses NA for missing values. | A complete-record TG distribution is selected by the outcome measurement process. It cannot stand in for the full distribution. Do not replace NA with 0 or 50, treat it as ordinary random missingness, or use complete cases to claim unrestricted TG fidelity. NA metadata alone does not distinguish below-range results from other missingness. |
| BMI and waist | Supplement p.5: BMI derives from measured weight and height; waist is averaged over three measurements. | These are usable definitions for declared covariates, subject to the released coding. Their units and derivations must remain distinct from body-fat percentage. |
| Age and sex | Supplement p.3: interview information is self-reported. Dryad confirms these fields. | Age/sex can enter the target definition and adjustment set; exact coding and eligibility still need to be fixed from metadata. |
| Lifestyle and sampling context | Supplement pp.2–3 describes Turkana and Laikipia contexts; Dryad provides a lifestyle category defined in the paper. | Lifestyle composition is material to the target joint distribution. A pooled coefficient may depend on that composition; an adjusted association is still descriptive. |
| Inference identifiers | Dryad's fourteen-column inventory contains individual ID and lifestyle, but no listed site, household, sampling-cluster identifier or survey weight. | Do not promise design-based population inference or cluster-robust coverage that the released fields cannot support. Lifestyle categories are not a substitute for sampling clusters. |

Fourteen columns including an identifier are thirteen substantive fields, not thirteen independent laboratory measurements. Several are covariates, anthropometric constructs or derived quantities.

## A scientifically usable conditional target remains possible

The clean minimum lipid core is age, sex, BMI, lifestyle, TC and HDL. An admissible analysis family would be the BMI coefficients in separately specified TC and HDL regressions adjusted for age, sex and lifestyle, with distributions and residual dependence examined on the same frozen virtual release. This is a candidate estimand specification, not an authorized analysis or a selection based on observed coefficient directions. Its exact models, age eligibility, common versus outcome-specific denominator and inference rule must be fixed before any reference outcomes are opened.

If the construction remains whole-cohort generation, the builder must generate covariates and lifestyle composition as well as the lipid outcomes. Supplying actual participant covariates would change the task to enrichment. A target composition may be an explicitly supplied design input or a disclosed model assumption; it cannot be recovered from hidden outcome data and then presented as independent generalization. Merely including lifestyle in a regression does not make the result invariant to all population-composition changes.

Unknown fasting status does not by itself eliminate a study-protocol TC/HDL comparison: the measured endpoint can be defined as collected. It does prevent a fasting-equivalence claim and requires explicit treatment when the construction evidence describes fasting laboratory values. This review does not assert that fasting status is irrelevant to any lipid or association.

## Minimum unresolved scientific requirements

1. **Compatible construction evidence:** Within the existing intake allowance, identify external primary evidence that informs relevant TC/HDL relationships and variation, not just marginal means. Retain its population, specimen, instrument, fasting conditions and adjustment set. A measurement/transport assumption can be explicit; it cannot be advertised as a validated bridge. The Turkana target study's outcome results cannot become construction evidence for an independent test of those same results. No such external evidence was assessed here.
2. **An executable target definition:** Resolve the released coding of age, sex and lifestyle, study eligibility, and measurement-validity/missingness rules from metadata. Set the analytic denominator without inspecting favorable effects. Use a custodial check for computable cases and usable variation after the rule is fixed; do not inspect participant rows in the builder context. The repository variable list establishes prospective availability, not adequate complete-case size or model rank.
3. **An honest inference boundary:** Establish whether sampling/dependence information beyond the listed fields is available. If it is not, this case can still compare descriptive point estimates in the released analytic sample, but cannot support nominal cluster-aware or population-representative coverage claims. An iid or heteroskedasticity-robust interval would add assumptions and would not resolve unobserved clustering.

These are the remaining case-admission requirements, not a request for a broader framework or another experimental suite.

## Firm exclusions and stop conditions

- Exclude LDL as an independently measured confirmation endpoint. Exclude a fasting-lipid or central-laboratory-equivalence interpretation without supporting documentation.
- Exclude unrestricted TG distribution, tail, prevalence or regression validation under the current missingness information. A later recorded-range estimand would be a separately declared selected-sample analysis; it would not recover below-limit values. Censoring correction requires an explicit measurement/missingness model and cannot be claimed merely from knowing the lower limit.
- Do not use this single cross-sectional study to claim a causal effect of modernization, disease prediction, cardiovascular-risk calibration or participant-level recovery.
- If the available external evidence cannot constrain a relevant measured-lipid relationship and its variability under a defensible declared transfer assumption, do not launch another marginal-only construction and call it the intended scale-up. Record the evidence gap. If metadata cannot support the promised denominator or inference, narrow the claim explicitly or exclude the case; do not search for a more favorable outcome result.

## Exposure and verification boundary

The repository page incidentally displayed its qualitative abstract. The supplement view included adjacent text already flagged by the root as incidental exposure; no new numerical target associations or result tables were sought or read. The root's existing exposure record therefore remains applicable; this review does not reset it or establish that every association is scientifically unseen. The same-study methods review adds no independent original-study count. No participant file was acquired, no row-level data were viewed, and no empirical claim about eligibility counts, missingness rates or target effects is made here.

**Admission recommendation:** retain for the bounded TC/HDL methods route, with the three scientific requirements above still unresolved. The direct-measurement distinction and TG censoring rules are sufficient to reject the broader unrestricted lipid-panel framing now.
