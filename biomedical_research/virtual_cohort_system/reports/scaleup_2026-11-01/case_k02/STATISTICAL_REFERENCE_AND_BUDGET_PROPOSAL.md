# K02 statistical reference and finite source-execution proposal

2 November 2026. **Proposal for independent review; no case or campaign release.**
This document specifies S01, a transparent completion reference, and a common
source budget for A01–A05 and S01. It implements neither a generator nor a
runner. The existing campaign inventory, frozen experiments and STATE are
unchanged. The accompanying JSON records the proposed schedule and the limited
source-only algebra feasibility check actually performed.

## Decision and information boundary

Recommend a six-component source-marginal mixture with explicit conditional
independence and positive lipid-sum completion. This is a conventional, auditable
reference under incomplete aggregate evidence, not the best possible statistical
model, an optimal use of every source result, or a causal model. Its simplicity
must remain visible when comparing it with five independently authored Agent
constructions. Do not claim matched-search-budget superiority.

All six constructors receive exactly the same admitted external packet, target
population/schema, allowed operators, source contexts, source schedule and one
source-feedback opportunity. Agents retain responsibility for their scientific
structure and assumptions; S01's completion rule is not prescribed to them.
No constructor receives target participant rows, target covariate moments or
composition, target effects/signs, evaluation-only discrepancy scales, another
constructor's output, or the target-study exposure notes. Current coordinator
knowledge does not make K02 globally unseen. This proposal neither restores
independence nor changes the separately adjudicated counting label.

The source packet is
`evidence/SOURCE_CANDIDATE_GREINER.json`, SHA256
`34eeb0be18f7a9d015e9a7d2446beeb10beb134d389315c998a22199f7d7e753`.
Its transcription status does not itself admit a live harness packet. Any
scientific evidence change requires the common pre-outcome version process;
private additions or retries with a revised packet are forbidden.

## Exact source schedule, separate from target slots

Use these six contexts, each with **5,000 rows and one seed at each scheduled
stage**. Seeds are identical across constructors and reused for a changed final
stage; they support paired simulation comparisons, not independent participants.

| Source context ID | Seed | Rows per executed stage |
|---|---:|---:|
| `malawi_rural_men` | 3101 | 5,000 |
| `malawi_urban_men` | 3102 | 5,000 |
| `uganda_men` | 3103 | 5,000 |
| `malawi_rural_women` | 3104 | 5,000 |
| `malawi_urban_women` | 3105 | 5,000 |
| `uganda_women` | 3106 | 5,000 |

Per construction/stage, a bridge plan has seven contexts and nine trials: six
source trials above and three 5,000-row target trials with unchanged campaign
seeds **2101, 2102, 2103**. Trial IDs incorporate construction, stage and context;
all are fixed before execution. Canonical generated lipids are mmol/L in all
seven contexts; age is years and BMI kg/m². The reviewed target-analysis unit
adapter acts downstream without regenerating rows. Target feedback policy is
`none`; the controller delivers only the initial source reports and validity/
failure statuses to the constructor, not target-table scientific summaries.

| Accounting level | Source allocation | Target allocation |
|---|---:|---:|
| One construction, one stage | 6 slots / 30,000 rows | 3 slots / 15,000 rows |
| Six constructions, initial stage | 36 slots / 180,000 rows | 18 slots / 90,000 rows |
| Initial plus final stage labels | **72 slots / 360,000 rows** | **36 slots / 180,000 rows** |

The last row is the nontransferable reservation ceiling. Retained final slots
alias the exact initial candidate/output hashes and consume no new execution
or rows. S01's precommitted retention rule below makes its six final source and
three final target slots aliases. Thus this specific proposal permits at most
**66 new source attempts / 330,000 scheduled source rows** and **33 new target
attempts / 165,000 scheduled target rows**, when every Agent changes its final
stage. If all six retain, the corresponding maxima are 36 and 18 unique runs.
Reserved but unused S01 allocations cannot be reassigned to an Agent.

One initial packet comprises all six planned source results, including failures
and unavailable diagnostics. There is one feedback decision after that packet;
the constructor may revise once, retain, or stop. A changed final candidate is
frozen before its one six-source/three-target schedule. Final diagnostics are
retained for reporting and never trigger another revision. Final target stages
remain primary; initial stages support paired revision/retention analysis.

Each attempted slot is debited before dispatch, including prelaunch error,
failure, timeout or interruption. No retries, replacement seeds, additional
source contexts, warm-up cohorts or automatic resumption are permitted. Unstarted
slots stay unstarted; missing/failed slots are not replaced with favorable draws.
The controller must enforce the allocation across candidate versions; the current
bridge alone limits one retained parent, not the whole scientific campaign.

Proposed common per-run limits are 60 seconds, 1,024 MiB memory, 2,000,000 output
bytes and 10,000 log bytes, applied to source and target trials alike. These are
software resource limits, not scientific stopping rules. Only the existing
isolated executor is permitted; no host fallback, scheduler, HPC or paid API.

