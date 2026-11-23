"""Freeze the study and run independent constructors without exposing the reference."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from filelock import FileLock

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
BASE = HERE.parent/"search_to_model_2026-11-22"
RUNTIME = HERE.parent/"article_autonomy_design_2026-11-22"
sys.path.insert(0,str(BASE))
from run import bound_flow, send_scientific
from verify_model import checked_bundle

SEARCH=HERE/"private/search"
SLOTS=[f"a{i:02d}" for i in range(1,7)]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_bytes())

def write(p,d):
    if p.exists():
        if load(p)!=d:
            raise ValueError("Existing artifact differs: "+str(p.name))
        return
    with p.open("x",encoding="utf8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write("\n")

def seal(label,files):
    p=HERE/(label+".json")
    digests={v.relative_to(PROJECT).as_posix():sha(v) for v in sorted(set(files))}
    if p.exists():
        if load(p)["sha256"]!=digests:
            raise ValueError("Freeze mismatch "+label)
    else:
        write(p,{"stage":label,"utc":datetime.now(timezone.utc).isoformat(),"sha256":digests})

def verify(label):
    for name,digest in load(HERE/(label+".json"))["sha256"].items():
        if sha(PROJECT/name)!=digest:
            raise ValueError("Input changed after freeze: "+name)

def presearch():
    if SEARCH.exists() and not (HERE/"PRESEARCH.json").exists():
        raise ValueError("Cannot freeze design after selection starts")
    files=[HERE/v for v in ("PROTOCOL.md","REQUEST.txt","eligible.json","select_study.py","experiment.py")]
    files += [BASE/v for v in ("run.py","search_audit.py","retrieve.py","verify_model.py")]
    seal("PRESEARCH",files)

def prebuild():
    verify("PRESEARCH")
    _, ids=checked_bundle(SEARCH)
    if len(ids)!=1 or ids!=load(SEARCH/"selection.json")["pmcids"]:
        raise ValueError("One verified selected paper required")
    if (HERE/"private/authors").exists() and not (HERE/"PREBUILD.json").exists():
        raise ValueError("Late prebuild freeze")
    files=[HERE/"PRESEARCH.json",HERE/"evaluate.py",HERE/"REFERENCE_ACCESS.json",HERE/"PREBUILD_READING.md",
           SEARCH/"article.txt", SEARCH/"selection_audit.json", HERE/"private/reference"/load(HERE/"REFERENCE_ACCESS.json")["local_file"]]
    files += sorted((RUNTIME/"evidence_replay").glob("*.py"))
    files += [RUNTIME/v for v in ("author_stage.py","run_candidate_stage.py","run_with_evidence_replay.py","runtime_stage.py")]
    if load(HERE/"REFERENCE_ACCESS.json")["pmcid"]!=ids[0]:
        raise ValueError("Reference and selected source are different studies")
    seal("PREBUILD",files)

def build():
    verify("PRESEARCH")
    verify("PREBUILD")
    article,_=checked_bundle(SEARCH)
    question=(HERE/"REQUEST.txt").read_text(encoding="utf8")
    folder=HERE/"private/authors"
    folder.mkdir(exist_ok=True)
    def author(slot):
        root=folder/slot
        root.mkdir(exist_ok=True)
        with FileLock(str(root/"slot.lock"),timeout=0):
            receipt=root/"slot_result.json"
            if receipt.exists():
                return load(receipt)
            try:
                final=bound_flow.run(root,article,question,send=send_scientific)
                result={"slot":slot,"status":final["execution_status"],"n_tables":len(final["runs"])}
            except Exception as exc:
                result={"slot":slot,"status":"failed","reason":f"{type(exc).__name__}: {str(exc)[:350]}"}
            write(receipt,result)
            print(result,flush=True)
            return result
    with ThreadPoolExecutor(max_workers=3) as pool:
        outcomes=list(pool.map(author,SLOTS))
    write(HERE/"CONSTRUCTORS.json",outcomes)

def prereveal():
    verify("PRESEARCH")
    verify("PREBUILD")
    files=[HERE/v for v in ("PREBUILD.json","CONSTRUCTORS.json","MEASUREMENT_MAPS.json","PREREVEAL_READING.md")]
    for slot in SLOTS:
        root=HERE/"private/authors"/slot
        files.append(root/"slot_result.json")
        files+=sorted((root/"episodes").glob("*/calls/*/receipt.json"))
        for name in ("design_as_authored.json","build.json","review.json","final_manifest.json","final_source_replay.json"):
            if (root/name).is_file():
                files.append(root/name)
        if (root/"final_manifest.json").exists():
            for r in load(root/"final_manifest.json")["runs"]:
                if r["status"]=="success":
                    p=Path(r["table"]).resolve()
                    if not p.is_relative_to(root/"execution_final") or sha(p)!=r["sha256"]:
                        raise ValueError("Virtual row receipt mismatch")
                    files.append(p)
    seal("PREREVEAL",files)

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=["presearch","prebuild","build","prereveal"])
    args=parser.parse_args()
    {"presearch":presearch,"prebuild":prebuild,"build":build,"prereveal":prereveal}[args.stage]()
