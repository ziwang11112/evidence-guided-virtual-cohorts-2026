"""Exploratory deterministic assignment control on the registered Polish lung-function grids."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time

# The scientific calculation uses a single BLAS thread.
for key in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[key]="1"

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linear_sum_assignment, milp
from scipy.sparse import coo_matrix

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/"article_lung_pairing_2026-11-22"
sys.path.insert(0,str(SOURCE))
import lung

N=8000
NBLOCK=100
WEIGHTS=sorted([0.]+[s*r for r in (.01,.05,.2,1.,5.,20.,100.,1000.) for s in (-1.,1.)])
TOLERANCE=.00010


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_menu(x,y,sign):
    zx=(x-x.mean())/x.std(); zy=(y-y.mean())/y.std()
    menus=[]; group_ids=[]
    for start in range(NBLOCK):
        ids=np.arange(start,N,NBLOCK)
        hit=(x[ids,None]/y[ids][None,:]<.70).astype("int16")
        physical=x[ids,None] <= y[ids][None,:]
        prod=zx[ids,None]*zy[ids][None,:]
        choices={}
        def add(indices):
            key=indices.tobytes()
            if key not in choices:
                ii=np.arange(len(ids))
                assert physical[ii,indices].all() and np.array_equal(np.sort(indices),ii)
                choices[key]=(indices.copy(),float(prod[ii,indices].sum()/N),int(hit[ii,indices].sum()))
        add(np.arange(len(ids)))
        for multiplier in WEIGHTS:
            cost=-sign*hit.astype(float)-multiplier*prod
            cost[~physical]=np.inf
            rows,columns=linear_sum_assignment(cost)
            assert np.array_equal(rows,np.arange(len(ids)))
            add(columns.astype(int))
        groups=list(choices.values())
        menus.append(groups);group_ids.append(ids)
    return group_ids,menus


def measures(menus, choice):
    return math.fsum(g[k][1] for g,k in zip(menus,choice)),sum(g[k][2] for g,k in zip(menus,choice))


def greedy(menus,target,sign):
    choice=np.zeros(NBLOCK,dtype=int)
    cov,hits=measures(menus,choice)
    attempts=0
    # First select the neighboring menu option that best closes the moment error.
    # On ties prefer the requested screening direction.
    while abs(cov-target)>TOLERANCE and attempts<2*NBLOCK:
        best=(abs(cov-target),-sign*hits,NBLOCK,0)
        for b,g in enumerate(menus):
            for k,(_,cv,count) in enumerate(g):
                residual=abs(cov+cv-g[choice[b]][1]-target)
                outcome=hits+count-g[choice[b]][2]
                candidate=(residual,-sign*outcome,b,k)
                if candidate<best:
                    best=candidate
        _,_,b,k=best
        if b==NBLOCK:
            break
        choice[b]=k
        cov,hits=measures(menus,choice)
        attempts+=1
    if abs(cov-target)>TOLERANCE:
        return None,attempts
    for _ in range(64):
        improved=False
        for b,g in enumerate(menus):
            feasible=[k for k,v in enumerate(g) if abs(cov+v[1]-g[choice[b]][1]-target)<=TOLERANCE]
            k=max(feasible,key=lambda k: (sign*g[k][2],-abs(cov+g[k][1]-g[choice[b]][1]-target),-k))
            if sign*(g[k][2]-g[choice[b]][2])>0:
                cov+=g[k][1]-g[choice[b]][1];choice[b]=k;improved=True
        if not improved:
            break
    return choice,attempts


def integer_selection(menus,target,sign):
    groups=np.array([b for b,menu in enumerate(menus) for _ in menu])
    cov=np.array([v[1] for menu in menus for v in menu])
    counts=np.array([v[2] for menu in menus for v in menu],dtype=float)
    m=len(groups);idx=np.arange(m)
    # Scale the covariance coefficients so the solver's feasibility tolerance
    # is negligible compared with the registered rounding intervals.
    rows=np.r_[groups,np.full(m,NBLOCK)]
    mat=coo_matrix((np.r_[np.ones(m),cov*N],(rows,np.r_[idx,idx])),shape=(NBLOCK+1,m)).tocsr()
    lo=np.r_[np.ones(NBLOCK),(target-TOLERANCE)*N]
    hi=np.r_[np.ones(NBLOCK),(target+TOLERANCE)*N]
    result=milp(c=-sign*counts,integrality=np.ones(m),bounds=Bounds(np.zeros(m),np.ones(m)),
                constraints=LinearConstraint(mat,lo,hi),
                options={"node_limit":2000,"time_limit":8.,"mip_rel_gap":0.0,"disp":False})
    choice=None
    if result.status==0 and result.x is not None:
        rounded=np.rint(result.x)
        assert np.allclose(result.x,rounded,atol=1e-5,rtol=0)
        off=np.r_[0,np.cumsum([len(g) for g in menus])]
        choices=[np.flatnonzero(rounded[i:j]) for i,j in zip(off[:-1],off[1:])]
        if all(len(v)==1 for v in choices):
            c=np.array([v[0] for v in choices],dtype=int)
            if abs(measures(menus,c)[0]-target)<=TOLERANCE+1e-8:
                choice=c
    return choice,{"solver_status":int(result.status),"message":result.message,
                   "node_count":getattr(result,"mip_node_count",None)}


def solve(x,y,target,sign):
    t0=time.perf_counter()
    ids,menus=build_menu(x,y,sign)
    a,n=greedy(menus,target,sign)
    b,solver=integer_selection(menus,target,sign)
    solutions={name:c for name,c in (("greedy",a),("optimal_over_block_menus",b)) if c is not None}
    logged={name:{"correlation":measures(menus,c)[0],"screen_count":measures(menus,c)[1]} for name,c in solutions.items()}
    stats={**solver,"greedy_target_steps":n,"feasible_selections":logged,
           "menu_options":sum(map(len,menus)),"linear_assignment_calls":NBLOCK*len(WEIGHTS)}
    if not solutions:
        stats.update(status="no_feasible_solution",elapsed_seconds=time.perf_counter()-t0)
        return None,stats
    which=max(solutions,key=lambda k:(sign*measures(menus,solutions[k])[1],k=="greedy"))
    choice=solutions[which]
    perm=np.empty(N,dtype=np.int64)
    for idx,menu,k in zip(ids,menus,choice):
        perm[idx]=idx[menu[k][0]]
    assert np.array_equal(np.sort(perm),np.arange(N)) and np.all(x<=y[perm])
    stats.update(status="feasible",selected=which,elapsed_seconds=time.perf_counter()-t0)
    return perm,stats


def main(output_dir):
    t0=time.perf_counter()
    private=output_dir/"private";private.mkdir(exist_ok=True)
    source=lung.gold()
    grids=lung.grids(source,N)
    out={"status":"post-outcome deterministic constructive comparison",
         "design_sha256":sha(HERE/"DESIGN.md"),"registered_source_freeze_sha256":sha(SOURCE/"FREEZE.json"),
         "source_validation_sha256":sha(SOURCE/"lung.py"),"scipy_version":__import__("scipy").__version__,
         "arms":{},"search":{},"sha256":{},"cutoff_band_pct":{}}
    for name,sign in (("low",-1),("high",1)):
        assignments=[]
        for sex,x,y in grids:
            perm,detail=solve(x,y,math.sqrt(source[sex]["r2_pct"]/100),sign)
            out["search"][name+"_"+sex]=detail
            if perm is not None:
                assignments.append(perm)
        if len(assignments)!=len(grids):
            continue
        report=lung.score_rows(grids,assignments,source)
        assert not report["failures"]
        out["arms"][name]=report
        path=private/("pairings_"+name+".npy");np.save(path,np.stack(assignments),allow_pickle=False)
        out["sha256"][name]=sha(path)
        band=[]
        for (_,x,y),p in zip(grids,assignments):
            r=x/y[p]
            band.append(float(100*np.mean((r>=.695)&(r<.705))))
        out["cutoff_band_pct"][name]=float(np.mean(band))
    complete=set(out["arms"])=={"low","high"}
    gap=out["arms"]["high"]["percent"]-out["arms"]["low"]["percent"] if complete else None
    out["gap_pp"]=gap
    out["material_pair"]=bool(complete and gap>5)
    out["elapsed_seconds"]=time.perf_counter()-t0
    # Rows are private. Readable aggregates can be compared across offline replays.
    (output_dir/"RESULTS.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
    print(json.dumps({k:out[k] for k in ("gap_pp","material_pair","elapsed_seconds","cutoff_band_pct")}))
    for name,a in out["arms"].items():
        print(name,a["percent"],a["ratio_of_means_pct"],a["failures"])
    for name,a in out["search"].items():
        print(name,a["solver_status"],a["selected"] if a["status"]=="feasible" else "failed",a["elapsed_seconds"])
    return out


if __name__=="__main__":
    if sys.argv[1:]==["--replay"]:
        recorded=json.loads((HERE/"RESULTS.json").read_text(encoding="utf8"))
        (HERE/"private").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=HERE/"private") as tmp:
            replayed=main(Path(tmp))
            for obj in (recorded,replayed):
                obj.pop("elapsed_seconds")
                for result in obj["search"].values():
                    result.pop("elapsed_seconds")
            assert recorded==replayed, "The numerical replay changed a recorded result"
            for name, expected_hash in recorded["sha256"].items():
                local=HERE/"private"/("pairings_"+name+".npy")
                if not local.exists():
                    shutil.copyfile(Path(tmp)/"private"/local.name,local)
                assert sha(local)==expected_hash
        print("Exact scientific, solver and assignment-hash replay.")
    elif not sys.argv[1:]:
        if (HERE/"RESULTS.json").exists():
            raise FileExistsError("Results exist. Use --replay.")
        main(HERE)
    else:
        raise SystemExit("Usage: python control.py [--replay]")
