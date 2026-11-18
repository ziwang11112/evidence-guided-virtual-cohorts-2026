# Matched-size scientific-use comparison

17 November 2026 · KDD Paper 1 · Completed existing-data evaluation

## Finding and decision

The strongest supported use in this case is reproducing the positive, age/sex-adjusted urban BMI contrasts at an approximately useful effect scale. Matching sample size and lifestyle-by-sex composition also places several urban lipid comparisons on a discrepancy scale similar to real–real sampling variation. This improves the interpretation of existing data quality; it does not improve the frozen generators themselves.

Two problems remain visible across the six saved tables: the rural–pastoralist lipid effects are too small, and both lipid distributions are underdispersed. Similar group contrasts therefore do not establish adequate individual variability. Close the planned P0 diagnostic with an analysis-specific use profile, retaining every prespecified contrast and diagnostic. No additional sampling, parameter change or new cohort is needed for this unit.

## What was compared

This is the source-rich Turkana lifestyle application already evaluated on 11 November, not a new target. Two independent Agent constructions supplied three saved seeded tables each (six tables, 1,226 complete rows per table). The measured reference has trait-specific available-case counts of 1,189 for BMI, 400 for total cholesterol, and 405 for HDL after the frozen adult/availability rule.

Each of 500 repetitions draws two independent real resamples and one resample from each saved virtual table, with replacement within six lifestyle-by-sex strata. For a given trait, all eight resamples have exactly the real available-case sample size and stratum counts. The virtual comparisons share the repetition's real B reference. Age and outcome distributions are not forced to match. These are independently drawn resamples of the same empirical real pool, not two independently recruited cohorts.

The original frozen analysis operator is used unchanged: age/sex-adjusted lifestyle comparisons from OLS. Its outcome-standardized coefficients are converted back to raw units using the same sample's SD. All nine pooled contrasts are reported. Standard deviations are necessary companion diagnostics. Original unmatched point estimates are retained in the complete CSV and HTML.

## Main results

For the urban–pastoralist BMI contrast, the six matched-resample mean effects are 1.649 to 2.262 kg/m², compared with 1.896 in real B resamples (original measured estimate 1.882). The real–real mean absolute discrepancy is 0.316 kg/m²; the six virtual–real values range from 0.314 to 0.428. This supports using these virtual cohorts to prototype and reproduce the principal urban BMI group comparison, with uncertainty about precision and other uses.

Total-cholesterol urban–pastoralist mean absolute discrepancies are 8.556–9.479 mg/dL, compared with 8.848 mg/dL for real–real. That is a materially less pessimistic assessment than judging the original point estimates alone. However, rural–pastoralist total-cholesterol effects remain lower by 7.800–9.545 mg/dL on average, and HDL effects by 4.074–6.208 mg/dL. Weak urban HDL comparisons are particularly uncertain: overlapping sampling ranges cannot establish the correct direction or equivalence.

The table below includes all nine contrasts. Ranges across virtual tables are descriptive, not independent-model confidence intervals. BMI uses kg/m²; both cholesterol outcomes use mg/dL. A signed difference is the first sample's adjusted contrast minus real B's adjusted contrast. The real–real range is an empirical sampling reference, not a pass threshold.

| Outcome | Adjusted contrast | Original real effect | Real–real 95% difference range | Virtual–real mean signed difference (six-table range) | Real–real mean absolute difference | Virtual–real mean absolute difference (six-table range) |
|---|---|---|---|---|---|---|
| BMI | Rural − pastoralist | 0.242 | -0.422 to 0.442 | -0.362 to 0.147 | 0.184 | 0.185 to 0.380 |
| BMI | Urban − pastoralist | 1.882 | -0.771 to 0.771 | -0.246 to 0.367 | 0.316 | 0.314 to 0.428 |
| BMI | Urban − rural | 1.640 | -0.755 to 0.751 | 0.008 to 0.472 | 0.291 | 0.277 to 0.497 |
| Total cholesterol | Rural − pastoralist | 9.493 | -11.404 to 10.672 | -9.545 to -7.800 | 4.543 | 8.118 to 9.695 |
| Total cholesterol | Urban − pastoralist | 20.342 | -22.061 to 19.899 | -6.158 to -2.085 | 8.848 | 8.556 to 9.479 |
| Total cholesterol | Urban − rural | 10.849 | -21.364 to 20.380 | 2.953 to 6.359 | 8.743 | 8.110 to 10.365 |
| HDL cholesterol | Rural − pastoralist | 4.446 | -5.718 to 5.721 | -6.208 to -4.074 | 2.363 | 4.195 to 6.242 |
| HDL cholesterol | Urban − pastoralist | 1.750 | -10.964 to 10.778 | -3.592 to -1.053 | 4.375 | 3.807 to 4.818 |
| HDL cholesterol | Urban − rural | -2.696 | -10.097 to 10.138 | 1.971 to 3.942 | 4.362 | 4.029 to 4.851 |

## Dispersion and the scope of scientific use

