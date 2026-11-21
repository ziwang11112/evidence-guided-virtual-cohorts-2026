"""Common estimands for evidence-only pairs, unpaired target quantiles and measured records."""
from pathlib import Path
import hashlib
import json

import numpy as np
from scipy.special import ndtri

HERE = Path(__file__).resolve().parent
PRIVATE = HERE / "private"
ROOT = HERE.parents[1]
N = 4096
SEEDS = (52103, 52109, 52121)
CELLS = ("M50", "M60", "F50", "F60")
USES = ("mean_abs_gap_kg", "gap_at_least_5_pct", "mean_both_kg", "within_rank")
MARGINS = dict(zip(USES, (1., 5., 2., .10)))
EPS = 1e-10


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(path):
    return hashlib.sha256(Path(path).read_text(encoding="utf-8").encode()).hexdigest()


def seal(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if read(path) != obj:
            raise FileExistsError(f"Different content at {path.name}")
        return
    with path.open("x", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, allow_nan=False)
        fh.write("\n")


def source_grids(n=N):
    normal = ndtri((np.arange(n) + .5) / n)
    normal = (normal - normal.mean()) / normal.std()
    groups = []
    for key, _, _, rm, rs, lm, ls in read(HERE/"AU_SOURCE.json")["cells"]:
        r, l = rm + rs*normal, lm + ls*normal
        assert min(r.min(), l.min()) > 0
        groups.append((key, r, l))
    assert tuple(g[0] for g in groups) == CELLS
    return groups


def weighted_midranks(x, weights):
    values, inv = np.unique(x, return_inverse=True)
    mass = np.bincount(inv, weights=weights, minlength=len(values))
    return (np.cumsum(mass) - .5 * mass)[inv] / mass.sum()


def cell_scores(r, l, w):
    w = w / w.sum()
    gap = np.abs(r-l)
    x, y = weighted_midranks(r,w), weighted_midranks(l,w)
    x, y = x - w@x, y - w@y
    scale = np.sqrt((w@(x*x)) * (w@(y*y)))
    if not scale > 0:
        raise ValueError("No within-cell rank variation")
    return np.array([w@gap, 100 * (w@(gap >= 5-EPS)), w@((r+l)/2), (w@(x*y))/scale])


def score_order(grids, order):
    result = []
    for (key,r,l), indices in zip(grids,order,strict=True):
        k = len(r)
        assert len(l)==k and indices.dtype.kind in "iu" and np.array_equal(np.sort(indices),np.arange(k)),key
        result.append(cell_scores(r,l[indices],np.ones(k)))
    return np.mean(result,axis=0)


def independent(grids):
    """Exact expectation over all uniformly random within-cell permutations."""
    rows = []
    for _,r,l in grids:
        assert np.all(l[1:]>=l[:-1]) and len(r)==len(l)
        n = len(l)
        prefix = np.r_[0., np.cumsum(l)]
        k = np.searchsorted(l,r,side="right")
        dist = (2*k-n)*r + prefix[-1] - 2*prefix[k]
        lower = np.searchsorted(l,r-5+EPS,side="right")
        upper = n - np.searchsorted(l,r+5-EPS,side="left")
        rows.append([dist.sum()/n**2,100*(lower+upper).sum()/n**2,(r.mean()+l.mean())/2,0.])
    return np.mean(rows,axis=0)


def rule_permutation(grids, seed):
    """First-order variance of log(left/right), approximating the published orientation."""
    extra = read(HERE/"JOINT_SOURCE.json")
    vr = np.log1p((extra["dimensionless_individual_ratio_sd"]/extra["dimensionless_individual_ratio_mean"])**2)
    rng = np.random.default_rng(seed)
    qs, correlations = [], []
    for _,r,l in grids:
        cr, cl = r.std()/r.mean(), l.std()/l.mean()
        rho = float(np.clip((cr**2+cl**2-vr)/(2*cr*cl),-1.,1.))
        z = ndtri((np.arange(len(r))+.5)/len(r))
        latent = rho*z + np.sqrt(max(0.,1-rho*rho))*rng.normal(size=len(r))
        qs.append(np.argsort(np.argsort(latent,kind="stable"),kind="stable"))
        correlations.append(rho)
    return np.stack(qs),correlations


def cell_index(age, sex):
    return (2*(np.asarray(sex)=="F") + (np.asarray(age)>=60)).astype(int)


def measured(arr, w):
    group, r, l = arr
    result = []
    for g in range(4):
        take = (group==g) & (w>0)
        if not take.any():
            raise ValueError(f"No eligible measurements in {CELLS[g]}")
        result.append(cell_scores(r[take],l[take],w[take]))
    return np.mean(result,axis=0)


def separate_grids(arr, w, n=N):
    group, r, l = arr
    percentiles = (np.arange(n)+.5)/n
    def quantile(values, weights):
        order = np.argsort(values,kind="stable")
        cum = np.cumsum(weights[order])/weights.sum()
        return values[order][np.searchsorted(cum,percentiles,side="left")]
    return [(key,quantile(r[group==g],w[group==g]),quantile(l[group==g],w[group==g]))
            for g,key in enumerate(CELLS)]


def gain_bounds(left, right, x, ci):
    """All extrema of the difference of medians of absolute errors on a closed interval."""
    left, right = np.asarray(left,dtype=float),np.asarray(right,dtype=float)
    def gain(y):
        return float(np.median(np.abs(left-y))-np.median(np.abs(right-y)))
    lo,hi = ci
    knots = [lo,hi]
    for vals in (left,right):
        knots.extend(v for v in vals if lo<=v<=hi)
        knots.extend((a+b)/2 for a in vals for b in vals if lo<=(a+b)/2<=hi)
    gains = [gain(y) for y in knots]
    return {"point":gain(x),"over_reference_interval":[min(gains),max(gains)]}


def status(pred, ci, margin):
    lo,hi = ci
    if pred-margin<=lo and hi<=pred+margin:
        return "within"
    if hi<pred-margin or lo>pred+margin:
        return "outside"
    return "unresolved"


def named(values):
    return {k:float(v) for k,v in zip(USES,values,strict=True)}
