"""Analysis-use audit of closed aggregates; no row reads or new generator runs.

Observed discrepancies are not acceptance margins. This script does not classify
any clinically acceptable bound or conduct an equivalence test.
"""
from pathlib import Path
import hashlib,json,math,csv
from datetime import datetime,timezone
from collections import defaultdict
import numpy as np

W=Path(__file__).resolve().parent
P=W.parents[1]
INPUTS=[
 'manuscript/DRAFT_v0_32.md',
 'work/lifestyle_application_2026-11-11/ANALYSIS_CONTRASTS.csv',
 'work/lifestyle_application_2026-11-11/PROTOCOL.md',
 'work/lifestyle_application_2026-11-11/analysis_operator.py',
 'work/lifestyle_application_2026-11-11/reference_adapter.py',
 'work/pns_joint_evidence_2026-11-16/analysis/seed_results.json',
 'work/pns_joint_evidence_2026-11-16/analysis/REFERENCE_USED.json',
 'work/scientific_use_review_v30_2026-11-11/NUMERICAL_USE_AUDIT.json',
 'work/analysis_use_diagnosis_2026-11-08/RECONSTRUCTION_PROSPECTIVE_AUDIT.json',
 'work/analysis_use_diagnosis_2026-11-08/IRON_LIPID_AUDIT.json',
 'work/evidence_composition_pilot_2026-11-16/analysis/SUMMARY.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bound={r:sha(P/r) for r in INPUTS}
binding=W/'INPUT_BINDINGS.json'
if binding.exists():assert json.loads(binding.read_text())['files']==bound
else:binding.write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'files':bound},indent=2))
def read(rel):return json.loads((P/rel).read_text(encoding='utf8'))
records=[]
def add(study,arm,analysis,role,author,seed,value,reference,unit,interval='',regime=''):
    records.append(dict(study=study,arm=arm,analysis=analysis,role=role,author=author,
                        seed=int(seed),value=float(value),reference=float(reference),unit=unit,
                        reference_interval_kind=interval,information_regime=regime))

with (P/INPUTS[1]).open(encoding='utf8',newline='') as f:l=list(csv.DictReader(f))
l=[r for r in l if r['stratum']=='pooled']
lrefs={(r['trait'],r['contrast']):r for r in l if r['dataset_id']=='real'}
for r in l:
    if r['dataset_id']=='real':continue
    z=lrefs[r['trait'],r['contrast']]
    parts=r['dataset_id'].split('_')
    add('Lifestyle','source-rich',r['trait']+':'+r['contrast'],'primary',parts[1],parts[-1].lstrip('s'),r['raw_estimate'],z['raw_estimate'],r['raw_unit'],
        'conventional model-based 95% interval; not an acceptance region','same-source reconstruction')

p=read(INPUTS[5]);pr=read(INPUTS[6])['PNS']
for r in p:
    if r['estimand']=='sbp_below_dbp_fraction':continue
    a=r['estimand'];rr=pr[a]
    add('PNS',r['arm'],a,'primary' if '.' not in a else 'dispersion diagnostic',r['id'],r['seed'],r['value'],rr['value'],rr['unit'],
        rr['uncertainty'].get('kind','unavailable'),'external-evidence developmental comparison')

e=read(INPUTS[7]);es=[r for r in e['summary_records'] if r['study']=='Q4 ENSANUT']
for r in es:
    for seed,v in zip(r['seeds'],r['values']):
        eu=('HbA1c % (NGSP)' if r['analysis_id']=='hba1c.mean'
            else r['unit'].replace('%','HbA1c percentage points'))
        add('ENSANUT','external-evidence',r['analysis_id'],r['role'],r['author'],seed,v,r['reference']['value'],eu,
            r['reference'].get('interval',{}).get('meaning','unavailable'),'external-evidence developmental comparison')

# Iron: retain both laws and all three predefined scientific quantities.
iron=read(INPUTS[9])
for r in iron['analyses'][:3]:
    obs=r['observed_result'];ref=obs['reference']['estimate']
    unit={'IRON_OR':'odds ratio','IRON_BURDEN':'proportion','IRON_RANK':'Spearman correlation'}[r['id']]
    for author,item in obs['authors'].items():
        for draw,v in enumerate(item['seed_values'],1):
            add('Iron','external-evidence',r['id'],'primary',author,draw,v,ref,unit,'recorded survey reference; no margin','external-evidence comparison; seed index only')

