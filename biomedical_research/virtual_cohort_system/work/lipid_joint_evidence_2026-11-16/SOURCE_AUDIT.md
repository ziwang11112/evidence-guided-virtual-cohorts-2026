# Lipid source admission audit

16 November 2026. Root audit of all seven original XML articles retrieved by the actual research Agent. No target reference values were parsed in this unit. Source selection was based on the predeclared missing paired/conditional relationship, not a desired target number.

## Decision

**Do not admit a generation experiment in this unit.** The search did retrieve partial relationship information, but the Agent did not complete an admissible evidence report. The available numerical constraints also have unresolved operator, row-commonality, reporting or population limitations. A same-source marginal-versus-joint experiment is therefore not frozen and the planned nine constructor calls are not launched.

This is a bounded **source-admission and execution closeout**, not a negative generated-data result, proof that joint evidence is unavailable, or an exhaustive literature review. It is also not a requirement that every useful source exactly match the target operator. Partial constraints can be useful, as demonstrated by the completed PNS experiment. Here their qualifications must be resolved and documented before a fair increment experiment can proceed.

## Original-paper checks

| Original study | What is present | What prevents treating it as the requested constraint |
|---|---|---|
| [Brombo et al., TRAIL, DOI 10.1371/journal.pone.0058225](https://pmc.ncbi.nlm.nih.gov/articles/PMC3589335/) | 199 first-visit Italian metabolic outpatients; Table 5 lipid/metabolic correlations; fasting enzymatic assays | Table 5 lacks TC and BMI. LDL is calculated, and some variables were log-transformed. The available incomplete moment block cannot simply be rearranged into raw TC–HDL residual covariance. |
| [Shidfar et al., postmenopausal women, DOI 10.5830/CVJA-2012-038](https://pmc.ncbi.nlm.nih.gov/articles/PMC3721927/) | Table 1 TC/HDL means and SDs; Table 2 raw Pearson TC–HDL 0.15 | Women-only selected clinic sample; age correlations absent. Enrolled n=165 versus table subgroup counts totaling 150; BMI eligibility conflicts with a reported maximum. Preserve these ambiguities rather than treating the raw pair as age/sex/BMI adjusted. |
| [Phenotypic, genetic, and genome-wide structure, DOI 10.1186/1471-2156-4-S1-S95](https://pmc.ncbi.nlm.nih.gov/articles/PMC1866536/) | Framingham variance-component estimates; Table 2 phenotypic TC–HDL correlation 0.12 | Different covariates and family model; upper triangle is genomic, not a confidence interval for the lower triangle. Environmental correlation 0.27 is not an ordinary OLS residual correlation. Suitable unconditional mean/SD increments are absent. |
| [Exploring Multifactorial Relationships, DOI 10.7759/cureus.59934](https://pmc.ncbi.nlm.nih.gov/articles/PMC11162279/) | Raw Pearson block for TC, HDL, age and BMI | Sex absent; N row blank; narrative column labels conflict with the table, including references to LDL where no LDL column appears. No corresponding marginal-SD table. Do not infer a sample size from p-values. |
| [Nigerians with hypertension, DOI 10.4314/mmj.v31i3.5](https://pmc.ncbi.nlm.nih.gov/articles/PMC6895384/) | Lipid versus age/adiposity/BP correlations; sex-stratified lipid means/SDs | Table 5 has no TC–HDL cell. Sex-stratified summaries encode a relationship and cannot be labeled purely univariate additions. Hypertension selection and incomplete paired moments remain. |
| [Dyslipidemia and cerebral alterations, DOI 10.1002/oby.20332](https://pmc.ncbi.nlm.nih.gov/articles/PMC3695042/) | Age/sex-adjusted BMI/lipid and cerebral-metabolite analyses in 64 selected middle-aged adults | Relevant tables have HDL, LDL and triglycerides, but no TC. They do not supply the requested paired covariance. |
| [Cotrimoxazole and lipids, DOI 10.1186/s12944-025-02722-3](https://pmc.ncbi.nlm.nih.gov/articles/PMC12487471/) | Table 2 pooled TC, HDL and non-HDL SDs; non-HDL explicitly defined as TC−HDL | Potential **rounded raw** covariance information. Header N=395 versus threshold rows n=390 leaves common-row handling unresolved. HIV/ART-selected population and absent covariate cross-moments do not identify target adjusted dependence. |

Source populations, assays, transformations and uncertainty are also recorded in `audit/ORIGINAL_SOURCE_AUDIT.json`, with exact downloaded XML hashes and bytes. None of these seven reports was identified as Turkana-derived. This is not a registry-level guarantee of every possible participant overlap. They are not counted as independent confirmations of a common parameter because their operators and populations differ.

## Useful partial lead, with its limits

The Ugandan report supplies TC SD 1.0, HDL SD 0.5 and non-HDL SD 1.0 mmol/L to one decimal place. **If** these are the same individuals, same scale and same variance convention, then

`Cov(TC, HDL) = [Var(TC) + Var(HDL) − Var(TC−HDL)] / 2`.

Using the displayed rounded numbers gives covariance 0.125 (mmol/L)² and raw Pearson correlation 0.25. These are conditional algebraic implications, not new measured estimates or proposed target parameters. Allowing each displayed SD its nearest-tenth rounding range gives a raw correlation envelope approximately 0.0029–0.4351, conditional on the same-row premise. This envelope is not a sampling confidence interval. It does not account for uncertain population transfer or adjustment for age, sex and BMI.

This also exposes an information-control issue: non-HDL SD cannot be included in a marginal-only addition along with TC and HDL SDs, because their identity already encodes covariance. Other component-completing information requires the same audit. Simply deleting a published correlation cell would not guarantee a valid marginal-only control.

## Implementation boundary

The research Agent selected and retrieved the sources. The root read original methods/tables and documented the audit above; the numerical source algebra is a root source check, not an Agent-selected target model. No new generative law, target parameter, synthetic row, or clinical estimate was produced. The report does not claim autonomous successful source admission or source-feedback improvement.
