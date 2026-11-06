# KDD nearest-method comparison: evidence to analyzable cohorts

5 November 2026. **Design v1; implementation and execution release pending.** This document selects the scientific question, comparison, cases, endpoints and bounded run plan. It does not report a new experiment, reopen an old generator, or authorize an unreviewed implementation as a faithful published baseline. The machine-readable contract separates design decisions from the remaining release gates.

## 1. Scientific question and contribution

Given the same biomedical research request and the same externally published evidence, how do two Agent-based construction strategies turn that information into complete virtual data, and which requested scientific analyses do their outputs support?

The proposed contribution is an operational route from study-qualified evidence to a joint generating law and analyzable data. A meaningful comparison must examine both the resulting analyses and the consequential construction choices. It is not a contest against every possible hand-designed statistical model, and a direct-analysis Agent does not produce the data product being studied.

The primary comparator is **LLMSynthor-E: an independent paper-based LLMSynthor reimplementation with a declared biomedical evidence-to-macro intake**. Our arm is **EVC: the existing evidence-qualified Agent law-construction workflow, cross-task v1, with fixed curated evidence**. Both use the same authorized LLM service, research questions, source packet and population constraints. Different representations and native update procedures are allowed.

This is a comparison of complete workflows under matched information, not an isolated causal test of an evidence-interpretation component. LLMSynthor-E is a domain adaptation; it must not be labelled the authors' official code, their published numerical reproduction, or the unmodified original method. Both arms use established numerical samplers and meaningful LLM decisions.

