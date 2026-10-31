# Independent source admission audit

Date: 2026-10-31. Scope: independent reread of the three already selected papers and the official NGSP unit page. This is a source audit, not target admission, a target definition, or a joint-model specification. The target remains unfrozen.

**Decision:** retain the reviewed marginal summaries and correctly matched association constraints as source evidence, with the restrictions below. Do not admit a complete five-variable joint distribution or transport claim. The inspected originals support the core extraction in `GLYCEMIA_SOURCE_REVIEW.md`; the important refinement is to keep Lifelines model-specific sample sizes explicitly unresolved.

## Original-source verification

### Pani 2008

[Original PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC2551641/), DOI 10.2337/dc08-0577. Locators: Methods; Laboratory measurements; Statistical analysis/NHANES; Results opening; Table 1; Results immediately before Table 2.

- Both cohorts require age≥25 and FPG<126 mg/dL; FOS additionally excludes previous antidiabetic treatment, NHANES diagnosed/self-reported diabetes. FOS n=2473, NHANES n=3270; FOS retains 44 people with 2-hour glucose≥200 mg/dL.
- HbA1c: NGSP/DCCT-standardized HPLC; glucose: hexokinase. Fasting duration is not specified in inspected text.
- Table 1 explicitly says “Mean ± SE”. HbA1c(%), age<40/≥70: FOS 4.97±0.04/5.50±0.04; NHANES 5.20±0.01/5.51±0.02.
- Adjusted HbA1c age slope: NHANES **0.010 percentage points/year**, adjusting sex, BMI, FPG; P<0.001. FOS **0.012** additionally adjusts 2-hour glucose. No coefficient SE is supplied there.
- NHANES analyses incorporate survey design/weights. Opening demographic spreads are printed as SD despite implausibly small magnitudes; preserve the label and quarantine their use as dispersion parameters. Do not silently relabel.
- Appendix A3a/A3b was referenced but not retrieved. Abstract/full-table percentile discrepancies remain quarantined; cross-sectional coefficients are separate from Table 2 longitudinal changes.

### Jansen 2013 / Lifelines

