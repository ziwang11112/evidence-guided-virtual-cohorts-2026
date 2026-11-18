# PNS evidence-content control — completed result

16 November 2026 local; closeout UTC 2026-11-17T03:54:03.084128+00:00.

**Adding the same paper's joint correlation block improved the requested residual-dependence analysis; adding its marginal summaries alone did not.** The benefit was specific: BMI slopes did not improve. This completes the frozen bounded comparison; no further construction or tuning is scheduled by this report.

## What was run

One already exposed PNS case, three evidence conditions, three fresh GPT constructions per condition, three fixed sampling seeds per construction. All **9 constructions and 27 tables** succeeded. Each table contains 3,000 entirely virtual people; the 81,000 rows are Monte Carlo outputs, not 81,000 independent empirical observations. A program-writing Agent chose each population law and its parameters. The host provided approved source information, enforced the interface and executed the program in isolation.

The existing base packet was identical. SUMMARY added one Burkina Faso paper's population/measurement context and univariate moments. JOINT added exactly six reported same-sample pairwise correlations to that same packet. No source-derived partial correlation or target parameter was put in either prompt. The baseline already contained INTERSALT relationship information and Beijing raw covariance context: SUMMARY is a **marginal-only increment**, not a wholly relationship-free condition.

This follows the previous PNS two-arm result but uses nine fresh authors and one additional source, not the previous two-source augmented packet. Existing source retrieval was reused. This unit does not test autonomous search or compare our workflow with an ordinary Agent.

## Full scientific result

Entries below are averages of each constructor's three saved draws, then equally averaged across the three constructors. They are not statistics fitted to pooled synthetic rows.

| Analysis | Existing sample reference | Base | + summaries | + joint block |
| --- | ---: | ---: | ---: | ---: |
| Residual correlation | 0.7172 | 0.5540 | 0.5539 | 0.7251 |
| BMI–SBP slope (mmHg / 5 kg/m²) | 3.5240 | 3.7103 | 3.7617 | 3.9238 |
| BMI–DBP slope (mmHg / 5 kg/m²) | 2.2599 | 2.9875 | 2.9977 | 3.0149 |
| SBP SD (mmHg) | 18.1916 | 17.5350 | 17.4468 | 17.9824 |
| DBP SD (mmHg) | 11.0941 | 10.4221 | 10.4139 | 10.4312 |


The frozen primary endpoint is average absolute difference, computed **per saved draw**, averaged within construction, then across constructions:

| Analysis | Base MAE | + summaries MAE | + joint block MAE |
| --- | ---: | ---: | ---: |
| Residual correlation | 0.1632 | 0.1633 | 0.0350 |
| BMI–SBP slope (mmHg / 5 kg/m²) | 0.1934 | 0.3396 | 0.5091 |
| BMI–DBP slope (mmHg / 5 kg/m²) | 0.7276 | 0.7378 | 0.7550 |
| SBP SD (mmHg) | 0.8140 | 0.7448 | 0.2991 |
| DBP SD (mmHg) | 0.6721 | 0.6803 | 0.6630 |


For residual correlation, SUMMARY MAE was **0.163279** and JOINT MAE was **0.034977**, a descriptive **78.58% reduction**. Base MAE was 0.163169. The JOINT group's mean r of 0.7251 partly averages under- and over-shoots; its difference of about 0.008 from the reference must **not** replace the preregistered MAE of about 0.035.

All three joint-informed constructions had lower residual-r MAE than each of the three summary-only constructions in this small run. JOINT_3 overshot the reference, while JOINT_1 and JOINT_2 undershot. The six source correlations did not remove transport uncertainty.

SBP dispersion was closer on average. BMI–SBP MAE increased from 0.3396 in SUMMARY to 0.5091 in JOINT, and BMI–DBP MAE was 0.7378 versus 0.7550. All nine DBP slope means remained above the sample reference. DBP SD remained below it. Thus this result supports a targeted dependence benefit, not uniform improvement of the table or all its scientific analyses.

## Every construction

| Construction | Residual r | Residual-r MAE | BMI–SBP | BMI–DBP | SBP SD | DBP SD | Estimated USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BASE_1 | 0.5439 | 0.1733 | 3.8447 | 3.0343 | 17.5425 | 10.8252 | 0.07306 |
| BASE_2 | 0.5508 | 0.1664 | 3.6385 | 3.0639 | 18.4277 | 10.7588 | 0.10370 |
| BASE_3 | 0.5674 | 0.1498 | 3.6478 | 2.8644 | 16.6347 | 9.6822 | 0.10930 |
| JOINT_1 | 0.6928 | 0.0244 | 3.9575 | 3.0484 | 18.1732 | 10.3905 | 0.11446 |
| JOINT_2 | 0.7009 | 0.0163 | 3.8096 | 2.9321 | 17.5539 | 10.1678 | 0.09478 |
| JOINT_3 | 0.7815 | 0.0643 | 4.0044 | 3.0643 | 18.2202 | 10.7352 | 0.12145 |
| SUMMARY_1 | 0.5536 | 0.1635 | 3.3712 | 2.8411 | 17.8843 | 10.0951 | 0.09187 |
| SUMMARY_2 | 0.5567 | 0.1604 | 3.9945 | 2.9942 | 16.6794 | 10.7045 | 0.10127 |
| SUMMARY_3 | 0.5513 | 0.1658 | 3.9193 | 3.1578 | 17.7767 | 10.4420 | 0.11249 |


Full draw-level results, including seed minima and maxima, are in [analysis/seed_results.csv](analysis/seed_results.csv) and [analysis/author_results.csv](analysis/author_results.csv). There were no discarded authors, replacement calls, seed searches, row trimming or post-evaluation model edits.

## What the Agent actually did

