# M17-B: aggregate evidence to a complete virtual cohort

31 October 2026. Prospective small scientific pilot; this protocol precedes reference outcome inspection. M17-A established the execution interface, not scientific validity.

## Question and information boundary

Can a scientific Agent use externally published aggregate evidence and a population specification to construct **all** requested variables, and can the frozen complete virtual cohort support useful analyses in a separate measured reference cohort?

The requested table has `sample_id`, `age` (years), `female` (0/1), `bmi` (kg/m2), and `urate` (mg/dL). No source or target individual records, observed covariates, target moments or target fitted coefficients enter either builder's bundle. Source originals and aggregate extraction are admitted with provenance. All NHANES-derived evidence is excluded for this case. Model pretraining exposure cannot be ruled out by this procedural boundary.

An independent custodian first audits an unused public NHANES cycle. The tentative candidate is 2007–2008, subject to its metadata/exposure admission. Previously revealed targets stay closed. A different cycle is temporal validation within the same survey family, not a new independent study family. If admission fails, record that failure rather than silently substituting an exposed case.

## Defined cohort, not national representativeness

Both generated and reference cohorts have 320 adults aged 20–79. There are 40 participants in each of eight cells: sex crossed with age bins [20,35), [35,50), [50,65), [65,80). These quotas are a prospectively specified study design, not statistics learned from hidden data. The builder chooses within-bin ages and all BMI/urate values.

The reference requires measured BMI and urate, valid sex, and the specified age range. No medication, ethnicity, disease, pregnancy or laboratory-value restriction is silently added. Use positive finite BMI and nonnegative finite urate; no outcome-based trimming. Select within each cell without replacement using a fixed custodian seed 17101, ordered by participant ID before sampling. If any cell has fewer than 40 eligible participants, stop and report the design failure without inspecting endpoint estimates or changing quotas to obtain results.

This is a standardized quota-cohort comparison, not an estimate of US prevalence. Survey weights are not used to turn these artificial quotas into a national population. Reference HC3 intervals below describe the specified regression and selected sample; they do not implement NHANES complex-survey inference or establish biological transport.

## Construction and fixed schedule

- Two fresh-context Agents receive the same admitted evidence packet and task. They choose structure, parameters, assumptions and a program or direct-table route. Root does not supply scientific coefficients, desired signs or a preferred functional form.
- Initial candidates are validated, reviewed for implementation errors and frozen before isolated execution. Interface corrections before freezing are recorded; scientific edits after freezing require a new candidate.
- Each gets one source-only feedback opportunity using a separately fixed seed 17110 and the candidate's declared source checks. Population mismatch makes such checks approximate; impossible checks remain non-computable. The adapter does not recreate each source population. Do not force a quota cohort to reproduce an incompatible source's unconditional mean.
- Each may revise once or retain. Feedback and the actual decision are preserved. Retention is a valid outcome, not a repair benefit.
- The fixed analytical seeds are 17111, 17112 and 17113, paired between initial and final program versions. Direct tables are one realization, not three independent draws; do not duplicate them and count repetitions. Identical retained code/specification may reuse verified outputs with explicit lineage, not claim new executions.
- Final decisions and all scheduled outputs are frozen before the custodian reveals any reference outcomes. There is no target-feedback iteration, candidate selection by target performance or favorable-seed selection.

Two constructions in one case are a feasibility screen. Repeated seeds quantify stochastic realization variation, not independent evidence samples, calibrated model uncertainty or independent Agent constructions.

## Locked downstream analyses

Use the same complete-case equations on each generated table and on the reference. Define x=(BMI−27.5)/5, a=(age−50)/10, and f=female. Do not standardize x or a using hidden sample moments.

| Endpoint | Fixed analysis and quantity |
|---|---|
| Adjusted BMI relationship | y ~ 1 + x + a + f; coefficient x, mg/dL per 5 kg/m2 |
| Adjusted age relationship | Same model; coefficient a, mg/dL per decade |
| Adjusted sex contrast | Same model; coefficient f, mg/dL |
| BMI curvature | y ~ 1 + x + x² + a + f; f(35)−2f(30)+f(25) = 2 times coefficient x², mg/dL |
| Sex difference in BMI relationship | y ~ 1 + x + a + f + x*f; coefficient x*f |
| Male BMI relationship | Interaction-model coefficient x |
| Female BMI relationship | Interaction-model coefficient x plus coefficient x*f |
| Reverse relationship | BMI ~ 1 + urate + a + f; coefficient urate, kg/m2 per mg/dL |

Report all eight estimates, HC3 reference standard errors and 95% normal intervals, signed generated-minus-reference differences, and realization ranges. Sign agreement is descriptive; a reference interval spanning zero cannot establish a reliable direction. Neither matching signs nor inclusion in a broad interval alone establishes equivalence. Do not invent a composite success threshold after seeing results.

Supporting diagnostics: actual cell counts, BMI and urate mean/SD and 10th/50th/90th percentiles overall and by sex; age–BMI and BMI–urate Pearson correlations. Keep scientifically useful relationships primary, with distribution summaries helping explain failures.

Before revealing the target, classify endpoint exposure against the **full admitted source packet and actual candidate**: explicitly supplied relationship, derivable/assumption encoded, or not directly calibrated. A source-supplied relationship evaluated in a new population is transfer validation. An analysis not directly fitted can demonstrate reuse, but is not automatically a new discovery independent of assumptions.

## Implementation and reporting

The custodian implements and locks the evaluator before outcome access, checks arithmetic on invented nonbiomedical inputs, then evaluates once after root releases frozen outputs. A separate reviewer recomputes reported fits from actual retained tables after unblinding; no failed analysis is dropped. Preserve source/target checks, failed commands, initial/final decisions and mixed outcomes.

Artifacts remain under `work/m17b_whole_cohort_2026-10-31/`. Patient-level and generated tables remain local. GitHub may receive our protocol, code, decisions and aggregate reports through the existing bounded export workflow, excluding original papers and rows.

No new paid API, model training or HPC is required. This unit ends with an audited result and a continue/modify/stop recommendation; it does not autonomously begin another target or turn this sample into training data.
