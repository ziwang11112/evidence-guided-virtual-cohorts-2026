# PNS HbA1c task preparation

Prepared 7,979 participants from 8,952 official laboratory records. This package supports enrichment of fully hidden HbA1c from visible baseline age, sex and measured BMI. No scientific generator or target-distribution/association analysis was run.

## Eligibility and missingness

Baseline age is C008, explicitly labelled age from the IBGE base, restricted to 20–79 inclusive. Z002 is not used because its time reference is unspecified. The supplied dictionary declares no age topcoding.

Measured weight z004 is in kg (dictionary validity 30–200); measured height z005 is in cm (120–210). BMI = z004 / (z005 / 100)^2. Error code 999 and unavailable anthropometry are excluded. There is no additional BMI trimming.

P005==1 excludes reported pregnancy at the baseline interview. Unknown and inapplicable/missing values remain. This does not establish pregnancy status during the later laboratory visit. All remaining participants with finite positive peso_lab and available numeric finite Z034 are preserved. No target magnitude threshold or target-derived diagnostic/proxy condition is used. Additional complete-case restrictions are not corrected by new weights.

| Step | Remaining | Excluded at step |
| --- | ---: | ---: |
| all_official_lab_records | 8,952 | 0 |
| baseline_age_20_to_79 | 8,439 | 513 |
| documented_sex_code | 8,439 | 0 |
| dictionary_valid_measured_weight_height | 8,352 | 87 |
| not_reported_pregnant_at_baseline | 8,352 | 0 |
| finite_positive_lab_weight | 8,352 | 0 |
| hba1c_available_numeric_finite | 7,979 | 373 |

## Timing and design

The interview is from 2013, while the official laboratory page dates the second-stage collection to 2014–2015. Baseline pregnancy and age should not be read as lab-date measurements. Exact participant measurement dates are unavailable.

The workbook has 509 columns and supplies peso_lab. It supplies no explicit PSU, stratum or official person-ID column. Region is not substituted for a sampling stratum. ID mapping therefore records sealed source worksheet row positions, not an invented official ID. A full-interview join was not attempted without a stable public key.

The estimand is the lab-complete participant distribution under the provided weights, with an unweighted sensitivity analysis. National representativeness is not assumed. The official page describes post-stratification by age, education, race/color and macroregion; weight-calibration interpretation remains unresolved. Later evaluation may use weighted point estimates and unweighted sensitivity, but no design-based uncertainty until a valid design is recovered. The parent identified a calibration-methods paper for further methodological review: https://www.scielo.br/j/rbepid/a/WCZswnbNLN9FyYkQmvJtKTs/?lang=pt . Its results were not inspected in this preparation.

## Custody and artifacts

Builder access is limited to `visible/` and approved external evidence. `visible/observed.csv` contains only opaque row_id, age_years, sex and bmi_kg_m2. Z034 is held in `custodian/reference.csv`; peso_lab is held unchanged in `custodian/design_weights.csv`; original worksheet positions are held in `custodian/id_mapping.csv`. The secret used for opaque IDs is retained only in the custodian directory. Rows are sorted by opaque ID, not source order.

Z035 (estimated average glucose) and every other HbA1c-derived diagnostic/proxy field are excluded from visible data. The full official workbook remains in the custodian raw archive. Custody is procedural in the shared filesystem and does not claim OS isolation or anonymization. This is a fresh project case only, not a claim of pretraining cleanliness.

`visible/field_map.json` retains exact dictionary entries, worksheet cell ranges and the source header inventory. `visible/source_manifest.json` contains official URLs and hashes. `task.json` and `visible/task.json` are identical validated contracts. Evidence budgets are 0 queries, 0 downloads and 2 revisions for the shared evidence packet; acquisition of custodian preparation data is distinct from the generation budget.

## Reproduction and validation

Use the bundled Python runtime with pandas, numpy and openpyxl. Run `download_sources.py`, then `prepare_pns.py` from this directory. Keep `custodian/id_secret.bin` for bit-for-bit row identities and ordering. The preparation verifies the ZIP and dictionary hashes and that the ZIP's dictionary equals the separately downloaded dictionary.

Task validation, visible-input validation, reference structural/observed-cell preservation, unique opaque IDs and reference/design/mapping alignment passed. These are structural checks only. No target mean, spread, quantile, prevalence, association, coefficient sign or plot was computed or exposed.

Official source page: https://www.pns.icict.fiocruz.br/bases-de-dados/

Official laboratory methods page: https://www.pns.icict.fiocruz.br/exames-laboratoriais/

ZIP SHA256: `d31544efdad138f3292ab86c9606cd722bf091781cc86ef371354ba63c9994bb`

Dictionary SHA256: `5aa4a3685fa2b1a9b8aa3739e3da2b83cf72fdb0affe988f2b6cc4442a6833c0`
