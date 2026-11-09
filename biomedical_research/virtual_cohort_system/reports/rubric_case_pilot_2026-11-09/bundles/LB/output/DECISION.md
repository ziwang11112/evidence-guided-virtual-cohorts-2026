# LB construction decision

Delivered one developmental joint law, not an estimate recovered from target results. The four artifacts are `generator.py`, `model_spec.json`, `SOURCE_USE.json` and this record. The program is synchronous `generate(observed, specification, seed)`, uses the supplied specification, and returns the requested six ordered columns and 3,000 fictional rows.

## Scientific choices

BMI has sex-specific lognormal margins fitted algebraically to Agongo arithmetic means and individual SDs. TC and HDL have positive lognormal mixture margins preserving Agongo pooled arithmetic moments under the explicitly assumed F probability 0.5. Greiner Malawi rural F/M geometric-mean ratios specify proportional sex differences. These ratios are used as geometric-mean ratios, never as arithmetic means. All source confidence intervals remain estimation uncertainty; none is converted into individual dispersion or precision weights.

A Gaussian copula joins age, BMI, TC and HDL. The three Ashanti rural unadjusted Spearman correlations are mapped to latent normal correlations using the continuous Gaussian-copula identity. Their use within sex groups, with weak assumed age correlations, is a declared transfer assumption. They are not substituted for raw-scale OLS coefficients or adjusted Pearson residual correlation. The urban triple is retained as declined alternative-context evidence; no target urban/rural mixture is inferred. Agongo and Greiner regression coefficients remain numerically unused because scale and adjustment do not match the request.

Age follows a softplus-normal law above 18 with a source-informed median of 34, assumed shape 0.7, and no upper age cutoff. The age law and 50/50 expected sex composition describe an illustrative scenario; actual target age, sex, site and lifestyle composition are unknown. The softplus upper tail is Gaussian-like; BMI and lipid tails are unbounded lognormal with finite moments. No truncation, clipping, outlier rejection, health/fasting exclusions or TC>=HDL constraint is introduced. Distinct latent components leave conditional variation in each lipid. F/M coding is operationally mapped to source men/women; the target biological label legend is unverified.

Transporting selected fasting laboratory source distributions to immediate CardioChek Plus venous-EDTA measurements, with unestablished fasting status, is unvalidated. The factor 38.67 is numerical unit conversion only. Pregnancy, HIV and diabetes exclusions belong to source contexts and are not applied here. Source populations and repeated statistics are not independent confirmations; no meta-analytic precision is claimed.

## Rubric and analysis delivery

The supplied TASK_RUBRIC.md is used unchanged. `generator.py::_assessment` runs all three requested unweighted OLS/residual analyses during isolated generation, on identical eligible rows and the same full design. It computes the requested means, sample SDs (`ddof=1`), linearly interpolated q10/q50/q90, F fraction, and both residual RMS values (`sqrt(SSE/n)`, mg/dL). It also records schema counts, duplicate IDs, rank, condition number, residual BMI variation, F/M support, min/q01/q99/max, and measured TC<HDL count. Noncomputable fits receive `None` with a reason.

The runtime results are attached as `DataFrame.attrs['developmental_assessment']`. The controller should retain this metadata or independently recompute the same diagnostics because ordinary CSV serialization drops attrs. These analyses have **not** been executed or sampled on the host. Their numerical results and actual finite-sample schema/support checks are unresolved at submission. Implementation is not evidence of a successful run. SOURCE_USE.json contains the rubric's required assessment fields for each analysis ID, with no matching numerical reference asserted and no overall quality score.

The request's four-file/root-execution contract supersedes the common skill's old-style validation, source-checks, freeze and replay steps. No literature adapter, source-feedback collector or author-side isolated execution adapter was supplied, so those steps were not performed. No source reconstruction table is available. Analytic moment agreement is distinct from reconstruction of source participants, covariates, eligibility or measurement conditions, and establishes no target validity.

## Retained deterministic algebra

The following exact PowerShell command was executed once. It uses fixed admitted numbers and explicit assumptions only; it neither imports the generator nor draws random numbers or rows.

```powershell
@'
import json, math
import numpy as np
p=0.5
out={}
for name,m,s,d in [('TC',3.23,0.92,math.log(3.9/3.6)),('HDL',1.14,0.38,math.log(1.1/1.05))]:
    h1=(1-p)+p*math.exp(d)
    h2=(1-p)+p*math.exp(2*d)
    v=math.log((1+(s/m)**2)*h1*h1/h2)
    mu=math.log(m/h1)-v/2
    recovered_mean=math.exp(mu+v/2)*h1
    recovered_sd=math.sqrt(math.exp(2*mu+2*v)*h2-recovered_mean**2)
    out[name]={'log_sex_ratio':d,'log_variance':v,'log_location_M':mu,'pooled_mean':recovered_mean,'pooled_sd':recovered_sd}
for name,m,s in [('BMI_M',20.87,3.15),('BMI_F',22.28,3.85)]:
    v=math.log1p((s/m)**2)
    out[name]={'log_sd':math.sqrt(v),'log_location':math.log(m)-v/2}
a,b,c=[2*math.sin(math.pi*r/6) for r in [0.212,-0.1,0.106]]
R=np.array([[1,.15,.20,.05],[.15,1,a,b],[.20,a,1,c],[.05,b,c,1]])
out['latent_correlation']=R.tolist()
out['eigenvalues']=np.linalg.eigvalsh(R).tolist()
out['cholesky_reconstruction_max_abs_error']=float(np.max(np.abs(np.linalg.cholesky(R)@np.linalg.cholesky(R).T-R)))
q=[-.6744897501960817,0,.6744897501960817]
out['age_population_q25_q50_q75']=[18+16/math.log(2)*float(np.logaddexp(0,z/.7)) for z in q]
print(json.dumps(out,sort_keys=True))
'@ | python -
```

