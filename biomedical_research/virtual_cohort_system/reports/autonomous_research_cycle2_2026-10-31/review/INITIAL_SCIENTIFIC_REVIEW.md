# Initial scientific candidate review

**PASS WITH DECLARED LIMITATIONS for both frozen initial candidates. No blocking defect was found in the bounded static scientific review.** This permits the controller to consider the already planned source executions under its separate release; it is not a numerical source-validation result, an execution release, or approval of target effects. Candidates remain unchanged.

Review date: 2026-10-31. Reviewed A (`b1/candidates/initial`) and B (`b2/candidates/initial`) separately against their own approved input package, public brief, task, evidence, source recipes and frozen scientific artifacts. No generator was imported or executed. No private, raw participant or generated table was read. Only deterministic arithmetic on declared aggregate parameters was independently recomputed; no simulated rows, fits, feedback or target statistics were produced.

## Candidate A: one limitation finding

**INITIAL-A-01 — Limitation, not a blocker.** The shared conditional Gaussian construction is algebraically coherent, but the unidentified residual BMI/glucose correlation 0.30 and declared age/sex trends determine its conditional biomarker coefficients. The Pani location is a count-weighted mixture of survey-weighted age-band means; the author correctly labels this as an approximate location rather than a recovered survey mean. Source slope agreement therefore cannot identify the unreported joint distribution or validate transfer to the Mexican analytical subset. Age linearity can conflict with the acknowledged older-age plateau.

The program uses the same conditional covariate law, HbA1c slopes and residual law in all contexts. Only the declared age/sex distribution and source location reference change; target reuses the exact Pani reference. The two Jansen projections are solved jointly after an explicit covariance assumption, rather than concatenated as simultaneous coefficients. The declared HbA1c residual SD is derived from the published individual SD, not a Pani survey SE. Its first-stage target quota and positivity/glucose rejection implement the public schema without empirical target calibration. No candidate revision is required by this review.

## Candidate B: one limitation finding

**INITIAL-B-01 — Limitation, not a blocker.** The common covariance/projection algebra is coherent. Its Pani/target level uses the published 50-54 age-band mean 5.40%, anchored at assumed age 52 and female fraction 0.5. That legitimate source anchor still depends on unreported within-band covariates and unverified transport. The same residual correlation 0.30, Gaussian form, zero direct HbA1c female term and common residual scale are explicit scenario assumptions. Its positive linear age law can miss the acknowledged older-age plateau.

The program computes the shared simultaneous coefficients from declared moments, trends and covariance at execution time; the deterministic algebra file agrees with an independent aggregate-only calculation. Target and Pani have identical HbA1c anchors, and no target-only coefficient or biological branch appears. Selection, source age tails, fasting plasma-to-serum comparability, anemia/medication differences and conditional eligibility are declared approximations. No forced change to these initial choices is requested.

## Algebra, units and selection

Both use the correct task-unit source constraints: BMI projection `0.13 * 0.09148 = 0.0118924` HbA1c percentage points per kg/m²; glucose projection `2.29 * 0.09148 / 18 = 0.01163828888888889` percentage points per mg/dL; Pani conditional age coefficient `0.010` percentage points per year. The NGSP offset is not applied to slopes or SDs. The original percent HbA1c mean/SD 5.6/0.3 are used, and alternate IFCC representations are not independent constraints.

Writing residual variances as vB/vG and covariance as c, both solve `pB = betaB + betaG*c/vB` and `pG = betaG + betaB*c/vG`. The denominator is `1-rho²`; both declared residual covariance matrices and residual HbA1c variances are positive. Independent deterministic calculations reproduce:

| Quantity | A | B |
|---|---:|---:|
| Conditional BMI coefficient, % per kg/m² | 0.004688866112 | 0.004678334308 |
| Conditional glucose coefficient, % per mg/dL | 0.010994224428 | 0.010996477723 |
| HbA1c residual SD, % | 0.257925059802 | 0.256762250080 |

These are model coefficients derived from assumptions and aggregate constraints, not newly estimated clinical or target effects. The arithmetic also reproduces A's count-weighted Pani level and age anchor. The closed-form identities apply to nominal untruncated moments. Source age discretization, finite support and conditional glucose/positivity rejection perturb exact moment/projection equalities, which both authors disclose.

Both generate exactly 250 rows for each target age/sex design cell by construction and keep age/sex fixed during biomarker rejection. They model the distribution conditional on eligibility; they do not simulate diagnosis, anemia, medication, fasting-duration or measurement-documentation mechanisms. This limitation is explicit. Lifelines uses assumed age support 18-95 and Pani 25-95; neither silently restricts the Pani open-ended older band to 79. The individual Gaussian variation and repeated seeds do not represent parameter, model or transport uncertainty.

## Evidence, recipes and code boundary

