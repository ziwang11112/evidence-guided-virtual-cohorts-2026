# Economy paired-feedback pilot

Evaluation slots: 30/36 executed successfully; 30/36 have complete endpoint sets. Diagnostic slots were separately fixed at 6.

Only two preassigned Sol initial laws received diagnostic sampling. Their feedback and ordinary second-look branches shared the exact initial artifact. All four final review dispositions were sealed before fresh evaluation seeds. Retained/no-op and review-failed branches remain separately identified.

Primary inspection concerns component consistency in generated data. Previously exposed aggregate reference comparisons describe the adjusted analyses and scales; they supply no construction feedback and do not establish fresh clinical confirmation.

| Version | Case | Kind | Arm | Seed | Execution | Analysis |
|---|---|---|---|---:|---|---|
| PNS_SOL_A | PNS | initial | unavailable | 42001 | success | complete |
| PNS_SOL_A | PNS | initial | unavailable | 42003 | success | complete |
| PNS_SOL_A | PNS | initial | unavailable | 42007 | success | complete |
| LIPID_SOL_A | lipids | initial | unavailable | 42001 | success | complete |
| LIPID_SOL_A | lipids | initial | unavailable | 42003 | success | complete |
| LIPID_SOL_A | lipids | initial | unavailable | 42007 | success | complete |
| LIPID_DS | lipids | initial | unavailable | 42001 | candidate_unavailable | unavailable |
| LIPID_DS | lipids | initial | unavailable | 42003 | candidate_unavailable | unavailable |
| LIPID_DS | lipids | initial | unavailable | 42007 | candidate_unavailable | unavailable |
| PNS_DS | PNS | initial | unavailable | 42001 | failed | unavailable |
| PNS_DS | PNS | initial | unavailable | 42003 | failed | unavailable |
| PNS_DS | PNS | initial | unavailable | 42007 | failed | unavailable |
| PNS_SOL_B | PNS | initial | unavailable | 42001 | success | complete |
| PNS_SOL_B | PNS | initial | unavailable | 42003 | success | complete |
| PNS_SOL_B | PNS | initial | unavailable | 42007 | success | complete |
| LIPID_SOL_B | lipids | initial | unavailable | 42001 | success | complete |
| LIPID_SOL_B | lipids | initial | unavailable | 42003 | success | complete |
| LIPID_SOL_B | lipids | initial | unavailable | 42007 | success | complete |
| LIPID_ASTRA | lipids | initial | unavailable | 42001 | success | complete |
| LIPID_ASTRA | lipids | initial | unavailable | 42003 | success | complete |
| LIPID_ASTRA | lipids | initial | unavailable | 42007 | success | complete |
| PNS_ASTRA | PNS | initial | unavailable | 42001 | success | complete |
| PNS_ASTRA | PNS | initial | unavailable | 42003 | success | complete |
| PNS_ASTRA | PNS | initial | unavailable | 42007 | success | complete |
| PNS_SOL_A_SECOND_LOOK | PNS | review | second_look | 42001 | success | complete |
| PNS_SOL_A_SECOND_LOOK | PNS | review | second_look | 42003 | success | complete |
| PNS_SOL_A_SECOND_LOOK | PNS | review | second_look | 42007 | success | complete |
| PNS_SOL_A_FEEDBACK | PNS | review | feedback | 42001 | success | complete |
| PNS_SOL_A_FEEDBACK | PNS | review | feedback | 42003 | success | complete |
| PNS_SOL_A_FEEDBACK | PNS | review | feedback | 42007 | success | complete |
| LIPID_SOL_A_FEEDBACK | lipids | review | feedback | 42001 | success | complete |
| LIPID_SOL_A_FEEDBACK | lipids | review | feedback | 42003 | success | complete |
| LIPID_SOL_A_FEEDBACK | lipids | review | feedback | 42007 | success | complete |
| LIPID_SOL_A_SECOND_LOOK | lipids | review | second_look | 42001 | success | complete |
| LIPID_SOL_A_SECOND_LOOK | lipids | review | second_look | 42003 | success | complete |
| LIPID_SOL_A_SECOND_LOOK | lipids | review | second_look | 42007 | success | complete |

