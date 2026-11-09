# LC construction decision

Submit one developmental joint-law generator and its specification. All 3,000 rows are fictional. No generator was imported or executed on the host, no rows were sampled, and no seed was selected or optimized. The root owns staging and isolated execution of these bytes.

Agongo's sex-specific BMI arithmetic means/individual SDs and pooled lipid arithmetic means/individual SDs provide the scale anchors. Their restricted Ghana population is not reconstructed: transport to a broader adult age distribution, recorded F/M, different selection and CardioChek Plus measurements is explicit. Greiner rural Malawi female/male geometric-mean ratios supply only the numerical multiplicative sex ratios, with a separately declared assumption that these marginal contrasts can act conditionally. Geometric means are not arithmetic means. Neither study's unresolved-scale regression coefficients enter the model.

The joint law uses one internally coherent rural Ashanti Spearman triple in an assumed age/sex-conditional Gaussian copula. Source unadjusted rank correlations are not adjusted Pearson correlations. Conditioning and population transfer are assumptions, and the mathematical Gaussian-copula conversion is family-dependent. Urban correlations were read but not pooled into an invented target mixture. There is no evidence identifying the target conditional covariance; this construction is one transparent scenario.

Age is 18 plus Gamma(2, 10 years), with no finite upper bound. Recorded F probability is 0.5. Both are assumed composition, not recovered target demographics. Age is independent of sex and of BMI within sex; that is a stated simplification rather than evidence of a null relationship. Lipid log-age trends are assumed 0.003/year for TC and 0.0005/year for HDL. BMI and age/sex-conditional lipids have lognormal margins. The specification recomputes lipid log variances after subtracting the moment contributions of age and sex; published marginal SDs are not inserted unchanged as residual SDs. No arbitrary upper BMI/lipid cap, TC>=HDL filter, health exclusion or fasting exclusion is used.

Finite second moments and positive-definite latent covariance are established for this law by the retained algebra. Continuous residual variation remains. The law has unvalidated tails: P(age>100)=0.0025268128 and P(age>120)=0.0004163076; these are consequences of the assumed gamma law, not plausible-age certifications. Positive lipid moments exist for order q<1/(10*b), including second moments. No diagnostic can establish clinical support merely from this probability-law choice.

## Fixed rubric and findings

TASK_RUBRIC.md was applied unchanged, with the supplied base skill/interface and analysis-guided-cohort skill plus rubric/procedure references. Source definition, conditional variation and joint dependence procedures were relevant; longitudinal procedures were not. REQUEST.md replaces the old harness bundle/freeze/execution steps. No harness CLI, source collector, literature adapter or independent reviewer was used.

| Goal | Actual finding | Assessment and next action |
|---|---|---|
| Task invariants | Static generator structure and positive-support law specified; unique IDs and ordered fields follow directly from code | Finite-table result unresolved until isolated execution validates 3,000 complete finite rows, exact columns/units/categories and identifiers |
| K02-HDL-BMI | Declared-law OLS projection: -2.0977372705 mg/dL per 5 BMI; BMI residual variance 12.3725; HDL residual RMS 14.5809556688 mg/dL | Mathematical implication computed; finite-sample analysis and target support unresolved |
| K02-TC-BMI | Declared-law OLS projection: 10.7071243905 mg/dL per 5 BMI; TC residual RMS 33.9725809678 mg/dL | Mathematical implication computed; finite-sample analysis and target support unresolved |
| K02-LIPID-RESIDUAL | Declared-law adjusted Pearson residual correlation 0.1320653055; both residual variances positive; copula determinant 0.9225045789 | Mathematical implication computed; source statistic is a different operator, and target support unresolved |
| Selected source moments | Law arithmetic means/SDs reproduce chosen lipid anchors algebraically; BMI sex moments are imposed by lognormal parameterization | Demonstrated only for imposed own-law moments, not a source-population replay or independent validation |

These numerical results were derived after choosing parameters from permitted sources and named assumptions. They were not desired targets and caused no output-informed revision. Source pooled BMI 21.63/3.61 is deliberately not an extra constraint: the assumed 50/50 sex mixture implies 21.575/3.587412 instead.