All three JOINT authors independently derived the external paper's age/BMI-adjusted residual correlation, approximately 0.788, from its reported correlation matrix. The source transformation is ordinary projection algebra, not a new statistical estimator, and it does not include sex adjustment.

- JOINT_1 documented the source projection and chose an explicit target innovation correlation of 0.70 as a transport assumption.
- JOINT_2 independently documented the same source projection, also chose 0.70, and built bounded paired innovations with a covariate-dependent common support scale.
- JOINT_3 assembled the source covariance blocks in its sampler and computed the Schur complement there. It then used a conditional Student-t construction and physiological support restrictions.
- All six BASE/SUMMARY authors chose nominal innovation correlation 0.55 as an assumption informed by older raw-correlation context. They did not derive the missing adjusted dependence from marginal moments.
- All nine retained INTERSALT's converted BMI anchors, 3.877 and 2.9835 mmHg per 5 kg/m², under stated transport assumptions. This helps explain why the added dependency block did not systematically repair the BMI slopes, although it does not establish causal mediation.

The source-only answer and desired target value were not hand-entered by the root task. The root did curate the evidence cards and mask fields. This contribution should therefore be described as an **evidence-content intervention on Agent construction**, not a fully automatic source-admission achievement.

Conditional rejection, nonlinear age terms and heterogeneous residual scales mean an innovation parameter need not equal the final regression-residual correlation or slope. That is why the saved datasets were actually analyzed rather than substituting declared model numbers for results.

## Implementation and verification

- Requested and returned model: **gpt-6.1-sol**, high reasoning, nine fresh contexts, no tools, no retries or revisions in this diagnostic.
- Estimated construction cost **USD 0.9223776**, under the USD3 ceiling. This is usage valued at the stored tariff, not an invoice, and excludes earlier source retrieval and development.
- Input tokens 44,631; cached input tokens 29,736; output tokens 88,218, including 45,103 reasoning tokens. Reasoning tokens are not added again to output.
- Every program/specification was sealed before sampling; all constructions closed before final execution. Generation ran only in WSL/bubblewrap with no host fallback.
- All **162 endpoint calculations** agreed with the separate QR implementation, maximum absolute difference **8.62e-14**. This is independent numerical implementation, not a second external scientific reviewer.
- Full code and model declarations of all nine programs were inspected. Their released variables are bounded, so relevant moments are finite. No generator was changed as a result of inspection.
- All 27 table hashes are distinct. No duplicate measurement rows, nonpositive BMI/BP, SBP below DBP or rank-deficient design was observed. These checks do not certify every clinical feature of the generated people.
- All **770 existing files** in the previous closed PNS experiment remained unchanged.
- The figure includes all 135 saved-draw scientific values, 45 construction means, five reference values and nine costs; all **194 plotted values** reconcile with the closed outputs. PNG was visually inspected for legibility and clipping.

The reference is an already exposed weighted complete-case PNS laboratory-substudy estimate. It is neither an exact population truth nor a new protected confirmation. Authors were not given its results. No real-patient refit or new dataset download occurred.

## Interpretation for the paper

Supported wording:

> In a frozen developmental PNS comparison, adding a same-source joint correlation block improved the residual-dependence analysis beyond adding that paper's marginal summaries. Agents independently translated the block into conditional covariance reasoning, while improvements did not extend uniformly to regression slopes.

The experiment strengthens the link **requested scientific analysis → relevant missing relation → source evidence → Agent-authored joint law → analysis of virtual data**. It supplies a control against the simpler explanation that any extra paper or extra marginal summaries would have produced the same observed benefit.

What it does not establish:

1. A general effect across diseases, target populations or model families. This is one selected, previously positive and exposed case with three construction calls per arm.
2. Novelty of conditional covariance algebra or information supplied by correlation matrices.
3. That the full six-correlation composition, rather than the new raw SBP–DBP correlation alone, is the uniquely active ingredient. This pilot compares the complete joint block.
4. Token-length/attention equivalence: JOINT necessarily contains additional informative numbers. Prompt and call ceilings are common, but payload lengths differ.
5. Clinical equivalence, target-population identification, universal synthetic-data suitability, retrieval-policy superiority or feedback benefit.
6. That the synthetic table can replace measurements of individual participants.

## Decision and next work

**Complete this unit and retain the targeted positive result with the full mixed profile.** Do not retune the exposed PNS laws or add paid calls to improve its slopes. Use the result as the evidence-content-control subsection beside the artificial composition experiment and the scientific-use examples. A proposed insertion is provided separately; v0.32 has not been silently overwritten.

For a broader conference claim, the remaining substantive gap is repeatability of the same evidence-to-analysis mechanism in a separately admitted case with usable conditional evidence. The lipid source investigation remains closed at admission failure. A new case must be chosen on evidence/operator availability before target-performance inspection; this report does not authorize or launch another search or batch. The earlier matched-size lifestyle sampling diagnostic remains **planned, not run**.

## Artifacts

- [Frozen protocol](PROTOCOL.md), [source audit](SOURCE_AUDIT.md), [freeze receipt](GENERATION_FREEZE.json).
- [Program inspection](PROGRAM_INSPECTION.json), [inspected hashes](INSPECTED_PROGRAM_HASHES.json).
- [Independent recomputation](analysis/INDEPENDENT_RECOMPUTATION.json), [complete slot accounting](analysis/SLOT_ACCOUNTING.json), [costs](analysis/COSTS.json).
- [Complete result figure](figures/evidence_content_control.png), [vector PDF](figures/evidence_content_control.pdf), [editable SVG](figures/evidence_content_control.svg).
- [Closeout quality checks](CLOSEOUT_QA.json).

All generated rows, raw API exchanges and third-party source material remain local. No GitHub synchronization occurred in this unit.
