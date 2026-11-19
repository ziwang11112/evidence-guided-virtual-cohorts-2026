"""Check actual recorded payloads, matched sibling inputs, model settings, cost and chronology."""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import math

HERE=Path(__file__).resolve().parent


def verify_tables(frame, bands, count_matrix, recorded=None):
    """Recalculate the source table quantities without the scientific scoring module."""
    import numpy as np
    h=frame.hb_g_dl
    f=frame.ferritin_ug_l
    a=h.lt(12)
    b=f.lt(15)
    cells=[(a&b).sum(),(a&~b).sum(),(~a&b).sum(),(~a&~b).sum()]
    calculated={f"threshold_cell_fraction_{i+1}": n/len(frame) for i,n in enumerate(cells)}
    src_n=sum(sum(row) for row in count_matrix)
    published={f"threshold_cell_fraction_{i+1}": n/src_n for i,n in enumerate(sum(count_matrix,[]))}
    for i,(values,band) in enumerate(zip(bands, [a,h.ge(12)&h.lt(14),h.ge(14)]),1):
        vals={"fraction":float(band.mean()),"depletion_fraction":float(b[band].mean()),
              "hb_mean":float(h[band].mean()),"hb_sd":float(h[band].std()),
              "ferritin_gm":float(np.exp(np.log(f[band]).mean())),"ferritin_gsd":float(np.exp(np.log(f[band]).std()))}
        for key,value in vals.items():
            label=f"band_{i}_{key}"
            calculated[label]=value
            published[label]=(values["n"]/src_n if key=="fraction" else values["depleted"]/values["n"] if key=="depletion_fraction" else values[key])
    if recorded is None:
        for label, value in calculated.items():
            is_rounded=any(label.endswith(k) for k in ["hb_mean","hb_sd","ferritin_gm","ferritin_gsd"])
            assert np.isclose(round(value,3) if is_rounded else value,published[label],rtol=0,atol=1e-12),label
    else:
        assert set(calculated)=={v["label"] for v in recorded}
        for v in recorded:
            assert np.isclose(v["virtual"],calculated[v["label"]],rtol=0,atol=1e-12),v["label"]
            assert np.isclose(v["observed_A"],published[v["label"]],rtol=0,atol=1e-12),v["label"]
    return len(calculated)


def get(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    from study import request, verify_freeze
    import pandas as pd
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
            written=u.get("cache_write",0) or 0
            assert 0<=cached+written<=u["input"]
            tariff=((u["input"]-cached-written)*cfg["input_rate"]+cached*cfg["cached_rate"]+
                    written*cfg["cache_write_rate"]+u["output"]*cfg["output_rate"])/1e6
            assert math.isclose(tariff,receipt["tariff_cost_usd"],abs_tol=1e-12)
            cost+=tariff
    assert len(limits)==1 and receipt_count==source["api_calls"] and math.isclose(cost,source["known_usd"])
    table=get(HERE/"A_TABLES.json")
    source_frame=pd.read_csv(HERE/"private/A.csv")
    count=verify_tables(source_frame,table["table_2"]["rows"],table["table_1"]["counts"])
    same=0
    feedback_checks=0
    for p in plan["parents"]:
        parent=source["models"][p]
        if parent["usable"]:
            frame=pd.concat([pd.read_csv(HERE/"private/runs"/p/str(seed)/"output/generated.csv") for seed in plan["seeds"]],ignore_index=True)
            feedback_checks+=verify_tables(frame,table["table_2"]["rows"],table["table_1"]["counts"],parent["feedback"])
        if p+"_control" in inputs and p+"_evidence" in inputs:
            assert inputs[p+"_evidence"].replace(base_marker+extra,control_text)==inputs[p+"_control"]
            same+=1
    dest=HERE/"INPUT_AUDIT.json"
    if not dest.exists():
        assert not (HERE/"REFERENCE_OPEN.json").exists()
    audit={"verified_before_target_open":True,"verified_recorded_payloads":receipt_count,"matched_sibling_requests":same,
           "sibling_difference":"Only the supplement paragraph replaces the no-new-statistic paragraph.",
           "identical_model_effort_and_output_cap":True,"ordinary_received_workflow_skill":False,
           "all_costed_receipts_recomputed_usd":cost,"analysis_reference_in_prompt_attachments":False,
           "recomputed_A_table_quantities":count,"recomputed_initial_source_feedback_comparisons":feedback_checks}
    if not dest.exists():
        with dest.open("x",encoding="utf8",newline="\n") as f: json.dump(audit,f,indent=2)
    else:
        assert get(dest)==audit
    print(json.dumps(audit,indent=2))


if __name__=="__main__":
    run()
