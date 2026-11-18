"""Audit new manuscript tables/figure values against saved reviewed aggregates.

No patient rows, generator execution, fitting, model calls or new scientific
estimates. This is root-led editorial verification, not a new independent review.
"""
from pathlib import Path
import csv, hashlib, json, re, statistics

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
M = P / 'manuscript/DRAFT_v0_31.md'
text = M.read_text(encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L = P / 'work/lifestyle_application_2026-11-11'
source = json.loads((L / 'ANALYSIS_RESULTS.json').read_text())['results']
by_id = {x['dataset_id']: x for x in source}
checks = []

def check(label, condition):
    checks.append(label)
    assert condition, label

def rows(number):
    section = text.split('**Table S' + str(number) + '.', 1)[1]
    block = re.search(r'(?m)^\|.*(?:\n\|.*)+', section)[0]
    return [[c.strip() for c in line.strip('|').split('|')]
            for line in block.splitlines()[2:]]

def rounded_cell(label, cell, vals, places=3):
    tokens = re.findall(r'-?\d+(?:\.\d+)?', cell)
    expected = [f'{float(x):.{places}f}' for x in vals]
    check(label, tokens == expected)

traits = {'BMI':'bmi', 'TC':'total_cholesterol', 'HDL':'hdl_cholesterol'}
contrasts = {'Rural - pastoralist':'rural_minus_pastoralist',
             'Urban - pastoralist':'urban_minus_pastoralist', 'Urban - rural':'urban_minus_rural'}

def result(dataset, trait, contrast):
    return next(x for x in dataset['analysis']['contrasts']
                if (x['trait'], x['contrast'], x['stratum']) == (trait, contrast, 'pooled'))

for table, prefix in [(22, ''), (23, 'raw_')]:
    rr = rows(table)
    check(f'S{table} all nine contrasts', len(rr) == 9)
    seen = set()
    for row in rr:
        t, c = row[0].split(' / ')
        t, c = traits[t], contrasts[c]
        seen.add((t,c))
        ref = result(by_id['real'], t, c)
        rounded_cell(f'S{table} {t} {c} reference', row[1], [ref[prefix+k] for k in ['estimate','lower','upper']])
        for idx, ep in enumerate(['LIFESTYLE_A1', 'LIFESTYLE_A2'], 2):
            vals = [result(d,t,c)[prefix+'estimate'] for d in source if d.get('episode_id') == ep]
            check(f'{table} {t} {c} {ep} three draws', len(vals)==3)
            rounded_cell(f'S{table} {t} {c} {ep}', row[idx], [statistics.mean(vals), min(vals), max(vals)])
    check(f'S{table} unique coverage', len(seen)==9)

diagnostics = rows(24)
check('S24 all 21 diagnostics', len(diagnostics)==21)
for row in diagnostics:
    did = 'real' if row[0]=='Reference' else 'LIFESTYLE_'+row[0]
    d = by_id[did]['analysis']; t = traits[row[1]]
    info = next(x for x in d['trait_status'] if x['trait']==t)
    lr = next(x for x in d['interactions'] if x['trait']==t)
    check(f'S24 {did}/{t} sample', row[2]==str(info['n']))
    rounded_cell(f'S24 {did}/{t} SD',row[3],[info['sample_sd']])
    rounded_cell(f'S24 {did}/{t} LRT',row[4],[lr['p_value']],5)
    check(f'S24 {did}/{t} branch',row[5]==('Sex-specific' if lr['selects_sex_specific'] else 'Additive'))

Q = P/'work/published_analysis_replay_2026-11-11/PAIR_RESULTS.csv'
with Q.open(newline='',encoding='utf-8') as f: pair_rows=list(csv.DictReader(f))
rr=rows(25)
check('S25 reference plus eight laws',len(rr)==9)
pairs=['bmi__total_cholesterol','bmi__hdl_cholesterol','total_cholesterol__hdl_cholesterol']
for row in rr:
    ep=row[0].split(' / ')[0]
    for j,pair in enumerate(pairs,1):
        selected=[x for x in pair_rows if x['episode']==ep and x['pair']==pair]
        vals=[float(x['r']) for x in selected]
        check(f'S25 {ep}/{pair} samples',len(vals)==(1 if ep=='REAL' else 3))
        if ep=='REAL': expected=[statistics.mean(vals)]
        else: expected=[statistics.mean(vals),min(vals),max(vals)]
        if ep=='LIPID_WORKFLOW_R2' and j==2:
            tokens=re.findall(r'-?\d+(?:\.\d+)?',row[j])
            check('near-zero mean not rounded to negative zero',tokens==[f'{expected[0]:.4f}',f'{expected[1]:.3f}',f'{expected[2]:.3f}'])
        else: rounded_cell(f'S25 {ep}/{pair}',row[j],expected)

fig = json.loads((HERE/'FIGURE_DATA.json').read_text())
check('figure source hash',fig['aggregate_input_sha256']==sha(L/'ANALYSIS_RESULTS.json'))
check('126 plotted records',len(fig['plotted_records'])==126)
seen=set()
for r in fig['plotted_records']:
    prefix='raw_' if r['figure']=='fig3-lifestyle-raw' else ''
    base=result(by_id[r['dataset']],r['trait'],r['contrast'])
    key=(r['figure'],r['trait'],r['contrast'],r['dataset'])
    check('plot estimate '+str(key),r['x']==base[prefix+'estimate'])
    for k in ['lower','upper']:
        if k in r:check('plot interval '+str(key)+k,r[k]==base[prefix+k])
    seen.add(key)
check('unique plotted coverage',len(seen)==126)
for name,value in fig['files'].items():
    check('figure file binding '+name,sha(P/'manuscript/paper_figures_v31_2026-11-11'/name)==value)

facts=json.loads((HERE/'REVISION_FACTS.json').read_text())
for rel,value in facts['preserved_inputs'].items():
    check('preserved '+rel,sha(P/rel)==value)

check('all lifestyle analysis rows retained',sum(len(d['analysis']['contrasts']) for d in source)==189)
check('all interaction rows retained',sum(len(d['analysis']['interactions']) for d in source)==21)
check('reuse includes all saved analyses',len(pair_rows)==75)
for phrase in ['source-rich','request-only','previously exposed','A1/seed64001','No generator was changed or executed',
               '1.882','1.700-2.251','31.85-34.06','14.40-15.10','not confidence intervals']:
    check('scope/number '+phrase,phrase in text)
for kind,expected in [('Figure',[str(x) for x in range(1,12)]+['S'+str(x) for x in range(1,9)]),
                      ('Table',[str(x) for x in range(1,8)]+['S'+str(x) for x in range(1,26)])]:
    found=re.findall(r'^\*\*'+kind+r' (S?\d+)\.',text,re.M)
    check(kind+' caption sequence',found==expected)

report={'status':'PASS_ROOT_EDITORIAL_AUDIT','review_scope':'New tables, saved plot data, complete-case/branch reporting and input integrity; not a new independent scientific review',
        'checks':len(checks),'check_names':checks,'source_markdown_sha256':sha(M),
        'old_files_unchanged':len(facts['preserved_inputs']),'patient_rows_read':False,
        'new_scientific_estimates':False,'new_model_calls':0}
(HERE/'CONTENT_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','checks','old_files_unchanged']}))
