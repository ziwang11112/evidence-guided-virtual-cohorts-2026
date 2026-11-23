"""Verify recorded source handoff, authorship and final table replay. No API calls."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "article_autonomy_design_2026-11-22"))
from evidence_replay import audit_run, core, flow
from evidence_replay.bind_units import bind_design


PMCID = re.compile(r"\bPMC[1-9][0-9]*\b", re.I)
HEADING = re.compile(r"^## \[(PMC[1-9][0-9]*)\](?:\s|$)")


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def text_sha(value):
    return hashlib.sha256(value.encode("utf8")).hexdigest()


def require(condition, failure):
    if not condition:
        raise ValueError(failure)


def checked_bundle(root):
    retrieval = root / "retrieval"
    raw = (retrieval / "selected_sources.txt").read_bytes()
    require((root / "article.txt").read_bytes() == raw, "Selected-source bundle differs from handoff")
    manifest = read(retrieval / "source_manifest.json")
    state = read(retrieval / "retrieval_state.json")
    require(manifest["bundle_sha256"] == hashlib.sha256(raw).hexdigest() and
            manifest["bundle_bytes"] == len(raw), "Selected bundle differs from retrieval receipt")
    require(manifest["config_sha256"] == hashlib.sha256((retrieval / "gateway_config.json").read_bytes()).hexdigest(),
            "Gateway configuration differs from selection record")
    docs = manifest["sources"]
    ids = manifest["ids"]
    require(1 <= len(ids) <= 2 and len(set(ids)) == len(ids) and ids == [d["pmcid"] for d in docs],
            "Selected source list differs from records")
    parts = []
    for doc in docs:
        pmcid = doc["pmcid"]
        require(PMCID.fullmatch(pmcid) and doc["status"] == "ok" and
                state["opens"].get(pmcid) == doc and pmcid in state["hits"],
                "Selected document lacks a matching successful open and search hit")
        part = (retrieval / (pmcid + ".txt")).read_bytes()
        require(hashlib.sha256(part).hexdigest() == doc["text_sha256"] and len(part) == doc["text_bytes"],
                "Returned document differs from select/open source receipts")
        parts.append(part)
    require(b"\n".join(parts) == raw, "Bundle differs from opened texts in selection order")
    text = raw.decode("utf8")
    header_ids = [m.group(1) for line in text.splitlines() if (m := HEADING.match(line))]
    require(header_ids == ids, "Selected PMCID headings differ from verified source manifest")
    return text, ids


def handoff_prefix(article, request):
    return "Research request\n" + request + "\n\nFull article\n" + article + "\n\n"


def verify_body(body, article, request, stage):
    prefix = handoff_prefix(article, request)
    require(isinstance(body.get("input"), str) and body["input"].startswith(prefix),
            f"{stage}: captured request or source text differs from handoff")
    # Checking the next section prevents an appended source from looking like a true match.
    suffix = body["input"][len(prefix):]
    next_section = flow.author.DESIGN if stage == "design" else "Your pre-execution scientific design\n"
    require(suffix.startswith(next_section), f"{stage}: unexpected material in source block")
    require(not body.get("tools"), f"{stage}: unexpected additional information channel")
    return {"stage":stage, "exact_request_and_source_block":True, "model":body["model"]}


def map_citations(items, allowed):
    rows = []
    for item in items:
        locator = item["source"]
        ids = sorted({v.upper() for v in PMCID.findall(locator)})
        unknown = sorted(set(ids) - set(allowed))
        status = "unmapped" if not ids else ("unknown_pmcid" if unknown else "mapped")
        rows.append({"id":item["id"], "source":locator, "provenance":item["provenance"],
                     "applicability":item["applicability"], "citation_status":status,
                     "cited_pmcids":ids, "unknown_pmcids":unknown})
    return rows


def audit(root, request_path):
    root = Path(root).resolve()
    model = root / "model"
    article, allowed = checked_bundle(root)
    request = Path(request_path).read_text(encoding="utf8")
    bound = read(model / "replay_binding.json")
    require(text_sha(article) == bound["article_text_sha256"], "Article text differs from model binding")
    require(text_sha(request) == bound["request_sha256"], "Research request differs from model binding")
    # Reuse the earlier independent verifier for the three receipts and exact review payload.
    receipt_report = audit_run.verify(model)
    receipts = receipt_report["calls"]
    require([r["call_number"] for r in receipts] == [1, 2, 3], "Expected three fresh author calls")
    raw_design = read(model / "design_as_authored.json")
    build, review = [read(model / (name + ".json")) for name in ("build", "review")]
    normalized, bindings = bind_design(raw_design)
    require(normalized == read(model / "design.json"), "Normalized design differs from submitted design")
    unit_log = read(model / "unit_bindings.json")
    require(unit_log["items"] == bindings and unit_log["raw_design_sha256"] == core.digest(raw_design)
            and unit_log["bound_design_sha256"] == core.digest(normalized), "Unit binding records differ")
    stages = []
    for index,(stage,expected) in enumerate((("design",raw_design),("build",build),("review",review)), 1):
        directory = model / "episodes/development/calls" / f"{index:04d}"
        body = read(directory / "request.json")
        stage_proof = verify_body(body, article, request, stage)
        response = read(directory / "response_raw.json")
        output = flow.author.client.extract_response("openai",response)["text"]
        require(flow.author.decode(output) == expected, f"{stage}: authored response differs from saved object")
        require(receipts[index-1]["returned_model"] == stage_proof["model"] == bound["model"],
                f"{stage}: model identity mismatch")
        stages.append(stage_proof)
    evidence = read(model / "source_inventory.json")
    require(evidence == normalized["evidence"], "Working inventory differs from submitted design")
    selected = review["candidate"] if review["action"] == "revise" else build
    manifest = read(model / "final_manifest.json")
    require(manifest["review_sha256"] == core.digest(review) and manifest["action"] == review["action"],
            "Final manifest action or review binding differs")
    require(manifest["n"] == bound["n"] and manifest["seeds"] == bound["final_seeds"],
            "Generation or seed budget differs from protocol")
    started = {(r["scenario"], r["seed"]) for r in manifest["runs"]}
    require(len(started) == len(manifest["runs"]), "Duplicate final scenario and seed")
    if manifest["status"] == "success":
        scenarios = ["primary", *selected["model_spec"].get("alternatives", [])]
        expected_runs = {(s, v) for s in scenarios for v in bound["final_seeds"]}
        require(started == expected_runs, "Missing or unexpected final scenario or seed")
    reread = core.replay(model, "final", evidence, selected, manifest)
    saved = read(model / "final_source_replay.json")
    require(all(saved.get(key) == val for key,val in reread.items()),
            "Independent source replay from actual final rows differs from recorded report")
    table_summaries = []
    for mrow, replay in zip(manifest["runs"], reread["runs"]):
        if mrow["status"] == "success":
            require(mrow["n"] == bound["n"], "Final table row count differs from registered budget")
        table_summaries.append({"scenario":mrow["scenario"], "seed":mrow["seed"], "status":mrow["status"],
                                "n":mrow.get("n"), "sha256":replay.get("table_sha256"),
                                "declared_output_estimates":mrow.get("outputs",{}),
                                "source_replay_counts":replay["counts"]})
    rows = map_citations(core.inventory(evidence), allowed)
    decisions = selected["decision_record"]
    provenance = decisions.get("parameter_provenance", [])
    return {"selected_source_ids_in_bundle":allowed, "article_text_sha256":text_sha(article),
            "request_text_sha256":text_sha(request), "stages":stages, "citations":rows,
            "unmapped_item_ids":[r["id"] for r in rows if r["citation_status"] != "mapped"],
            "assumed_item_ids":[r["id"] for r in rows if r["provenance"] == "assumed"],
            "transport_item_ids":[r["id"] for r in rows if r["applicability"] == "transport_assumption"],
            "unknown_applicability_ids":[r["id"] for r in rows if r["applicability"] == "unknown"],
            "final_action":review["action"], "candidate_sha256":reread["candidate_sha256"],
            "generator_py_sha256":text_sha(selected["generator_py"]),
            "parameter_provenance_entry_count":len(provenance),
            "output_definitions":selected["model_spec"].get("outputs",[]), "tables":table_summaries,
            "model_receipt_audit":receipt_report,
            "interpretation":"Citation links establish declared attribution to delivered document IDs. "
                             "Factual extraction, population applicability and measured-target utility require "
                             "independent scientific evaluation. Output estimates are the author's analysis "
                             "on each generated table; the source replay is separately recomputed."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", type=Path)
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.run_root, args.request)
    if args.output:
        flow.execution.record(args.output, report)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
