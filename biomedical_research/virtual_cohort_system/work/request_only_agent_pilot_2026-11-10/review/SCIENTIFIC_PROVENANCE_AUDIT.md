# Request-only pilot: static scientific provenance audit

Audit scope: all four terminal episodes, submitted model specifications and code, source text already returned by their tools, selected tables in their already downloaded XML, and diagnostic execution receipts. No new literature retrieval, author-code execution, patient-table inspection or clinical-reference input was used. The small source-covariance calculation below was independently recomputed from printed summaries; it did not call a generator.

## What actually completed

| Episode | API calls | Source queries / fetched full texts | Candidate versions / trials | Terminal result | Recorded tariff cost |
|---|---:|---:|---:|---|---:|
| PNS ordinary | 19 | 11 / 2 | 0 / 0 | Input-byte limit | $0.1830744 |
| PNS workflow | 20 | 12 / 2 | 0 / 0 | Input-byte limit | $0.1880455 |
| Lipid ordinary | 21 | 8 / 2 | 2 / 2 | Selected v002 | $0.2447480 |
| Lipid workflow | 18 | 3 / 3 | 2 / 2 | Selected v002 | $0.2508103 |

Total: 78 API calls, $0.8666782 estimated from recorded tariffs. The denominator is four requested episodes; only two delivered a selected generator. The four candidate versions represent two authors' attempts, not four independent scientific models. All API receipts report `gpt-6.1-sol`. Exact timestamps, returned-model IDs, token counts, tool usage and artifact hashes are in `TOOL_SOURCE_COST_AUDIT.json`.

The two PNS outcomes do not measure scientific data quality because no data generator was submitted. Their principal observed failure is the shared retrieval/context interface described in `RETRIEVAL_INTERFACE_REPAIR_PROPOSAL.md`.

## Revisions repaired execution, not the scientific model

Both authors passed a complete task/model object as the tool's `model_spec` argument. The tool then wrapped that object in its documented outer task/model structure. Their initial programs read only one `model` level and failed before producing data:

- Ordinary trial 1: `KeyError: age_beta`. Its v002 recursively unwraps the model nesting; all scientific constants and stochastic transformations remain the same. Minor rewriting of equivalent expressions is not a new fitted model.
- Workflow trial 1: `KeyError: ghana`. Its v002 embeds the same scientific constants in its program and removes dependence on metadata nesting. The companion specification is reorganized and more explicit, but the scientific values and distributions are unchanged.

Each second trial completed successfully at the predefined diagnostic seed. Each author then selected v002. These records demonstrate autonomous mechanical recovery. They do **not** demonstrate that generated-only statistical feedback improved a scientific relationship, because no scientific law was changed in either revision. No host wrote the scientific coefficients: the literals in the workflow program were authored by the API Agent.

## Ordinary lipid model: evidence-informed choices with an assumed dependence

The final program constructs an age/sex distribution and a three-component lifestyle mixture, draws positive BMI, then draws TC and HDL from correlated conditional lognormal laws.

