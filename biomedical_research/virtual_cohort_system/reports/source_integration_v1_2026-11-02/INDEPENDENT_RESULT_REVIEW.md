The retained aggregate records are consistent on all four qualified statistics, source-table and execution-receipt hash bindings, row accounting, schema and eligibility outcomes, and source-only execution accounting. No discrepancy affecting these results was found. A 0.002996-second difference between the two timing representations is recorded below. This review establishes consistency of the retained computation records; it does not establish scientific equivalence, original-estimator replay, source reconstruction, transport validity, or improvement.

Reviewed by the independent source-check agent using only the five aggregate JSON artifacts listed below. The reviewer parsed their fields, compared their bindings and values, and computed their file hashes. The independent calculation had already been run once by the coordinator. This review did not rerun that helper, tests, a generator, or a source draw; did not open generated CSV rows, original receipt files, patient data, or target artifacts; and did not add samples.

| Reviewed aggregate artifact | SHA-256 of bytes reviewed |
| --- | --- |
| INDEPENDENT_RECOMPUTATION.json | `975cb3b32a44ac0e41ffe769316852d00693b501aae9a2036eb463e0685ee443` |
| COMPARISON_SUMMARY.json | `540eec332147159572a6aa93998a37f3b8b9115a340f24f0899f1746103bc916` |
| SOURCE_FEEDBACK.json | `6e2b6d9bc349a09a5a375fa5126b7d872ddce757a57bececdea6e0e89bd5db3d` |
| SOURCE_PHASE_RESULT.json | `621b757043f4ffe35c94957c98330162edd3e05b77d015ce4d0c9acab7b1dc4b` |
| SOURCE_RUN_TIMING.json | `ff5669889973fe52519a2112980a390e602a547fc876ae3201de91a679b4baef` |

The feedback packet SHA-256 is `ae843f0311233efab7d27c6aad7b87fdba55dc7bdcf3dd262bbdbb029043fe5f`. It agrees with COMPARISON_SUMMARY.json and was independently reproduced from the embedded packet using sorted JSON keys, compact comma/colon separators, UTF-8, and no trailing newline. This packet digest differs appropriately from the hash of the containing SOURCE_FEEDBACK.json file. The feedback's embedded source-phase object equals SOURCE_PHASE_RESULT.json exactly as parsed. Its source-completion binding is `aa7b783bd7c2c26f3a4b53f4bce5feafc11a5c2a34f91fd31b3d55c98a89a1e3`.

All four retained qualified calculation values equal the corresponding independent coefficient/correlation fields and both calculation fields in COMPARISON_SUMMARY.json exactly as parsed. Each stored recomputation difference is 0.0. The comparison threshold of 1e-10 applies only to numerical recomputation and is not a scientific equivalence margin. The published points and raw differences also agree across the qualified feedback and summary.

| Qualified check | Retained and independent value | Published point | Raw calculated minus published | Native unit | n | Independent design rank |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| Q_J_bmi | 0.11934886227995753 | 0.13 | -0.010651137720042475 | mmol/mol/(kg/m^2) | 1000 | 4 of 4 |
| Q_J_fpg | 2.233082684083217 | 2.29 | -0.05691731591678284 | mmol/mol/(mmol/L) | 1000 | 4 of 4 |
| Q_B_pearson | 0.6197775352761575 | 0.619 | 0.0007775352761575371 | 1 | 1000 | Not applicable |
| Q_M_spearman | 0.5004650964650965 | 0.529 | -0.02853490353490351 | 1 | 1000 | Not applicable |

J retains two separate intercept-including, equal-weight projections: HbA1c IFCC on age/female/BMI and HbA1c IFCC on age/female/FPG. Each design has positive residual degrees of freedom, 996, and both female categories are present. The response conversion is `(hba1c - 2.152) / 0.09148`. Bao retains unadjusted Pearson FPG/HbA1c percent; MIND retains unadjusted Spearman FSG/HbA1c percent with average tied ranks. The MIND operand remains fasting serum glucose. These mappings and conventions do not certify assay equivalence or the original estimators.

Every qualified calculation records `n_input = n_selected = n_used = 1000` and `n_missing_dropped = 0`, with empty selection and missing-policy error. The independent reader records 1000 rows and 1000 distinct nonempty identifiers per source, zero duplicate or blank identifiers, zero malformed records, zero nonfinite/invalid numeric values, and zero age, female, or numeric-minimum schema violations. Each source schema passes. Its calculation conventions explicitly record zero filtered or repaired rows. These aggregate counts agree; this review did not inspect individual records.

All 22 declared source eligibility predicates are accounted for: eight in J and seven each in B and M. Every predicate has n = evaluated = passed = 1000 and failed = unevaluable = 0. Each source has 1000 rows satisfying every predicate and zero rows failing or lacking any predicate evaluation.

| Context | All declared output conditions checked | Result |
| --- | --- | --- |
| J | age >=18; age <=81; female >=0; female <=1; BMI >0; glucose >0; HbA1c >0; glucose <7 | 1000/1000 pass each |
| B | age >=20; age <=80; female >=0; female <=1; BMI >0; glucose >0; HbA1c >0 | 1000/1000 pass each |
| M | age >=61; age <=80; female >=0; female <=1; BMI >0; glucose >0; HbA1c >0 | 1000/1000 pass each |

