# First fasting-insulin enrichment pilot: main association retained, shape and subgroup structure not recovered

27 October 2026 local project date; execution timestamps are recorded in UTC. Status: generation, reserved evaluation and independent numerical audit complete. All 84 fits, 168 endpoints and 20 outputs were independently checked. No model has been changed in response to the results below.

## What was actually run

The official NHANES 2017–2018 public data provided measured BMI, fasting serum insulin and demographic/design variables. Eligibility was fixed before relationship analysis. The scored complete-case domain contains **1,700 adults aged 20–79** without self-reported diagnosed diabetes, allowing borderline responses, with documented exclusions for insulin use and pregnancy. The survey design retains **2,711 positive fasting-weight records**, including outside-domain records with zero estimating-equation contributions. Original subsample weights do not automatically correct remaining item nonresponse.

The generation Agent received only randomly keyed BMI, age and sex rows. The entire insulin column, original record IDs, all target insulin summaries and the reserved analysis specifications/results were withheld. Generation did not use glucose, HOMA-IR, source insulin microdata, target calibration, or a target-trained statistical model.

The clean Agent independently issued six substantive literature queries through a screening gateway and reviewed six accepted non-NHANES primary papers. Three supplied numerical inputs; the others informed limitations or were explicitly not used numerically. One earlier search context encountered prohibited snippets and was retired before constructing a model. Its incident is disclosed; none of its snippets or parameters were forwarded to the fresh context. The gateway and fresh context provide procedural controls, not proof that a pretrained model has never encountered relevant public facts.

The Agent selected an executable **conditional lognormal generator**. It derived a BMI log slope from a published contrast between two non-diabetic BMI groups, used published age-bin location anchors and an older-age ratio, and derived a spread parameter from published standard errors and group sizes. It explicitly assumed no additional sex effect or BMI-by-sex interaction and a common linear BMI slope on the log scale. These were Agent decisions, not coordinator-written target coefficients. They remain assumptions, not identified individual conditional effects.

All **20 scheduled seeds** produced an enriched table of 1,700 rows, giving 34,000 generated insulin values across repetitions. Every original BMI, age, sex and row key was preserved; same-seed replay was exact. These are 20 stochastic draws from one Agent construction, not 34,000 new observed patients or 20 independent Agents. The numerical executor performs sampling; the LLM did not directly type each record. No language model was trained.

Source/code review verified the extracted values, SE-to-SD arithmetic and generator implementation. It requested two documentation clarifications, supplied as addenda: one source-line locator and the distinction between simulated source-assay-scale measurements and an identified latent physiological distribution. No numerical revision was justified or made. A no-op on generation is reported honestly; there is no claim that review improved predictive performance.

## Main scientific findings

All four prespecified models and eight associated endpoints were retained. These endpoints overlap and are not eight independent studies. The same survey-weighted functions were used for true and generated insulin. Reference intervals account for stratified PSU design; generated intervals condition on simulated outcomes and do not capture all source/model/transport uncertainty.

| Scientific question | Real-data analysis | Enriched-data analysis across20 draws | Interpretation |
|---|---|---|---|
| Is BMI positively associated with insulin? | Weighted raw-scale correlation0.543; log-insulin correlation0.607 | Median raw correlation0.439 (draw range0.365–0.531); median log correlation0.423 (0.368–0.495) | Broad positive relationship retained; magnitude is weaker. This relationship was supported by input literature. |
| Does the BMI association remain after adjusting for age and sex? | Per5 kg/m², insulin geometric-mean ratio1.346,95% survey interval1.304–1.390 | Median ratio1.230; every draw has a positive adjusted association with an interval above the null | Similar qualitative conclusion, without exact effect recovery. It is a target-specific transfer check of an evidence-supported relationship. |
| Is the BMI slope different between lower and upper prespecified BMI intervals? | Upper-minus-lower log-slope contrast−0.123 [−0.174,−0.072] per5 BMI units | Median0.003, draw range−0.039–0.052; all20 conditional intervals include zero | The source-data curvature contrast is not recovered. The generator assumes a common linear log-BMI slope. |
| Do female and male BMI slopes differ? | Female-minus-male log-slope difference−0.109 [−0.176,−0.042] | Median0.006, draw range−0.045–0.058;19 intervals include zero and1 is positive | The observed subgroup difference is not recovered; one draw points confidently in the opposite direction. The generator imposes no interaction. |
| Are BMI slopes positive within each sex? | Male ratio1.447 [1.358,1.542]; female ratio1.297 [1.255,1.341] per5 BMI units | Median male ratio1.223 and female1.233; all20 draws positive within both sexes | Within-group qualitative relationships are retained, while their contrast is missed. |
| Are adjusted main age and sex effects clearly resolved? | Both reference intervals include zero | Age intervals include zero in19/20 draws; sex intervals in20/20 | Similar unresolved evidence states are not proof of no biological effect, nor an independent success count. |

The shape contrast compares secant slopes over the predictor-only frozen BMI quartiles24.375,28.0 and33.125 kg/m², under the specified spline. It does not prove a universal plateau over every BMI value or population. Sex contrasts use the recorded binary survey coding and a descriptive cross-sectional model. No causal interpretation is claimed.

