"""Verify published closures, model bindings and the paired comparisons without private data."""
from pathlib import Path
from datetime import datetime
import json
import hashlib
import math


ROOT=Path(__file__).resolve().parent
def get(n): return json.loads((ROOT/n).read_text(encoding="utf8"))
def canon(p): return hashlib.sha256(p.read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def run():
    freeze=get("FREEZE.json"); parents=get("PARENT_CLOSURE.json"); closure=get("CLOSURE.json"); draw=get("DRAW_CLOSURE.json")
    raw=get("SOURCE_RESULTS.json"); result=get("SCIENTIFIC_RESULTS.json"); bridge=get("INTERFACE_CLOSURE.json"); opened=get("REFERENCE_OPEN.json"); revealed=get("REVEAL.json")
    times=[freeze["frozen_utc"],parents["time_utc"],closure["time_utc"],draw["time_utc"],raw["time_utc"],bridge["time_utc"],result["time_utc"],opened["time_utc"],revealed["time_utc"]]
    assert [datetime.fromisoformat(s) for s in times]==sorted(datetime.fromisoformat(s) for s in times)
    add=get("INTERFACE_FREEZE.json")
    assert parents["time_utc"]<add["time_utc"]<draw["time_utc"]
    for n,h in add["files_lf_sha256"].items(): assert canon(ROOT/n)==h
    assert bridge["raw_source_results_lf_sha256"]==canon(ROOT/"SOURCE_RESULTS.json")
    assert result["interface_closure_lf_sha256"]==canon(ROOT/"INTERFACE_CLOSURE.json")
    for p,h in freeze["files_lf_sha256"].items():
        if p.startswith("work/original_paper_iron_sensitivity_"):
            assert canon(ROOT/Path(p).name)==h
    assert closure["freeze_lf_sha256"]==canon(ROOT/"FREEZE.json")
    assert draw["closure_lf_sha256"]==canon(ROOT/"CLOSURE.json")
    assert opened["source_results_lf_sha256"]==canon(ROOT/"SOURCE_RESULTS.json")
    assert opened["draw_closure_lf_sha256"]==canon(ROOT/"DRAW_CLOSURE.json")
    means=result["laws"];total=sum(float(v["tariff_cost_usd"] or 0) for v in closure["all"].values())
    assert math.isclose(total,result["known_tariff_cost_usd"])
    usable=0
    for cid,record in closure["all"].items():
        if record.get("sealed"):
            assert datetime.fromisoformat(record["started_utc"])>datetime.fromisoformat(freeze["frozen_utc"])
            if "_" in cid:
                assert datetime.fromisoformat(record["started_utc"])>datetime.fromisoformat(parents["time_utc"])
            b=get("model_bindings.json")[cid]
            assert canon(ROOT/"laws"/(cid+".py"))==b["code_lf_sha256"]
            assert canon(ROOT/"laws"/(cid+".json"))==b["spec_lf_sha256"]
            assert b["private_artifact_lf_sha256"]==record["artifact_lf_sha256"]
    for row in result["pairs"]:
        a,b=means.get(row["primary"],{}),means.get(row["primary"]+"_"+row["branch"],{})
        assert row["both_tier2"]==bool(a.get("tier2") and b.get("tier2"))
        if "rank_gap" in row:
            gap=abs(a["spearman"]-b["spearman"])
            margin=1.96*math.hypot(a["rank_mcse"],b["rank_mcse"])
            assert math.isclose(row["rank_gap"],gap) and math.isclose(row["mc_margin"],margin)
            usable+=row["both_tier2"]
    v=get("VERIFICATION.json")
    assert v["passed"] and sum(revealed["result"]["unweighted_cells"])==revealed["result"]["n_complete"]
    assert get("SCIENTIFIC_VERIFICATION.json")["passed"]
    return {"calls":result["calls"],"strictly_compatible_pairs":usable,"reconciled_tariff_usd":round(total,6),"reference_n":revealed["result"]["n_complete"]}


if __name__=="__main__":print(json.dumps(run(),indent=2))
