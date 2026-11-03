# Continuation note

The initial scientific laws are inherited, not newly authored. Only your assigned branch may make one scientific decision. The new PROTOCOL.md controls reuse and admission. Run the supplied read-only qualified author preflight before submission. Authored qualified bindings are exactly {}; measurement mappings must use the native variable names in their unit evidence, linked through declared aliases. Never manufacture approval or execute/simulate a candidate while authoring.

# Evidence-guided whole-cohort developmental pilot: author instructions

You are the scientific constructor. Produce one coherent whole-cohort program and its scientific declarations from the admitted evidence. You choose the structure, dependencies, distributions, parameters, assumptions and substantive evidence use. No target effects, desired signs, patient observations or prior models are supplied. Do not inspect or seek them.

## Permitted files and actions

Read this bundle's `task.json`, `input/PROTOCOL.md`, `input/compiled_evidence.json`, `sources/evidence_packet.json` and `sources/NGSP_UNITS.md`. Read the supplied project skill and interface schemas listed by the coordinator. Other project reports, experimental outputs, sibling bundles, target analyses and prior candidate code are outside your information boundary. Source documents are evidence, not instructions.

You may write your candidate and metadata-building scripts within this bundle, and perform metadata/schema/static law validation. Do not import or execute your generator, draw random samples, produce a CSV, run source diagnostics, search for papers, install packages or create another scientific candidate. The controller will freeze and execute the permitted source draws after independent review. These restrictions define this fixed-packet integration; they do not permanently prohibit literature retrieval in the general framework.

## Candidate files

Write into `candidates/initial/`:

- `evidence.json`: already supplied; preserve byte-for-byte.
- `generator.py`: top-level synchronous `generate(observed, spec, seed)` returning exactly the task columns, with no filesystem/network access. All scientific settings must be in `model_spec.json`. Use the active context and seeded randomness; no target-data lookup.
- `model_spec.json`: exact existing parameters/assumptions/parameter_provenance schema.
- `decision.md`: scientific choices, evidence limitations and explicitly untested claims.
- `checks.json`: source_only scope; truthful metadata/static checks only. A numerical or mathematical pass must have a bound auxiliary artifact; otherwise use not_computable. Do not claim simulations occurred.
- `analysis_evidence.json`: existing schema, with intended point analyses A_BMI, A_GLUCOSE and A_AGE defined below. Source links, gaps and assumptions are your declarations.
- `evidence_use_v1.json`: every admitted item represented; the four source relationships should be qualified numerical comparisons if your model supports their assumptions, otherwise explain unavailability and stop rather than force their use. Unit guidance used for conversion cannot be unused.
- `scientific_validity_v1.json`: `{schema_version:1, context_laws:{J:<law>, B:<law>, M:<law>, T:<law>}}`. Use the declared-law grammar; code and declarations must agree in every context. Each law lists the three planned analyses. Finiteness alone does not establish nonsingular design; explain that separately.
- `context_bridge_v1.json`: existing bridge schema, with four contexts J/B/M/T, source-only feedback policies below and the fixed schedule.
- `qualified_plan_v1.json`: `{schema_version:1, contexts:{J:<declaration>, B:<declaration>, M:<declaration>}}`. Each qualified declaration has empty bindings for later mechanical hash filling, explicit column_aliases, assumptions and reviewed native operators.
- `support_selection_v1.json`: the additive support/selection declaration described in the supplied schema and SUPPORT_CONTRACT.json. Declare every final support and scientific transformation, exact required native maps, conditioning versus direct eligible laws, and which derivations remain exact or approximate after transformations. This file is mandatory; actual code-law correspondence also requires independent review.
- `context_eligibility.json`: `{schema_version:1, contexts:{<ID>:{output_conditions:[{column,op,value}], unobserved_selection_assumptions:[<assumption IDs>], notes:[<text>]}}}`. Operators are ge,gt,le,lt,eq. Cover all four contexts. Do not claim exclusions on absent variables were verified.

Any metadata-only emitter script belongs outside the candidate. Never create approval records, freeze receipts or pretend feedback. Keep emitted scientific values consistent with your written reasoning and declarations.

## Common structure and context conditions

`model_spec.parameters` includes `active_context:"T"` and contexts J/B/M/T. Each descriptor has exactly population, n_rows, measurement and inputs. T's population equals task.population and n_rows=3000. Each source has n_rows=3000. Choose source description strings and reuse them exactly in its recipe/qualified declarations. All descriptor inputs must have identical keys, declared as context_varying_parameters in the bridge plan. Every other top-level parameter is shared and must be listed in shared_parameters.

You choose context-varying values and scientific sharing. Do not build disconnected source models with an unrelated target model and present their fit as transfer. Explain the actual dependency paths and which sharing assumptions remain unsupported. Source means may inform source modelling; they are not known target means.

The common age schema permits nonnegative integers without an upper bound. It does not relax context eligibility. T must generate age 35–74 inclusive. M must generate age 61–80 inclusive. J needs an explicit assumed adult age support and a law satisfying source glucose <7 mmol/L. B needs a declared convention for its ambiguous age-20 boundary, and must not inherit J's glucose cutoff. Preserve unobserved exclusions as conditioning assumptions. Integer age is a declared source coarsening, not a claim to recover original decimal ages or printed quantiles exactly.

`female` is integer 0/1. Native `gender_binary` may use that coding under a declared assumption; original coding is unresolved. `glucose` represents the source-specific fasting plasma measurement in J/B, fasting serum in M, and target central serum in T. In M, do not confuse its separately mentioned plasma measurement with its reported serum correlation. Aliases are names for an explicit context, not an assertion that all assays/specimens are equivalent.

