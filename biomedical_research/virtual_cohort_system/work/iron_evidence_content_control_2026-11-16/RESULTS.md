# Second-case evidence-content control: iron status

Completed 16 November 2026 local (17 November UTC). **The primary analysis improved, but the full profile did not.** Adding paired threshold evidence lowered absolute log-OR discrepancy by **46.81%** relative to marginal summaries. Joint low-marker prevalence and continuous rank correlation became less close to the measured sample. This is a useful analysis-specific result and a transport/structural limitation, not general data-quality improvement.

## What was frozen and run

Nine fresh GPT constructions, three per information condition, each followed by three fixed 5,000-person draws. All **9/9 constructions and 27/27 tables** completed, with no repair, replacement, target feedback or nonestimable endpoint. The 135,000 virtual rows are simulations from nine laws, not additional clinical participants. One artificial 128-row preflight fixture is excluded from these counts.

The user-requested second case uses existing NHANES iron-status data through its **previously exposed aggregate reference**: 979 complete-measurement nonpregnant women aged 20–44, positive phlebotomy weights, no CRP restriction. This unit did not download or refit patient data. The case was chosen for source-table separability and existing operator availability; root and project history were not target-blind. Constructors received fresh isolated prompts without target values, old programs or outcomes.

All arms shared the study request, original source identity/population/measurement context, three requested analyses and prompt scaffold. BASE received no selected outcome statistics. SUMMARY additionally received source single-marker low counts and ferritin geometric mean. JOINT additionally received a paired contingency table from the **same women**. SUMMARY and JOINT differed only by this joint block. This is an explicit within-source masking comparison, not a new literature-search study or a comparison to the old full two-source iron packet.

All constructors chose their own law, parameters and assumptions. The root supplied audited source facts, not a desired coefficient, correlation, OR or probability-model structure. The unchanged isolated worker sampled the submitted law. One call per constructor; no feedback/revision round in this diagnostic. Model requested and returned: **gpt-6.1-sol**, high reasoning, default service; all requests, outputs, model IDs and usage retained. Estimated total tariff cost **USD 0.6806303**, no unknown usage, below USD3. This is not an invoice amount.

## Complete scientific profile

Values below average the three seeds within each constructor and then the three constructors equally. These are descriptive summaries; no clinical equivalence tolerance or significance-based acceptance rule was added.

| Analysis | Measured sample | Context only | + Marginals | + Joint counts |
| --- | ---: | ---: | ---: | ---: |
| Crude low-marker odds ratio | 17.7898 | 4.0659 | 3.0638 | 6.9725 |
| Both markers low (%) | 7.6304 | 5.8911 | 7.7511 | 10.2244 |
| Continuous Spearman correlation | 0.3984 | 0.3215 | 0.3564 | 0.5720 |
| Hb <12 g/dL (%) | 15.2401 | 16.3978 | 14.9711 | 15.0644 |
| Ferritin <15 ug/L (%) | 12.1531 | 17.4289 | 29.8400 | 29.9844 |

The existing reference has sampling uncertainty: OR 17.79 (95% interval 9.28–34.11), joint prevalence 7.63% (6.07–9.55%), and Spearman 0.398 (0.318–0.473), using the preserved survey-design calculation. These intervals are not acceptance margins. No intervals were invented for the two newly displayed marginal fractions. The reference is a measured-sample estimate, not known population truth.

| Analysis discrepancy | Context only | + Marginals | + Joint counts |
| --- | ---: | ---: | ---: |
| Crude low-marker odds ratio — absolute natural-log OR difference | 1.5495 | 1.7620 | 0.9373 |
| Both markers low (%) — percentage points | 1.7903 | 0.5187 | 2.5940 |
| Continuous Spearman correlation — correlation units | 0.0769 | 0.0447 | 0.1736 |
| Hb <12 g/dL (%) — percentage points | 2.3844 | 0.5978 | 0.6022 |
| Ferritin <15 ug/L (%) — percentage points | 5.2758 | 17.6869 | 17.8314 |

