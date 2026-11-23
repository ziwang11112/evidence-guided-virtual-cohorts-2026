"""Verify actual model decisions against the saved search actions and handoff."""
import argparse
import json
from pathlib import Path

from run import author, persist, transport


def check(root):
    selection = transport.read(root/"selection.json")
    trace, unique_hits, opened = [], set(), set()
    selected = None
    for number in range(1,selection["actions"]+1):
        folder = root/"episodes"/"search"/"calls"/f"{number:04d}"
        rec = transport.read(folder/"receipt.json")
        for filename,field in (("request.json","request_sha256"),("reservation.json","reservation_sha256"),
                               ("response_raw.json","response_raw_sha256")):
            if transport.sha(folder/filename) != rec[field]:
                raise ValueError("Search call receipt does not match " + filename)
        request = transport.read(folder/"request.json")
        if rec["status"] != "received" or rec["returned_model"] != request["model"]:
            raise ValueError("Unverified search decision")
        action_log = transport.read(root/"actions"/f"{number:04d}.json")
        decision = author.decode(author.client.extract_response("openai",transport.read(folder/"response_raw.json"))["text"])
        if decision != action_log["decision"]:
            raise ValueError("Dispatched action differs from the model response")
        body = json.loads(request["input"])
        if transport.sha_bytes(body["research_request"].encode("utf8")) != transport.read(root/"binding.json")["research_request_sha256"]:
            raise ValueError("Original request changed during retrieval")
        if body["previous_actions"] != [
                transport.read(root/"actions"/f"{n:04d}.json") for n in range(1,number)]:
            raise ValueError("Retrieved evidence differs from that seen by the next model decision")
        observation = action_log["observation"]
        entry = {"number":number,"decision":decision,"status":observation["status"],
                 "model":rec["returned_model"],"tariff_estimate_usd":rec["tariff_cost_usd"]}
        if decision["action"] == "search":
            entry["hit_ids"] = [i["pmcid"] for i in observation.get("hits",[])]
            unique_hits.update(entry["hit_ids"])
        if decision["action"] == "open" and observation["status"] == "ok":
            pmcid = decision["pmcid"]
            if pmcid not in unique_hits or transport.sha_bytes(observation["text"].encode()) != observation["text_sha256"]:
                raise ValueError("Opened text lacks a verified search hit and content")
            opened.add(pmcid)
            entry.update(doi=observation["doi"],source_text_sha256=observation["text_sha256"])
        if observation["status"] == "selected":
            selected = decision["pmcids"]
            if not set(selected) <= opened:
                raise ValueError("Selected item was not opened")
        trace.append(entry)
    if selection.get("pmcids") != selected:
        raise ValueError("Final source decision differs from trace")
    return {"trace":trace,"distinct_hit_count":len(unique_hits),"opened_count":len(opened),
            "selected_pmcids":selected,"search_model_calls":len(trace),
            "search_estimated_usd":sum(item["tariff_estimate_usd"] for item in trace)}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("root",type=Path)
    p.add_argument("output",type=Path)
    args=p.parse_args()
    persist(args.output,check(args.root))
