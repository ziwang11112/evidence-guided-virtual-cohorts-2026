"""Same generated statistics for both conditions; L never loads a reference."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd

def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def generated_statistics(frame,definitions):
    diagnostics=[]
    for name in definitions['diagnostics']['marginal_variables']:
        x=frame[name].to_numpy(dtype=float)
        values={'mean':float(np.mean(x)),'sd':float(np.std(x,ddof=1)),
                'q10':float(np.quantile(x,.1,method='linear')),'median':float(np.quantile(x,.5,method='linear')),
                'q90':float(np.quantile(x,.9,method='linear'))}
        diagnostics.extend({'id':name+'_'+key,'value':value,'status':'computed','n':len(frame)} for key,value in values.items())
    for kind in ('pearson','spearman'):
        x=frame[['glucose','hba1c']]
        if kind=='spearman':x=x.rank(method='average')
        value=float(np.corrcoef(x.to_numpy(dtype=float),rowvar=False)[0,1])
        if not np.isfinite(value):value=None
        diagnostics.append({'id':'glucose_hba1c_'+kind,'value':value,'status':'computed' if value is not None else 'unavailable','unit':'1','n':len(frame)})
    nonpositive={v:int((frame[v]<=0).sum()) for v in ('glucose','hba1c')}
    analyses=[]
    for d in definitions['analyses']:
        x=np.column_stack([np.ones(len(frame)),frame[d['predictors']].to_numpy(dtype=float)])
        rank=int(np.linalg.matrix_rank(x));value=None
        if rank==x.shape[1] and not any(nonpositive.values()):
            beta=np.linalg.lstsq(x,frame[d['outcome']].to_numpy(dtype=float),rcond=None)[0]
            value=float(beta[d['predictors'].index(d['term'])+1])
        analyses.append({'id':d['id'],'value':value,'status':'computed' if value is not None else 'unavailable','unit':d['unit'],'n':len(frame),'rank':rank})
    return {'analyses':analyses,'diagnostics':diagnostics,'n':len(frame),
            'quality':{'nonpositive_glycemia':nonpositive,'duplicate_measurement_rows':int(frame.drop(columns=['row_id']).duplicated().sum())}}

def with_reference(generated,reference):
    result=json.loads(json.dumps(generated))
    for row in result['analyses']:
        ref=reference['estimands'][row['id']]
        row.update(reference=ref['coefficient'],reference_interval=ref['interval'],difference=row['value']-ref['coefficient'] if row['value'] is not None else None)
    for row in result['diagnostics']:
        if row['id'].startswith('glucose_hba1c_'):value=reference['diagnostics']['joint'][row['id'].split('_')[-1]]
        else:
            name,stat=row['id'].rsplit('_',1);value=reference['diagnostics']['marginal'][name][stat]
        row.update(reference=value,difference=row['value']-value if row['value'] is not None else None)
    return result

def evaluate(bundle,candidate,run_id,profile):
    from cohort_harness.execution import verify_execution
    from cohort_harness.lifecycle import read_table
    bundle=Path(bundle);config=load(profile)
    receipt=verify_execution(bundle,run_id)
    assert receipt['status']=='success'
    assert receipt['candidate']=='candidates/'+str(candidate).removeprefix('candidates/')
    output=bundle/'executions'/run_id/'output/generated.csv'
    frame=read_table(output,load(bundle/'task.json'),output=True)
    result=generated_statistics(frame,load(config['analysis_definitions']))
    if config['information_condition']=='R':
        result=with_reference(result,load(config['reference_summary']))
        result['reference_sha256']=sha(config['reference_summary'])
    else:
        assert config['information_condition']=='L' and 'reference_summary' not in config
    result.update(kind='allowed_information_analysis',output_sha256=sha(output),information_condition=config['information_condition'])
    return result
