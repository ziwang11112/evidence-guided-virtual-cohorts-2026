# P1 results: original papers to analyzable virtual cohorts

17 November2026, America/Chicago. Status: closed after all six scheduled construction sessions and18 final tables. No replacement author, target-feedback revision, new dataset, training or HPC was used.

**Main finding:** with an original-paper entry point, the Agent itself can extract and compose numerical evidence, choose a scientific probability law and deliver a runnable whole-cohort generator. In this batch the generated BP data support approximately the same age/sex-adjusted BMI associations as the measured reference. Iron-state associations are positive but substantially weaker; source fidelity does not establish target fidelity.

## Frozen experiment and actual execution

Two existing cases, three fresh GPT sessions each, one final law per session and three final seeds17121/17123/17127. The BP schema has six columns and3000 rows; the iron schema has three columns and5000 rows. No target individual inputs are supplied. The final inventory is18 tables and72000 virtual rows, not72000 independent real participants or18 independent modeling decisions. The inferential replication unit is the construction/session within a case; final seeds only describe sampling from that fixed law.

The Agent receives the research request, output contract, exact desired analyses and access to a complete original XML or PDF-text paper. It may search additional literature, decide how to model the data, submit code and parameters, run a generated-only inspection, and revise once if needed. All six chose to retain their first model after one trial. Root added an original-paper reader and estimator routing, audited the interface, and froze the implementation, prompts, source bytes and analysis definitions before any paid construction. Root supplied no numerical evidence card, target slope, target mean, residual correlation or preferred generator family.

All six candidates and their histories were sealed before the final draws and target comparisons. The same established analysis estimators are used for generated data and the existing measured references. These are already exposed sample estimates, not known population truth or fresh clinical holdouts. No equivalence margin was chosen after observing the results.

## Complete result profile

Values below are means of the three fixed-seed results per author. The complete33 author-endpoint and99 seed-endpoint records, including all diagnostics, are retained in `analysis/`. Fractions are on0–1 scale. BP slopes are mmHg per5kg/m² BMI adjusted for age and sex; iron OR uses Hb<12g/dL and raw ferritin<15ug/L.

| Case / analysis | Author 1 mean | Author 2 mean | Author 3 mean | Measured sample reference |
|---|---:|---:|---:|---:|
| PNS / bmi_sbp | 3.64232 | 3.40248 | 3.80402 | 3.52400 |
| PNS / bmi_dbp | 2.28505 | 2.40179 | 2.35038 | 2.25995 |
| PNS / residual_correlation | 0.77869 | 0.77220 | 0.78133 | 0.71718 |
| PNS / sbp.sd_population | 20.00347 | 19.70252 | 19.56612 | 18.19157 |
| PNS / dbp.sd_population | 11.56844 | 11.56909 | 11.47171 | 11.09414 |
| PNS / sbp_below_dbp_fraction | 0.00000 | 0.00000 | 0.00000 | 0.00000 |
| IRON / odds_ratio | 7.14134 | 6.34756 | 6.62476 | 17.78978 |
| IRON / joint_prevalence | 0.05180 | 0.04673 | 0.05847 | 0.07630 |
| IRON / spearman | 0.32886 | 0.19673 | 0.30733 | 0.39844 |
| IRON / low_hb_fraction | 0.10660 | 0.08807 | 0.11727 | 0.15240 |
| IRON / low_ferritin_fraction | 0.15680 | 0.18513 | 0.17487 | 0.12153 |

### What the analyses support

- **BP associations:** author means for BMI–SBP are3.402–3.804 versus reference3.524; BMI–DBP2.285–2.402 versus2.260. This supports approximate reproduction of these associations under the specified analysis, not a formal equivalence conclusion or intervention effect.
- **BP joint dependence and spread:** residual correlation0.772–0.781 exceeds reference0.717. SBP SD19.566–20.003 exceeds18.192; DBP SD11.472–11.569 exceeds11.094. All BP records respect SBP>DBP. Useful slopes do not imply the whole joint distribution is recovered.
- **Iron associations:** OR6.348–7.141 versus17.790 preserves a positive association but materially understates its strength. All authors calibrate to the same source crude OR6.653; this is a transparent source-transfer assumption, not evidence that the target OR should equal it.
- **Other iron analyses:** joint-low prevalence4.673–5.847% versus7.630%, rank correlation0.197–0.329 versus0.398, low-Hb prevalence8.807–11.727% versus15.240%, and low-ferritin prevalence15.680–18.513% versus12.153%. The common threshold constraint does not determine these other analyses. Supplemental marginal evidence and different model families do not remove their uncertainty.

