"""Pre-disclosure checks on invented values and functions using the published summaries only."""
import itertools
import numpy as np
import pandas as pd
from scipy.stats import rankdata,spearmanr
from science import (cell_index,cell_scores,gain_bounds,independent,measured,score_order,separate_grids,
                     source_grids,status,weighted_midranks,rule_permutation,read,HERE)
from reference import estimate


def check():
    np.testing.assert_array_equal(cell_index([50,60,55,69],["M","M","F","F"]),range(4))
    g=[(str(k),np.array([2.,4.,9.,15.])+k,np.array([3.,8.,9.,14.])+k) for k in range(4)]
    got=[]
    for q in itertools.permutations(range(4)):
        got.append(score_order(g,np.tile(q,(4,1))))
    np.testing.assert_allclose(independent(g),np.mean(got,axis=0),atol=2e-13)
    xs=np.array([4.,2.,4.,7.]);ys=np.array([0.,3.,1.,2.]);w=np.array([3,1,2,4])
    rr=np.repeat(xs,w);ll=np.repeat(ys,w)
    np.testing.assert_allclose(cell_scores(xs,ys,w)[3],spearmanr(rr,ll).statistic,atol=1e-13)
    idx=np.tile(np.arange(4),4);a=np.repeat([1.,4.,9.,14.],4)
    df=pd.DataFrame({"cell":idx,"r":a,"l":a+2,"w":np.ones(16),"stratum":np.zeros(16),"psu":np.repeat(range(4),4)})
    point,ci,deg=estimate(df,df[["stratum","psu"]].drop_duplicates())
    np.testing.assert_allclose(point,[2.,0.,8.,1.]);np.testing.assert_allclose(ci[[0,1]],[[2,2],[0,0]])
    assert deg==3
    grid=separate_grids((idx,df.r.to_numpy(),df.l.to_numpy()),df.w.to_numpy(),4)
    assert all(np.array_equal(l,r+2) for _,r,l in grid)
    for m,(_,r,l) in zip(read(HERE/"AU_SOURCE.json")["cells"],source_grids(),strict=True):
        np.testing.assert_allclose([r.mean(),r.std(),l.mean(),l.std()],[m[3],m[4],m[5],m[6]])
    rule,rhos=rule_permutation(source_grids(),17)
    assert rule.shape==(4,4096) and all(-1<=z<=1 for z in rhos)
    for r in rule:assert np.array_equal(np.sort(r),np.arange(len(r)))
    x,y=[1,7,8,21],[0,2,14,15]
    actual=gain_bounds(x,y,8,[1,19])
    cand=np.linspace(1,19,3601)
    dif=np.median(abs(cand[:,None]-x),axis=1)-np.median(abs(cand[:,None]-y),axis=1)
    np.testing.assert_allclose(actual["over_reference_interval"],[dif.min(),dif.max()])
    assert status(1,[.1,1.9],1)=="within" and status(1,[2.1,3.],1)=="outside" and status(1,[1.1,3.],1)=="unresolved"
    print("Synthetic fixture, exact permutations, weighted ranks, survey factors, empirical margins, source cells and interval extrema passed.")
