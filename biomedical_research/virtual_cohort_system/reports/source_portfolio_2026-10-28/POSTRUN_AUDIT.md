# Independent aggregate and implementation audit — 2026-10-28

No blocking implementation, aggregate-consistency or reporting issue was found within the source-only development scope. The final decision is **retain**: broader diagnostics informed a documented decision, while the scientific model and generated-source results remained unchanged. This increment does not provide new target validation or demonstrate improved preservation of age or BMI-curvature conclusions.

This audit inspected code, specifications, evidence records, source-extraction audit records, aggregate diagnostics, freeze/execution receipts and documentation. No participant-level observed, generated, source-covariate, hidden-outcome or raw dataset was opened or hashed. No generator, test suite, target analysis or replay verifier was run. Only this audit file was written. Source values were checked against the retained extraction audit; the original publications were not independently re-extracted in this review.

## Checks and findings

- The five added WHS mappings retain the reported estimators: median 115 mg/dL, quartiles 81/169 mg/dL at probabilities .25/.75, and marginal Spearman correlations .33 for BMI and .18 for age. Their selections, variables, units, missing precision and source limitations agree across evidence, replay definitions and the extraction audit. The quantile convention is explicitly unreported in the source, with linear interpolation declared as an approximation. Spearman computes Pearson correlation of average tied ranks after complete-pair selection; it does not convert the reported coefficient to a Pearson coefficient. All 34 checks retain approximate status.
- The starter's generator, scientific parameters, parameter provenance and existing assumptions are unchanged in the initial candidate. Only the quantile-method assumption and five actual estimator definitions are added; all 29 prior replay definitions and source-context declarations are retained exactly. The protocol's starting-freeze hash matches the historical M3-final freeze. Initial/final generator, entire specification, evidence and recipe hashes match. The final parent binding, revision kind `retain`, and actual feedback copies match the initial freeze and supplied reports.
- Independently recalculated all 68 stage/check summaries from their aggregate run values, including means, sample SDs, ranges, signed/absolute discrepancies and discrepancy-pattern labels. All 204 run records agree with their corresponding retained replay diagnostics. The comparison retains 34 checks and 102 paired changes; every change is zero. The six same-seed/context output-hash pairs agree between stages. These are receipt/hash comparisons, not an independent re-reading of output bytes.
- Six successful replay reports cover two contexts each and the complete ordered seed schedule 75101, 75102, 75103 at each stage. Current replay/operator engine hashes match their recorded hashes. The portfolio verifies candidate linkage, complete schedules, fixed check definitions and unchanged evidence/source-interpretation assumptions before comparison. Undefined diagnostics remain visible without an aggregate, and scheduled failures prevent a summary. No mixed-unit score or automatic winner is produced.

The new diagnostics reveal unresolved source discrepancies rather than a new success claim:

| WHS diagnostic | Reported | Three-draw range, identical in both stages |
|---|---:|---:|
| Median TG, mg/dL | 115 | 113.28–115.03 |
| TG first quartile, mg/dL | 81 | 78.25–79.09 |
| TG third quartile, mg/dL | 169 | 165.15–166.19 |
| Spearman TG–BMI | .33 | .3304–.3425 |
| Spearman TG–age | .18 | .2043–.2222 |

Retention has a concrete source-only rationale. Raising female TG could help WHS quartiles while worsening Oh female mean/high-BMI discrepancies. Reducing the female age rise could reduce the WHS age rank association while lowering the already underpredicted Oh age-50–59 mean. These marginal summaries do not uniquely identify conditional effects under assumed independent source age/BMI inputs. Three residual draws do not separate source sampling, joint-distribution, structural or transport uncertainty. Consistent discrepancy signs are descriptive, not significance tests or acceptance thresholds.

## Chronology and information boundary

The matching protocol commitment is timestamped 20:39:13 UTC, before initial freeze at 20:40:59 and the earliest retained source execution receipt at 20:41:17. Initial replay reports complete at 20:41:22, 20:41:26 and 20:41:31. Final freeze is 20:44:50, before final source executions and replay completions at 20:45:08, 20:45:13 and 20:45:18. The final freeze binds all three initial replay reports and the actual initial portfolio. No change to scientific settings, source definitions or scheduled seeds appears in this retained lineage.

The inherited case was already exposed to the controller. The builder also disclosed incidental qualitative historical target wording reached through the former skill-directed README path. This cannot be reclassified as fresh blinded validation; the initial/final decisions and extraction audit preserve the disclosure. The corrected project and installed skill interfaces now direct builders to contracts and admitted source-interface documents, explicitly excluding result documents; exposed evaluation discussion is separated in `docs/ANALYTICAL_VALIDATION_DESIGN.md`.

The controller code contains only the declared source-replay schedule and aggregation. No new target execution/evaluation artifact is part of the reviewed workflow. Receipts and inspected code cannot prove the complete external access history of an Agent on a trusted host. Schedule timing is procedurally committed, not enforced by the portfolio API alone. These limitations are documented and do not invalidate this narrower development result.

The retained test log reports **258 passed, one Windows symlink-fixture skip**; this audit did not rerun tests. Historical replay reports require their recorded engine version, as the schema-2 verifier explicitly states.

## Reviewed artifact hashes

Paths below are relative to this experiment directory.

| Artifact | SHA-256 |
|---|---|
| `protocol.json` | `830790ba3f322717f33094afd3d6d5aa04cf07f7d65c81126164e0e7441effed` |
| `protocol_commitment.json` | `76b2e2cd2bf82b656ff78631860ab7862763685ef2523aeabcdabb7de0d229a7` |
| `initial_portfolio.json` | `17bc4bca660156415604d8ac870aaf8e14fd42e7702728c565ef3f0e9ad28d6c` |
| `final_portfolio.json` | `acf8576d7f7807d1472effd61d215e89d4c7e2c0df551d5c7158a924ee83183b` |
| `comparison.json` | `ba34e9792ed974144a617795c660d625a78674004d4e0b8a99ef234fb3825098` |
| `agent_bundle/candidates/initial/freeze.json` | `e0a4d52cf104e11713f1032a5424c933e4d9f4ae5ee98916b9dc067239480cdd` |
| `agent_bundle/candidates/final/freeze.json` | `7a9524a9c9f8924b6e6449dc18b38e95d7b39bf2e65ca5871a9dc5707c94a757` |
