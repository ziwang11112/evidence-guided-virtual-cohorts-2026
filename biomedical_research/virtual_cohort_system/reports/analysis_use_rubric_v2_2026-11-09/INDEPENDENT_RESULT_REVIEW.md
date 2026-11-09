# Independent closed-result review

The recorded run and aggregate report pass this audit, with scientific limitations. All 276 sealed files match the closure inventory and hashes. Both stages, all six fixed-seed executions, both analysis adapters, dual source feedback and all 156 endpoint values are retained. No blocking reporting or provenance discrepancy was found.

This reviewer checked hashes, controller records, aggregate arithmetic and frozen code; individual tables were not parsed and no target outcomes or source bodies were read. The separate arithmetic audits below are attributed to their authors.

## Identity, schedule and author choice

Closure SHA-256: `430dbb0a2dc7991d47e2d6af1afe51c8f41e49afd37342e02c9ea41bcb793626`. Evaluation SHA-256: `21de9d4a833c66f855245202c5458a0b05b3ff9d31bcd689b89d8df3e603a7fa`. Protocol and design-lock bindings also match.

The baseline and `coherent_projection` each completed seeds 9601, 9602 and 9603 with 3,000 eligible observations in every endpoint. Each run has one successful generated analysis, one successful use/coherence analysis and one successful dual-feedback action. All stage means, ranges and selected-minus-baseline differences were recalculated from the retained aggregate values. All endpoint values are computable; none was omitted as unfavorable.

Usage is 30 actions, two candidates, six executions, six feedback actions and twelve analyses. Action `a15` failed preflight with `Semantic recipe hash mismatch`; it remains recorded and charged. `a16` succeeded before `a17` submission. Final selection is the projection candidate after the complete schedule. The author explicitly limits that choice to the stated structural scenario and makes no clinical-improvement claim.

All nine current baseline commitments remain intact. The original generator and model specification are unchanged; the prior namespace correction only changed two evidence paths and two evidence-hash bindings, as documented in [SETUP_REVIEW.md](SETUP_REVIEW.md). Six original files remain byte-identical and all source bytes are unchanged. The revision binds 16 actual baseline artifacts whose copies match their original sealed paths; all 19 check-artifact hashes match.

## Transformations and limitations

The exact generator diff adds an explicit midpoint projection: when HDL exceeds TC, both values become their common midpoint. It adds no random draws, row deletion, rejection or resampling. Existing parameter values are unchanged; one policy string is added. The frozen analysis provider requires all 3,000 observations to satisfy its fixed eligibility rules, so a silent posthoc eligibility subset cannot explain these results. The lipid values are intentionally modified; this is a disclosed transformation.

The [separate coherence audit](COHERENCE_RECOMPUTATION.json) independently parsed saved outputs and confirmed unchanged IDs, age, sex and BMI, unchanged nonviolating pairs, and exactly 5, 5 and 6 changed lipid pairs. Baseline violations of 5, 5 and 6 become zero, with no missing/unknown pairs. Every changed pair becomes TC=HDL, creating 5, 5 and 6 artificial zero-non-HDL values. This unsupported boundary probability is a material limitation. This reviewer verified the audit's closure, evaluation, protocol, script and output bindings rather than duplicating its row calculations.

The [endpoint recomputation](RECOMPUTATION.json) passed all 156 checks, with maximum absolute arithmetic difference `1.1723955140041653e-13`. This is floating-point agreement, not biological equivalence.

## Every endpoint mean change

These are descriptive changes across three seeds; the signs are not judgments of clinical benefit. No clinical equivalence margin was specified.

| Endpoint | Baseline mean | Selected mean | Selected minus baseline | Unit |
|---|---:|---:|---:|---|
| K02-HDL-BMI | -1.150084356 | -1.137195445 | 0.01288891116 | mg/dL per 5 kg/m^2 |
| K02-TC-BMI | 8.630396114 | 8.617507203 | -0.01288891116 | mg/dL per 5 kg/m^2 |
| K02-LIPID-RESIDUAL | 0.1854108988 | 0.1882811142 | 0.00287021536 | 1 |
| age.mean | 38.7044955 | 38.7044955 | 0 | year |
| age.sd_sample | 16.35741101 | 16.35741101 | 0 | year |
| age.q10 | 19.18958812 | 19.18958812 | 0 | year |
| age.q50 | 36.21195975 | 36.21195975 | 0 | year |
| age.q90 | 61.77690414 | 61.77690414 | 0 | year |
| bmi.mean | 24.12703987 | 24.12703987 | 0 | kg/m^2 |
| bmi.sd_sample | 5.214679879 | 5.214679879 | 0 | kg/m^2 |
| bmi.q10 | 18.07501217 | 18.07501217 | 0 | kg/m^2 |
| bmi.q50 | 23.53126225 | 23.53126225 | 0 | kg/m^2 |
| bmi.q90 | 30.96751779 | 30.96751779 | 0 | kg/m^2 |
| total_cholesterol.mean | 154.9726218 | 154.9852135 | 0.01259170246 | mg/dL |
| total_cholesterol.sd_sample | 31.55171159 | 31.53644323 | -0.01526835625 | mg/dL |
| total_cholesterol.q10 | 116.7885185 | 116.7885185 | 0 | mg/dL |
| total_cholesterol.q50 | 152.1851149 | 152.2077495 | 0.02263455251 | mg/dL |
| total_cholesterol.q90 | 196.2044688 | 196.2044688 | 0 | mg/dL |
| hdl_cholesterol.mean | 56.80447863 | 56.79188693 | -0.01259170246 | mg/dL |
| hdl_cholesterol.sd_sample | 18.3426086 | 18.29139704 | -0.05121155182 | mg/dL |
| hdl_cholesterol.q10 | 36.51762081 | 36.51762081 | 0 | mg/dL |
| hdl_cholesterol.q50 | 53.97068507 | 53.97068507 | 0 | mg/dL |
| hdl_cholesterol.q90 | 80.97675741 | 80.95146909 | -0.02528831897 | mg/dL |
| total_cholesterol.conditional_rms | 29.95914462 | 29.94797389 | -0.01117072168 | mg/dL |
| hdl_cholesterol.conditional_rms | 18.16623083 | 18.11638114 | -0.04984968477 | mg/dL |
| sex.F_fraction | 0.5487777778 | 0.5487777778 | 0 | 1 |

