"""All predeclared contrasts, no success threshold or post-reveal selection."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent
j=json.loads((R/'ANALYSIS_RESULTS.json').read_text(encoding='utf-8'))
real=next(x for x in j['results'] if x['kind']=='real_reference')
summary=[]
for c in real['analysis']['contrasts']:
    if c['stratum']!='pooled':continue
    row={k:c[k] for k in ['trait','contrast','estimate','lower','upper','raw_estimate','raw_lower','raw_upper','raw_unit','p_value']}
    row['constructors']={}
    for ep in ['LIFESTYLE_A1','LIFESTYLE_A2']:
        vals=[]
        for r in j['results']:
            if r.get('episode_id')==ep:
                cc=next(t for t in r['analysis']['contrasts'] if t['stratum']=='pooled' and (t['trait'],t['contrast'])==(c['trait'],c['contrast']))
                vals.append(cc)
        a={}
        for key in ['estimate','raw_estimate']:
            v=[x[key] for x in vals];a[key]=dict(mean=float(np.mean(v)),minimum=min(v),maximum=max(v),draws=v)
        row['constructors'][ep]=a
    summary.append(row)
out=dict(scope='All 9 additive contrasts; 3 seeds are within-constructor Monte Carlo repeats, not independent constructions',summary=summary)
(R/'PRIMARY_SUMMARY.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for r in summary:
    print(r['trait'],r['contrast'],'real',round(r['estimate'],4),'A1',round(r['constructors']['LIFESTYLE_A1']['estimate']['mean'],4),'A2',round(r['constructors']['LIFESTYLE_A2']['estimate']['mean'],4))
