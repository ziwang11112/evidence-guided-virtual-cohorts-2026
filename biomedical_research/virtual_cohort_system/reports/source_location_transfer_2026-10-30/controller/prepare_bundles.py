"""Controller admission and visible task binding. Does not read target outcomes."""
from pathlib import Path
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding="utf-8-sig"))
def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value,f,indent=2,ensure_ascii=False); f.write("\n")

def main():
    visible = HERE/"custodian/visible/observed.csv"
    if sha(visible) != "1a54f4713d6368e76e890eaea8b88126f09d6f298b8012d9d5d72f7e02dc3728":
        raise ValueError("Custodian visible input changed")
    packet=read(HERE/"source_audit/source_evidence_packet.json")
    for source in packet["sources"]:
        if sha(PROJECT/source["artifact"]) != source["sha256"]:
            raise ValueError("Source extraction binding failed: "+source["id"])
    old=PROJECT/"work/m10/ha"
    admission=[]
    for family in ["ha","hb"]:
        bundle=HERE/family
        bundle.mkdir(exist_ok=False)
        (bundle/"sources").mkdir()
        (bundle/"candidates").mkdir()
        shutil.copyfile(visible,bundle/"observed.csv")
        task=read(old/"task.json")
        task["task_id"]="m11_hba1c_source_location_"+family
        task["n_rows"]=5378
        task["population"]="NHANES August2021-August2023 paired-analysis domain, age20-79, observed sex/BMI, positive WTPH2YR, finite measured HbA1c reserved solely for evaluation; no outcome-magnitude selection. New endpoint, potentially overlapping participants with prior other-outcome work."
        task["budget"]["revisions"]=3
        registry=read(old/"registry.json")
        for artifact in registry["artifacts"]:
            source=old/artifact["path"]
            if sha(source)!=artifact["sha256"]: raise ValueError("Old source changed")
            shutil.copyfile(source,bundle/artifact["path"])
        for source in packet["sources"][1:]:
            path=PROJECT/source["artifact"]
            relative="sources/"+path.name
            shutil.copyfile(path,bundle/relative)
            registry["artifacts"].append({"source_id":source["id"],"path":relative,"sha256":sha(path),"origin":"curator","screening":"approved"})
        summary=HERE/"source_audit/source_evidence_packet.json"
        shutil.copyfile(summary,bundle/"sources/m11_source_packet.json")
        registry["artifacts"].append({"source_id":"m11_source_packet","path":"sources/m11_source_packet.json","sha256":sha(summary),"origin":"curator","screening":"approved"})
        write(bundle/"task.json",task)
        write(bundle/"registry.json",registry)
        admission.append({"family":family,"bundle":str(bundle),"task_sha256":sha(bundle/"task.json"),"registry_sha256":sha(bundle/"registry.json"),"observed_sha256":sha(bundle/"observed.csv")})
    write(HERE/"source_admission.json",{"scope":"Controller source admission, no target outcome reading","same_cohort":"Masuch, Volzke and Grossmann SHIP-Trend overlap; not independent evidence","grossmann_use":"Admitted context-only cross-check, not an extra primary calibration target","packet_sha256":sha(summary),"bundles":admission})
    print(json.dumps({"bundles_prepared":2,"observed_rows":5378,"reference_read":False}))

if __name__=="__main__": main()
