from itertools import permutations
import math
import numpy as np
from scipy.special import ndtr
from science import CUTOFF,HERE,N,SEEDS,estimates,gaussian_rho,paired,possible_counts,read,source_law,stat_permutation,values

def test():
    s=read(HERE/"SOURCE.json");l=source_law();st,sh=l["log_sds"]
    for i,(cut,p) in enumerate(((6.2,1-s["tc_high_pct"]["estimate"]/100),(1.,s["hdl_low_pct"]["estimate"]/100))):
        sigma=l["log_sds"][i];mean=l["means_mg_dl"][i]/s["cholesterol_mg_dl_per_mmol_l"]
        assert abs(ndtr((math.log(cut/mean)+sigma*sigma/2)/sigma)-p)<1e-10
    mt,mh=l["means_mg_dl"]
    assert abs(mt/mh*math.exp(sh*sh-gaussian_rho()*st*sh)-s["mean_individual_ratio"]["estimate"])<1e-10
    t,h=values()
    np.testing.assert_allclose([t.mean(),h.mean()],[mt,mh],rtol=0,atol=1e-10)
    for seed in SEEDS:
        m=estimates(paired(stat_permutation(N,seed)))
        assert abs(m["mean_mg_dl"]-(mt-mh))<1e-9
    assert estimates(np.array([[200.,40.],[199.9,40.],[201.,40.]]))["tail_count"]==2
    for t,h in (([200,190,180,195],[40,30,60,50]),([100,115,120],[60,50,40]),([300,305],[40,60])):
        outcomes=[sum(a-b>=CUTOFF for a,b in zip(t,v)) for v in permutations(h)]
        assert possible_counts(t,h)==(min(outcomes),max(outcomes))
    try:paired(np.zeros(N,dtype=int))
    except ValueError:pass
    else:raise AssertionError("Duplicate permutation should fail")
    print("Source extraction operator, both marginals, ratio calibration, permutation, threshold equality and sharp bounds passed.")
if __name__=="__main__":test()