The root should execute every requested OLS analysis on the same eligible rows and Pearson-correlate the full-model residuals. Diagnostics are means, sample SDs (ddof=1), linear-interpolation q10/q50/q90 for age/BMI and converted lipids, residual RMS sqrt(SSE/n), F fraction, rank, BMI variation after age/sex, subgroup support, invalid/duplicate rows and tails. Lipids are delivered in mmol/L and multiplied by 38.67 for analysis. Full coding is `[1, (age-50)/10, I(F), (bmi-25)/5]`, so the BMI5 coefficient is already per 5 kg/m². Quantile conventions here do not assert a source quantile convention. None of these finite-row calculations has been performed in this construction context. No sign, p-value, similarity band or numerical clinical pass threshold is imposed.

## Retained deterministic algebra

This exact PowerShell inline command was executed using `functions.exec` -> `exec_command`. It imports only standard-library `math` and `json`; it neither imports the generator nor samples observations. `LA` and `LF` are log MGFs of centered gamma age and the F indicator. Conditional-sex means and cross-moments identify the population OLS projections. The variance/covariance subtraction is the Frisch-Waugh-Lovell projection using mutually orthogonal centered age, sex, and sex-residualized BMI. Residual RMS here is the square root of the probability-law projection residual variance, not an observed finite-table RMS.

```powershell
@'
import math, json
p=0.5; k=2.0; theta=10.0
mB=[20.87,22.28]; sdB=[3.15,3.85]
m=[3.23,1.14]; sd=[0.92,0.38]; b=[0.003,0.0005]
d=[math.log(3.9/3.6),math.log(1.1/1.05)]
r=[2*math.sin(math.pi*x/6) for x in [0.212,-0.1,0.106]]
LA=lambda x:-k*theta*x-k*math.log1p(-theta*x)
LF=lambda x:math.log((1-p)+p*math.exp(x))
v=[math.log1p((sd[j]/m[j])**2)-(LA(2*b[j])-2*LA(b[j]))-(LF(2*d[j])-2*LF(d[j])) for j in range(2)]
mu=[math.log(m[j])-LA(b[j])-LF(d[j])-v[j]/2 for j in range(2)]
vB=[math.log1p((sdB[s]/mB[s])**2) for s in range(2)]
VLb=(1-p)*sdB[0]**2+p*sdB[1]**2
conditional_means=[[m[j]*math.exp(d[j]*s-LF(d[j])) for s in [0,1]] for j in range(2)]
betaB=[sum([(1-p),p][s]*mB[s]*conditional_means[j][s]*math.expm1(math.sqrt(vB[s]*v[j])*r[j]) for s in [0,1])/VLb for j in range(2)]
betaA=[m[j]*b[j]/(1-theta*b[j]) for j in range(2)]
delta=[x[1]-x[0] for x in conditional_means]
VA=k*theta**2
cov=m[0]*m[1]*math.expm1(LA(sum(b))-sum(LA(x) for x in b)+LF(sum(d))-sum(LF(x) for x in d)+math.sqrt(v[0]*v[1])*r[2])
resvar=[sd[j]**2-p*(1-p)*delta[j]**2-VA*betaA[j]**2-VLb*betaB[j]**2 for j in range(2)]
rescov=cov-p*(1-p)*delta[0]*delta[1]-VA*betaA[0]*betaA[1]-VLb*betaB[0]*betaB[1]
det=1+2*r[0]*r[1]*r[2]-sum(x*x for x in r)
result={'latent_correlations_B_TC_B_HDL_TC_HDL':r,'copula_leading_minors':[1,1-r[0]**2,det],'normal_log_variances_TC_HDL':v,'log_intercepts_TC_HDL':mu,'BMI_mean':sum([(1-p),p][s]*mB[s] for s in [0,1]),'BMI_sd':math.sqrt(VLb+p*(1-p)*(mB[1]-mB[0])**2),'BMI_variance_after_age_sex':VLb,'age_mean':18+k*theta,'age_sd':math.sqrt(VA),'P_age_gt100':math.exp(-8.2)*(1+8.2),'P_age_gt120':math.exp(-10.2)*(1+10.2),'lipid_marginal_mean_mg_dl':[x*38.67 for x in m],'lipid_marginal_sd_mg_dl':[x*38.67 for x in sd],'OLS_5BMI_TC_HDL_mg_dl':[x*5*38.67 for x in betaB],'OLS_age_TC_HDL_mmol_per_year':betaA,'OLS_residual_variance_TC_HDL_mmol2':resvar,'OLS_conditional_RMS_TC_HDL_mg_dl':[math.sqrt(x)*38.67 for x in resvar],'OLS_residual_correlation':rescov/math.sqrt(resvar[0]*resvar[1]),'declared_law_source_moment_identity':{'TC_mean':math.exp(mu[0]+LA(b[0])+LF(d[0])+v[0]/2),'HDL_mean':math.exp(mu[1]+LA(b[1])+LF(d[1])+v[1]/2),'TC_sd':m[0]*math.sqrt(math.expm1(LA(2*b[0])-2*LA(b[0])+LF(2*d[0])-2*LF(d[0])+v[0])),'HDL_sd':m[1]*math.sqrt(math.expm1(LA(2*b[1])-2*LA(b[1])+LF(2*d[1])-2*LF(d[1])+v[1]))}}
print(json.dumps(result,indent=2))
'@ | python -
```

