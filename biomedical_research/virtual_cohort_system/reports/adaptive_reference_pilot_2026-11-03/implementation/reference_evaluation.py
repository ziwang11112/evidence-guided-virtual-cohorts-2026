"""Aggregate-only development evaluation of verified synthetic output."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def evaluate(bundle, candidate, run_id, profile):
    from cohort_harness.execution import verify_execution
    from cohort_harness.lifecycle import read_table
    bundle=Path(bundle); config=load(profile)
    receipt=verify_execution(bundle,run_id)
    assert receipt['status']=='success'
    assert receipt['candidate']=='candidates/'+str(candidate).removeprefix('candidates/')
    out=bundle/'executions'/run_id/'output/generated.csv'
    frame=read_table(out,load(bundle/'task.json'),output=True)
    ref=load(config['reference_summary']); definitions=load(config['analysis_definitions'])
    ids=config['required_diagnostic_ids']; diags=[]
    for var,targets in ref['diagnostics']['marginal'].items():
        x=frame[var].to_numpy(dtype=float)
        values={'mean':float(np.mean(x)),'sd':float(np.std(x,ddof=1)),
                'q10':float(np.quantile(x,.1,method='linear')),'median':float(np.quantile(x,.5,method='linear')),
                'q90':float(np.quantile(x,.9,method='linear'))}
        for key,target in targets.items():
            diags.append({'id':var+'_'+key,'value':values[key],'reference':target,'difference':values[key]-target})
    for key,target in ref['diagnostics']['joint'].items():
        a=frame[['glucose','hba1c']]
        if key=='spearman':a=a.rank(method='average')
        val=float(np.corrcoef(a.to_numpy(dtype=float),rowvar=False)[0,1])
        if not np.isfinite(val): val=None
        diags.append({'id':'glucose_hba1c_'+key,'value':val,'reference':target,'difference':val-target if val is not None else None})
    nonpositive={v:int((frame[v]<=0).sum()) for v in ('glucose','hba1c')}
    analyses=[]
    for d in definitions['analyses']:
        x=np.column_stack([np.ones(len(frame)),frame[d['predictors']].to_numpy(dtype=float)])
        rank=int(np.linalg.matrix_rank(x)); val=None
        if rank==x.shape[1] and not any(nonpositive.values()):
            beta=np.linalg.lstsq(x,frame[d['outcome']].to_numpy(dtype=float),rcond=None)[0]
            val=float(beta[d['predictors'].index(d['term'])+1])
        r=ref['estimands'][d['id']]
        analyses.append({'id':d['id'],'value':val,'reference':r['coefficient'],'difference':val-r['coefficient'] if val is not None else None,
            'unit':d['unit'],'reference_interval':r['interval'],'rank':rank,'n':len(frame),
            'status':'computed' if val is not None else 'unavailable','interpretation':'Exposed-reference consistency; interval membership is not equivalence.'})
    assert {d['id'] for d in diags}==set(ids)
    assert {a['id'] for a in analyses}==set(config['required_analysis_ids'])
    return {'kind':'development_reference_analysis','analyses':analyses,'diagnostics':diags,'n':len(frame),
        'quality':{'nonpositive_glycemia':nonpositive,'duplicate_measurement_rows':int(frame.drop(columns=['row_id']).duplicated().sum())},
        'output_sha256':sha(out),'reference_sha256':sha(config['reference_summary']),
        'limitations':['All reference quantities are available to author; no independent validation.',
                       'Conditional Monte Carlo variation is not evidence, model or transport uncertainty.',
                       'No global pass score or post-hoc equivalence margin.']}
