"""Construct explicit feasible pairings under the numerical source checks."""
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linear_sum_assignment, milp
from scipy.sparse import csr_matrix, vstack

from scoring import OLD, score

sys.path.insert(0, str(OLD))
from science import values

MULTIPLIERS = (-32., -8., -2., -.5, -.125, 0., .125, .5, 2., 8., 32.)


def construct(tc, hdl, sign):
    blocks = 125
    n = len(tc)
    if n != blocks * 128:
        raise ValueError("The prespecified block partition requires 16000 pairs")
    options, lengths, tail_sum, ratio_sum = [], [], [], []
    for k in range(blocks):
        ids = np.arange(k, n, blocks)
        t, h = tc[ids,None], hdl[ids][None,:]
        ratio = t/h
        cutoff = (t-h >= 160.).astype(float)
        valid = h <= t
        choices = {}
        for weight in MULTIPLIERS:
            rows, cols = linear_sum_assignment(np.where(valid, sign*cutoff + weight*ratio, np.inf))
            key = cols.tobytes()
            if key not in choices:
                choices[key] = (cols.copy(), cutoff[rows,cols].sum(), ratio[rows,cols].sum())
        lengths.append(len(choices))
        for perm, tail, r in choices.values():
            options.append((ids, ids[perm]))
            tail_sum.append(tail)
            ratio_sum.append(r)
    p = len(options)
    membership = csr_matrix((np.ones(p), (np.repeat(np.arange(blocks),lengths), np.arange(p))),shape=(blocks,p))
    constraints = vstack([membership,csr_matrix(np.asarray(ratio_sum)/n)])
    # Use a slightly narrower interval so floating-point endpoints pass the original tests.
    lo = np.r_[np.ones(blocks),3.6595]
    hi = np.r_[np.ones(blocks),3.6605]
    opt = milp(sign*np.array(tail_sum), integrality=np.ones(p), bounds=Bounds(0,1),
               constraints=LinearConstraint(constraints,lo,hi), options={"mip_rel_gap":.005,"time_limit":40})
    if opt.x is None:
        raise ValueError("No integer witness within the fixed candidate library and time budget")
    groups = np.flatnonzero(opt.x > .5)
    if len(groups) != blocks:
        raise ValueError("Incomplete integer assignment")
    ix = np.full(n,-1,dtype=np.int64)
    for j in groups:
        ids, assigned = options[j]
        if (ix[ids] != -1).any():
            raise ValueError("Repeated block")
        ix[ids] = assigned
    stats = score(tc,hdl,ix)
    if stats["invalid_order"] or not 3.655 <= stats["mean_ratio"] < 3.665:
        raise ValueError("Optimizer witness failed direct row-level checks")
    return ix, {"score":stats,"option_count":p,"solver_status":int(opt.status),"library_mip_gap":float(opt.mip_gap)}


def numerical_control(directory):
    tc,hdl = values()
    rows = {}
    directory.mkdir(parents=True,exist_ok=True)
    for name, sign in (("low",1.),("high",-1.)):
        try:
            ix, result = construct(tc,hdl,sign)
            np.save(directory / (name+".npy"),ix,allow_pickle=False)
            rows[name] = result
        except (ValueError,RuntimeError) as exc:
            rows[name] = {"failure":str(exc)}
    return rows
