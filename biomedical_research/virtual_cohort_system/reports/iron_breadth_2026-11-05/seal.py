"""Seal all final private synthetic deliveries before admitting any reference outcomes."""
from pathlib import Path
import datetime as dt
import hashlib
import json

BASE = Path(__file__).resolve().parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_delivery():
    protocols = json.loads((BASE/"PROTOCOL_LOCK.json").read_text())["sha256"]
    for name, sha in protocols.items():
        if digest(BASE/name) != sha: raise ValueError("Changed precommit input: " + name)
    amend=json.loads((BASE/"PREAUTHOR_ADDENDUM.json").read_text())
    if digest(BASE/amend["added_input"]) != amend["sha256"]: raise ValueError("Changed admitted clarification")
    records={}
    for author in ("A","B"):
        law=BASE/"candidates"/author/"final"/"generator.py"
        initial=BASE/"candidates"/author/"initial"/"generator.py"
        for f in [law, initial, law.with_name("model.md"), initial.with_name("model.md"), law.with_name("decision.md")]:
            records[f.relative_to(BASE).as_posix()]=digest(f)
        for stage in ("initial","final"):
            note=BASE/"admission"/f"{author}_{stage}.json"
            for name,sha in json.loads(note.read_text())["hashes"].items():
                f=BASE/"private_runs"/author/"initial"/"source_4101"/"source_diagnostics.json" if name=="source_feedback" else BASE/"candidates"/author/stage/name
                if digest(f)!=sha: raise ValueError("Author lock no longer valid")
            records[note.relative_to(BASE).as_posix()]=digest(note)
        replay=[("final","source",4101)] if digest(initial)!=digest(law) else []
        for stage,context,seed in [("initial","source",4101), *replay, *[("final","target",i) for i in (5101,5102,5103)]]:
            run=BASE/"private_runs"/author/stage/f"{context}_{seed}"
            receipt=json.loads((run/"execution.json").read_text())
            records[(run/"execution.json").relative_to(BASE).as_posix()]=digest(run/"execution.json")
            expected_law=digest(initial if stage=="initial" else law)
            if receipt["status"]!="success": raise ValueError("Scheduled run failed; do not release automatically.")
            if receipt["agent_code_sha256"] != expected_law or digest(run/"input"/"author.py") != expected_law: raise ValueError("Wrong generator bytes")
            table=run/"output"/"generated.csv"
            if digest(table)!=receipt["generated_sha256"]: raise ValueError("Changed generated table")
            records[table.relative_to(BASE).as_posix()]=digest(table)
    for f in ["iron_runner.py","evaluation/analyze.py","seal.py"]:
        records[f]=digest(BASE/f)
    return records

if __name__=="__main__":
    out={"utc":dt.datetime.now(dt.timezone.utc).isoformat(),"n_laws":2,"n_final_tables":6,"records":check_delivery()}
    with (BASE/"BATCH_LOCK.json").open("x",encoding="utf-8") as fh: json.dump(out,fh,indent=2)
    print("Six final tables and both initial source runs sealed.")
