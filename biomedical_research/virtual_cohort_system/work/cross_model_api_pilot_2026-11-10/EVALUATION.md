# Cross-model API construction pilot: scientific analysis

Scheduled constructions: 20. Scheduled seed slots: 60. Successful executions: 42/60. Complete endpoint sets: 42/60.

All initial and final constructions were sealed before execution. Only existing aggregate references were reused. These are developmental results; no patient rows were read and no reference model was refit.

- Developmental comparison using previously exposed clinical aggregate references; no new clinical confirmation.
- One construction per case/model configuration/context; repeated seeds are draws from one authored law, not independent constructions or clinical studies.
- No source or target quality feedback was supplied during construction; at most one static mechanical repair preceded the construction seal.
- The three adjusted estimands are association projections, not causal intervention effects or proof of individual-row recovery.
- No new numerical acceptance cutoff, pooled cross-unit score, significance test, superiority gate, or equivalence claim is introduced.
- PNS weights describe the declared finite analytical distribution; supplied row-resampling intervals are not design-based national-population confidence intervals.
- Lipid reference slopes use the existing selected complete-case sample and HC3 conditional sensitivity intervals; assay and population equivalence are not established by unit conversion.
- Missing reference diagnostics remain unavailable; no patient rows, new clinical fits, or reference recalibration are used.
- Host-side hashes audit bytes relative to commitments, not cryptographic signatures against a host rewriting artifacts and receipts together.

## Primary adjusted estimands

