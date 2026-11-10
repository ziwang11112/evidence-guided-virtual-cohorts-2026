# Summary-conditioned synthetic obesity data: frozen temporal prediction pilot

25 October 2026. Executed experiment, not a proposed result.

## Main finding

Models trained on the two directly authored synthetic cohorts retained useful discrimination in later real participants, but the primary result did not show a consistent advantage over an ordinary statistical generator. Logistic-regression ROC-AUC was **0.734936** using 128 real training records, **0.712130 / 0.726871** using the two agent cohorts, and **0.717394** at the median of 100 ordinary synthetic cohorts. Each training cohort contained 128 rows. All models were frozen before accessing the 1,811 eligible real test participants.

This is stronger evidence than matching the supplied means or a paper's p-values: the endpoint here is prediction in a different survey cycle. It is still a small generator pilot, with one real training draw and two agent contexts. It establishes neither equivalence to real training nor an agent-specific benefit, and it does not demonstrate replacement of patient recruitment.

[Frozen temporal prediction results] (local audit artifact)

## What was actually run

The source is public, real participant data from the CDC National Health and Nutrition Examination Survey (NHANES), rather than a hospital patient cohort. Development uses 2015–2016; evaluation uses 2017–2018. These are distinct cycles within one survey program, not independent clinical institutions.

The task is to classify **current measured HbA1c >=5.7% among adults with measured BMI >=30**, using age, recorded sex, BMI, waist circumference and mean available positive auscultatory systolic blood pressure. The operational label includes diabetes-range measurements and treatment effects. It is not a future-diabetes forecast, adjudicated diagnosis or an undiagnosed-disease label.

The frozen protocol selected 128 participants without outcome stratification or redraw from 1,870 eligible development participants. The remaining 1,742 were not used for fitting, tuning or summary estimation. The 128 records contained 60 below-threshold and 68 elevated-HbA1c labels. Their high_a1c-by-male counts were 38, 22, 39 and 29.

Both fresh agent contexts and the ordinary generator received the same conditional aggregate information: counts, means, sample standard deviations, seven quantiles and a regularized Gaussian-rank correlation matrix within each of the four label-by-sex strata. No individual records were provided to the two authors. Their contexts were instructed to directly write the numerical rows, using only the file-writing tool, with no code execution, browsing or source inspection. This is procedural context isolation on a shared host, not a security sandbox or a formal pretraining-contamination guarantee.

Both initial agent outputs passed structural validation. Neither received a repair request, numerical-fidelity feedback or predictive feedback. Every ordinary cohort used the fixed Gaussian-copula/seven-quantile interpolation procedure and a prespecified seed. Both methods received all aggregate values; the ordinary sampler specifically uses the quantiles and rank matrix and does not enforce each finite-sample mean/SD exactly. It is an information-matched baseline, not an assertion that every statistical synthesis technique was tested.

Two fixed model families were fit to all 103 cohorts: standardized L2 logistic regression and a small histogram gradient-boosting classifier. All 206 fitted models, generator outputs, preparation code, predictor definitions and provenance were hashed before downloading the test participant files. There was no feature selection, hyperparameter search, test-guided calibration or selection of a favorable ordinary seed. The same 128 real records supplied the real-only comparator.

This evaluates the generation component of the proposed small agent system. It **does not measure a benefit from a Diehl-style feedback/revision loop**, because no performance feedback or revision was used here. The earlier tool-planning arm was not counted again: it previously reproduced the ordinary generator exactly.

## Test cohort and data integrity

The 2017–2018 selection was: 9,254 demographic records → 8,704 examined → 4,883 ages 20–79 → 2,067 with BMI >=30 → 2,038 after excluding recorded pregnancy → 1,945 with waist → 1,879 with HbA1c → **1,811** with an available positive systolic reading and positive MEC weight. All 1,811 had recorded sex. There were **975 elevated-HbA1c labels and 836 below-threshold labels**. No source identifiers overlapped the eligible development participants.

