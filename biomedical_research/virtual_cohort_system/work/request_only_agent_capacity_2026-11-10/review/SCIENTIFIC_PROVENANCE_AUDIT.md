# Capacity-round source and scientific-provenance audit

## Inspection boundary

This is a postclosure static review of the four request-only Agent episodes. The reviewer read their submitted code/specifications/notes, tool requests and returned source text, approved cached article XML, API receipts, and generated-only trial receipts. No author program was imported or executed by the reviewer; no new literature was retrieved; no target reference, target table, final evaluation result, private reasoning, or credential was read. Small numerical checks below independently evaluate explicit scalar formulas, not the submitted generators.

All four OUTCOME files were terminal before the accompanying `audit_run.py` was run. `TOOL_SOURCE_COST_AUDIT.json` supplies per-action paths, source hashes/versions, immutable candidate hashes, and API receipts. This report concerns extraction and implementation, not clinical accuracy or target validation.

## What completed

| Episode | API calls | Search actions / provider queries | Article versions fetched | Candidates / trials | Selected | Tariff cost USD |
|---|---:|---:|---:|---:|---|---:|
| PNS_BASE | 20 | 8 / 8 | 4 | 1 / 1 | v001 | 0.2562012 |
| PNS_WORKFLOW | 35 | 16 / 16 | 9 | 1 / 1 | v001 | 0.4017387 |
| LIPID_BASE | 28 | 8 / 7 | 6 | 1 / 1 | v001 | 0.2453062 |
| LIPID_WORKFLOW | 32 | 12 / 11 | 4 | 1 / 1 | v001 | 0.3727907 |

There were **115 API calls, four selected generators, four successful first trials, and zero candidate revisions**. Recorded tariff cost totals **$1.2760368**, with no unknown-usage calls. Requested and returned model IDs were `gpt-6.1-sol`. The first request began 2026-11-11 04:38:32 UTC and the last episode closed 04:49:24 UTC. Source query rejections count as Agent actions but not provider queries; each lipid episode initially included the prohibited cohort name in a negated query, then reformulated it. Article version disambiguation and local pagination are also real actions, not extra scientific evidence.

Both policies therefore completed an end-to-end retrieval, construction, generated-data check, and final selection. The more explicit policy used more calls in these two pairs. Four successful trials demonstrate operability; they do not demonstrate a revision benefit, policy superiority, or clinical validity. This round changed the shared capacity allowance relative to the preceding repair round and used fresh Agent sessions, so between-round differences cannot be attributed solely to capacity.

## PNS_BASE: reported residual dependence, with an operator mismatch

The Agent independently found four papers. The numerical evidence actually appears in its received pages:

* **ELSA-Brasil, PMC7433850, Table 1**, DOI 10.1590/1414-431X20209815: sex-specific BMI means/SDs 27.0/4.3 and 27.1/5.1; SBP 125.6/16.8 and 117.7/16.9; DBP 78.9/10.8 and 74.0/10.2. The Agent accurately labels these as marginal occupational-cohort summaries, then assumes they can anchor age-52 conditional location/scale. They are not reported age-52 conditional statistics.
* **China-PEACE, PMC6324286**, DOI 10.1001/jamanetworkopen.2018.1271: the Results paragraph returned in action 0009 reports adjusted SBP/DBP slopes **1.15/0.75 mmHg per BMI unit**, equivalently **5.75/3.75 per five units**. Methods read in action 0008 adjust for age, sex and multiple socioeconomic, geographic, smoking, stroke, and treatment variables. The Agent copies the numbers and units accurately, but transport to an age/sex-only analysis remains an assumption.
* **Uganda STEPS, PMC11392332**, DOI 10.1371/journal.pgph.0003707: action 0016 returns the Table 2 entry **residual correlation 0.7307**, adopted as 0.73. This is not merely an unadjusted correlation copied from an abstract. The paper explicitly labels it residual correlation in a joint linear SBP/DBP model, with original mmHg outcomes; no BP logarithm or standardization is described. The paper also uses the same number in one paragraph describing the preliminary association, an ambiguity that should not erase the clearer Table 2 residual label.
* **Brazil MMM2018, PMC7455292**, DOI 10.1093/eurheartj/suaa022: used as contextual support for Brazilian scale and repeated seated BP measurement, not as a calibrated target prevalence.

