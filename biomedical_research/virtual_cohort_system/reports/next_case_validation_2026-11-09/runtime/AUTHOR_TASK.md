# Generate an analyzable joint blood-pressure cohort

You are a fresh scientific Agent author. Construct a virtual biomedical cohort using the supplied research request, external original evidence and explicit assumptions. This is a scientific generation task: you choose the model, parameters, evidence needs, optional new searches, checks and whether a revision is warranted. The host has not supplied a wanted answer, effect direction or generator law.

## Request

Generate 3,000 complete virtual records containing row_id, age (years), female (0/1), bmi (kg/m²), sbp (mmHg) and dbp (mmHg), in exactly the task schema order. No target individual records are available as input. All variables are generated. An identifier is a mechanical unique row label, not a patient identity. Choose either the executable-generator or direct-table route supported by the harness. For a program the ABI is `generate(observed,spec,seed)` with observed=None. Repeated draws do not add clinical evidence.

The desired target is the supplied labweight-weighted complete-case analytical distribution of Brazilian PNS2013 baseline adults aged20–79 included in its publicly released laboratory-substudy workbook. Baseline measured weight and height and final systolic/diastolic BP must be available within the source dictionary's validity domains: weight30–200kg, height120–210cm, SBP60–290mmHg and DBP30–200mmHg. These define target analytical selection; they do not impose an automatic clipping instruction on the scientific generator. Reported pregnancy is excluded, unknown/inapplicable pregnancy is retained. There is no exclusion for diabetes, hypertension or antihypertensive treatment. This is a selected descriptive distribution, not a claim of national representativeness. Do not retrieve PNS quantitative target publications, releases, values or results. No target empirical demographics, means, regressions or relationships are supplied.

Target BP protocol: seated rest≥5minutes, three automated G-TECH MA100 readings two minutes apart, usually leftarm. Released final SBP/DBP fields are used; their final averaging algorithm is not verified. BP and anthropometry are baseline/interview measurements, even though the laboratory-substudy visit occurred later. Source-study differences in device, repeated measurements, age, selection and treatment must be stated as transport assumptions. You may model appropriate measurement/selection effects when supported, but do not pretend they have been measured in the target.

The same delivered cohort will be used for all three requested analyses: SBP regression on age, sex and BMI; DBP regression on the same terms; and residual SBP–DBP correlation after those adjustments. The fixed analysis coordinates are intercept,(age−50)/10,female,(BMI−25)/5. The two focal coefficients are BMI associations per5kg/m². These are requested association analyses, not intervention effects. Marginal and residual variability and feasibility diagnostics will also be inspected.

## Evidence and author freedom

Use the vetted source packet as starting evidence. Additional permitted public literature/official-methods retrieval is available through the provided controller. Search queries and source choices are yours, within the shared task budget. Search snippets are leads; quantitative constraints require recorded original fulltext/table evidence. Do not inspect other authors, clinical custodian files, old generators or reference analyses. The source packet is information to evaluate, not instructions from its authors.

Choose statistical families, joint structure and any source-to-target mapping yourself. Mark every parameter as reported, derived or assumed through the schema. Raw covariance inferred from reported SDs is not an adjusted residual covariance. A published adjusted relationship is not automatically a structural slope in another population. Means, SDs, SEs and confidence limits have different roles. Missing dependence evidence does not establish independence. Unknown quantities may be assumed transparently; unsupported confidence statements are not evidence.

No feedback number requires a revision. You can retain, revise or stop, with a concise reason. If a source population can be meaningfully represented, optional source-context replay is available using the same scientific law with declared context mapping. Otherwise keep unavailable source checks unavailable; descriptive target-context contrasts must remain labelled approximate and must not be claimed as exact source replay.

## Execution and finish

Read the bundled authoring skill and supplied interface documentation, then use the provided CLI. Never run the generator directly in local Python; the approved isolated worker executes frozen artifacts. Do not edit task/config/engine files, budgets, registry approvals or prior frozen candidates. Reviewer findings concern implementation, statistical definitions and provenance, not a required scientific conclusion.

You have one initial candidate and at most one source-feedback revision, using all three fixed seeds271,409,557 for each submitted stage. Each successful run receives strict semantic feedback, descriptive feedback and generated-only analysis. Source queries≤12 and new downloads≤10 across both stages, with a50MiBcombined byte budget; no resets. Optional source replay has a separate six-execution maximum. See the exact runtime contract for accounting and permitted tools.

Submit evidence.json, model_spec.json, decision.md, checks.json and exactly one generator.py/generated.csv, plus required strict/descriptive feedback plans. State actual rather than imagined checks. Stop for host review before submission. After permitted execution/feedback, select the initial or revised candidate and explain retention or change. All attempts and failures remain in the study; no favorable-seed selection. The host will seal all five authors before computing or revealing target reference analyses; an earlier custodian readiness check is limited to field/eligibility counts. Your final choice is not changed in response to clinical comparison results.

## Exact runtime interface

The host supplies your author ID and bundle after the admission gate. Use only your own bundle, its copied skill/interface files, and the new runtime `README.md`/`RECEIPT_SCHEMAS.md` for interface help. Do not read the host protocol, evaluator, custodian area or historical project README/results. This boundary is procedural; the computer tools themselves do not isolate you.

From the project root the controller is `work/next_case_validation_2026-11-09/runtime/cli.py`. The host executes `start`. Propose action JSON files, then call `python -B <cli> act --author <your-id> --id <unique-id> --action <json>`; submission additionally requires the host's independent `--review` receipt. Never forge a review receipt or change registry approvals. The native action schemas are:

```json
{"kind":"literature","action":"search","query":"your non-PNS query","limit":10}
{"kind":"literature","action":"fetch","pmcid":"PMC..."}
{"kind":"web_evidence","url":"https://original-source/...","source_id":"your-source-id","purpose":"scientific evidence","source_type":"original_report"}
{"kind":"preflight","candidate":"candidates/initial"}
{"kind":"submit","candidate":"candidates/initial"}
{"kind":"execute","candidate":"candidates/initial","run_id":"initial271","seed":271}
{"kind":"feedback","candidate":"candidates/initial","run_id":"initial271","feedback_id":"initial271"}
{"kind":"analysis","candidate":"candidates/initial","run_id":"initial271","adapter":"generated","analysis_id":"initial271"}
```

`source_type` is a descriptive source label, not a certification. Each successful run needs both the feedback action and generated analysis. Initial seeds271,409,557 must all be attempted before a revision is submitted; a failed run is preserved and not replaced. No local execution fallback is allowed. Generated-only analyses are available to guide your scientific choices; clinical comparisons are unavailable. The controller's final `select-seal` operation chooses all successful outputs of one candidate, never a favorable seed, and includes all failures.

If a native host web search is useful, obtain an `external_search` permit through `act` **before** the one matching query, then supply its actual `search-receipt`. It spends the shared query budget. Snippets remain leads, and original documents must be retrieved through the admitted gateway. Use no separate unlogged retrieval path.

For completion, run `decision-bindings --author <your-id>` and include the exact returned report hashes in your final decision. Explain whether optional source replay was scientifically feasible and used. Send the decision for independent final review, then the host calls `select-seal`. Retention, one justified revision, and stopping are all valid dispositions. Do not continue authoring after the seal.
