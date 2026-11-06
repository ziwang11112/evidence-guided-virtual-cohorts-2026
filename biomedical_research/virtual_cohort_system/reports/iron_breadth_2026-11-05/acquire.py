"""After closure only, admit the three official NHANES files into a private store."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import requests
from seal import BASE, digest, check_delivery

def main():
    lock=json.loads((BASE/"BATCH_LOCK.json").read_text())
    if check_delivery()!=lock["records"]: raise ValueError("Batch seal no longer matches")
    private=BASE/"private_reference"
    private.mkdir(exist_ok=True)
    # File identities found in the workspace before release; none of their
    # records are used to construct a generator. No download of duplicates.
    reuse=BASE.parent/"structure-robustness-2026-10-28"/"custodian"/"raw"/"DEMO_L.xpt"
    ledger={}
    for short in ("DEMO_L","CBC_L","FERTIN_L"):
        url=f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/{short}.xpt"
        if short=="DEMO_L" and reuse.is_file():
            path=reuse
            status="reused-local"
            if digest(path)!="ca4374a158b493b8b0163e1388da21d57a18d1b9cecff2aa4e2fa2bec494fe23":
                raise ValueError("Demographics do not match the October CDC acquisition receipt")
        else:
            path=private/f"{short}.xpt"
            if path.exists():
                status="reused-local"
            else:
                with requests.get(url,timeout=(12,60),stream=True) as r:
                    r.raise_for_status()
                    chunks=[]
                    total=0
                    for chunk in r.iter_content(262144):
                        total+=len(chunk)
                        if total>10*1024*1024: raise ValueError("Unexpected individual download size")
                        chunks.append(chunk)
                    data=b"".join(chunks)
                    if not data.startswith(b"HEADER RECORD*******LIBRARY HEADER RECORD"): raise ValueError("Response is not an XPT library")
                    with path.open("xb") as f: f.write(data)
                status="downloaded"
        with path.open("rb") as f:
            if not f.read(80).startswith(b"HEADER RECORD*******LIBRARY HEADER RECORD"): raise ValueError("Invalid XPT")
        ledger[short]={"url":url,"acquisition":status,"bytes":path.stat().st_size,"sha256":digest(path),"path":str(path)}
    local={"utc":dt.datetime.now(dt.timezone.utc).isoformat(),"batch_lock_sha256":digest(BASE/"BATCH_LOCK.json"),"files":ledger}
    with (private/"ACQUISITION.json").open("x",encoding="utf8") as f: json.dump(local,f,indent=2)
    public={**local,"files":{k:{a:b for a,b in vals.items() if a!="path"} for k,vals in ledger.items()}}
    with (BASE/"ACQUISITION_PUBLIC.json").open("x",encoding="utf8") as f: json.dump(public,f,indent=2)
    print({k:(v["bytes"],v["acquisition"]) for k,v in ledger.items()})
if __name__=="__main__":main()
