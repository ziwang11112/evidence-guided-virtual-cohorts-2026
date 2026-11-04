# Independent evidence review

Date: 2026-11-04. Reviewed analysis: `hba1c ~ 1 + bmi + glucose + age + female` in the supplied Chinese community analytical population.

## Decision

The acquisition has obtained useful source-context constraints, including a continuous BMI association with glucose adjustment and a contrasting BMI result under a different conditioning set. None of the five inspected studies directly identifies the requested BMI coefficient for Chinese adults aged 35–74 with no diabetes/treatment exclusions and central serum glucose of unverified individual fasting status. Retain the evidence and its conflicts; do not fill that gap by treating different estimands as interchangeable.

Four studies are supported by gateway-registered originals. The LifeLines article has separately inspected publisher-rendered evidence; it is suitable for inclusion in this evidence report with its route and qualifications preserved, but this review does not create a gateway approval or registry entry. No generator, candidate, parameter specification, source replay, or clinical-row analysis was constructed.

## Review scope and provenance

- Read the five selected originals and compared their principal statistics and classifications with `evcGap01/reports/EVIDENCE_CANDIDATES.json`. The Hainan and Japan originals also received a delegated local-only extraction check; that check made no network calls or file changes.
- Verified all twelve registered original XML/text/manifest files for the four PMC studies against their registry SHA-256 values and accepted gateway artifact events. These checks establish byte/procedural provenance, not scientific validity.
- Inspected the saved LifeLines publisher render, including methods and Tables 1–3, then independently reopened the exact successful publisher URL and reproduced the central table values. This saved artifact is partial rendered text, not a complete raw publisher HTML/PDF.
- Reviewed `EVIDENCE_ASSIGNMENT.md`. It explicitly resolves the generic author packet's construction clauses in favor of acquisition only, preserves the packet, and states that the narrower byte limits are procedural. The protocol review was amended accordingly.
- No old work/results/manuscript content, individual clinical rows, or candidate contents were read. No new study was sought.

## Source classifications

### S1: Hainan, Li et al. 2021 — descriptive and rank-association evidence