The Uganda operator is still **not the requested residual operator**. Table 2 includes age, categorical BMI, glucose category, region, marital status, fruit consumption, salt, activity, income, cholesterol category and central obesity. Sex was considered but not retained after screening. Antihypertensive users were excluded, and the source population was Ugandan adults approximately 18–68 years (another passage says 18–69). The paper describes three seated readings and uses average BP for prevalence, but does not unambiguously specify the final reading aggregate for the regression. The target task permits treatment and asks for residualization on age, sex and continuous BMI. Applying 0.73 to its Gaussian final-reading innovations is therefore a **reported external dependence value plus a substantial transfer assumption**, not a measured target parameter.

The submitted law uses assumed age-band weights, sex-by-age probabilities, shifted-lognormal BMI, nonlinear BP age curves, residual SDs **14.8/9.9 mmHg**, and paired BP rejection on bounds and pulse pressure. These SDs are not extracted residual SDs. BMI truncation, nonlinear age terms, conditional rejection and rounding mean the declared BMI slopes and innovation correlation are not exact population OLS slopes/residual correlation for the requested linear-age analysis. No finite-sample coefficient forcing is present. All generated variables are bounded after rejection, so the earlier unbounded-tail pathology is not present in this law.

Exact local anchors: `episodes/PNS_BASE/tool_actions/action_0009/result.json` (China slopes), `action_0013/result.json` (ELSA table), `action_0016/result.json` (Uganda correlation), `action_0017/result.json` (Uganda definitions and exclusions), and `candidates/v001/{generator.py,model_spec.json,notes.json}`. Uganda cached XML SHA256 is `3761cd2f9b793a7a0f6d4347db7e9dbb60d7f45daa535b228f72473c328c84b4`.

## PNS_WORKFLOW: a genuine derivation, not a directly reported Pearson correlation

This Agent independently retrieved the same China-PEACE BMI slopes, but chose different marginal and dependence sources:

* **ELSA-Brasil Minas Gerais subset, PMC4338719, Table 1**, DOI 10.1161/JAHA.114.001279: age **52±9**, female fraction **0.44**, BMI **26.8±4.6**, SBP **122±17**, DBP **78±11**. These copied values match the received table. This is a selected peripheral-tonometry subset of 1,535 civil servants, not a representative target cohort.
* **San Antonio family studies, PMC4143670, Table 3**, DOI 10.1186/1753-6561-8-S1-S72: **Kendall tau 0.578**, SE 0.05 and 99% CI 0.449–0.707. Actions 0030–0031 include the relevant methods and table. The phenotypes are averages of residuals from the first three exams, after age/sex/smoking adjustment and censored-regression correction for treatment. BMI is not adjusted. The null copula omits a genetic variant, not all covariate adjustment. This is neither raw BP dependence nor the requested baseline measured-BP Pearson residual correlation.

The Agent explicitly introduces a **Gaussian-copula approximation**: `sin(pi*0.578/2) = 0.788225612`. The source uses an asymmetric copula with tail dependence, and reports better fit than a bivariate normal model. Consequently the conversion is an added model assumption; it does not recover the source's empirical Pearson correlation.

Its separate variance budget subtracts assumed linear-age and sex contributions from Brazilian marginal variances, then subtracts BMI slope contributions. Independent scalar arithmetic confirms:

| Quantity | Independently recomputed construction value |
|---|---:|
| Pre-BMI SBP variance | 256.6764 |
| Pre-BMI DBP variance | 115.5424 |
| Final innovation SBP SD | 15.12257584 |
| Final innovation DBP SD | 10.18036836 |
| Final innovation correlation | 0.763162706 |

The subtraction is coherent as the stated approximation, but assumes compatible populations/operators, negligible nonlinear reference variance and no reference age–sex–BMI covariance. The actual generator subsequently includes nonlinear age, age-dependent BMI, age-dependent sex composition, rounding and joint BP rejection. These departures prevent interpreting the budget as exact source replay or final OLS identification. The source's longitudinal treatment-corrected residuals cannot become a baseline observed-BP estimand through algebra alone.

The notes correctly distinguish all these transfer assumptions from published estimates. The evidence search itself was adaptive; one query specified `0.7`. It was an Agent-chosen search, with no target result provided, but the resulting literature set should not be portrayed as an exhaustive or unbiased meta-analysis. The first trial succeeded; no scientific or mechanical revision followed.

Exact anchors: `episodes/PNS_WORKFLOW/tool_actions/action_0031/result.json` (copula methods/table), `action_0032/result.json` (ELSA table), and `candidates/v001/`. Copula XML SHA256 is `9ee772f09b1d70508237b264f12ba7d5a069bc8949a37b17aab705b6de7e4929`.

