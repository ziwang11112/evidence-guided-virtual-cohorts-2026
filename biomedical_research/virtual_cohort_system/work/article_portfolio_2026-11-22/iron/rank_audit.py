"""Post-outcome bound for all within-band permutations of the registered finite marginal values."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

HERE = Path(__file__).resolve().parent


def load(p):
    return json.loads(p.read_text(encoding="utf8"))


def write(out):
    p = HERE / "RANK_AUDIT.json"
    if p.exists():
        assert load(p) == out
    else:
        p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf8",newline="\n")


def main():
    results = load(HERE/"RESULTS.json")
    assert hashlib.sha256((HERE/"RESULTS.json").read_bytes()).hexdigest() == load(HERE/"VERIFICATION.json")["results_sha256"]
    grid = None
    identical_grids = set()
    unique = {role:set() for role in ("initial","ordinary","alternative")}
    checksums = {}
    at_max = Counter()
    at_min = Counter()
    examples = []
    total = 0
    for tag, model in sorted(results["models"].items()):
        if not model["usable"]:
            continue
        role=tag.split("_",1)[1]
        signature = []
        on_max, on_min = True, True
        for d in model["draws"]:
            group = load(HERE/"private/draws"/tag/str(d["seed"])/"run/input/model_spec.json")["groups"]
            unique_grid = hashlib.sha256(json.dumps(group,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            identical_grids.add(unique_grid)
            if grid is None:
                grid = group
                x = [np.array(v["x"]) for v in grid]
                y = [np.array(v["y"]) for v in grid]
                X = np.concatenate(x)
                assert all(np.all(np.diff(v)>0) for v in x+y)
                rx = rankdata(X)-(.5*len(X)+.5)
                ry = rankdata(np.concatenate(y))-(.5*len(X)+.5)
                rxg = np.split(rx,np.cumsum([len(v) for v in x])[:-1])
                ryg = np.split(ry,np.cumsum([len(v) for v in y])[:-1])
                scale = math.sqrt(np.dot(rx,rx)*np.dot(ry,ry))
                # Each within-group permutation preserves both marginal rank variances.
                low = sum(np.dot(u,v[::-1]) for u,v in zip(rxg,ryg))/scale
                high = sum(np.dot(u,v) for u,v in zip(rxg,ryg))/scale
                expectation = sum(len(u)*u.mean()*v.mean() for u,v in zip(rxg,ryg))/scale
                assert np.isclose(low,spearmanr(X,np.concatenate([v[::-1] for v in y])).statistic)
                assert np.isclose(high,spearmanr(X,np.concatenate(y)).statistic)
            q = d["outcome"]["requested"]
            assert low-1e-9 <= q <= high+1e-9
            on_max &= abs(q-high)<1e-9
            on_min &= abs(q-low)<1e-9
            signature.append(d["sha256"])
            total+=1
        checksums[tag]=tuple(signature)
        unique[role].add(tuple(signature))
        at_max[role] += int(on_max)
        at_min[role] += int(on_min)
        examples.append((model["requested"],tag))
    assert len(identical_grids)==1
    identical = [b for b in sorted(results["blocks"]) if checksums[b+"_ordinary"]==checksums[b+"_alternative"]]
    write({"status":"exploratory after registered scoring","all_scored_tables":total,
           "distinct_full_marginal_grids":len(identical_grids),"source_of_bounds":"Rearrangement inequality within each Hb band, fixed marginal rank vectors",
           "sharp_minimum":float(low),"conditional_random_pairing_expected_rho":float(expectation),
           "sharp_maximum":float(high),"observed_minimum_of_three_seed_means":min(examples),
           "observed_maximum_of_three_seed_means":max(examples),
           "models_on_upper_bound_at_all_seeds":dict(at_max),"models_on_lower_bound_at_all_seeds":dict(at_min),
           "distinct_three_seed_index_file_signatures":{r:len(s) for r,s in unique.items()},
           "identical_ordinary_targeted_index_files_at_all_seeds":identical})
    print((HERE/"RANK_AUDIT.json").read_text(encoding="utf8"))


if __name__=="__main__":
    main()