grouped=defaultdict(list)
for r in records:grouped[r['study'],r['arm'],r['analysis']].append(r)
summary=[]
for key,rows in grouped.items():
    authors=defaultdict(list)
    for r in rows:authors[r['author']].append(r['value'])
    values=np.array([r['value'] for r in rows]);ref=rows[0]['reference']
    assert all(r['reference']==ref for r in rows)
    assert all(len(v)==3 for v in authors.values())
    means=np.array([sum(v)/len(v) for v in authors.values()]);errors=np.abs(values-ref)
    s={k:rows[0][k] for k in ['study','arm','analysis','role','unit','reference_interval_kind','information_regime']}
    s.update(n_constructors=len(authors),n_draws=len(values),reference=ref,constructor_mean_min=float(min(means)),constructor_mean_max=float(max(means)),
             draw_min=float(min(values)),draw_max=float(max(values)),mean_absolute_point_difference=float(np.mean(errors)),
             max_absolute_point_difference=float(max(errors)),max_constructor_mean_point_difference=float(max(abs(means-ref))),
             quantitative_acceptance='not_assessed_no_use_justified_margin',generalization='not_established')
    directional=((s['role']=='primary' and s['analysis']!='IRON_BURDEN')
                 or s['analysis']=='Q2_minus_Q3_bmi5')
    null=1.0 if s['unit']=='odds ratio' else 0.0
    s['association_null']=null if directional else None
    s['n_draws_same_side_of_association_null']=int(sum(np.sign(values-null)==np.sign(ref-null))) if directional else None
    if s['unit']=='odds ratio':
        s.update(max_absolute_log_ratio=float(max(abs(np.log(values/ref)))),mean_log_ratio=float(np.mean(np.log(values/ref))))
    summary.append(s)

def write_csv(path,rows):
    names=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(rows)
write_csv(W/'ESTIMATE_LEDGER.csv',records);write_csv(W/'ANALYSIS_USE_PROFILE.csv',summary)

# Algebraic direction-pattern checks on the same saved tables; no generated p-value
# or interval is treated as a clinical correctness label.
bmi=[r for r in records if r['study']=='Lifestyle' and r['analysis'].startswith('bmi:')]
bytable=defaultdict(dict)
for r in bmi:bytable[r['author'],r['seed']][r['analysis']]=r['value']
urban=sum(d['bmi:urban_minus_pastoralist']>0 and d['bmi:urban_minus_rural']>0 for d in bytable.values())
e_bytable=defaultdict(dict)
for r in records:
    if r['study']=='ENSANUT':e_bytable[r['author'],r['seed']][r['analysis']]=r['value']
attenuation_checks=[]
for k,d in e_bytable.items():
    assert abs((d['Q2_bmi5']-d['Q3_bmi5'])-d['Q2_minus_Q3_bmi5'])<1e-12
    attenuation_checks.append(d['Q2_bmi5']>d['Q3_bmi5']>0)
pattern={'lifestyle_urban_above_both_groups':{'tables':len(bytable),'matching_tables':int(urban),'constructors':2,'interpretation':'source-rich qualitative reconstruction; not causality or equivalence'},
         'ensanut_positive_bmi_attenuation_after_glucose':{'tables':len(e_bytable),'matching_tables':int(sum(attenuation_checks)),'constructors':2,'interpretation':'specified conditional association pattern; not mediation'},
         'acceptance_margin_selected':False,'equivalence_tests_performed':0}
(W/'PATTERNS.json').write_text(json.dumps(pattern,indent=2),encoding='utf8')

lines=['# Observed scientific-use profiles','','Closed aggregate estimates only. No acceptance margin is selected from these results. The largest absolute discrepancy is a descriptive distance from this particular sample reference, not a minimum clinically acceptable threshold. The means and ranges below retain all constructors and all three draws.','','| Case / analysis | Reference | Author-mean range | Draw range | Largest absolute point difference |','|---|---:|---:|---:|---:|']
for r in summary:
    lines.append(f"| {r['study']} / {r['arm']} / {r['analysis']} ({r['unit']}) | {r['reference']:.5g} | {r['constructor_mean_min']:.5g}–{r['constructor_mean_max']:.5g} | {r['draw_min']:.5g}–{r['draw_max']:.5g} | {r['max_absolute_point_difference']:.5g} |")
lines+=['','This is a focused audit of the current clinical figures, the existing ENSANUT pattern and all three iron analyses. It is not a new evaluation of every project version. HRS and artificial composition are interpreted separately in SCIENTIFIC_USE_AND_MARGINS.md; fitted source coefficients and mathematical population values are not pooled with measured-reference errors.','', 'The reported signs alone do not prove a useful effect size. Relative error is not used for weak near-zero relations. The iron odds-ratio ledger also reports discrepancies on the log-ratio scale. No source, generator or old evaluation file is edited.']
(W/'OBSERVED_PROFILES.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
check={'status':'passed','aggregate_rows':len(records),'analysis_condition_profiles':len(summary),'all_three_draws_retained':True,'pattern_algebra_checked':True,
       'all_input_hashes_unchanged':all(sha(P/r)==h for r,h in bound.items()),'patient_rows_read':False,'new_generators':0,'new_api_calls':0,'new_patient_fits':0,'selected_equivalence_margins':0,
       'note':'Reconciled closed numerical results only; descriptive use judgments will be stated separately.'}
(W/'COMPUTATION_CHECKS.json').write_text(json.dumps(check,indent=2),encoding='utf8')
print(json.dumps(check))
for r in summary:
    if r['analysis'] in ['bmi:urban_minus_pastoralist','total_cholesterol:rural_minus_pastoralist','hdl_cholesterol:rural_minus_pastoralist','residual_correlation','bmi_sbp','bmi_dbp','Q1_age10','Q2_minus_Q3_bmi5','IRON_OR']:
        print(json.dumps(r))
