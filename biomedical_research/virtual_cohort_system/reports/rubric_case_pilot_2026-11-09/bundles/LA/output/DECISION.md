# LA construction decision

Submitted one fixed whole-cohort scenario for 3,000 independent adults. The generator returns the exact ordered six-column schema, using source-unit mmol/L lipids. It does not compute, optimize or force any of the three requested OLS/residual-analysis results. All scientific settings are read from `model_spec.json`.

Navrongo supplies arithmetic BMI/lipid moments and individual SDs; rural Malawi supplies an adult age template and geometric female/male lipid contrasts; rural Ashanti supplies the three pairwise Spearman correlations for one coherent Gaussian copula. The fitted object is a conditional lognormal scenario, not a reconstruction of any source cohort. In particular, interpreting unadjusted source correlations and sex differences as conditional dependence/effects is an explicit strong assumption. Source moments become reference distributions at age 50 and centered sex; the resulting full-age marginals need not equal those source moments.

Equal sex probability, age support 18-90 with piecewise-uniform quantile intervals, weak positive log-BMI/log-TC age trends, and zero log-HDL age trend are working assumptions. No evidence establishes the zero age trend or the tail shape. The six-SD latent cap gives finite positive bounded measurements and affects nominal Gaussian probability about 1.97e-9 per component. It makes uncapped lognormal moment/copula identities approximate. Positive measured HDL may exceed measured TC; no ordering filter or invented assay correction is imposed. This is a model limitation requiring inspection, not a biological statement about true non-HDL cholesterol.

All three requested analyses are supported computationally by the intended complete rows but remain scientifically assumption-dependent. No directly matched age/sex-adjusted BMI slopes or raw-scale Pearson lipid residual correlation exists in the admitted extracts. Unresolved-scale Agongo/Greiner regression coefficients were excluded from numeric calibration. Source CI widths were not used as individual SDs or precision weights. Missing uncertainty remains missing. Shared-source summaries are dependent evidence, not replication. Fixed seeds vary sampled individuals, not evidence or transport uncertainty.

I applied the supplied common `base_skill/SKILL.md` and its linked `references/harness-interface.md`. REQUEST.md replaces their old candidate/freeze/CLI steps with these four files; no old harness CLI was called. The interface's request to inspect project contracts or other documents was not followed because those files are outside the explicitly allowed-read list. No TASK_RUBRIC.md or additional reusable procedure skill was supplied in this bundle's allowed inputs. No external source collector or literature adapter was available.

Tools/actions actually used: PowerShell reads of allowed task/guidance/source/input files; JSON field selection to recover an initially truncated source read; deterministic inline Python standard-library algebra; ordinary JSON/AST/schema/source-hash static checks and scalar support algebra; file writing through apply_patch. No network, old author bundle, project-history file, sampling call, generator import/execution, subagent, review agent, source feedback or seed search was used.

## Retained deterministic algebra

The following exact PowerShell command was executed. It creates no file and does not import or execute the generator.

```powershell
@'
import math, json
from statistics import NormalDist
r = [2*math.sin(math.pi*x/6) for x in (0.212, -0.1, 0.106)]
a,b,c = r
det = 1 + 2*a*b*c - a*a - b*b - c*c
res = (c-a*b)/math.sqrt((1-a*a)*(1-b*b))
params = {}
for name,m,s in [('BMI_M',20.87,3.15),('BMI_F',22.28,3.85),('TC',3.23,0.92),('HDL',1.14,0.38)]:
    v = math.log1p((s/m)**2)
    params[name] = {'log_location':math.log(m)-v/2, 'log_sd':math.sqrt(v), 'nominal_recovered_mean':math.exp(math.log(m)-v/2+v/2), 'nominal_recovered_sd':math.sqrt((math.exp(v)-1)*math.exp(2*(math.log(m)-v/2)+v))}
print(json.dumps({'latent_correlations_BMI_TC_BMI_HDL_TC_HDL':r, 'determinant':det, 'conditional_latent_TC_HDL_given_BMI':res, 'lognormal_parameters':params, 'TC_female_log_ratio':math.log(3.9/3.6), 'HDL_female_log_ratio':math.log(1.1/1.05), 'per_variable_cap_probability_6':2*(1-NormalDist().cdf(6)), 'union_bound_cap_any_3000_by_3':9000*2*(1-NormalDist().cdf(6))}, indent=2))
'@ | python -B -
```

