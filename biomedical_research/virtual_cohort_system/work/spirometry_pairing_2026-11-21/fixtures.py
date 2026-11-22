"""Pre-disclosure tests using toy volumes and the published source summaries."""
import itertools
import numpy as np
import pandas as pd

from study import SEXES, comparator, fit, grids, named, project, score, target_grids


def check():
    toy=[]
    for sex, scale in zip(SEXES,[1.,1.4],strict=True):
        toy.append((sex, np.array([1., 2.2, 2.6, 4.])*scale, np.array([1.9, 2.5, 3.6, 5.])*scale))
    reverse=np.tile(np.array([3,2,1,0]),(2,1))
    fixed,stats=fit(toy,reverse)
    assert stats["changed_pairs"]>0 and stats["raw_invalid_rows"]>0 and stats["final_invalid_rows"]==0
    identity=np.tile(np.arange(4),(2,1))
    assert np.array_equal(fit(toy,identity)[0],identity)
    for _,x,y in toy:
        for perm in itertools.permutations(range(4)):
            q=project(x,y,np.array(perm))
            assert np.array_equal(np.sort(q),np.arange(4)) and np.all(x<=y[q])
    for q in [fixed,identity,reverse]:
        result=score(toy,q)
        x=np.concatenate([k[1] for k in toy])
        y=np.concatenate([k[2][v] for k,v in zip(toy,q,strict=True)])
        np.testing.assert_allclose(result[:3],[100*np.mean(x/y),100*x.mean()/y.mean(),100*np.mean(x/y<.70)])
    controls=grids()
    for joint in (False,True):
        proposal,_=comparator(controls,71,joint)
        accepted,info=fit(controls,proposal)
        assert info["final_invalid_rows"]==0
        if not joint: assert info["raw_invalid_rows"]==0
        measured=named(score(controls,accepted))
        assert abs(measured["ratio_of_means_pct"]-100*5.8/7.6)<1e-10
    one=pd.DataFrame(dict(sex=["F","F","M","M"],x=[1.,2.,2.,3.],y=[2.,3.,3.,4.],w=[1.,1.,1.,1.]))
    new=target_grids(one)
    assert all(len(x)==4096 and {min(x),max(x)}==set(one[one.sex==s].x) for s,x,_ in new)
    authors=np.array([-1.,0.,.3,5.4])
    for target in np.linspace(-5,10,151):
        difference=abs(2.-target)-np.median(np.abs(authors-target))
        assert abs(difference)<=np.median(np.abs(authors-2.))+1e-12
    from reference_spiro import summarize
    frame=pd.DataFrame(dict(sex=["F"]*6+["M"]*6,x=[1.,2.,3.,2.,1.8,2.6]*2,
        y=[2.,3.,4.,3.,2.6,3.1]*2,w=np.ones(12),stratum=[1]*12,psu=[1,1,2,2,3,3]*2))
    for design in (None,pd.DataFrame({"stratum":[1,1,1],"psu":[1,2,3]})):
        z,uncertainty=summarize(frame,design)
        assert np.isclose(z["mean_individual_ratio_pct"]["estimate"],100*(frame.x/frame.y).mean())
        assert np.isclose(z["ratio_of_means_pct"]["estimate"],100*frame.x.sum()/frame.y.sum())
        assert all(np.isfinite(x["ci"]).all() for x in z.values())
        if design is None:
            assert uncertainty["estimable_replicates"]["mean_individual_ratio_pct"]==2000


if __name__=="__main__":
    check()
    print("Toy pairing, native estimands, source controls and pre-disclosure error bound passed.")
