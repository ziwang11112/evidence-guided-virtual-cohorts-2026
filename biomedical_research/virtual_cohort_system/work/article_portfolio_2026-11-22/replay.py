"""Pack scientific submissions and reproduce a published index file and estimates offline."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from matched import Publication, read, save, sha


def artifact_hash(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False).encode()).hexdigest()


def pack(study):
    dest = study.path / "PROGRAMS.json"
    closure = read(study.path/"PUBLIC_AUTHORS.json")
    verification = read(study.path/"VERIFICATION.json")
    assert sha(study.path/"RESULTS.json")==verification["results_sha256"]
    assert sha(study.path/"PUBLIC_AUTHORS.json")==verification["receipts_sha256"]
    models = {}
    for slot, receipt in closure["calls"].items():
        obj = study.program(slot)
        if obj is None:
            continue
        assert set(obj)=={"model_spec","generator_py","decision_record"}
        assert artifact_hash(obj)==receipt["artifact.json_sha256"]
        models[slot] = obj
    if dest.exists():
        assert read(dest)==models
    else:
        save(dest,models)
    print("Packed",len(models),"scientific submissions")


def replay(study, slot, seed):
    if seed not in study.case.SEEDS:
        raise ValueError("Choose a registered seed")
    results = read(study.path/"RESULTS.json")
    closure = read(study.path/"PUBLIC_AUTHORS.json")
    assert sha(study.path/"PUBLIC_AUTHORS.json")==results["authors_sha256"]
    obj = read(study.path/"PROGRAMS.json")[slot]
    assert artifact_hash(obj)==closure["calls"][slot]["artifact.json_sha256"]
    groups = study.case.groups(obj["model_spec"])
    where = study.private / "offline_replay"
    where.mkdir(parents=True,exist_ok=True)
    orders, checksum = study.execute(obj,groups,seed,Path(tempfile.mkdtemp(dir=where)))
    draw = next(v for v in results["models"][slot]["draws"] if v["seed"]==seed)
    assert checksum==draw["sha256"]
    outcome = study.case.stats(groups,orders)
    assert outcome==draw["outcome"]
    print(json.dumps({"slot":slot,"seed":seed,"generated_sha256":checksum,
                      "fixed":outcome["fixed"],"requested":outcome["requested"]},indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("publication",choices=("iron","grip"))
    sub=parser.add_subparsers(dest="action",required=True)
    sub.add_parser("pack")
    runner=sub.add_parser("run")
    runner.add_argument("slot"); runner.add_argument("seed",type=int)
    args=parser.parse_args()
    study=Publication(args.publication)
    if args.action=="pack":
        pack(study)
    else:
        replay(study,args.slot,args.seed)
