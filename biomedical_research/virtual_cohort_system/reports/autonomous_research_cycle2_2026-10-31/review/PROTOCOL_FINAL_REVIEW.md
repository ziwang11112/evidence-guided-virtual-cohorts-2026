# Final prospective protocol review

Date: 2026-10-31. Reviewed protocol SHA-256: `fe1bbe83b0bf847a090575389272dfdbeeba3ef65c9d3af8e5bb53f9def795cd`.

**Scientific protocol freeze: PASS.** The earlier review's design requirements are resolved sufficiently for this bounded five-variable pilot. There is no remaining scientific-design blocker requiring another archive, new paper, national weighting solution, fully identified joint distribution, or new framework. **This review is not an execution release.** Independent preparation/evaluator implementation review and the applicable hash-bound release remain separate pending gates.

## Closure of the earlier checklist

| Earlier concern | Final resolution and assessment |
|---|---|
| Finite rather than national estimand | The opening target definition now explicitly names the age/sex-balanced finite reference. Each of eight groups has mass 1/8, with participant weights 1/(8*n_h). The complete eligible linked subset supplies the finite reference. National prevalence, national means, and design-based confidence inference are excluded. PASS. |
| Lab/anthropometry design mismatch | Original module design fields remain separate. Lab clustering is used for a declared empirical perturbation, without substituting expansion factors or claiming the mismatch is resolved. This is sufficient for the limited estimand. PASS. |
| Literal measurement rule and stale averaging proposal | PROTOCOL.md incorporates the full metadata adjudication and expressly supersedes the unexecuted mean-of-two proposal. First complete admissible ordinal pair precedes the second; no cross-pairing, averaging, alternative stature reconstruction, or discrepancy-driven selection is allowed. PASS. |
| Result flags and route precedence | Both age-routed block result flags must be code 1. The exact meaning is **no problem**, and the exclusion of other documented/missing flags is an investigator quality/documentation restriction, not proof that stored values are invalid. At 60+, P11 must be 1 or 4; alternative routes, no-weighing flags, undocumented codes, and explicit contradictions have distinct outcomes. The second pair cannot bypass block/route rules. PASS. |
| Eligibility semantics | Prior diagnosis is exactly lab P7==2; gestational-history code 3 is excluded rather than merged with ordinary no-diagnosis status. Recorded 8–12 hours since food is a prospective restriction, not verified source fasting duration. Anthropometry P6==4 applies to women 25–49 only; structural blanks elsewhere do not imply negative pregnancy/lactation status. No medication verification is claimed. PASS. |
| Source selection and specimen differences | Anemia is not observable in the acquired set; source anemia exclusions and plasma-to-serum/assay transfer remain explicit assumptions. The code-1 quality restriction and allowed P11=1 standing route define additional target-specific selection/comparability limits in the incorporated adjudication. No extra participant archive or invented correction is required. PASS. |
| Association estimands | Q1 is adjusted age; Q2 is BMI adjusted for age/sex; Q3 is BMI additionally adjusted for glucose. Q3 remains a noncalibrated conditional projection. Q2 minus Q3 is correctly named a coefficient change that may show attenuation, suppression, or reversal, without mediation inference. The separate source-indexed glucose projection remains secondary. PASS. |
| Resampling definition | Eligible lab PSU clusters are sampled within lab strata with multiplicity; singletons contribute once; demographic weights are recomputed. There are 399 attempts, seed 18301, no replacement retries for failed replicates, valid/failed accounting, and 2.5/97.5 percentiles with linear interpolation. Bands are conditional empirical stability, not truth confidence intervals. PASS. |
| Numerical definitions | Square-root-weight WLS, the SVD rank threshold, normalized finite-reference SD, inverted empirical-CDF weighted quantiles, and Q1 residual weighted RMS are specified. Source sample SD is separately named and need not equal the finite-reference descriptive SD convention. PASS at specification level; implementation equivalence is a separate gate. |
| Source-context linkage | Same generator, unchanged complete specification except active_context, all contexts declared before feedback, and an explicit shared-parameter/common-transfer-rule statement are required. Source-specific unsupported assumptions remain visible; a selector alone does not establish scientific linkage. PASS. |
| Source and analytical budgets | Source IDs are lifelines and pani, 6,000 Monte Carlo rows each when defensible, source seed 18101. Analytical seeds are 18203/18211/18223 for scheduled initial/final stages. At most two constructions, one revision/retention opportunity each, and no fit-selected reruns. Retention reuses outputs/receipts. PASS. |
| Source-check scope | The frozen schedule is 11 Lifelines checks plus 9 Pani checks, for 20 total. The Lifelines panel retains original reported percent HbA1c margins and separate age/sex-adjusted coefficients. Pani uses its NHANES adjusted age projection plus the eight specified age-band mean checks. Exact operators/evidence mappings must be bound before feedback; approximations and not-computable outcomes remain permitted. PASS as a fixed protocol schedule, not certification of the not-yet-inspected recipe. |
| Information boundary and whole-cohort generation | All five scientific variables are generated; no individual source/target records or target empirical age histogram are supplied. Eligibility flows and preparation diagnostics go only to controller/evaluator/reviewer; builders receive the public task and readiness decision. Target evaluation waits for all final candidates to freeze. PASS. |

