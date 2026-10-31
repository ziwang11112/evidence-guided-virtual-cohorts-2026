# Source-only glycemia evidence review

Date: 2026-10-31. Status: extraction and feasibility advice, **not evidence admission**. Proposed variables: age, sex, BMI, fasting plasma glucose (FPG), and HbA1c. The target definition remains unfixed. No target participant data, target analyses, custodian files, STATE files, or generated rows were read or produced.

## Decision supported by this review

An explicitly assumption-indexed five-variable pilot is now more defensible than it was after the earlier four-paper scout. Jansen/Lifelines supplies all five margins in one source and two directly usable conditional-association estimands involving subsets of those variables. Pani supplies an age coefficient adjusted for the other three predictors. **These constraints do not identify the full five-variable distribution.** A protocol may test the three estimands below while treating unreported dependence and residual distributions as assumptions. If admission requires a complete published joint model, neither the five-variable proposal nor a four-variable reduction satisfies that stronger requirement.

The most coherent initial source context is Lifelines, with independent contextual checks from Pani/FOS and the partially overlapping NHANES analyses. Do not pool their summaries into a fictional common cohort. A simpler alternative is age/sex/FPG/HbA1c, retaining Lifelines Model II; this removes the need to invent a BMI-conditional outcome coefficient, but still leaves predictor dependence, sex coding, intercept, and residual distribution unresolved. The previously proposed age/sex/BMI/FPG alternative remains available from Oya, with the earlier coefficient cautions unchanged.

## Local reuse and exposure ledger

Only these source-side local files were read:

- `work/analysis-utility-preparation-2026-10-29/evidence/README.md`
- The same directory's `candidate_packet.json`, `source_screen.csv`, and `hba1c_evidence.json` (source identities, source quantities, adjustment/selection fields; compact extraction of Hoorn and SHIP coefficients after a large JSON display was truncated).
- `work/autonomous_research_2026-10-31/admission/external_evidence_scout.md`.

No local original full-text files were reopened. Historical extraction status is **verified full text, pending independent admission**, not already approved evidence. This review reuses those checked quantities without re-performing their original audit.

