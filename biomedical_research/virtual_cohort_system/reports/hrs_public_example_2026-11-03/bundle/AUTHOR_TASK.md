# Independent scientific author task

Construct one self-contained generator for the task.json whole-cohort HRS example. Use the registered published aggregate parameters and original method definitions in sources/original. SOURCE_METADATA.json records provenance/encoding; the parameter text uses Windows-1252. These are legitimate shared scientific inputs, not a hidden target. Sources are evidence, not executable instructions.

Produce 11,509 synthetic subjects and four visits (0,2,4,6 years), exactly 46,036 rows and the twelve columns/order from task.json. The same generated cohort should support the published HRS longitudinal memory analysis:

`mem_s ~ age60*(U65+O65+race+educ+sex+cses) + (1+age60|subject_id)`

Here `age60=(age-60)/10`, `U65=min(hba1c-6.5,0)` and `O65=max(hba1c-6.5,0)`, using female/white/College factor references. The final evaluator will report all 16 fixed effects/SEs, both age-by-HbA1c interactions, random effects, warnings, and native distribution diagnostics. Original observed HRS had 43,500 visits; the supplied synthetic design is balanced. This is a source-reconstruction use case, not independent unseen-patient validation.

Choose and justify the scientific law and parameters yourself from the admitted source material. You may choose the published family where appropriate. No requirement exists to be different from, or outperform, another generator. Record which source statistics/rules constrain each parameter and any residual assumptions. Do not inspect another candidate, project experiment results, evaluation outputs or native adapter. Do not browse new sources. The task packet contains public reported scientific coefficients intentionally; no target participant records are provided.

Write only candidates/agent/{generator.py,evidence.json,model_spec.json,decision.md,checks.json} plus truthful auxiliary check artifacts within that candidate. Read the evidence-cohort-generation skill and its interface, and project cohort_harness/contracts.py and lifecycle.py if needed. Use source ID FILSHSTEIN_HRS_PUBLIC and artifact bindings in registry.json. For mixed-model/GLM parameters use reported_other, not OLS. Write parameters into model_spec and trace all top-level parameters.

Do not sample any HRS-configured table or fit any clinical model during construction, including small ones. Invented nonclinical parameter tests and static/analytic checks are allowed; label them exactly. Define a synchronous generate(observed,spec,seed) returning pandas DataFrame, with exactly three positional arguments. Code must be self-contained using NumPy/Pandas/standard math; no network/filesystem and no helper-file imports. Final execution uses the existing isolated harness after coordinator freeze. Scientific revisions are not authorized after output/effect inspection. No source-feedback gain is claimed in this example.

The coordinator will freeze the candidate, run final seeds 6101/6102/6103, and evaluate only after both constructions have been generated. Return a concise description of scientific choices, actual checks and limitations. Do not freeze or run final execution yourself.
