# Evidence composition pilot — results

This unit tests exact-moment composition in artificial populations. It does not establish clinical transport, literature-search reliability or workflow superiority.

Completed 24/24 constructions and 72 tables. All 216 predefined analysis estimates are retained. Three random draws per author are nested repetitions, not new independent authors.

| Family | Evidence | Authors | Primary range across author means | MAE when identified | Source checks within tolerance | Correct identification labels |
|---|---|---:|---:|---:|---:|---:|
| adjusted | none | 3 | -0.4930 to -0.2380 | Not an error score | 54/54 | 9/9 |
| adjusted | anchor_only | 3 | 0.2926 to 0.3387 | Not an error score | 63/63 | 9/9 |
| adjusted | bridge_only | 3 | 0.2615 to 0.2624 | Not an error score | 72/72 | 9/9 |
| adjusted | combined | 3 | 0.2211 to 0.2230 | 0.00731 | 81/81 | 9/9 |
| longitudinal | none | 3 | -0.4911 to -0.2966 | Not an error score | 108/108 | 9/9 |
| longitudinal | anchor_only | 3 | 0.2893 to 0.2907 | Not an error score | 117/117 | 9/9 |
| longitudinal | bridge_only | 3 | 0.1911 to 0.5923 | Not an error score | 117/117 | 9/9 |
| longitudinal | combined | 3 | -0.6013 to -0.5991 | 0.01492 | 126/126 | 9/9 |

All identified primary/secondary analyses: 90/90 inside the preregistered numerical tolerance. Source diagnostics: 738/738. Identification labels: 72/72.

## How to read the result

The reference line appears only where the primary estimand is identified. A source-consistent point scenario in an incomplete-evidence cell is not counted as incorrect because it differs from that line. Narrow variation across authors or seeds is not evidence that an assumed relationship is correct.

## Implementation and cost

Requested and returned models: ['gpt-6.1-sol'] / ['gpt-6.1-sol']. Calls: 24; returned-usage tariff estimate: $0.654076; unresolved charge reservations: $0.000000. These are tariff estimates, not invoices.

Covariance-based recomputation checked 216 estimates across 72 tables. Maximum discrepancy: 1.17e-15. Independently coded by the same root assistant, not independent personnel adjudication.

Recorded failures: 0. Complete failures are in analysis/failures.json; all calls, scientific programs, specifications and output tables remain local.

## Files

- `PROTOCOL.md`, `FREEZE.json`: fixed design and hashes.
- `inputs/`: exact approved records, schema and prompts.
- `calls/`: requests, raw responses, usage and cost receipts.
- `candidates/`: model-authored code, provenance, sealed specifications.
- `executions/`: isolated execution bindings, logs and generated rows.
- `analysis/constructor_analyses.csv`: all author-level results and declared values.
- `analysis/cell_summary.csv`, `analysis/identification_labels.csv`: complete summaries.
- `analysis/INDEPENDENT_RECOMPUTATION.json`: alternative numerical route.
- `analysis/evidence_composition.png` and `.pdf`: result figure.

See `IMPLEMENTATION_REVIEW.md` for code-level interpretation and the next-step decision.