Both freeze hashes match the controller's supplied identities. All 20 A commitments and 19 B commitments match current bytes. Each approved 23-file copied input set and registry hash also match admission, and each evidence.json is byte-identical to its 32-item admitted template. Jansen Table 3 remains quarantined, Liu remains contextual, Pani/FOS remain separate and Pani/Liu overlap is disclosed. Every top-level model parameter has valid evidence/assumption provenance references.

Each candidate preserves exactly 11 Lifelines and 9 Pani checks, including all eight Pani age-band means. IDs, evidence IDs and operators match the fixed panel exactly: raw source units, original adjustment sets, sample SD convention and age restrictions are preserved. All checks are marked approximate with valid assumption references; current numerical source validation is correctly not computable. Child tasks retain all parent policy/schema fields except the permitted population, row count and numeric support bounds, and all context definitions match their tasks.

Both frozen programs contain one synchronous `generate(observed, specification, seed)` and only NumPy/pandas imports. Whole-cohort input must be None, all scientific settings come from the passed specification and random draws use the passed seed. Full static inspection found no file/network/process access, dynamic code execution, hidden patient rows, empirical target summaries or target-answer constants. The allowed source-derived coefficients/levels and expressly declared assumptions are not target leakage. This is a static finding about the submitted artifacts; runtime success remains for the isolated controller execution.

## Cross-candidate interpretation

**These are two same-family parameterizations, not structural diversity.** Both use conditional bivariate Gaussian BMI/glucose residuals, a shared linear HbA1c law, residual correlation 0.30, the same admitted projection constraints and the same target/Pani level linkage strategy. They differ in assumed covariate trends, source age discretization/tail and the particular Pani location anchor. Those differences provide some parameter/anchoring variation, but they do not probe uncertainty in the shared covariance closure, nonlinear model family or transport mechanism. Their nearly equal conditional biomarker coefficients follow from their common construction assumptions.

Do not describe agreement between these candidates as robustness across structural alternatives or independent clinical replication. This limitation does not justify altering either frozen initial candidate to force diversity now. Preserve both constructions and the single planned source-feedback opportunity, report all fixed discrepancies, and keep target diagnostics unavailable to builders.

## Core bindings

All reviewed candidate commitments and approved copied input files are individually bound in the companion JSON. Core identities are shown here.

| Relative path | SHA-256 |
|---|---|
| `b1/BUILDER_BRIEF.md` | `68af29744b7d858f4613557b78ac4fb7a15f5fd82a134796865c50331d6d258a` |
| `b1/INPUT_ADMISSION.json` | `574baa48d6552bfce33d0757ac1b3f35a50686804fb39a36c63fe5bcbcf1da40` |
| `b1/SOURCE_PANEL_SPEC.json` | `ba7d3d771672029f877f29864f4017801e60fae6c3864742e3a44c02173df4e0` |
| `b1/candidates/initial/freeze.json` | `357cba8fce214024106dcf0028e69d3ab97f0aa0e1fce29d55230d0776752bfb` |
| `b1/candidates/initial/generator.py` | `616ca15ce0bc625f37cfbd43b7e28f55a1665ad2baaee6cca29ee5cd34babb4e` |
| `b1/candidates/initial/model_spec.json` | `01432a2d3f88c118e0463f4d17289d311c469198fe9f0ccee36687666c183711` |
| `b1/candidates/initial/evidence.json` | `618e16efbfc47d971f6a21194648a017efa307fd1e15952b2b999412da901dd1` |
| `b1/candidates/initial/transfer_linkage.md` | `56bccde848845f23c66ff849579d4b5ad8011ffa035c462c15008b3435738724` |
| `b2/BUILDER_BRIEF.md` | `68af29744b7d858f4613557b78ac4fb7a15f5fd82a134796865c50331d6d258a` |
| `b2/INPUT_ADMISSION.json` | `0ffb68a87897a017d625936ad0e1eded712e91ea6d53bee765547724b6683fe8` |
| `b2/SOURCE_PANEL_SPEC.json` | `ba7d3d771672029f877f29864f4017801e60fae6c3864742e3a44c02173df4e0` |
| `b2/candidates/initial/freeze.json` | `1737da8304906e833f7c89f4b4e0ca86116caed2d735b87c3254d72f1cbbbfec` |
| `b2/candidates/initial/generator.py` | `ff48f5e4e33dae30fd1d934fc596d4b49e643e6a44a5da95cda2408ef88081f7` |
| `b2/candidates/initial/model_spec.json` | `6cc6f6306fd4ca5111d86f145cc155ffcc7379e1c91f148b2b3f7a430ffaac2c` |
| `b2/candidates/initial/evidence.json` | `618e16efbfc47d971f6a21194648a017efa307fd1e15952b2b999412da901dd1` |
| `b2/candidates/initial/transfer_linkage.md` | `374a3cc82722d65f9e7b722db9869ef065229fb5c5b56668c6c5467b2f7ca59d` |

The JSON binds this Markdown report. No prior review or candidate file was changed.