The [KDD Research call](https://kdd2027.kdd.org/research-track-call-for-papers/) includes general data-science methodologies, with eight content pages under the currently posted rules. This experiment is intended to strengthen the general evidence-to-data construction claim. No new clinical discovery, model training or universal superiority claim is required by this design.

## 2. Why these comparators

| Method | Role in this unit | Reason and boundary |
|---|---|---|
| LLMSynthor-E | Primary new comparison | Closest aggregate-to-micro-record strategy; preserves LLM dependency selection, optional missing-joint inference, proposal/count generation, cumulative feedback and sampling. Its official repository currently contains documentation/images only. |
| EVC cross-task v1 | Our matched new runs | Agent derives numerical evidence uses, authors a joint law, receives permitted checks and retains/revises within the existing scientific workflow. New episodes use the method specification, never old winning laws. |
| G-Sim–ES, summary adaptation | Specified secondary option; not scheduled in this first unit | Its structure search and numerical calibration are relevant, but the released trajectory/oracle environment is not our evidence interface. The existing CHNS supplied-summary packet is a clearer matched setting if generator-search/calibration becomes a headline claim. |
| Existing prescribed statistical constructions | Retained historical context | The CHNS rich-summary comparison was already completed on 3 November and achieved close reconstruction. Do not repeat it or silently call it Filshtein/SynthIPD. |

SPADA and microdata-trained tabular generators are not primary controls for an input regime without individual records. SynthIPD's survival/KM task is different. These are scope decisions, not empirical failures of those methods. G-Sim can use aggregate constraints in principle; it is not excluded as microdata-only.

Primary evidence and implementation audits: [LLMSynthor](LLMSYNTHOR_IMPLEMENTATION_AUDIT.md), [G-Sim](GSIM_IMPLEMENTATION_AUDIT.md), and [local readiness](LOCAL_READINESS_AND_PROTOCOL_REVIEW.md). The latter's preliminary 120-call budget suggestion is superseded by Section 7 below; it would not preserve the Appendix-A LLMSynthor schedule.

## 3. Small, scientifically relevant task set

Use the already admitted **ENSANUT2018 glycemia** and **Turkana lipid** requests. These were selected for readiness, distinct measurement/analysis requirements and existing endpoint contracts; their previous favorable and unfavorable outcomes are already known at project level. No new family, raw-data download, reference fit or outcome-driven case selection is needed.

| Request | Complete generated schema | Three primary analyses, unchanged |
|---|---|---|
| ENSANUT2018 | Age, recorded sex, BMI, glucose, HbA1c and row identifier | HbA1c age effect adjusted for sex/BMI/glucose; BMI effect adjusted for age/sex; BMI effect additionally adjusted for glucose |
| Turkana | Age, recorded sex, BMI, total cholesterol, HDL and identifier | Age/sex-adjusted BMI effects for HDL and TC; residual TC–HDL Pearson correlation after age/sex/BMI adjustment |

Every final table has 3,000 fictional rows and no individual construction inputs. Full formulas, units, weights, centering, eligibility and diagnostics are inherited from the pinned request and endpoint contracts, not re-created from endpoint names. HbA1c effects use percentage points per decade or per 5 kg/m²; lipid effects use mg/dL per 5 kg/m² after the existing mmol/L conversion.

For ENSANUT, preserve 375 rows in each of the eight admitted sex-by-age cells. These are requested population quotas, not learned clinical relationships. Both methods receive exactly these final quotas. LLMSynthor-E uses an explicit, outcome-free round schedule: the first 96 rounds cycle through the eight cells twelve times, adding 30 rows in the designated cell; the last four rounds add 15 rows in each of two successive cells. Each cell therefore receives 360 + 15 = 375 rows, and a round requires at most two demographic cells, leaving room for its five proposals. Proposals remain within a scheduled cell; the Agent chooses all biomarker intervals and how counts are divided among its within-cell proposals. Validators reject invalid allocations rather than edit biological values. This task adapter constrains demographic scheduling, not biological associations, and must be disclosed as an adaptation. It avoids an impossible last round with eight nonempty residual quotas but only five proposals. For Turkana, preserve the existing eligibility and coding; do not add new fasting, disease or TC-versus-HDL exclusion rules.

Preserve all 28 ENSANUT secondary diagnostics and all 23 Turkana diagnostics. Cached references exist for all 31 ENSANUT outputs and only five Turkana outputs: its three primary endpoints and two sample SDs. Other Turkana diagnostics remain generated-only. This missing coverage is not repaired by inventing new reference values.

## 4. Information equality and the difficult interface

### Common, outcome-free preparation

Build new clean input folders from the original curated-source manifests and original request files. Do not expose old author folders, decisions, programs, generated tables, feedback histories or result reports. Preserve source population, units, measurement method, statistical operator, adjustment set, estimate, uncertainty and provenance. Common preparation may transcribe/parse available facts and explicit unit conversions; it may not choose a joint family, complete an unknown correlation, infer target histograms or import the old target results.

Both arms can see all three analysis questions. They receive the same available source material and task metadata, including uncertainty and limitations. This controlled comparison has no new retrieval for either arm, so source acquisition does not confound generation. This restriction does not remove retrieval from the broader system or assert that unknown scientific questions must be hidden.

Historical target aggregates remain outside all author input and feedback. They are read by evaluation only after every scheduled episode has terminally closed. This preserves an operational separation but does not reset project exposure; these are developmental comparisons, not new clinical confirmation. A fresh context alone is not filesystem isolation. The implementation review must describe the actual read controls rather than claim stronger isolation than is implemented.

### LLMSynthor's input adaptation must do real scientific work

The [v4 paper](https://arxiv.org/html/2505.14752v4) supplies a general aggregation abstraction but demonstrates frequency vectors, discretized margins and contingency tables. A published adjusted slope is not already a target contingency table, and the CHNS R30 packet is not a native frequency packet.

LLMSynthor-E therefore uses a generic, same-backbone intake to interpret the shared evidence and propose its macro targets/bin definitions. Any source-to-target transfer, moment-to-histogram conversion or missing joint table is marked as a model assumption with its derivation. The optional missing-joint route is enabled; it is not disabled to weaken the comparator. Source statements may remain contextual or unusable rather than being silently rewritten.

This intake cannot call our law generator, use our completed copula/covariance, or use our generated rows to manufacture its macro targets. It cannot use hidden target quantiles for bins or target participant records for sub-bin frequencies. Each inferred macro receives provenance (`reported`, `derived`, or `assumed`) and a target-population interpretation. Matching an assumed macro is model self-consistency, not validation of its underlying population assumption.

Each LLMSynthor proposal round works from its own available/frozen macro values and matching operators. Newly inferred joint targets may be introduced within the declared budget, with versioned provenance; every empirical, derived and assumed numerical target is immutable after admission. Inference of a new numerical target receives only the admitted evidence, schema and already admitted targets in a separate input context, never current synthetic frequencies or evaluation results. Validate nonnegative normalized tables and compatibility with their declared margins and population quotas. A failed inference may be repaired within its fixed budget; after the 20 inference-call allowance is exhausted, an unsupported group is excluded as permitted by the paper, with the exclusion recorded. Do not fill missing tables using current rows or silently relax an admitted target. The deterministic checker validates declared units, types and definitions. It does not certify transfer or convert the same target-context statistics into a source-population replay.

EVC retains its numerical evidence-use interface and `semantic_feedback_v1`. Its last study had 132 unavailable source checks, so this plan cannot promise an already functioning numerical source-calibration oracle. Undefined operators remain unavailable in either arm. Numerical checks against a stated assumption remain labelled as such.

### What this comparison can attribute

The main result is an end-to-end comparison of evidence-to-law construction against evidence-to-macro/proposal construction. It includes each arm's evidence translation choices. It cannot isolate the sampler, retrieval, feedback or provenance ledger as the cause of a difference.

A later **common, independently prepared macro packet** could isolate downstream construction under the same numerical constraints. That is a separate ablation, not a mandatory new arm here; its targets must not be derived from our fitted model or optimized against these evaluation results. G-Sim with our source-qualified operators would similarly test shared-operator downstream search, not independent upstream translation. Neither extension starts automatically.

## 5. Fidelity before performance

No biomedical ranking is allowed until a reviewer signs the paper-to-code fidelity map. The official LLMSynthor repository at audited commit `92e443f93c6edecc0fa9ca3045d4204da7d42aa5` has no algorithm implementation or software license; this is an original implementation of the described ideas, not copied unreleased software.

The first implementation milestone uses invented, abstract categorical and bounded continuous fixtures with explicit marginal/contingency tables. It checks arithmetic, source access, schema, cumulative updates, row budgets and reproducible RNG, not biomedical accuracy. A scripted 100-round trace must exercise the full controller; at most two short live fixture episodes (three proposal rounds each) check actual model-response parsing and cost instrumentation. At most 24 logical model requests across these short fixtures, including grouping/intake/repairs. These outputs cannot be counted as patient validation or included in the main 20-table result.

Required fidelity decisions and checks:

1. Preserve LLM-selected groups, optional missing-joint approximation, category/range/count proposals, within-range sampling and append-only cumulative records. Do not replace this with a fitted copula, row-by-row chat generation or post-hoc regression calibration.
2. Compute frequency discrepancy from the entire cumulative dataset using exactly the admitted bins; handle empty mass and parent/sub-bin totals explicitly. Positive deficits guide addition; excess mass is not removed.
3. Do not add best-checkpoint selection, deletion, target-based rollback, outcome-based sample replacement or optimization of proposal counts against held-out results.
4. Resolve the v4 prompt boxes against Appendix C before release. The cached v3 prompt and v4 appendix differ/are underspecified on payload schema and proposal count. A typed JSON schema is an implementation choice and must be recorded.
5. For the primary declared setting follow Appendix A's 100 proposal rounds, at most five proposals and up to three selected variable groups per round. Group inference repeats each round. Algorithm 1's once-per-episode grouping remains a documented publication ambiguity; do not silently switch schedules after results.
6. Use 30 newly sampled rows per round so 100 rounds produce the requested 3,000 rows. The Agent allocates these counts among its proposals subject to the ENSANUT demographic schedule in Section 3. This row schedule and quota handling are biomedical task adaptations because the paper does not specify its batch-size rule sufficiently. Test exact terminal quotas and adversarial invalid count/range proposals in the scripted fixtures. No final downsampling or count optimization hides these choices.
7. Resolve integer ages, interval edges, finite values, units and recorded sex codes. Independent uniform draws within a continuous box are a declared reconstruction choice, not verified author-code behavior. Marginal independence within a box does not imply independence of the mixture across proposals.
8. Bounded syntax/count repair may fix malformed responses using only the public contract and that response. Scientific reviewers must not prescribe a missing target slope, sign or residual correlation. Both arms get the same review remit and at most two pre-construction scientific review exchanges; all interventions are logged.

An implementation failure stops or repairs this engineering phase before the biomedical run. It is not an empirical failure of LLMSynthor. If prompt/input fidelity cannot be established, report a limited reproduction and omit the comparative headline rather than inventing a weak baseline.

## 6. Native episodes, not artificial replications

**Main design: 2 requests × 2 workflows × 5 fresh end-to-end episodes = 20 scheduled final tables, 60,000 fictional rows if all succeed.** Each table is analyzed on its three case-specific primary estimands: 60 scheduled primary estimates. This is two reference populations, ten episodes per method, and five computational repetitions per method/request—not 20 clinical cohorts or 60 independent findings.

LLMSynthor's final output is the actual cumulative table produced by its adaptive episode. Replaying one frozen set of boxes with three seeds would change the primary method and would not supply three independent constructions. Consequently each arm returns one primary final table per fresh episode. EVC keeps its normal initial law, one trial and at most one source/diagnostic-based revision; it then makes one preassigned final delivery. Its five episodes are fresh law constructions, not reuses of the old six laws.

No current workflow is limited to the other workflow's native iteration count. In particular, LLMSynthor is not truncated to EVC's single revision. The scheduled episode order alternates methods within task/replicate blocks and alternates the two requests. Saved model responses and RNG seeds support replay. Identical seed labels would not establish common random numbers across different samplers, so no such paired-sample claim is made.

All old frozen models, results and target fits remain unchanged. This is a separate versioned comparison with pinned method instructions, generic adapter and new episode controller. Historical graphs may provide context but do not become matched concurrent arms.

## 7. Resource plan and operational release

The proposed primary LLMSynthor schedule has **1,000 proposal calls plus 1,000 group calls across its ten episodes**, before input adaptation, missing-target inference or repairs. Five proposals in a response are one call, not five. A 10-round smoke test cannot be used to claim that a 100-round competitor is worse.

Use these design ceilings per episode: 100 proposal calls, 100 group calls, two intake calls, up to 20 missing-joint inference calls, up to ten schema/count-repair calls, and two scientific-review requests: **234 logical model requests**. Review is included, not a free unmetered allowance. EVC retains its existing scientific procedure under the same overall ceiling; unused calls are not spent on new candidate search. These are common ceilings, not a claim of equal consumed compute. Record actual calls, available token accounting, input preparation, sampling, inspection, failures and elapsed time by phase.

Before execution release, the dispatcher must identify the model/service, exposed version and inference settings; demonstrate fresh context boundaries; enforce call limits; and meter visible input/output usage. Use a common total visible-output ceiling of one million tokens per episode as a safety bound; published proposal/group caps and EVC code-response caps are separately declared. If hidden reasoning/input tokens or costs are unavailable, report them unavailable and make no equal-compute or total-cost claim. A host conversation turn is not automatically a measured provider API call.

The short fixture checks establish latency and validate the route. A bounded active-time limit is then fixed in `EXECUTION_RELEASE.json` before any biomedical episode; the gate cannot be satisfied by leaving a timeout unspecified. No new paid endpoint, model training, model-weight download or HPC job is authorized by this design. If the existing service cannot support the repeated-call route, save the implementation and its specific resource limitation; do not bypass the restriction, quietly reduce rounds or call manually invented responses actual model outputs.

Numerical sampler/evaluator work is CPU-scale for these tables; no GPU/HPC requirement is established. Model calls, faithful implementation and evidence review are the primary anticipated costs. No dollar or speedup estimate is asserted before measurement.

## 8. Analysis and quality assessment

The final data are the object of evaluation. The analysis questions are known to both methods; target measurements/aggregates outside the allowed packet are not construction feedback in this information condition. A separate summary-assisted condition would legitimately provide them but would answer a different reconstruction question.

### Primary report

For each of the six primary estimands, show every episode's estimate in its original units alongside the cached sample reference and available uncertainty. Report the mean/median absolute discrepancy and range across the five episodes within each method/request, plus signed discrepancies. An endpoint-level difference between methods is descriptive; do not combine unrelated units into one quality score, use percent errors near zero, or treat constructed rows as independent evidence of method performance.

Record direction agreement as supplementary interpretation, alongside effect magnitude and uncertainty. The TC reference sensitivity interval crosses zero, so agreement with its positive point is not recovery of an established positive population effect. Formal equivalence requires a justified, prospectively chosen scientific margin; none is invented in this study. No p-value-matching target or universal pass band is used.

### Completeness, variation and joint structure

Retain every inherited diagnostic. Core companion views include HbA1c SD and residual RMS; TC/HDL sample SD; and the residual lipid relationship already in the primary set. Row validity, exact/rounded duplicate rates and occupied proposal/bin cells can be generated-only quality diagnostics with definitions fixed before execution. Finite observed variation alone does not prove realistic diversity. No new patient-based diversity reference or classifier two-sample score is manufactured from aggregate-only access.

The existing CHNS real-real resplit distribution is not a transferable tolerance for ENSANUT or Turkana. Their available reference bands provide their own limited context; a sample reference is not known population truth. Reference uncertainty does not erase material discrepancies. Unavailable target diagnostics remain unavailable.

### Failures and independent recomputation

Report all 20 slots, including failures, invalid schema, unavailable analyses and budget exhaustion. Show the denominator beside each summary over evaluable outputs. An ineligible method/adapter is not assigned a fabricated infinite clinical error or called inferior; unsupported interfaces and data-quality failures have separate statuses. No replacements or favorable seeds are selected.

After all episodes close, use the existing formulas to calculate 310 glycemia and 260 lipid analysis/diagnostic values if all outputs are valid: **570 total, 360 with matching cached references and 210 generated-only**. Independently recompute the final-data statistics and reference mappings. These counts are output accounting, not sample sizes for hypothesis tests. All real/generated individual tables remain local.

## 9. Result interpretation before seeing outcomes

| Observed outcome | Supported interpretation / decision |
|---|---|
| EVC improves requested conditional/joint analyses with comparable spread | Evidence of a useful workflow difference on these requests; inspect derivations to propose explanations, without claiming a proven component mechanism or universal superiority. |
| Both produce similar useful analyses | Valuable matched evidence that the task is feasible by both approaches. Report quality/cost/assumption differences actually measured; do not claim an accuracy advantage. |
| LLMSynthor-E is better | Preserve the result and assess its proposal sampler as a possible system component in future work. Do not alter this frozen comparison to recover a win. |
| Marginals fit but conditional/joint results differ | Report analysis-specific usefulness and unresolved dependence; good marginal fit does not certify all analyses. |
| Both are weak or source constraints unavailable | Attribute only what the evidence supports. Distinguishing missing evidence from a mechanism limitation may need the separately declared common-macro diagnostic; it is not automatically launched. |
| Reimplementation/adaptation is not credible or fails technically | Close the implementation claim or report a restricted result; no ranking against the published method. |

Finish with a six-panel effect figure, a compact spread/joint-structure display, and a table of information access, implementation identity, completion, actual calls and human/host interventions. A trace may illustrate a frozen, ordinal-selected construction. Do not choose the prettiest model or add a new endpoint after results.

## 10. Immediate implementation order and stop rule

1. Finish v4 prompt parity and the original LLMSynthor core on invented native fixtures.
2. Build generic evidence intake and source-provenance records for the comparator; independently review scientific assumptions and the distinction between empirical and inferred targets.
3. Derive a new native-episode controller, cumulative-output receipt path, fresh-context dispatcher and all-episode evaluator. Keep the old hard-coded six-author/three-seed controller frozen.
4. Bind equal curated packets and all exact code, prompt, input, schema, model, timing and reference hashes in a reviewed execution release.
5. Run the 20 preassigned episodes; close all slots; evaluate once and independently recompute. Preserve unfavorable outcomes and then stop this unit.

No new case, G-Sim run, shared-macro ablation, new source search, extra seed or method change is triggered by an unfavorable result. A material technical change before target evaluation is versioned and reviewed; after any comparison outcome is revealed, this study closes to scientific tuning. The next decision is whether to integrate these results into the KDD draft, simplify the contribution, or design a separately justified extension.

## Sources and local anchors

- [LLMSynthor v4](https://arxiv.org/html/2505.14752v4): §3, Algorithm 1, Appendices A/C; [official repository](https://github.com/YihongT/LLMSynthor).
- [G-Sim official ICML paper](https://proceedings.mlr.press/v267/holt25b.html) and [official code](https://github.com/samholt/generative-simulations).
- [Completed cross-task protocol](../evidence_use_cross_task_2026-11-05/PROTOCOL.json), [endpoint contract](../evidence_use_cross_task_2026-11-05/ENDPOINT_CONTRACT.json), [closed results](../evidence_use_cross_task_2026-11-05/RESULTS.md).
- [Completed CHNS statistical-summary comparison](../summary_comparator_2026-11-03/RESULTS.md), [exposure registry](../../docs/DATASET_EXPOSURE_REGISTRY.md), [current manuscript](../../manuscript/DRAFT_v0_15.md).

The companion audits preserve exact code/source-access limitations. This protocol contains proposed decisions and expected run counts, not new performance results.
