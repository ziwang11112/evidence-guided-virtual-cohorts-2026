# Independent two-round alignment and denominator audit

**PASS.** The two rounds can be synthesized descriptively on aligned evidence, references and statistical operators. They cannot be treated as a larger confirmatory trial or a balanced model leaderboard. Actual source, program/specification, receipt and output hashes are recorded in `ROUND_ALIGNMENT_AUDIT.json`.

| Quantity | First round | Economy round | Combined |
|---|---:|---:|---:|
| Initial API construction opportunities | 20 | 8 | 28 |
| Dependent review requests | 0 | 4 | 4 |
| Complete initial API candidates | 14 | 7 | 21 |
| Initial candidates that produced tables | 14 | 6 | 20 |
| New revised data-law versions | 0 | 1 | 1 |
| Exact retained review products | 0 | 3 | 3 |
| Scheduled evaluation slots | 60 | 36 | 96 |
| Successful evaluation files | 42 | 30 | 72 |
| Unavailable-candidate slots | 18 | 3 | 21 |
| Execution-failed slots | 0 | 3 | 3 |
| Separate diagnostic slots, all successful | 0 | 6 | 6 |
| Distinct successful evaluation file hashes | 42 | 21 | 63 |

The **32 paid requests comprise 28 fresh initial contexts and four parent-dependent reviews**. There are 25 complete API artifacts, including the three review no-ops. The captured candidates contain **22 distinct exact program/canonical-specification combinations**, of which **21 produced evaluation tables**: 20 initial candidates and one dependent revision. These signatures identify implementations, not proven distinct probability laws. “Independent authors” must not be substituted for candidate, law-version, seed or table counts.

All **102 scheduled table slots** remain represented: 96 evaluation and six diagnostic. There are 78 successful output files, but only **69 distinct output hashes** after including diagnostics. Nine extra file instances arise from exact retained branches. Successful file instances contain 234,000 rows (216,000 evaluation); deduplicated file bytes represent 207,000 rows (189,000 evaluation). Neither row total is a count of independent clinical evidence.

The nine source/task/prompt files and host-only aggregate snapshot are byte-identical across rounds. Both use the same frozen statistical functions and runtime/worker. The stored endpoint units, reference values and uncertainty objects also match exactly. PNS uses equal-weight OLS on intercept, centered/scaled age, female and BMI, with BMI slopes per 5 kg/m² and centered residual Pearson correlation. Lipids uses the same adjustment set and common eligible rows, converts mmol/L to mg/dL by 38.67 for slopes, and retains the original positivity/eligibility rules. PNS SD uses population ddof=0; lipid SD uses sample ddof=1. HDL > TC is a diagnostic, not an inferred exclusion rule. No rows were repaired to enforce ordering.

Shared-model initial requests have identical endpoint/body settings: the same source prompt, model alias, high effort and 32,768 output ceiling. Sol, Astra and DeepSeek also retain identical published tariff parameters. The first round's persisted prompt text uses Windows line endings, but the previously audited submitted JSON input equals the same frozen LF prompt; storage-line-ending differences are not an evidence difference. Review prompts intentionally add the same initial artifact and shared review instruction, with own-generated observations added only to feedback.

The same endpoints support case-specific comparison of generated results and provenance choices across initial constructions. The three old seeds (31001/31003/31007) and three new evaluation seeds (42001/42003/42007) differ; diagnostic seeds are separately 41001/41003/41007. Repeated seeds are nested draws, not independent authors. Round 2 changes the primary focus to component consistency, so common endpoint alignment does not justify a pooled post-hoc success score. Both rounds use previously exposed aggregate references; alignment does not turn them into ground truth or fresh clinical confirmation.

Known usage-derived tariffs sum to **$14.14412666**: $11.20699712 in the first round and $2.93712954 in the second. The second round additionally retains **$0.21840852** for the transport failure with unknown usage, yielding **$14.36253518 accounted** across rounds. These are not invoices. Cache use, reasoning/output allocation, longer review inputs, model mix and unequal request counts prevent treating cost differences as matched-compute or scientific-equivalence evidence. DeepSeek uses the conservative peak tariff in both rounds.

Keep failure mechanisms separate: six first-round incomplete outputs exhausted delivery budgets; the second round adds one transport failure and one delivered program with an output-interface execution error. Neither Fable nor Carbon was tested again. Four review contexts depend on two Sol parents, and both cases actually dispatched feedback first despite planned counterbalancing. No general feedback or model-superiority inference follows.

This audit verifies alignment with curated frozen packets and completed prior audits; it is not a fresh article audit. No API, credential file, private response, clinical row, generated program execution or new statistical fit was used. Final integrated synthesis tables and prose remain subject to a separate consistency check.

## Correction to the first-round provenance review

The earlier `CORE_PROVENANCE_REVIEW.md` (line 19), `LIPID_CORE_REVIEW.md` (line 37) and associated `LIPID_CORE_REVIEW.json` wrongly said that Astra C1's Greiner `.rows` evidence pointers should have used `.records`. **That criticism is retracted.** The actual frozen author packet encodes `reported_statistics` using exactly `format`, `columns`, and `rows`; no `records` field exists. All 16 declared `.rows[i]` pointer occurrences resolve to 12 unique rows. All 12 occurrences with a declared statistic ID match the resolved ID exactly; the other four correctly identify the Uganda age median/Q3 rows.

This is an error in the previous reviewer report, not a source-pointer failure by the author. The original packet SHA-256 is `8f4686adea0ddd9e9d7f17e0c08c32ad5c7fff58f88874dd5bd85b341b4562ed`; the captured Astra C1 artifact SHA-256 is `ece8aedcbb32106f24c9e0f833443f0cb40a52637de1c4e533ab6e6c027c935f`. The JSON audit stores each pointer, its resolved row and the exact historical-report hashes. Historical audits remain unchanged for traceability. No source values, programs, numerical results or separate statistical-operator/transport conclusions are altered. This check used the admitted frozen packet and captured artifact; it was not a new original-article audit.
