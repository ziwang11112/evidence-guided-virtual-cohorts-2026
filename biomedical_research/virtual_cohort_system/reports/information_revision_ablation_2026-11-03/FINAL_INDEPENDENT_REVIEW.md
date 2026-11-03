# Independent closed-experiment review

Date: 2026-11-03. Unit: information provision × additional revision, CHNS development case.

**Disposition: numerical results are reproducible and the bounded experiment can close. The evidence supports reference-conditioned construction feasibility, limited external-literature transfer on this case, and no observed benefit from the additional revision stage.** It does not establish independent clinical validity, recovery of the joint population distribution, or superiority to equally informed statistical synthesis.

## Actual work and independent numerical checks

The reviewer waited for all six final decisions and handbacks before opening generated tables or the aggregate reference. No scientific generator was run, no new cohort was produced and no original patient record was read by the reviewer. Six author contexts produced 42 successful 3,000-row executions: six initial trials and 36 delivery executions; no failed attempt is present in the retained ledgers. There were 24 distinct output hashes overall and 18 distinct delivery hashes.

`INDEPENDENT_RECOMPUTE.py` separately parsed every generated CSV using the standard library. It used standard-library means, sample SDs and explicit linear quantiles; SciPy Pearson/Spearman calculations; and centered, pivoted-QR least squares rather than the provider's uncentered NumPy SVD implementation. It did not call the experiment's statistics function or common evaluator.

All **1,260 statistic values** (42 × 30) were independently recomputed. Across **8,949 numerical, hash, ledger, coverage, summary and paired-change comparisons**, there were zero mismatches; the largest numeric difference was **7.11 × 10⁻¹⁵**. The audit verified all three regression definitions, all 27 diagnostics, reference values and coefficient intervals, differences, stage summaries, seed pairs, duplicate counts and failed-attempt accounting. Complete results are in `INDEPENDENT_RECOMPUTE.json`.

Output support, finite values and identifier checks passed for these realized tables. This is distinct from a claim that biological tails or all possible downstream analyses are realistic.

## Retention and actual revision effect

All six authors declared retention. Independent hashes confirm that both `generator.py` and `model_spec.json` are byte-identical between initial and final delivery for each author. All **18 same-seed final tables** are byte-identical to their paired initial tables. Every additional-stage contrast is therefore exactly zero; the apparent number of delivery executions must not be presented as 36 distinct cohort realizations or additional independent evidence.

Initial construction already included one trial per author, and R authors performed deterministic fitting to supplied summaries. The experiment therefore shows no effect of this **additional optional revision stage**. It does not test absence of all feedback, and it does not prove that revision can never help. Earlier experiments are not pooled here.

## Information, source and execution boundaries

- The six declared author IDs are distinct and follow the planned launch order. Retained session notes and `AUTHOR_DISPATCH_PROVENANCE.json` record fresh contexts (`fork_turns: none`) with no model/reasoning override. That provenance file is the coordinator's transcription of tool calls, not an independent OS access attestation. Exact provider snapshot, tokens and cost are not returned by the tool.
- Ledgers show one initial trial and three initial plus three final delivery attempts per author. There are no additional revision trials, no recorded retrieval queries or new documents, and no quota reset. All delivery and trial seeds satisfy the declared policy. Hash chains, bound code/profile files and snapshots match.
- L analysis feedback contains only permitted generated statistics and shared quality diagnostics. No unexpected analysis-reference fields were found in its delivery feedback. R receives the explicitly admitted 30 reference statistics. Ordinary retrieval was permitted but was not used in these six retained records; this experiment therefore does not demonstrate an active evidence-acquisition loop.
- External source-population numerical replay remains unavailable in every delivery feedback. L has an unavailable contextual check. R additionally has 30 numeric checks for its explicitly supplied CHNS reference. `matched_declared` identifies compatible declared statistical semantics; it does **not** mean that a numerical estimate met an acceptance threshold or that biological transfer was validated.
- The three R derivation producers use supplied aggregate summaries, analytic moments/CDF equations, quadrature and optimization. Retained producer code separates those calculations from row generation. The six inspected generators create their requested output arrays inside `generate` and contain no patient-file/network access or hidden fitting loops. This scoped code inspection and the retained ledger cannot certify every unlogged action available through an author's general tools.
- Generator/specification contents are retained under the assigned author candidates with explicit source/derivation/assumption provenance. Mechanical attachment preserves their hashes and installs predeclared statistical checks. This is consistent with author-owned scientific construction; it is not a cryptographic attestation of who typed every constant. No source extraction or applicability claim was newly authenticated by this numerical audit.

