# Adaptive reference-assisted whole-cohort data generation

This is a new developmental pilot, authorized on 3 November 2026. Deliver a scientifically usable virtual cohort for the declared CHNS 2009 selected analytical population. Every person and all five variables are generated. There is no observed.csv and no individual input. This is not a prospective validation and not an external-evidence-only experiment.

## Scientific use and information

Bundle: `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/evcAR/b`.
Project interface root: `D:/AIR-014_ECRC_Paper_Clean_2026-08-16/biomedical_research/virtual_cohort_system`.

Read task.json, input/compiled_evidence.json, input/reference_summary.json, input/analysis_definitions.json and the admitted sources in this bundle. The full reference contains all 27 existing diagnostics and all three scientific regression estimates with their available intervals. They are expressly permitted construction, fitting and revision inputs. They are sample estimates, not population truth. No patient-level data are permitted for this run. Do not read other candidate generators or their outputs or reports. External original studies and metadata may be retrieved within the budget. Record actual queries/URLs and findings; do not claim searches not made. Newly retrieved material used numerically needs curator registration before candidate freezing.

Requested uses: adjusted BMI-HbA1c, glucose-HbA1c, and age-HbA1c regressions as defined in input/analysis_definitions.json; accompanying distribution and glucose/HbA1c joint diagnostics. You know the research questions. You may adapt the generation process to them. Do not force exact matches to a chosen seed, manufacture a desired p-value or describe exposed-reference agreement as new validation.

Choose the scientific structure, dependence, parameters, residual distributions and numerical strategy yourself. There is no prescribed sign, family, equation or complexity. Use evidence where applicable; distinguish internal development reference, external observations, algebraic derivations and assumptions. Source populations, sample exclusions, measurements, adjusted slopes and correlation types must not be silently pooled. A source not reporting a relation does not establish independence. Source-study replay is optional for this bounded pilot; if not performed, state that honestly.

## Budget and workflow

One fresh scientific construction; initial and final authoring phases; one feedback revision cycle. Each phase may request at most two isolated numerical trials, 3000 rows per table. The controller will execute them and return all 30 numerical diagnostics. Both initial and final delivery consist of three fixed seeds 3101, 3102, 3103 at 3000 rows. Total at most ten tables including trial/source-context tables and failed execution attempts. A no-op final is valid and duplicated output is not independent evidence.

Up to four literature queries and two new original documents across the entire pilot. Existing admitted source reads and mathematical parameter calculations do not use table slots. Do not run random sampling/generator code outside the supplied isolated session; analytic algebra/optimization without synthetic rows is allowed. If numerical trials are useful, submit a candidate and explicitly request a trial; the coordinator returns actual execution and feedback. Do not invent a runtime result. No paid API, training, HPC, new cohort acquisition or raw-patient access.

## Submission

Read the evidence-cohort-generation skill and its harness interface. Place each new draft in a NEW directory under `evcAR/b/candidates/`; root will bind the fixed feedback definitions, validate, freeze and execute via the session. Never change a frozen candidate. Before execution supply:

- `generator.py`: top-level synchronous `generate(observed, spec, seed)` returning a pandas DataFrame matching task columns/order exactly. observed is None. No filesystem/network access. numpy/pandas/scipy are available in the isolated runtime.
- `model_spec.json`: exact harness schema parameters/assumptions/parameter_provenance. Include row count 3000 in author-controlled settings; declared task size is a design choice, not scientific evidence. Parameter values belong here, with evidence/assumption IDs and derivations.
- `evidence.json`: use the supplied compiled evidence; optionally a properly registered supplemented version. The reference source is explicitly CHNS_DEV_REF, not external literature.
- `decision.md`: concise rationale, scientific use, input provenance, finite-moment/tail reasoning, known unidentified relationships, and whether a numerical trial is requested. No private reasoning trace is needed.
- `checks.json`: truthful scope/records/artifacts. Legacy `source_only` label means all declared input sources here, including exposed CHNS reference; it does not mean independent external studies only. Unrun checks must be not_computable, not pass. Actual prior trial feedback may be copied and hash-bound as an auxiliary artifact.

Root attaches complete versioned semantic feedback definitions and executes existing numerical tools. Root does not alter scientific code or parameter values. Corrections to a technical interface must be distinguished from scientific changes. Respond with candidate path, actual actions, optional next trial request, costs and limitations. After initial delivery feedback, revise or retain with an explicit final decision and paired change rationale.