Integer age and binary female are additionally verified by the common schema counts. J's chosen adult age range remains an assumption; Bao's inclusion of integer age 20 remains the declared boundary convention. Bao does not acquire J's upper glucose cutoff. Unobserved-selection assumptions A_J_SELECTION, A_B_SELECTION and A_M_SELECTION remain explicitly unverified; none of the output counts verifies unavailable clinical, ancestry, family, questionnaire, or follow-up selection variables.

The source-table byte hashes recorded by the independent reader exactly match each corresponding execution-phase entry and both strict and qualified feedback bindings. Execution-receipt hashes also match between source-phase accounting and strict/qualified bindings. Both feedback paths record verified output links for every source.

| Context / trial | Generated source table SHA-256 | Execution receipt SHA-256 |
| --- | --- | --- |
| J / srcJ | `30d0fe67bde01e0f92641760181d773431ad47fffe35fb02322cb6f33da478d6` | `ee6c92f52bbb35c8b616b03fd8dd88768129878b090e7deb7448cfcfd6021c28` |
| B / srcB | `fe82bfdd00a1006c6443ce5faead39c14ba7ee341067e4de33dfce2e35758bae` | `62149789e3e5e48c6d2cbab26ecddc0696475f7669789af1b0f3ac3f6d809f01` |
| M / srcM | `a5e601b4898bd48040f6c3d736ee88138eb37c89cc77360019b2519fc1eba63b` | `42d9f48ba4dccbe09032a59da86324be758bd6a02ddd8cc2e300f23c10c81251` |

The independent report binds helper implementation SHA-256 `dcab6af32f3993f6563b7933204cd84cf2120310e8d5fdc9a0d76b59dd9805fb` and eligibility-declaration SHA-256 `ee15e103178cbb970d7f229aff5b3fb6e60d26d2c117ff1cfca29405aa0e6499`. Those are recorded execution-time bindings, not fresh hashes of their original files in this review. Similarly, receipt/table agreement here is a cross-check of retained records against the byte hashes already computed by the independent reader; original receipt files and CSV bytes were not reopened. Hash bindings are procedural evidence, not independently verified identities or cryptographic signatures.

All three frozen source slots from the governing protocol are represented once: srcJ, srcB and srcM, with matching J/B/M contexts, source role, successful status, consumed attempt and verified generation link. The source-phase record reports three source slots and no unattempted source IDs; the aggregate summary reports three tables and 3000 rows. All three execution diagnostics record return code 0, no host timeout, and no stdout/stderr output. No failed or additional source attempt is present in these records. The aggregate artifacts do not expose receipt seed fields, so this review does not independently reverify the seed bytes or execution environment from the original receipts.

Zero-target scope is consistent across the five records: target attempts = 0; target release authorized = false; target results included = false; target tables = 0; target rows read = 0; independent target inputs read = 0; and all result/report context lists contain only J/B/M. The mechanically reserved dormant target slot was not counted as an executed table. No target result or target validity conclusion is supported.

Strict unavailability remains intact for J_bmi, J_fpg, B_pearson and M_spearman. All four strict results retain `status = not_computable`, `semantic_status = unavailable`, null operator/calculation/difference, source weights and definition status not reported, and Monte Carlo uncertainty not estimated. Their embedded strict copies in qualified feedback equal the corresponding strict feedback records. Strict computable counts remain 0 for every source; not-computable counts are 2/1/1. Qualified feedback separately reports 2/1/1 available checks, equal-weight assumptions, `exact_source_check_allowed = false`, null strict-source differences and pooled loss, and no uncertainty conversion. Unknown original weights, preprocessing, J intercept convention, and M imputation/tie details have not been repaired by the successful qualified calculations.

SOURCE_RUN_TIMING.json records 2026-11-03T04:34:01.362657+00:00 through 2026-11-03T04:34:11.334653+00:00, with `wall_seconds = 9.968999999924563` and scope `dispatch_and_feedback_only`. Subtracting the ISO timestamps gives 9.971996 seconds, 0.002996000075437877 seconds more than the wall-seconds field. The reviewed artifacts do not explain the clock/sampling distinction. This minor timing inconsistency does not change trial, row, hash, or statistic accounting; neither duration represents the entire integration workflow.

Only one draw was made per source. Its simulation uncertainty remains unestimated. The four raw differences are descriptive point discrepancies without precision weighting, interval membership criteria, a pooled objective, or an equivalence conclusion. Output eligibility does not establish full physiological support, original participant reconstruction, or source-to-target validity; the retained qualified review also acknowledges the HbA1c-percent law's possible negative IFCC tail. No additional sample or revision execution is justified or performed by this review.

This review contains aggregate numerical results, counts, decisions and hashes only. Public-export scope remains aggregate metadata only. Generated source tables remain local; this review neither copied nor exported them, and performed no publication action.
