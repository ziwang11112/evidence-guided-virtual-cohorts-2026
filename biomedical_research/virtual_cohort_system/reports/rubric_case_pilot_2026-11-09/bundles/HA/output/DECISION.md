# HA construction decision

The submission defines one conditional joint law for 3,000 fictional people, with exactly 375 in each requested age–sex cell. Age is discrete uniform within cells, BMI is a bounded lognormal, fasting serum glucose is a conditionally truncated normal, and HbA1c has a linear conditional location with bounded Student-t residuals. Parameters are in `model_spec.json` and consumed by `generator.py`. Identifiers are unique within a draw; rows are shuffled.

The primary age anchor is the NHANES adjusted 0.010 percentage-point/year association in Pani et al. The Finnish supplementary age/sex-adjusted BMI–HbA1c slope informs the association without glucose adjustment. No admitted study supplies the requested glucose-adjusted BMI association reliably. I therefore declared a cross-source additive decomposition, using the Finnish BMI–glucose slope and an Iranian glucose–HbA1c crude slope derived from Pearson r and SDs. Treating the latter as conditional is an assumption, and the decomposition is neither a mediation analysis nor causal identification. The Iranian Table 2 beta scale is unresolved and is not used.

The chosen BMI mean, conditional intercepts, residual spreads, tail shapes, independence assumptions, absence of interactions and support restrictions are separately labeled as transferred values or assumptions. The output permits HbA1c >=6.5 despite glucose <126. The model does not assert absence of anemia or medication use. Eligibility beyond the six output variables defines the scenario and cannot be verified from those columns. Assumed BMI/HbA1c supports omit possible rare extremes and do not follow from the documentation-based anthropometry exclusions.

Q1 is source-informed but transport-dependent. Q2 additionally depends on reconciling binary-age source adjustment and source HbA1c exclusion with this task. Q3 is especially assumption-dependent. Truncating conditional measurements can alter projection coefficients; the untruncated algebra below is not a report of realized WLS estimates. Repeated seeds represent individual sampling variation under fixed assumptions, not source, transport or structural uncertainty.

## Guidance and boundary

Read and applied the supplied common `base_skill/SKILL.md` and linked `references/harness-interface.md`. `input/` was absent: the attempted directory listing returned “Cannot find path,” so no task rubric or additional procedure was supplied there. The pilot REQUEST supersedes the older candidate/freeze/validate steps and authorizes exactly these four files. Accordingly, no old harness CLI, old-style freeze, source-feedback collector, source replay, external literature, other bundle, project history, target statistics or subagent was used. No unavailable guidance is silently substituted.

## Actual tools and actions

- `functions.exec` with PowerShell `Get-Content` read REQUEST, task, request, registry, supplied guidance, admitted study text/metadata, selected XML body/tables and supplementary text. XML was parsed using PowerShell `[xml]`; admitted supplement JSON was parsed using `ConvertFrom-Json`. Some broad source displays were tool-truncated, and focused XML table displays and both supplement text extractions were then read for the numerical items used.
- `Get-ChildItem` inventoried only permitted `sources/` and attempted `input/`. No directory outside the allowed read list was inventoried for evidence.
- One retained inline Python command performed deterministic algebra from stated numbers. It imported only `math`, wrote no file, sampled nothing, and did not read/import/execute the generator.
- `functions.exec` invoked `apply_patch` to write the four requested artifacts and record ordinary self-check results in this document and `SOURCE_USE.json`.
- Two coordination messages to the parent reported progress and the absence of `input/`; a parent status-only query supplied no new evidence, review or target feedback.
- A separate inline Python static check used `ast`, `json`, `math`, `hashlib` and `pathlib` to parse the submitted files, compare their interface/design/analysis declarations to the task, verify parameter references/arithmetic, and hash the registered admitted artifacts. It did not import the generator or NumPy/Pandas, compile an executable module, or create another file.

## Retained deterministic calculation

Exact PowerShell command executed:

