"""Verify public timing, seals, tariffs, paired contrasts and reported decisions."""
import hashlib
import json
import math
import statistics
from datetime import datetime
from pathlib import Path

HERE=Path(__file__).resolve().parent
PROJ=HERE.parents[1]


def read(p):
    return json.loads(p.read_text(encoding="utf8"))


def lf(p):
    return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def replay():
    plan,parents,source,audit,opening,result,verified=[read(HERE/file) for file in
        ["FREEZE.json","PARENTS.json","SOURCE_CLOSURE.json","INPUT_AUDIT.json","REFERENCE_OPEN.json","RESULTS.json","VERIFICATION.json"]]
    times=[datetime.fromisoformat(a["utc"]) for a in [plan,parents,source,opening,result]]
    assert times==sorted(times) and opening["source_closure_lf_sha256"]==lf(HERE/"SOURCE_CLOSURE.json")
    assert source["parent_closure_lf_sha256"]==lf(HERE/"PARENTS.json") and source["freeze_lf_sha256"]==lf(HERE/"FREEZE.json")
    assert opening["target_sha256"]==read(HERE/"PARTITION.json")["parts"]["B"]["sha256"]
    for loc,h in plan["bound_files_lf_sha256"].items():
        assert lf(PROJ/loc)==h,loc
    laws=source["models"]; ct=0; cost=0.; hashes=0
    for name,model in laws.items():
        if "receipt" in model:
            ct+=1; cost+=model["receipt"]["tariff_cost_usd"] or 0.
        folder=HERE/"laws"/name
        if folder.exists():
            seal=read(folder/"SEAL.json")
            assert seal["artifact_sha256"]==model["artifact_sha256"]
            for file, h in seal["scientific_files"].items():
                assert lf(folder/file)==h,(name,file)
        hashes+=sum(item["status"]=="success" for item in model["runs"])
    actual=result["reference"]["rank"]; cells=result["reference"]["cells"]
    if min(cells)>0: assert math.isclose(cells[0]*cells[3]/(cells[1]*cells[2]),result["reference"]["odds_ratio"])
    for arm in ["ordinary","workflow"]:
        deltas=[];good=0
        for parent in [p for p in plan["parents"] if p.startswith(arm)]:
            row=result["pairs"][parent]
            if not row["complete"]: continue
            old,new=[laws[parent+s]["metrics"] for s in ["_control","_evidence"]]
            delta=abs(old["rank"]-actual)-abs(new["rank"]-actual)
            assert math.isclose(delta,row["control_to_evidence"],abs_tol=1e-12)
            deltas.append(delta)
            if min(cells)>=10 and new["odds_ratio"] and old["odds_ratio"]:
                ok=(1/1.5<=new["odds_ratio"]/result["reference"]["odds_ratio"]<=1.5 and
                    1/1.2<=new["odds_ratio"]/old["odds_ratio"]<=1.2)
                good+=int(ok and abs(new["rank"]-actual)<=.1)
        group=result["arms"][arm]
        assert len(deltas)==group["complete_pairs"] and good==group["final_rank_and_guard_passes"]
        if deltas:
            point=statistics.median(deltas)
            assert math.isclose(point,group["median_incremental_gain"],abs_tol=1e-12)
            assert (len(deltas)==3 and good>=2 and point>=.05 and group["median_incremental_B_sampling_interval"][0]>0 and
                    result["reference"]["precision_rule"])==group["material_benefit_rule_pass"]
    assert ct==source["api_calls"]==audit["verified_recorded_payloads"]==result["api_calls"]<=18
    assert math.isclose(cost,result["tariff_usd"]) and cost<=plan["cap_usd"]
    assert verified["verified"] and hashes>=verified["successful_table_hashes_and_analyses"]
    print(f"Verified {ct} calls, {hashes} successful draw receipts, both arm decisions, source seals and chronological holdout opening.")


if __name__=="__main__":
    replay()