## Scoped mathematical support review

| Construction | Inspected support/moment argument | Remaining qualification |
| --- | --- | --- |
| L01 | Bounded age/sex; positive conditional lognormal BMI; `tanh` bounds BMI effects inside biomarker exponentials; positive lognormal cores plus nonnegative gamma increments. Positive-order polynomial moments exist. | Saturation, subgroup probability and gamma-tail structure are assumptions. |
| L02 | BMI has a bounded positive conditional mean, independently minimized at 23.1125. Biomarker means are affine increasing functions of positive BMI with lower bounds 3.687 for glucose and 5.0965 for HbA1c. Multiplication by finite-moment lognormal errors preserves positivity and finite polynomial moments. | These bounds establish mathematical admissibility, not calibrated biology or subgroup effects. |
| L03 | Biomarker log-values depend on log-BMI, bounded demographics and Gaussian errors; bounded mixture selection is dominated by a finite sum of finite-moment lognormal terms. | Unobserved mixture/tail dependence remains assumption-dependent. |
| R01 | Finite Gaussian/lognormal mixtures; nonnegative normalized probabilities; all four inspected covariance matrices positive definite (smallest eigenvalue approximately 0.0924). | Fitting supplied projections does not identify unsupplied dependence. |
| R02 | Two finite lognormal/copula components, positive-definite latent matrices (minimum eigenvalues approximately 0.5444 and 0.4578); normalized age probabilities. | Female independence and other unspecified couplings are declared simplifications. |
| R03 | Finite Gaussian/lognormal mixture with normalized nonnegative probabilities and positive-definite matrices (minimum eigenvalues approximately 0.5613 and 0.2823). A zero component probability is a declared nesting choice, not a numerical failure. | Nested latent classes and female independence are not identified by the reference summaries. |

No earlier exponentiated-unbounded-lognormal moment defect was found in these six scientific laws. Theoretical moment existence does not itself prove floating-point robustness for every extreme draw, plausible physiological tails, or valid clinical inference.

## Scientific reading of the results

All three prescribed regression coefficients are positive in every distinct delivery table. This supports preservation of broad directions in the tested setting. It does not establish adequate magnitude: external-literature constructors produce mean BMI coefficients from 0.0130 to 0.0343 against the CHNS sample estimate 0.05495, while their mean Spearman correlations range from 0.5013 to 0.5665 against 0.36146. These differences remain meaningful even though the reference is a sample estimate rather than known population truth.

Reference-assisted constructions give closer means for the requested regression projections and rank association. Those quantities were already supplied and used for calibration. The correct claim is transparent consistency with admitted summaries; there is no withheld-analysis or new-population validity test inside R. Not every individual seed/statistic is uniformly closer: no universal improvement, global accuracy score or equivalence conclusion should be inferred.

`SCIENTIFIC_DECISION.md` accurately separates this result from independent scientific reuse and proposes retaining the construction core while making review/revision optional. Its numeric ranges match the audited report. The result supports drafting the actual workflow and information regimes. It leaves generalization, partial-evidence completion, transport, unsupported joint relations, model uncertainty and comparison with equally informed synthesis methods unresolved.

The complete report retains all authors and statistics. Figures show reference sampling intervals only for the three regression coefficients, not marginal/correlation uncertainty or acceptance margins. Fixed-seed dots measure conditional simulated variation; author ranges are descriptive construction ranges. Six fresh contexts on one exposed clinical case are not six independent clinical validations.

## Artifacts and closure

Read `INDEPENDENT_RECOMPUTE.py`, `INDEPENDENT_RECOMPUTE.json` and `FINAL_INDEPENDENT_REVIEW.json` for the independent computation, exact hashes, structural checks and provenance limits. No further experiment, cohort acquisition or calibration is authorized by this review. Preserve the all-retain outcome and close this bounded unit without adding iterations to seek a favorable result.
