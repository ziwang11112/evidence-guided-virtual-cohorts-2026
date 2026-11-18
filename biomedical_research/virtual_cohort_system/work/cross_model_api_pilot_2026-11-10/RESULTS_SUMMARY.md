# First twenty API constructions: results and interpretation

10 November 2026. This is a completed, same-information developmental pilot, not a new clinical confirmation. Model authoring and numerical evaluation are now both observed, rather than proposed.

## What was actually done

Two whole-cohort tasks (PNS-context blood pressure; Turkana-context lipids), five model configurations, and two fresh authoring requests per configuration/task produced **20 initial API calls**. No individual participant input was supplied. Every author for a task received identical reviewed source evidence, population/schema and three requested analyses. Models chose their own scientific structures, numerical assumptions and executable Python generators. The host did not write desired relationships into the candidates.

This controlled pilot used fixed source packets and no web retrieval or scientific feedback. It tests cross-model evidence-based construction, not an advantage of the full adaptive research loop. The two GPT configurations are an additional within-provider comparison; they do not constitute two independent providers.

After all calls closed, **14 complete candidates were sealed and 6 incomplete responses retained as failures**. No repair call, replacement call or manual scientific edit occurred. All 14 candidates ran successfully under the existing isolated WSL/bubblewrap backend, at three fixed seeds and 3,000 rows per draw: **42 tables and 126,000 synthetic rows**. These rows are Monte Carlo draws from 14 authored laws, not additional clinical evidence. All 60 planned seed slots remain in the report: 42 complete and 18 unavailable because their six constructions were not delivered.

The same predefined adjusted regressions, residual correlations and diagnostics were applied to every delivered table. Existing real-data aggregate references were used only after construction closure. They were never sent to the authors or used to change a candidate. Original clinical rows were not read or refit in this unit.

## Delivery and cost

| Requested and returned API model | Complete constructions / 4 | Successful tables / 12 | Usage-derived cost estimate, USD |
|---|---:|---:|---:|
| gpt-6-astra | 4 | 12 | 3.258792 |
| gpt-6.1-sol | 4 | 12 | 0.5778412 |
| deepseek-v4-pro | 4 | 12 | 0.45008392 |
| claude-fable-5-2 | 2 | 6 | 5.521792 |
| gemini-4-carbon | 0 | 0 | 1.398488 |
| **Total** | **14 / 20** | **42 / 60** | **11.20699712** |

All provider requests returned recorded usage; no unknown-cost reserve remains. These are published-tariff estimates, not invoices or a verified account-balance debit. DeepSeek uses its conservative peak tariff. OpenAI's total was USD3.8366332. All requested and returned model identifiers matched, but returned aliases are not proof of immutable model-weight snapshots.

The six incomplete responses were four Gemini calls and both PNS Claude calls, all ending at the 32,768-token output ceiling. Gemini reported 32,765 thought tokens and only three candidate tokens in every call. Claude's two blood-pressure outputs also exhausted the ceiling; its lipid outputs completed. These are delivery failures under the chosen HIGH/high, non-streaming configuration. Their scientific correctness is **not assessable**, and the table must not be interpreted as a general model-capability ranking. See [delivery-budget audit](DELIVERY_BUDGET_NOTE.md).

## Scientific results

Each range below is across **construction means**, where each mean uses the three predefined draws. It is not a confidence interval. Every complete construction and every scheduled endpoint is retained.

| Case and requested analysis | Generated construction-mean range | Existing real-data estimate | Supplied reference uncertainty |
|---|---:|---:|---|
| Blood pressure: BMI–SBP, mmHg per 5 kg/m² | 3.553 to 4.008 | 3.524 | Conditional row-resampling range 2.961 to 4.119 |
| Blood pressure: BMI–DBP, mmHg per 5 kg/m² | 2.684 to 3.092 | 2.260 | Conditional row-resampling range 1.931 to 2.585 |
| Blood pressure: residual correlation | 0.467 to 0.608 | 0.717 | Conditional row-resampling range 0.700 to 0.734 |
| Lipids: BMI–TC, mg/dL per 5 kg/m² | 7.835 to 10.774 | 5.683 | HC3 conditional sensitivity interval −3.754 to 15.120 |
| Lipids: BMI–HDL, mg/dL per 5 kg/m² | −1.975 to −1.202 | −4.623 | HC3 conditional sensitivity interval −8.392 to −0.854 |
| Lipids: residual correlation | 0.097 to 0.382 | 0.512 | Not available in the frozen aggregate |

The PNS uncertainty is not a design-based national-population confidence interval; the lipid intervals are conditional HC3 sensitivity intervals. Neither is a prespecified equivalence margin. The samples are imperfect references, not known population truths. In particular, the broad lipid slope intervals prevent treating point-estimate differences alone as decisive failures; the real-data TC slope interval includes zero.

**What is supported:** the delivered data can be analyzed with the requested statistical models. The blood-pressure SBP coefficient is relatively close to this reference, and all successful generated primary estimates have the same sign as their reference point estimates. Direction agreement is descriptive, not evidence of equal effects or universally preserved scientific conclusions.

