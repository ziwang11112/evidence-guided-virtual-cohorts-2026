# Final HRS result review

**PASS.** Independent audit of the completed, explicitly recovered public-example experiment. No new generation, model fitting, parameter change or frozen-file edit occurred.

## Complete numerical reconciliation

- All **32 coefficient summary groups** and **54 distribution summary groups** were independently reconstructed from the six retained native evaluator JSON files, including means, ranges, signed mean discrepancies and mean absolute discrepancies.
- All **96 all-seed coefficient rows** and **162 all-seed diagnostic rows**, plus both summary CSVs, match retained native results and source references.
- The three corrected tables were read only to independently calculate **81 baseline statistics**; maximum disagreement was **1.42e-14**. The earlier Agent-only audit already checked its 81 baseline values and was not rerun.
- All six retained fits have 16 estimable terms, optimizer code 0, no warnings and no singularity; all six existing conditional GLS checks pass. No fit was repeated.
- All original and recovery release hashes and the previous Agent result/table hashes remain unchanged.

## Concrete focal results

| Construction | Focal coefficient | Source | Three-seed mean | Seed range | Mean absolute discrepancy |
|---|---|---:|---:|---|---:|
| native | age60:hba1c_U65 | -0.046837 | -0.040500 | -0.047478 to -0.036550 | 0.006764 |
| native | age60:hba1c_O65 | 0.012867 | -0.011691 | -0.026974 to -0.002345 | 0.024558 |
| agent | age60:hba1c_U65 | -0.046837 | -0.044635 | -0.051059 to -0.038247 | 0.005017 |
| agent | age60:hba1c_O65 | 0.012867 | 0.026485 | 0.013677 to 0.036768 | 0.013618 |

Both implementations preserve the negative below-threshold interaction in every draw. The weak above-threshold interaction has positive point estimates in the three Agent draws and negative estimates in the three corrected-law draws. All corrected-law intervals include zero; one Agent interval excludes zero. These six finite draws from nearly the same supplied family do not establish an accuracy ranking, and binary significance agreement is not an appropriate sole quality claim.

The upper-HbA1c subgroup mean/SD are approximately **7.15149 / 0.56305** in both constructions, compared with **7.7 / 1.4** for the reported original sample and **7.2 / 0.6** for the paper's synthetic-law summary. The source-law reconstruction is useful but inherits the original simulator's distribution mismatch. The report preserves this unfavorable result.

## Accounting and interpretation

The ledger contains **nine physical generation attempts**: six initial attempts and three separately released technical corrections. The three invalid initial comparator tables remain visible and are excluded from comparative ranking. The six valid comparison tables are three draws per construction, not six clinical studies or six independent authoring decisions. All Agent outputs are unchanged. No further recovery or favorable-seed search is authorized by this closure.

`RESULTS.md` correctly describes the original model coefficients as permitted inputs, distinguishes source-rich reconstruction from unseen-relationship validation, discloses the parser defect and byte-identical correction, and makes no superiority, fully autonomous literature search, human-cost or transport claim. The Agent's printed-variance convention and the comparator's squared-rounded-SD convention are disclosed. The real source had 43,500 observations; balanced synthetic schedules have 46,036 visits, so their model SEs cannot be read as added patient evidence.

The capability demonstrated is an Agent-authored complete longitudinal table that supports the supplied scientific model, with all effects and diagnostic discrepancies exposed. This audit does not certify novel simulation mathematics, independent clinical truth or exact empirical-tail recovery. Plot rendering is the coordinator's separate review responsibility.

Complete arithmetic, file bindings and all checked values are retained in `FINAL_RESULT_REVIEW.json`.
