"""Construct the common decision material from old public evidence and frozen local draws.
No import or path in this module reads the new target measurements.
"""
import sys
from pathlib import Path
import numpy as np
from design import HERE, OLD, SENS, KEYS, USES, estimands, digest, obj, save


def bundle():
    sys.path.insert(0,str(OLD))
    from science import values
    tc, hdl = values()
    old, src = obj(OLD/"MODEL_CLOSURE.json"), obj(OLD/"SOURCE.json")
    provenance, draws = {}, []
    for run in old["arms"]["agent"]["runs"]:
        p = OLD/"private"/f"agent-{run['seed']}.npy"
        assert digest(p) == run["array_sha256"]
        draws.append(np.load(p, allow_pickle=False))
        provenance[p.name] = digest(p)
    nominal = estimands(*np.concatenate(draws).T)
    historical = {}
    for site in ("mekelle","workers"):
        path = OLD/"private"/(site+"-eligible.npy")
        rows = np.load(path,allow_pickle=False)
        assert rows.shape == ((321,3) if site=="mekelle" else (1164,3))
        historical[site] = estimands(rows[:,1], rows[:,2])
        provenance[path.name] = digest(path)
    estimates = {}
    laws = obj(SENS/"SENSITIVITY.json")["authors"]
    for author, record in laws.items():
        for mode, runs in record["runs"].items():
            assert record["scenarios"][mode]["pass"]
            pairs = []
            for run in runs:
                p = SENS/"private/draws"/author/mode/str(run["seed"])/"perm.npy"
                assert digest(p) == run["permutation_hash"]
                pairs.append(hdl[np.load(p,allow_pickle=False)])
            estimates[f"{author}_{mode}"] = estimands(np.tile(tc,len(pairs)), np.concatenate(pairs))
    for key, rec in obj(SENS/"CONTROL.json")["constructive_examples"].items():
        p = SENS/"private/control"/(key+".npy")
        assert digest(p) == rec["permutation_hash"]
        estimates["numerical_"+key] = estimands(tc,hdl[np.load(p,allow_pickle=False)])
    assert len(estimates)==10
    cases = {}
    for j,k in enumerate(KEYS):
        title, unit, tol, reported = USES[k]
        source = None
        if reported:
            s = src[reported]
            scale = 38.67 if k=="mean_nonhdl" else 1.
            source = {"point":s["estimate"]*scale,"ci95":[v*scale for v in s["source_ci"]]}
        alt = [v[j] for v in estimates.values()]
        cases[k] = {"use":title,"unit":unit,"tolerance":tol,"source_report":source,
                    "common_virtual":nominal[j],
                    "previous_external_measurements":{site:v[j] for site,v in historical.items()},
                    "alternative_models_range":[min(alt),max(alt)]}
    return {"cases":cases, "all_laws":{k:dict(zip(KEYS, p.tolist())) for k,p in estimates.items()},
            "old_files_sha256":provenance}


def comparator(cases):
    out = {}
    for k, e in cases.items():
        x = e["common_virtual"]
        source = e["source_report"]
        components = {
            "source_sampling": max(abs(y-source["point"]) for y in source["ci95"]) if source else None,
            "previous_transport": max(abs(y-x) for y in e["previous_external_measurements"].values()),
            "alternative_models": max(abs(y-x) for y in e["alternative_models_range"])}
        z = max(v for v in components.values() if v is not None)/e["tolerance"]
        out[k] = {"components":components,"score":z,"endorse":bool(z<=1)}
    return {"ranking":sorted(KEYS,key=lambda k: (out[k]["score"],KEYS.index(k))),
            "uses":out}


if __name__ == "__main__":
    value = bundle()
    paths = [(HERE/"PACKET.json",value), (HERE/"STATISTICAL_DECISION.json",comparator(value["cases"]))]
    for path,data in paths:
        if path.exists():
            assert obj(path)==data
        else:
            save(path,data)
    print("One frozen author law, ten alternative laws, and two historical cohorts. No new target access.")
