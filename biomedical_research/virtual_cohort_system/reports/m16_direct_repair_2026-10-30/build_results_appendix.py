"""Reformat released aggregate records; no individual data or new estimators."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
r=json.loads((R/'results/evaluation.json').read_text())
c={(x['builder'],x['stage']):{e['estimand']:e['generated']['value'] for e in x['estimands']}
   for x in r['candidate_comparisons']}
lines=['# All 24 locked analyses', '',
       'Aggregate point estimates only. B1 and B3 initial/final tables are identical; their repeated stages are collapsed here without selecting a favorable result. The complete six-stage ledger is in `estimands.csv`. B2 final equals revision1.', '',
       '| Analysis | Units | Measured | B1 initial/final | B2 initial | B2 final | B3 initial/final |',
       '|---|---|---:|---:|---:|---:|---:|']
for e in r['reference_estimands']:
    values=[e['value']]+[c[key][e['estimand']] for key in [('b1','final'),('b2','initial'),('b2','final'),('b3','final')]]
    cells=['NA' if v is None else f'{v:.6f}' for v in values]
    lines.append('| '+e['estimand']+' | '+e['units']+' | '+' | '.join(cells)+' |')
lines+=['','These are unweighted descriptions of the same 200-person quota cohort, not national estimates, tests of equivalence, clinical measurements for synthetic rows, or causal effects. No failed analysis is silently omitted.']
with (R/'results/analysis_tables.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
print('Wrote all 24 aggregate analysis records.')