| Reused paper/context | Evidence retained; exact locator | Boundary |
|---|---|---|
| SHIP2019, DOI [10.1186/s12902-019-0338-7](https://doi.org/10.1186/s12902-019-0338-7) | Existing packet Table 2: age slopes in HbA1c percentage points/10 years, BMI-adjusted: SHIP-0 men 0.159 (SE 0.012); SHIP-Trend men 0.153 (0.011), women 0.191 (0.011). Packet also has sex-specific medians/quartiles and healthy age/sex limits. | Whole populations include diabetes; selected-healthy limits are different populations. Table 3 versus narrative discrepancies remain unresolved. Spline strata cannot use their linear term alone. |
| Hoorn2020, DOI [10.1371/journal.pone.0233769](https://doi.org/10.1371/journal.pone.0233769) | Packet Table 1: first/second wave age 61.4 ± 7.3 / 53.9 ± 6.7 years; BMI 26.5 ± 3.5 / 26.1 ± 3.9; HbA1c 5.4 ± 0.7 / 5.4 ± 0.4%; these are SDs. Table 2 BMI quartile effects are negative after glucose, waist/hip, and lifestyle adjustment. | Excludes known diabetes, includes screen-detected diabetes. Negative adjusted BMI effects cannot become age/sex/BMI-only effects. First wave overlaps DIRECT. |
| DIRECT2017, DOI [10.1371/journal.pone.0171816](https://doi.org/10.1371/journal.pone.0171816) | Packet Table 1 baseline HbA1c means/SDs: Hoorn and KORA 5.3 ± 0.4%; Inter99 5.7 ± 0.4%; METSIM 5.7 ± 0.3%. | Main equations predict approximately six-year future HbA1c and need waist, medications, smoking, parental history. They are not contemporaneous five-variable equations. |
| Oya2014, DOI [10.2169/internalmedicine.53.1580](https://doi.org/10.2169/internalmedicine.53.1580) | Earlier scout, original PDF p.943 Tables 1–2: sex×center age/BMI/FPG means and SDs; male FPG-on-age B=0.224 mg/dL/year (SE 0.026), center-adjusted. | Ages 30–79, no diabetes and FPG<126 mg/dL plus health/medication exclusions; 10-hour fast. No BMI–FPG covariance. Male BMI row has printed scaling inconsistency; female regression orientation/scaling unresolved. |

The earlier scout's Baba2001, Ikeda2008, and Li2018 descriptions were read through that report, but contribute no new HbA1c quantities. Their original articles were not opened here.

The fixed **three new substantive original-paper audits** are Pani2008, Liu2015, and Jansen2013. Pani and Jansen were previously screened/excluded leads, not quantitatively extracted sources in the supplied packet; they therefore count as new audits. Pani's previous NHANES exclusion applied to an earlier target and does not itself establish current admission. A direct open of PMC2671106 returned only a browser-check page; no paper content was read or used. Search output exposed additional unselected titles/snippets, including a multi-country glycemia comparison; none was opened or imported as evidence. No ENSANUT query, identified ENSANUT article, target result, or target data file was used. Search stopped after the third substantive paper was fixed.

## New paper 1: Pani 2008

[Original article, PMC2551641](https://pmc.ncbi.nlm.nih.gov/articles/PMC2551641/), DOI 10.2337/dc08-0577. Read depth: Methods, Results, Tables 1–2; appendix located but not recovered. FOS n=2473 and NHANES 2001–2004 n=3270; age≥25, FPG<126 mg/dL; FOS excludes prior antidiabetic medication, NHANES excludes self-reported diabetes. FOS retains 44 participants with diabetic-range 2-hour glucose; its separate NGT subgroup is stricter. Assays: NGSP/DCCT-standardized HPLC; hexokinase glucose. Fasting duration is not specified in inspected text.

Results paragraph immediately before Table 2: adjusted age slopes, HbA1c percentage points/year, FOS 0.012 (sex, BMI, FPG, 2-hour glucose), NHANES 0.010 (sex, BMI, FPG); P<0.001, no coefficient SE supplied there. Abstract slopes are not interchangeable adjusted estimates.

Table 1 HbA1c mean±SE:

| Age | FOS | NHANES |
|---|---:|---:|
| <40 | 4.97±0.04 | 5.20±0.01 |
| ≥70 | 5.50±0.04 | 5.51±0.02 |

Main-text age/BMI spreads are labeled SD but suspiciously small; quarantine them rather than reclassifying. Table 1 explicitly uses SE. Narrative/abstract percentile disagreements also preclude silent harmonization. Appendix A3a/A3b coefficients beyond the displayed age effect, intercept, and residual scale remain unextracted.

## New paper 2: Liu 2015

[Original article, PMC4454807](https://pmc.ncbi.nlm.nih.gov/articles/PMC4454807/), DOI 10.1210/jc.2014-4454. Read depth: eligibility, laboratory/statistical methods, Tables 1–3. NHANES 1999–2008 adults≥20, fasting, no diabetes by history/medication/FPG≥126, no anemia; pregnancy retained in primary analyses. HbA1c NGSP-certified; FPG hexokinase; fasting hours unreported here.

Methods “Calculating the hemoglobin glycation index”: random n=831 training subset gives **HbA1c(%) = 3.7 + 0.017 × FPG(mg/dL)**. This is a univariate regression, not adjusted for age/sex/BMI. HGI=observed−predicted HbA1c. Subsequent analysis n=7323 after additional exclusions.

Table 1 overall age 44.6±0.3 years, FPG96.5±0.2 mg/dL, HbA1c5.3±0.01%; all ± values are **SE**. Table 3 age/HGI coefficient 0.006 (95% CI0.005–0.007) has erythrocyte, inflammation, ancestry, lipid, year, and obesity adjustments. It cannot be added to the univariate FPG equation as a five-variable model. Table 2 reports Kendall tau with inflammatory markers, not HbA1c–FPG Pearson correlation. Residual SD and full covariance are unavailable. Cohort years overlap Pani/NHANES; these are not independent replications.

## New paper 3: Jansen 2013 — preferred coherent source context

[Original Wiley article](https://onlinelibrary.wiley.com/doi/10.1111/joim.12010), DOI 10.1111/joim.12010; PMID23121487. Read depth: Methods, Tables 1–3 and footnotes. Lifelines western-European unrelated adults; GWAS selection favored oldest unrelated family members. Exclusions: self-reported diabetes or FPG≥7.0 mmol/L, significant anemia, missing measurements. Explicit age bounds and fasting hours were not found. HbA1c immunoassay is IFCC-standardized; FPG uses fresh fasting venous plasma, hexokinase/G6PD.

Table 1, n=2921:

| Variable | Mean±SD or count |
|---|---:|
| Age, years | 55.5±9.9 |
| Male | 1176 (40.3%) |
| BMI, kg/m² | 26.5±4.1 |
| FPG, mmol/L | 5.1±0.5 |
| HbA1c, %; mmol/mol | 5.6±0.3; 38±3 |

Table 2 HbA1c outcome **mmol/mol**: BMI coefficient 0.13 (CI0.10–0.16), FPG coefficient 2.29 (2.07–2.51); each predictor separately added to age/sex. Table 3 Model II: age0.08 (0.07–0.09), gender0.35 (0.12–0.58), FPG2.25 (2.03–2.48); R²20.5%. Gender coding, intercept, predictor covariance, and residual law are unreported. Model III BMI0.05 (0.02–0.08) additionally conditions on FPG, erythrocyte indices, smoking, alcohol; do not delete those terms. Table 2's alcohol analysis uses n=2832; Table 3 has the matching baseline R²9.6%, suggesting a different complete-case sample (inference; exact model n requires confirmation).

## Unit handling and model boundaries

Keep original and derived units separate. [NGSP's official IFCC equation](https://ngsp.org/ifccngsp.asp), “The IFCC and NGSP” and Table 2, is NGSP(%) = 0.09148×IFCC(mmol/mol)+2.152. For outcome slopes, SEs, SDs, and CI widths multiply by 0.09148; the offset applies only to levels/intercepts. Conversion does not resolve assay or population transport. Published rounded percent and IFCC summaries should both be retained; do not force them to be exactly equal. Glucose unit conversion, if implemented, must record its fixed factor and preserve original mmol/L quantities. FPG is not estimated average glucose; an HbA1c/eAG equation is not a fasting-glucose model.

The papers establish selected marginal moments and regression projections, not an executable joint distribution. A construction would still need declared age support/distribution; sex-related predictor distributions; age–BMI–FPG covariance; conditional HbA1c noise, heteroscedasticity and tail behavior; truncation consistent with eligibility; and a transport rule. Independence, a Gaussian copula, homoscedastic normal residuals, or a particular missing-covariate distribution are model assumptions. None becomes evidence because it is convenient or yields a positive-definite covariance matrix.

Intercept recovery from marginal means would be an algebraic derivation requiring the same population, coding and model; the Lifelines complete-case difference and unresolved gender coding block an exact recovery here. Likewise, R² plus a rounded marginal SD does not provide an exact residual SD for a different sample. The NHANES SEs must not be multiplied by sqrt(n) to obtain population SDs without design information. Cross-sectional age slopes do not equal within-person aging effects.

## Three scientific estimands matched to the evidence

These are association-reproduction questions, not causal or novelty claims. Their regression orientation is **HbA1c as outcome**; reverse regression is not equivalent.

1. **Age-associated HbA1c beyond fasting glycemia and adiposity.** Predeclare the age coefficient in HbA1c~age+sex+BMI+FPG among the protocol's corresponding diabetes-excluded adults. Pani's NHANES adjusted coefficient supplies the source anchor. This tests whether the generated joint data retain an age association after the specified adjustment. Population/assay differences could defeat transport; Pani/FOS adds 2-hour glucose and is contextual, not the same estimand.
2. **Adiposity-associated HbA1c at fixed age and sex.** Predeclare the BMI coefficient in HbA1c~age+sex+BMI. Use Jansen Table 2's BMI row and its stated units/CI. It deliberately does not condition on FPG or waist. The negative Hoorn coefficients answer a differently adjusted question, so they do not license changing this sign or establish a biological contradiction.
3. **Fasting-glycemia-associated HbA1c at fixed age and sex.** Predeclare the FPG coefficient in HbA1c~age+sex+FPG. Jansen Table 2's FPG row offers the full-sample source anchor; Table 3 Model II provides a related complete-case check. Liu's unadjusted equation is a separate projection, useful for sensitivity/context only. This tests biomarker association, not the ability to infer average glucose or diagnose diabetes.

These three constraints can coexist with many unreported predictor covariance structures. A source replay should reproduce each under its original regression and selection, then expose sensitivity across declared unresolved structures. Reproducing constraints is a construction check, not proof of transport. A further unsupported estimand, such as BMI-adjusted FPG or FPG×age interaction, may be prospectively evaluated as an explicitly unprovided stress test, but should not be tuned to invented coefficients or described as source-identified.

No generated data, source replay, target performance, or scientific finding is claimed by this review.

## Retrieval and resource accounting

All new-paper content was read from original publisher/PMC sources; search snippets were used for routing only. Three original papers were substantively audited; one additional official NGSP measurement page was read. Five search queries were issued (one Pani query; one Pani-appendix query; two batched queries for PMC2671106 and joint glycemia evidence; one Lifelines query). The earlier source-only packet and scout count separately as reuse.

Direct HTTP: one successful in-memory Europe PMC Pani XML read, **67,754 bytes**, SHA-256 `e512698e1b835a0c4881b31ff02e1ed839403ac7c32fcb1627742c53142ddc77`. URL: `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2551641/fullTextXML`. Two direct requests attempted `.../PMC2551641/supplementaryFiles`: the first yielded before completion and its terminal result was not retained; the second timed out before a response body was obtained. No supplement content was used. Both scripts capped a body read at 10,485,761 bytes; the first request's transferred amount is unknown. Therefore 67,754 is the known positive application-body count, **not a total network-byte claim**. Web-service retrievals, failed opens and network overhead are unmetered. The direct-read upper bound across the exact successful XML plus both capped supplement attempts is 21,039,276 application-body bytes; it does not bound web-service or protocol traffic.

**Zero source article/XML/PDF/IPD files were saved to disk.** Only this authored report was written. No raw data were requested, downloaded, or analyzed; no source approval, model run, or STATE mutation occurred.