Exact result (exit code 0):

```json
{"BMI_F": {"log_location": 3.0889779369073453, "log_sd": 0.17153121087276166}, "BMI_M": {"log_location": 3.0270499393471284, "log_sd": 0.15008518742354843}, "HDL": {"log_location_M": 0.05508785050991984, "log_sex_ratio": 0.04652001563489291, "log_variance": 0.10481982897258037, "pooled_mean": 1.14, "pooled_sd": 0.37999999999999984}, "TC": {"log_location_M": 1.0934570469273615, "log_sex_ratio": 0.08004270767353636, "log_variance": 0.07640619157389766, "pooled_mean": 3.23, "pooled_sd": 0.9200000000000005}, "age_population_q25_q50_q75": [25.460327677506655, 34.0, 47.702225225811176], "cholesky_reconstruction_max_abs_error": 2.220446049250313e-16, "eigenvalues": [0.7002087667015995, 0.8304960206055519, 1.083032839816765, 1.3862623728760826], "latent_correlation": [[1.0, 0.15, 0.2, 0.05], [0.15, 1.0, 0.22155024842155735, -0.10467191248588766], [0.2, 0.22155024842155735, 1.0, 0.11094596004995781], [0.05, -0.10467191248588766, 0.11094596004995781, 1.0]]}
```

These results demonstrate positive lipid log variances, positive definiteness of the specified latent matrix, and the intended population-moment algebra. Source rounded SDs are treated as approximate population parameters, an assumption. The implied age population quartiles are approximately 25.46, 34 and 47.70 years; this is not an exact fit to unreported source sample-quantile conventions. No requested OLS slope, adjusted residual correlation or target diagnostic was calculated by this command.

## Tools, actions and actual check scope

Used `functions.exec` with `exec_command` for PowerShell `Get-Content` of the allowed documents, `ConvertFrom-Json`/`ConvertTo-Json` to inspect the admitted large Greiner extraction without truncated sections, the retained deterministic algebra above, and JSON authoring that copies selected admitted statistic records into SOURCE_USE.json. Used `apply_patch` to author the other requested artifacts. No URL or original-path reference embedded in source documents was followed. No other bundles, project history, target results, old harness CLI, filesystem-generated cohort or subagent was used. Communication with the root only described progress and the runtime metadata handoff.

Static pre-submission checks were actually run with an inline Python command using only `ast`, `hashlib`, `json`, `math` and `pathlib`. It parsed the generator as syntax, without importing or executing it; parsed the two authored JSON files; checked the exact four filenames, task-ordered specification columns and 3,000-row contract; checked conversion/contrast settings and all three analysis assessment fields; checked the three-position synchronous signature, imports, top-level definitions-only structure and absence of direct filesystem/eval/exec calls; and compared all three admitted source hashes with registry.json. All assertions passed (exit code 0). This is a limited static inspection, not a security audit or demonstration of runtime behavior.

Actual returned check result:

```json
{"all_three_analysis_records_and_required_fields": true, "exact_four_artifacts": true, "generator_imported_or_executed": false, "imports": ["math", "numpy", "pandas"], "json_and_finite_literals": true, "ordered_schema_and_3000_contract": true, "python_AST_and_synchronous_ABI": true, "registered_source_hashes": {"agongo_2018_navrongo": "matched registered SHA256", "greiner_2021": "matched registered SHA256", "obirikorang_2015_ashanti": "matched registered SHA256"}, "rows_sampled": false, "status": "static checks passed", "top_level_only_docstring_imports_definitions": true}
```

No simulation, clinical validation, source replay, external review, target comparison or seed optimization is claimed.

## Permitted use and unresolved limitations

This construction supports inspection of an explicit fictional data law and descriptive estimator demonstrations once executed. It does not support clinical or causal conclusions, measurement replacement, target representativeness, calibrated inferential uncertainty or publication readiness. The largest uncertainties are demographic composition, distribution tails, age-related dependence, transferring unadjusted rank relations into a joint adjusted analysis, cross-study combination of moments and sex ratios, and assay/health-selection transfer. Repeated seeds reflect conditional simulation variation, not new scientific evidence or uncertainty about these choices.

Stop after this one construction and ordinary pre-submission checks. The root handles staging and three later fixed-seed draws from sealed bytes. No study-level feedback or output-informed revision was provided. Token/cost telemetry is unavailable and no counts are invented.