**What needs attention:** residual dependence is below the reference point in all six blood-pressure constructions and all eight lipid constructions. For lipids, GPT and DeepSeek yield construction means 0.097–0.151; Claude yields 0.333 and 0.382, closer to the 0.512 reference but still below it. Thus the cross-model observation is not that every model makes the same assumption: the chosen dependence structures differ substantially.

Dispersion is **not universally underestimated**. Lipid TC SDs are 30.60–41.59 versus 42.85, and HDL SDs are 11.94–14.87 versus 20.18. In contrast, blood-pressure SBP SDs span 15.17–22.79 around the 18.19 reference, and DBP SDs span 9.74–11.39 around 11.09. The earlier broader conjecture of universal dispersion shrinkage must therefore be narrowed.

Physical component checks found 47 SBP<DBP rows among 54,000 blood-pressure draws and 197 HDL>TC rows among 72,000 lipid draws. These were retained, counted and analyzed without silent correction. The maximum per-table rates were 0.6% and 0.9667%, respectively. Successful program execution does not certify physiological plausibility.

## What this says about the research story

This pilot extends the dependence-attenuation observation beyond a single inherited host-model backend: it recurs among successful API constructions from several model families on two fixed evidence packages. That is a useful, auditable empirical pattern. It does not establish a universal LLM bias, identify its sole cause, or separate evidence limitations from transfer, covariance interpretation and generator transformations.

The parameter-origin review remains important. All six successful PNS authors adopt the same source BMI coefficients (INTERSALT, converted by a factor of five); agreement across authors does not create independent clinical evidence. Their dependence and scale constructions differ. In the lipid audit, positive-value rejection/truncation in one generator invalidates a claim that pre-rejection slopes and residual correlation must be exact post-rejection population estimands. Consequently, “every generated statistic equals its declared parameter” is too strong. Source parameters, implied population analyses and finite generated-sample analyses must remain distinct.

No configuration is declared an overall scientific winner. For example, the Astra PNS residual correlations are closer to this reference than the other delivered PNS configurations, whereas DeepSeek's lipid TC slopes are closer in point estimate than Astra's; uncertainty and small construction counts remain material. A universal ranking or a claim that stronger models alone repair missing joint evidence is unsupported.

An informative **structural contrast** is Claude's second lipid construction: it generates HDL and non-HDL components, then forms TC as their sum. The literal zero correlation refers to HDL/non-HDL errors, while the component identity induces a TC/HDL residual correlation of about 0.38133; the realized three-draw mean is 0.38236. That construction has zero HDL>TC rows. This is an actual agent-chosen modeling decision, not host-written target fitting. It suggests a useful hypothesis about combining biochemical identities with evidence to preserve joint structure. It is not a matched causal ablation: SDs and other scientific choices also differ, and its HDL/BMI slope remains weaker than the reference point. It does not justify making this one construction the universal recipe.

## Review, artifacts and next bounded decision

- [Protocol](PROTOCOL.md), [frozen run plan](RUN_PLAN.json), and [evaluation protocol](EVALUATION_PROTOCOL.md).
- [Independent preflight](INDEPENDENT_PREFLIGHT_REVIEW.md): 14 API/packet tests and 19 deterministic execution/analysis tests passed before launch.
- [Independent actual-call audit](INDEPENDENT_CALL_AUDIT.md): all 20 requests, outputs, model IDs, fees and selected candidate bindings checked; no blocker.
- [Full endpoint report](EVALUATION.md) and [machine-readable evaluation](EVALUATION.json): all seeds, uncertainty, failures and diagnostics.
- [Independent numerical recomputation](review/INDEPENDENT_RECOMPUTATION.json): all 42 tables, primary/secondary endpoints and construction summaries agree; maximum absolute numerical discrepancy 8.35×10⁻¹⁴. Every successful construction has three distinct output hashes.
- [Costs](PILOT_COSTS.json), [scientific-results figure](SCIENTIFIC_RESULTS.png), [vector PDF](SCIENTIFIC_RESULTS.pdf), [editable SVG](SCIENTIFIC_RESULTS.svg).
- [Core parameter-origin review](provenance_review/CORE_PROVENANCE_REVIEW.md) covers all 14 delivered constructions; classification claims and independently verified mappings are kept separate.

The bounded twenty-call pilot is finished. No additional paid call or target-driven regeneration is launched. The next useful engineering step is a separately recorded, small delivery-configuration pilot for the truncated conditions (for example, MEDIUM thinking under the same evidence boundary), preserving this run unchanged. The next scientific step is to use the audited parameter/operator mappings to distinguish missing joint evidence from mathematical changes introduced by the generator. Merely generating more rows cannot resolve either problem.

Full raw API responses, candidate programs, generated tables and host-only references remain local. The authoring prompts contain published source evidence and task descriptions, not target patient data or credentials. No manuscript result or old frozen experiment was overwritten.