Result (exit code 0):

```json
{
  "latent_correlations_BMI_TC_BMI_HDL_TC_HDL": [0.22155024842155735, -0.10467191248588766, 0.11094596004995781],
  "determinant": 0.9225045789083934,
  "conditional_latent_TC_HDL_given_BMI": 0.13831420562981062,
  "lognormal_parameters": {
    "BMI_M": {"log_location": 3.0270499393471284, "log_sd": 0.15008518742354843, "nominal_recovered_mean": 20.869999999999997, "nominal_recovered_sd": 3.1500000000000044},
    "BMI_F": {"log_location": 3.0889779369073453, "log_sd": 0.17153121087276166, "nominal_recovered_mean": 22.28, "nominal_recovered_sd": 3.849999999999995},
    "TC": {"log_location": 1.1334796807657677, "log_sd": 0.2792935963061002, "nominal_recovered_mean": 3.2299999999999995, "nominal_recovered_sd": 0.9199999999999997},
    "HDL": {"log_location": 0.07834800457749083, "log_sd": 0.3245928459745013, "nominal_recovered_mean": 1.14, "nominal_recovered_sd": 0.38000000000000006}
  },
  "TC_female_log_ratio": 0.08004270767353636,
  "HDL_female_log_ratio": 0.04652001563489291,
  "per_variable_cap_probability_6": 1.973175400848959e-09,
  "union_bound_cap_any_3000_by_3": 1.775857860764063e-05
}
```

The partial correlation above concerns uncapped Gaussian innovations given latent BMI. It is not the requested Pearson correlation of residuals after observed-scale OLS. Recovery of inserted uncapped lognormal moments is an algebra check, not independent evidence or a source fit test.

## Retained ordinary static checks

This exact command was executed without loading generator code as a module or calling its functions. It reads only allowed files and creates no additional artifact.

