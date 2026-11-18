# What two evidence-compatible virtual cohorts predict for blood-pressure screening

**One Agent preserved the directly reported correlation and demonstrated that the same five published statistics allow different answers to a second screening question.** With all five moments fixed at their source values, its two executable models imply that **11.94% or 15.09%** of participants exceed both blood-pressure cutoffs. The independent Freetown release returned **44.21%**. A separate check on that file found zero people exceeding only one cutoff. This limits biological interpretation of the external discrepancy.

## From the publication to the tables

One fresh GPT-6.1 Sol session received the verified pooled means, SDs and unadjusted Pearson correlation from Tables 2–3 of the rural Nouna study in Burkina Faso, plus a description of an urban screening population aged 40 and over. We elicited two plausible constructions and an analysis-specific judgment before revealing the target. Both models were produced without target rows, a target effect, a cohort name or the comparator program. This trial isolates modeling from an identical five-statistic packet. The original-paper experiment in v0.34 separately tests source reading. The public protocol preceded the API call and a second public commit recorded both programs, decisions, simulated-table hashes and mathematical predictions before disclosure. [Nouna publication](https://pmc.ncbi.nlm.nih.gov/articles/PMC12185928/) · [Protocol freeze](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/commit/da7e108713a5c0ff90829fa684c19ba4eac66c26) · [Pre-disclosure model freeze](https://github.com/ziwang11112/evidence-guided-virtual-cohorts-2026/commit/74bb744bbf8721aec04ac1a0b2992e5ff7161b40)

The Agent's primary law jointly samples diastolic pressure and positive pulse pressure, then sums them to obtain systolic pressure. It independently chose the same bivariate lognormal family as the statistical comparator. Its alternative introduces a hypothetical 75%/25% mixture with different mean pressures. The program reduces the within-group covariance by the between-group contribution, retaining the source means, variances and correlation. The two components represent an assumption about heterogeneity. No observed clinical subgroups validate that assumption. The primary and statistical implementations draw different finite samples from the same population law. [Agent's decisions](DECISIONS.json) · [Submitted code and parameters](candidates)

The two Agent laws and the statistical comparator each produced three independently seeded draws of 10,000 people in the offline worker. The nine tables are simulation replicates under three specifications. One completed model call used 852 input and 8,281 output tokens. The recorded tariff estimate is USD 0.084514. The direct source calculation and statistical comparator used zero model calls. [Execution and cost record](CLOSURE.json)

## Same analysis on every table

Q1 is crude Pearson correlation. Q2 counts people with systolic pressure ≥140 **and** diastolic pressure ≥90 mmHg on the same averaged measurements. The reported rates refer to this conjunction. A diagnosis of hypertension uses a different definition.

| Input | Q1 correlation | Q2 both at or above threshold |
| --- | ---: | ---: |
| Direct calculation from the five inputs | 0.780 | Undetermined |
| Agent primary, pooled draws | 0.781 | 11.89% |
| Agent alternative, pooled draws | 0.781 | 15.06% |
| Statistical constructor, pooled draws | 0.781 | 12.15% |
| Independent Freetown release (1,244 records) | 0.859 (0.847–0.872) | 44.21% (41.64–46.79%) |

Parentheses give 95% percentile intervals across 2,000 within-zone participant bootstraps. These intervals condition on the eight represented zones. They omit uncertainty about community selection, field construction and population transfer. All three virtual arms passed the five frozen source checks and produced positive, ordered pressures in every row. The target means were 131.50 and 87.41 mmHg, compared with 125.22 and 80.54 in the source. Source estimates are rounded sample summaries. [Complete aggregates](AGGREGATES.json) · [Two-panel figure](prospective_pressure.pdf)

### What was established before looking at Freetown

