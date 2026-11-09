"""Recompute scalar endpoints without importing the providers or author programs."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd
import runner

ROOT=Path(__file__).resolve().parent


def calculate(frame, family):
    n=len(frame)
    if family=='H':
        counts=frame.groupby(['female',pd.cut(frame.age,[24,39,54,69,79])],observed=False).size()
        assert len(counts)==8 and (counts==375).all()
        x=np.column_stack([np.ones(n),(frame.age-50)/10,frame.female,(frame.bmi-25)/5,(frame.glucose-100)/10])
        y=frame.hba1c.to_numpy();full=np.linalg.lstsq(x,y,rcond=None)[0]
        reduced=np.linalg.lstsq(x[:,:4],y,rcond=None)[0]
        secondary=np.linalg.lstsq(x[:,[0,1,2,4]],y,rcond=None)[0]
        out={'Q1_age10':full[1],'Q2_bmi5':reduced[3],'Q3_bmi5':full[3],
             'Q2_minus_Q3_bmi5':reduced[3]-full[3],'glucose10_age_sex':secondary[3],
             'q1_residual_rms':np.sqrt(np.mean((y-x@full)**2))}
        for col in ['age','female','bmi','glucose','hba1c']:
            values=frame[col].to_numpy(dtype=float);out[col+'.mean']=values.mean();out[col+'.sd_population']=values.std(ddof=0)
            # Equal cells and equal row counts imply uniform weights. Recompute
            # the exact inverse-CDF convention with stable sums, independently.
            ordered=np.sort(values,kind='stable');w=1/(8*375);total=math.fsum([w]*n)
            for q in [.1,.5,.9]:
                k=next(k for k in range(1,n+1) if math.fsum([w]*k)>=q*total)
                out[col+'.q'+str(int(100*q))]=ordered[k-1]
        return out
    f=frame.copy();f[['total_cholesterol','hdl_cholesterol']]*=38.67
    x=np.column_stack([np.ones(n),(f.age-50)/10,(f.sex=='F').astype(float),(f.bmi-25)/5])
    assert np.linalg.matrix_rank(x)==4
    out={};res=[]
    for col,name in [('total_cholesterol','K02-TC-BMI'),('hdl_cholesterol','K02-HDL-BMI')]:
        y=f[col].to_numpy();b=np.linalg.lstsq(x,y,rcond=None)[0];r=y-x@b
        out[name]=b[3];out[col+'.conditional_rms']=np.sqrt(np.mean(r*r));res.append(r)
    out['K02-LIPID-RESIDUAL']=np.corrcoef(res)[0,1]
    out['sex.F_fraction']=(f.sex=='F').mean()
    for col in ['age','bmi','total_cholesterol','hdl_cholesterol']:
        values=f[col].to_numpy(dtype=float);out[col+'.mean']=values.mean();out[col+'.sd_sample']=values.std(ddof=1)
        for q in [.1,.5,.9]:out[col+'.q'+str(int(q*100))]=np.quantile(values,q,method='linear')
    return out


def main():
    runner.closure_gate()
    raw=(ROOT/'EVALUATION.json').read_bytes();report=json.loads(raw)
    completed=runner.read(ROOT/'EVALUATION_COMPLETED.json')
    assert hashlib.sha256(raw).hexdigest()==completed['outputs']['EVALUATION.json']
    rows=[];unavailable=[]
    for slot in report['all_slots']:
        author,seed=slot['author_id'],slot['seed']
        receipt=runner.verify_execution(author,seed)
        if slot['analysis_status']!='complete':
            unavailable.append({'author':author,'seed':seed,'status':slot['analysis_status']});continue
        assert receipt['status']=='success'
        path=ROOT/'private_runs'/author/f'seed_{seed}'/'output/generated.csv'
        frame=runner.lifecycle.read_table(path,runner.task_contract(author),output=True)
        values=calculate(frame,author[0]);expected={r['id']:r['value'] for cat in ('analyses','diagnostics') for r in slot[cat]}
        assert set(values)==set(expected)
        for name,value in values.items():
            difference=abs(float(value)-expected[name]);tolerance=1e-9*max(1,abs(expected[name]))
            rows.append({'author':author,'seed':seed,'id':name,'absolute_difference':difference,
                         'tolerance':tolerance,'passed':difference<=tolerance})
    result={'scope':'Independent formulas on sealed generated tables only; no author/provider imports, clinical rows or new reference fits.',
        'evaluation_sha256':hashlib.sha256(raw).hexdigest(),'checks':len(rows),'passed':sum(r['passed'] for r in rows),
        'max_absolute_difference':max((r['absolute_difference'] for r in rows),default=None),
        'unavailable_slots':unavailable,'comparisons':rows}
    with (ROOT/'RECOMPUTATION.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:result[k] for k in ('checks','passed','max_absolute_difference','unavailable_slots')}))
    if result['passed']!=result['checks']:raise SystemExit(1)


if __name__=='__main__':main()
