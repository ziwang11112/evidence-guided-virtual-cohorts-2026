# Independent method review before lifestyle generation

Scope: protocol design only. No participant records, new target effects, API calls, or new synthetic data were inspected or executed by this reviewer.

## Verified source operator

The [original Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC7577730/) (Data filtering; Testing for lifestyle effects, equations 1–2) standardize biomarker outcomes by mean and SD. The additive model uses three lifestyle categories, age in years, and sex. A likelihood-ratio comparison adds lifestyle-by-sex interaction, with sex-specific models following a nominal p<.05 result. The stated multiple-testing family covers ten biomarkers plus a composite outcome. Recruitment is strictly above age 18. The original outlier, pregnancy, and interview exclusions cannot all be reconstructed from current released columns.

## Decisions the protocol must resolve

1. **Define the scale denominator.** Standardizing each outcome among all eligible observed rows before regression deletion is not identical to standardizing after that outcome's complete-case selection. The source prose does not fully resolve the ordering. Choose and record it; apply it identically to real and virtual tables. Do not call it exact author-code reproduction. If sex-stratified fits are added, explicitly state whether pooled outcome scaling is retained; silently rescaling within sex changes the estimand.
2. **Keep categorical lifestyle categorical.** Three groups require two indicators, not an ordinal numeric lifestyle score. Freeze the reference group and report both contrasts for all three outcomes. Preserve age in years; standardizing predictors would alter coefficient interpretation.
3. **Specify model branching before results.** A fixed primary additive model with a separate interaction diagnostic is an explicit partial replay. Following the source's conditional interaction branch instead requires predefined output slots, sample selection, and failure handling; do not choose favorable branches after evaluation.
4. **Do not equate a new q-value family with the original one.** A six-contrast or three-outcome correction is a different declared family. Report it as such, or omit inferential success classifications. Any group comparison absent from the original reference coding is a separate linear contrast and must be identified.
5. **Virtual sample size is not evidence size.** A generator can create arbitrarily many rows, changing coefficient standard errors and p-values without increasing empirical support. Effect-size patterns and explicitly conditional simulation variability are suitable primary comparisons here. If inferential output is retained as an application demonstration, label its model-conditional nature; it is not validation of clinical precision.
6. **Separate direct source reconstruction from empirical reuse.** If original published estimates are available to the Agent, their reproduction is an intended source-use check. Applying the frozen model to the already exposed real deposit is a developmental application comparison, not independent confirmation. The Agent should never receive the new real-data fit during construction/revision.
7. **Keep the bounded generation task honest.** Age, sex, lifestyle, BMI, TC and HDL must all be produced by the Agent-selected scientific law. Old latent lifestyle components must not be relabeled as validated categories. Source-provided numerical inputs are allowed; the reviewer/root must not manually prescribe target numerical coefficients or expected signs.

## Preflight acceptance criteria

- The two fresh authors, permitted feedback revision, all final seeds, and failure slots are fixed before launch; retained candidates remain valid outcomes.
- Evidence versions, prompts, tool calls, model identity, cost, candidate code, final selection and draw receipts are preserved. Neither clinical target fits nor previous evaluation answers enter the Agent's context.
- The evaluator has an independently checked categorical design and scaling convention; tests include reference-level contrasts, interaction degrees of freedom, degeneracy, missingness, strict age threshold, and unit invariance where appropriate.
- Reports retain all three outcomes and every frozen lifestyle contrast for every successful final construction. A large virtual n or a statistically significant generated association is never a standalone quality success criterion.
- Clinical consistency and mathematical checks are diagnostic tools. Their success does not certify publication extraction accuracy, source transport, or population truth.

This preliminary review is not launch approval. Final code, evidence and protocol hashes must be reviewed and frozen first.

## Root's subsequent bounded clarification

The planned table now has all three pairwise lifestyle contrasts for each of the three biomarkers (nine additive results), plus all three contrasts for each sex (18 sex-specific results). The latter remain visible whether or not the interaction branch is selected. The added rural-versus-urban contrast must use a linear combination of coefficients and their full covariance, not a difference of standard errors. A nine-additive-comparison BH correction is explicitly an exploratory subset family; sex-specific outputs retain nominal p-values without claiming post-selection FDR control.

The cohort-generation task uses 1226 rows from the published recruitment total, with missing biomarker values allowed, and TC/HDL in mg/dL. Actual per-outcome usable sample counts must still be reported. The documented disagreement between the main table's group-count total and the narrative recruitment total remains a source inconsistency for the Agent to explain, not permission to inspect target rows or hand-adjust proportions.

**Final-protocol supersession:** The preceding preliminary allowance for generated missing biomarkers was withdrawn before launch. The final protocol and task require all seven generated fields to be complete, consistent with the unchanged output contract. The real reference retains trait-specific available cases. The full preflight review binds this final specification and treats the unequal measurement completeness and effective sample sizes as explicit interpretation limits.