The command exited 0 and printed:

```json
{
  "latent_correlations_B_TC_B_HDL_TC_HDL": [0.22155024842155735, -0.10467191248588766, 0.11094596004995781],
  "copula_leading_minors": [1, 0.9509154874243462, 0.9225045789083934],
  "normal_log_variances_TC_HDL": [0.07449221407655696, 0.10476932455975474],
  "log_intercepts_TC_HDL": [1.0934956207066144, 0.05508801906924404],
  "BMI_mean": 21.575000000000003,
  "BMI_sd": 3.5874120198271067,
  "BMI_variance_after_age_sex": 12.3725,
  "age_mean": 38.0,
  "age_sd": 14.142135623730951,
  "P_age_gt100": 0.002526812843743711,
  "P_age_gt120": 0.0004163075692622194,
  "lipid_marginal_mean_mg_dl": [124.9041, 44.0838],
  "lipid_marginal_sd_mg_dl": [35.5764, 14.694600000000001],
  "OLS_5BMI_TC_HDL_mg_dl": [10.707124390512655, -2.0977372705136053],
  "OLS_age_TC_HDL_mmol_per_year": [0.009989690721649486, 0.0005728643216080402],
  "OLS_residual_variance_TC_HDL_mmol2": [0.77180704882519, 0.1421751303074618],
  "OLS_conditional_RMS_TC_HDL_mg_dl": [33.97258096780359, 14.580955668790224],
  "OLS_residual_correlation": 0.1320653055105349,
  "declared_law_source_moment_identity": {"TC_mean": 3.2299999999999995, "HDL_mean": 1.14, "TC_sd": 0.92, "HDL_sd": 0.38000000000000006}
}
```

## Actions and use limits

Actual tools/actions: `functions.exec` with `exec_command` read only the allowed bundle files and guidance using PowerShell, including compact structural views of the long Greiner extraction; `apply_patch` wrote the generator, model specification and this record; inline standard-library Python wrote SOURCE_USE.json by retaining admitted source rows and explicit decisions; inline deterministic algebra was run and retained above. A pre-submission prose correction fixed the stated HDL tail-moment limit from 2,000 to 200 (1/(10*0.0005)); no scientific parameter or generator law was changed in response to a sample. Static pre-submission checks are recorded below after execution. No network, literature query/download, old author material, other bundle, target result, generator execution, source replay, simulation, clinical validation, reviewer or output-informed revision was used.

Only fictional developmental analysis and assumption exploration are supported. The requested analyses remain assumption-dependent and empirically unchecked here. Actual target composition, adjusted associations, residual dependence, assay bridge, tail calibration, parameter uncertainty and selection effects remain unresolved. The recorded source CIs concern estimation, not individual dispersion, and are not converted to SD or precision weights. Multiple rows/seeds cannot resolve these limitations. No token telemetry is available and no token/cost estimate is supplied.


## Static submission checks

A standard-library-only inline Python check (`ast`, `hashlib`, `json`, `pathlib`) exited 0. It strictly parsed both JSON outputs (rejecting duplicate keys and nonfinite constants), parsed generator AST without import/execution, checked the synchronous three-positional-argument ABI and import-only/definition-only top level, compared row count/column order with task.json, verified stable analysis IDs and rubric assessment fields, and recomputed the three admitted-source SHA-256 hashes against registry.json.

Actual results: exactly `DECISION.md`, `SOURCE_USE.json`, `generator.py`, `model_spec.json`; JSON 2/2 valid; generator AST/ABI valid; only math/NumPy/pandas imports and no import-time calls; n=3000 and exact column order agree; all three analysis IDs covered; admitted source hashes 3/3 match. Generator was not imported or executed and no rows were sampled. This is a static pre-submission check, not the replaced harness validator or an execution receipt. The check record was then appended to SOURCE_USE.json using JSON serialization; its final parse was also successful.
