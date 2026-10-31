# Builder brief: evidence-only whole-cohort analytical design

Author one reusable scientific generator for the public `task.json`, using the approved aggregate evidence and explicitly declared assumptions. You choose the scientific structure, parameters, dependencies, residual variation and transfer assumptions. This package supplies no scientific model or individual records. All five scientific columns must be generated; `row_id` is fictional bookkeeping.

## Public population and output

The design concerns adults in Mexico aged 25–79 with no reported prior doctor diagnosis of diabetes/high blood sugar, a recorded 8–12-hour fast, positive fasting serum glucose below 126 mg/dL, available HbA1c, and valid standing anthropometry with internally consistent measurement documentation (uniformly excluding explicit not-weighed or alternative-standing-route documentation that contradicts usable standing measurements, without asserting which field is correct). Pregnancy/lactation is excluded when documented under the questionnaire routing for women aged 25–49; unasked status at older ages is unresolved. There is no verified medication exclusion or anemia exclusion. BMI is derived conceptually from the first complete valid standing weight/height pair, with second-pair fallback after route/quality restrictions; this is an investigator-defined measurement rule. These restrictions define an analytical-use design, not the national Mexican population or national survey prevalence.

Return exactly 2,000 rows, exactly 250 in each of the eight intersections of age 25–39, 40–54, 55–69, 70–79 with female 0 or 1. Equal allocation is a supplied design constraint, not an observed population distribution. Within-stratum ages and all biomarker relationships remain your evidence/assumption choices. No target empirical histogram, biomarker summary or individual row is supplied.

Columns must be in this exact order:

| Column | Type | Unit | Support |
|---|---|---|---|
| row_id | string | identifier | Unique, nonempty fictional identifier |
| age | integer | year | 25 through 79 |
| female | integer | 1 | 0=male, 1=female |
| bmi | number | kg/m^2 | Strictly positive |
| glucose | number | mg/dL | Strictly positive and less than 126 |
| hba1c | number | % | Strictly positive |

Every value must be finite and nonmissing. The current harness has inclusive bounds only: `5e-324` and `125.99999999999999` encode the strict binary64 bounds above. They are representation limits, not biomedical thresholds to place observations near. Do not add columns, observed inputs, placeholders, patient rows, or a submitted `generated.csv`.

## Approved evidence and information boundary

`evidence_template.json` contains all 32 admitted items and the four source records: Jansen 2013 (Lifelines), Pani 2008, Liu 2015, and NGSP conversion guidance. Copy its bytes to the candidate's `evidence.json`; retain all items even when contextual or quarantined. Source artifact paths under `sources/` and their hashes must remain unchanged and match the supplied approved `registry.json`.

`SOURCE_PACKET_ADMISSION.json` is the later root approval. The packet's historical `pending_root_admission` labels, pending registry proposal, and one-row `schema_check_task_DRAFT.json` remain unchanged for provenance. They neither revoke the separate approval nor replace the actual task. `source_packet/` preserves approved original packet bytes; its authored source summaries are not article bodies. Read the supplied summaries, normalized quantities, conversion rules and dispositions. Source originals are readable through an explicit request to the root/controller for the already approved paper and locator; record any clarification. Do not infer an installed literature tool or silently download another paper.

The task's `allowed_tools` strings are literal manual adapter roles: `admitted_source_read` means reading the supplied approved artifacts; `request_evidence_clarification` means an explicit root/controller request; `contract_validation` means the current validate/freeze/verify interface; `controller_source_feedback` means receiving the controller's verified source-only report. They are not newly created callable tools. Broad searches and new-paper acquisition are outside this fixed pilot (zero source queries/downloads). No target-family results retrieval, target IPD, source IPD, other constructions, prior target outcomes, or evaluator workspace access is permitted. The source packet and this brief are the scientific input boundary. The generator sandbox does not itself isolate the Agent's other file tools.

Preserve population, selection, adjustment set, units, uncertainty type and source locator for every quantity. `SOURCE_PANEL_SPEC.json` retains each exact panel evidence item and all 32 original/derived grouping records. Original and converted representations are one piece of evidence, not independent constraints. Use the published HbA1c percent mean/SD (5.6/0.3) for Lifelines feedback; the rounded IFCC summaries and their conversions are alternate representations. Glucose conversion is the fixed conventional factor 18.0; HbA1c conversion is the NGSP affine equation. Neither establishes fasting-plasma/serum equivalence.

