# HB initial construction

Delivered one developmental generator with a fixed, fully declared scientific law. No participant data, target outcomes, other bundles, project history or external sources were consulted. No seed was sampled or optimized. Exactly the four requested files are submitted; the root stages and executes them.

## Scientific choices

- Use the NHANES adjusted age association (0.010 HbA1c percentage points/year) from PMC2551641 because its diagnosis/FPG selection and adjustment set are closest among the admitted evidence. Its survey weighting, plasma measurement and US population remain different from this Mexican equal-cell design.
- Use the general Finnish population's continuous-BMI coefficients in PMC6458679 Tables S1/S2: glucose 0.0240 mmol/L per BMI unit and HbA1c 0.0125 percentage points per BMI unit. These are weighted age-category/sex-adjusted associations; the latter is not glucose-adjusted. Finnish HbA1c-based and medication/register exclusions are not transferred to the task population.
- Supply the missing glucose-HbA1c conditional association as an assumption, 0.008 percentage points per mg/dL. Define a conditional BMI coefficient by subtraction, 0.0125 - 0.008*0.432 = 0.009044. This is a cross-source modeling assumption, not identification of Q3 or causal mediation. Glucose truncation means the untruncated algebra does not fix the fitted Q2 coefficient or its difference from Q3.
- Use a truncated lognormal BMI distribution, conditional truncated normal glucose and conditional truncated normal HbA1c with age-dependent residual SD. All scientific inputs are in `model_spec.json` and are used by the generator. No standard error is used as individual dispersion. BMI-age and BMI-sex independence, additivity, normal biomarker residuals, chosen supports and the absence of interactions are explicit simplifications.
- Use exact 375-person age/sex cells, with balanced integer ages within bands. This is an analytical design, not a national population sample. The broad HbA1c support permits values above 6.5%; it does not apply the Finnish HbA1c exclusion. Unrepresented diagnosis, fasting record, anthropometry-documentation and pregnancy/lactation routing criteria are assumed cohort membership, never row-level verification. Medication and anemia are not asserted excluded.

Source overlap, estimator distinctions, numerical adoptions, declined numbers, source uncertainty and transfer assumptions are recorded in `SOURCE_USE.json`. In particular, the Kerman printed glucose/HbA1c regression coefficient has an unresolved scale discrepancy with its reported correlation and SDs; it was not silently corrected or adopted. The Taiwan age/sex coefficients have a different adjustment and fasting-selection context and are used only as contextual evidence.

## Guidance and execution boundary

Applied the supplied common [base skill](../../../common/base_skill/SKILL.md), its [interface reference](../../../common/base_skill/references/harness-interface.md), and the unchanged [TASK_RUBRIC.md](../TASK_RUBRIC.md). The rubric requests running all three analyses and all provider diagnostics on delivered rows. The task-specific REQUEST.md expressly reserves generator execution to root and prohibits host sampling, old harness CLIs and old-style freeze. Consequently those execution-dependent requirements are recorded as unresolved, with the exact requested formulas, weights and diagnostic inventory retained for root execution. No source-feedback collector, literature adapter, isolated author execution or independent reviewer was available. There was no revision based on numerical study feedback.

## Actual deterministic algebra

Executed the following inline Python command through PowerShell (`@' ... '@ | python -`). It neither reads nor imports the generator and produces no files or sampled rows:

```python
from math import exp, sqrt, pi
from statistics import NormalDist
nd = NormalDist()
print('source_BMI_glucose_mgdL_per_BMI =', 18.0 * 0.0240)
print('source_male_glucose_mgdL =', 18.0 * 0.2472)
print('assumed_HbA1c_direct_BMI =', 0.0125 - 0.008 * (18.0 * 0.0240))
print('untruncated_Q2_per5 =', 5 * 0.0125)
print('untruncated_Q3_per5 =', 5 * (0.0125 - 0.008 * (18.0 * 0.0240)))
print('Kerman_crude_slope_from_r_SD =', 0.23 * 0.73 / 12.4)
print('BMI_untruncated_SD =', 28.01 * sqrt(exp(0.20**2)-1))
gmin=96+0.16*(25-50)-18*0.2472+18*0.0240*(12-28)
gmax=96+0.16*(79-50)+18*0.0240*(65-28)
print('glucose_location_bounds =',gmin,gmax)
print('minimum_glucose_acceptance_probability =', nd.cdf((126-gmax)/10.5)-nd.cdf((0-gmax)/10.5))
b=0.0125-0.008*18*0.0240
hmin=5.38+0.01*(25-50)-0.04+b*(12-28)+0.008*(0-95)
hmax=5.38+0.01*(79-50)+b*(65-28)+0.008*(126-95)
print('HbA1c_location_bounds =', hmin,hmax)
print('HbA1c_residual_SD_bounds =',0.31+0.001*(25-50),0.31+0.001*(79-50))
print('equal_cell_row_weight =', (1/8)/375)
```