Generated ratios in this report are obtained by exponentiating the median log-effect estimate across20 draws. This is not the arithmetic median of the20 exponentiated values. The distinction is numerically small here and changes no scientific interpretation. Draw ranges are not confidence intervals.

For an analysis-focused user, the important result is **partial analytical usefulness**: adding the virtual column permits valid execution of the planned analyses and reproduces the broad positive association. The two structural mismatches are not failures to match a decimal place; they change what one would say about the relation's shape and heterogeneity. Conversely, matching the broad relationship does not demonstrate every added-variable analysis is valid.

## Evidence roles and why the mismatches are informative

1. **Evidence consistency:** positive BMI–insulin association and positive within-sex slopes largely follow from the imported BMI contrast and common-slope construction. They demonstrate translation of literature into analysable records, not discovery of an unknown relationship.
2. **Target-specific transfer:** the adjusted target coefficient and correlations were not supplied or fitted. Their recovery tests the transport of the chosen evidence and assumptions. No exact numerical equivalence was required, and no equivalence claim is made.
3. **Assumption-sensitive reserved analyses:** the generator's common linear slope and absent interaction make nonlinear and subgroup contrasts weak or absent by construction, apart from simulation fluctuation and covariate/model projection. The real reference contains both contrasts in this prespecified descriptive analysis. The result pinpoints an information/model-structure limitation, not a discovered source-parser defect.
4. **Unresolved reference questions:** intervals overlapping zero remain unresolved. Treating those as proven nulls would overstate validation.

All substantive findings must be read alongside source limitations: highly selected healthy reference populations, an ecological group-to-individual bridge, differing assay/sample matrices, marginal spread reused as conditional spread, and no posterior uncertainty for these choices. Source arithmetic can be correct while transport is limited.

## What the pilot supports, and what it does not

Supported: a real literature-searching Agent can author a traceable generator that enriches a wholly missing clinical variable, preserves real covariates, and reproduces some scientifically useful relationships under a newly locked evaluation. The complete workflow has run rather than merely been specified.

Not established: superiority over other generation methods; recovery of all relationships; individual insulin accuracy; new biological discoveries; calibrated inferential uncertainty; reliable generalization across populations; or savings in actual patient recruitment. There is no statistical-generator comparator in this first requested feasibility run. Sampling more rows cannot resolve missing structural evidence.

This result is neither a reason to declare the full method validated nor a reason to discard the broader idea. It provides a concrete next question: **can the framework identify which structural assumptions are unsupported, acquire applicable joint/conditional evidence, and improve genuinely new held-out analyses in another locked cohort?**

## Next bounded step

Retain this cohort as an exposed development case after this release. Improve the general evidence-to-model workflow, not this reference coefficient: require the Agent to document coverage of functional form, subgroup heterogeneity, conditional variation and population/assay transport, and decide what evidence it can actually justify. Do not hand-insert the observed curvature or sex contrast, and do not count a rerun against these now-known answers as independent confirmation.

Then run the unchanged assessment policy on a separately locked cohort or cycle, reporting that its family/source may still overlap the current benchmark. A small suitable evidence-matched statistical comparator can be added when the information regime is audited. One more bounded test is justified before any large batch or HPC allocation; no new execution is started by this report.

## Artifacts and audit trail

- [Full analysis table with endpoint evidence roles](results/report_v3/ALL_ANALYSES.md), [aggregate interpretation CSV](results/report_v3/scientific_interpretation.csv), and [correlation summary](results/report_v3/correlations.json).
- [Comparison figure](results/report_v3/initial_v1_analyses.png) and [PDF](results/report_v3/initial_v1_analyses.pdf). Grey bars are real-data survey intervals; teal bars are min–max across draws, not confidence intervals.
- [Source/code review](review/INITIAL_SOURCE_CODE_REVIEW.md), [source ledger](agent_clean/EVIDENCE_LEDGER.json), [Agent decision](agent_clean/INITIAL_DECISION.md), [review response](agent_clean/REVIEW_RESPONSE.md), and [incident record](review/INCIDENTS.md).
- `freeze_v1/outputs_freeze.json` SHA256: `aee9d3b44df52b59a754cdcfd88629eddf414f4e8b2c7e23c4ce102ba271f4c4`. All generated outputs were bound before the single reserved evaluation.
- [Independent postrun audit](review/postrun/POSTRUN_AUDIT.md) and [source/role audit](review/postrun/SOURCE_ROLE_AUDIT.md): 192 hash checks across 98 unique files passed; maximum independent coefficient difference 1.13e-14 and covariance difference 9.59e-17. These are implementation checks, not a scientific superiority claim.
- The first report render had an overlapping legend. `report_v2` repaired layout; `report_v3` adds explicit per-endpoint evidence/assumption labels requested by audit. The frozen numerical evaluation is unchanged. No cohort was regenerated for these reporting changes.

Official sources: [NHANES insulin documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/INS_J.htm), [body measures](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.htm), [demographics](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm), and [survey variance guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx). These describe the data and analysis design; the numerical findings in this report are this pilot's calculations.