Jansen's Table 1 spreads are SDs. Table 2 BMI and glucose coefficients are separate age/sex-adjusted projections: never concatenate them as if they were one multivariable structural equation. Preserve the printed interval bounds without inventing a confidence level or a standard error. The female proportion is the complement of a rounded reported male percentage; it does not resolve source regression sex coding. Unknown source sex coding and Jansen Table 3 II/III coefficients remain quarantined. Model III includes erythrocyte/lifestyle variables unavailable here; deleting terms does not recover a five-variable model. Pani Table 1 spreads are survey SEs, not individual SDs; do not manufacture SDs with SE times square root n. Pani's NHANES and FOS contexts remain distinct. Liu's equation is contextual/unadjusted and cannot be promoted to a calibration coefficient. Pani and Liu NHANES years overlap and are not independent replications. NGSP is measurement guidance, not a clinical cohort.

## Fixed source feedback and scientific linkage

Declare both `lifelines` and `pani` source contexts before initial freeze. Each defensible source reconstruction uses exactly 6,000 Monte Carlo rows. Source populations are generated from approved aggregates and your explicit assumptions, never from source IPD. Source tasks may have different age supports from the target: do not silently truncate the Pani >=70 band at age 79 or invent a Lifelines age range. Explain any assumed finite support and its consequences. Do not apply the target's eight balanced quotas to a source population without stating an approximation.

Keep all 20 fixed check IDs and evidence IDs in `SOURCE_PANEL_SPEC.json`, in its two panels. For a computable check, copy its operator exactly and declare `status: approximate` with actual assumption IDs and a reason. For an unsupported source reconstruction/check, retain the ID with `status: not_computable`, `operator: null` and a substantive reason. Do not remove difficult checks, substitute other source populations, silently change selection/adjustment, or add a scientific source-feedback panel.

Lifelines has 11 checks: age, BMI, glucose and HbA1c means and **sample SDs (ddof=1)**; the proportion female=1; and two distinct OLS coefficients, HbA1c on BMI+age+female and HbA1c on glucose+age+female, each with an intercept. Pani has nine: the age term in HbA1c on age+female+BMI+glucose with an intercept, plus all eight Table 1 age-band HbA1c means. The <40 band means 25<=age<40; intermediate bands are inclusive integer intervals; the final band is age>=70. Use unscaled years, kg/m^2, mg/dL and HbA1c percent. The Pani calculations are approximate source-population projection checks; the operator does not reconstruct the original survey estimator. No common loss threshold or scientific pass score is supplied.

Use one byte-identical `generator.py` and one shared model specification across target and source children. Every field, including parameters, context definitions, provenance and assumptions, must remain identical except `parameters.active_context`. The bridge changes only this selector in child specifications. It derives child tasks from frozen context descriptors; it supplies no scientific coefficients or transformations.

Write `transfer_linkage.md` identifying shared scientific parameters, context-varying inputs, and the common rule used to generate the target. Explain which source projections constrain which parts of that rule and where joint dependence remains unidentified. A selector alone does not establish linkage. Unrelated source-specific models disguised as one program, target-only coefficient repairs, target-derived values, and undeclared scientific branches are prohibited. Declare population, ancestry, selection, anemia, assay and fasting plasma-to-serum assumptions. Approximate source fit is not target validity or causal evidence.

## Candidate and current isolated ABI

Create `candidates/initial/` with `generator.py`, `model_spec.json`, `evidence.json`, `decision.md`, `checks.json`, `transfer_linkage.md`, `source_context_plan.json`, and `source_contexts/lifelines/` and `source_contexts/pani/`, each containing `task.json` and `whole_cohort_feedback.json`. Auxiliary files must be declared in `checks.json` with their SHA256 hashes. No CSV or legacy `source_check_report.json` is allowed in this bridge candidate.