## LIPID_BASE: contextual evidence plus assumed conditional slopes

The Agent retrieved rural Kenyan, Tanzanian Maasai, Kajiado, and Tanzania/Uganda aggregate evidence, plus an abstract on rural Kenyan age patterns. It did not obtain a directly transferable TC–HDL residual correlation.

The inspected citations are numerically faithful at their stated level:

* **PMC6435188 version 1, Table 1**, DOI 10.1002/ajhb.23199: six sex/ethnicity groups with BMI means 20.0–22.5, TC means 3.6–4.0 mmol/L and HDL means 0.9–1.2. These are marginal summaries, not BMI slopes.
* **PMC7263614, Table 2**, DOI 10.1371/journal.pone.0233777: BMI **21.9±3.9** and TC **177.7±38.9 mg/dL**. The stated conversion to about **4.60±1.01 mmol/L** is correct. The clinical sampling/measurement circumstances remain different from the requested cohort.
* **PMC6897412, Table 4**, DOI 10.1371/journal.pone.0223189: adjusted overweight/obese LDL differences **+0.23/+0.48** and HDL **−0.06/−0.15 mmol/L** relative to normal BMI. They motivate, but do not numerically identify, the Agent's chosen continuous TC/HDL slopes. LDL is not TC.
* **PMC7579460, Table 3** and **PMID26073640 abstract** provide urban-transition and age/sex context; they are not a joint distribution.

The actual law uses three assumed lifestyle contexts, a bounded age distribution, inverse-CDF truncated lognormal BMI, and **linear arithmetic lipid-component means**. The chosen BMI slopes are HDL **−0.012** and non-HDL **+0.065 mmol/L per BMI unit**, hence within-context TC **+0.053**. Equivalently the conditional TC/HDL slopes are **10.24755/−2.32020 mg/dL per five BMI units**; these are independently derived construction coefficients, not final cohort OLS estimates. Omitted context affects the requested adjustment.

HDL and non-HDL have lognormal residual multipliers with CVs **0.27/0.28**, log-error correlation **0.08**, and TC is their sum. The 0.08 value is explicitly assumed, not a source estimate and not TC–HDL residual Pearson correlation. TC–HDL dependence follows from the shared HDL component plus this assumed component covariance and context mixture. The linear means stay positive on the stated bounded age/BMI supports; lognormal multipliers have finite moments. Thus this law does not contain the earlier exponential-of-unbounded-lognormal tail defect. It also does not filter rows according to TC/HDL ordering: the positive-component law enforces that ordering structurally.

Exact anchors: `episodes/LIPID_BASE/tool_actions/action_0008/result.json`, `action_0015/result.json`, `action_0025/result.json`, and `candidates/v001/`. The first trial succeeded and the Agent retained v001.

## LIPID_WORKFLOW: explicit standardized-effect transport and a remaining dependence assumption

The Agent used **PMC6435188 version 2 Table 1** for the Maasai anchors, **PMC6747887 Tables 2–3** for Malawian context contrasts and associations, and PMC6897412 for qualitative age/heterogeneity context. Version 2 was explicitly requested after version ambiguity; its selected numerical anchors match the cached table. Versions 1 and 2 of the Kenyan paper are one study, not independent evidence.

Kenyan female/male anchors match the paper: BMI **22.5/21.0**, both SD **4.8**; TC **3.8/4.0**, SD **0.9/1.1**; HDL **1.2/1.1**, SD **0.30/0.32**. Malawian Table 2 urban-minus-rural contrasts are correctly subtracted: female/male BMI **2.5/1.1**, TC **0.11/0.25**, HDL **0.05/0.06**. These are age-adjusted marginal contrasts and are not causal settlement effects.

Malawian Table 3 reports differences per **one SD of BMI**, not per kg/m²:

| Source stratum | TC difference per SD | HDL difference per SD |
|---|---:|---:|
| Rural women | 0.23 | −0.03 |
| Rural men | 0.20 | −0.03 |
| Urban women | 0.13 | −0.05 |
| Urban men | 0.15 | −0.04 |

The Agent extracted these values and their intervals accurately. The source adjustment includes age, ethnicity, education, household assets, marital status, parity for women, lipid medication, smoking, alcohol, activity and HIV/ART. The Agent **does not know the Malawian BMI SD**; dividing these effects by the modeled/Kenyan SD **4.8** is explicitly labeled standardized-effect transport. It must not be described as a recovered physical-unit coefficient from Malawi. It likewise omits most source adjustment variables.

