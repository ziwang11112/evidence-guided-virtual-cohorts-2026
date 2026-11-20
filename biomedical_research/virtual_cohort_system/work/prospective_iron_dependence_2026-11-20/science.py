"""Source-only pairing laws and fixed endpoints for the external transport test."""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import ndtr, ndtri
from scipy.stats import beta, rankdata

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
MODEL_DIR = WORK / "chns_statistical_comparator_2026-11-19"
SOURCE = WORK / "chns_iron_conditional_holdout_2026-11-19"
sys.path.insert(0, str(MODEL_DIR))
import source_model

SEEDS = [201101, 201103, 201107]
N = 12000
PARENTS = [f"author{i}" for i in range(1, 7)]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def log_ferritin(band, standard_score):
    """Quantile at Phi(standard_score), stably computed on either side of 15."""
    u = ndtr(standard_score)
    if u < band.p:
        z = ndtri(ndtr(band.t) * u / band.p)
    else:
        z = -ndtri(ndtr(-band.t) * ndtr(-standard_score) / (1 - band.p))
    return band.mu + band.sigma * z


def population_contrast(band, rho):
    p_low = beta.cdf((13 - band.lo) / (band.hi - band.lo),
                     band.first_shape, band.second_shape_or_scale)
    cut = ndtri(p_low)
    remainder = math.sqrt(1 - rho * rho)
    def integrand(z):
        pr_low = ndtr((cut-rho*z)/remainder)
        return (math.exp(-z*z/2)/math.sqrt(2*math.pi) * log_ferritin(band,z) *
                ((1-pr_low)/(1-p_low) - pr_low/p_low))
    pivot = ndtri(band.p)
    return sum(quad(integrand,a,b,epsabs=5e-12,epsrel=5e-12)[0]
               for a,b in [(-10.,pivot),(pivot,10.)])


def baseline_fit():
    bands=source_model.fit(read(SOURCE/"A_TABLES.json"))
    target=math.log(read(SOURCE/"A_SUPPLEMENT.json")["estimate"])
    rho=brentq(lambda r:population_contrast(bands[1],r)-target,-.995,.995,xtol=2e-12)
    if abs(population_contrast(bands[1],rho)-target)>1e-9:
        raise ValueError("Source calibration failed")
    return bands,float(rho)


def marginals(bands,seed,n=N):
    source=source_model.draw(bands,seed,n)
    ids=np.digitize(source.hb_g_dl,[12.,14.])
    return [{"hb":np.sort(source.hb_g_dl.to_numpy()[ids==i]).tolist(),
             "ferritin":np.sort(source.ferritin_ug_l.to_numpy()[ids==i]).tolist()}
            for i in range(3)]


def baseline_indices(groups,rho,seed):
    rng=np.random.default_rng(np.random.SeedSequence([seed,3901]))
    seq=[]
    for group in groups:
        n=len(group["hb"])
        a,b=rng.standard_normal((2,n))
        f=rho*a+math.sqrt(1-rho*rho)*b
        seq.extend(np.argsort(np.argsort(f))[np.argsort(a)].tolist())
    return np.asarray(seq)


def pair(groups,indices):
    ix=np.asarray(indices)
    if not np.issubdtype(ix.dtype,np.integer) or ix.ndim!=1:
        raise ValueError("One integer index per Hb value is required")
    out=[]; offset=0
    for group in groups:
        h,f=np.array(group["hb"]),np.array(group["ferritin"])
        k=ix[offset:offset+len(h)]
        if not np.array_equal(np.sort(k),np.arange(len(f))):
            raise ValueError("Ferritin order must be a permutation within each band")
        out.append(np.column_stack([h,f[k]]))
        offset+=len(h)
    if offset!=len(ix):
        raise ValueError("Unexpected permutation length")
    return np.vstack(out)


def endpoints(rows):
    h,f=rows.T
    if not (np.isfinite(rows).all() and (rows>0).all()):
        raise ValueError("Measurements must be finite and positive")
    rank=float(np.corrcoef(rankdata(h),rankdata(f))[0,1])
    a,b,c,d=[int(np.count_nonzero(((h<12)==hx) & ((f<15)==fx)))
             for hx,fx in [(True,True),(True,False),(False,True),(False,False)]]
    low=(h>=12)&(h<13)
    high=(h>=13)&(h<14)
    ratio=float(np.exp(np.log(f[high]).mean()-np.log(f[low]).mean())) if low.any() and high.any() else None
    return {"n":len(rows),"rank":rank,"cells":[a,b,c,d],
            "odds_ratio":a*d/(b*c) if b*c else None,"middle_ratio":ratio}


def preflight():
    bands,rho=baseline_fit()
    assert abs(population_contrast(bands[1],0.))<1e-10 and 0<rho<.995
    assert population_contrast(bands[1],-.3)<0<population_contrast(bands[1],.3)
    groups=marginals(bands,913,25000)
    output=pair(groups,baseline_indices(groups,rho,913))
    natural=pair(groups,np.concatenate([np.arange(len(g["hb"])) for g in groups]))
    one,two=endpoints(output),endpoints(natural)
    assert one["cells"]==two["cells"] and one["rank"]<two["rank"]
    assert abs(math.log(one["middle_ratio"]/1.215))<.05
    h=np.array([[10,10],[11,25],[12,15],[13,12],[14,20]],dtype=float)
    assert endpoints(h)["cells"]==[1,1,1,2] and endpoints(h)["odds_ratio"]==2.
    try:
        pair(groups,np.zeros(len(output),dtype=int))
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicated ranks were accepted")
    return {"rho_statistical":rho,"fitted_source_middle_ratio":math.exp(population_contrast(bands[1],rho)),
            "tests":["zero, sign and positive solution","conditional quadrature root",
                     "source-only Monte Carlo contrast","cell invariance and changing rank",
                     "strict boundary rules","reject invalid permutation"]}
