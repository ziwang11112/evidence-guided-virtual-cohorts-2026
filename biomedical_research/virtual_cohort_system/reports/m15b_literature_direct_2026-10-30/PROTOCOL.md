# M15-B1: literature-enabled direct urate enrichment

Protocol set 30 October 2026 before new target analysis or generation. Eligibility and selection were sent to the custodian before acquisition; this consolidated document was prepared while acquisition work proceeded. Do not describe the entire document as an externally preregistered pre-download protocol. This is a bounded analytical-utility pilot, not national estimation, patient reconstruction, a framework-superiority comparison, or a preregistered publication study. Historical M15-A and M13-B remain unchanged.

## Aim and information

Can a scientific Agent use full published sources, identify missing relationship evidence, search permitted literature, directly author an unmeasured urate column for observed age/sex/race/BMI rows, and support meaningful analyses on the resulting table?

Two full seed originals are provided through controller admission: Yun 2021 (PMC8236402) and Sun 2014 (PMC4208749). Their SDs and relationship statistics may all be read and used. They share Bogalusa participants/survey periods, so they are not independent evidence replications. Sun's Discussion contains a pediatric NHANES comparison; this is recorded exposure, not a source constraint or a result for the 2021–2023 reference. Do not use NHANES-derived findings as generation evidence in this case. Exact 2021–2023 reference outcomes remain private. Prior model training cannot be excluded.

Source admission identified native age-adjusted reverse BMI-on-urate regression as usable joint evidence; it did not prescribe a forward slope, correlation, sign, age effect, symmetric pairing, residual distribution or numerical generator. The builder independently extracts adopted evidence, defines assumptions and chooses a direct table construction. Marginal SDs are not automatically conditional residual SDs. The old four SD holdouts are now input material, never new validation.

## Target and fixed cohort selection

Official NHANES August 2021–August 2023 components BIOPRO_L, DEMO_L, BMX_L and DIQ_L; join on SEQN. Target eligibility is fixed before download: RIDSTATR=2; 20<=RIDAGEYR<=56; RIAGENDR in {1,2}; RIDRETH3 in {3,4}; DIQ010=2; finite positive BMXBMI and WTPH2YR; nonmissing SDMVSTRA/SDMVPSU; finite nonnegative LBXSUA for evaluable availability only. Do not inspect values to choose a favorable target.

Within each of four race/sex strata, sort by SHA256 of the UTF-8 string `M15B-20261030-v1|` followed by integer SEQN. Take the first 50, giving 200 rows. If any stratum has fewer than 50, stop preparation without changing the selection. The custodian may inspect outcome availability for eligibility but computes no outcome summary or association before final release. Source-to-target differences in era, geography, assay, treatment, fasting and self-reported versus laboratory-defined diabetes remain explicit transfer assumptions. No implicit pregnancy, fasting or treatment exclusion is added.

Builder-visible columns are `sample_id,race,sex,age,bmi`, with pseudonymous IDs, race White/Black and sex male/female. Preserve these exact rows, order and values; append only `urate` in mg/dL. Both LBXSUA and its SI alias LBDSUASI, all outcome-derived labels, original SEQN, and private evaluation artifacts are excluded from builder inputs. No synthetic extra people are appended to this enrichment task. Whole-cohort expansion remains a separate future use.

This equal-stratum quota subset is a finite benchmark cohort, not a probability sample for national prevalence. Analyses below use unweighted descriptive estimates on the identical selected 200 people, not national estimates. WTPH2YR is used for eligibility only; original weights and design variables are privately retained. Reference uncertainty is assessed by descriptive leave-one-PSU-out sensitivity, not falsely calibrated survey CIs for this quota subset. Report sample/domain and design limitations prominently.

## Retrieval, authorship and feedback

Use one fresh-context scientific builder. It receives this scientific contract without private reference content, full seed sources, permitted interface docs and the covariate table. It first identifies evidence gaps and performs a relevant source search, unless it supplies a concrete evidence-based reason none is needed. The existing single gateway session permits search, fulltext and supplement actions. No Agent-training job, paid API, HPC or recurring automation is added.

Total case working resource cap remains 24 query attempts, 12 source acquisition attempts and eight deeply inspected primary originals. Admission used one metadata search and three source acquisition attempts (two browser failures, one successful new full text); one seed original was reused from cache. The concrete gateway therefore allows 23 queries and nine downloads for construction/revision. Two primary originals are already counted toward eight. Supplement discovery and HTTP accounting also remain visible. Controller-assisted access, if essential because the gateway cannot handle a source, uses the same remaining case ledger. This is procedural accounting, not an implemented cross-task limiter. Full seed papers are curator-admitted; their registration is not a claim of Agent retrieval.