**Primary result:** SUMMARY log-OR discrepancy 1.7620 versus JOINT 0.9373, a 46.81% descriptive reduction. All three JOINT constructor means were closer on this endpoint than all three SUMMARY means. The resulting OR remained well below the sample reference; improvement does not mean recovery.

**Adverse results:** joint-prevalence discrepancy rose from 0.5187 to 2.5940 percentage points; rank-correlation discrepancy rose from 0.0447 to 0.1736. Low-ferritin prevalence was about 30% in both evidence-augmented groups versus 12.15% in the measured sample. Low-Hb prevalence remained near 15%. Every planned constructor and endpoint remains in the tables and figure.

| Constructor | OR | Both low (%) | Spearman | Estimated USD |
| --- | ---: | ---: | ---: | ---: |
| BASE_1 | 6.3615 | 7.3133 | 0.3435 | 0.0511061 |
| BASE_2 | 2.8617 | 4.6267 | 0.2809 | 0.0552561 |
| BASE_3 | 2.9746 | 5.7333 | 0.3401 | 0.0547585 |
| JOINT_1 | 7.0634 | 10.2333 | 0.5712 | 0.0901185 |
| JOINT_2 | 7.0457 | 10.3800 | 0.5712 | 0.0870949 |
| JOINT_3 | 6.8084 | 10.0600 | 0.5735 | 0.0907149 |
| SUMMARY_1 | 2.9104 | 7.6067 | 0.3401 | 0.0754639 |
| SUMMARY_2 | 2.9104 | 7.6067 | 0.3401 | 0.0822035 |
| SUMMARY_3 | 3.3706 | 8.0400 | 0.3890 | 0.0939139 |

## What the Agent actually did

All three JOINT authors chose a Gaussian copula and independently calibrated its latent correlation to the published four-cell counts. Two implemented integration over the correlation parameter; the third implemented a conditional-normal integral. They chose different bounded/positive marginal laws, numerical routines and concentration spreads. The host supplied no copula or correlation.

An independent source-only calculation gives latent rho **0.584221** and implied Spearman **0.566145**, conditional on the chosen Gaussian family. The corresponding source OR is **6.653137** and source joint prevalence **10.3531%**. Generated values track these declared laws with finite-sample variation. This confirms successful evidence-to-program construction; it does not validate source transport or identify the continuous copula from the table.

SUMMARY authors assumed latent correlations 0.35, 0.35 and 0.40. Their population-law ORs implied by source margins are approximately 2.874, 2.874 and 3.381. BASE authors proposed three different assumption-driven models, including a nonlinear latent-iron/mixture construction. Ordinary Agent prior knowledge can therefore produce meaningful structure even without supplied quantitative evidence; BASE is not forced independence.

Complete program/specification/decision inspection found no infinite-moment law in these nine candidates. Five impose finite concentration supports on both measurements. SUMMARY_1 uses ideal half-normal log tails with finite positive polynomial moments; its implemented probability guard additionally caps numerical extremes. The remaining three have bounded Hb and positive lognormal-type ferritin tails with finite positive polynomial moments. One provenance-label issue remains: BASE_2 labels its source-suitability assessment REPORTED even though it is an Agent assessment. No scientific code was edited after submission. [Program review](PROGRAM_REVIEW.json) records each law and its limitations.

The 27 output tables have distinct hashes. Nevertheless, SUMMARY_1 and SUMMARY_2 have identical three-seed primary-analysis profiles because their selected dependence and threshold probabilities coincide and common seeds were prespecified. Other individual rank estimates also coincide. These are convergent model choices, not extra independent evidence; construction, not row or seed, remains the unit.

## Why some analyses improved and others did not