Actual result:

```text
source_BMI_glucose_mgdL_per_BMI = 0.432
source_male_glucose_mgdL = 4.4496
assumed_HbA1c_direct_BMI = 0.009044
untruncated_Q2_per5 = 0.0625
untruncated_Q3_per5 = 0.045219999999999996
Kerman_crude_slope_from_r_SD = 0.013540322580645161
BMI_untruncated_SD = 5.658489646668757
glucose_location_bounds = 80.63839999999999 116.624
minimum_glucose_acceptance_probability = 0.8140586629043822
HbA1c_location_bounds = 4.185296 6.2526280000000005
HbA1c_residual_SD_bounds = 0.285 0.339
equal_cell_row_weight = 0.0003333333333333333
```

Bounds refer to the declared parameter support and normal locations, not observed sample minima/maxima. Positive acceptance throughout the glucose location range supports the rejection algorithm's feasibility, but is not a runtime test. The printed untruncated slopes are algebraic model implications, not cohort estimates, targets or clinical results.

## Actual static and integrity checks

Executed this inline non-executing check:

```python
import ast, hashlib, json
from pathlib import Path
base = Path(r'work\rubric_case_pilot_2026-11-09\bundles\HB')
source = (base/'output/generator.py').read_text(encoding='utf-8')
tree = ast.parse(source)
gen = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'generate')
assert [x.arg for x in gen.args.args] == ['observed', 'specification', 'seed']
assert not gen.args.posonlyargs and not gen.args.kwonlyargs and gen.args.vararg is None and gen.args.kwarg is None
assert all(isinstance(x, (ast.Import, ast.ImportFrom, ast.FunctionDef)) or (isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant) and isinstance(x.value.value, str)) for x in tree.body)
assert {a.name for x in tree.body if isinstance(x, ast.Import) for a in x.names} == {'numpy', 'pandas'}
spec = json.loads((base/'output/model_spec.json').read_text(encoding='utf-8'))
task = json.loads((base/'task.json').read_text(encoding='utf-8'))
assert spec['output_columns'] == [x['name'] for x in task['columns']]
assert spec['design']['rows_per_cell'] * len(spec['design']['female_values']) * len(spec['design']['age_bands_inclusive']) == task['n_rows']
registry = json.loads((base/'registry.json').read_text(encoding='utf-8'))
for artifact in registry['artifacts']:
 assert hashlib.sha256((base/artifact['path']).read_bytes()).hexdigest() == artifact['sha256'], artifact['path']
print('PASS: generator AST syntax, synchronous three-argument signature, imports, import-time definitions-only structure; specification JSON, column order and design arithmetic; 15/15 registered source hashes.')
print('No generator import, function execution, random sampling or cohort analysis occurred.')
```

Actual output was both printed lines, with exit code 0. The checks demonstrate only the stated static/identity scope. Manual code inspection also confirms parameter use, rejection instead of clipping, unique indexed string identifier construction, independent biomarker draws and output column selection; this is not empirical validation of returned rows.

## Tools/actions and limitations

Used `functions.exec` with `exec_command` for allowed PowerShell file reads/listing, Python standard-library XML/text inspection, retained algebra, AST/JSON inspection and SHA256 comparison. Used `apply_patch` to author the four requested files. One XML reading attempt stopped on Windows stdout encoding; it was repeated with explicit UTF-8. A source-directory inventory and optional-input-directory check returned a nonzero shell exit when no input directory was found. No participant input was available or used. Sent a progress message to root; created no subagents. No web/API calls, package installs, generator imports, sample rows, host cohort execution, old harness CLIs or additional output artifacts were used.

All three scientific goal assessments are **unresolved**. Required generated-row schema checks, duplicate-ID versus repeated-profile checks, marginals, quantiles, design rank, conditional support/variance, collinearity, glucose-boundary inspection, the three WLS estimates and their descriptive Q2/Q3 difference await root execution. There are no results for these checks in this submission. No source reconstruction, simulation validation or clinical validation was performed. The target distribution, joint conditional relationship, assay transfer, selection consequences, tails and model uncertainty remain unverified. Further seeds would represent Monte Carlo variability only, not new evidence.

Permitted use is developmental inspection of this law and the requested analytical workflow. No claims of national representativeness, causal effects, Mexican-population accuracy, clinical diagnosis, measurement savings or publication readiness are supported. The submission stops because the specified one-response construction is complete; token telemetry and cost are unavailable and are not fabricated.

Final pre-submission check: an inline standard-library AST/JSON/file-list inspection returned exit code 0 and reported: `PASS: exactly four artifacts; generator syntax; both JSON objects; all three requested analysis IDs/formulas; every rubric assessment field; no unperformed scientific check marked successful.` It compared formulas and IDs with `request.json`, required the nine rubric assessment fields for each goal, and confirmed all three scientific assessments are `unresolved`. This was another static check, with no generator execution. This sentence records that completed check; it does not add a new scientific result.
