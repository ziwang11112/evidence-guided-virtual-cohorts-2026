# K02 Agent-visible request — draft for independent review

Construct a joint whole cohort of **5,000 adults aged at least 18**, with
categorical sex F/M, age, BMI, measured total cholesterol and HDL cholesterol,
plus a unique synthetic identifier. No individual covariates or measured
target values are supplied. This packet is a prospective request, not an
executable candidate, active source-check bundle or permission to begin the
campaign.

Read `clinical_request.json`, `task_template.json`,
`target_protocol_metadata.json`, `source_contexts.json` and the exact-byte
`sources/greiner_source_packet.json` copy. `manifest.json` binds this draft.
The original source packet remains unchanged; its historical administrative
status, counts and relative review links do not update this task's permission
or evidence boundary. Follow only the current packet allowlist. The build
script is reproducibility scaffolding, not a model or generator.

All generation contexts use BMI in kg/m² and TC/HDL in **mmol/L**. The same
columns and units must be retained across source and target generation.
Target analysis uses mg/dL through the separate reviewed `../unit_mapping`
artifact when activated. This is a numerical unit transformation; it does not
harmonize assays, fasting or population selection.

The target demographic, BMI and lifestyle distributions are unspecified.
Choose and document the scientific structure, distributions, shared parameters,
context-varying parameters and unreported relationships using the admitted
source evidence and explicit assumptions. No target sign, slope, mean,
variance, distribution family or expected result is supplied. A missing
relationship is neither automatically zero nor a reason to demand complete
identification before proceeding.

The six source contexts are Malawi rural men/women, Malawi urban men/women and
Uganda Masaka men/women from the same Greiner paper. Preserve its adult and
health-selection rules, table-specific subgroup counts, original units,
measurement methods, fasting qualifications and issue flags. Source health
exclusions are not target exclusions, and source sex/site strata are not target
lifestyle categories. Source counts record published evidence and do not set
synthetic row counts. Source trial rows, seeds and attempt caps still require a
finite controller declaration before execution.

Target F/M values are verified literal categories; their biological-label
legend was not independently established. The source contexts' male-to-M and
female-to-F encoding is an explicit internal convention, not verification of
that target legend. Do not silently turn it into a verified transfer fact.

The three requested analyses use the same release and common eligible rows:

- HDL on age, categorical sex and BMI; report the BMI contrast per 5 kg/m².
- TC on age, categorical sex and BMI; report the same BMI contrast.
- Pearson correlation of residuals from those two models.

These are unweighted descriptive analyses. Expected effects, target
distributions, target reference SDs and evaluation margins are not inputs.

The source evidence includes 30 numerical candidates. Of those, 18 geometric
means for BMI/TC/HDL and six low-HDL proportions have potentially usable direct
source-scenario descriptive operators after their context/bindings are reviewed.
The remaining six non-HDL geometric means stay evidence only for this request:
non-HDL is not a task column, and no derived diagnostic view is added here.
**Zero checks are activated.** Unknown source weights prevent strict source
checks; geometric means also remain unsupported by frozen semantic v1. Any
unweighted proxy needs explicit assumptions and separate independent review.

Retain all original source numbers and uncertainty. Reported CIs are estimator
uncertainty, never individual or residual SDs, acceptance bands or automatic
precision weights. The printed anomalous and rounded intervals remain flagged.
Age quartiles stay context only because the finite-sample convention is
unresolved. Pooled Table 3 coefficients stay context only because their
transformations/adjustments do not define executable subgroup or target
equations. The source packet's optional distribution illustration is not a
required construction.

Use only the admitted external source packet and supplied interface guidance.
Do not inspect target rows, target-derived moments/effects, exposed target
conclusions, other candidates or result-bearing project notes. No new search,
study or download is authorized by this packet. This is a procedural input
boundary, not a claim that the Agent's general filesystem access is sandboxed.
