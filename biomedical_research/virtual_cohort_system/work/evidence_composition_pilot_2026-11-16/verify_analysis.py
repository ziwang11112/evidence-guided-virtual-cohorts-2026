"""Independent numerical route: covariance formulas, not OLS refits.

This is an independently coded recomputation by the same root assistant, not
an independent human adjudicator or another model's review.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent

def recompute(frame,family):
    if family=='adjusted':
        v=frame[['X','Y','Z']].to_numpy(float);c=np.cov(v.T)
        residual_cov=c[0,1]-c[0,2]*c[1,2]/c[2,2]
        residual_var=[c[j,j]-c[j,2]**2/c[2,2] for j in (0,1)]
        return {'partial_xy_given_z':float(residual_cov/np.sqrt(np.prod(residual_var))),
                'marginal_xy':float(c[0,1]/np.sqrt(c[0,0]*c[1,1])),
                'slope_x_on_z':float(c[0,2]/c[2,2])}
    v=frame[['X_visit1','Y_visit1','X_visit2','Y_visit2']].to_numpy(float);c=np.cov(v.T)
    a=np.array([-1,0,1,0]);b=np.array([0,-1,0,1])
    return {'change_correlation':float(a@c@b/np.sqrt((a@c@a)*(b@c@b))),
            'same_visit_correlation':float((c[0,1]/np.sqrt(c[0,0]*c[1,1])+c[2,3]/np.sqrt(c[2,2]*c[3,3]))/2),
            'cross_visit_correlation':float(c[0,3]/np.sqrt(c[0,0]*c[3,3]))}

def main():
    entries=json.loads((ROOT/'analysis/analyses.json').read_text(encoding='utf-8'));comparisons=[]
    cache={}
    for row in entries:
        key=(row['id'],row['seed'])
        if key not in cache:
            frame=pd.read_csv(ROOT/'executions'/row['id']/str(row['seed'])/'output/generated.csv',float_precision='round_trip')
            cache[key]=recompute(frame,row['family'])
        other=cache[key][row['estimand']];gap=abs(other-row['value'])
        comparisons.append({'id':row['id'],'seed':row['seed'],'estimand':row['estimand'],'difference':gap,'passed':gap<1e-10})
    result={'description':__doc__,'recomputed_tables':len(cache),'comparisons':len(comparisons),
            'max_absolute_difference':max([r['difference'] for r in comparisons],default=None),
            'all_passed':bool(comparisons) and all(r['passed'] for r in comparisons),'checks':comparisons}
    with (ROOT/'analysis/INDEPENDENT_RECOMPUTATION.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
    if not result['all_passed']:raise SystemExit(1)

if __name__=='__main__': main()
