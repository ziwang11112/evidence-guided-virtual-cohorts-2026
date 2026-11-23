"""Verify every assigned author without reading either measured workbook."""
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"search_to_model_2026-11-22"))
from verify_model import checked_bundle, verify_body, require, text_sha, read
from evidence_replay import audit_run, core, flow


def check_slot(root,article,request):
    result=read(root/"slot_result.json")
    out={"slot":root.name,"status":result["status"],"reason":result.get("reason"),"calls":[],"tables":[]}
    binding=read(root/"replay_binding.json")
    require(binding["article_text_sha256"]==text_sha(article) and binding["request_sha256"]==text_sha(request),
            "Author binding differs from selected paper or original request")
    stages=("design","build","review")
    for folder in sorted((root/"episodes/development/calls").glob("*")):
        index=int(folder.name)
        rec=read(folder/"receipt.json")
        body=read(folder/"request.json")
        stage=stages[index-1]
        proof=verify_body(body,article,request,stage)
        require(rec["requested_model"]==binding["model"]==proof["model"],"Incorrect model")
        require(body.get("store") is False and "previous_response_id" not in body and
                "conversation" not in body,"Unexpected provider conversation state")
        for file,key in (("reservation.json","reservation_sha256"),("request.json","request_sha256"),
                         ("response_raw.json","response_raw_sha256")):
            if key=="response_raw_sha256" and not rec.get(key):
                require(rec["status"]!="received","Received response missing hash")
                continue
            require(flow.author.transport.sha(folder/file)==rec[key],"Invalid receipt digest for "+file)
        out["calls"].append({k:rec.get(k) for k in
            ("call_number","requested_model","returned_model","response_id","request_sha256","response_raw_sha256",
             "status","completion_status","tariff_cost_usd","usage")})
        artifact=root/{"design":"design_as_authored.json","build":"build.json","review":"review.json"}[stage]
        if rec["status"]=="received":
            require(rec["returned_model"]==binding["model"],"Returned model mismatch")
            if artifact.is_file():
                submitted=flow.author.client.extract_response("openai",read(folder/"response_raw.json"))["text"]
                require(flow.author.decode(submitted)==read(artifact),f"Saved {stage} differs from paid output")
    out["charged_tariff_usd"]=sum(c["tariff_cost_usd"] or 0. for c in out["calls"])
    out["responses_without_usage"]=sum(c["usage"] is None for c in out["calls"])
    if not (root/"final_source_replay.json").exists():
        require(result["status"]=="failed","Published success lacks completed source replay")
        out["interpretation"]="Construction stopped before a delivered and verified final model."
        return out
    full=audit_run.verify(root)
    require(len(out["calls"])==3 and all(c["status"]=="received" for c in out["calls"]),
            "Complete result lacks distinct design/build/review calls")
    review=read(root/"review.json")
    candidate=review["candidate"] if review["action"]=="revise" else read(root/"build.json")
    inventory=read(root/"source_inventory.json")
    require(inventory==read(root/"design.json")["evidence"],"Final source inventory changed")
    manifest=read(root/"final_manifest.json")
    require(manifest["action"]==review["action"] and manifest["review_sha256"]==core.digest(review),
            "Final action differs from saved review")
    if review["action"]!="abstain":
        require(manifest["candidate_sha256"]==core.digest(candidate),"Final candidate digest mismatch")
    else:
        require(not manifest["runs"],"Abstention contains delivered tables")
    out.update(final_action=review["action"],model_columns=candidate["model_spec"].get("columns"),
               alternatives=candidate["model_spec"].get("alternatives",[]),
               model_structure=candidate["decision_record"].get("structure"),
               author_limitations=candidate["decision_record"].get("limitations",[]),
               model_outputs=candidate["model_spec"].get("outputs",[]),
               source_items=len(core.inventory(inventory)),
               trial_feedback_in_captured_review=full["trial_feedback_in_captured_request"],
               dispositions_complete=full["final_dispositions_complete"],scientific_review_reason=review["reason"],
               generator_sha256=text_sha(candidate["generator_py"]),candidate_sha256=core.digest(candidate))
    replay=core.replay(root,"final",inventory,candidate,manifest)
    saved=read(root/"final_source_replay.json")
    require(all(saved.get(k)==v for k,v in replay.items()),"Independent final table/source checks differ")
    for entry,proof in zip(manifest["runs"],replay["runs"]):
        out["tables"].append({"scenario":entry["scenario"],"seed":entry["seed"],"n":entry.get("n"),
                              "status":entry["status"],"sha256":proof.get("table_sha256"),
                              "counts":proof.get("counts",{})})
    if result["status"]=="success":
        require(all(t["status"]=="success" and t["n"]==binding["n"] for t in out["tables"]),
                "Successful slot has incomplete tables")
        expect=set((s,seed) for s in ["primary",*out["alternatives"]] for seed in binding["final_seeds"])
        require(len(out["tables"])==len(expect) and {(t["scenario"],t["seed"]) for t in out["tables"]}==expect,
                "Successful slot has missing or repeated preregistered tables")
    return out


def audit():
    article,ids=checked_bundle(HERE/"private/search")
    request=(HERE/"REQUEST.txt").read_text(encoding="utf8")
    report={"selected_study":ids,"article_sha256":text_sha(article),"request_sha256":text_sha(request),
            "assigned_slots":6,"authors":[]}
    for i in range(1,7):
        report["authors"].append(check_slot(HERE/"private/authors"/f"a{i:02d}",article,request))
    calls=[c for a in report["authors"] for c in a["calls"]]
    ids=[c["response_id"] for c in calls if c["status"]=="received"]
    require(all(ids) and len(set(ids))==len(ids),"Duplicated or missing model response IDs")
    report.update(completed_calls=len(ids),distinct_model_response_ids=len(set(ids)),
                  author_total_tariff_usd=sum(a["charged_tariff_usd"] for a in report["authors"]),
                  total_delivered_tables=sum(t["status"]=="success" for a in report["authors"] for t in a["tables"]),
                  interpretation="Captured evidence, model authorship, generated-only feedback and final output "
                                 "integrity. Scientific source extraction and external endpoint validity require separate checks.")
    return report


if __name__=="__main__":
    report=audit()
    path=HERE/"AUTHOR_AUDIT.json"
    if path.exists():
        require(read(path)==report,"Published author audit differs")
    else:
        with path.open("x",encoding="utf8") as f:
            json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False)
            f.write("\n")
    print({k:report[k] for k in ("completed_calls","author_total_tariff_usd","total_delivered_tables")})