Gateway aliases conservatively screen NHANES sources; an independent article rejected merely for a citation may be sent to controller source-provenance review without changing the existing gateway configuration or resetting usage. Log every rejected/failed attempt. No target-related outcome search or target data access is allowed. Describe the limits of this procedural boundary.

Initial output is a literal 200-row CSV directly authored by the Agent, plus actual evidence/specification/decision/check records. Programs may calculate statistics and validate preservation; no sampler, rescaling script or optimizer populates row values under the direct-row label. No program fallback silently replaces this route.

Allow at most two source-feedback revisions after the initial version. A retain decision is valid and ends the loop. Freeze every version and retain all technical failures. The source feedback includes only (a) contract/preservation errors, and (b) builder-declared scientifically comparable or explicitly approximate source checks that are reviewed before calculation. No target outcome value, association, score or pass/fail result enters feedback. Do not provide new unregistered source values through diagnostics.

A direct target-shaped table is not the original source population. Approximate transport checks may compare the declared stratum statistics/operators, with population, selection and adjustment mismatches stated; they are not exact source replay. A separately authored source-context table also lacks program execution linkage and cannot be mislabeled verified replay. The builder may decline a noncomparable numerical check and request better evidence instead. Neither all paper summaries nor all target analyses must be fitted.

Source checks and stopping decisions cannot use true target urate. Source fidelity may improve, worsen or remain unchanged. The final candidate is selected by the stated source-based decision, not by target analysis. After the final freeze there is no further repair under this protocol.

## Fixed analysis objects and evaluation

After the final release verifies, apply these same numeric definitions to initial and final generated tables and the selected measured reference. If initial=final, report one unique table and zero changes. Intermediate versions may be retained for audit but are not selected on target results.

Define b=(BMI-28)/5, a=(age-40)/10, m=1 for male, r=1 for Black. All models have an intercept. No p-values or clinical-equivalence threshold is predeclared. Every output retains its units, sample count and matrix rank; unestimable values remain failures rather than disappearing.

1. **Primary analytical use:** OLS `urate ~ 1+b+a+m+r`, coefficient of b in mg/dL per five BMI units. This is a related forward analysis of the source-constrained joint relation, not a completely independent new discovery.
2. **Age reuse candidate:** coefficient of a in the same model. If later source retrieval provides a matching quantitative constraint, record that exposure/use and downgrade the reuse label; retain the analysis rather than replacing it opportunistically.
3. **Curvature reuse candidate:** OLS `urate ~ 1+b+a+m+r+b*b`, coefficient of b*b in mg/dL. Record source knowledge of curvature if encountered. Do not require a particular sign.
4. **Interaction reuse candidate:** OLS `urate ~ 1+b+a+m+r+b*m`, coefficient of b*m. This is a separate model, not combined curvature/interaction search.
5. **Source-informed relationship transport:** within each race/sex group, OLS `bmi ~ 1+urate+age`, extract urate coefficient in (kg/m²)/(mg/dL). No reciprocal-slope conversion.
6. **Supporting preservation diagnostics:** in each group, arithmetic urate mean, SD with n-1, median and Q90 using the explicit linear quantile convention. These remain diagnostics, not a single quality score or the principal success criterion.

There are 24 fixed estimands: four global coefficients, four group coefficients and 16 group summaries. Report measured and generated estimates side by side, differences and direction where meaningful. Do not equate a same-sign result with general usability. Do not require exact equality to real outcomes or exact reconstruction of individuals.

For the four global reference coefficients, remove each distinct joint (SDMVSTRA,SDMVPSU) group in turn and refit the identical model. Report the minimum/maximum finite leave-one-PSU-out estimates and sign stability, number of omitted PSU groups and any rank failures. This is descriptive cluster-deletion sensitivity, not a 95% CI, sampling distribution or population uncertainty guarantee. It cannot account for literature, generator, transport or finite-row authoring uncertainty. Synthetic sample size does not increase real evidence.

No new endpoint is added or removed after target results. If an analysis's source-exposure status changes during permitted retrieval, update only its interpretation, leaving its numeric definition and complete reporting intact. One construction can demonstrate an inspectable instance, not general robustness across populations or Agents.

## Audit and closure

Before builder launch verify approved source hashes, task/observed schema, hidden alias exclusion and actual direct-row tool boundary. Before evaluation verify both releases, source feedback binding, source/exposure map and actual preservation. Independently recompute primary analysis and review implementation before claims. No hand-coded target relationship is permitted.

Keep patient-level inputs, generated rows and full original articles local. Sync only code, design, source references, decisions and aggregate results to the existing private GitHub repository. A failed scientific result is retained. The admission and source-access ledger remains separate from a claim that a complete Agent-driven search or generation succeeded.