[Original](https://pmc.ncbi.nlm.nih.gov/articles/PMC7960723/), version PMC7960723.1; saved text `sources/gateway/0500a8193e7aa69aa70a347519211515c6c08c29c6e8c026609c90ad7f7e627f.txt`.

The source reports 1,579 participants (567 men, 1,012 women), including diabetes and medication users. Main-text age, fasting plasma glucose and HbA1c mean/SD pairs and sex-specific HbA1c–FPG Spearman correlations agree with the ledger. These may constrain the source's marginal and rank-association summaries. The methods describe a fasting protocol of at least ten hours; this is documentation of a protocol, not proof of individual adherence. Sampling dates, target age bounds and a representative recruitment frame are not established in the inspected main methods.

The principal restrictions are consequential:

- Table 1 is logistic regression for T2D, not continuous HbA1c regression. Its BMI B values are not HbA1c slopes.
- The figure workflow applies log10 transformation and removes some outliers for visualization. The separate SPSS-regression descriptions do not establish the exact scale/orientation of uninspected supplemental coefficients.
- The text's HbA1c–FPG coefficient ordering conflicts with its stated sex comparison. The acquisition appropriately quarantines those slopes rather than inverting or assigning them to the target outcome.
- The listed additional adjustments do not establish a BMI association conditional on FPG, age and sex. Sex-stratified analyses also do not estimate a female-indicator coefficient.

The supplement was not inspected; its unsupported gateway format is an access limitation, not evidence that the missing coefficients are zero. Data reuse from Li et al. 2020 is explicit in the original and should remain one overlapping cohort, not independent confirmation. Relevant original locators: lines 178–198, Table 1, lines 423–425, methods lines 637–649, reference 39.

### S2: Japan Diabetes Prevention Program, Sakane et al. 2017 — partial quantitative evidence; Beta scale unresolved

[Original](https://pmc.ncbi.nlm.nih.gov/articles/PMC5330780/), version PMC5330780.1; saved text `sources/gateway/3704a552039c61405b70e2971bbe20a7276ad8571f200ec0aebb6f7582ce8c1b.txt`.

This is a selected Japanese IGT sample, enrolled at ages 30–60 during 1999–2002, with 121 men and 124 women. Diabetes and additional conditions were excluded. The total 245 does not establish the complete-case denominator for every fitted model because missing cases were omitted by analysis.

Table 1 contains medians and quartiles, not means and SDs. Table 2 contains Pearson correlations, not Spearman correlations: BMI–HbA1c r=0.29 in men and 0.08 in women. Table 3 reports BMI **Beta=0.27** (men, P<0.01) and **Beta=0.22** (women, P=0.03), with no CI/SE. Neither the text nor Table 3 explicitly defines that Beta as standardized or unstandardized. The ledger's unresolved-scale classification is correct; the numbers cannot be certified as HbA1c percentage points per kg/m² or as verified standardized coefficients.

The final male model contains BMI, FPG, 2-hour glucose and white-rice intake; the female model contains BMI, FPG, HOMA-β and bread intake. Neither includes age, and neither estimates a female coefficient. The positive fitted BMI terms therefore offer source-specific conditional information, not a portable target slope or required target sign. HbA1c assay calibration alignment is unresolved. Relevant locators: methods lines 200–219; Tables 1–3, especially lines 463–509.

### S3: Pani et al. 2008, FOS/NHANES — adjusted age constraint, not a BMI coefficient

[Original](https://pmc.ncbi.nlm.nih.gov/articles/PMC2551641/), version PMC2551641.1; saved text `sources/gateway/77b5f7f6715e9a07e28eab219ed09f29f266e59d803003ba4b0240bedc5ace64.txt`.

The main Results text reports adjusted cross-sectional age coefficients of **0.012 HbA1c percentage points/year in FOS** and **0.010 in NHANES**, after sex, BMI and FPG adjustment; FOS additionally includes 2-hour glucose. These differ from the unadjusted FOS value of 0.014 in the abstract. Main-text P values are supplied, but the inspected passage does not give the coefficient CIs/SEs; uninspected Appendix A3 must not be treated as reviewed.

The NHANES age effect has the requested companion covariates in its own nondiabetic US population. It does not reveal the other fitted slopes or identify an intercept, residual law, or target covariance matrix. Source plasma glucose is in mg/dL; the age coefficient does not require converting glucose units. The HbA1c assays are described as NGSP/DCCT-standardized HPLC. Table 1 means are accompanied by SEs, not SDs; its ≥70-year category cannot be equated with target ages 70–74.

Selection remains material: FOS included 2,473 adults aged ≥25 in 1991–1995; NHANES included 3,270 adults aged ≥25 in 2001–2004, with diabetes exclusions and survey weighting. The FOS main nondiabetic sample still included 44 people with diabetic-range 2-hour glucose to maintain comparability with NHANES, which lacked OGTT. Thus “nondiabetic” is the paper's operational definition, not absence of all screen-detected diabetes. The longitudinal FOS subset overlaps the cross-sectional sample and estimates a different relationship. Relevant locators: lines 193–225 and 248–253; Table 1, lines 644–739.

### S4: LifeLines, Jansen et al. 2013 — strongest continuous conditional BMI lead

[Publisher original](https://onlinelibrary.wiley.com/doi/10.1111/joim.12010), DOI 10.1111/joim.12010; saved render `sources/web/jansen_2013_wiley_web_render.txt`, publisher lines 235–361.

Table 3 Model III reports:

| Predictor | Beta | Reported CI | Native effect unit |
|---|---:|---|---|
| BMI | 0.05 | 0.02–0.08 | HbA1c mmol/mol per kg/m² |
| FPG | 2.13 | 1.91–2.36 | HbA1c mmol/mol per mmol/L |
| Age | 0.07 | 0.06–0.09 | HbA1c mmol/mol per year |

Adjustment: age, gender, BMI, FPG, MCH, MCHC, smoking and alcohol; genetics enters later models. Native-unit interpretation follows table labels and selective erythrocyte standardization. “Beta” alone does not imply standardization. CI level and gender coding remain unverified.

The 2,921-person Western-European sample excluded diabetes/anemia and favored older unrelated family members. Table 2 gives alcohol-model n=2,832; Model III's denominator is inferred from 89 missing alcohol responses. The final ledger correctly marks this inference. Added covariates and selection prevent direct target transfer.

The ledger's conversion divides by the source's factor 10.93; it is algebraic, not a target estimate. No conversion search was performed.

### S5: Hoorn Studies, Wisgerhof et al. 2020 — retain contrasting conditional results

[Original](https://pmc.ncbi.nlm.nih.gov/articles/PMC7272077/), version PMC7272077.1, including embedded review history; saved text `sources/gateway/64f2ab1d3dde956c0eadec2006458d8b8f1ff3e80c05efe6ee7ec64f7c0b5ee4.txt`.

The first sample contains 2,309 adults aged 49–75 from 1989–1992; the second contains 2,619 aged 40–65 from 2006–2007. Known diabetes/glucose-lowering treatment was excluded; screen-detected diabetes was retained. Small amounts of missing data were multiply imputed. These are neither the unrestricted target population nor a strictly complete-case analysis.

Table 2's BMI coefficients are quartile-versus-Q1 **HbA1c percentage-point differences**, not continuous slopes. The ledger's values and confidence intervals agree with the saved original. In particular, Q4 contrasts are −0.135 (95% CI −0.228 to −0.043) and −0.022 (−0.044 to 0.001) for the first and second samples. The second sample's Q3 and Q4 intervals include zero; the first sample's pattern is not monotonic.

Both models condition on FPG, 2-hour glucose, age, female versus male, BMI quartiles, waist circumference, hip quartiles, smoking, alcohol, carbohydrate intake and vitamin-C quartiles. The first also includes creatinine quartiles and fiber. The first-wave backward-selection threshold was P<0.10; it must not be presented as an a priori target model. Simultaneous body-size and glucose adjustments define a different association from the requested regression. The embedded author response explicitly cautions that closely related predictors make the inverse BMI estimates unstable.

Continuous predictors are scaled per reported SD; the female row is an explicit female-minus-male contrast. Do not convert the BMI contrasts to slopes by assuming quartile distances, or treat the Spearman correlations in Table 1 as Pearson covariances. The ledger correctly preserves the first-wave FPG point/CI asymmetry and the differing reported 2-hour-glucose SDs without repairing them. Relevant locators: methods lines 370–440; Tables 1–2, lines 475–790; author response around line 1973.

## Corrections and remaining assumptions

The final ledger retains the critical distinctions: Japan's Beta scale is unknown; Hainan's ambiguous and reverse-orientation slopes are quarantined; Hoorn's quartile contrasts and uncertain pattern remain visible; LifeLines gender coding and CI level are unresolved. The requested denominator-provenance correction has been made and independently checked in the final JSON. Prefer “documented fasting protocol” over wording that could imply verified individual adherence. No blocking extraction defect remains in the reviewed classifications and central constraints.

No direct cohort overlap among these five original studies was identified. Repeated models, FOS longitudinal subsets, earlier Hainan reports, and the same study's two Hoorn cohorts must not inflate the count of independent studies. The four saved PMC texts contained no CHNS alias; population descriptions also distinguish their named cohorts. This is evidence of screening performed, not proof of universal absence of excluded-cohort material. Incidental excluded snippets recorded during acquisition remain excluded.

The unresolved scientific assumptions are substantial but specific:

1. Transport across geography, age/calendar windows, diabetes/treatment and anemia selection, and assay/specimen differences.
2. The target glucose measurement process and fasting-adherence mixture. A documented source fasting protocol does not estimate a target contamination rate.
3. Removing a source model's extra covariates. Without their relationships to the target predictors and outcome, the richer model's BMI coefficient cannot be preserved by assumption-free marginalization.
4. A full target joint distribution, intercept, residual variation, nonlinearities and treatment mixture. Marginal means, selected correlations and several conditional coefficients do not identify these.
5. Sampling uncertainty versus transport uncertainty. Reported CIs describe source estimators; they do not measure uncertainty about moving the relationship to this target. No confidence score or extra synthetic rows can supply that missing information.

Source-context constraints are therefore validated for their stated summaries and models, not for arbitrary recombination into a target generator. The contradictory conditional BMI patterns are informative about conditioning and selection; they do not justify choosing the preferred sign, averaging incompatible effects, or calling a cross-sectional association causal.

## Reviewer access accounting and stop

Reviewer searches: **0**. Reviewer new studies: **0**. Reviewer downloads/source files: **0**. Reviewer web-page opens: **2**, both for the already-selected LifeLines study:

1. `https://onlinelibrary.wiley.com/doi/full/10.1111/joim.12010` — failed with an internal/inaccessible tool result; counted.
2. `https://onlinelibrary.wiley.com/doi/10.1111/joim.12010` — successful publisher open centered at line 330, reproducing the central table and its context.

No further network calls are planned. The final `SEARCH_LOG.json` records five acquisition plus two reviewer opens: **seven shared web opens**. Its seven gateway queries plus three web queries equal **ten combined queries**, including metadata lookups; the gateway operation records end at four downloads. Five original studies were seriously reviewed. The `EVIDENCE_REPORT.md` agrees with these totals and the final source classifications. No budget was reset. Saved bytes for this review consist only of review documents; browsing traffic is unmetered and is not reported as zero network bytes. Final aggregate file-byte inventory belongs to the controller's consolidated accounting.

The five-study ceiling has been reached. Stop with these usable constraints, source-access limitations and unresolved target questions; no sixth study or candidate construction is required by this review.

## Controller summary cross-check

The central source statements and counts in this unit's draft `RESULTS.md` were cross-checked against the final ledger and originals. The controller was advised to describe prohibited prior-file reads as a procedural boundary rather than absence of technical access, and to distinguish the partial saved publisher rendering from the four saved gateway originals. The source itself supplies the slope-conversion factor, so availability of a conversion source is no longer an unresolved gap. Assertions about an earlier run's abstract-only access and a subsequent public export are outside this independent review's scope; those files/runs were not inspected.