```powershell
@'
import ast, hashlib, json, math
from pathlib import Path
b = Path('work/rubric_case_pilot_2026-11-09/bundles/LA')
o = b / 'output'
expected = {'generator.py', 'model_spec.json', 'SOURCE_USE.json', 'DECISION.md'}
assert {p.name for p in o.iterdir()} == expected
spec = json.loads((o / 'model_spec.json').read_text(encoding='utf-8'))
use = json.loads((o / 'SOURCE_USE.json').read_text(encoding='utf-8'))
task = json.loads((b / 'task.json').read_text(encoding='utf-8'))
request = json.loads((b / 'request.json').read_text(encoding='utf-8'))
registry = json.loads((b / 'registry.json').read_text(encoding='utf-8'))
assert spec['n_rows'] == task['n_rows'] == request['n_rows'] == 3000
assert spec['ordered_columns'] == [c['name'] for c in task['columns']]
assert spec['evaluation_unit_conversion']['factor'] == 38.67
assert {x['id'] for x in spec['analyses']} == {x['id'] for x in request['intended_analyses']}
assert {x['analysis_id'] for x in use['analyses']} == {x['id'] for x in request['intended_analyses']}
for item in registry['artifacts']:
    assert hashlib.sha256((b / item['path']).read_bytes()).hexdigest() == item['sha256']
tree = ast.parse((o / 'generator.py').read_text(encoding='utf-8'))
assert all(isinstance(x, (ast.Import, ast.FunctionDef)) for x in tree.body)
assert [a.name for x in tree.body if isinstance(x, ast.Import) for a in x.names] == ['numpy', 'pandas']
gen = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'generate')
assert [a.arg for a in gen.args.args] == ['observed', 'specification', 'seed']
assert not (gen.args.posonlyargs or gen.args.kwonlyargs or gen.args.vararg or gen.args.kwarg or gen.args.defaults or gen.decorator_list)
data = next(x.value for x in ast.walk(gen) if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'data' for t in x.targets))
assert [x.value for x in data.keys] == spec['ordered_columns']
p = spec['parameters']
assert 0 < p['sex']['probability_F'] < 1
for key in ('quantile_probabilities', 'quantile_values_M', 'quantile_values_F'):
    values = p['age'][key]
    assert len(values) == 5 and all(x < y for x,y in zip(values, values[1:]))
assert p['age']['quantile_probabilities'][0] == 0 and p['age']['quantile_probabilities'][-1] == 1
assert p['age']['quantile_values_M'][0] >= 18 and p['age']['quantile_values_F'][0] >= 18
r1,r2,r3 = [2*math.sin(math.pi*x/6) for x in p['dependence']['reference_spearman']]
minor2 = 1-r1*r1
det = 1+2*r1*r2*r3-r1*r1-r2*r2-r3*r3
assert minor2 > 0 and det > 0
bounds = {}
for variable in ('bmi', 'total_cholesterol', 'hdl_cholesterol'):
    pairs = []
    q = p[variable]
    for sex,s in [('M',0),('F',1)]:
        m,sd = (q[sex]['mean'],q[sex]['sd']) if variable == 'bmi' else (q['reference_mean'],q['reference_sd'])
        v = math.log1p((sd/m)**2)
        mu = math.log(m)-v/2
        shift = 0 if variable == 'bmi' else (s-q['sex_effect_center'])*math.log(q['female_reference_geometric_mean']/q['male_reference_geometric_mean'])
        for age in (18,90):
            for z in (-p['dependence']['latent_cap_sd'],p['dependence']['latent_cap_sd']):
                pairs.append(math.exp(mu+math.sqrt(v)*z+q['log_change_per_age_scale']*(age-p['age']['effect_center_years'])/p['age']['effect_scale_years']+shift))
    bounds[variable] = [min(pairs),max(pairs)]
    assert all(math.isfinite(x) and x > 0 for x in pairs)
print(json.dumps({'file_set_exact':True,'json_and_AST_parse':True,'ABI_and_schema_static':True,'source_hashes_matched':3,'analysis_IDs_matched':3,'correlation_leading_minors':[1,minor2,det],'analytic_support_bounds':bounds,'generator_executed':False,'sampling_performed':False},indent=2))
'@ | python -B -
```

Result (exit code 0):

```json
{
  "file_set_exact": true,
  "json_and_AST_parse": true,
  "ABI_and_schema_static": true,
  "source_hashes_matched": 3,
  "analysis_IDs_matched": 3,
  "correlation_leading_minors": [1, 0.9509154874243462, 0.9225045789083934],
  "analytic_support_bounds": {
    "bmi": [7.12628935344978, 69.28061921976814],
    "total_cholesterol": [0.5156622660735566, 19.091870428677122],
    "hdl_cholesterol": [0.1506992607072059, 7.761418300999479]
  },
  "generator_executed": false,
  "sampling_performed": false
}
```

The support extrema are possible limiting values, not observed rows or frequency estimates. Their scientific plausibility and extreme-tail frequency have not been validated. Static checks establish text/contract consistency, not realized DataFrame validity. These check records were then added to SOURCE_USE.json and this decision record without changing the scientific specification or generator.

## Unavailable checks and allowed uses

No generated rows were sampled, no generator execution or simulated-source replay was performed, and no clinical or target validation is claimed. Actual runtime behavior, three fixed-seed outputs, requested OLS/residual results, all marginal/conditional diagnostics, tail frequencies and measurement ordering need isolated execution. No measured target distribution or analysis result was supplied. Source-to-target differences in geography, ethnicity, adult composition, selection, fasting and CardioChek Plus versus laboratory assay remain unresolved. The model also omits clustering, hidden lifestyle composition, separate measurement error and epistemic parameter uncertainty.

Permitted use is developmental inspection and exercising the three requested descriptive analyses. It does not support causal, clinical, representative-population, measurement-savings or publication-readiness claims. Stop after ordinary pre-submission static checks; no output-informed revision or seed optimization is available or authorized. Token telemetry/cost was not exposed and is not estimated here.
