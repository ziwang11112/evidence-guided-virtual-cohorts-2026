"""Independent invented-data arithmetic only; no experiment data files are read."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import math

import pandas as pd
import evaluator as ev

HERE = Path(__file__).resolve().parent
WATCH = [HERE/'evaluator.py', HERE/'test_evaluator.py', HERE.parent/'controller.py',
         HERE.parent/'PROTOCOL.md', HERE.parent/'private/prelaunch_commitment.json']


def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in WATCH}


def solve_exact(x, y):
    """Exact rational normal equations + Gaussian elimination, not NumPy OLS."""
    width = len(x[0])
    augmented = [[sum(row[j]*row[k] for row in x) for k in range(width)] +
                 [sum(row[j]*target for row, target in zip(x, y))]
                 for j in range(width)]
    for col in range(width):
        pivot = next(i for i in range(col, width) if augmented[i][col])
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        divisor = augmented[col][col]
        augmented[col] = [value/divisor for value in augmented[col]]
        for i in range(width):
            if i != col:
                factor = augmented[i][col]
                augmented[i] = [a-factor*b for a, b in zip(augmented[i], augmented[col])]
    return [row[-1] for row in augmented]


def exact_globals(rows):
    base = [[F(1), q['b'], q['a'], q['m'], q['r']] for q in rows]
    y = [q['y'] for q in rows]
    simple = solve_exact(base, y)
    quadratic = solve_exact([z+[q['b']**2] for z, q in zip(base, rows)], y)
    interaction = solve_exact([z+[q['b']*q['m']] for z, q in zip(base, rows)], y)
    return dict(global_bmi=simple[1], global_age=simple[2],
                global_curvature=quadratic[5], global_interaction=interaction[5])


def linear_quantile(values, probability):
    ordered = sorted(values)
    h = (len(ordered)-1)*probability
    i = int(h)
    if i == len(ordered)-1:
        return ordered[i]
    return ordered[i] + (h-i)*(ordered[i+1]-ordered[i])


before = hashes()
latent, records = [], []
for m, r in product([F(0), F(1)], repeat=2):
    for b, av, e in product(map(F, range(-2, 3)), map(F, range(-2, 3)), [F(-1), F(1)]):
        a = F(4, 5)*av
        y = F(5)+F(7,10)*b+F(3,10)*a+F(1,5)*m-F(1,10)*r+F(11,10)*b*b-F(2,5)*b*m+F(3,20)*e
        stratum, psu = 1 if av <= 0 else 2, 1 if e < 0 else 2
        q = {'b': b, 'a': a, 'm': m, 'r': r, 'y': y, 'cluster': (stratum, psu)}
        latent.append(q)
        records.append({'sample_id': f'explicitly-invented-{len(records):03d}',
                        'race': 'Black' if r else 'White', 'sex': 'male' if m else 'female',
                        'age': float(40+10*a), 'bmi': float(28+5*b), 'urate': float(y),
                        'SDMVSTRA': stratum, 'SDMVPSU': psu})
frame = pd.DataFrame(records)
actual = {q['estimand']: q for q in ev.evaluate_table(frame, reference=True)}
checks = []


def check(name, observed, expected):
    delta = abs(float(observed)-float(expected))
    assert delta <= 1e-10, (name, observed, expected, delta)
    checks.append({'check': name, 'expected': float(expected), 'actual': float(observed), 'absolute_error': delta})


for name, expected in exact_globals(latent).items():
    check('rational_'+name, actual[name]['value'], expected)
for name, expected in {'global_bmi': F(1,2), 'global_age': F(3,10),
                       'global_curvature': F(11,10), 'global_interaction': F(-2,5)}.items():
    check('analytic_'+name, actual[name]['value'], expected)
for m, r in product([F(0), F(1)], repeat=2):
    label = ('Black' if r else 'White')+'_'+('male' if m else 'female')
    subset = [q for q in latent if q['m']==m and q['r']==r]
    coefficient = solve_exact([[F(1), q['y'], 40+10*q['a']] for q in subset],
                              [28+5*q['b'] for q in subset])[1]
    check('rational_reverse_'+label, actual['reverse_'+label]['value'], coefficient)
    k = F(7,10)-F(2,5)*m
    check('analytic_reverse_'+label, actual['reverse_'+label]['value'], 10*k/(2*k*k+F(6821,2000)))
    values = [q['y'] for q in subset]
    mean = sum(values)/len(values)
    sd = math.sqrt(float(sum((v-mean)**2 for v in values)/(len(values)-1)))
    for statistic, value in {'mean': mean, 'sd': sd, 'median': linear_quantile(values,F(1,2)),
                             'q90': linear_quantile(values,F(9,10))}.items():
        check('rational_'+statistic+'_'+label, actual[statistic+'_'+label]['value'], value)

sensitivity = ev.reference_sensitivity(frame)
for summary in sensitivity['summaries']:
    for deletion in summary['deletions']:
        key = (int(deletion['omitted_stratum']), int(deletion['omitted_psu']))
        remaining = [q for q in latent if q['cluster'] != key]
        expected = exact_globals(remaining)[summary['estimand']]
        check('rational_delete_'+str(key)+'_'+summary['estimand'], deletion['value'], expected)
        assert deletion['n_retained'] == len(remaining)

shifted = frame.loc[:, ev.BASE_COLUMNS].copy()
shifted['urate'] += 0.25
comparison = ev.compare_tables(frame, shifted)
for q in comparison:
    expected = 0.25 if q['coefficient'] in ('mean','median','q90') else 0.0
    check('constant_shift_'+q['estimand'], q['difference_generated_minus_measured'], expected)

after = hashes()
assert before == after
report = {'scope': 'Independent rational/analytic checks using invented algebraic data only',
          'real_data_read': False, 'fixture_rows': len(frame), 'numeric_checks': len(checks),
          'max_absolute_error': max(q['absolute_error'] for q in checks),
          'joint_deletion_groups': len(sensitivity['summaries'][0]['deletions']),
          'watched_hashes_before': before, 'watched_hashes_after': after, 'unchanged': True,
          'checks': checks}
(HERE/'independent_calculation_results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({key: report[key] for key in ['real_data_read','fixture_rows','numeric_checks','max_absolute_error','joint_deletion_groups','unchanged']}))
