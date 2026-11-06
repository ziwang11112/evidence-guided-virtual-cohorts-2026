# LLMSynthor implementation audit and biomedical comparator design

Date: 2026-11-05. Status: design and read-only verification completed; no implementation, generation, model call, experiment, new paper/data download, or new participant-level read.

## Recommendation

Use **LLMSynthor as an agentic, macro-guided whole-cohort comparator**. Its LLM selects dependencies and plans corrective proposal distributions; tools sample records and calculate feedback. It already admits multiple aggregate sources and optional inference of absent joint statistics. Our comparison cannot rest on claiming that it lacks an Agent, uses a fixed analyst-authored biological law, requires construction-time participant records, or is incapable of completing unreported dependencies.

The official release is still a documentation-only repository. Therefore the implementable next step is a **transparent independent paper-based reproduction of LLMSynthor, adapted to a frozen biomedical evidence contract**. Do not call it an official implementation, official-code adapter, or reproduction of its published numerical results. Recheck the official release before implementation and use its code if an auditable implementation becomes available.

For the existing study, the correct task is generating a complete 3,000-person cohort without individual construction inputs. Keep the published append-only procedure. Fixed-person imputation would be an unnecessary and less faithful alteration.

## Verification record

The current primary source is [arXiv v4, revised 8 June 2026](https://arxiv.org/abs/2505.14752v4), with KDD 2026 DOI [10.1145/3770855.3818965](https://doi.org/10.1145/3770855.3818965). I read its HTML methodology, Algorithm 1 and appendix prose, and compared the pre-existing [detailed v3 audit](../neighbor_deep_read_2026-10-31/llmsynthor/LLMSYNTHOR_DEEP_REVIEW.md), [combined review](../../docs/GSIM_LLMSYNTHOR_DEEP_REVIEW_2026-10-31.md), and [manuscript v0.15](../../manuscript/DRAFT_v0_15.md). The local reviews already documented optional missing-joint inference; it is not newly discovered in v4.

The [author project page](https://yihongt.github.io/llmsynthor_web/) and v4 paper link the same [official repository](https://github.com/YihongT/LLMSynthor). Current read-only API checks found:

| Item | Verified result |
|---|---|
| Default branch / HEAD | main / 92e443f93c6edecc0fa9ca3045d4204da7d42aa5 |
| HEAD commit date | 2025-07-03T01:28:04Z |
| Complete recursive tree | README.md; .DS_Store; resources/.DS_Store; resources/icon.png; resources/icon_old.png; truncated=false |
| Implementation paths | None: no generator, package, executable, config, dependency lockfile, tests, or task adapter |
| Branches / tags / releases | main only / none / none |
| License | No LICENSE file; GitHub license field null; README promises a future open-source license |
| Author release statement | README still promises code following acceptance |
| Alternate official artifact | No executable release linked by the inspected official project page |

The [pinned README](https://github.com/YihongT/LLMSynthor/blob/92e443f93c6edecc0fa9ca3045d4204da7d42aa5/README.md) retains the earlier title and three-author citation. This is a version mismatch, not grounds for questioning the reported experiments. Paper publication or a paper license is not a verified software license. No exact code path can honestly be supplied for the algorithm because none was present. [Metadata JSON](LLMSYNTHOR_SOURCE_METADATA.json) retains blob hashes, API findings and limitations.

GitHub connectors were used for repository reads. The tags endpoint was unsupported there and inaccessible through web; a small read-only GitHub API request returned an empty list. No repository was cloned. Exact v4 prompt boxes did not appear in the HTML extraction; prompt-field details below are verified from the existing local v3 text and require a v4 prompt parity check before implementation.

## Actual input contract and information boundary

The paper-level inputs are named variables and valid value descriptions, available macro-statistics, a matching aggregation operator, a discrepancy rule, iteration budget, and requested synthetic size. Record length may vary. The demonstrated numerical representation comprises categorical frequency vectors, discretized continuous margins, and joint contingency tables. The framework permits more general aggregation operators, but that does not supply an implemented biomedical regression interface. [Methodology](https://arxiv.org/html/2505.14752v4#S3)

There is **no official callable Python interface to audit**. Do not invent constructor arguments or claim that a PDF, evidence packet, regression formula, or article DOI is natively parsed by a released API.

| Information | Paper-supported role | Biomedical handling |
|---|---|---|
| Schema, category names, numerical ranges | Describes variables and admissible proposals | Preserve names, units, coding and eligibility |
| Explicit marginal / joint frequencies | Numerical alignment targets | Use only when available and semantically compatible |
| Practitioner-specified joint statistics | Allowed target source | Preserve how they were obtained; no hidden target answers |
| Missing dependency structure | LLM selects related variable groups | Keep this LLM decision |
| Missing numerical joint statistics | Optional LLM suggestions/approximations when approximate control is acceptable | Enable a declared approximation route; distinguish inferred from observed constraints |
| Full articles / adjusted biomedical effects | No verified dedicated literature-to-operator implementation | Provide through a labeled input adapter; do not silently equate with frequency tables |
| True individual records | Not required by synthesis interface | Keep unavailable in our same-information arm |
| Source/target record oracle | Used to derive experimental aggregates; fine binning possible when records exist | Prohibit in our external-evidence arm |

Section 3.2 separates group selection from numerical identification: preserve all marginals; select/refine available joint targets; exclude unsupported groups or optionally approximate absent joint statistics. The latter is a capability we should preserve, not disable to manufacture a weak comparator. Approximation is a prior-driven construction assumption, not measured biomedical evidence or proof of a uniquely recovered joint law. [Dependency inference](https://arxiv.org/html/2505.14752v4#S3.SS2)

The paper's experiments derive targets from ground-truth datasets. When those records are available, Appendix A uses six target-quantile bins and eight uniform subdivisions of a selected underrepresented parent bin. When only partial external aggregates exist, it explicitly uses the supplied aggregates directly. Thus record-derived fine-bin feedback is an experimental information resource, not a mandatory input to every LLMSynthor run. A method should not be denied its actual partial-aggregate mode. [Appendix A](https://arxiv.org/html/2505.14752v4#A1)

## Generation and calibration, beyond the label

The mechanism already reconstructed in the local audit is confirmed by the current paper:

1. Start with an empty synthetic dataset.
2. Ask the LLM which variable groups deserve joint guidance.
3. Assemble the permitted marginal and selected joint targets and their matching operator.
4. Aggregate the cumulative generated rows in exactly that representation.
5. Calculate target frequency minus generated frequency for each named bin/cell.
6. Ask the LLM for a compact set of proposals. Each specifies categories, continuous intervals and a number of rows.
7. Sample those rows and append them to the cumulative dataset.
8. Repeat; return the cumulative dataset.

Positive discrepancies identify regions that need more mass. The published procedure adds rows; it does not delete earlier rows, refit a global parametric copula, or perform a hidden numerical optimizer over biological coefficients. The LLM determines the local configurations and their counts. Across iterations the collection of proposals forms a mixture that can express dependence; calling it “independent sampling” without this qualification would be inaccurate. Continuous values are sampled uniformly in intervals in the main method; Appendix C allows another simple scheme. Independence among continuous draws *within* one proposal is not specified enough to verify. [Algorithm and proposal sampling](https://arxiv.org/html/2505.14752v4#S3.SS3)

Do not add a best-iteration selector, rollback, optimization-based count fitting, post-hoc regression calibration, or deletion-based repair and still label it the unmodified published mechanism. No monotonic decrease of every discrepancy is guaranteed by the displayed algorithm. Semantic validity can be diagnosed without silently replacing the procedure with rejection sampling.

### Prompt and execution details still needing a declared reproduction choice

The cached v3 proposal prompt takes joint guidance, marginal guidance, variable descriptions, proposal budget and row budget. It requests a JSON object containing proposal entries, a short reason, a proposal representation and a count. Its printed schema leaves the proposal payload as a string while accompanying rules describe category/min/max structure; it is not a complete machine-readable schema. The dependency prompt requests at most a specified number of groups, each containing at least two variables.

| Unresolved point | Transparent design choice to freeze before any scored run |
|---|---|
| Dependency schedule | Algorithm 1 infers once; Appendix A says each iteration. Implement both schedules as named options; nominate Appendix-A schedule for reported-default reproduction and report sensitivity on development fixtures |
| Proposal count | Appendix A says five; cached prompt says fewer than its budget. Resolve exact prompt parity and document whether this means at most five; do not conceal the discrepancy |
| Missing-joint approximation | Paper permits it but supplies no verified separate prompt or solver. Freeze its prompt, permitted evidence/context, prior-assumption labels, marginal-coherence checks, admission policy and call budget. Every new table must trace to permitted sources or explicit LLM completion assumptions; never derive its numerical target from hidden references or tune it toward the cumulative synthetic data. |
| Intra-proposal numerical sampling | Use explicit independent uniform draws as a declared reconstruction assumption, not a verified author-code fact |
| Empty-data frequencies | Define zero initial accumulated mass so first feedback is the admitted target; label implementation convention |
| Row-budget enforcement | Fix per-iteration row totals and require exact proposal-count sum; repair invalid syntax/counts without optimizing against outcomes |
| Interval boundaries/integer fields | Specify closed/open edges, valid range handling and integer sampling; avoid unnoticed age-rounding bias |
| Invalid responses | Freeze bounded schema-repair policy, include its model calls and failures in budget, retain raw responses |
| Stopping | Fixed iteration/row budget for comparable runs; no target-reference-based early stopping |
| Final sampling | Preserve cumulative output for native comparison; replaying a frozen mixture for additional draws is a separate deployment diagnostic |

The current source does not resolve retries, parser behavior, model snapshot IDs, seed handling, actual package versions, per-proposal count limits, or exact adaptive reference-query schedules. Do not fill those gaps with claims of fidelity.

## Model requirements and resource planning

Published defaults are five proposals and 100 iterations; three joint combinations; GPT-4.1-nano Chat Completion at temperature 0.8. Appendix A also describes Qwen2.5-7B-Instruct via vLLM with 2,048 maximum generated tokens, temperature 0.7, top-k 20 and top-p 0.98. Table 3 includes a Qwen2.5-3B-Instruct comparison. No task-specific LLM fine-tuning is described. Reported hardware is a 40-thread Xeon E5-2698 v4 server, 252 GB RAM and four 32-GB V100 GPUs; that is the experimental machine, **not an established minimum requirement**. [Experimental setup](https://arxiv.org/html/2505.14752v4#S4), [implementation settings](https://arxiv.org/html/2505.14752v4#A1)

The package/environment and model snapshots are unavailable. Current model availability, account access and prices have not been checked, and no endpoint was invoked. A CPU can handle the small table sampler/aggregator; model inference dominates operational resources. A local Qwen path needs an already available compatible installation and model weights; this audit does not authorize model downloads or hardware procurement.

For budgeting, separate calls from proposals: five proposals returned in one response are not five model calls. Under separate dependency/proposal prompts, 100 iterations imply approximately 101 calls if groups are inferred once or 200 if inferred every iteration, before repairs or missing-table inference. This is a planning count, not a measured author implementation count.

With 2,048 output-token caps applied to every call, 101/200 calls have upper bounds of 206,848/409,600 generated tokens. The paper states that cap for the local inference settings; applying it to another model is a new budget decision. Input tokens depend on packet and contingency-table size and must be metered. An illustrative mean latency of 2–10 seconds per sequential call would imply roughly 3–34 minutes per run; this is arithmetic for planning, not a runtime claim. Do not quote a dollar cost until the chosen service and its actual token counts/prices are known.

For a common-backbone comparison, use the same authorized model service as our method and label the substitution. That estimates workflow differences under one backbone, not the published nano result. Keep a paper-backbone track separate if resources later permit. Equal information and transparent compute accounting matter more than forcing LLMSynthor into our “one trial plus one revision” contract, which would remove its central iterative mechanism.

## Nearest fair comparison to the current project

Manuscript v0.15 Sections 3–4 and Table 1 establish complete-cohort generation with no individual construction inputs for Q1/Q5. The historical fixed-row enrichment proposal in the October review is not the current primary task.

| Existing task | Fair LLMSynthor condition | Scientific evaluation retained |
|---|---|---|
| Q1 CHNS E0/E1 | Same frozen E0 or E1 external evidence and population metadata; same requested complete schema; no target-aggregate oracle | All six CHNS/ENSANUT focal analyses and complete diagnostics under original endpoint definitions |
| Q1 ENSANUT E0/E1 | Same eligibility and eight sex-by-age cell design; no additional measured biomarker margins/joints | BMI effects with/without glucose and conditional age, in native units |
| Q5 HbA1c | Same curated glycemia originals, population request and admitted retrieval policy | Age per decade; BMI per 5 kg/m² with/without glucose; marginal/residual spread |
| Q5 TC/HDL | Same three original lipid studies and correction, measurement assumptions, units and target context | Age/sex-adjusted BMI slopes, residual TC–HDL Pearson relation, marginal spread |
| Q2 supplied-target-summary reconstruction | Separate summary-assisted arm with exactly the supplied 30 summaries | Reconstruction, not external-evidence inference or held-out validation |

The existing [Q5 protocol](../evidence_use_cross_task_2026-11-05/PROTOCOL.json) fixes 3,000 rows, three final seeds, per-author retrieval limits, delayed reference reads and exposed-development status. Keep those information and endpoint boundaries; do not simply inherit its single-revision cap for an intrinsically 100-step comparator. Current exposed CHNS/ENSANUT/Turkana results are development references, not fresh external validation.

### A faithful biomedical input adapter

The adapter should do only auditable interface work before generation:

- Supply identical variable descriptions, admissible evidence, population/measurement metadata and requested size to both methods.
- Maintain each statistic's source, estimator, adjustment set, population, units and availability.
- Convert units and category encodings only when justified; preserve source values.
- Send existing frequency tables directly to LLMSynthor's frequency guidance.
- Give non-frequency evidence to its LLM as attributed context for a declared approximation stage; retain any resulting joint tables and their assumptions.
- Mark unsupported quantities unavailable. A mean and SD do not determine quantile bins; a regression coefficient does not determine a joint table; a rank correlation is not automatically Pearson correlation.
- Keep observed, exactly transformed and LLM-inferred targets distinct in the ledger, feedback and reported fit.

Do not supply analyst-built Gaussian-copula tables derived from our successful generators and call this neutral formatting. That would transfer our completion model into the baseline. Conversely, do not strip relational evidence from LLMSynthor merely because its demonstrated feedback uses histograms. Let its LLM use the same admissible evidence, with transparent conversion/approximation choices and an explicit equal access budget.

A defensible first comparison uses the original proposal/count loop plus a labeled **evidence-to-guidance adapter**. Missing-joint approximation should be enabled in the principal external-evidence comparator; an available-aggregates-only variant can diagnose the contribution of that capability. Freeze the approximation prompt and budget on nonclinical fixtures before scored runs.

Applying arbitrary biomedical regression/source-conditioned operators directly in feedback is plausible under the framework's general operator definition, but is not the verified published frequency implementation. Report that as an enhanced LLMSynthor variant or a shared-operator mechanism ablation, not as the only baseline. Especially in Q5, all 132 existing source-check entries were unavailable: an implementation must not silently convert these into valid numeric feedback. Its own declared approximate guidance can be evaluated as assumption-based feedback, separately from actual source-fit claims.

### Evaluation and repeat structure

Keep feedback-source fit separate from target scientific performance. Lock final analysis references outside the generation process; do not use cached reference slopes, signs, tails or residual correlations to revise prompts, pick seeds or select a final iteration. The audit itself has read exposed manuscript results, so eventual constructors need fresh isolated task bundles, while reporting the overall study as exposed development.

Independent LLMSynthor runs repeat both LLM proposal decisions and sampling. Three replays of one fixed proposal mixture only measure conditional sampling variability and are not three independent planning runs. Report these two variance sources separately. Preserve every scheduled result, invalid output and unavailable endpoint. Match row counts, input evidence and model access; report calls, tokens, deterministic compute and failures rather than claiming compute equality solely from seed counts.

For the coordinated primary design, use two cases × two workflows × five fresh contexts = 20 final tables, each with 3,000 rows. Each LLMSynthor final table is the native cumulative output of one complete adaptive episode; do not append additional Monte Carlo replays to the primary sample count. Use its 100-round setting and up to five proposals per round, with the exact interpretation of the prompt-count discrepancy declared. Allocate 30 requested rows per round to achieve 3,000 exactly. This is a biomedical row-schedule adaptation: the paper's mathematical task specifies total size and its cached prompt specifies a batch request, but the released materials do not establish this particular batch-size rule. Preserve LLM choice of the relative counts among proposals. Require a valid sum of 30 through the frozen schema policy; do not use an optimization routine to secretly reallocate counts.

The ten LLMSynthor episodes therefore imply 1,000 proposal calls, plus approximately 10 or 1,000 dependency calls depending on the declared schedule, plus intake, missing-statistic inference and schema-repair calls. Appendix A's per-round dependency schedule yields approximately 2,000 planning calls for those ten episodes before extras. This is a material resource commitment. Do not claim a 10-round truncated comparison establishes superiority over the reported 100-round method. If the host cannot instrument this call budget, the next deliverable is the bounded technical stage and its measured feasibility, not an immediate full batch. Generating a variable-sized episode followed by a 3,000-row subsample adds an avoidable output transformation and is not preferable to a declared exact-size schedule.

### Should the workflows share a common macro front end?

The principal same-evidence comparison should retain each workflow's own intake and generation decisions. LLMSynthor plus a generic evidence-to-macro intake tests a complete adapted workflow; our evidence-to-joint-law system tests its own complete workflow. Both receive the same articles, allowed summaries and metadata, and neither receives the other's completed joint distribution.

A supplementary **common-macro-input comparison** is useful if the scientific claim concerns the downstream controller or generative representation. Freeze one independent set of compatible margins/contingency tables and give exactly that set to both workflows. A hand-designed synthetic fixture supplies this input without patient access and is also the clean fidelity check. Such an experiment isolates generation and feedback behavior conditional on common macro information; it does not establish which workflow best interprets heterogeneous papers. Do not construct the shared macros from our successful generator, its fitted parameters, or exposed target endpoints, and do not present CHNS's 30 regression/correlation summaries as if they were native frequency tables. For heterogeneous papers, the common front end would itself need a fully declared evidence-to-macro model and assumptions; its conclusions belong to that added model as well as the downstream methods.

## What must remain intact

1. Substantive LLM dependency inference and proposal/count allocation.
2. The ability to suggest absent joint constraints under a declared approximation mode.
3. Matching target and generated aggregation semantics.
4. Directed, attributable macro discrepancies and cumulative feedback.
5. Compact proposal execution by a sampler; no substitution with literal row-by-row LLM printing.
6. Append-only whole-cohort construction for the primary comparison.
7. No micro-record access, hidden target aggregate queries, or outcome-informed tuning in the same-information arm.
8. Clear separation between paper-reported behavior, reproduction choices and biomedical extensions.
9. No additional source-conditioned optimizer or reused biological model concealed in an “adapter.”

## Realistic smoke-test sequence; proposed only

**Stage 0 — specification and static review.** Recheck release availability; finalize prompt parity, schema, seed/budget policy, source ledger and adapter tests. Use only hand-constructed fixtures, e.g. two categorical variables and one bounded numerical variable. Confirm exact row counts, interval/category validation, joint normalization, unchanged prior rows, and deterministic sampler replay. No LLM or biomedical target is needed.

**Stage 1 — tiny authorized model smoke test.** If an already authorized model becomes available, run one fixture with 3–5 iterations, up to five proposals per iteration and 150–300 total rows. Approximate budget: 4–10 planning calls plus any explicitly budgeted repair/approximation calls. Verify that guidance is used, append-only feedback operates, and the missing-joint route records its assumption provenance. This checks execution, not published accuracy or clinical usefulness.

**Stage 2 — controlled development convergence.** One small known distribution; test both dependency schedules and repeat independent planning. Nominate one schedule/interpretation before biomedical scoring. Check marginal and joint discrepancy traces as well as row validity; do not require every iteration to improve every metric.

**Stage 3 — costed biomedical comparison.** After the technical stage demonstrates an instrumented host interface and acceptable resources, use the coordinated 20-table plan above, with complete 100-round LLMSynthor episodes. Run all prespecified target analyses only after outputs are frozen. A smaller exploratory biomedical run, if separately chosen, remains a pilot and cannot support a full-method superiority claim. Extend beyond the two selected cases only if fidelity and interface checks pass, regardless of whether the early comparator wins.

The deliverable at this stage is the audited specification and source metadata. No experiment has been launched. Exact author-code reproduction remains unavailable; a bounded, clearly labeled paper reconstruction can still be a useful and fair neighbor comparison.