| Construction | Endpoint | Unit | Available/3 | Seed mean | Seed range | Reference | Mean signed difference | Mean absolute difference |
|---|---|---|---:|---:|---|---:|---:|---:|
| PNS_OA_ASTRA_C1 | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 3.5526 | [3.347870049072855, 3.704074619657703] | 3.524 | 0.0286054 | 0.146022 |
| PNS_OA_ASTRA_C1 | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.73619 | [2.679003153283017, 2.7888002862176147] | 2.25995 | 0.476248 | 0.476248 |
| PNS_OA_ASTRA_C1 | residual_correlation | 1 | 3 | 0.608423 | [0.6043007470575507, 0.6120049873537314] | 0.717184 | -0.108761 | 0.108761 |
| LIPID_OA_ASTRA_C1 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -1.66785 | [-1.9256496941046586, -1.4322791627135905] | -4.623 | 2.95515 | 2.95515 |
| LIPID_OA_ASTRA_C1 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 10.7745 | [10.64883126255808, 10.962844950610657] | 5.68311 | 5.09139 | 5.09139 |
| LIPID_OA_ASTRA_C1 | K02-LIPID-RESIDUAL | 1 | 3 | 0.123467 | [0.10665042786144326, 0.13509803763207345] | 0.51207 | -0.388603 | 0.388603 |
| LIPID_DS_PRO_C1 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -1.20243 | [-1.3314753127941525, -1.0998763569761525] | -4.623 | 3.42057 | 3.42057 |
| LIPID_DS_PRO_C1 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 7.83465 | [7.377223976717174, 8.17574363964617] | 5.68311 | 2.15154 | 2.15154 |
| LIPID_DS_PRO_C1 | K02-LIPID-RESIDUAL | 1 | 3 | 0.150722 | [0.1332308090802847, 0.17012362730235622] | 0.51207 | -0.361347 | 0.361347 |
| PNS_DS_PRO_C1 | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 4.00777 | [3.9174921518358863, 4.060860026178732] | 3.524 | 0.48377 | 0.48377 |
| PNS_DS_PRO_C1 | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 3.09178 | [2.928388887431154, 3.2135196844333755] | 2.25995 | 0.83183 | 0.83183 |
| PNS_DS_PRO_C1 | residual_correlation | 1 | 3 | 0.466529 | [0.45363875691925715, 0.4779228370129587] | 0.717184 | -0.250655 | 0.250655 |
| PNS_CL_FABLE_C1 | bmi_sbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 3.524 | unavailable | unavailable |
| PNS_CL_FABLE_C1 | bmi_dbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 2.25995 | unavailable | unavailable |
| PNS_CL_FABLE_C1 | residual_correlation | 1 | 0 | unavailable | unavailable | 0.717184 | unavailable | unavailable |
| LIPID_CL_FABLE_C1 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -1.25716 | [-1.6858838355117785, -0.9495746975781134] | -4.623 | 3.36584 | 3.36584 |
| LIPID_CL_FABLE_C1 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 9.36892 | [8.804981853230085, 10.334203886161028] | 5.68311 | 3.68581 | 3.68581 |
| LIPID_CL_FABLE_C1 | K02-LIPID-RESIDUAL | 1 | 3 | 0.332721 | [0.3263350889585133, 0.3436238986747609] | 0.51207 | -0.179349 | 0.179349 |
| LIPID_GE_CARBON_C1 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 0 | unavailable | unavailable | -4.623 | unavailable | unavailable |
| LIPID_GE_CARBON_C1 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 0 | unavailable | unavailable | 5.68311 | unavailable | unavailable |
| LIPID_GE_CARBON_C1 | K02-LIPID-RESIDUAL | 1 | 0 | unavailable | unavailable | 0.51207 | unavailable | unavailable |
| PNS_GE_CARBON_C1 | bmi_sbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 3.524 | unavailable | unavailable |
| PNS_GE_CARBON_C1 | bmi_dbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 2.25995 | unavailable | unavailable |
| PNS_GE_CARBON_C1 | residual_correlation | 1 | 0 | unavailable | unavailable | 0.717184 | unavailable | unavailable |
| PNS_OA_SOL_C1 | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 3.93088 | [3.6042059812493346, 4.155223281971361] | 3.524 | 0.406886 | 0.406886 |
| PNS_OA_SOL_C1 | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.68431 | [2.3113536863354893, 2.909205874006384] | 2.25995 | 0.424361 | 0.424361 |
| PNS_OA_SOL_C1 | residual_correlation | 1 | 3 | 0.545167 | [0.5256902644703683, 0.5621106747680523] | 0.717184 | -0.172017 | 0.172017 |
| LIPID_OA_SOL_C1 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -1.69323 | [-2.1207731599343127, -1.3425899402153372] | -4.623 | 2.92977 | 2.92977 |
| LIPID_OA_SOL_C1 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 8.45229 | [8.352335020388631, 8.614604752514373] | 5.68311 | 2.76919 | 2.76919 |
| LIPID_OA_SOL_C1 | K02-LIPID-RESIDUAL | 1 | 3 | 0.138836 | [0.13599939755454188, 0.1402817926103381] | 0.51207 | -0.373233 | 0.373233 |
| LIPID_OA_ASTRA_C2 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -1.9094 | [-2.200931086653483, -1.6061211736639356] | -4.623 | 2.7136 | 2.7136 |
| LIPID_OA_ASTRA_C2 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 9.63087 | [9.540018561374946, 9.730707301223376] | 5.68311 | 3.94776 | 3.94776 |
| LIPID_OA_ASTRA_C2 | K02-LIPID-RESIDUAL | 1 | 3 | 0.123394 | [0.10475842594069819, 0.13446251675587317] | 0.51207 | -0.388676 | 0.388676 |
| PNS_OA_ASTRA_C2 | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 3.82358 | [3.533906780540581, 4.388103004149227] | 3.524 | 0.299586 | 0.299586 |
| PNS_OA_ASTRA_C2 | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.78188 | [2.4412958797182283, 3.166441295474675] | 2.25995 | 0.521934 | 0.521934 |
| PNS_OA_ASTRA_C2 | residual_correlation | 1 | 3 | 0.572447 | [0.5629710145623186, 0.5775774720054322] | 0.717184 | -0.144738 | 0.144738 |
| PNS_DS_PRO_C2 | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 3.81481 | [3.508484400033329, 4.101496470682362] | 3.524 | 0.290814 | 0.301155 |
| PNS_DS_PRO_C2 | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.94661 | [2.8982448841265924, 3.036713341460312] | 2.25995 | 0.686667 | 0.686667 |
| PNS_DS_PRO_C2 | residual_correlation | 1 | 3 | 0.488411 | [0.47629039530279405, 0.4961770819172367] | 0.717184 | -0.228773 | 0.228773 |
| LIPID_DS_PRO_C2 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -1.59861 | [-1.8205818828794071, -1.1573432939358401] | -4.623 | 3.0244 | 3.0244 |
| LIPID_DS_PRO_C2 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 7.86745 | [7.568117361055791, 8.332185675730752] | 5.68311 | 2.18434 | 2.18434 |
| LIPID_DS_PRO_C2 | K02-LIPID-RESIDUAL | 1 | 3 | 0.0973546 | [0.0692380217301208, 0.11536731386035172] | 0.51207 | -0.414715 | 0.414715 |
| LIPID_CL_FABLE_C2 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -1.20656 | [-1.3376912302307833, -1.0709812503492933] | -4.623 | 3.41645 | 3.41645 |
| LIPID_CL_FABLE_C2 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 9.3408 | [8.31462686848765, 10.685717220302477] | 5.68311 | 3.6577 | 3.6577 |
| LIPID_CL_FABLE_C2 | K02-LIPID-RESIDUAL | 1 | 3 | 0.382356 | [0.36821200800543763, 0.4043000627583962] | 0.51207 | -0.129714 | 0.129714 |
| PNS_CL_FABLE_C2 | bmi_sbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 3.524 | unavailable | unavailable |
| PNS_CL_FABLE_C2 | bmi_dbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 2.25995 | unavailable | unavailable |
| PNS_CL_FABLE_C2 | residual_correlation | 1 | 0 | unavailable | unavailable | 0.717184 | unavailable | unavailable |
| PNS_GE_CARBON_C2 | bmi_sbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 3.524 | unavailable | unavailable |
| PNS_GE_CARBON_C2 | bmi_dbp | mmHg per 5 kg/m^2 | 0 | unavailable | unavailable | 2.25995 | unavailable | unavailable |
| PNS_GE_CARBON_C2 | residual_correlation | 1 | 0 | unavailable | unavailable | 0.717184 | unavailable | unavailable |
| LIPID_GE_CARBON_C2 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 0 | unavailable | unavailable | -4.623 | unavailable | unavailable |
| LIPID_GE_CARBON_C2 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 0 | unavailable | unavailable | 5.68311 | unavailable | unavailable |
| LIPID_GE_CARBON_C2 | K02-LIPID-RESIDUAL | 1 | 0 | unavailable | unavailable | 0.51207 | unavailable | unavailable |
| LIPID_OA_SOL_C2 | K02-HDL-BMI | mg/dL per 5 kg/m^2 | 3 | -1.97473 | [-2.1573702502691523, -1.7460015817760395] | -4.623 | 2.64827 | 2.64827 |
| LIPID_OA_SOL_C2 | K02-TC-BMI | mg/dL per 5 kg/m^2 | 3 | 8.6866 | [8.267203318324036, 8.94398740749271] | 5.68311 | 3.00349 | 3.00349 |
| LIPID_OA_SOL_C2 | K02-LIPID-RESIDUAL | 1 | 3 | 0.120768 | [0.10520384510505708, 0.13361268427380368] | 0.51207 | -0.391302 | 0.391302 |
| PNS_OA_SOL_C2 | bmi_sbp | mmHg per 5 kg/m^2 | 3 | 3.55973 | [3.321952936252828, 3.7142960085414467] | 3.524 | 0.0357334 | 0.170428 |
| PNS_OA_SOL_C2 | bmi_dbp | mmHg per 5 kg/m^2 | 3 | 2.82631 | [2.6330781942889816, 2.962255948641959] | 2.25995 | 0.566365 | 0.566365 |
| PNS_OA_SOL_C2 | residual_correlation | 1 | 3 | 0.476785 | [0.46726085714088755, 0.48430910183024545] | 0.717184 | -0.2404 | 0.2404 |