[Original Wiley article](https://onlinelibrary.wiley.com/doi/10.1111/joim.12010), DOI 10.1111/joim.12010. Locators: Methods/participants, laboratory, statistics; Tables 1–3; Appendix A3–A4.

Western-European unrelated adults, GWAS-selected with oldest family members preferred; n=2921 after excluding diabetes (self-report/FPG≥7.0 mmol/L), anemia (Hb<8.2 men/<7.0 women mmol/L), missing HbA1c/erythrocytes/FPG. HbA1c: IFCC-standardized immunoassay; fasting fresh-plasma glucose: hexokinase/G6PD.

| Table 1 item | Verified summary |
|---|---|
| Age, years | 55.5±9.9 |
| Male | 1176; 40.3% |
| BMI, kg/m² | 26.5±4.1 |
| FPG, mmol/L | 5.1±0.5 |
| HbA1c | 5.6±0.3%; 38±3 mmol/mol |

Footnote: “Values are means ± SD or number (%)”.

All following HbA1c coefficients use mmol/mol. Table 2 separately adds each predictor to age/gender: BMI 0.13 (CI 0.10–0.16); FPG 2.29 (2.07–2.51). Table 3 II includes age 0.08 (0.07–0.09), gender 0.35 (0.12–0.58), FPG 2.25 (2.03–2.48); R²=20.5%. III includes age/gender/BMI/FPG/MCH/MCHC/smoking/alcohol; BMI=0.05 (0.02–0.08).

Alcohol has 89 missing; Table 2 alcohol baseline n=2832, R²=9.6%; Table 3 I also R²=9.6%. A3/A4 strata total 2832. Table 3 I/II exact n remains unstated; **2832 is inference**. Table 2 BMI/FPG row-n likewise is not explicit. Gender coding, intercept, covariance, residual law, age bounds, fasting hours remain unresolved.

### Liu 2015

[Original PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4454807/), DOI 10.1210/jc.2014-4454. Locators: Research design/method; Data collection; Calculating the hemoglobin glycation index; Statistical analysis; Tables 1–3.

NHANES 1999–2008, age≥20, fasting, excluding diabetes by history/medication/FPG≥126 mg/dL and anemia (Hb<13 men/<12 women g/dL). HbA1c assays are NGSP-certified; FPG uses hexokinase. Fasting hours are unspecified. Pregnancy remains in primary analyses.

Random training n=831 from eligible n=8310 supplies **HbA1c(%)=3.7+0.017×FPG(mg/dL)**, an unadjusted projection. HGI subtracts predicted from observed HbA1c. Subsequent analysis n=7323 follows laboratory/infection exclusions.

Table 1: HbA1c 5.3±0.01%, FPG 96.5±0.2 mg/dL, age 44.6±0.3 years. Footnote says “means ± se”; these are not individual-level SDs.

Table 3 outcome is **HGI**, age coefficient 0.006 (CI 0.005–0.007). Model 1 adjustment names survey years, age, sex, race/ethnicity, Hb, MCV, RDW, triglycerides; inflammatory predictors are examined. Model 2 adds categorical obesity. This is not an age/sex/BMI/FPG HbA1c equation. Table 2 contains Kendall tau against inflammatory biomarkers, not an HbA1c–FPG Pearson coefficient. Survey-weighted summaries and the training/subsequent-analysis populations must stay separate.

### Official NGSP units

[NGSP: IFCC and NGSP](https://ngsp.org/ifccngsp.asp), section “The IFCC and NGSP” and Table 2: **NGSP(%)=0.09148×IFCC(mmol/mol)+2.152**. The page distinguishes the earlier IFCC percent scale from mmol/mol; the coefficient for mmol/mol is 0.09148, not 0.9148.

Algebraic consequences, not additional empirical evidence: multiply outcome slopes, SDs, SEs and confidence-interval endpoints for slopes by 0.09148; add 2.152 only to levels/intercepts. Outcome variances multiply by the squared factor. Preserve published rounded percent and IFCC summaries as separate reports. Unit conversion does not reconcile selection, assay differences, covariate adjustment or transport. The page's eAG relationship describes average glucose, not FPG.

## Admission boundaries and quarantines

The following are audit judgments about how the verified quantities may be used:

| Item | Usable constraint | Quarantine / condition |
|---|---|---|
| Marginal summaries | A published cohort-specific mean, SD, SE or count with its original label | An SE is not a population SD; do not apply SE×√n to survey summaries as though sampling were simple random. Do not infer tails, truncation, support or covariances from means/SDs alone. |
| Separate regressions | Keep each coefficient attached to its outcome, predictor unit, selection and adjustment set | Separate added-predictor fits cannot be pasted into one multivariable equation. Forward-stepwise estimates cannot be reduced by deleting conditioning variables. |
| Lifelines model comparisons | Treat Table 2 and Table 3 as related published projections | No silent assignment of the full-cohort margins to an unconfirmed complete-case model. Additional appendix evidence strengthens a sample-size inference without establishing it. |
| Sex/gender coding | Preserve the printed coefficient as an un-oriented binary-covariate result | Do not assume male=1/female=0 or infer coding from coefficient signs. A numerical implementation requires explicit declared coding and support, not a guessed source convention. |
| Intercept/residual reconstruction | Algebraic derivations can be considered only when the required inputs genuinely correspond | Do not recover an exact intercept from marginal means across potentially different samples. Rounded SD plus R² does not supply an exact residual law or residual SD; homoscedasticity and normality would be assumptions. |
| Cross-source consistency | Compare source-context results with their boundaries visible | Pani/NHANES years overlap Liu/NHANES; they are not independent replication. Do not pool source summaries as one cohort or average incompatible slopes. |
| Population/measurement transfer | Preserve distinct clinically screened nondiabetic source contexts | Diabetes exclusion does not imply normoglycemia or universal health. No pregnancy restriction, ethnicity, fasting duration, age support or assay equivalence may be filled in without evidence or an explicit assumption. |
| Five-variable feasibility | The named marginal and conditional-association checks can constrain a prospective pilot | They do not identify the five-variable distribution. Predictor dependence, unreported conditional effects, residual distribution, missingness and transport need declared assumptions. A good source fit cannot validate a target population. |

The critical prospective constraints are therefore source-indexed projections, not a recovered generative mechanism. A source replay must retain the source regression orientation and model-specific conditioning. Any new target definition should be frozen separately before transport or target performance is assessed.

## Access and resource ledger

- Local task source read: `evidence/GLYCEMIA_SOURCE_REVIEW.md`. Also read the evidence-cohort-generation skill and listed this evidence directory's filenames. No target records, target results, private/custodian material, STATE files, generated rows or code were inspected.
- External retrieval: **4 web-tool calls, 16 open operations, 4 distinct URLs** (three original papers plus one official units page). Repeated opens selected text windows of those same sources. No search queries, additional primary sources, supplements, reference-link papers, ENSANUT searches or target-result searches.
- **Three independent original-paper rereads; zero additional new primary papers.** These are the same three already counted by the cycle's source review. The NGSP page is measurement guidance, not another primary cohort paper.
- Direct HTTP/application-body downloads: **0**. Direct downloaded body bytes: **0**. Web-service body/traffic bytes are unmetered; zero direct bytes is not a zero-network-traffic claim and does not revise the parent review's earlier download ledger.
- Source article/PDF/XML/IPD files saved: **0**. Only this authored audit was written; no evidence export includes source bodies.
- Verbatim excerpts are limited to the short quoted labels above (Pani 3 whitespace-delimited tokens; Jansen 8; Liu 3; NGSP section title 4). Numerical quantities and equation are transcribed facts, with original locators. No unresolved issue has been silently repaired.