Only age, male, BMI, waist and SBP entered a model. Raw HbA1c, source identifiers, survey weights, strata and PSU identifiers were retained as audit sidecars and excluded from predictors. The primary evaluation targets the observed eligible sample. MEC-weighted metrics are descriptive sensitivity analyses; no survey-design confidence interval or US population prevalence estimate is claimed.

The observed test label fraction was 53.8377%; the weighted fraction was 44.6813%. These differ because the survey weights change the represented composition. They were computed only after model lock and were not used to change class balance or recalibrate predictions. Unknown pregnancy status is not verified absence of pregnancy; the public pregnancy field has restricted coverage. Seven retained women ages 20–44 had unknown/unconfirmed pregnancy status, consistent with the frozen rule to exclude recorded pregnancy. Age 80 and above was excluded because age is top-coded. Complete-case selection and absence of medication adjustment limit interpretation.

## Primary results: fixed logistic regression

| Training data | ROC-AUC ↑ | Brier ↓ | Log loss ↓ | Balanced accuracy at 0.5 ↑ | Mean predicted probability |
|---|---:|---:|---:|---:|---:|
| Real 128 | 0.734936 | 0.210303 | 0.611327 | 0.676056 | 0.550724 |
| Direct agent A1 | 0.712130 | 0.216229 | 0.624841 | 0.658277 | 0.541259 |
| Direct agent A2 | 0.726871 | 0.213445 | 0.618035 | 0.674859 | 0.544048 |
| Ordinary synthesis, median of 100 | 0.717394 | 0.215560 | 0.624669 | 0.666441 | 0.549142 |

The ordinary-generator 2.5th–97.5th percentile interval was **0.651048–0.743380 for AUC** and **0.205302–0.234218 for Brier**. These intervals describe variability across generated training datasets, not confidence intervals, participant sampling uncertainty, or a statistical superiority test. Different column medians need not correspond to the same generated cohort.

A1 and A2 were respectively **0.022806 and 0.008065 AUC below real training**, and **0.005264 below / 0.009477 above the ordinary median**. Their AUCs exceeded 38 and 67 of the 100 ordinary draws. Both fall inside the ordinary-generation interval. The real comparator exceeded 86 ordinary draws; it did not beat every ordinary realization. No best ordinary draw was selected as the comparator.

The prevalence-only reference had AUC 0.500000 and Brier 0.248578. Thus the synthetic-trained models contained useful predictive information relative to this reference. That information was partly supplied by the outcome-conditional real summaries; it was not newly discovered by the LLM.

Average predicted probabilities were near the unweighted observed fraction, but this single calibration-in-the-large diagnostic does not establish calibration across risk ranges or subgroups.

## Prespecified secondary model and weighting sensitivity

| Training data | Gradient-boosting AUC ↑ | Gradient-boosting Brier ↓ | Weighted logistic AUC ↑ | Weighted logistic Brier ↓ |
|---|---:|---:|---:|---:|
| Real 128 | 0.660930 | 0.240598 | 0.742122 | 0.215360 |
| Direct agent A1 | 0.634484 | 0.247879 | 0.722713 | 0.219157 |
| Direct agent A2 | 0.646883 | 0.242525 | 0.734453 | 0.218190 |
| Ordinary synthesis, median of 100 | 0.638858 | 0.261487 | 0.724310 | 0.219780 |

Both agents had lower gradient-boosting Brier than the ordinary median; A2 was close to the real comparator on that metric. Its gradient-boosting log loss (0.690898) was also slightly below real training (0.692248), so the real comparator was not best on every reported endpoint. However, both agents had lower gradient-boosting AUC and higher Brier than the real comparator. The primary logistic result remained mixed relative to ordinary synthesis. A secondary favorable metric does not reverse the primary conclusion or establish a stable generator advantage.

No model family was selected after these results. The gradient-boosting family performed less well than logistic regression under the fixed small-training-budget configuration; this does not establish that boosting is generally inferior or that tuning would fail.

## What the result changes