The measurement restriction is scientifically permissible because it was selected prospectively, is explicit, and preserves its effect on the target definition. Official code semantics do not prove that it is the unique appropriate secondary-analysis choice. Its treatment of documented difficulties, missing status, and retained upper-limb amputation must remain visible in later reporting.

## Separate release decisions

### 1. Protocol and public analysis/source-check schedule

**May freeze now at the reviewed hashes.** No Agent model is needed to freeze the public design, association questions, source-check panel, run budgets, seeds, and analysis operators. The protocol must not prescribe the Agent's scientific dependence structure, residual distribution, target slopes, or transfer parameters.

### 2. Custodian preparation-only release

**Scientific design clearance: PASS. Execution clearance: PENDING the separate implementation review and preparation release.** That release should bind this protocol, the measurement adjudication and its metadata sources, pinned inputs, and reviewed preparation implementation. Its scope is the fixed join, eligibility/measurement masks, private BMI/reference preparation, permitted readiness checks and allowed flow/boolean outputs. It does not authorize target association effects, model diagnostics, target distributions, or feedback to a scientific builder.

A frozen Agent construction and source-context definitions are not prerequisites for this preparation-only gate. The planned readiness floors remain conditions whose satisfaction is unknown here. Unexpected active codes or explicit contradictions trigger the prescribed pre-effect hold; failure of the readiness floors cannot be cured by inspecting endpoints and altering the cohort.

### 3. Clinical generation and later evaluation

**Not released by this review.** The protocol's independent implementation/arithmetic checks, task/evidence admission, working isolated execution/bridge verification, and hash-bound execution release must pass. Builders may then author their constructions within the public contract. For each candidate stage, its generator, specification, context definitions, source task/feedback recipes, transfer statement, assumptions, and exact admitted evidence mappings must freeze before its first source-feedback-producing execution. A revision is a new bounded stage with its actual feedback bound; retaining a stage does not authorize fresh draws.

The candidate-specific freeze is sequentially later than the protocol freeze and cannot reasonably be required before an Agent has authored its model. It must nevertheless precede feedback. Every final candidate must freeze before the once-only target analysis. Source numerical agreement cannot waive target separation or establish transport validity.

## Scope of the remaining implementation/package checks

These are ordinary verification conditions, not requests to change the scientific design:

- Verify that preparation enforces finite numeric age/analytes and the declared nonpositive/nonmeasurement exclusions, including HbA1c; the protocol's compact “available HbA1c” wording must not allow an infinity to become an eligible value. Verify literal module suffixes, active-field code domains, quality-versus-invalid distinctions, precedence, and ordinal fallback against the incorporated adjudication.
- Verify WLS, ranks, weighted summaries, cluster multiplicity/restandardization, singleton behavior, and failed-replicate accounting on artificial cases. This review read the numerical definitions, not their code or outputs.
- Bind every one of the 20 source checks to its exact approved source quantity, cohort/age-band selection, units, estimator, and assumptions. The fixed count of checks is not by itself source admission or evidence that every recipe is scientifically computable. The present source audit summaries do not enumerate all eight Pani mean mappings, so their individual entries still require the already-planned approved-evidence/recipe check; this review supplies no new source quantities.
- Preserve the method readiness reports' limited meaning. They report focused tests and an isolated artificial smoke; they do not certify an unseen biomedical candidate, source adequacy, target accuracy, or Agent-wide isolation. The case-local bridge's implementation identity and verification must be bound to the actual release.

## Review boundary and hash receipt

Newly read for this follow-up: PROTOCOL.md, custodian/MEASUREMENT_RULE_ADJUDICATION.md, method/SOURCE_CONTEXT_READINESS.md, and method/SOURCE_CONTEXT_REVIEW.md. The earlier review, source audits, redacted preflight metadata, and SOURCE_CONTEXT_SCHEMA.md remain the prior review context. Hashes of these reviewed records are recorded in PROTOCOL_FINAL_REVIEW.json, together with this report's hash.

Only filename discovery, local document reads, and SHA-256 calculations were performed. No private participant file, old target/candidate output, clinical result, method smoke output table, new primary paper, or external webpage was read. No preparation, generator, analysis, or target fit was executed. The only new writes are this review and its JSON hash receipt. This is an independent protocol assessment, not an assertion that separate pending gates have passed.
