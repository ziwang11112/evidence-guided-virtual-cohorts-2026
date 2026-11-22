"""Release the scientific submissions and replay a registered seed without an API call."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from lung import evidence, grids, run_model, score_rows, gold
import trial as t


def model_hash(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False).encode()).hexdigest()


def pack():
    result=t.read(t.HERE/"RESULTS.json")
    verified=t.read(t.HERE/"VERIFICATION.json")
    assert t.sha(t.HERE/"RESULTS.json")==verified["results_sha256"]
    closed=t.read(t.HERE/"AUTHORS.json")
    assert result["author_sha256"]==t.sha(t.HERE/"AUTHORS.json")
    out={}
    for slot,receipt in closed["calls"].items():
        assert not {"response_id","request_id","headers","prompt","response_text"}.intersection(receipt)
        obj=t.artifact(slot)
        if obj is not None:
            assert set(obj)=={"model_spec","generator_py","decision_record"}
            assert model_hash(obj)==receipt["artifact.json_sha256"]
            out[slot]=obj
    programs=t.HERE/"PROGRAMS.json"
    if programs.exists():assert t.read(programs)==out
    else:t.save(programs,out)
    receipt=t.HERE/"PUBLIC_AUTHORS.json"
    if receipt.exists():assert t.sha(receipt)==result["author_sha256"]
    else:shutil.copyfile(t.HERE/"AUTHORS.json",receipt)
    print("Released",len(out),"scientific model submissions.")


def replay(slot,seed):
    if seed not in t.SEEDS:raise ValueError("Choose a registered seed")
    obj=t.read(t.HERE/"PROGRAMS.json")[slot]
    recipient=t.read(t.HERE/"PUBLIC_AUTHORS.json")
    result=t.read(t.HERE/"RESULTS.json")
    assert t.sha(t.HERE/"PUBLIC_AUTHORS.json")==result["author_sha256"]
    assert model_hash(obj)==recipient["calls"][slot]["artifact.json_sha256"]
    v,_=evidence(obj["model_spec"])
    g=grids(v,t.N)
    directory=t.PRIVATE/"offline_replay"
    directory.mkdir(parents=True,exist_ok=True)
    orders,h=run_model(obj,g,seed,Path(tempfile.mkdtemp(dir=directory)))
    previous=next(r for r in result["models"][slot]["draws"] if r["seed"]==seed)
    assert h==previous["sha256"]
    recalculated=score_rows(g,orders,gold())
    assert recalculated==previous["outcome"]
    print(json.dumps({"slot":slot,"seed":seed,"sha256":h,"percent":recalculated["percent"],
                      "ratio_of_means_pct":recalculated["ratio_of_means_pct"]},indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="action",required=True)
    sub.add_parser("pack")
    run=sub.add_parser("run");run.add_argument("slot");run.add_argument("seed",type=int)
    args=parser.parse_args()
    if args.action=="pack":pack()
    else:replay(args.slot,args.seed)
