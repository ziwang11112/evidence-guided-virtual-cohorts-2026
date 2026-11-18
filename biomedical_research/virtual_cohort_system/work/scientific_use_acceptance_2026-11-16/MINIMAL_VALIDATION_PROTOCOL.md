# One bounded validation: matched-size analysis utility

Status: **design ready for implementation review; not executed**. 16 November 2026.

## Aim and scope

Use the existing lifestyle case to contextualize virtual–real analysis differences against finite-sample real–real differences under a common empirical sampling scheme. This is a diagnostic of the evaluation, not a new generator competition, independent cohort, clinical equivalence test or population-transport validation.

No Agent call, new source, new family, generator revision or new virtual cohort is allowed. Use the two existing authors and all six final tables. Keep the source-rich information regime explicit. The reference and its results have already been exposed; no prospective-confirmation claim follows from freezing this diagnostic now.

## Input and implementation freeze before any resampling output

Bind the existing PROTOCOL.md, analysis_operator.py, reference_adapter.py, final-table inventory, all six saved virtual CSVs and the real source file by SHA256. Respect the original adapter's expected source SHA256:

`7508097bd6578307a55aef793c15b4c26d2346e2d8e60e55ba8bf9d5254037f9`.

The exact paths must come from the closed experiment's inventory, not from a new filename search selecting convenient versions. Verify six final slots, authors A1/A2 and final seeds 64001, 64003, 64007. Read no API credentials. No third-party text or participant-level rows are to be copied into a public report.

Run a preflight on schema and eligibility only; verify counts of BMI 1,189, TC 400 and HDL 405. If these differ under the bound adapter, stop with the discrepancy rather than changing selection. The virtual tables have 1,226 complete rows. Preserve the original exclusion/positivity rules. Do not add outcome trimming or missingness imputation.

Use the frozen analysis operator. A thin wrapper may select the trait and extract its pooled raw-unit contrasts and sample SD. Bootstrap copies require fresh within-copy row IDs because the operator correctly rejects duplicate IDs; these are temporary row labels, not new people. Source and generated files stay unchanged. A fixture should verify that an unchanged input copy produces the original estimates and that raw-unit contrasts equal standardized contrasts times that table's SD. This is necessary wrapper verification, not a rerun of old test suites.

## Sampling scheme

1. For each trait, use the original positive, finite, adult, covariate-complete available-case pool. No common-complete lipid subset is substituted.
2. Define six strata from the recorded three lifestyle groups and sex. Fix the resample size in each stratum to that trait's observed reference count. This conditions on the available-case group/sex mix. Do not force age distributions, biomarker moments, slopes or correlations.
3. Predeclare 500 replicates and root RNG seed 16161. Use deterministic, independent child streams for each trait, replicate, dataset and side, with the stream map saved before execution. Do not generate more replicates to change a result.
4. In each replicate draw two independent, with-replacement samples R_A and R_B from the real empirical pool within strata. For each of the six saved virtual tables, draw S_k using the same stratum counts. “Independent” here means independent random draws conditional on the same empirical pool, not independent clinical cohorts.
5. Apply the same operator to every sample. For each pooled contrast calculate D_RR = estimate(R_A) − estimate(R_B) and D_SR,k = estimate(S_k) − estimate(R_B). Sharing R_B across virtual comparisons makes their reference perturbation comparable. Retain authors and original table seeds as separate identifiers.
6. Strata with zero reference count receive zero draws. A nonzero reference cell missing from a virtual table is an explicit unavailable slot. Singular fits, nonfinite values and operator failures remain recorded; no replacement samples or discarded outcomes.

This is participant resampling conditional on the stored group/sex cells. The current adapter does not retain household/site sampling identifiers. Consequently the output is an empirical stability diagnostic, not a cluster- or survey-design-valid population confidence interval. Any later design-based analysis needs verified design metadata and a separate protocol.

The diagnostic standardizes both sample size and the available-case group/sex mix. Therefore a change from the original unmatched comparison cannot be attributed to sample size alone. Keep the original unmatched estimates visible. Reference stratum counts are evaluation inputs only; they are never returned to an Agent or used to modify a delivered law.

## Estimands and outputs

Retain exactly the nine existing pooled contrasts: rural–pastoralist, urban–pastoralist and urban–rural, for BMI, TC and HDL. Raw units are primary: kg/m² and mg/dL. Preserve the original age/sex adjustment. Keep the three trait SDs as explanatory diagnostics; standardization can otherwise conceal scale mismatch. The existing sex-specific and interaction results remain in the original report; this bounded diagnostic does not open another interaction investigation.

For each contrast and every saved virtual table report:

- the original reference and virtual point estimates;
- the empirical median, signed mean, and 2.5%, 25%, 75%, 97.5% quantiles of D_RR and D_SR,k;
- the corresponding absolute-difference summaries;
- successful and failed fit counts, sampling-cell availability, and raw-unit SD diagnostics.

Use NumPy's linear empirical quantile convention and record package versions. Keep all table-level outputs; any author-level display must show all three original seeds, not pick the best one. Do not rank or retrain generators from these results.

No “percent inside the reference CI”, pass-rate threshold, significance-agreement score or clinical equivalence label is primary. The empirical envelopes show sampling context. They are not acceptance margins, new clinical evidence or a confidence interval covering source/model/transport uncertainty. Five hundred resamples and three table seeds do not increase the number of Agent constructions or case families.

## Review and resource bounds

After freezing the wrapper and stream map, verify representative resampled fits independently by a second formula/implementation; check that raw-unit estimates are unaffected by the operator's within-table z-scaling. Audit the complete result inventory and all failures. Root-authored numerical recomputation must be labeled as such, not called an external expert review.

At most 500 replicates × 3 traits × (2 reference samples + 6 saved virtual tables) = 12,000 trait-sample evaluations. Only extracted aggregate estimates/diagnostics are saved. Temporary resample rows remain in memory. Set a one-hour wall-clock cap and stop at a saved partial inventory if exceeded; do not silently lower the replicate count or expand resources. No paid API budget, training, HPC, new download or new source search is required.

## Decision after this one diagnostic

- If the BMI pattern and effect scale remain useful while lipid discrepancies persist, retain the specific BMI use claim and lipid limitation. Do not repair the laws using this exposed reference.
- If a precision/significance discrepancy is explained mainly by unmatched sample counts, correct that comparison and report the matched-size analysis.
- If a scientific use requires an equivalence claim, obtain a separately justified raw-unit margin and an adequate uncertainty model. This diagnostic cannot supply either by itself.
- Only a planned stronger claim about new-population generalization warrants a future independent target. Do not automatically start it after this diagnostic.

Close with a full nine-contrast result and a continue/limit/stop decision. No additional condition, model family or dataset is authorized by this protocol.