The original [Zhu2010 study](https://storage.imrpress.com/imr/journal/IJVNR/article/501902/1752835456699.pdf) concerns selected rural Chinese parous women, 2–4 years postpartum and using IUD contraception, with different exclusions and assays from the US target. All admitted statistics come from the same source population.

Its anemia prevalence is 258/1671 = 15.44%, close to this target sample's 15.24%; its low-ferritin prevalence is 504/1671 = 30.16%, far from this target sample's 12.15%. All augmented constructors directly transported these margins. This explains the model-level low-ferritin discrepancy without a code or unit error. The cause of the underlying between-population difference is not established here.

Adding the source joint table strengthened the simulated low-marker association, making its OR closer to the target sample. It also transported a joint prevalence of 10.35%, higher than the target sample's 7.63%. The same change can improve the OR and worsen joint prevalence; these quantities depend differently on marginal and joint probabilities.

Continuous rank association is a further extrapolation. Four binary counts do not determine within-category ordering. The Gaussian copula linked the calibrated threshold association to a larger continuous correlation, and that implication overshot this target sample. This is not direct evidence that every copula or every way of using the table would fail.

Conversely, SUMMARY's near-reference joint prevalence coexists with a much weaker OR and a much larger low-ferritin marginal. Agreement on one analysis cannot establish a generally valid joint distribution. No target-based repair is performed here.

## Implementation and accounting

- Nine targeted preflight checks passed before freeze, including strict cutoffs, ties, zero-cell nonestimability, a same-margins/different-pairing fixture, new iron analyzer routing and isolated execution.
- Every call started after the protocol/input freeze. All nine authors closed before any final table was sampled.
- All 27 table executions used WSL/bubblewrap with no visible host home/mounts or network route. There was no host fallback.
- Independent weighted-midrank and contingency recomputation agreed on all **135 endpoint values**, maximum absolute difference **8.88e-16**. No patient data or additional generator draws were used in recomputation.
- No observed nonpositive measurements, exact threshold atoms, duplicate measurement rows, zero-cell ORs or constant-rank failures. These finite-table checks do not certify clinical validity.
- All **705 protected historical files** remain byte-unchanged.
- The figure uses all constructors/draws and marginal checks; all **194 plotted values** were reconciled and the PNG visually inspected.
- Source retrieval added one publisher PDF (151,976 bytes, hash in the source ledger). No new patient download, new automation, GitHub sync, training or HPC run occurred.

## Relation to the first case and the paper decision

The PNS content control found a residual-correlation discrepancy reduction from 0.1633 with marginal summaries to 0.0350 with joint evidence; its BMI slopes did not improve. Here, the iron OR improved while joint prevalence and rank correlation worsened. The BASE packets differ between cases, so do not pool their error scales or present the two BASE conditions as identical.

**Supported paper statement:** an Agent can convert published joint summaries into an executable joint data law, and supplying relevant joint evidence can improve a specified scientific analysis beyond marginal summaries. The complete analysis profile reveals remaining transfer and structural assumptions. There are now two developmental existing-case examples of a targeted improvement, not two new blinded clinical confirmations.

**Unsupported statement:** all downstream analyses improve, source matching establishes target validity, more rows solve missing information, or this workflow generally outperforms ordinary Agents/statistical synthesis. This experiment does not isolate the novelty of copula mathematics, multi-source composition, autonomous retrieval or feedback revision.

Close this bounded experimental unit. Do not retune the iron or PNS laws to their exposed reference. Integrate the useful results and their full trade-offs into the planned manuscript revision. The next methodological refinement, if pursued separately, must specify which target-analysis use it addresses and how additional evidence resolves the relevant marginal or continuous-dependence uncertainty; this result does not authorize another search or paid batch.

## Artifacts

[Protocol](PROTOCOL.md) · [Source audit](SOURCE_AUDIT.md) · [Freeze](GENERATION_FREEZE.json) · [Preflight review](IMPLEMENTATION_REVIEW_BEFORE_FREEZE.md) · [Program review](PROGRAM_REVIEW.json) · [Independent calculation](analysis/INDEPENDENT_RECOMPUTATION.json) · [Costs](analysis/COSTS.json) · [Complete figure](figures/iron_content_control.png) · [Vector figure](figures/iron_content_control.svg) · [Plot data](figures/PLOTTED_VALUES.csv) · [Closeout checks](CLOSEOUT_QA.json)

Full API responses, third-party source PDF and individual real/generated rows remain local.
