# HC construction decision

Delivered one explicit whole-cohort generator for 3,000 fictional adults, with 375 per prescribed age-sex cell. The population is the task's Mexico analytical-use selection, including 8–12-hour fasting, valid consistent standing-anthropometry documentation, diagnosis exclusion and routed pregnancy/lactation restrictions. These unrepresented selection features are construction assumptions, not verified row-level facts. Medication and anemia are not assumed excluded. Equal-cell WLS is the intended estimator; no national-survey inference is supported.

The conditional law uses a right-skewed bounded beta BMI distribution, beta glucose with a linear conditional mean and fixed conditional SD, and a linear HbA1c mean with independent bounded symmetric beta residuals. Scientific parameters are in `model_spec.json` and read by the generator. There is no sample fitting, row recentering, outcome clipping, seed optimization, or forced finite-sample coefficient. The strict glucose endpoint is protected only against floating-point rounding. All three scientific questions retain their original definitions.

The NHANES adjusted age coefficient informs Q1. Finnish age/sex-adjusted BMI associations inform Q2 and the glucose mean, with explicit transport from its different age coding, survey design, diabetes exclusions and HbA1c restriction. Q3 requires an unreported conditional HbA1c–glucose association: 0.01 percentage points per mg/dL is the chosen scenario, not a recovered estimate. This yields a derived conditional BMI coefficient. The Q2/Q3 difference describes joint regression algebra, not biological mediation. The Iranian article's Table 2 slopes were declined because reported raw scales disagree with its correlation and marginal SDs; they were not silently repaired or treated as adjusted evidence. See `SOURCE_USE.json` for exact locators, weighting, selection, units and uncertainty limitations.

All distribution shapes, support bounds, conditional dispersions and population transfer remain assumptions. In particular, BMI outside 14–55, glucose below 45, and HbA1c outside the law's broad implied range are unmodeled. The upper HbA1c tail is not restricted to 6.5%, but extreme discordant measurements remain underrepresented. No source SE or predictive-margin CI was converted to an individual SD. Seeds vary fictional individuals, not uncertainty about the evidence or model.

## Guidance and actions actually used

Read `REQUEST.md`, task/request/registry, the unchanged `TASK_RUBRIC.md`, supplied base skill and linked harness-interface reference, and supplied analysis-guided-cohort skill with rubric/procedures references. Applied source-definition, conditional-variation, joint-dependence and hypothesis-dependent-construction procedures. No replacement rubric or success tolerance was invented. The longitudinal procedure is inapplicable. The old validate/freeze/source-check workflow is explicitly replaced by REQUEST.md's four-file contract; no such CLI was called. There is no source-replay or literature adapter in this pass.

Used PowerShell `Get-Content`, XML-node/table extraction and `rg --files` to inspect allowed evidence. Initial combined full-source output was truncated, so focused XML/table and text reads were used for adopted claims. The attempted `input/` inventory reported that the optional directory does not exist; there are no observed participant inputs. Used one deterministic inline Python calculation through `exec_command`, retained verbatim below, and `apply_patch` to write the four outputs. Static parsing/inventory checks are recorded below. No other bundle, project history, target/evaluation reference or external source was read; no subagent was used. No generator was imported or executed and no rows were sampled. No simulation or clinical validation was performed. Token telemetry and costs are unavailable and are not reported.

## Retained deterministic algebra

The following exact PowerShell command was executed once. It uses only scalar mathematics and the declared finite age support, with no random draws, files or generator import:

```powershell
@'
import json, math
ages = [list(range(25,40)),list(range(40,55)),list(range(55,70)),list(range(70,80))]
ea = sum(sum(x)/len(x) for x in ages)/4
va = sum(sum((a-ea)**2 for a in x)/len(x) for x in ages)/4
lo,hi,bm,bs=14.,55.,28.01,5.5
p=(bm-lo)/(hi-lo); k=p*(1-p)*(hi-lo)**2/bs**2-1
ba,bb=p*k,(1-p)*k
ga=18*.1985/17.5; gb=18*.024; gf=-18*.2472; gh=.01
hb=.0125-gh*gb; hf=.023-gh*gf
vg=ga*ga*va+gb*gb*bs*bs+gf*gf*.25+100
tha=.01+gh*ga; thb=hb+gh*gb; thf=hf+gh*gf
vh=tha*tha*va+thb*thb*bs*bs+thf*thf*.25+gh*gh*100+.32**2
cg=tha*ga*va+thb*gb*bs*bs+thf*gf*.25+gh*100
mglo=94+ga*(25-50)+gb*(lo-bm)+gf*.5
mghi=94+ga*(79-50)+gb*(hi-bm)-gf*.5
gshapes=[]
for m in (mglo,mghi):
    q=(m-45)/81; c=(m-45)*(126-m)/100-1
    gshapes.append([q*c,(1-q)*c])
hlo=5.45+.01*(25-50)+hb*(lo-bm)-hf*.5+gh*(45-94)-3*.32
hhi=5.45+.01*(79-50)+hb*(hi-bm)+hf*.5+gh*(126-94)+3*.32
out={'age_mean':ea,'age_variance':va,'bmi_beta_shapes':[ba,bb],'glucose_age_per_year':ga,'glucose_bmi_per_unit':gb,'glucose_female_contrast':gf,'hba1c_conditional_bmi_per_unit':hb,'hba1c_conditional_female_contrast':hf,'glucose_mean_support':[mglo,mghi],'glucose_shapes_at_mean_endpoints':gshapes,'hba1c_support_bounds':[hlo,hhi],'population_Q1_Q2_Q3':[.01*10,thb*5,hb*5],'age_residual_variance_after_female_bmi_glucose':va*100/(ga*ga*va+100),'bmi_residual_variance_after_age_female_glucose':bs*bs*100/(gb*gb*bs*bs+100),'glucose_marginal_sd':math.sqrt(vg),'hba1c_marginal_mean':5.45+tha*(ea-50),'hba1c_marginal_sd':math.sqrt(vh),'glucose_hba1c_marginal_correlation':cg/math.sqrt(vg*vh),'hba1c_conditional_residual_variance':.32**2,'Kerman_crude_h_on_g_from_reported_r_and_sd':.23*.73/12.4,'Kerman_crude_g_on_h_from_reported_r_and_sd':.23*12.4/.73}
print(json.dumps(out,sort_keys=True,indent=2))
'@ | python -
```

Exit code 0; returned:

```json
{
  "Kerman_crude_g_on_h_from_reported_r_and_sd": 3.9068493150684938,
  "Kerman_crude_h_on_g_from_reported_r_and_sd": 0.013540322580645161,
  "age_mean": 53.875,
  "age_residual_variance_after_female_bmi_glucose": 242.9755595213817,
  "age_variance": 270.359375,
  "bmi_beta_shapes": [3.9296894972787744, 7.5704724861922985],
  "bmi_residual_variance_after_age_female_glucose": 28.633529592435735,
  "glucose_age_per_year": 0.2041714285714286,
  "glucose_bmi_per_unit": 0.432,
  "glucose_female_contrast": -4.4496,
  "glucose_hba1c_marginal_correlation": 0.4127835441198015,
  "glucose_marginal_sd": 11.039261951887815,
  "glucose_mean_support": [80.6185942857143, 113.80545142857143],
  "glucose_shapes_at_mean_endpoints": [[6.668248845365187, 8.4959699371602], [6.27787241264799, 1.1126417815998453]],
  "hba1c_conditional_bmi_per_unit": 0.00818,
  "hba1c_conditional_female_contrast": 0.067496,
  "hba1c_conditional_residual_variance": 0.1024,
  "hba1c_marginal_mean": 5.496661642857143,
  "hba1c_marginal_sd": 0.3955524002006884,
  "hba1c_support_bounds": [3.6016502, 7.2745262],
  "population_Q1_Q2_Q3": [0.1, 0.0625, 0.0409]
}
```

Interpretation of this calculation:

- The total-variance formula includes age, sex, BMI and residual glucose contributions, so 0.32 is not mislabeled as marginal HbA1c SD. It yields marginal SD 0.39555 under this law. Independent residual variation remains after all requested covariates.
- BMI beta shapes are positive. Glucose concentration `(m-45)*(126-m)/100-1` is a concave quadratic in the conditional mean; positive values at both attained endpoints imply positive concentration throughout. With the mean strictly between 45 and 126, both beta shapes are positive throughout. No draw is needed for this admissibility argument.
- The population linear partial variances for age and BMI are positive. Together with nonzero sex variance and conditional glucose variance, the predictor covariance is positive definite in this law. This does not substitute for finite-draw matrix rank/collinearity diagnostics.
- The own-law coefficients are 0.100, 0.0625 and 0.0409 in the requested units. They are chosen-law consequences, not observed results or independent source fits. The own-law Q2-minus-Q3 difference is 0.0216 percentage points per 5 kg/m². Finite estimates may differ.
- The own-law marginal glucose–HbA1c correlation 0.41278 differs from the Kerman subgroup's 0.23. This is a descriptive incompatibility with treating that source r as a universal target. No source-context reconstruction was performed; different population selection and age/sex design cannot be disentangled from the assumed joint law here.
- HbA1c remains positive throughout the full support. The law permits HbA1c above 6.5 and does not impose the Finnish source's HbA1c eligibility rule on HC.

## Static self-check

Executed one inline Python static checker through PowerShell/`exec_command`, using only `ast`, `json` and `pathlib` to read the allowed task/request and four output files. It checked exact four-file inventory, parsed both JSON artifacts and Python AST, verified a synchronous three-positional-argument `generate(observed, specification, seed)` signature, required import/definition-only module top level and NumPy/Pandas imports, compared declared count/ordered columns/transformations and analysis definitions to the task/request, checked all required rubric fields, and resolved specification source/assumption links against `SOURCE_USE.json` IDs. This parser did not import the generator. Exit code 0; returned:

```json
{
  "JSON_parse": "passed",
  "Python_AST_and_ABI": "passed",
  "analysis_ids": ["Q1_age10", "Q2_bmi5", "Q3_bmi5"],
  "declared_rows": 3000,
  "generator_executed": false,
  "generator_imported": false,
  "imports": ["numpy", "pandas"],
  "ordered_columns": ["row_id", "age", "female", "bmi", "glucose", "hba1c"],
  "output_file_count": 4,
  "parameter_source_links": "resolved",
  "rows_sampled": 0,
  "status": "passed",
  "top_level": "imports_and_definitions_only"
}
```

Only this documentation record was subsequently updated with the result. No runtime, finite-cohort or clinical check is implied by static acceptance. No legacy harness validation command was run.

## Criterion results and permitted use

| Criterion | Actual evidence | Assessment and next action |
|---|---|---|
| Task invariants | Declared exact schema/counts; deterministic support calculation | Unresolved for actual output. Root must verify schema, finite values, integer/binary fields, unique IDs, duplicate profiles and 375 rows/cell after isolated execution. |
| Q1_age10 | Source-defined adjusted age slope; own-law coefficient and partial age variance | Unresolved for delivered cohorts and transfer. Run required WLS, rank, covariate-dependence and per-cell residual checks. |
| Q2_bmi5 | Source-defined age/sex-adjusted BMI slope; own-law reduced conditional mean | Unresolved for delivered cohorts and transfer. Run WLS and BMI conditional/joint diagnostics. |
| Q3_bmi5 | Explicit unreported dependence scenario; own-law adjusted slope and partial BMI variance | Unresolved scientifically. Run WLS/collinearity/residual checks; retain scenario dependence of Q2/Q3 difference. |
| Source reconstruction | Estimator/source extraction and raw-slope consistency algebra | Unresolved. Source weights, joint covariates and faithful source replay are unavailable. |
| Marginals, quantiles and tails | Only population moments/support were calculated | Unresolved for finite draws and source fit. Inspect all provider-defined diagnostics, glucose near 126 and all cell supports. |

No cohort-level WLS, quantiles, invalid-row counts, duplicate checks, cellwise residual diagnostics, simulation or clinical validation was run. The root's later three sealed-seed draws are not results available to this author and must not be used here to optimize a seed. The existing rubric's requirement to run all analyses is retained as an outstanding isolated-execution action, not marked passed.

Permitted use is developmental inspection of these three regressions under the declared scenario. Representative Mexican population estimates, clinical prevalence/tail claims, clinical power guarantees, measurement savings, causal conclusions and publication-ready validation are unsupported. This single construction stops after ordinary pre-submission checks because no additional evidence, source-feedback collector, execution feedback or revision pass is supplied.