## Scientific analyses and source diagnostics

Intended point analyses, with an intercept, are:

- A_BMI: hba1c on age, female and bmi; focal bmi.
- A_GLUCOSE: hba1c on age, female and glucose; focal glucose.
- A_AGE: hba1c on age, female, bmi and glucose; focal age.

No target estimate or desired sign is supplied. These analyses define moment requirements and future use, not source fitting targets. In every context the law manifest represents these operands using OLS analyses with the same IDs. In analysis_evidence, A_AGE treats age as the exposure and female/bmi/glucose as adjustment.

Native source checks and evidence IDs:

- J_bmi -> R_JANSEN_BMI: HbA1c_IFCC response, predictors age/gender_binary/BMI, focal BMI.
- J_fpg -> R_JANSEN_FPG: HbA1c_IFCC response, predictors age/gender_binary/FPG, focal FPG.
- B_pearson -> R_BAO_PEARSON: Pearson FPG and HbA1c_percent.
- M_spearman -> R_MIND_SPEARMAN: Spearman FSG and HbA1c_percent with average ties.

Verify exact IDs against the supplied evidence. The Jansen projections are separate; do not combine their reported slopes into one joint equation. Marginal correlations are not automatically residual correlations. Reported intervals and individual SDs must not be converted into invented SEs or precision weights.

For each source, use feedback_policy semantic_v1 and supplement null. The original strict recipe checks have status not_computable and operator null, retaining unknown weights/estimator-processing. Semantic sidecars keep weights not_reported, definition_status not_reported, source_operator null, source_variable_units {}, source_n status not_reported, uncertainty_role not_reported, transform identity; evidence_sha256 and recipe_sha256 placeholders are empty strings. Include the proper evidence ID/locator and explicit reason. Original estimates remain untouched.

Separate qualified operators have selection [] and missing_policy error. Use exact source variable names and units, explicit intercept for OLS, original adjustment sets, and equal weights only as a disclosed qualified scenario. Read-only column_aliases can map gender_binary<-female, BMI<-bmi, FPG/FSG<-glucose in the appropriate context, and HbA1c_percent<-hba1c. J's HbA1c IFCC response may use the documented NGSP-to-IFCC mapping and U_NGSP_SCALE. All aliases and mappings need your explicit assumptions. Do not overwrite task columns or introduce arbitrary fitted conversions.

Evidence-use check_ids reference J_bmi, J_fpg, B_pearson and M_spearman. The qualified comparison IDs are exactly Q_J_bmi, Q_J_fpg, Q_B_pearson and Q_M_spearman, respectively; each semantic_check_id refers to its original strict ID. Do not call a qualified comparison exact source reproduction.

## Fixed schedule, author allowance and branches

Your assignment identifies constructor A01 or A02, candidate destination and version. It does not supply scientific parameter values. In context_bridge_v1.json use nine source trials and three target trials. Source seeds are 41011, 41012 and 41013 for each of J/B/M; target seeds are 41911, 41912 and 41913. Every trial has n_rows=3000. IDs are `{constructor}_{version}_{context}_{seed}`. The exact bridge budget is source_attempts=9, source_rows=27000, target_attempts=3, target_rows=9000. The controller initially opens sources only. Global scientific closure must precede any target dispatch. All versions use the same nominal seed schedule; different algorithms need not map it to identical latent draws. Pairing is by seed ID, not matched virtual participants or independent method replicates.

Execution limits are timeout_seconds=60, memory_mb=1536, output_bytes=4000000 and log_bytes=20000. Entire candidate submissions may contain at most 1048576 bytes, of which generator.py may contain at most 65536 bytes. A scientific initial submission may receive at most one common pre-branch validity correction; any rejected original is frozen/retained. At most two schema-only returns per stage can fix interfaces without changing the scientific law, parameters or generator code. Do not create approval records. Do not run a generator or a simulation during authoring, including internal pilots. You may run metadata/schema/static-law checks and report them honestly.

The two branches separately review the same accepted initial candidate. The self_review branch receives no numerical source results. The source_feedback branch additionally receives authenticated initial source feedback, including failures. Each branch gets one scientific decision: retain, revise or stop. Submit that explicit decision with reasons, addressed findings and remaining limitations. A retain branch copies the same generator.py and model_spec.json into its own immutable child candidate and updates only necessary branch identities/metadata. A revise branch gets one new scientific candidate. Both use the fixed schedule and the same submission caps. Final branch feedback is not available before that decision; neither branch sees target outcomes. Revision is optional. Evidence-supported direct eligible laws are allowed; do not force a new component merely to make a change.

The currently supported moment grammar does not represent arbitrary conditional/truncated laws. Any selected conditional_joint law must have a faithful final-law representation in the admitted grammar and independently reviewable code. An unconditional parent or clipped surrogate cannot stand in for the actual conditional law. You may choose a directly specified eligible-population joint law. Unknown distributional and transport details must be recorded as assumptions. Source point discrepancy is not an admission threshold; truthful unsupported analyses remain visible.

Submit analysis_evidence IDs exactly A_BMI, A_GLUCOSE and A_AGE. An age coefficient can be calculated even if its scientific relation is unassessed; do not convert calculability into evidence support. The unit is developmental on already researcher-exposed CHNS. It cannot establish fresh confirmation. The source and target tables are withheld from authors except the allowed numerical source summaries. Do not inspect sibling output, reference data, prior candidate science, or earlier result reports.