```powershell
@'
import math
r, sy, sx = 0.23, 0.73, 12.4
hg = r * sy / sx
gb = 0.0240 * 18.0
ga = 0.1985 * 18.0 / 17.5
gs = 0.2472 * 18.0
hb = 0.0125 - hg * gb
mu_g_lo = 95.5 + ga * (25 - 50) + gs * (0.5 - 1) + gb * (14 - 28.01)
mu_g_hi = 95.5 + ga * (79 - 50) + gs * (0.5 - 0) + gb * (60 - 28.01)
mu_h_lo = 5.4 + 0.010 * (25 - 50) - 0.04 + hb * (14 - 28.01) + hg * (50 - 95.5)
mu_h_hi = 5.4 + 0.010 * (79 - 50) + hb * (60 - 28.01) + hg * (126 - 95.5)
print('glucose_to_hba1c_crude_derived_pp_per_mgdl =', format(hg, '.12f'))
print('bmi_to_glucose_mgdl_per_kgm2 =', format(gb, '.12f'))
print('age_to_glucose_mgdl_per_year =', format(ga, '.12f'))
print('male_minus_female_glucose_mgdl =', format(gs, '.12f'))
print('bmi_to_hba1c_conditional_assumed_pp_per_kgm2 =', format(hb, '.12f'))
print('untruncated_Q1_Q2_Q3_pp_per_requested_unit =', [round(0.010*10, 12), round((hb+hg*gb)*5, 12), round(hb*5, 12)])
print('glucose_location_bounds_mgdl =', [round(mu_g_lo, 12), round(mu_g_hi, 12)])
print('hba1c_location_bounds_pp =', [round(mu_h_lo, 12), round(mu_h_hi, 12)])
print('lognormal_log_sd =', format(math.sqrt(math.log(1+0.2**2)), '.12f'))
print('student_t_scale_for_sd_0.32_df_7 =', format(0.32*math.sqrt((7-2)/7), '.12f'))
print('iran_table2_slope_over_covariance_slope =', format(0.13 / hg, '.12f'))
'@ | python -
```

Exact result (exit code 0):

```text
glucose_to_hba1c_crude_derived_pp_per_mgdl = 0.013540322581
bmi_to_glucose_mgdl_per_kgm2 = 0.432000000000
age_to_glucose_mgdl_per_year = 0.204171428571
male_minus_female_glucose_mgdl = 4.449600000000
bmi_to_hba1c_conditional_assumed_pp_per_kgm2 = 0.006650580645
untruncated_Q1_Q2_Q3_pp_per_requested_unit = [0.1, 0.0625, 0.033252903226]
glucose_location_bounds_mgdl = [82.118594285714, 117.465451428571]
hba1c_location_bounds_pp = [4.400740687742, 6.315731913548]
lognormal_log_sd = 0.198042200435
student_t_scale_for_sd_0.32_df_7 = 0.270449361513
iran_table2_slope_over_covariance_slope = 9.600952948183
```

## Static self-check result

The inline static check exited with code 0. Exact result:

```text
PASS: exactly four artifacts; both JSON objects parsed; Python AST parsed without import/execution.
PASS: synchronous generate(observed, specification, seed); imports numpy/pandas only; top-level imports/definitions/docstring only; no listed unsafe call names.
PASS: exact ordered task columns; 3000 rows specified as eight cells of 375; age/sex boundaries; positive measurement supports; glucose upper bound 126 exclusive; Student df > 2.
PASS: all three requested analysis IDs/formulas/terms/units and all 24 numeric parameter leaf occurrences have generator key references; parameter arithmetic agrees.
PASS: 15 registered artifact SHA256 values verified; 13 selected artifacts registered to the declared sources; 11 distinct evidence item IDs.
LIMIT: static inspection and parameter assertions only; no generator execution, sampled rows, runtime schema checks or fitted estimates.
```

Checks assert declarations and inspect code structure; they do not prove runtime row counts, finite measurements, rejection completion, empirical coefficients or scientific validity. The generator and model specification were unchanged after this check; documentation was updated solely to retain this result.

## Check scope and permitted use

No generator import, execution, sample, seed optimization, simulation validation or clinical validation was performed. Source-statistic simulation checks, output schema checks, realized tail diagnostics and all three fitted WLS analyses require the root's isolated execution; their outcomes are unknown. The source metadata and extractions do not establish transport validity. The fixed specification is suitable for developmental pipeline inspection under its declared assumptions; it is not evidence about actual Mexican coefficients, causal effects, individual patients or national prevalence. Stop after this single construction and ordinary static self-checking; no outcome-informed revision is requested or available. Token telemetry is unavailable and no token counts or costs are asserted.
