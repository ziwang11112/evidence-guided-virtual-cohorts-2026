"""Record each immutable author stage and hash source feedback before review."""
import argparse, json, datetime
from pathlib import Path
from seal import BASE, digest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("author",choices=["A","B"]);p.add_argument("stage",choices=["initial","final"])
    a=p.parse_args()
    d=BASE/"candidates"/a.author/a.stage
    files=["generator.py","model.md"]+(["decision.md"] if a.stage=="final" else [])
    record={name:digest(d/name) for name in files}
    if a.stage=="final":
        record["source_feedback"]=digest(BASE/"private_runs"/a.author/"initial"/"source_4101"/"source_diagnostics.json")
    out=BASE/"admission"/(a.author+"_"+a.stage+".json")
    if out.exists(): raise FileExistsError(out)
    with out.open("x",encoding="utf8") as f:json.dump({"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"hashes":record},f,indent=2)
    print(record["generator.py"])
if __name__=="__main__": main()
