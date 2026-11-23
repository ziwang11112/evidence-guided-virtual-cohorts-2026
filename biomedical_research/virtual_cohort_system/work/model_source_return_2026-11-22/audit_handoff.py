"""Offline audit of a model-chosen table return and the exact material sent to authors."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, unquote, urlsplit

HERE = Path(__file__).resolve().parent
SEARCH = HERE.parent / "search_to_model_2026-11-22"
sys.path.insert(0, str(SEARCH))
from verify_model import audit as original_audit, audit_run, bind_design, checked_bundle, core, flow, verify_body
from search_audit import check as verify_search
from table_tools import TableTools, gateway
from read_table import _validate as validate_extraction


def read(path):
    return json.loads(path.read_bytes())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def captured(directory, episode, number, model):
    receipt = read(directory / "receipt.json")
    reservation = read(directory / "reservation.json")
    body = read(directory / "request.json")
    raw = read(directory / "response_raw.json")
    for key, name in (("request_sha256","request.json"),("response_raw_sha256","response_raw.json"),
                      ("reservation_sha256","reservation.json")):
        need(sha((directory / name).read_bytes()) == receipt[key], "Broken API receipt for " + name)
    for record in (receipt,reservation):
        need((record["episode_id"],record["call_number"],record["requested_model"]) == (episode,number,model)
             and record["request_sha256"] == receipt["request_sha256"], "Unbound reservation or response")
    need(receipt["status"] == "received" and raw["status"] == "completed" and
         body["model"] == receipt["returned_model"] == raw["model"] == model and
         receipt["response_id"] == raw["id"] and not body.get("tools"), "Wrong model, tool access or response")
    text = flow.author.client.extract_response("openai",raw)["text"]
    return body, flow.author.decode(text), receipt


def source_catalog(retrieval):
    # Reconstruct the available index from the retained JATS and official manifest,
    # without a live gateway, cache fills, or access to any individual data.
    gateway_dir = retrieval / "gateway"
    state = read(gateway_dir / "state.json")
    docs = read(retrieval / "source_manifest.json")["sources"]
    def artifact(record):
        path = (gateway_dir / record["session_relative_path"]).resolve()
        need(path.parent == (gateway_dir / "approved").resolve(), "Non-approved source artifact")
        data = path.read_bytes()
        need(sha(data) == record["sha256"] and len(data) == record["bytes"], "Source artifact changed")
        return data

    tables = TableTools.__new__(TableTools)
    tables.entries = {}
    for doc in docs:
        pmcid, version = doc["pmcid"], doc["version"]
        parent = state["parents"][pmcid]
        xml = artifact(parent["xml_artifact"])
        manifest = json.loads(artifact(parent["manifest_artifact"]))
        need(sha(xml) == doc["xml_sha256"] and manifest["pmcid"] == pmcid and
             str(manifest["version"]) == str(version) == str(parent["version"]), "Wrong parent or version")
        urls = {}
        for locator in manifest.get("media_urls") or []:
            url = gateway.Session.object_url(None,locator,pmcid,version)
            filename = Path(unquote(urlsplit(url).path)).name
            need(filename not in urls, "Duplicate manifest filename")
            urls[filename] = url
        tables._register(pmcid,version,xml,urls)
    return tables


def reader_proof(directory, number, question, table, media, model):
    body, decoded, rec = captured(directory,"table_reader",number,model)
    need(len(body["input"]) == 1 and body["input"][0]["role"] == "user", "Wrong native reader payload")
    content = body["input"][0]["content"]
    lead = "Return the JSON extraction for this question and table.\n"
    need(len(content) == 2 and content[0]["type"] == "input_text" and content[0]["text"].startswith(lead),
         "Missing reader source and question")
    context = json.loads(content[0]["text"][len(lead):])
    need(context["question"] == question, "Table reader received a different question")
    doc = content[1]
    if table["kind"] == "image":
        need(doc["type"] == "input_image" and doc["detail"] == "high","Expected attached original image")
        header, data = doc["image_url"].split(",",1)
        need(header in ("data:image/jpeg;base64","data:image/png;base64"), "Expected native image encoding")
        raw = base64.b64decode(data,validate=True)
        url = table["url"]
        filename = sha(url.encode()) + Path(urlsplit(url).path).suffix.lower()
        need(raw == (media/filename).read_bytes(), "API image differs from cached file")
        md5 = parse_qs(urlsplit(url).query)["md5"]
        need(len(md5) == 1 and hashlib.md5(raw).hexdigest().lower() == md5[0].lower(),
             "API image differs from published file checksum")
    else:
        need(table["kind"] == "text" and doc["type"] == "input_text" and doc["text"] == table["text"],
             "API text differs from the selected JATS table")
        raw = doc["text"].encode()
        need(raw == (media/(sha(raw)+".txt")).read_bytes(), "Cached table text changed")
    source = dict(table,sha256=sha(raw))
    meta = {k:source[k] for k in ("id","pmcid","label","caption","footnotes","kind","sha256")}
    need(context == {"question":question,"table":meta}, "Different parent, table label, footnotes or bytes")
    extraction = validate_extraction(decoded,source)
    extraction.update(api_request_sha256=rec["request_sha256"],api_response_sha256=rec["response_raw_sha256"],
                      tariff_cost_usd=rec["tariff_cost_usd"])
    need(extraction == read(directory/"extraction.json"), "Reader result differs from captured response")
    return extraction


def verify_model(root, expanded, request, prior, decision, model):
    prior_report = audit_run.verify(root)
    need([x["call_number"] for x in prior_report["calls"]] == [1,2,3],"Wrong number of model calls")
    bound = read(root/"replay_binding.json")
    need(sha(expanded.encode()) == bound["article_text_sha256"] and sha(request.encode()) == bound["request_sha256"]
         and model == bound["model"],"Wrong author binding")
    actual = {}
    stages = []
    for i,(stage,filename) in enumerate((("design","design_as_authored"),("build","build"),("review","review")),1):
        folder = root/"episodes"/"development"/"calls"/f"{i:04d}"
        body, result, receipt = captured(folder,"development",i,model)
        stages.append(dict(verify_body(body,expanded,request,stage),request_sha256=receipt["request_sha256"]))
        need(result == read(root/(filename+".json")), "Submitted response differs for " + stage)
        if stage == "design":
            context = ("\nOriginal candidate\n" + json.dumps(prior,ensure_ascii=False) +
                       "\nAuthor's return decision\n" + json.dumps(decision,ensure_ascii=False))
            need(context in body["input"], "Final design saw a different prior or return decision")
        actual[stage] = result
    normalized, bindings = bind_design(actual["design"])
    need(normalized == read(root/"design.json") and bindings == read(root/"unit_bindings.json")["items"] and
         normalized["evidence"] == read(root/"source_inventory.json"), "Unverified design or inventory")
    review = actual["review"]
    selected = review["candidate"] if review["action"] == "revise" else actual["build"]
    manifest = read(root/"final_manifest.json")
    need(manifest["review_sha256"] == core.digest(review) and manifest["action"] == review["action"], "Review changed")
    need(manifest["seeds"] == bound["final_seeds"] and manifest["n"] == bound["n"], "Run size/seed mismatch")
    if review["action"] == "abstain":
        need(not manifest["runs"], "Abstention returned generated rows")
        return {"stages":stages,"calls":prior_report["calls"], "action":"abstain", "tables":[]}
    need(manifest["candidate_sha256"] == core.digest(selected),"Final candidate changed")
    expected = {(sc,seed) for sc in ["primary",*selected["model_spec"].get("alternatives",[])] for seed in bound["final_seeds"]}
    seen = set()
    tables = []
    for row in manifest["runs"]:
        key = row["scenario"],row["seed"]
        need(key in expected and key not in seen,"Invalid or duplicate delivered table")
        seen.add(key)
        proof = {"scenario":key[0],"seed":key[1],"status":row["status"]}
        if row["status"] == "success":
            path = Path(row["table"]).resolve()
            need(path.is_relative_to((root/"execution_final").resolve()) and path.name == "generated.csv" and
                 sha(path.read_bytes()) == row["sha256"] and row["n"] == bound["n"],"Final table mismatch")
            import csv
            with path.open(encoding="utf8",newline="") as f:
                ids = [record["row_id"] for record in csv.DictReader(f)]
            need(len(ids) == len(set(ids)) == row["n"] and all(ids),"Invalid row count or identifiers")
            proof.update(n=len(ids),sha256=row["sha256"])
        tables.append(proof)
    if manifest["status"] == "success":
        need(seen == expected and all(r["status"] == "success" for r in tables),"Missing final table")
    replay = core.replay(root,"final",normalized["evidence"],selected,manifest)
    saved = read(root/"final_source_replay.json")
    need(all(saved.get(k) == v for k,v in replay.items()),"Final source-check recomputation differs")
    return {"stages":stages,"calls":prior_report["calls"],"action":review["action"],"tables":tables,
            "candidate_sha256":core.digest(selected),"generator_sha256":sha(selected["generator_py"].encode())}

def verify(search_root, newroot, request_path):
    search_root, root = Path(search_root).resolve(), Path(newroot).resolve()
    request = Path(request_path).read_text(encoding="utf8")
    article, ids = checked_bundle(search_root)
    search = verify_search(search_root)
    baseline = original_audit(search_root, request_path)
    selection = read(search_root/"model"/"review.json")
    prior = selection["candidate"] if selection["action"] == "revise" else read(search_root/"model"/"build.json")
    bound = read(root/"binding.json")
    need(ids == bound["source_ids"] == search["selected_pmcids"] and sha(request.encode()) == bound["research_request_sha256"]
         and sha(article.encode()) == bound["baseline_article_sha256"] and
         core.digest(prior) == baseline["candidate_sha256"] == bound["baseline_candidate_sha256"], "Prior binding mismatch")
    for name,value in bound["files"].items():
        need(Path(name).name == name and value == sha((HERE/name).read_bytes()), "Bound implementation differs")
    catalog = source_catalog(search_root/"retrieval")
    index = catalog.index()
    need(index == read(root/"table_index.json"),"Available source index differs from registered aggregate tables")
    model = bound["model"]
    need((bound["read_limit"],bound["decision_limit"]) == (2,3),"Wrong return budget")
    steps = sorted((root/"steps").glob("*.json"))
    need(1 <= len(steps) <= 3,"Wrong number of return actions")
    callroot = root/"decisions"/"episodes"/"return_decision"/"calls"
    need([p.name for p in sorted(callroot.iterdir())] == [f"{i:04d}" for i in range(1,len(steps)+1)],
         "Unaccounted decision call")
    history, receipts, seen, decision = [], [], set(), None
    for number, step_file in enumerate(steps,1):
        need(step_file.name == f"{number:02d}.json","Skipped decision step")
        body, decision, rec = captured(callroot/f"{number:04d}","return_decision",number,model)
        remaining = min(2-len(history),3-number)
        expected = {"format":"Return a JSON action.","research_request":request,"article":article,
                    "prior_candidate":prior,"available_tables":index,"remaining_table_reads":remaining,
                    "actions":["keep","remodel","abstain"]+(["read_table"] if remaining else []),
                    "previous_table_requests_and_results":history}
        need(json.loads(body["input"]) == expected,"Decision received different source text, history or state")
        saved = read(step_file)
        need(decision == saved["decision"] and isinstance(decision.get("reason"),str) and decision["reason"].strip(),
             "Recorded decision differs from raw model output")
        receipts.append({"number":number,"action":decision["action"],"request_sha256":rec["request_sha256"],
                         "response_sha256":rec["response_raw_sha256"],"tariff_cost_usd":rec["tariff_cost_usd"]})
        if number == len(steps):
            need(decision["action"] in ("keep","abstain","remodel") and set(saved) == {"decision"},
                 "No documented terminal decision")
            break
        key, question = decision["id"], decision["question"]
        need(decision["action"] == "read_table" and remaining > 0 and key not in seen and key in catalog.entries and
             catalog.entries[key]["status"] == "available" and isinstance(question,str) and question.strip(), "Invalid table choice")
        folder = root/"reader"/"episodes"/"table_reader"/"calls"/f"{number:04d}"
        extraction = reader_proof(folder,number,question,catalog.entries[key],root/"media",model)
        need(saved == {"decision":decision,"reading":extraction},"Returned transcription differs from captured output")
        history.append(saved)
        seen.add(key)
    readers = root/"reader"/"episodes"/"table_reader"/"calls"
    need((sorted(p.name for p in readers.iterdir()) if readers.exists() else []) ==
         [f"{i:04d}" for i in range(1,len(history)+1)], "Unaccounted reader call")
    returned = [{"question":item["decision"]["question"],"reading":item["reading"]} for item in history]
    expanded = article+"\n\nPublished aggregate table readings requested by the model author (machine transcriptions).\n"+json.dumps(returned,ensure_ascii=False)
    need(expanded.encode() == (root/"augmented_article.txt").read_bytes(),"Returned evidence differs from author handoff")
    readings = [{"id":item["reading"]["id"],"table_sha256":item["reading"]["sha256"],
                 "response_sha256":item["reading"]["api_response_sha256"],"question":item["question"]} for item in returned]
    need(read(root/"handoff.json") == {"base_article_sha256":sha(article.encode()),"augmented_article_sha256":sha(expanded.encode()),
         "baseline_candidate_sha256":core.digest(prior),"decision":decision,"readings":readings}, "Handoff receipt differs")
    report = {"selected_pmcids":ids,"request_sha256":sha(request.encode()),"baseline_candidate_sha256":core.digest(prior),
              "augmented_evidence_sha256":sha(expanded.encode()),"baseline_search_calls":search["search_model_calls"],
              "decisions":receipts,"readings":readings,"terminal_action":decision["action"],
              "table_read_cells":[{"id":r["reading"]["id"],"status":r["reading"]["status"],
                                 "count":len(r["reading"]["cells"])} for r in returned],
              "interpretation":"Hashes verify the supplied pixels or text and the recorded return. Numerical transcription and its scientific interpretation require a separate check against the source."}
    if decision["action"] == "remodel":
        report["author"] = verify_model(root/"model",expanded,request,prior,decision,model)
    else:
        need(not (root/"model").exists(),"Unexpected new construction after terminal keep or abstain")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("search_root",type=Path)
    parser.add_argument("new_root",type=Path)
    parser.add_argument("request",type=Path)
    parser.add_argument("--out",type=Path)
    opt = parser.parse_args()
    report = verify(opt.search_root,opt.new_root,opt.request)
    if opt.out:
        if opt.out.exists():
            need(read(opt.out) == report,"Prior audit output differs")
        else:
            with opt.out.open("x",encoding="utf8") as handle:
                json.dump(report,handle,ensure_ascii=False,indent=2)
                handle.write("\n")
    else:
        print(json.dumps(report,ensure_ascii=False,indent=2))