The generator assumes 55% female, 30% transitioning context, bounded beta age/BMI laws, modest age effects, and gamma HDL/non-HDL components. Source marginal lipid variances are reduced by the modeled age/BMI mean variance. Independent arithmetic for the rural reference assumptions gives:

| Sex | Conditional HDL variance | Conditional non-HDL variance | Conditional TC–HDL Pearson correlation under component independence |
|---|---:|---:|---:|
| F | 0.088755469 | 0.637991328 | 0.349466860 |
| M | 0.101086719 | 1.033371094 | 0.298505869 |

These are law-level, covariate/context-conditional calculations, not the requested pooled residual correlation. The decisive unreported assumption remains **conditional HDL/non-HDL independence**. A positive TC–HDL correlation arises mechanically through shared HDL; no source measured the generated cohort's residual dependence. Marginal SD replay is approximate: the variance budget uses source age/BMI moments, while the new cohort uses another age distribution, conditional BMI SD 4.8 plus age variation, and a context mixture. Sex/context-specific BMI slopes and omitted context further separate final OLS estimates from any single source coefficient.

The support and positive gamma components give finite moments under the submitted parameters. No after-the-fact sample coefficient matching or TC/HDL row filtering appears. The first trial succeeded and v001 was retained.

Exact anchors: `episodes/LIPID_WORKFLOW/tool_actions/action_0011/result.json` (Kenyan table), `action_0018/result.json` (Malawian effects), `action_0020/result.json` (context means), `action_0021/result.json` (methods), and `candidates/v001/`. Kenyan version-2 XML SHA256 is `1aea26e1be74dce369b18c4e0c8d21a488cdb12d77a39a0386ef39c010723f30`; Malawian XML SHA256 is `d091d84d54ac5f03ccaf000e894035f94415b283f010eef1954356eac07f17d7`.

## Exposure and retrieval audit

| Episode | Unique accepted titles / actually returned complete titles | Accepted PMCIDs / returned PMCIDs | Returned metadata characters, including repeats |
|---|---:|---:|---:|
| PNS_BASE | 55 / 45 | 55 / 45 | 64,176 |
| PNS_WORKFLOW | 84 / 73 | 73 / 65 | 105,938 |
| LIPID_BASE | 32 / 27 | 31 / 26 | 44,412 |
| LIPID_WORKFLOW | 83 / 63 | 71 / 54 | 91,892 |

The unavailable-on-first-page records were cached and explicitly pageable; admitted does not mean actually seen. Complete identity exposure does not mean the model understood an article. Article/table access and source versions remain hash-bound in the audit JSON.

Unlike the preceding repair round, **this audit found no PNS-family ancillary result in the current PNS returned pages**, and no Turkana occurrence in either lipid episode's returned source material or approved full-text XML. A cached PNS_WORKFLOW bibliography mentions **PNAD 2008**, which is a different Brazilian household survey, not PNS; it must not be conflated with the prior round's PNS prevalence exposure. This is a bounded local inspection finding, not a guarantee that all indirect cohort provenance has been resolved.

The prior round's PNS_BASE exposure remains on the historical record: an admitted ELSA paper returned a national-survey hypertension prevalence to the author, who stated it was ignored. Nothing in this round erases that exposure or repairs the general weakness of alias-based source screening. Current source exclusions were not modified after seeing the incident.

## What this round contributes

1. **Self-directed retrieval can supply numerical relationship information.** Both PNS Agents found actual external BMI coefficients; BASE also found an explicitly reported residual correlation, while WORKFLOW found a different dependence measure and documented a bridge. The framework did not hard-code those scientific values.
2. **Information retrieval does not remove operator or transport assumptions.** An accurate number can refer to a different adjustment set, treatment policy, measurement aggregate, population, or scale. The PNS dependence sources provide a concrete example, rather than an unsupported assertion that all residual parameters are arbitrary.
3. **The lipid dependence gap remains visible.** Both Agents built coherent positive components but assumed their unreported dependence. WORKFLOW extracted more structured association evidence and kept its standardized-effect conversion explicit; that is a provenance distinction, not yet an accuracy advantage.
4. **Operability improved, but revision remains untested here.** Every first candidate ran and was selected unchanged. The completed workflow supports a claim of autonomous retrieval-to-generation execution. It does not support a claim that feedback revision improved these generators.

The next numerical comparison belongs to the root's separately frozen evaluation. This source audit neither selects favorable endpoints nor uses target agreement to label assumptions as evidence.