## Secondary SD and component diagnostics

| Construction | Endpoint | Unit | Available/3 | Seed mean | Seed range | Reference | Mean signed difference | Mean absolute difference |
|---|---|---|---:|---:|---|---:|---:|---:|
| PNS_OA_ASTRA_C1 | sbp.sd_population | mmHg | 3 | 17.2686 | [16.889881171592926, 17.736843177252] | 18.1916 | -0.923014 | 0.923014 |
| PNS_OA_ASTRA_C1 | dbp.sd_population | mmHg | 3 | 9.7929 | [9.722462028826806, 9.841393250444662] | 11.0941 | -1.30124 | 1.30124 |
| PNS_OA_ASTRA_C1 | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 | 0 |
| LIPID_OA_ASTRA_C1 | total_cholesterol.sd_sample | mg/dL | 3 | 41.5931 | [41.441107172622814, 41.84057064703179] | 42.8466 | -1.2535 | 1.2535 |
| LIPID_OA_ASTRA_C1 | hdl_cholesterol.sd_sample | mg/dL | 3 | 13.1563 | [13.004667833345755, 13.308070665662818] | 20.1756 | -7.01921 | 7.01921 |
| LIPID_OA_ASTRA_C1 | hdl_above_total_fraction | 1 | 3 | 0.000444444 | [0.0, 0.001] | unavailable | unavailable | unavailable |
| LIPID_DS_PRO_C1 | total_cholesterol.sd_sample | mg/dL | 3 | 30.5991 | [30.47928115254575, 30.70975283171542] | 42.8466 | -12.2475 | 12.2475 |
| LIPID_DS_PRO_C1 | hdl_cholesterol.sd_sample | mg/dL | 3 | 11.9431 | [11.863525673792884, 11.99480876518981] | 20.1756 | -8.23242 | 8.23242 |
| LIPID_DS_PRO_C1 | hdl_above_total_fraction | 1 | 3 | 0 | [0.0, 0.0] | unavailable | unavailable | unavailable |
| PNS_DS_PRO_C1 | sbp.sd_population | mmHg | 3 | 20.4444 | [20.17016486297765, 20.632650992013428] | 18.1916 | 2.25283 | 2.25283 |
| PNS_DS_PRO_C1 | dbp.sd_population | mmHg | 3 | 10.9194 | [10.75938277577425, 11.00541431115132] | 11.0941 | -0.174732 | 0.174732 |
| PNS_DS_PRO_C1 | sbp_below_dbp_fraction | 1 | 3 | 0.00511111 | [0.004333333333333333, 0.006] | 0 | 0.00511111 | 0.00511111 |
| PNS_CL_FABLE_C1 | sbp.sd_population | mmHg | 0 | unavailable | unavailable | 18.1916 | unavailable | unavailable |
| PNS_CL_FABLE_C1 | dbp.sd_population | mmHg | 0 | unavailable | unavailable | 11.0941 | unavailable | unavailable |
| PNS_CL_FABLE_C1 | sbp_below_dbp_fraction | 1 | 0 | unavailable | unavailable | 0 | unavailable | unavailable |
| LIPID_CL_FABLE_C1 | total_cholesterol.sd_sample | mg/dL | 3 | 34.0509 | [33.17218541104651, 34.72706335262504] | 42.8466 | -8.79569 | 8.79569 |
| LIPID_CL_FABLE_C1 | hdl_cholesterol.sd_sample | mg/dL | 3 | 12.6956 | [12.279310432829304, 12.931948603769321] | 20.1756 | -7.48 | 7.48 |
| LIPID_CL_FABLE_C1 | hdl_above_total_fraction | 1 | 3 | 0.000333333 | [0.0003333333333333333, 0.0003333333333333333] | unavailable | unavailable | unavailable |
| LIPID_GE_CARBON_C1 | total_cholesterol.sd_sample | mg/dL | 0 | unavailable | unavailable | 42.8466 | unavailable | unavailable |
| LIPID_GE_CARBON_C1 | hdl_cholesterol.sd_sample | mg/dL | 0 | unavailable | unavailable | 20.1756 | unavailable | unavailable |
| LIPID_GE_CARBON_C1 | hdl_above_total_fraction | 1 | 0 | unavailable | unavailable | unavailable | unavailable | unavailable |
| PNS_GE_CARBON_C1 | sbp.sd_population | mmHg | 0 | unavailable | unavailable | 18.1916 | unavailable | unavailable |
| PNS_GE_CARBON_C1 | dbp.sd_population | mmHg | 0 | unavailable | unavailable | 11.0941 | unavailable | unavailable |
| PNS_GE_CARBON_C1 | sbp_below_dbp_fraction | 1 | 0 | unavailable | unavailable | 0 | unavailable | unavailable |
| PNS_OA_SOL_C1 | sbp.sd_population | mmHg | 3 | 17.7787 | [17.53256122905222, 18.189233880037882] | 18.1916 | -0.412901 | 0.412901 |
| PNS_OA_SOL_C1 | dbp.sd_population | mmHg | 3 | 10.1059 | [9.862177309013077, 10.320337537836007] | 11.0941 | -0.988227 | 0.988227 |
| PNS_OA_SOL_C1 | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 | 0 |
| LIPID_OA_SOL_C1 | total_cholesterol.sd_sample | mg/dL | 3 | 35.8739 | [35.385103969544275, 36.37888920892974] | 42.8466 | -6.97263 | 6.97263 |
| LIPID_OA_SOL_C1 | hdl_cholesterol.sd_sample | mg/dL | 3 | 14.6719 | [14.626562661777681, 14.746929143110515] | 20.1756 | -5.50363 | 5.50363 |
| LIPID_OA_SOL_C1 | hdl_above_total_fraction | 1 | 3 | 0.00844444 | [0.007666666666666666, 0.009666666666666667] | unavailable | unavailable | unavailable |
| LIPID_OA_ASTRA_C2 | total_cholesterol.sd_sample | mg/dL | 3 | 36.1579 | [36.033611332732804, 36.36642852569971] | 42.8466 | -6.68867 | 6.68867 |
| LIPID_OA_ASTRA_C2 | hdl_cholesterol.sd_sample | mg/dL | 3 | 14.8657 | [14.70950200654606, 15.025413063179201] | 20.1756 | -5.30986 | 5.30986 |
| LIPID_OA_ASTRA_C2 | hdl_above_total_fraction | 1 | 3 | 0.00433333 | [0.0033333333333333335, 0.006] | unavailable | unavailable | unavailable |
| PNS_OA_ASTRA_C2 | sbp.sd_population | mmHg | 3 | 22.791 | [22.590545588557077, 22.99592949356311] | 18.1916 | 4.59947 | 4.59947 |
| PNS_OA_ASTRA_C2 | dbp.sd_population | mmHg | 3 | 11.3908 | [11.287644536952223, 11.552035733349731] | 11.0941 | 0.296656 | 0.296656 |
| PNS_OA_ASTRA_C2 | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 | 0 |
| PNS_DS_PRO_C2 | sbp.sd_population | mmHg | 3 | 15.1746 | [15.120462271419383, 15.227382563246051] | 18.1916 | -3.01695 | 3.01695 |
| PNS_DS_PRO_C2 | dbp.sd_population | mmHg | 3 | 9.74241 | [9.681774986112622, 9.80474241712446] | 11.0941 | -1.35173 | 1.35173 |
| PNS_DS_PRO_C2 | sbp_below_dbp_fraction | 1 | 3 | 0.000111111 | [0.0, 0.0003333333333333333] | 0 | 0.000111111 | 0.000111111 |
| LIPID_DS_PRO_C2 | total_cholesterol.sd_sample | mg/dL | 3 | 33.9157 | [33.861593461486905, 33.947117422497904] | 42.8466 | -8.93087 | 8.93087 |
| LIPID_DS_PRO_C2 | hdl_cholesterol.sd_sample | mg/dL | 3 | 12.5641 | [12.36499587830399, 12.822783564692502] | 20.1756 | -7.6115 | 7.6115 |
| LIPID_DS_PRO_C2 | hdl_above_total_fraction | 1 | 3 | 0.00433333 | [0.003, 0.005333333333333333] | unavailable | unavailable | unavailable |
| LIPID_CL_FABLE_C2 | total_cholesterol.sd_sample | mg/dL | 3 | 34.8812 | [33.73413734689077, 36.19362906149574] | 42.8466 | -7.96538 | 7.96538 |
| LIPID_CL_FABLE_C2 | hdl_cholesterol.sd_sample | mg/dL | 3 | 12.9596 | [12.624470741627077, 13.568767923348615] | 20.1756 | -7.21594 | 7.21594 |
| LIPID_CL_FABLE_C2 | hdl_above_total_fraction | 1 | 3 | 0 | [0.0, 0.0] | unavailable | unavailable | unavailable |
| PNS_CL_FABLE_C2 | sbp.sd_population | mmHg | 0 | unavailable | unavailable | 18.1916 | unavailable | unavailable |
| PNS_CL_FABLE_C2 | dbp.sd_population | mmHg | 0 | unavailable | unavailable | 11.0941 | unavailable | unavailable |
| PNS_CL_FABLE_C2 | sbp_below_dbp_fraction | 1 | 0 | unavailable | unavailable | 0 | unavailable | unavailable |
| PNS_GE_CARBON_C2 | sbp.sd_population | mmHg | 0 | unavailable | unavailable | 18.1916 | unavailable | unavailable |
| PNS_GE_CARBON_C2 | dbp.sd_population | mmHg | 0 | unavailable | unavailable | 11.0941 | unavailable | unavailable |
| PNS_GE_CARBON_C2 | sbp_below_dbp_fraction | 1 | 0 | unavailable | unavailable | 0 | unavailable | unavailable |
| LIPID_GE_CARBON_C2 | total_cholesterol.sd_sample | mg/dL | 0 | unavailable | unavailable | 42.8466 | unavailable | unavailable |
| LIPID_GE_CARBON_C2 | hdl_cholesterol.sd_sample | mg/dL | 0 | unavailable | unavailable | 20.1756 | unavailable | unavailable |
| LIPID_GE_CARBON_C2 | hdl_above_total_fraction | 1 | 0 | unavailable | unavailable | unavailable | unavailable | unavailable |
| LIPID_OA_SOL_C2 | total_cholesterol.sd_sample | mg/dL | 3 | 35.5089 | [35.24442646891952, 36.00343458207821] | 42.8466 | -7.33765 | 7.33765 |
| LIPID_OA_SOL_C2 | hdl_cholesterol.sd_sample | mg/dL | 3 | 14.5269 | [14.292915525946762, 14.800295587535594] | 20.1756 | -5.64866 | 5.64866 |
| LIPID_OA_SOL_C2 | hdl_above_total_fraction | 1 | 3 | 0.004 | [0.0033333333333333335, 0.004333333333333333] | unavailable | unavailable | unavailable |
| PNS_OA_SOL_C2 | sbp.sd_population | mmHg | 3 | 16.3633 | [16.25252005455479, 16.442431242540398] | 18.1916 | -1.82831 | 1.82831 |
| PNS_OA_SOL_C2 | dbp.sd_population | mmHg | 3 | 10.4883 | [10.456125302186452, 10.513739860802325] | 11.0941 | -0.605815 | 0.605815 |
| PNS_OA_SOL_C2 | sbp_below_dbp_fraction | 1 | 3 | 0 | [0.0, 0.0] | 0 | 0 | 0 |