## Component consistency and adjusted analyses

| Version | Endpoint | Unit | Available/3 | Mean | Range | Reference | Mean absolute deviation |
|---|---|---|---:|---:|---|---:|---:|
| PNS_SOL_A | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 3.87137 | [3.6804015734589908, 4.134376845677693] | 3.524 | 0.347377 |
| PNS_SOL_A | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.97878 | [2.903515105287036, 3.124695481242421] | 2.25995 | 0.718838 |
| PNS_SOL_A | residual_correlation | 1 | 3 | 0.593096 | [0.5875029024856263, 0.5989696374346746] | 0.717184 | 0.124089 |
| PNS_SOL_A | sbp.sd_population | mmHg | 3 | 16.9971 | [16.78110215448227, 17.278871897608944] | 18.1916 | 1.19449 |
| PNS_SOL_A | dbp.sd_population | mmHg | 3 | 9.78292 | [9.679144266378927, 9.880952099450237] | 11.0941 | 1.31122 |
| PNS_SOL_A | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 |
| LIPID_SOL_A | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -2.06304 | [-2.295923354611337, -1.7642682109168581] | -4.623 | 2.55996 |
| LIPID_SOL_A | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 10.4564 | [9.194135661472458, 11.508371412545046] | 5.68311 | 4.77327 |
| LIPID_SOL_A | K02-LIPID-RESIDUAL | 1 | 3 | 0.123662 | [0.09188465259108737, 0.14783163233759808] | 0.51207 | 0.388407 |
| LIPID_SOL_A | total_cholesterol.sd_sample | mg/dL | 3 | 35.1286 | [34.805265400030805, 35.559180450155736] | 42.8466 | 7.71795 |
| LIPID_SOL_A | hdl_cholesterol.sd_sample | mg/dL | 3 | 14.6831 | [14.238141658102073, 15.228352623110522] | 20.1756 | 5.4924 |
| LIPID_SOL_A | hdl_above_total_fraction | 1 | 3 | 0.00377778 | [0.003, 0.004333333333333333] | unavailable | unavailable |
| LIPID_DS | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 0 | unavailable | unavailable | -4.623 | unavailable |
| LIPID_DS | K02-TC-BMI | mg/dL per 5 kg/m^2 | 0 | unavailable | unavailable | 5.68311 | unavailable |
| LIPID_DS | K02-LIPID-RESIDUAL | 1 | 0 | unavailable | unavailable | 0.51207 | unavailable |
| LIPID_DS | total_cholesterol.sd_sample | mg/dL | 0 | unavailable | unavailable | 42.8466 | unavailable |
| LIPID_DS | hdl_cholesterol.sd_sample | mg/dL | 0 | unavailable | unavailable | 20.1756 | unavailable |
| LIPID_DS | hdl_above_total_fraction | 1 | 0 | unavailable | unavailable | unavailable | unavailable |
| PNS_DS | bmi_sbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 3.524 | unavailable |
| PNS_DS | bmi_dbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 2.25995 | unavailable |
| PNS_DS | residual_correlation | 1 | 0 | unavailable | unavailable | 0.717184 | unavailable |
| PNS_DS | sbp.sd_population | mmHg | 0 | unavailable | unavailable | 18.1916 | unavailable |
| PNS_DS | dbp.sd_population | mmHg | 0 | unavailable | unavailable | 11.0941 | unavailable |
| PNS_DS | sbp_below_dbp_fraction | 1 | 0 | unavailable | unavailable | 0 | unavailable |
| PNS_SOL_B | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 4.07039 | [3.875816498048015, 4.4099209189790445] | 3.524 | 0.546392 |
| PNS_SOL_B | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.96969 | [2.78448101607623, 3.068884303990858] | 2.25995 | 0.709746 |
| PNS_SOL_B | residual_correlation | 1 | 3 | 0.474186 | [0.4696156300444904, 0.4802881384102413] | 0.717184 | 0.242998 |
| PNS_SOL_B | sbp.sd_population | mmHg | 3 | 20.2867 | [19.91834433717225, 20.542541862616766] | 18.1916 | 2.09512 |
| PNS_SOL_B | dbp.sd_population | mmHg | 3 | 10.8266 | [10.771166792089621, 10.887438459426745] | 11.0941 | 0.267533 |
| PNS_SOL_B | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 |
| LIPID_SOL_B | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -2.18854 | [-2.52761329796936, -1.8727045489957412] | -4.623 | 2.43446 |
| LIPID_SOL_B | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 9.59433 | [9.203380005227189, 10.11812308496366] | 5.68311 | 3.91122 |
| LIPID_SOL_B | K02-LIPID-RESIDUAL | 1 | 3 | 0.109697 | [0.09787293826826489, 0.12117871446503059] | 0.51207 | 0.402372 |
| LIPID_SOL_B | total_cholesterol.sd_sample | mg/dL | 3 | 35.3398 | [35.07304002913, 35.48745555477603] | 42.8466 | 7.50681 |
| LIPID_SOL_B | hdl_cholesterol.sd_sample | mg/dL | 3 | 14.5991 | [14.123956703952027, 14.960237746294439] | 20.1756 | 5.57646 |
| LIPID_SOL_B | hdl_above_total_fraction | 1 | 3 | 0.00344444 | [0.0026666666666666666, 0.005] | unavailable | unavailable |
| LIPID_ASTRA | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -2.21918 | [-2.469128696956434, -2.0485087346959383] | -4.623 | 2.40382 |
| LIPID_ASTRA | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 9.13825 | [8.742470976162588, 9.355958454490086] | 5.68311 | 3.45514 |
| LIPID_ASTRA | K02-LIPID-RESIDUAL | 1 | 3 | 0.105287 | [0.09520835943526919, 0.11550094331155408] | 0.51207 | 0.406783 |
| LIPID_ASTRA | total_cholesterol.sd_sample | mg/dL | 3 | 35.4611 | [35.03437479739842, 35.779547328209276] | 42.8466 | 7.38545 |
| LIPID_ASTRA | hdl_cholesterol.sd_sample | mg/dL | 3 | 14.6004 | [14.129171160975, 14.958591553721874] | 20.1756 | 5.57514 |
| LIPID_ASTRA | hdl_above_total_fraction | 1 | 3 | 0.00388889 | [0.0026666666666666666, 0.005666666666666667] | unavailable | unavailable |
| PNS_ASTRA | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 4.59988 | [4.255866687931089, 4.7752102948806305] | 3.524 | 1.07589 |
| PNS_ASTRA | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 3.22636 | [3.1355805354186193, 3.3592336005347296] | 2.25995 | 0.966413 |
| PNS_ASTRA | residual_correlation | 1 | 3 | 0.375343 | [0.36310265116234225, 0.3949101008109046] | 0.717184 | 0.341841 |
| PNS_ASTRA | sbp.sd_population | mmHg | 3 | 16.9274 | [16.55035999416329, 17.14784208544925] | 18.1916 | 1.26415 |
| PNS_ASTRA | dbp.sd_population | mmHg | 3 | 9.92038 | [9.849560491011681, 9.97169938876442] | 11.0941 | 1.17376 |
| PNS_ASTRA | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 |
| PNS_SOL_A_SECOND_LOOK | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 3.87137 | [3.6804015734589908, 4.134376845677693] | 3.524 | 0.347377 |
| PNS_SOL_A_SECOND_LOOK | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.97878 | [2.903515105287036, 3.124695481242421] | 2.25995 | 0.718838 |
| PNS_SOL_A_SECOND_LOOK | residual_correlation | 1 | 3 | 0.593096 | [0.5875029024856263, 0.5989696374346746] | 0.717184 | 0.124089 |
| PNS_SOL_A_SECOND_LOOK | sbp.sd_population | mmHg | 3 | 16.9971 | [16.78110215448227, 17.278871897608944] | 18.1916 | 1.19449 |
| PNS_SOL_A_SECOND_LOOK | dbp.sd_population | mmHg | 3 | 9.78292 | [9.679144266378927, 9.880952099450237] | 11.0941 | 1.31122 |
| PNS_SOL_A_SECOND_LOOK | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 |
| PNS_SOL_A_FEEDBACK | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 3.87137 | [3.6804015734589908, 4.134376845677693] | 3.524 | 0.347377 |
| PNS_SOL_A_FEEDBACK | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.97878 | [2.903515105287036, 3.124695481242421] | 2.25995 | 0.718838 |
| PNS_SOL_A_FEEDBACK | residual_correlation | 1 | 3 | 0.593096 | [0.5875029024856263, 0.5989696374346746] | 0.717184 | 0.124089 |
| PNS_SOL_A_FEEDBACK | sbp.sd_population | mmHg | 3 | 16.9971 | [16.78110215448227, 17.278871897608944] | 18.1916 | 1.19449 |
| PNS_SOL_A_FEEDBACK | dbp.sd_population | mmHg | 3 | 9.78292 | [9.679144266378927, 9.880952099450237] | 11.0941 | 1.31122 |
| PNS_SOL_A_FEEDBACK | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 |
| LIPID_SOL_A_FEEDBACK | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -2.06585 | [-2.3735021058772823, -1.6729948880368433] | -4.623 | 2.55716 |
| LIPID_SOL_A_FEEDBACK | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 10.4688 | [9.213346376325955, 11.489271044283075] | 5.68311 | 4.78573 |
| LIPID_SOL_A_FEEDBACK | K02-LIPID-RESIDUAL | 1 | 3 | 0.123623 | [0.09197865638604262, 0.14759452722624633] | 0.51207 | 0.388447 |
| LIPID_SOL_A_FEEDBACK | total_cholesterol.sd_sample | mg/dL | 3 | 35.1286 | [34.805265400030805, 35.559180450155736] | 42.8466 | 7.71795 |
| LIPID_SOL_A_FEEDBACK | hdl_cholesterol.sd_sample | mg/dL | 3 | 14.6831 | [14.238141658102073, 15.228352623110522] | 20.1756 | 5.4924 |
| LIPID_SOL_A_FEEDBACK | hdl_above_total_fraction | 1 | 3 | 0.00377778 | [0.003, 0.004333333333333333] | unavailable | unavailable |
| LIPID_SOL_A_SECOND_LOOK | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -2.06304 | [-2.295923354611337, -1.7642682109168581] | -4.623 | 2.55996 |
| LIPID_SOL_A_SECOND_LOOK | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 10.4564 | [9.194135661472458, 11.508371412545046] | 5.68311 | 4.77327 |
| LIPID_SOL_A_SECOND_LOOK | K02-LIPID-RESIDUAL | 1 | 3 | 0.123662 | [0.09188465259108737, 0.14783163233759808] | 0.51207 | 0.388407 |
| LIPID_SOL_A_SECOND_LOOK | total_cholesterol.sd_sample | mg/dL | 3 | 35.1286 | [34.805265400030805, 35.559180450155736] | 42.8466 | 7.71795 |
| LIPID_SOL_A_SECOND_LOOK | hdl_cholesterol.sd_sample | mg/dL | 3 | 14.6831 | [14.238141658102073, 15.228352623110522] | 20.1756 | 5.4924 |
| LIPID_SOL_A_SECOND_LOOK | hdl_above_total_fraction | 1 | 3 | 0.00377778 | [0.003, 0.004333333333333333] | unavailable | unavailable |

Each seed remains a draw from one law. Seed ranges are not confidence intervals; no numeric superiority, equivalence, pooled score, or new acceptance threshold is applied. Component violations are counted without altering delivered values. A feedback contrast uses one shared parent per case and cannot establish a general model-level or causal feedback effect.
