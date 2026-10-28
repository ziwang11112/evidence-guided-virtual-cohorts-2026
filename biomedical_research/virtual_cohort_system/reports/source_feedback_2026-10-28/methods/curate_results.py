"""Summarize fixed analyses and copy explicit non-participant review artifacts."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parent
project=root.parents[1]
out=project/'reports/source_feedback_2026-10-28'
out.mkdir(parents=True,exist_ok=False)
case=root/'tg_agent_bundle'
custodian=root/'custodian/nhanes_tg_j_v2'
evaluation=custodian/'evaluation'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj): p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')
expected=read(evaluation/'result_hashes.json')
for name,digest in expected.items(): assert sha(evaluation/name)==digest
comparison=pd.read_csv(evaluation/'endpoint_comparison.csv')
reference=read(evaluation/'reference_analyses.json')
endpoints=list(reference)
rows=[]
for endpoint in endpoints:
    frame=comparison.loc[comparison.endpoint.eq(endpoint)]
    item={'endpoint':endpoint,'reference':reference[endpoint]}
    for stage in ('initial','final'):
        selected=frame.loc[frame.stage.eq(stage)].sort_values('seed')
        assert len(selected)==5
        item[stage]={'median_log_estimate':float(selected.log_estimate.median()),
                     'min_log_estimate':float(selected.log_estimate.min()),
                     'max_log_estimate':float(selected.log_estimate.max()),
                     'median_absolute_log_error':float(selected.absolute_log_error.median()),
                     'direction_counts':{str(k):int(v) for k,v in selected.direction.value_counts().items()}}
    rows.append(item)
source=[]
reports={s:read(case/'source_replays'/f'{s}_feedback/replay.json') for s in ('initial','final')}
for context in reports['initial']['contexts']:
    final_context=next(c for c in reports['final']['contexts'] if c['id']==context['id'])
    for check in context['checks']:
        final=next(c for c in final_context['checks'] if c['id']==check['id'])
        op=check['operator']
        columns={op.get(k) for k in ('column','x','y','outcome')}
        columns.update(op.get('predictors',[]))
        columns.update(s['column'] for s in op['selection'])
        if 'event' in op: columns.add(op['event']['column'])
        source.append({'context':context['id'],'id':check['id'],'unit':check['unit'],
            'reported':check['reported_value'],'initial':check['value'],'final':final['value'],
            'initial_difference':check['difference'],'final_difference':final['difference'],
            'outcome_involving':'tg_mg_dl' in columns,'status':check['status'],
            'generation_link_verified':check['generation_link_verified'] and final['generation_link_verified']})
source_frame=pd.DataFrame(source)
source_frame.to_csv(out/'source_diagnostic_comparison.csv',index=False)
affected=source_frame.loc[source_frame.outcome_involving]
delta=affected.final_difference.abs()-affected.initial_difference.abs()
counts={'improved':int((delta < -1e-12).sum()),'worsened':int((delta > 1e-12).sum()),
        'unchanged':int((delta.abs()<=1e-12).sum()),'outcome_involving_checks':len(affected),
        'covariate_only_checks':int((~source_frame.outcome_involving).sum()),
        'interpretation':'Descriptive diagnostic counts across mixed units, not an aggregate scientific success score'}
controlled=root/'controlled'
c_initial=read(controlled/'controller_runs/initial_target_summary.json')
c_final=read(controlled/'controller_runs/final_target_summary.json')
same=all(a['seed']==b['seed'] and a['sha256']==b['sha256'] for a,b in zip(c_initial['outputs'],c_final['outputs'],strict=True))
summary={'scope':'One procedural-holdout public-data exploratory pilot, not method superiority',
    'date':'2026-10-28','n_participants':2072,'agent_constructions_public_case':1,
    'stages':['initial','final'],'seeds_per_stage':5,'endpoints':rows,'source_diagnostic_counts':counts,
    'controlled_fixture':{'decision':'retain','initial_final_same_seed_outputs_identical':same,
                          'target_rows':128,'seeds_per_stage':3},
    'evaluation_commitment_sha256':sha(root/'evaluation_commitment.json'),
    'reference_file_sha256':sha(evaluation/'reference_analyses.json'),
    'data_source':'NHANES 2017-2018 fasting reference-method serum TG; WTSAF2YR, SDMVSTRA, SDMVPSU',
    'feedback_sources':['Oh et al. 2019, Healthy Twin Study, Korea','Bansal et al. 2007, Women\u2019s Health Study'],
    'limitations':['Builder boundary is procedural, not OS-isolated.',
        'Initial/final comparison has no matched extra-compute no-feedback control.',
        'Five draws are residual simulations of one Agent construction, not independent clinical replication.',
        'Generated sampling intervals omit source, model and transport uncertainty.',
        'Unadjusted reserved endpoint intervals are exploratory; no equivalence or clinical-replacement claim.',
        'Curated source retrieval is not an autonomous evidence-gap search test.']}
write(out/'aggregate_results.json',summary)
for name in ('endpoint_comparison.csv','initial_final_changes.csv','reference_analyses.json','report_notes.json'):
    shutil.copyfile(evaluation/name,out/name)
for label,bundle in [('controlled',controlled),('tg',case)]:
    for stage in ('initial','final'):
        dest=out/'candidates'/f'{label}_{stage}'
        dest.mkdir(parents=True)
        for name in ('generator.py','model_spec.json','evidence.json','decision.md','source_replay.json','revision.json'):
            src=bundle/'candidates'/stage/name
            if src.exists(): shutil.copyfile(src,dest/name)
methods=out/'methods'
methods.mkdir()
for name in ('analysis_protocol.json','survey_analysis.py','prepare_case.py','evaluate_committed.py',
             'evaluate_committed_v2.py','test_evaluator_receipt_guard.py','reader_amendment.json','guard_validation.json'):
    shutil.copyfile(custodian/name,methods/name)
for name in ('run_committed_stage.py','commit_real_evaluation.py','prepare_real_bundle.py','curate_results.py'):
    shutil.copyfile(root/name,methods/name)
shutil.copyfile(case/'controller_runs/source_audit.json',out/'source_audit.json')
names={'adjusted_bmi_per5':'BMI +5 kg/m² (primary)', 'adjusted_age_per10':'Age +10 years',
       'adjusted_female_vs_male':'Female versus male',
       'bmi_curvature_second_difference':'BMI curvature contrast',
       'bmi_sex_interaction':'Female-minus-male BMI slope'}
fig,ax=plt.subplots(figsize=(10.2,5.5),layout='constrained')
for i,row in enumerate(rows):
    ref=row['reference']; x=ref['log_estimate']
    ax.errorbar(x,i-.19,xerr=[[x-ref['log_ci_low']],[ref['log_ci_high']-x]],fmt='o',
                color='#243447',capsize=3,label='Real data: 95% survey CI' if i==0 else None)
    for stage,dy,color in [('initial',0,'#3b82b1'),('final',.19,'#d47732')]:
        s=row[stage]; x=s['median_log_estimate']
        ax.errorbar(x,i+dy,xerr=[[x-s['min_log_estimate']],[s['max_log_estimate']-x]],fmt='s',
            color=color,capsize=3,label=f'{stage.title()}: median and range of 5 draws' if i==0 else None)
ax.axvline(0,color='#8c939c',linestyle='--',linewidth=.8)
ax.set_yticks(range(len(rows)),[names.get(r['endpoint'],r['endpoint']) for r in rows])
ax.invert_yaxis(); ax.set_xlabel('Log-scale association / contrast (same frozen analysis for all tables)')
ax.set_title('Held-out TG analyses after source-only Agent feedback',loc='left',fontweight='bold')
ax.grid(axis='x',alpha=.2)
ax.legend(loc='best',fontsize=8)
fig.suptitle('2,072 adults; one Agent construction. Simulated ranges are not confidence intervals.',
             fontsize=10,y=1.04)
fig.savefig(out/'heldout_associations.png',dpi=180,bbox_inches='tight')
fig.savefig(out/'heldout_associations.pdf',bbox_inches='tight')
plt.close(fig)
write(out/'curated_file_hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
print(json.dumps({'report_directory':str(out),'source_counts':counts,'endpoints':rows},indent=2))