## Every scheduled slot

| Construction | Seed | Execution | Analysis | Failure |
|---|---:|---|---|---|
| PNS_OA_ASTRA_C1 | 31001 | success | complete | unavailable |
| PNS_OA_ASTRA_C1 | 31003 | success | complete | unavailable |
| PNS_OA_ASTRA_C1 | 31007 | success | complete | unavailable |
| LIPID_OA_ASTRA_C1 | 31001 | success | complete | unavailable |
| LIPID_OA_ASTRA_C1 | 31003 | success | complete | unavailable |
| LIPID_OA_ASTRA_C1 | 31007 | success | complete | unavailable |
| LIPID_DS_PRO_C1 | 31001 | success | complete | unavailable |
| LIPID_DS_PRO_C1 | 31003 | success | complete | unavailable |
| LIPID_DS_PRO_C1 | 31007 | success | complete | unavailable |
| PNS_DS_PRO_C1 | 31001 | success | complete | unavailable |
| PNS_DS_PRO_C1 | 31003 | success | complete | unavailable |
| PNS_DS_PRO_C1 | 31007 | success | complete | unavailable |
| PNS_CL_FABLE_C1 | 31001 | construction_failed | unavailable | construction_failed |
| PNS_CL_FABLE_C1 | 31003 | construction_failed | unavailable | construction_failed |
| PNS_CL_FABLE_C1 | 31007 | construction_failed | unavailable | construction_failed |
| LIPID_CL_FABLE_C1 | 31001 | success | complete | unavailable |
| LIPID_CL_FABLE_C1 | 31003 | success | complete | unavailable |
| LIPID_CL_FABLE_C1 | 31007 | success | complete | unavailable |
| LIPID_GE_CARBON_C1 | 31001 | construction_failed | unavailable | construction_failed |
| LIPID_GE_CARBON_C1 | 31003 | construction_failed | unavailable | construction_failed |
| LIPID_GE_CARBON_C1 | 31007 | construction_failed | unavailable | construction_failed |
| PNS_GE_CARBON_C1 | 31001 | construction_failed | unavailable | construction_failed |
| PNS_GE_CARBON_C1 | 31003 | construction_failed | unavailable | construction_failed |
| PNS_GE_CARBON_C1 | 31007 | construction_failed | unavailable | construction_failed |
| PNS_OA_SOL_C1 | 31001 | success | complete | unavailable |
| PNS_OA_SOL_C1 | 31003 | success | complete | unavailable |
| PNS_OA_SOL_C1 | 31007 | success | complete | unavailable |
| LIPID_OA_SOL_C1 | 31001 | success | complete | unavailable |
| LIPID_OA_SOL_C1 | 31003 | success | complete | unavailable |
| LIPID_OA_SOL_C1 | 31007 | success | complete | unavailable |
| LIPID_OA_ASTRA_C2 | 31001 | success | complete | unavailable |
| LIPID_OA_ASTRA_C2 | 31003 | success | complete | unavailable |
| LIPID_OA_ASTRA_C2 | 31007 | success | complete | unavailable |
| PNS_OA_ASTRA_C2 | 31001 | success | complete | unavailable |
| PNS_OA_ASTRA_C2 | 31003 | success | complete | unavailable |
| PNS_OA_ASTRA_C2 | 31007 | success | complete | unavailable |
| PNS_DS_PRO_C2 | 31001 | success | complete | unavailable |
| PNS_DS_PRO_C2 | 31003 | success | complete | unavailable |
| PNS_DS_PRO_C2 | 31007 | success | complete | unavailable |
| LIPID_DS_PRO_C2 | 31001 | success | complete | unavailable |
| LIPID_DS_PRO_C2 | 31003 | success | complete | unavailable |
| LIPID_DS_PRO_C2 | 31007 | success | complete | unavailable |
| LIPID_CL_FABLE_C2 | 31001 | success | complete | unavailable |
| LIPID_CL_FABLE_C2 | 31003 | success | complete | unavailable |
| LIPID_CL_FABLE_C2 | 31007 | success | complete | unavailable |
| PNS_CL_FABLE_C2 | 31001 | construction_failed | unavailable | construction_failed |
| PNS_CL_FABLE_C2 | 31003 | construction_failed | unavailable | construction_failed |
| PNS_CL_FABLE_C2 | 31007 | construction_failed | unavailable | construction_failed |
| PNS_GE_CARBON_C2 | 31001 | construction_failed | unavailable | construction_failed |
| PNS_GE_CARBON_C2 | 31003 | construction_failed | unavailable | construction_failed |
| PNS_GE_CARBON_C2 | 31007 | construction_failed | unavailable | construction_failed |
| LIPID_GE_CARBON_C2 | 31001 | construction_failed | unavailable | construction_failed |
| LIPID_GE_CARBON_C2 | 31003 | construction_failed | unavailable | construction_failed |
| LIPID_GE_CARBON_C2 | 31007 | construction_failed | unavailable | construction_failed |
| LIPID_OA_SOL_C2 | 31001 | success | complete | unavailable |
| LIPID_OA_SOL_C2 | 31003 | success | complete | unavailable |
| LIPID_OA_SOL_C2 | 31007 | success | complete | unavailable |
| PNS_OA_SOL_C2 | 31001 | success | complete | unavailable |
| PNS_OA_SOL_C2 | 31003 | success | complete | unavailable |
| PNS_OA_SOL_C2 | 31007 | success | complete | unavailable |

Endpoint-level seed values, supplied reference uncertainty, provenance hashes, and unavailable entries are retained in EVALUATION.json. Seed ranges are descriptive ranges, not confidence intervals. Component violations are counted in the delivered rows without silently repairing them.
