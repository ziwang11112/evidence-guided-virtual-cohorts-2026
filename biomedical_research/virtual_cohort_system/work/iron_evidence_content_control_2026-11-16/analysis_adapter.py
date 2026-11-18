"""New routing only: existing iron estimator plus separate numerical recomputation."""
from pathlib import Path
import importlib.util, math
import numpy as np
import pandas as pd

P=Path(__file__).resolve().parents[2]
OLD=P/'work/iron_breadth_2026-11-05/evaluation'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
production=load('iron_content_production',OLD/'analyze.py')
independent=load('iron_content_independent',OLD/'independent.py')
PRIMARY=['odds_ratio','joint_prevalence','spearman']
ENDPOINTS=PRIMARY+['low_hb_fraction','low_ferritin_fraction']
UNITS={'odds_ratio':'1','joint_prevalence':'fraction','spearman':'1','low_hb_fraction':'fraction','low_ferritin_fraction':'fraction'}

def statistics(frame,task):
    if len(frame)!=task['n_rows'] or list(frame)!=['row_id','hb_g_dl','ferritin_ug_l']:
        raise ValueError('Wrong delivered shape/columns')
    if not frame.row_id.is_unique or not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError('Duplicate identifiers or invalid measurements')
    result=production.analyze_synthetic(frame)
    values={k:result['estimands'][k]['estimate'] for k in PRIMARY}
    values.update(low_hb_fraction=float((frame.hb_g_dl<12).mean()),
                  low_ferritin_fraction=float((frame.ferritin_ug_l<15).mean()))
    def entry(k):
        v=values[k]
        return {'id':k,'value':v,'status':'computed' if v is not None else 'not_estimable',
                'unit':UNITS[k],'reason':None if v is not None else 'Zero cell or constant ranks; no smoothing',
                'uncertainty':{'status':'unavailable','reason':'No inferential interval for simulated table'}}
    marginal={}
    for k in ['hb_g_dl','ferritin_ug_l']:
        x=frame[k].to_numpy(dtype=float)
        marginal[k]={'mean':float(x.mean()),'sd_population':float(x.std(ddof=0)),
                     'min':float(x.min()),'max':float(x.max()),
                     'geometric_mean':float(np.exp(np.log(x).mean())) if (x>0).all() else None,
                     'quantiles':{str(q):float(np.quantile(x,q)) for q in [.01,.25,.5,.75,.99]}}
    return {'status':'complete','analyses':[entry(k) for k in PRIMARY],
            'diagnostics':[entry(k) for k in ENDPOINTS[3:]],'cells':result['cells'],'flags':result['flags'],
            'marginals_delivered_units':marginal,
            'quality':{'n':len(frame),'row_filtering':False,
                'duplicate_measurement_rows':int(frame[['hb_g_dl','ferritin_ug_l']].duplicated().sum()),
                'nonpositive_hb':int((frame.hb_g_dl<=0).sum()),'nonpositive_ferritin':int((frame.ferritin_ug_l<=0).sum()),
                'exact_threshold_hb':int((frame.hb_g_dl==12).sum()),'exact_threshold_ferritin':int((frame.ferritin_ug_l==15).sum())},
            'target_reference_read':False}

def independent_values(frame):
    x=frame.rename(columns={'hb_g_dl':'hb','ferritin_ug_l':'fe'}).copy();x['w']=1.
    values,counts,mass=independent.weighted_metrics(x)
    n=len(frame)
    values.update(low_hb_fraction=(counts[0]+counts[1])/n,
                  low_ferritin_fraction=(counts[0]+counts[2])/n)
    return values,counts

def discrepancy(key,value,reference):
    if value is None or reference is None:return None
    if key=='odds_ratio':
        return abs(math.log(value)-math.log(reference)) if value>0 and reference>0 else None
    return abs(value-reference)

