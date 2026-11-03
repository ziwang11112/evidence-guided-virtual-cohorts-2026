# Independent results review: existing CHNS information benchmark

Reviewer: `/root/highlight_core_design`; producer/coordinator: `/root`. Review completed after all ten constructors and all thirty slots closed. **The finite-table results reproduce, but the prespecified improvement on both evidence-addressed endpoints is not achieved.** A separately confirmed structural tail defect also prevents treating seven submitted laws as scientifically adequate population models.

The reviewed [independent calculation](independent_recompute.py) was executed once after `FINAL_INVENTORY.json` and the primary report existed. It uses a separate CSV parser and QR linear solve, without importing the primary analysis/summarization functions or a generator. Two pre-execution fixes made scientific withholding explicit and bound each output to the sealed inventory. The resulting [receipt](INDEPENDENT_RECOMPUTATION.json) records **790 checks, zero mismatches, 90 recomputed focal coefficients, and 90,000 generated rows read**. No patient rows were opened, historical reference uncertainty was not re-estimated, and no generator was rerun. A further read-only audit checked 200 closure, review, candidate and freeze bindings; the evaluation intent matches the final inventory.

All **10 constructors × 3 seeds × 3,000 rows** completed: 30/30 runtime successes, 30 complete scientific analyses, 90/90 focal estimates, and no failed, withheld or unrun slot. The assignment and candidate-review records report zero technical correction returns. The full denominator remains intact. The immutable primary report's initial `independent_recomputation: pending` is superseded by this separately bound receipt, not edited retrospectively.

The calculations take absolute discrepancy from the fixed measured-reference coefficient for each seed, average over three seeds within each constructor, then average over five constructors per arm. Endpoint identifiers below are distinct from the E0/E1 information-arm names. HbA1c units are **percentage points**, not relative percentage changes.

| Focal coefficient and adjustment | Unit | Reference | E0 arm mean absolute discrepancy | E1 arm mean absolute discrepancy | E1 minus E0 |
|---|---|---:|---:|---:|---:|
| BMI; age, female (endpoint E1) | HbA1c percentage points/(kg/m²) | 0.05494608 | 0.02667490 | 0.02951665 | +0.00284175 |
| Serum glucose; age, female (endpoint E2) | HbA1c percentage points/(mmol/L) | 0.40209339 | 0.08917701 | 0.02290069 | −0.06627631 |
| Age; female, BMI, serum glucose (endpoint E3) | HbA1c percentage points/year | 0.00810704 | 0.00321878 | 0.00385760 | +0.00063882 |

The additional relationship evidence is associated with **74.3% lower glucose-projection discrepancy in these finite tables**, while BMI and age discrepancies increase. The complete-arms flag is true; the required two-addressed-endpoint improvement flag is false. This is partial, endpoint-specific gain, not overall improvement and not evidence that the extra information had no effect. The direction of each arm contrast is unchanged at both existing reference-interval endpoints. Those endpoint calculations are sensitivity summaries, not equivalence tests, confidence regions for the arm contrasts, or a check at every interior reference value.

Constructor variation remains visible: glucose discrepancy spans 0.06266–0.11304 in E0 and 0.00972–0.06669 in E1; BMI spans 0.02277–0.03274 and 0.02038–0.03731; age spans 0.00184–0.00562 and 0.00126–0.00554. No pairing of equally numbered constructors is implied. All 90 finite-table slopes are positive, but all 30 BMI slopes fall below the reference interval's lower endpoint. Sign agreement therefore does not establish magnitude recovery or clinical adequacy. These are adjusted associations in a selected, unweighted CHNS complete-case sample (n=6,631), not treatment effects or nationally representative estimates. Source/target population and plasma/serum transport assumptions remain unresolved.

**Post-freeze structural finding.** I independently inspected the frozen code and numeric specifications after the static auditor's alert. E0_A01, E0_A03, E0_A04 and E1_A01–E1_A04 all draw untruncated, nondegenerate lognormal BMI conditional on bounded age/sex, then put a positive linear function of raw BMI inside the exponential generating both glucose and HbA1c. The effective positive coefficients of raw BMI in these two log outcomes are:

| Constructor | Glucose | HbA1c |
|---|---:|---:|
| E0_A01 | 0.00875000 | 0.00300000 |
| E0_A03 | 0.00360000 | 0.00240000 |
| E0_A04 | 0.00625000 | 0.00200000 |
| E1_A01 | 0.00714286 | 0.00228571 |
| E1_A02 | 0.00514286 | 0.00114286 |
| E1_A03 | 0.00600000 | 0.00150000 |
| E1_A04 | 0.00714286 | 0.00342857 |

For the declared continuous laws, if `B = exp(mu + sigma Z)`, `sigma > 0`, then `E[exp(c B)]` diverges for every `c > 0`: the positive `c exp(mu + sigma z)` term dominates the normal tail's quadratic exponent. Bounded age/sex terms, finite mixture states and the conditional residual laws here do not remove that divergence. Thus glucose/HbA1c means and second moments are infinite, and conventional moment-based population OLS interpretations are not justified for these seven laws. This concerns the intended continuous model, not a claim that the observed CSVs contain infinities or that a finite-precision pseudorandom implementation literally has infinite support. Three benign finite draws cannot validate its population tails.

E0_A02 uses a bounded `tanh` BMI driver; E0_A05 and E1_A05 use log-BMI and additive finite-moment tail terms. They avoid this specific defect; that is not a general clinical-validity certificate. This post-freeze finding is retained alongside the unchanged primary finite-table result. It does not retrospectively replace the protocol, reclassify successful runs as execution failures, justify a three-constructor survivor analysis, or authorize repairs/reruns of the frozen candidates. It is a material limitation on reusable population-law claims and any extrapolation beyond the evaluated tables.

The comparison remains an exposed, researcher-selected benchmark. Ten fresh contexts are ten constructions from a shared language-model environment, not ten independently trained methods or ten clinical cohorts. The collaboration API did not expose exact model-version/temperature/token-meter details, and fresh contexts do not erase shared model priors or prove absence of pretraining knowledge. E0 lacks the four supplied relationship records but may still encode relationships from those priors and declared assumptions. Consequently the observed arm contrast concerns the added packet under this construction procedure; it cannot identify one relationship's contribution, superiority over another method, a benefit of feedback/retrieval, clinical equivalence, or unseen-cohort generalization. No changes were made to the frozen generators, evaluator, primary report or historical studies.

Exact SHA-256 bindings:

- [Primary report](evaluation/REPORT.json): `89dd4aa6ad82e7fb10790686947ff144c208facca57c8d7b48bd3155fae969be`.
- [Independent receipt](INDEPENDENT_RECOMPUTATION.json): `ef24304c3a7dc0e3a290ba76d6b1b7ed04b1ae82c9ae3aa90c6ffd7713475b17`.
- [Independent code](independent_recompute.py): `c0c05c09815cc3947bf624ad79306f99ba282b07cc42686012bff85841ee0688`.
- [Final inventory](FINAL_INVENTORY.json): `a393efdbc4720d4b9261141751ebeee80c8fbd14daa5f9ec17170e006b62b518`.
- [Executed release](RELEASE.json): `764ba98d0e6102c015e4cb2dba9708d8c8a886c0e77192de09d7f598e4d9dc6f` (approved scientific release digest excluding approval: `347671221fc5c8f12500dea30de4af5ce4914d44820c64d81af8c82a219e9885`).
