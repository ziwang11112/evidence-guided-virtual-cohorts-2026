"""Pre-disclosure regression checks for scientific units, complex weights and gain bounds."""
import numpy as np
from scipy.stats import spearmanr

from common import AGE_MASS, NAMES, check_grid, interval_class
from survey import gain, gain_range, standardized


def test():
    tc=np.array([200.,199.,6.2*38.67,250.,200.,199.])
    hdl=np.array([40.,40.,38.67,35.,40.,40.])
    groups=np.repeat([0,1,2],2)
    raw=np.array([1.,3.,1.,1.,2.,2.])
    w=np.repeat(AGE_MASS,2)*np.array([.25,.75,.5,.5,.5,.5])
    ans=dict(zip(NAMES,standardized(tc,hdl,groups,raw)))
    assert abs(ans["nonhdl160"]-100*(w[0]+w[2]+w[3]+w[4]))<1e-10
    assert abs(ans["hdl_low"]-100*w[3])<1e-10
    assert abs(ans["tc_high"]-100*(w[2]+w[3]))<1e-10
    rt=np.array([w[tc<t].sum()+.5*w[tc==t].sum() for t in tc])
    rh=np.array([w[hdl<h].sum()+.5*w[hdl==h].sum() for h in hdl])
    cov=np.cov(rt,rh,aweights=w,ddof=0)
    assert np.isclose(ans["rank_tc_hdl"],cov[0,1]/np.sqrt(cov[0,0]*cov[1,1]))
    uniform=standardized(tc,hdl,groups,np.ones(6))
    assert np.isfinite(uniform).all() and spearmanr(tc,hdl).statistic<0
    check_grid(np.array([[1.,2.],[2.,3.]]))
    try:
        check_grid(np.array([[1.,2.],[1.,3.]]))
    except AssertionError:
        pass
    else:
        raise AssertionError("Tied transformation was accepted")
    p=[23.,25.,31.,38.];lo,hi=gain_range(30.,p,[21.,33.])
    grid=np.arange(21.,33.001,.01)
    dense=[gain(30.,p,v) for v in grid]
    assert np.allclose([lo,hi],[min(dense),max(dense)],atol=1e-8)
    assert interval_class(-2.,2.,2.)=="within" and interval_class(2.,3.,2.)=="unresolved"
    assert interval_class(2.001,3.,2.)=="contradicted"


if __name__=="__main__":
    test()
    print("Numerical fixtures passed.")
