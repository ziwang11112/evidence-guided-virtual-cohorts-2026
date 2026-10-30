# M15-A evidence-basis audit

30 October 2026. Post-run audit requested by the user; no generation, calibration, repair or new target evaluation.

**Verdict: the table is guided by genuine published marginal summaries, but its joint relationships and individual values are not established by those summaries. It is a directly authored, assumption-dependent illustration, not yet evidence-supported data for substantive biomedical analysis.** The builder disclosed its assumptions; the main limitation is the narrow evidence contract, not an undisclosed numerical generator or a fabricated citation.

## What was actually supplied

The builder received a curator-prepared excerpt from [Yun et al. (2021)](https://doi.org/10.1038/s41366-021-00810-9), specifically Table 2 and limited Methods context. Its 20 admitted summaries were the age mean/SD, BMI mean/SD and urate mean for each of four published race/sex strata. Independent review of the cached original Europe PMC XML confirms the transcription. The source describes 3,402 nondiabetic Bogalusa adults, ages 20–56, with urate measured by an Olympus AU-5000 uricase assay.

The protocol fixed a much smaller fictional table of 128 rows, with group counts 38/46/19/25 approximating source proportions. These counts are a task design choice, not additional patient evidence. The evidence JSON and source checks were prepared by the controller. This builder did not retrieve papers, extract the evidence itself, or combine different studies: the task explicitly prohibited those actions.

The builder chose all literal row values. The controller checked them and returned discrepancies for the same 20 supplied summaries once. After reviewing that report, the builder retained the table unchanged. Therefore this run demonstrates direct authorship and a feedback review, but no successful correction and no end-to-end autonomous literature-to-data process.

## Evidence-to-output map

| Output property | Actual basis | What can be claimed |
|---|---|---|
| Four age means and four age SDs | Reported source summaries | Numerical resemblance to those summaries can be checked; the full age distribution is not identified. |
| Four BMI means and four BMI SDs | Reported source summaries | Group centers and dispersion have support; skewness, tails and individual BMI values do not follow uniquely. |
| Four urate means | Reported source summaries | The group averages have support. This does not support every urate value or its dispersion. |
| Group allocation and table size | Protocol choices informed by source counts | A small illustrative allocation, not 128 observed or independently validated participants. |
| Age range and units | Source context plus task rules | Compatibility checks, not proof that each fictional participant meets all source inclusion criteria. |
| Within-group BMI–urate ordering | Builder-selected positive ordering with crossovers | An explicit assumption. The model specification has no evidence IDs for this joint structure. |
| Age–urate pairing, interactions and curvature | Consequences of manually paired rows | Unassessed scientific properties, not recovered findings. |
| Urate spread and bounded ranges | Builder-selected ranges | Explicit assumptions; no admitted SD, residual law or empirical bounds. |
| Exact symmetry and rounding | Manual pairing and authoring conventions | Construction artifacts, not reported population characteristics. |
| Individual row values | Fictional Agent choices under the above constraints | No individual measurement has been recovered. |

No diabetes indicator or glucose field was generated, so the source's nondiabetic selection cannot be verified in these rows. Likewise, the table does not recreate a measurement process merely by adopting its unit and assay context. Published race/sex strata are descriptive labels here, not causal biological mechanisms.

## What the numerical audit found

The original evaluation found 1.10% mean absolute relative discrepancy across the 20 supplied summaries. That statistic measures agreement with the input. It does not measure overall scientific validity.

A separate post hoc audit of the frozen rows found the following. Correlations below are descriptive outputs of this constructed table; there is no admitted empirical reference for their correctness.

| Published stratum | Fictional n | Within-group BMI–urate Pearson r | Age–urate Pearson r | Generated urate SD | Withheld source SD |
|---|---:|---:|---:|---:|---:|
| White men | 38 | 0.8152 | 0.4246 | 0.8571 | 1.30 |
| White women | 46 | 0.8991 | 0.1174 | 0.9843 | 1.20 |
| Black men | 19 | 0.9013 | −0.0838 | 1.0536 | 1.50 |
| Black women | 25 | 0.9354 | −0.0582 | 1.0824 | 1.70 |

All four urate marginal value multisets are exactly mirror-symmetric about the supplied group means, including repeated-value counts. Thus every noncentral value has a balancing value on the other side of the mean; values at the center remain unchanged under reflection. This accounts for the exact supplied means. It is not evidence that actual urate distributions are symmetric.

The four urate SDs are all below the withheld source values, with average relative discrepancy 29.53%. These are internal same-paper checks, not independent target validations. They show a limitation in dispersion for this construction; they do not establish that every direct Agent generator underdisperses or that a positive BMI association is necessarily false.

There are no duplicate joint rows after excluding identifiers. That rules out simple repeated-record copying in this table, but does not establish realistic diversity. The assumption-selected BMI relationship is strong even without duplicates.

The post hoc auditor independently recomputed the previously reported OLS model `urate ~ age + BMI + male + Black`: raw BMI coefficient 0.120103 mg/dL per kg/m², age coefficient 0.008397 mg/dL per year, and descriptive R² 0.873877. The R² describes predictability inside the authored table, not clinical prediction accuracy or a successful comparison against real data. Numerical recomputation is not scientific validation.

## A real paper does not support every generated relationship

The original article contains an adult standardized BMI–urate coefficient of 0.322 in Figure 2, adjusted for age, race, sex, smoking and alcohol. That result was excluded from the screened builder packet. It cannot be cited retrospectively as the evidence the builder used, and it cannot be numerically compared directly with the raw-scale coefficient 0.120103 from a model lacking smoking and alcohol.

The source review can establish that the article discusses a positive relationship. It cannot establish that the table's much more specific within-stratum correlation strengths, age patterns, residual spread or interactions are correct. Nor does an unreported relationship imply independence. A justified modeling assumption remains an assumption until it is constrained or independently checked.

## What this means for the project

The fair interpretation is that M15-A exercised the direct-output interface under a deliberately limited marginal-evidence task. It did not test the full intended contribution: constructing reusable analytical data from multiple studies' joint and conditional evidence. The task's restrictions matter. We should not blame the Agent for failing to retrieve relationship evidence when retrieval was forbidden, nor infer the whole method's failure from this pilot.

The appropriate next design, if pursued, is to let a fresh builder obtain approved evidence for a small number of scientifically relevant relationships and their conditions, record how it uses each one, and state what remains unspecified. Evidence may support a reported conditional association, a justified derivation, or a declared sensitivity assumption; every individual simulated value does not need a patient-level citation. Additional unrelated papers would not resolve the missing joint structure.

Before another validation, freeze the new evidence packet, construction and analysis questions. Check whether one frozen output supports compatible analyses in measured data, while retaining some analyses or a separate target for evaluation. Agreement with directly supplied source statistics is a construction check; agreement in a new target is a transfer check; agreement on unsupplied analyses is a reuse check. These answer different questions. Supplying every eventual answer and measuring its reproduction would not test analytical reuse.

If relation or variability evidence remains insufficient, report a range of explicitly assumed constructions and which conclusions change across them. Do not silently treat a single preferred pairing as a population fact. Such sensitivity output is still not a statistically calibrated probability distribution without further justification.

## Integrity and audit scope

Initial and final CSV SHA-256 both remain `3e95264632fc2e9fd4e022147724b028c06c105eea753bee30eff4e435c915fb`, unchanged before and after this audit. No old target, frozen candidate, protocol or feedback was altered. No results from this audit were sent to the original builder. The numerical diagnostics are explicitly post hoc; they are not newly declared successful endpoints of the original experiment.

Independent original-source review and numerical diagnostics are retained locally in `work/m15a_direct_rows_2026-10-30/evidence_basis_audit/`. Aggregate-only copies accompany this report in `reports/m15_evidence_basis_audit_2026-10-30/`. Generated rows and original article XML remain local. The numerical audit script expects its original local work-directory layout; its exported copy is for inspection and requires the original local files to rerun.

This audit supports a limited positive statement—published summaries genuinely guided part of the construction—and a clear unresolved requirement: the dependence and variation needed for scientific analysis still require evidence or independent evaluation. It does not authorize or perform another generation run.
