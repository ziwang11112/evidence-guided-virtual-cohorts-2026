# External BMI–lipid association inventory

Audit date: 9 November 2026. This branch read the approved source originals and newly retrieved primary literature. It did not inspect targets, candidates, generated outputs, or individual datasets. Numerical values below are recorded from original tables; source bodies and rendered table images stay local.

## Decision

**No exact pooled, unweighted, raw-BMI coefficient adjusted only for age and sex was established by this branch.** There are usable candidates for separately labelled analyses: raw lipid change per one standard deviation of BMI with broader adjustment, sex and sometimes location stratification. They cannot silently become the requested common raw-BMI slope. Independent review has verified the strongest Soares 2020 table and its limitations. Root separately audits Greiner 2021.

## Continuous association candidates

[Soares et al. 2019](https://gh.bmj.com/content/4/5/e001542), main Table 3, reports the following raw lipid differences in mmol/L per **one SD of BMI**:

| MEIRU group | BMI model n | TC coefficient (95% CI) | HDL coefficient (95% CI) |
|---|---:|---:|---:|
| Rural women | 4,971 | 0.23 (0.19, 0.26) | −0.03 (−0.04, −0.02) |
| Rural men | 3,548 | 0.20 (0.16, 0.23) | −0.03 (−0.04, −0.02) |
| Urban women | 7,455 | 0.13 (0.11, 0.15) | −0.05 (−0.05, −0.04) |
| Urban men | 3,705 | 0.15 (0.12, 0.18) | −0.04 (−0.05, −0.04) |

Community residents aged ≥18 in Southern Karonga and Lilongwe, Malawi, were examined during 2013–2017. Models include age, ethnicity, education, assets, marital status, parity in women, lipid medication, smoking, alcohol, physical activity, and HIV/ART status. Household clustering uses robust SE; regression sampling weights are not explicitly reported. Lipids were assayed in ≥8-hour fasting serum using Beckman Coulter AU480. Missing fasting lipids and covariates cause selection; see machine-readable eligibility fields. The exact BMI standardization reference population and denominator are **unspecified**. Supplementary Figure 2 (page 11) gives age-only results graphically with both BMI and lipids standardized; no exact coefficient labels. Its BMI SDs for descriptive samples cannot be presumed to be model scaling constants.

[Soares et al. 2020](https://link.springer.com/article/10.1186/s12916-020-01648-0), Additional file 1, Table S7, pages 12–13, reports:

| Urban Malawi group | n | TC coefficient (95% CI) | HDL coefficient (95% CI) |
|---|---:|---:|---:|
| Female, 18–19 | 774 | 0.05 (0.00, 0.11) | −0.04 (−0.06, −0.02) |
| Male, 18–19 | 474 | 0.04 (−0.01, 0.10) | −0.02 (−0.04, 0.00) |
| Female, 40–60 | 1,487 | 0.15 (0.10, 0.20) | −0.05 (−0.06, −0.03) |
| Male, 43–70 | 790 | 0.20 (0.13, 0.27) | −0.05 (−0.08, −0.03) |

Units remain mmol/L per one SD of BMI. Adult adjustment matches the preceding list except HIV status replaces HIV/ART; the adolescent footnote omits medication. Missing covariates use chained-equation imputation separately by age and sex; adult HIV missingness is 9.2%. Household robust SE is used. The source SD reference population is unresolved. Figure S4 (page 21) is an age-only plot with both variables standardized. Table S9 has substantially different HDL numbers under the same printed units, requiring clarification; no silent scale correction is made. The main Results text labels one LDL table value as HDL. Verified table rows govern this extraction.

**Overlap:** the two Soares papers use the same MEIRU survey; the 2020 urban age subsets overlap the 2019 sample and Greiner 2021's Malawi component. Multiple papers, strata, outcomes, and adjustment variants are dependent evidence.

## Existing sources and missed information

[Agongo et al. 2018](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206326): original Tables 4–5 and S2–S3 contain additional multivariable BMI coefficients. The outcome is **log lipid**, with log base unspecified, and raw BMI is kg/m².

| Model | BMI coefficient (95% CI) | Locator |
|---|---:|---|
| Men, log HDL | 0.001 (−0.011, 0.013) | Table 4 |
| Women, log TC | −0.009 (−0.019, 0.001) | Table 5 |
| Men, log TC | 0.010 (0.001, 0.019) | Table 5 |
| Pooled, log HDL | −0.001 (−0.008, 0.007) | S2 Table |
| Pooled, log TC | 0.001 (−0.006, 0.007) | S3 Table |

The exact, different adjustment lists are in JSON. Pooled HDL and male TC omit age; female HDL has no BMI row. Participants were 40–60-year-old longstanding Navrongo residents; pregnant women and incomplete records were excluded. Fasting serum used direct Randox assays. Sampling weights are not explicitly described. Source methods give 864 men versus 846 in tables/abstract. The [correction](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0213233) changes waist/hip summaries and a reference, not these rows. S1 adds age–lipid Pearson correlations, but no complete BMI/age/sex/lipid covariance block. Published model explained variation cannot be combined with raw marginal SD to manufacture log residual SD.

[Kavishe et al. 2019](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0223189): adult Tanzania/Uganda survey, n=1,957, nonfasting serum Roche assays. Unlike descriptive summaries, regressions explicitly omit sampling weights. Table 4 gives HDL BMI-category differences relative to normal BMI: underweight 0.01 (−0.07, 0.09), overweight −0.06 (−0.12, 0.00), obese −0.15 (−0.21, −0.09) mmol/L. Age category, sex, and stratum are forced; other distal covariates are selected hierarchically. The complete final BMI design matrix is not supplied as a standalone formula. No TC regression or continuous BMI coefficient appears. S1 aggregate supplement contains diagnostic combinations only; the published dataset was intentionally not downloaded. Category differences do not determine a continuous slope.

[Zanzibar 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6615808/): n=470, ages 5–95, after fasting, complete measurement, and extreme-value exclusions. Tables 4–5 use binary BMI and binary outcomes with a household logistic random intercept. Table 4 high-BMI ORs are 1.13 (0.40, 3.19) for high TC and 1.21 (0.62, 2.37) for low HDL; jointly including waist/body-fat gives 1.31 (0.25, 6.79) and 1.35 (0.48, 3.76). Neither supplies a continuous slope. Table 5's title omits medication adjustment stated in methods. Listed reviewer/manuscript supplement download attempts returned 404, so those were not read. No scientific continuous-model supplement is listed in the approved XML.

[Obirikorang et al. 2015](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0129494): original Table 7 is **unadjusted Spearman**, not Pearson or age/sex-adjusted. Rural BMI–TC, BMI–HDL and TC–HDL are 0.212, −0.100, 0.106; urban values are 0.293, −0.040, 0.171. No CIs, pair-specific n, or rank/missingness convention are supplied. Household-selected participants with prior hypertension, diabetes, coronary disease or treatment were excluded, as were pregnant/lactating and disabled participants. Lipids used 12–14-hour fasting venous serum and Selectra Pro S enzymatic assays. The age/gender-adjusted logistic analysis concerns urban residence, not these correlations. No algebraic conversion to the requested OLS or residual Pearson statistic is justified.

## Identifiability and transport

- A one-SD BMI coefficient needs the source's exact standardization rule and constant for raw-unit conversion. Adjusted or cluster-robust CIs for means do not identify that SD.
- Separate sex-specific coefficients do not identify a pooled common slope without relevant within-stratum covariate cross-products and weights. Differently adjusted coefficients cannot be substituted for age/sex-only adjustment.
- Log outcomes need a specified log base and a conditional retransformation law to recover raw conditional means.
- Coefficient CIs quantify sampling uncertainty, not individual conditional spread. Robust and multiply-imputed SEs cannot be inverted as simple OLS residual variance.
- No TC–HDL conditional covariance or complete compatible covariance matrix emerged here. Marginal SDs, odds ratios, diagnostic combinations and rank correlations do not close that gap.
- All candidates concern measured assays. Population, age range, selection, fasting, laboratory and measurement transfer must be stated; these are not automatic latent-concentration constraints or causal effects.

## Search accounting and local artifacts

Two passes were completed: approved originals/supplements, then six targeted queries and one new reference follow-up (seven conservatively counted discovery requests, below eight). Ten web calls were used in total; their transport bytes were not metered. Eleven original source downloads total **1,789,624 bytes**. Failed/challenge responses and one unmeasured publisher HTML request are logged separately. Derivative text and PNG files are not counted as downloaded source bytes. No dataset, paid service, training or generator run was used.

`association_inventory.json` contains exact values, adjustment lists, selection/measurement fields, admission limits, and SHA-256 hashes. `SEARCH_ASSOCIATIONS.json` contains exact queries, primary URLs, screening reasons, accesses, failures and counts. Original files are in `source_bodies_associations/` and remain local. Stopping reflects information gaps and independently checked alternatives, not a selected coefficient direction or magnitude. This is a bounded audit, not an exhaustive systematic review.
