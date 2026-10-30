"""Post hoc descriptive audit; read frozen fictional rows, never generate/repair them."""
from pathlib import Path
import csv
from collections import Counter
from decimal import Decimal
import hashlib
import json
import math
import statistics
import numpy as np

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
INITIAL = RUN / 'visible/bundle/candidates/initial/generated.csv'
FINAL = RUN / 'visible/bundle/candidates/final/generated.csv'
EXPECTED = '3e95264632fc2e9fd4e022147724b028c06c105eea753bee30eff4e435c915fb'
MEANS = {('White', 'male'): '6.1', ('White', 'female'): '4.5',
         ('Black', 'male'): '6.2', ('Black', 'female'): '4.6'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ranks(values):
    result = [0.0] * len(values)
    ordered = sorted(range(len(values)), key=lambda i: values[i])
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and values[ordered[j]] == values[ordered[i]]:
            j += 1
        value = ((i + 1) + j) / 2
        for k in range(i, j):
            result[ordered[k]] = value
        i = j
    return result


def correlation(x, y):
    return float(np.corrcoef(x, y)[0, 1])


before = {'initial': sha(INITIAL), 'final': sha(FINAL)}
assert before['initial'] == before['final'] == EXPECTED
with INITIAL.open(newline='', encoding='utf-8-sig') as stream:
    rows = list(csv.DictReader(stream))
groups = []
for group, mean in MEANS.items():
    selected = [r for r in rows if (r['race'], r['sex']) == group]
    vals = {k: [float(r[k]) for r in selected] for k in ['age', 'bmi', 'urate']}
    urate_counts = Counter(Decimal(r['urate']) for r in selected)
    center = Decimal(mean)
    mirror_matched = sum(min(count, urate_counts[2 * center - value])
                         for value, count in urate_counts.items())
    joint_counts = Counter((r['age'], r['bmi'], r['urate']) for r in selected)
    groups.append({
        'race': group[0], 'sex': group[1], 'n': len(selected),
        'marginals': {k: {'mean': statistics.mean(v), 'sd_ddof1': statistics.stdev(v),
                           'min': min(v), 'max': max(v), 'distinct': len(set(v))}
                      for k, v in vals.items()},
        'pearson_bmi_urate': correlation(vals['bmi'], vals['urate']),
        'spearman_bmi_urate': correlation(ranks(vals['bmi']), ranks(vals['urate'])),
        'pearson_age_urate': correlation(vals['age'], vals['urate']),
        'spearman_age_urate': correlation(ranks(vals['age']), ranks(vals['urate'])),
        'urate_exact_mirror_multiset_about_supplied_mean': all(
            urate_counts[value] == urate_counts[2 * center - value] for value in urate_counts),
        'urate_mirror_matched_observations': mirror_matched,
        'urate_mirror_matched_fraction': mirror_matched / len(selected),
        'urate_observations_exactly_at_supplied_mean': urate_counts[center],
        'duplicate_joint_rows_beyond_first': sum(n - 1 for n in joint_counts.values()),
        'largest_repeated_joint_tuple_count': max(joint_counts.values())
    })

X = np.array([[1, float(r['age']), float(r['bmi']), int(r['sex'] == 'male'),
               int(r['race'] == 'Black')] for r in rows], dtype=float)
y = np.array([float(r['urate']) for r in rows])
beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
rss = float(np.sum((y - X @ beta) ** 2))
tss = float(np.sum((y - np.mean(y)) ** 2))
full_joint = Counter(tuple(r[k] for k in ['race', 'sex', 'age', 'bmi', 'urate']) for r in rows)
after = {'initial': sha(INITIAL), 'final': sha(FINAL)}
assert before == after
result = {
    'scope': 'POST HOC descriptive audit of one already frozen fictional table; no new validation endpoint or generator run',
    'scientific_reference_for_correlations': None,
    'interpretation': 'Age/BMI means and SDs and urate means have screened evidence, but within-group correlations, urate dispersion, tail/range choices and individual pairings are author assumptions. Correlation magnitude is not scientific accuracy.',
    'rows': len(rows), 'distinct_sample_ids': len({r['sample_id'] for r in rows}),
    'hashes_before': before, 'hashes_after': after, 'expected_hash_matches': True,
    'initial_final_equal': True,
    'groups': groups,
    'duplicate_full_joint_rows_beyond_first': sum(n - 1 for n in full_joint.values()),
    'ols_independent_recomputation': {
        'formula': 'urate ~ 1 + age + bmi + male + Black', 'n': len(rows), 'rank': int(rank),
        'coefficients': dict(zip(['intercept', 'age', 'bmi', 'male', 'Black'], map(float, beta))),
        'rss': rss, 'descriptive_r_squared': 1 - rss / tss,
        'condition_number': float(np.linalg.cond(X)),
        'warning': 'Not prediction accuracy or causal/clinical validation. Raw BMI slope is not comparable to a differently adjusted standardized effect from the original paper.'
    }
}
(HERE / 'numeric_audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
