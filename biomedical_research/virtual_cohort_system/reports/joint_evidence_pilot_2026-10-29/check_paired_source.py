"""Verify actual paired synthetic outputs against independently calculated mean ratios.

No generator import/execution or real target reading. This is a numerical
implementation check, not a new source or target biological validation.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
import numpy as np
import pandas as pd

E=Path(__file__).resolve().parent
B=Path(json.loads((E/'execution_location.json').read_text())['bundle'])
spec=json.loads((B/'candidates/joint_evidence/model_spec.json').read_text())['parameters']
joint=spec['joint_interaction'];grid=np.asarray(joint['relative_differences'])
out=[]

def g(age,bmi,sex):
    p=spec;r=p['reference']
    linear=r['tg_mean'][sex]+p['bmi_slope'][sex]*(bmi-r['bmi_mean'][sex])+p['age_slope'][sex]*(age-r['age_mean'][sex])
    floor=p['positive_mean']['floor'];width=p['positive_mean']['width'];x=(linear-floor)/width
    return floor+width*(max(x,0)+math.log1p(math.exp(-abs(x))))

for context in ['oh','bansal']:
    paths=[B/f'source_replays/{v}_80201/contexts/{context}/bundle/executions/replay/output/generated.csv' for v in ['baseline','joint_evidence']]
    tables=[pd.read_csv(path) for path in paths]
    left,right=tables
    pd.testing.assert_frame_equal(left.drop(columns='tg_mg_dl'),right.drop(columns='tg_mg_dl'),check_exact=True)
    assert left.tg_assay.eq('legacy_proxy').all()
    ids=set(np.linspace(0,len(left)-1,1024,dtype=int).tolist())
    for col in ['age','bmi']:
        ids|={int(left[col].idxmin()),int(left[col].idxmax())}
    errors=[]
    for i in sorted(ids):
        row=left.iloc[i];sex=int(row.sex)-1;age=float(row.age);bmi=float(row.bmi)
        ratios=grid[sex]
        contrasts=np.log(ratios*ratios[0,0]/(ratios[:,[0]]*ratios[[0],:]))
        by_age=[np.interp(bmi,joint['bmi_knots'],line) for line in contrasts]
        D=float(np.interp(age,joint['age_knots'],by_age))*joint['transfer_fraction']
        a0=joint['age_knots'][0];b0=joint['bmi_knots'][0]
        expected=(g(age,b0,sex)/g(age,bmi,sex))*(g(a0,bmi,sex)/g(a0,b0,sex))*math.exp(D)
        actual=float(right.iloc[i].tg_mg_dl/row.tg_mg_dl)
        errors.append(abs(actual/expected-1))
    assert max(errors)<1e-12,context
    out.append({'source_context':context,'synthetic_rows':len(left),'checked_rows':len(ids),
        'maximum_relative_ratio_error':max(errors),'observed_columns_exactly_preserved':True,
        'input_hashes':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]})
result={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','contexts':out,
    'scope':'paired source-generated rows only; same residual seed cancels in ratios; independent scalar softplus and nested 1D interpolation',
    'generator_code_imported_or_executed_here':False,'real_target_read':False,
    'scientific_validity':'not established by implementation equality'}
path=E/'review/PAIRED_SOURCE_NUMERICAL_CHECK.json'
with path.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
