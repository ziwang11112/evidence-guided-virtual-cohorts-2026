"""Retrospective interpretation of source constraints, evaluated analytically without further draws."""
import itertools
import numpy as np
from scipy.optimize import brentq
from scipy.special import ndtr
from science import HERE,read,seal,source_grids


def bounds(grids):
    lo=np.mean([np.mean(abs(r-l)) for _,r,l in grids])
    hi=np.mean([np.mean(abs(r-l[::-1])) for _,r,l in grids])
    return float(lo),float(hi)


def gaussian_gap(rho,cells):
    arr=[]
    for _,_,_,mr,sr,ml,sl in cells:
        mu=mr-ml
        sd=np.sqrt(max(0,sr**2+sl**2-2*rho*sr*sl))
        if sd==0:
            arr.append(abs(mu))
        else:
            t=mu/sd
            arr.append(sd*np.sqrt(2/np.pi)*np.exp(-.5*t*t)+mu*(2*ndtr(t)-1))
    return float(np.mean(arr))


def run():
    groups=source_grids()
    toy=[("toy",np.array([1.,4.,7.,10.]),np.array([2.,3.,9.,14.]))]
    _,r,l=toy[0]
    distances=[np.mean(abs(r-l[list(p)])) for p in itertools.permutations(range(4))]
    np.testing.assert_allclose(bounds(toy),(min(distances),max(distances)))
    lo,hi=bounds(groups)
    cell=read(HERE/"AU_SOURCE.json")["cells"]
    res=read(HERE/"RESULTS.json")
    cis=[res["reference"][s]["estimates"]["mean_abs_gap_kg"]["ci"] for s in ("US_NHANES","ZA_HAALSI")]
    margin=res["margins"]["mean_abs_gap_kg"]
    limits=[max(b-margin for a,b in cis),min(a+margin for a,b in cis)]
    common=None
    if limits[0]<=limits[1] and gaussian_gap(1,cell) < limits[0] <= limits[1] < gaussian_gap(-1,cell):
        common=[float(brentq(lambda x:gaussian_gap(x,cell)-y,-1,1)) for y in limits[::-1]]
    grid=np.linspace(-1,1,401)
    vals=np.array([gaussian_gap(r,cell) for r in grid])
    assert np.all(np.diff(vals)<0)
    out={"scope":"Post-disclosure interpretation only. No new fits, draws, target-dependent source revisions or primary endpoint changes.",
         "exact_fixed_source_pairing_range_kg":[lo,hi],
         "original_independent_expectation_kg":read(HERE/"PREDICTIONS.json")["methods"]["independent"]["values"]["mean_abs_gap_kg"],
         "parametric_sensitivity":"Continuous Gaussian marginals with a common within-cell Pearson correlation; folded-normal mean gap. This analytical family approximates the finite positive grids used by the programs.",
         "hypothetical_fixed_correlations_and_expected_gap":{str(t):gaussian_gap(t,cell) for t in (0,.5,.7,.8,.85,.9,1)},
         "virtual_point_range_supporting_primary_use_in_both_cohorts_kg":limits,
         "common_gaussian_rho_range_supporting_absolute_use_in_both":common}
    seal(HERE/"SENSITIVITY.json",out)
    print(out)


if __name__=="__main__":run()