1. **Feasibility is supported for this task.** Aggregate-conditioned synthetic rows can train a model that discriminates current elevated HbA1c in later real survey participants. The pilot moved beyond rechecking statistics mathematically implied by the generator input.
2. **The necessity of direct LLM authorship remains unsupported.** One agent was below the ordinary median and one above it; neither surpassed the real comparator in primary AUC/Brier. Two contexts cannot characterize generation stability.
3. **The existing source information remains essential.** The summaries were measured in 128 real people and were conditioned on their outcomes. Producing 128 synthetic rows does not create 128 new independent clinical observations or eliminate the need to collect outcomes.
4. **There is no current paper-ready central innovation claim.** This is an auditable methods pilot, not evidence of a new obesity mechanism, a novel validated generator, noninferiority or recruitment savings.

## Decision and bounded next step

Do not build a larger multi-agent platform or launch model training on the strength of this pilot. Preserve both runs and all ordinary draws; do not promote A2 as the selected generator or regenerate against this test.

If the generation question is continued, the next useful experiment is a small **reliability and comparator test**, not additional free-form architecture: use repeated prespecified real training draws, include a statistical comparator that reduces finite-sample moment/quantile sampling error, keep the information budget explicit, and report every agent run. This would distinguish a reproducible synthesis benefit from one favorable 128-person draw or ordinary Monte Carlo variability. The secondary Brier pattern is a hypothesis for that later study, not a confirmed mechanism.

The current 2017–2018 results are now exposed and cannot be reused as an untouched final test after development decisions based on them. A subsequent confirmatory study needs a newly locked evaluation cohort and a prospectively chosen meaningful performance margin. A non-significant difference or a small observed AUC gap would not by itself establish equivalence. Any claim about reducing recruitment would additionally require a direct, prespecified real-sample-size versus performance analysis, not merely matching a published table.

## Artifacts and reproducibility

- [Protocol] (local audit artifact), [data/source audit] (local audit artifact), [design critique] (local audit artifact), and [pre-test code audit] (local audit artifact).
- [Development freeze] (local audit artifact), [model freeze] (local audit artifact), [model index] (local audit artifact), and [event log] (local audit artifact).
- [Shared summary packet] (local audit artifact) and [author instruction provenance] (local audit artifact).
- [Unmodified A1 output] (local audit artifact), [unmodified A2 output] (local audit artifact), and all 100 ordinary outputs under `ordinary/`.
- [Full metrics] (local audit artifact), [ordinary distribution summaries] (local audit artifact), [compact comparison](results/compact_comparison.csv), and [evaluation metadata] (local audit artifact).
- [PNG figure] (local audit artifact) and [PDF figure] (local audit artifact).
- Preparation: `data_prepare.py`; fixed execution: `experiment.py`; descriptive reporting only: `summarize.py`.

Independent numerical and raw-test-data audits both **passed**: [numerical audit] (local audit artifact), [raw-data audit] (local audit artifact), [machine-readable audit results] (local audit artifact), and [audit script] (local audit artifact). All 207 saved prediction vectors (206 fitted models plus the constant reference), 206 model schemas and 323 locked artifact hashes were verified. Independently recomputed metrics differed by at most 1.33e-15. Both raw cohorts, the original seeded 128-person draw, the outcome labels, sequential exclusions and lack of ID overlap were independently checked. No data/model correction was needed. The code/protocol/model locks remained unchanged during reporting and audit. Exact LLM backend version, token usage and billing cost were not exposed by the subagent interface and are not estimated here.

## Primary data sources

- CDC [NHANES 2015–2016 data index](https://wwwn.cdc.gov/nchs/nhanes/search/DataPage.aspx?Cycle=2015-2016).
- CDC [NHANES 2017–2018 data index](https://wwwn.cdc.gov/nchs/nhanes/search/DataPage.aspx?Cycle=2017-2018).
- CDC [DEMO_J demographics and survey design](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm), [BMX_J anthropometry](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.htm), [BPX_J auscultatory blood pressure](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BPX_J.htm), and [GHB_J measured glycohemoglobin](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/GHB_J.htm). Raw XPT URLs, retrieval timestamps and SHA-256 hashes are retained in each cycle's download manifest.

This pilot uses a new, explicitly defined task on these public data; it is not advertised as exact replication of a published clinical prediction model.
