# M16 actual locked-target independent audit

**Computational decision: PASS. Scientific interpretation: partial and construction-dependent usefulness; no general revision benefit established.** This is the authorized independent recomputation after all three builders closed, the final closure audit passed, and the canonical evaluator completed its one scheduled run. No candidate was changed, no canonical evaluation was repeated, and no result was sent to builders. The target is now exposed and closed to further tuning.

## Execution and integrity

The reviewed wrapper and unchanged independent arithmetic were verified before execution. The following invocation was run once with the project Python 3.12 interpreter and exited with code 0:

```text
python independent_target_audit/recompute.py --execute
  --release private/evaluation_release.json
  --results results/evaluation.json
  --output independent_target_audit/actual_audit.json
```

The release/public commitments and aggregate CSV integrity gates passed before reference access. Independent actual-reference computation was authorized for this audit; it is not another development or validation opportunity.

| Check | Result |
|---|---|
| Total numerical/structural comparison checks | 2,863 |
| Numeric differences outside relative/absolute tolerance `1e-9` | 0 |
| Maximum absolute numerical difference | `1.794051018855214e-14` |
| Independent/canonical disagreement records | None |
| `estimands.csv` vs JSON | PASS, 144 rows |
| `initial_final_changes.csv` vs JSON | PASS, 72 rows |
| Scheduled table-stage records | 6, each with all 24 estimands |
| Distinct generated table hashes | 4 |
| Identity/order/observed covariate preservation | PASS for all three constructions |
| Numeric changed outcome rows, initial to final | b1: 0; b2: 12; b3: 0 |

The 24 endpoints comprise four global coefficients, four within-race/sex reverse regressions, and 16 descriptive summaries. Every reference and candidate endpoint was retained; actual endpoint fits were successful. Initial/final retention does not create additional independent tables.

## Primary global relationships

Values below are canonical aggregates independently reproduced to numerical tolerance. `b = (BMI - 28)/5`; the age term is per 10 years. Curvature is the coefficient of `b²`. Interaction is the additional BMI slope for males relative to females, per 5 kg/m² BMI. These are unweighted descriptions of the selected 200-person equal-stratum quota cohort.

| Endpoint | Measured reference | b1 final (=initial) | b2 initial | b2 final | b3 final (=initial) |
|---|---:|---:|---:|---:|---:|
| BMI | 0.316165 | 0.363935 | 0.364479 | 0.334604 | 0.362292 |
| Age | 0.282147 | 0.169686 | 0.207335 | 0.203520 | -0.017153 |
| BMI curvature | -0.022385 | -0.024097 | -0.013484 | -0.010589 | -0.013828 |
| BMI × male interaction | -0.066011 | 0.000746 | 0.059068 | 0.081255 | -0.057769 |

- Positive BMI direction was reproduced by all constructions.
- Positive age direction was reproduced by b1 and b2; b3 had the opposite sign. Therefore stable age-direction recovery across Agent constructions is **not** established.
- Negative curvature direction was reproduced by all three constructions. Its existence as a target comparison is supported here, but source-inspired high-BMI attenuation was already an explicit model assumption. This does not demonstrate that the Agent independently discovered curvature.
- The negative interaction was reproduced by b3; b1 and b2 had positive signs. The b1 estimate is extremely close to zero and should not be described as strong evidence of the opposite interaction.

## Reference PSU sensitivity

The actual reference contains **29 joint (stratum, PSU) groups**, computed from this cohort rather than assumed from earlier experiments. All 29 deletions were evaluated for each of four global models: **116 deletion fits**, with no numerical or rank failures.

| Reference endpoint | Leave-one-joint-PSU-out minimum | Maximum | Same sign in every deletion |
|---|---:|---:|---|
| BMI | 0.282537 | 0.358771 | Yes, positive |
| Age | 0.225365 | 0.323381 | Yes, positive |
| BMI curvature | -0.031106 | -0.009463 | Yes, negative |
| BMI × male interaction | -0.112339 | -0.001001 | Yes, negative |

Thus the reference directions used in the comparison are stable to these particular PSU deletions. B3's age sign mismatch is not explained by a sign-unstable reference under this diagnostic. The reference interaction approaches zero in one deletion even though its sign remains negative throughout.

These are descriptive sensitivity ranges, **not confidence intervals**, a significance test, or national estimates. This protocol applies the PSU deletion diagnostic to the reference, not to each generated table. It does not establish robustness across new independent cohorts or repeated fresh Agent constructions. Native `WTMEC2YR` is retained as metadata and is not used to weight these quota-cohort estimands.

## What the revision did and did not show

B1 and b3 retained their original rows; they show no measured revision gain because no numeric revision occurred. B2 changed 12 of 200 urate cells. Its absolute BMI-coefficient discrepancy decreased from 0.048314 to 0.018438 mg/dL per 5 kg/m². However, age discrepancy increased from 0.074811 to 0.078626, curvature discrepancy from 0.008902 to 0.011797, and interaction discrepancy from 0.125079 to 0.147266, in their respective units.

Across b2's 24 endpoint records, 12 absolute discrepancies decreased, 9 increased and 3 were unchanged. These correlated endpoints have different scientific roles and units; this count is a description, not a composite success score or an independent test of method superiority. All endpoint-level values remain in the committed aggregate CSV/JSON outputs.

The appropriate conclusion is that the source/own-construction feedback produced an actual limited revision in one run, with mixed downstream consequences. Computational implementation agrees independently. Scientific utility remains heterogeneous across relations, and neither accurate source translation nor a working repair loop guarantees preservation of every target relationship.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| Authorized release | `989bd13c6f35655df1fddb7ce9245d399aab122d4f78f901b728b6ad388fddad` |
| Reviewed independent wrapper | `c969c2141de94e7d31762ff86dca41a802f7e7deb800b79f7ba499cdb52d1f29` |
| Frozen independent arithmetic | `e2cd4b3cc7720c3d2bc42f5e67dae9c67595534091f1fe0631683f16fc1398da` |
| `independent_target_audit/actual_audit.json` | `bfb1cabef74003d9d341f122f817ca1a5ad0d70da5ee3dad8afc962e6e7eafba` |
| `results/evaluation.json` | `89ad70a294faf6a0869cf5b1f4286bbb51858b718f9b6826602c1336b0de0a53` |
| `results/estimands.csv` | `d16e995fc3daec07ddb7858eb11c6f3bf7853c938bb23dee7d3345db984924aa` |
| `results/initial_final_changes.csv` | `8d326b71f038a49e8632ce8484c7fb575c60b19318e0aff64813f9d439e8886a` |

This report contains aggregates only. Patient and generated rows remain local. Any later development must treat this reference and its revealed analyses as exposed, not as a fresh held-out test.