The Agent designated Q1 as reported in the source and Q2 as underdetermined. It explicitly flagged transfer concerns for both and predicted that the alternative law could change Q2. It did not provide a numerical prediction of the size or direction of that change in its decision text. The coordinator supplied the two endpoints and requested alternatives and support judgments. Independent analytic reconstruction of the submitted programs confirmed a population correlation of 0.780 in both laws. One-dimensional quadrature gave 0.119449 and 0.150851 for Q2. These are constructive examples with the same five model moments and different threshold probabilities. The two numbers describe the submitted scenarios. Other compatible laws could give values beyond them. [Pre-disclosure mathematical audit](MODEL_AUDIT.json)

We retain the prespecified operational criterion as written. The gap between the simulated estimates is 3.17 percentage points. Subtracting four times the sum of their Monte Carlo standard errors leaves **1.60 points**, below the specified **2-point** threshold. The finite-draw materiality check therefore **did not pass**. The independent integration establishes a population-law gap of **3.14 points** without Monte Carlo sampling. These statements concern two different quantities. The 2-point choice was an illustrative planning convention. [Frozen evaluation](PLAN.md) · [Calculations](AGGREGATES.json)

### What the independent release allows us to say

The research team had screened sources, workbook headers, eligibility counts and target methods before construction. It first computed target effects after both public freezes. For 550 of 1,244 eligible records both thresholds were met, and 694 met neither. No record showed isolated systolic or isolated diastolic elevation at these cutoffs. In the entire 2,394-row release the four counts were 871, 1,523, 0 and 0, respectively. The entire-release cross-tabulation was an additional post-disclosure check. The release contains 479 distinct numerical pairs among the 1,244 eligible records.

Freetown researchers describe averaging two seated electronic measurements. The deposited codebook describes the two pressure fields as columns added to represent SBP and DBP. The released workbook provides final pressure values; the codebook does not establish how the underlying reading pairs map into them. Exact agreement of the two binary indicators makes the recorded Q2 identical to each single-threshold rate. It gives limited leverage for validating individual pairing across the thresholds. The cause of this pattern remains unresolved. The bootstrap reproduces the released values and cannot resolve their provenance. [Freetown study](https://doi.org/10.1136/bmjopen-2022-067643) · [Dryad data and codebook, version 8](https://doi.org/10.5061/dryad.k98sf7mbp) · [Reference field audit](REFERENCE_AUDIT.json)

Both laws preserved the direction of association, underestimated the released correlation by about 0.079, and underestimated the recorded joint event by 29.15 to 32.32 percentage points. Source-to-target differences in pressure levels, population selection, resting protocol and the unresolved field pairing all matter for interpretation. No causal decomposition of that gap is available here. An independent estimator implementation in the same research session checked the real row selection, nine generated tables, both target endpoints and both interval endpoints; the largest absolute numerical difference was below 5 × 10⁻¹³. All participant-level tables and original API responses remain local. [Independent recomputation](VERIFICATION.json) · [Release and exposure record](ADMISSION.json)

## Manuscript decision

Keep this as a prospective test of what the Agent can establish **before** target disclosure. The directly reported analysis behaved alike in both models. The team could calculate it from the source without generating rows. For a second analysis the Agent produced two executable, moment-matched counterexamples that quantify the consequence of an unreported distributional choice. The method earns credit here for identifying that uncertainty and making it testable. Its primary law and the statistical comparator have identical population predictions. One elicited author and one external release leave the frequency of this behavior across Agents and the clinical validity of these estimates open.

The new case can sit alongside the v0.34 blood-pressure and iron experiments, which showed how supplying a joint statistic changed some downstream analyses. In this case the external reference has a material pairing limitation. We close the target to further tuning, retain all discrepancies and give the stronger clinical transfer claim lower priority than the source-supported sensitivity result. [v0.34 evidence summary](../v34_review_assessment_2026-11-18/ASSESSMENT.md)

## Reproduce the checks

Run `python replay_public.py` from this directory to verify the public receipts, aggregates and model-implied probabilities without an API call. Optionally pass `--workbook PATH` with the exact v8 data workbook from Dryad to recompute the two target analyses and their zone-conditioned intervals. The workbook hash is checked before decoding. Source uncertainty, target sampling uncertainty and the spread across modeling assumptions have distinct interpretations throughout.
