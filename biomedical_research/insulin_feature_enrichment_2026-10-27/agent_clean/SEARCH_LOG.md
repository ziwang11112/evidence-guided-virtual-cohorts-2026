# Screened literature search, initial construction

Date: 2026-10-27. Every search and fetch used the experiment-root `literature_gateway.py` CLI with `python -B`. All limits were 10. No browser, general search tool, raw request, alternate download, target-data access or rejected-source inspection was used. Approved texts were inspected locally. Sources were chosen by the generating agent, without supplied biological parameters.

| Order | Exact substantive query | Accepted / screened; rejected | Outcome |
|---|---|---|---|
| 1 | `fasting insulin BMI age sex healthy adults reference interval` | 7/10; 3 | Broad unfielded query yielded mostly irrelevant recent studies. No quantitative model evidence taken from these results. |
| 2 | `TITLE_ABS:"fasting insulin" AND TITLE_ABS:"reference" AND FIRST_PDATE:[1990-01-01 TO 2024-12-31]` | 10/10; 0 | S1 Brazilian reference paper and S2 lifespan paper selected. Duplicate Brazilian preprint not counted. Pregnancy, SLE and other disease-specific results not pursued. |
| 3 | `TITLE_ABS:"fasting insulin" AND TITLE_ABS:"body mass index" AND TITLE_ABS:"healthy" AND FIRST_PDATE:[1990-01-01 TO 2020-12-31]` | 10/10; 0 | S3 community study selected for separately reported non-diabetic BMI groups. Adolescent, pregnancy and diabetes-treatment studies not used. |
| 4 | `TITLE_ABS:"fasting insulin" AND TITLE_ABS:"Framingham" AND FIRST_PDATE:[1990-01-01 TO 2024-12-31]` | 10/10; 0 | S4 selected to examine U.S. community age/sex/adiposity evidence. Other Framingham papers not counted as independent confirmation. |
| 5 | `TITLE_ABS:"fasting insulin" AND TITLE_ABS:"body mass index" AND TITLE_ABS:"nondiabetic" AND FIRST_PDATE:[2000-01-01 TO 2024-12-31]` | 10/10; 0 | S5 MILES selected. Its mediation estimates do not identify the needed BMI slope, so it was not used numerically. |
| 6 | `TITLE_ABS:"fasting insulin" AND TITLE_ABS:"BMI" AND TITLE_ABS:"regression" AND TITLE_ABS:"adult" AND FIRST_PDATE:[1990-01-01 TO 2022-12-31]` | 9/10; 1 | S6 controlled physiology study selected for lean and obese non-diabetic subgroup comparison. Other results did not resolve continuous BMI coefficient gap. |

Approved search artifacts, in corresponding order, are under `literature/approved/`:

1. `search_72ee838473f3351ef8d5dbaeb821031d55795d352d8c7bb9bc4940b83ffa72d0.json`
2. `search_a2667e2f4437b09b50aedf852a35148cd3cce9baabc91caa33830115a42f04a0.json`
3. `search_417263d3d3b4ca1e086526d68cc26ed361b7023d91ec57ff32ff71906d5d7b85.json`
4. `search_b4d3c8a0c7cf120853917682aa1caff0f1a49b6e4be0abe56a5c8376f7791cee.json`
5. `search_f01a83ad9d12afbf3cdb63d7d1592d210ad84ee12b10523ad242c3c59de365a8.json`
6. `search_b94554d63c1aee4223525e2b4793efe967273e6ffdaa5e41798109e9a8e6ad86.json`

Each hash in the filename is the gateway-reported SHA256. Query 2 was repeated once, unchanged, only to recover its approved-artifact metadata after combined tool output truncation. It was not an additional scientific query. Six substantive queries and seven search invocations were made, below the requested initial cap of 12. The fourth query and fifth query were independently run in parallel; neither used the other's returned evidence.

Fetches, all accepted after full retrieved-XML screening including references, in order: `PMC11554367`, `PMC10350850`, `PMC6887811`, `PMC8862500`, `PMC9165426`, `PMC8169863`. All screened identifiers, DOIs, URLs, approved fulltext paths and hashes are in `EVIDENCE_LEDGER.json`. No fetch was rejected. The four search-level rejected items were unavailable; reasons/identities were not investigated or inferred.

The main text of S2 refers to adjusted BMI/age/sex analyses in supplementary tables, which the gateway did not retrieve. S4 uses waist circumference and exam-standardized insulin, preventing direct transfer of its coefficient to BMI/log-uU/mL. S5's mediation quantity is a different estimand. These gaps remain explicitly unresolved. No supplementary content was fetched by another route.

Search stopped after six approved primary fulltexts: three quantitatively inform the model, two give contrasting/contextual evidence, and one is documented nonuse. Enough source material exists to construct a tractable conditional simulator, but not to identify a validated target conditional distribution. Further searching was unlikely to remove the population/assay and aggregate-to-conditional transport assumptions within this initial pilot. No result-based source or model selection occurred.