## Finite fitting computation for every constructor

The campaign's `extra_simulation_calibration_calls: 0` remains literal. No fitting
job may generate a trial cohort, repeatedly call the generator, run Monte Carlo
or quasi-Monte Carlo integration, produce pseudopatient rows for an optimizer,
or evaluate target endpoints on additional generated tables. Sampling occurs
only in the scheduled frozen executions. Ordinary declared bounded support
sampling and RNG internals may use rejection within those executions and their
frozen resource limits. No extra whole cohort may be generated or discarded to
select a favorable diagnostic; parameters/seeds may not adapt inside a run to
improve fit. Invalid output or exhaustion of a declared sampler cap remains a
failure. S01 uses direct draws and transformations, with no rejection repair.

For this first campaign, permit **analytic parameter derivation only**, including
finite source-formula evaluation and scalar transformations such as logs and
inverse CDFs. Each initial or changed final stage permits at most one deterministic
calculation job, limited to 120 seconds and 1,024 MiB memory. No numerical fitting
optimizer, model grid, multistart, quadrature, random sampling or generator call
is allowed inside that job. Code review checks its finite calculation sequence
and declared inputs/outputs before dispatch. Failure or resource exhaustion
consumes the job; no extra calculation attempt is authorized.

The Agent still chooses its scientific model, parameters and named assumptions
from the common evidence; the coordinator supplies no target-informed values or
mandatory distribution family. The same calculation allowance applies to S01 and
every Agent. All design/feedback work stays within the campaign's existing
40-turn ceiling; this proposal adds no search, training or authoring rounds.

The maximum reservation is 12 jobs across six constructors/two stages;
S01 uses one and retains, reducing this proposal's maximum to 11 jobs. A fitting
receipt records input/evidence/code/output hashes, method, job ID, declared
finite calculations, elapsed time and status. The existing candidate review and
controller attempt ledger must check/debit these jobs before execution; no new
generic optimizer, counter engine or platform is proposed. This document does
not claim that a live campaign runner already enforces the allowance.

## Fixed S01 construction

For each source stratum `g`, let `G_B,g`, `G_H,g`, `G_N,g` be reported BMI, HDL
and non-HDL geometric means; let `c_g` and `p_g` be the strict low-HDL threshold
and reported percentage divided by 100. Use only original values and locators.
With `Phi_inverse` denoting the standard-normal inverse CDF, set:

```text
mu_B,g = log(G_B,g)
mu_H,g = log(G_H,g)
mu_N,g = log(G_N,g)
sigma_g = (log(c_g) - log(G_H,g)) / Phi_inverse(p_g)

Z_B, Z_H, Z_N mutually independent standard normals
BMI = exp(mu_B,g + sigma_g * Z_B)
HDL = exp(mu_H,g + sigma_g * Z_H)
N   = exp(mu_N,g + sigma_g * Z_N)
TC  = HDL + N
```

This is analytic fitting from the admitted rounded point summaries; no loss,
numerical optimizer, precision weighting or fitted conditional regression is
used. Six inverse-CDF evaluations and the finite scalar logs suffice. The
construction treats the point values as population constraints of an assumed
unweighted lognormal scenario. It matches those theoretical marginal quantities
under that scenario, not the original survey estimator, uncertainty interval,
finite simulated table or true source population. In particular `sigma_g` is a
model-derived marginal log dispersion, not a published SD or regression residual
SD. No confidence interval or sample size is inverted to obtain dispersion.

**Explicit completion assumptions:** within a source stratum BMI, HDL and N are
independent; the otherwise unidentified BMI and N log dispersions equal the
HDL-derived `sigma_g`. This common-dispersion rule is arbitrary and unsupported
by the source; it is a parsimonious reference convention, not estimated variance
transfer. TC and HDL dependence arises mechanically through their sum. Do not
describe independence as an observed zero, infer all correlations from the two
HDL regressions, or select these assumptions using target effects.

Age is independent of stratum and all generated measurements and follows
`Uniform(18, 80)` years in every context. The upper support and shape are fixed
arbitrary completion assumptions, not source or target facts. The 18 reported
age median/quartile records remain available as context but unused numerically:
the current packet explicitly excludes them from numerical calibration because
the quantile convention is unresolved. Using them as knots would require a
separate change to that common admission rule, which this unit does not make.
The generated support **does not introduce an upper-age target eligibility
cutoff**; actual target adults above 80 remain eligible under the fixed analysis.
This reference cannot assess age-dependent lipid or BMI relations.

Source execution selects its named stratum with probability one and uses its
declared source sex label. Target generation draws an internal donor-stratum
index with fixed probabilities `(1/6, 1/6, 1/6, 1/6, 1/6, 1/6)`, then applies
the same conditional law. This assumes equal donor mixture and equal category
frequency; neither is inferred from target composition or source table counts.
Donor rural/urban labels are never treated as Turkana lifestyle categories.
The unobserved donor index is not an extra delivered column or a measured target
property. A consistent source-sex-to-F/M label convention must be declared in
the task; this does not establish a biological interpretation of target codes.
The pooled primary analyses are invariant to swapping the two labels globally.

