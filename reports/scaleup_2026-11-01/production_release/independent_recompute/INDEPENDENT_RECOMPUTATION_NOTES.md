# Independent Wave A recomputation

The independent verifier was written and hash-pinned from the frozen JSON/prose contracts before any real or generated cohort table was read. It imports only the Python standard library, NumPy and pandas. It does not import or read either production analysis implementation or the designated evaluator. Only the controller's metadata-event and closure schema was inspected.

The coordinator explicitly authorized data access after all twelve constructors closed and the single matching target-reveal event existed. The verifier independently checked the ledger hash chain, twelve closures, wave inventory, release identity and reveal receipt before opening data. The reveal receipt is `880c642fade4ac1b732e14c1ae830756f0937d923eb807e315df541113218e9a`.

The first independent numerical report was written before any production numerical result was opened:

- `INDEPENDENT_WAVE_A_RESULTS.json`: SHA256 `2070ea209071d39c74749cbab064a83038cec21baaaf5ea7e50ba523def2f4a7`.
- Commitment timestamp: `2026-11-02T22:33:04.130007+00:00`.
- Prepared verifier SHA256: `e2309d74b165a5e4277625df7c0955acebd95a2417393429ee68e1a5f640676d`.

The report includes independent eligibility, full-precision point estimates, sample SDs, reference-only HC3 working intervals, raw and scaled discrepancies, all four margins, constructor bundles, case reliability, zero anchors and the Wave A gate. It covers 36 unique generated target outputs and 72 report slots; all 36 final slots alias initial outputs, so there are no extra final draws or revision gains.

## Independent results before production comparison

| Case | Input rows | Eligible rows | Reference outcome SD (n-1) |
|---|---:|---:|---|
| K01 | 5,059 | 4,394 | Glucose 3.169615166136949 mmol/L |
| K02 | 1,226 | 397 | HDL 20.17555227117999; TC 42.846572546396466 mg/dL |

| Endpoint | Reference point | Reference HC3 working interval |
|---|---:|---|
| K01 glucose/BMI per 5 kg/m² | 0.3138269353025704 | [0.21730623470208732, 0.41034763590305345] |
| K01 glucose/age per 10 years | 0.23224569202655113 | [0.165183757552692, 0.29930762650041026] |
| K01 Female-minus-Male BMI contrast | -0.24395406441449982 | [-0.4181872045148074, -0.06972092431419225] |
| K02 HDL/BMI per 5 kg/m² | -4.623003581925082 | [-8.391954206168002, -0.8540529576821614] |
| K02 TC/BMI per 5 kg/m² | 5.683107656300831 | [-3.753501977218371, 15.119717289820034] |
| K02 lipid residual Pearson correlation | 0.5120696931296308 | Unavailable by frozen contract |

| Margin | K01 passing Agents / 5 | K02 passing Agents / 5 |
|---:|---:|---:|
| 0.05 | 1 | 0 |
| 0.10 | 3 | 0 |
| 0.20 | 5 | 1 |
| 0.30 | 5 | 4 |

Initial and final results are identical because every constructor retained. At the fixed 0.10 margin neither case satisfies the required four-of-five reliability criterion. The three K01 zero-anchor discrepancies are 0.09901105303110193, 0.0732725204333265 and 0.07696646173984117, all within 0.10; K01 is insufficiently discriminating under the frozen rule. The independent positive Wave A gate is false. No Wave B execution is authorized or initiated by these results.

The only specification naming ambiguity concerns the labels of overlapping exclusion counts. The independent report explicitly counts nonfinite values per variable, missing sex, age below the inclusive minimum, and nonpositive BMI/outcomes; eligibility itself is fixed. These working intervals and resolutions are descriptive research checks, not clinical equivalence or population coverage claims.

## Production comparison

The designated production evaluation completed and was then opened for comparison. Its `FULL_EVALUATION.json` SHA256 is `4bcebaffbf0600b0c0e613d8274107c4d952d688e363760ec613ee27870d970d`. The original independent numerical report, verifier and commitment were not changed or rerun.

`compare_production.py` performed 6,704 checks with zero failures. It compares two reference analyses, six reference endpoints, all 36 unique generated tables through all 72 report slots and 216 endpoint slots, the 24 constructor-stage bundles, every point/raw discrepancy/scaled discrepancy, all four margins, comparable exclusion reasons, sample sizes, SDs, HC3 availability and values, design ranks, initial/final pairing and zero revision gains, zero anchors, case reliability, S01 results and the global gates. It reads only the two result JSON files and the independent commitment; it reads no cohort tables or production mathematics.

| Quantity | Maximum absolute difference |
|---|---:|
| Reference point estimates | 0 |
| Reference sample SDs | 0 |
| Generated point estimates | 3.730349362740526e-14 |
| Reference HC3 standard errors | 8.881784197001252e-16 |
| Reference HC3 interval bounds | 3.552713678800501e-15 |
| Zero-anchor numerical values | 0 |
| Initial/final changes | 0 |

All integer counts, provenance/alias identities and Boolean decisions agree exactly. Floating point comparisons use `math.isclose` with absolute and relative tolerances of 1e-12; these are arithmetic roundoff tolerances, not altered scientific margins. The observed differences are at floating point roundoff scale and cannot change any reported margin decision.

The full comparison is `INDEPENDENT_PRODUCTION_COMPARISON.json`, SHA256 `edd56c26e0baaf5a2abe7490d8b6d4ca5a0b0cdfeb9e876c5196e4dd3d7536c8`; `COMPARISON_RECEIPT.json` records the result. The detailed report retains every check and the exact input report hashes. Comparison can be reproduced by running `compare_production.py` with the pinned input reports; its exclusive-create output mode protects the original audit files.

Production's union missing/infinite numeric counts and this verifier's per-variable nonfinite counts have different granularity. They were not falsely equated by summing overlapping counts. Total input/eligible/excluded rows and equivalent sex, age and nonpositive-value exclusions agree exactly. No scientific or numerical discrepancy was found.