| Model feature | Actual basis | Attribution and limitation |
|---|---|---|
| Regional TC/HDL levels | Kavishe et al., [PMC6897412](https://pmc.ncbi.nlm.nih.gov/articles/PMC6897412/), Table 2; rural and municipality weighted means | Literal values in the notes match the retrieved table. Generator intercepts and group offsets are selected approximations, not a replay of a weighted source population. |
| HDL female coefficient +0.08 mmol/L | Same paper, Table 4 | A reported adjusted coefficient is directly adopted; the generated adjustment set and target population differ. |
| HDL BMI slope −0.012 mmol/L per BMI unit | Source categorical HDL contrasts −0.06 and −0.15; Agent interpolation | Explicit assumption-dependent conversion from BMI categories to a continuous slope. Category means and a matching adjusted regression are not supplied. |
| TC BMI slope +0.05 mmol/L per BMI unit | Source LDL category differences and a retrieved Tanzania abstract reporting positive BMI–TC association | Cross-outcome extrapolation plus qualitative support, not a reported adjusted TC coefficient. The abstract is PMID 12656207 / DOI 10.3177/jnsv.48.352, exposed through `search_0006`; no full text was fetched. |
| Lean active component and dispersion context | Diarz et al., [PMC7263614](https://pmc.ncbi.nlm.nih.gov/articles/PMC7263614/), Table 2 | Retrieved BMI 21.9 (SD 3.9), TC 177.7 (SD 38.9) mg/dL and activity statistics match the notes. The model does not directly reproduce this sample or its SDs. |
| Conditional original-unit lipid correlation 0.35 | Agent assumption | The author explicitly states that no retrieved source identified the requested residual correlation. It is not a literature estimate. |
| Age distribution, 55% female, lifestyle weights, most age effects, group offsets and log-SDs | Agent assumptions | These define a fictional scenario and are not target-population estimates. |

The ordinary program correctly distinguishes original-unit conditional Pearson correlation from latent Gaussian correlation and applies the lognormal conversion. Its fixed log-SDs imply heteroscedastic original-unit SDs. A softplus mapping makes lipid conditional means positive; therefore the declared arithmetic linear slopes are not exact global slopes in the tails. Omitted lifestyle components correlate with BMI and affect both lipid levels, so age/sex-adjusted slopes and final OLS residual correlation are not identical to the structural coefficients or 0.35.

## Workflow lipid model: a genuine numerical use of joint external evidence

The workflow author independently located [Ofori and Angmorterh, PMC6658156](https://pmc.ncbi.nlm.nih.gov/articles/PMC6658156/), including Tables 1, 2 and 5. These contain pooled SDs, sex-specific means and a Pearson correlation matrix covering age, BMI, TC and HDL. Thus this episode found a usable **source-side joint summary**, rather than relying only on marginal distributions or assuming all residual dependence.

The SDs and six pairwise correlations used in the code match those tables. Differences between reported female and male means also match. The source has 120 students, including 100 women and 20 men according to Table 1; Table 2 labels its female column `n=120`, inconsistent with Table 1 and the total. The Agent used 100/120, but did not explicitly flag this source-table inconsistency. This should remain a source-quality caveat.

The calculation reconstructs the covariance between a binary female indicator and each measured variable from the sex mean difference and sample sex variance. It solves covariance normal equations and a Schur complement. Independent arithmetic from the stated rounded summaries gives:

| Derived source quantity | Independent calculation |
|---|---:|
| Age coefficient for TC, mmol/L per year | +0.000548616 |
| Age coefficient for HDL, mmol/L per year | −0.003086565 |
| BMI coefficient for TC, mmol/L per BMI unit | +0.035191146 |
| BMI coefficient for HDL, mmol/L per BMI unit | +0.001130608 |
| Corresponding TC structural slope, mg/dL per 5 BMI units | +6.804208 |
| Corresponding HDL structural slope, mg/dL per 5 BMI units | +0.218603 |
| Source-derived residual TC–HDL correlation | 0.186424424 |

The reconstructed residual covariance is positive definite. These are **derived source-summary quantities**, not reported fitted regression coefficients, not results from generated rows, and not clinical target values. Their interpretation assumes compatible pooled summaries from the same observations, rounded-summary consistency, linear projection and a source-to-target transfer of slopes/dependence. The source-derived sex coefficient and source residual SDs are not used directly.

The other ingredients are separately traceable:

| Model feature | Actual basis | Attribution and limitation |
|---|---|---|
| Sex-specific BMI and lipid baseline anchors | Unwin et al., [PMC2892446](https://pmc.ncbi.nlm.nih.gov/articles/PMC2892446/), Table 4 | Numerical anchors match the source. These are baseline observations among people retained in a migration follow-up analysis, with different denominators for BMI and lipid measurements. |
| Component differences in BMI, TC and HDL | Same table's reported 12-month changes | Values are reported; interpreting longitudinal differences as cross-sectional mixture offsets is an additional scenario assumption. They are not identified causal effects. |
| Conditional lipid SDs: TC 1.00/1.30 and HDL 0.30/0.38 mmol/L for men/women | Rounded-down values selected from source marginal SDs | Explicit approximations; source marginal SDs do not identify residual SDs. The amount removed as explained variation is not estimated. |
| 52% female and sex-specific age-band weights | Magodoro et al., [PMC6485175](https://pmc.ncbi.nlm.nih.gov/articles/PMC6485175/), Table 2 | Reported weighted demographic proportions match. The source's first band starts at 16, while the generated band starts at 18. The model's within-band ages and upper bound are assumed. |
| 30% transition component; BMI age slope +0.04 | Agent assumptions | Unidentified mixture and transport choices, not target estimates. |

The program analytically converts chosen conditional arithmetic means, SDs and Pearson correlation to row-specific bivariate lognormal parameters. This is more careful than equating latent and observed correlation. Nevertheless, the final requested residual correlation also contains unmodeled lifestyle effects, and the requested BMI projections contain lifestyle/BMI association. The source-derived 0.186424 correlation and the table above therefore must not be presented as exact predictions of final generated-data estimators.

Geography, student selection, fasting status, age extrapolation and differing source adjustment sets remain substantial applicability gaps. The fixed generator does not propagate paper-estimation or transport uncertainty across its random seeds. Positive lognormal outputs also do not enforce HDL ≤ TC; neither author claims to enforce that component constraint.

## Retrieval and information exposure

| Episode | Unique admitted PMCIDs | Literally exposed PMCIDs | Unique admitted titles | Complete title fields exposed | Returned metadata characters |
|---|---:|---:|---:|---:|---:|
| PNS ordinary | 26 | 8 | 35 | 10 | 131,601 |
| PNS workflow | 31 | 10 | 33 | 5 | 129,680 |
| Lipid ordinary | 21 | 7 | 29 | 6 | 110,000 |
| Lipid workflow | 12 | 5 | 12 | 4 | 41,917 |

These conservative literal-exposure counts describe the shared metadata interface, not comprehension. Some hits have no PMCID, repeat across queries or split their title fields across pages. The two successful authors used distinct external studies, with source IDs and hashes recorded. Gateway screening is a conservative exclusion check, not proof of cohort independence or clinical transferability.

## What this round supports

The two lipid episodes demonstrate an actual request-to-search-to-authored-model-to-execution path, including a model-authored repair of an interface error. One author autonomously retrieved and numerically combined joint evidence; the other transparently supplied assumptions where its evidence did not identify a relationship. This is useful evidence about capabilities and failure attribution.

It does not establish that the workflow policy is generally better, that feedback improved scientific data quality, that sources fully constrain the target distribution, or that the four episodes all completed. The scientific-quality comparison belongs to the separately frozen final evaluation; no target results were used in this audit. The next minimal engineering improvement is shared search-result presentation and unambiguous model-spec submission semantics, not host adjustment of coefficients.