Deliver exactly the identifier plus age, sex, BMI, TC and HDL task columns. N is
an internal positive component; no non-HDL column or additional independently
measured biomarker is claimed. This model always has TC > HDL. It cannot reproduce
measured TC < HDL records and must never use that limitation to exclude target
records. There is no rounding, clipping, post-hoc adjustment, residual-variance
fitting or conditional coefficient supplied by the coordinator. Finite-validity
failure remains failure.

The target mixture can induce BMI–lipid relationships through stratum means even
when within-stratum slopes are zero; the age/sex-adjusted target projections are
not fitted or assigned a desired direction. The reuse endpoint is dominated by
explicit joint-completion and mixture assumptions. A failure of this reference
does not establish that richer statistical approaches fail.

## Source checks, unsupported constraints and one feedback decision

| Source information | S01 use | Existing execution diagnostic disposition |
|---|---|---|
| Six BMI GMs and six HDL GMs | Analytic marginal locations | 12 supplemental GMs, canonical units |
| Six low-HDL percentages | HDL lognormal marginal dispersion | Six strict-threshold proportions; preserve percentage scale and denominator rules |
| Six non-HDL GMs | Analytic internal N locations | Unavailable on the five-variable task; current collector cannot derive TC−HDL |
| Six TC GMs | Retained diagnostic, **not fitted** | Six supplemental GMs; preserve any discrepancy |
| All reported CIs and denominator anomalies | Original provenance/uncertainty only | No SD conversion, precision weights or ad hoc correction |
| 18 age median/quartile records | Context only | No numerical calibration/check |
| 12 Table 3 regression records | Context only | Raw/log scale, weighting and unavailable covariates prevent numerical use |

Thus **24 potentially numerical diagnostics** are supported by the current
operand interface: 18 GMs (BMI/TC/HDL) plus six proportions. All 30 GM/prevalence
records receive a disposition; the six non-HDL GMs are not falsely reported as
execution-checked merely because S01 uses them analytically. No derived-variable
adapter is introduced here. Source GMs remain `reported_other`/geometric in
semantic v1, with unavailable native arithmetic and a separately labelled
supplement. Supported proportion arithmetic does not remove unknown weighting.

All six source contexts approximate each paper's selected adult, sex/site
population; health exclusions, missingness and source sampling are not recovered
from five columns. A simulated context does not manufacture disease, pregnancy
or HIV flags. Source weights remain `not_reported`. Exact source-estimator
discrepancies remain unavailable. Descriptive values may be reported; each raw
equal-weight proxy difference requires the existing separate independent
scenario approval. Source eligibility and lab/fasting/assay differences remain
disclosed, including after unit conversion. Do not weight the target donor
mixture by inconsistent table counts or treat repeated strata as independent
studies.

**Precommitted S01 decision:** after receiving the same initial source packet,
retain the identical scientific construction and alias all initial outputs if
execution/contract integrity is valid. Keep every source mismatch, including TC,
as a limitation. There is no recalibration to realized Monte Carlo discrepancies,
no rescaling to hit observed sample GMs and no alternative family selected after
feedback. An implementation/integrity failure stops S01 with its failed/unrun
slots retained; it does not authorize a repair-and-retry scientific candidate.
This uses the permitted retention opportunity honestly; zero improvement is
reported. Agent constructors may use their one reviewed scientific revision
within the same reserved ceilings.

## Check performed and conditions before implementation

A source-only deterministic domain check on the packet hash above inspected the
six named HDL GM/prevalence pairs. Each has a positive threshold/GM, probability
strictly between zero and one and unequal to one half, matching mmol/L units,
strict `<` boundary, and a finite positive solution for the formula. **6/6 were
feasible.** It returned only evidence IDs and feasibility flags; no parameter
table, trial rows, candidate, target statistic or new source study was produced.
Feasibility of the algebra does not validate the lognormal/completion assumptions
or guarantee stable scientific transfer. Recompute and retain parameter
provenance only after the specification is independently accepted.

Before implementation/release, independently approve or reject this reference,
age/common-dispersion/mixture assumptions, source contexts/proxies and budget;
review the finite analytic calculation code and attempt ledger; freeze the
common packet, task and actual code; review the
derived source bindings and unit manifest; and complete the existing campaign
admission/global-freeze rules. Real coefficients are not supplied by this note.
K02 remains a context-exposed prospective quantitative case under its separate
counting decision, not a new globally unseen validation by virtue of this file.

Basis: `docs/METHOD_AND_EXPERIMENT_DESIGN_v1_2026-11-02.md`, the unchanged
`campaign_plan.json`, K02 coordinator/prospective decisions, the existing Greiner
source packet/review, and `bridge/README.md` plus `operators/INTEGRATION.md`.
