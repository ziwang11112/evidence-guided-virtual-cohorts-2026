"""Re-execute a released scientific program from its original model and a registered seed."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import experiment as ex
from evaluation import execute_candidate, grids, source_check


def source_digest(obj):
    # The provider client's immutable artifact.json format.
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")).hexdigest()


def pack():
    audit=ex.read(ex.HERE/"VERIFICATION.json")
    close=ex.read(ex.HERE/"AUTHORS.json")
    models={}
    for name,rec in close["calls"].items():
        obj=ex.artifact(name)
        if obj is not None:
            assert source_digest(obj)==rec["artifact.json_sha256"]
            models[name]=obj
    assert len(models)==audit["source_artifacts_verified"]
    target=ex.HERE/"PROGRAMS.json"
    if target.exists():
        assert ex.read(target)==models
    else:
        ex.save(target,models)
    # The signed local closure retains provider transaction IDs. Replay needs
    # the public model receipts, usage and hashes, not those identifiers.
    public_close = {
        "local_author_closure_sha256": ex.sha(ex.HERE / "AUTHORS.json"),
        "closed_utc": close["closed_utc"], "freeze_sha256": close["freeze_sha256"],
        "accounted_usd": close["accounted_usd"],
        "calls": {tag: {k: v for k, v in rec.items() if k != "response_id"}
                  for tag, rec in close["calls"].items()},
    }
    dest = ex.HERE / "PUBLIC_AUTHORS.json"
    if dest.exists():
        assert ex.read(dest) == public_close
    else:
        ex.save(dest, public_close)
    print("Archived",len(models),"scientific model submissions.")


def replay(tag,seed):
    if seed not in ex.SEEDS:
        raise ValueError("Choose a registered seed")
    obj=ex.read(ex.HERE/"PROGRAMS.json")[tag]
    closure = ex.read(ex.HERE / "PUBLIC_AUTHORS.json")
    audit = ex.read(ex.HERE / "RESULTS.json")
    assert closure["local_author_closure_sha256"] == audit["authors_sha256"]
    receipt=closure["calls"][tag]
    assert source_digest(obj)==receipt["artifact.json_sha256"]
    v,_=source_check(obj["model_spec"])
    tc,hdl=grids(v,ex.N)
    parent=ex.PRIVATE/"offline_replay";parent.mkdir(parents=True,exist_ok=True)
    folder=Path(tempfile.mkdtemp(dir=parent))
    observed=execute_candidate(obj,tc,hdl,seed,folder)
    prev=next(d for d in audit["models"][tag]["draws"] if d["seed"]==seed)
    if "score" in prev:
        assert observed["output_sha256"]==prev["output_sha256"]
    print(json.dumps(observed,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="action",required=True)
    sub.add_parser("pack")
    run=sub.add_parser("run");run.add_argument("slot");run.add_argument("seed",type=int)
    args=parser.parse_args()
    if args.action=="pack":pack()
    else:replay(args.slot,args.seed)