No binary overall dataset-quality pass is assigned. The measured references have sampling uncertainty; proximity is encouraging for a specific analysis, while persistent larger discrepancies remain visible. The preceding P0 matched-size real–real diagnostic concerns the lifestyle case and is not silently transferred as an acceptance threshold for these BP/iron tasks.

## Evidence and code findings

All three BP authors recover the original covariance matrix and derive an age/BMI partial covariance instead of simply naming a paper. All three iron authors correctly collapse an eight-row table, distinguish crude from adjusted OR, and flag source unit/interval ambiguities. They then choose different supplementary literature and assumptions. The final programs implement these decisions. The [source/model audit](SOURCE_MODEL_AUDIT.md) links the literal sources, transformations and remaining assumptions.

One same-target-family search preview reached PNS_A2, containing study identity/demographics and a qualitative topic but not the requested target estimates. It was explicitly excluded by the author; exposure remains recorded. Other historical-survey previews are also retained. No target dataset or aggregate answer file was sent to the API. This experiment therefore tests controlled original-paper modeling capability with imperfect source screening, not pristine unseen-population performance.

## Validation and cost

- All18 final isolated executions succeeded; zero missing analysis slots.
- All99 endpoint values agree with the separately implemented QR/count/rank computation; maximum absolute difference7.55e-14. This verifies numerical implementation, not biological truth.
- 1076 prior protected files are unchanged; all frozen current inputs and candidate bindings verify.
- Model requested/returned:`gpt-6.1-sol`;142 calls; estimated token-tariff costUSD1.5113403; zero unknown-usage calls. This is recorded tariff accounting, not an invoice. The precommitted maximum wasUSD24.
- All model prompts, responses, tool calls, code/spec/notes, hashes and execution receipts remain local. Final individual virtual rows and full third-party texts are not public-report contents.

| Session | Model calls | Literature queries | Download attempts charged | Candidates / trials | Estimated USD |
|---|---:|---:|---:|---:|---:|
| P1_IRON_A1 | 21 | 4 | 2 | 1 / 1 | 0.1973 |
| P1_IRON_A2 | 22 | 6 | 0 | 1 / 1 | 0.2134 |
| P1_IRON_A3 | 23 | 6 | 2 | 1 / 1 | 0.2480 |
| P1_PNS_A1 | 28 | 7 | 2 | 1 / 1 | 0.2903 |
| P1_PNS_A2 | 25 | 5 | 2 | 1 / 1 | 0.3127 |
| P1_PNS_A3 | 23 | 5 | 2 | 1 / 1 | 0.2497 |

## KDD contribution and next decision

This experiment supports the **Agent's actual evidence interpretation and model authorship**, in addition to the earlier fixed-packet composition controls and P0 same-analysis utility context. The useful claim is an evidence-to-analyzable-data capability with analysis-specific successes and traceable assumptions. It does not establish workflow superiority, revision benefit, all-analysis utility, human-level extraction accuracy, or reliable new-population transport.

The next bounded item remains P2: inspect a faithful LLMSynthor comparison in a compatible information/output setting and run it only after the adaptation and analysis are specified. Do not keep tuning these six generators against the now-known reference. A cross-model extension is conditional on what P2 can resolve, rather than expanding models/data by default. The unchanged v0.33 manuscript has a [prepared insertion](MANUSCRIPT_INSERT.md); no new reading edition is silently substituted.

Artifacts: [offline visual report](report/index.html), [protocol](PROTOCOL.md), [source/model audit](SOURCE_MODEL_AUDIT.md), `analysis/author_results.csv`, `analysis/seed_results.csv`, `analysis/COSTS.json`, `audit/TRACE_SUMMARY.json`.
