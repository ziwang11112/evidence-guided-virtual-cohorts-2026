"""Check actual recorded payloads, matched sibling inputs, model settings, cost and chronology."""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import math

HERE=Path(__file__).resolve().parent


def get(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    from study import request, verify_freeze
    verify_freeze()
    calls=HERE/"private/api/calls"
    source=get(HERE/"SOURCE_CLOSURE.json")
    plan=get(HERE/"FREEZE.json")
    base_marker="Additional evidence available:\n"
    control_text="No additional source statistic is available in this round."
    extra=(HERE/"A_SUPPLEMENT.json").read_text(encoding="utf8")
    skill=(HERE.parents[1]/"skills/evidence-cohort-generation/SKILL.md").read_text(encoding="utf8")
    limits=set(); inputs={}; cost=0.; receipt_count=0
    for folder in sorted(calls.iterdir()):
        receipt=get(folder/"receipt.json")
        payload=get(folder/"request.json")["body"]
        text=payload["input"]
        assert text==(folder/"prompt.txt").read_text(encoding="utf8")
        assert text==request(folder.name)
        assert sha(folder/"request.json")==receipt["request_sha256"] and sha(folder/"prompt.txt")==receipt["prompt_sha256"]
        assert receipt["request_sha256"]==source["models"][folder.name]["receipt"]["request_sha256"]
        assert (skill in text)==folder.name.startswith("workflow")
        assert (base_marker+extra in text)==folder.name.endswith("_evidence")
        assert (control_text in text)==folder.name.endswith("_control")
        assert "tools" not in payload and payload["store"] is False
        assert datetime.fromisoformat(plan["utc"])<datetime.fromisoformat(receipt["started_utc"])
        limits.add((payload["model"],payload["reasoning"]["effort"],payload["max_output_tokens"]))
        inputs[folder.name]=text
        receipt_count+=1
        if receipt["tariff_cost_usd"] is not None:
            u=receipt["usage"]; cfg=receipt["tariff"]; cached=u.get("cached",0) or 0
            tariff=((u["input"]-cached)*cfg["input_rate"]+cached*cfg["cached_rate"]+u["output"]*cfg["output_rate"])/1e6
            assert math.isclose(tariff,receipt["tariff_cost_usd"],abs_tol=1e-12)
            cost+=tariff
    assert len(limits)==1 and receipt_count==source["api_calls"] and math.isclose(cost,source["known_usd"])
    same=0
    for p in plan["parents"]:
        if p+"_control" in inputs and p+"_evidence" in inputs:
            assert inputs[p+"_evidence"].replace(base_marker+extra,control_text)==inputs[p+"_control"]
            same+=1
    dest=HERE/"INPUT_AUDIT.json"
    if not dest.exists():
        assert not (HERE/"REFERENCE_OPEN.json").exists()
    audit={"verified_before_target_open":True,"verified_recorded_payloads":receipt_count,"matched_sibling_requests":same,
           "sibling_difference":"Only the supplement paragraph replaces the no-new-statistic paragraph.",
           "identical_model_effort_and_output_cap":True,"ordinary_received_workflow_skill":False,
           "all_costed_receipts_recomputed_usd":cost,"analysis_reference_in_prompt_attachments":False}
    if not dest.exists():
        with dest.open("x",encoding="utf8",newline="\n") as f: json.dump(audit,f,indent=2)
    else:
        assert get(dest)==audit
    print(json.dumps(audit,indent=2))


if __name__=="__main__":
    run()
