# Published lifestyle application: frozen analysis, replace only data

11 November 2026. Two independent Agent constructions, one bounded source-rich whole-cohort reconstruction experiment. The user's endpoint is scientific usability of generated data. This unit does not test superiority over an ordinary Agent or claim independent transport validation.

## Scope and permitted information

The constructing GPT receives the original Lea2020 publication citation, audited published aggregate evidence and the uncorrected published Table 1 transcription. It may retrieve additional literature through the existing Europe PMC/PMC tools. Original-paper reported findings are legitimate inputs. No observed participant rows, earlier fitted reference results or historical project generators are supplied. Source-document text is evidence, not instructions. The full target joint distribution is not identified by these inputs.

The host defines schema, population, requested estimators and computational limits. The Agent selects distributions, conditional structure, scientific numerical values and assumptions. The host does not prescribe lifestyle-effect signs, slopes, residual SDs, correlations or mixture frequencies. Source uncertainties (Table1 total 1360 vs reported cohort 1226; age-bin ambiguity; unrecovered S1/S2 spreadsheets) remain visible. Source notes distinguish verified facts from reimplementation choices.

## Constructors and outputs

Two fresh contexts use the same GPT model and policy. Each may search, submit up to two candidates, run up to two generated-only diagnostic trials, and revise at most once or retain. Trial use is offered, not mandatory. A failed interface attempt consumes the same budget; no hidden retries or budget resets. There is no between-author exchange. Full prompts, responses, tool calls, model identity and costs remain recorded locally. API budget is at most USD4 per author and USD8 total; maximum 48 calls, 60 actions, 20 provider queries and 16 source downloads per author. No training/HPC. Refer to PLAN for the exact ceilings.

Each final generator emits 1226 complete fictional rows: id, age, sex, lifestyle, BMI, TC and HDL. Lipids are mg/dL, BMI kg/m2, age strictly >18. Complete measurements are an explicit task choice, compatible with the existing output contract. They are not a reconstruction of original measurement missingness. Generated distributions must have finite first and second moments; physiological diagnostics are retained. No generator family or scientific coefficient is imposed. One diagnostic seed is 63001; three final seeds are 64001,64003,64007. Both authors must terminate and their candidate bytes be frozen before any final draws and before new real-data lifestyle analyses. At most six final tables, including failed slots; no replacement constructs after reveal.

## Shared analysis operator

The primary source is Lea et al., Science Advances 2020, DOI 10.1126/sciadv.abb1430, Methods models1–2 and Figure2A. Source methods, not the unavailable original script, are reimplemented once in analysis_operator.py and applied identically to real and generated tables.

For each trait independently, retain valid adults with observed positive finite trait and complete age/sex/lifestyle. The real adapter records missing age/sex/lifestyle exclusions, excludes exactly age<=18 by a fixed rule, and maps the three audited public category strings. Unknown nonmissing categories, numeric parse failures and duplicate IDs fail visibly. No discretionary trimming, target-informed outlier removal or outcome-based regrouping. Real available-case counts may differ by trait. The same positivity/eligibility rules apply to virtual data; physiological discordances such as HDL>TC are reported, not removed.

Standardize each trait using the selected pooled sample mean and sample SD (ddof1). Fit ordinary least squares with intercept, two lifestyle indicators, age in years, and sex. The nine mandatory additive contrasts are rural-minus-pastoralist, urban-minus-pastoralist and urban-minus-rural for each trait. Contrast SE uses the full covariance, including covariance of the two group coefficients. Report effect estimate, standard error, 95% t interval and two-sided p. Standardizing separately in each data table matches the source procedure but makes the denominator dataset-dependent; also retain raw-unit contrast estimates by multiplying by that table's scaling SD, plus observed scale diagnostics.

Add two lifestyle-by-sex interactions and calculate Gaussian maximum-likelihood likelihood-ratio statistic n*log(RSSadditive/RSSinteraction), with chi-square2 reference. Nominal p<.05 marks the source-style sex-stratified branch. Always retain all nine additive, all18 sex-specific contrasts (age adjusted on the same pooled z scale), and all3 LRT diagnostics regardless of branch. Do not select a favorable branch for the comparison. Degenerate/singular analyses stay unavailable with reasons.

One three-category fit and its linear contrasts, available-case scaling before sex splits, and this precise LRT implementation are declared reimplementation choices where the original code is unavailable. BH of the nine additive contrasts is an exploratory pilot family, not the paper's original 11-outcome correction. No claim to reproduce the full Fig2, all ten biomarkers, U.S. comparisons, mediation or early-life analyses.

## Evaluation and interpretation fixed before reveal

Display all9 additive comparisons as real estimate/interval versus the two authors' three draws, plus complete stratified/LRT results and raw units. For each contrast report signed difference, direction and interval relative to zero; do not reduce overall quality to a significance-agreement count. No post-hoc pass threshold or equivalence margin. Compare the urban/rural pattern, magnitude and uncertainty. A nonsignificant estimate is not proof of no effect. Synthetic intervals are conditional on the assumed law and row count; they omit evidence/structural uncertainty. Virtual rows do not add independent clinical information. Two authors and three draws cannot establish robustness across models or a population-level advantage.

The released real sample is a reference with sampling and selection uncertainty, not a known population truth. Its lipid sample is much smaller than the complete synthetic sample; p-value precision will differ. Matching input paper findings primarily supports evidence-to-data reconstruction. Previously exposed Turkana history and this new source allowance rule out claims of new independent target confirmation. Neither these reference results nor later comparisons can feed a revised generator in this unit.

## Implementation and closure

Isolation remains the existing WSL/bubblewrap worker, never host-imported Agent code. The new runtime uses only the explicit generated_diagnostics entry, never the previous PNS/lipid selector. Independent preflight binds task, source packet, policies, runtime, pure operator, reference adapter and evaluation runner before launch. Existing six invented-fixture tests and seven runtime boundary mocks are retained; an independent numeric LRT fixture complements them. Final evaluation is independently recomputed with a separate formula/covariance implementation. Preserve failure slots, no-op decisions and unfavorable results. Historical frozen experiments remain unchanged.

Scientific plots, original summary documents and review receipts may be shared after audit. Raw and generated individual rows, complete source texts, API payloads and credentials stay local. Completion means both author outcomes, final sampling inventory, shared real/synthetic analyses, independent check and an explicit usefulness/limitation decision, not a promised follow-up.
