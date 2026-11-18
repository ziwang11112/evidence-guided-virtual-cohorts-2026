"""One new invented-fixture LR check; does not rerun the six operator tests."""
from pathlib import Path
import hashlib
import importlib.util
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lifestyle_operator_review', ROOT / 'analysis_operator.py')
op = importlib.util.module_from_spec(spec)
spec.loader.exec_module(op)
rng = np.random.default_rng(811765)
n = 240
groups = np.tile(op.GROUPS, n // 3)
female = np.tile([False, True], n // 2)
age = rng.uniform(20, 80, n)
rural = (groups == op.GROUPS[1]).astype(float)
urban = (groups == op.GROUPS[2]).astype(float)
f = pd.DataFrame(dict(id=[f'invented_{i}' for i in range(n)], age=age,
                     sex=np.where(female, 'F', 'M'), lifestyle=groups,
                     bmi=30 + .03 * age + rural + 3 * urban + 2 * urban * female + rng.normal(size=n),
                     total_cholesterol=150 + .1 * age + 5 * urban + rng.normal(0, 10, n),
                     hdl_cholesterol=60 - 2 * rural + 3 * rural * female + rng.normal(0, 4, n)))
observed = op.analyze_frame(f)
x = np.column_stack([np.ones(n), rural, urban, age, female.astype(float)])
full_x = np.column_stack([x, rural * female, urban * female])
checks = []
for trait in op.TRAITS:
    z = (f[trait] - f[trait].mean()) / f[trait].std(ddof=1)
    reduced = sm.OLS(z, x).fit()
    full = sm.OLS(z, full_x).fit()
    lr, p, df = full.compare_lr_test(reduced)
    actual = next(a for a in observed['interactions'] if a['trait'] == trait)
    okay = actual['status'] == 'computed' and abs(lr - actual['lr']) <= 1e-10 \
        and abs(p - actual['p_value']) <= 1e-12 and df == actual['df'] == 2 \
        and (p < .05) == actual['selects_sex_specific']
    checks.append(dict(trait=trait, pass_check=bool(okay), independent_lr=float(lr),
                       operator_lr=actual['lr'], independent_p=float(p), operator_p=actual['p_value'],
                       independent_df=int(df), selected_branch_matches=bool((p < .05) == actual['selects_sex_specific'])))
report = dict(status='pass' if all(x['pass_check'] for x in checks) else 'failed',
              fixture='One new 240-row invented three-outcome fixture, seed 811765',
              independent_method='statsmodels OLS fit likelihoods and compare_lr_test; production uses n*log(RSS0/RSS1)',
              checks=checks, earlier_operator_tests_rerun=False, target_rows_read=0,
              api_calls=0, generator_runs=0,
              hashes={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                      for name in ['analysis_operator.py', 'review/check_lr.py']})
with (ROOT / 'review/LR_CHECK.json').open('x', encoding='utf-8') as stream:
    json.dump(report, stream, indent=2, allow_nan=False)
    stream.write('\n')
print(json.dumps({'status': report['status'], 'new_fixture_count': 1, 'trait_checks': len(checks),
                  'max_lr_absolute_difference': max(abs(x['independent_lr'] - x['operator_lr']) for x in checks)}))
if report['status'] != 'pass':
    raise SystemExit(1)