## Source discrepancies and unresolved evidence

Every run retains 29 unavailable strict comparisons. Descriptive feedback has 22 assumed-convention checks, four known weighting mismatches and three unsupported checks. Across the 66 comparable check/seed pairs, absolute discrepancies move farther from the source statistic in 16, closer in 18 and remain unchanged in 32. The other 21 paired checks have unavailable or mismatched source differences and are not ranked. Counts are descriptive bookkeeping, not independent confirmations or a quality score.

Every farther discrepancy is listed below; the JSON companion retains all 87 paired source checks. Exact floating-point changes are shown without a scientific success threshold.

| Seed | Source check | Baseline difference | Selected difference | Increase in absolute difference |
|---:|---|---:|---:|---:|
| 9601 | check_z0_total_cholesterol_mean | 0.005873467129 | 0.006139872028 | 0.0002664048988 |
| 9601 | check_z0_total_cholesterol_sd | -0.00865934183 | -0.008998733798 | 0.0003393919677 |
| 9601 | check_ashanti_rural_bmi_hdl_cholesterol | 0.03232271515 | 0.03235840448 | 3.56893373e-05 |
| 9601 | check_ashanti_rural_total_cholesterol_hdl_cholesterol | 0.05084242543 | 0.05117386946 | 0.0003314440368 |
| 9601 | check_ashanti_urban_bmi_total_cholesterol | -0.01515440291 | -0.01525153403 | 9.71311219e-05 |
| 9602 | check_z0_total_cholesterol_mean | 0.007386470837 | 0.008024474081 | 0.0006380032434 |
| 9602 | check_z0_hdl_cholesterol_mean | -0.0001166458348 | -0.0007546490782 | 0.0006380032434 |
| 9602 | check_z0_hdl_cholesterol_sd | -0.009459540446 | -0.01209704573 | 0.002637505283 |
| 9602 | check_ashanti_rural_bmi_hdl_cholesterol | 0.002392100266 | 0.00247037183 | 7.827156425e-05 |
| 9602 | check_ashanti_rural_total_cholesterol_hdl_cholesterol | 0.02709546946 | 0.02805139356 | 0.0009559241062 |
| 9602 | check_ashanti_urban_bmi_total_cholesterol | -0.0132877387 | -0.01389248232 | 0.0006047436227 |
| 9603 | check_z0_total_cholesterol_mean | 0.009792235464 | 0.01041835078 | 0.0006261153191 |
| 9603 | check_z0_hdl_cholesterol_sd | -0.002530612741 | -0.004835412162 | 0.002304799421 |
| 9603 | check_ashanti_rural_bmi_hdl_cholesterol | 0.06192692821 | 0.06195705977 | 3.01315589e-05 |
| 9603 | check_ashanti_rural_total_cholesterol_hdl_cholesterol | 0.05134265526 | 0.05197729844 | 0.0006346431816 |
| 9603 | check_ashanti_urban_bmi_hdl_cholesterol | 0.001926928214 | 0.001957059773 | 3.01315589e-05 |

All three requested uses remain submitter-declared partial, despite exact ID/estimand coverage. No new acquisition action occurred. Measured-to-underlying transfer, transport, conditional dependence, selection, tails, the projection metric/boundary atom and uncertainty remain unresolved. The [scientific review](SCIENTIFIC_REVIEW.md) addresses those assumptions separately.

The result demonstrates the recorded effect of an explicit structural constraint in one development case. It establishes neither clinical accuracy nor target-population recovery, calibrated uncertainty, a causal rubric benefit, or general Agent advantage. The ledger and closed inventory support the recorded workflow; procedural author boundaries do not constitute complete OS isolation.