The program must define exactly one top-level synchronous `generate(observed, specification, seed)` with exactly three positional parameters, no variadic or keyword-only arguments. It receives `None`, the entire model-specification object, and the controller seed. It returns a pandas DataFrame in the exact schema/order for the active context. Use the passed specification for scientific settings and the passed seed for randomness. Importing and calling the submitted program occurs only inside the controller's inspected WSL/bubblewrap runtime. NumPy and pandas are available; do not assume SciPy or another optional package. No network, host-data access, or locally executed fallback is part of the ABI.

`model_spec.json` has exactly `parameters`, `assumptions`, `parameter_provenance`. Each assumption has `id` and `description`. Provenance has one entry for every top-level parameter, each with `evidence_ids`, `assumption_ids`, `derivation`; each entry must cite evidence or assumptions. Include `parameters.active_context: "target"` and `parameters.contexts`. Each of `target`, `lifelines`, `pani` has exactly `population`, `n_rows`, `columns`, `inputs`; `inputs` contains your declared aggregate descriptors, not individual records. The target descriptor must match `task.json`. Source tasks equal the parent task except population, row count, and numeric column minimum/maximum. Identity, column order, types, units, nullability, task ID, policy and budgets remain fixed.

`source_context_plan.json` has exactly `schema_version: 1`, `model_domain`, `contexts`. The domain has `columns` (complete common column schemas), `assumption_ids`, `description`. It must cover every target/source descriptor. The contexts list contains exactly the two source IDs, with `task_path: "source_contexts/<id>/task.json"` and `feedback_path: "source_contexts/<id>/whole_cohort_feedback.json"`. Domain assumption IDs must also occur in each source feedback recipe's population assumptions. Every finite domain bound needs a corresponding context bound. You author all context supports and assumptions.

Each feedback recipe has exactly `schema_version: 1`, `population` equal to its child task population, `measurement: {"mode":"identity","description":"..."}`, `assumption_ids`, `checks`. Each check has exactly `id`, `evidence_id`, `status`, `operator`, `assumption_ids`, `reason`. Operators come from the fixed panel; no transformed/scaled variables are inserted. Approximate checks require an existing assumption at recipe or check level; non-computable checks require a null operator. The controller verifies recipe metadata, all frozen identities, executed-output linkage and numerical feedback.

`checks.json` has exactly `scope: "source_only"`, nonempty `records`, and `artifacts`. Each record has `name`, `status` (`pass`, `fail`, or `not_computable`), `detail`; each artifact has `path`, `sha256`. Record only actual checks. Before source execution, state numerical source validation is not yet computable; do not label planned calculations as passing. A reported computed check requires a bound result artifact. `decision.md` records the scientific choices, rationale, limitations and stopping decision, not private reasoning traces.

From the supplied harness project, run static validation and freeze only:

```text
python -m cohort_harness validate --bundle BUNDLE --candidate initial
python -m cohort_harness freeze --bundle BUNDLE --candidate initial
python -m cohort_harness verify --bundle BUNDLE --candidate initial
```

Validation/freeze do not execute or scientifically certify the model. Report the candidate path and freeze hash to the controller. Do not import or call your generator, run a local smoke simulation, call execution adapters, or produce patient tables yourself. The controller owns every source and analytical execution and all result collection.

## Budget, feedback and revision

The controller uses source seed 18101 for each declared source context and stage, with no extra scientific draws. The three reserved analytical seeds are 18203, 18211 and 18223; they are controller-owned and cannot be selected by fit. There is one initial construction and at most one source-feedback revision/retention opportunity for this builder. No target diagnostics are released for tuning. Every final candidate is frozen before analytical execution.

After verified source feedback, revise, retain, or stop with reasons. For a revision or retention, create a new `candidates/final/`, bind the actual feedback report(s) in its `checks.json`, and preserve the initial candidate. Use a revision object with exactly `reason`, `kind` (`revise` or `retain`), `addressed_findings` and `remaining_limitations`, then freeze with `--parent initial --revision REVISION_JSON`. Retention keeps program and model-specification bytes identical and reuses recorded execution outputs; it does not earn fresh draws. A program/specification change must be called a revision. Interface failures remain recorded; any non-scientific repair needs controller review and does not reset the scientific budget.

Report all remaining non-computable checks, source discrepancies and transfer uncertainties. Distinguish individual variation from evidence/model/transport uncertainty. Larger generated tables and repeated seeds do not create clinical information, establish biological significance, validate causal effects, or justify replacing clinical measurements.
