"""Summarize durable receipts, transmitted feedback and final per-item results."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from evidence_replay import core, flow


def verify(root):
    read = flow.author.transport.read
    receipts = []
    payload = read(root/"source_feedback_sent.json")
    trial = read(root/"trial_source_replay.json")
    final = read(root/"final_source_replay.json")
    evidence = read(root/"source_inventory.json")
    if (trial["inventory_sha256"] != core.digest(evidence) or final["inventory_sha256"] != core.digest(evidence)
            or core.review_feedback(trial) != payload):
        raise ValueError("Source replay or inventory binding mismatch")
    review = read(root/"review.json")
    build = read(root/"build.json")
    if trial["candidate_sha256"] != core.digest(build):
        raise ValueError("Initial candidate binding mismatch")
    chosen = review["candidate"] if review["action"] == "revise" else build
    if final["candidate_sha256"] != core.digest(chosen):
        raise ValueError("Final candidate binding mismatch")
    call_root = root/"episodes"/"development"/"calls"
    for folder in sorted(call_root.iterdir()):
        rec = read(folder/"receipt.json")
        for key,name in (("request_sha256","request.json"),("reservation_sha256","reservation.json"),
                         ("response_raw_sha256","response_raw.json")):
            if rec[key] != hashlib.sha256((folder/name).read_bytes()).hexdigest():
                raise ValueError("API capture integrity mismatch")
        receipts.append({k:rec[k] for k in ("call_number","returned_model","status","tariff_cost_usd","request_sha256")})
    body = read(call_root/"0003"/"request.json")
    marker = "Independent calculations on your trial rows using your declared source evidence\n"
    actual, end = json.JSONDecoder().raw_decode(body["input"].rsplit(marker,1)[1])
    if actual != payload:
        raise ValueError("The API review did not receive the saved replay")

    def summary(r):
        return [{"scenario":run["scenario"],"seed":run["seed"],"statuses":run["counts"],
                 "outside_precision":{c["id"]:{"value":c["value"], "difference":c["difference"]}
                                      for c in run["checks"] if c["status"] == "outside_precision"}}
                for run in r["runs"]]
    return {"run":root.name, "source_entries":len(evidence["evidence_checks"]),
            "trial_feedback_in_captured_request":True,"action":review["action"],
            "disposition_reconciliation":final["review_reconciliation"],
            "final_dispositions_complete":final["dispositions_complete"],
            "final_numeric_comparisons_across_tables":final["final_numerically_recomputed"],
            "trial":summary(trial),"final":summary(final),"calls":receipts,
            "total_estimated_usd":sum(r["tariff_cost_usd"] for r in receipts)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run_directory",type=Path)
    p.add_argument("output",type=Path)
    args = p.parse_args()
    flow.execution.record(args.output,verify(args.run_directory))