| Outcome | Original real SD | Mean real-resample SD | Real-resample SD 95% range | Mean virtual-resample SD (six-table range) | Outer endpoints of six virtual SD 95% ranges |
|---|---|---|---|---|---|
| BMI | 2.827 | 2.829 | 2.631 to 3.040 | 2.417 to 2.704 | 2.309 to 2.830 |
| Total cholesterol | 42.811 | 42.784 | 39.262 to 46.287 | 31.486 to 32.674 | 28.909 to 36.376 |
| HDL cholesterol | 20.228 | 20.194 | 18.788 to 21.392 | 14.496 to 14.889 | 13.366 to 16.698 |

For total cholesterol and HDL, even the largest upper endpoint of the six virtual-resample SD ranges is below the real-resample lower endpoint. Their shortfall therefore remains clear under this matched analysis. The last table column reports outer endpoints across six separate ranges, not a pooled interval.

| Intended analysis or use | What this unit supports |
|---|---|
| Age/sex-adjusted urban BMI group comparisons | Useful source-rich reconstruction/prototyping of the positive contrasts and approximate effect scale. |
| Urban total-cholesterol comparisons | Sampling-context agreement is encouraging, but small real urban groups and narrow virtual dispersion limit the inference. |
| Rural–pastoralist lipid comparisons | Not adequately reproduced: effects remain systematically too small in these saved tables. |
| Weak urban HDL contrasts | Uncertain; wide real–real variation is not evidence that the generated direction is correct. |
| Individual heterogeneity, variance-dependent precision or power calculations | Current lipid tables are insufficiently dispersed; these uses are not established. |
| Clinical equivalence, individual recovery or new-population transport | Not tested by this same-pool, source-rich diagnostic. |

The measured urban lipid groups contain only 37 participants for total cholesterol and 38 for HDL. Their wider real–real ranges make some urban discrepancies less distinguishable, but do not erase consistently weak rural effects. An underdispersed generator may also look favorable on an effect-only discrepancy, which is why the SD panel accompanies the contrast panel.

## Implementation and audit

- The scientific plan predates this run; the implementation, approved input bindings, invented-fixture checks and complete random-stream map were frozen before resampling. All 28 bound files remained unchanged.
- All 12,000 planned trait-sample evaluations completed: 3,000 real-resample fits and 9,000 virtual-resample fits. There were zero unavailable/failed slots and no replacement runs. Runtime for this execution was 130.125 seconds, excluding setup, rendering and review.
- The six wrapper tests passed before freezing. They cover units, immutability, cell matching, reproducibility, eligibility, non-computable fits and duplicate identifiers. They were not repeated after success.
- A separately implemented raw-outcome, centered-age QR regression reproduced 21 original trait fits and 72 preselected resampled fits. Across 372 checked numerical fields, the maximum discrepancy was 4.05e-13. This is an independent formula check by the root agent, not external statistical review.
- All 31,500 contrast differences and 900 aggregate summary fields were independently checked. All 28 v0.33 delivery files remained unchanged.
- No new Agent/API calls, downloads, generated cohorts or participant-level resample files were created. New API cost was $0. The 12,000 evaluations are computational repetitions, not 12,000 independent studies; evidence still comes from two constructions and one real study family.

## Interpretation limits

The empirical reference is an observed sample, not known population truth. The conditional bootstrap conditions on available cases, lifestyle/sex counts and the bound empirical pools. It omits household/site clustering, source-study estimation uncertainty, population transport and missingness uncertainty. Its central 95% ranges are neither cluster/survey-valid population intervals nor clinically meaningful equivalence margins. Sample size and composition were matched together, so changes from the unmatched result cannot be attributed solely to sample size. No tolerance or pass rate was selected after looking at the results.

This same-paper, previously exposed setting establishes a reconstruction use profile; it does not reset target exposure. Two authors with three saved seeds each do not provide six independent modeling decisions. Matching to the observed target composition is an evaluation standardization, not part of a newly blind generation protocol.

## Contribution to the KDD paper

Use this as evidence that generated-cohort usefulness must be evaluated through the requested scientific analyses and real sampling variation, with dispersion checked alongside effects. The positive result is a concrete use of final virtual data, not a new claim that feedback, more agents or this workflow outperform alternatives. The full nine-analysis profile belongs in the paper/supplement together; the urban BMI example can lead the narrative without suppressing the lipid limitations.

The planned next priority remains P1: verify original-paper-to-model capability on existing cases under the KDD-first plan. This unit launches no such experiment and makes no generator change. The supplied manuscript insertion is ready for the next reading edition; v0.33 is intact.

## Files

- [Offline visual report](report/index.html)
- [All nine scientific contrasts](figures/matched_scientific_contrasts.pdf) and [dispersion diagnostic](figures/matched_dispersion.pdf)
- [Manuscript insertion and figure captions](MANUSCRIPT_INSERT.md)
- [Complete contrast summaries](CONTRAST_SUMMARIES.csv) and [SD summaries](SD_SUMMARIES.csv)
- [Frozen protocol](PROTOCOL.md), [execution receipt](RUN_RESULT.json), [independent numerical review](INDEPENDENT_REVIEW.json)

Only aggregate estimates and original documentation appear in this report. Participant-level source and virtual tables remain in their existing local locations.
