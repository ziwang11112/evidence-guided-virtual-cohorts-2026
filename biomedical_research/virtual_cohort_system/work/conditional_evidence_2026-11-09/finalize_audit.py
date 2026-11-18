"""Validate audit artifacts and prepare a finite public summary-only export."""
from pathlib import Path
import ast
import base64
import hashlib
import json

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    a = read(HERE / "SEARCH_ASSOCIATIONS.json")
    j = read(HERE / "SEARCH_JOINT.json")
    r = read(HERE / "SEARCH_ROOT.json")
    review = read(HERE / "INDEPENDENT_EVIDENCE_REVIEW.json")
    state = read(HERE / "STATE.json")
    checks = []
    for entry in a["downloads"]:
        path = Path(entry["saved_path"])
        assert path.stat().st_size == entry["body_bytes"]
        assert digest(path) == entry["sha256"]
        checks.append({"path": str(path.relative_to(HERE)), "sha256": digest(path)})
    for entry in j["saved_originals"]:
        path = HERE / entry["path"]
        assert path.stat().st_size == entry["bytes"]
        assert digest(path) == entry["sha256"]
        checks.append({"path": entry["path"], "sha256": digest(path)})
    for source in review["independently_inspected_sources"]:
        for entry in source["original_artifacts"]:
            assert digest(HERE / entry["path"]) == entry["sha256"]
    count = a["counts"]["conservative_discovery_total"] + j["discovery_requests_used"] + r["successful_web_discovery_queries"]
    original_bytes = a["counts"]["source_download_bytes"] + j["saved_original_transport_bytes"]
    extra_bytes = a["counts"]["known_additional_http_response_bytes"] + j["discarded_direct_response_bytes"]
    assert count == state["successful_discovery_requests"] == 18
    assert count + r["failed_connector_queries"] <= state["discovery_request_ceiling"]
    assert original_bytes == state["saved_original_source_bytes"] == 5838353
    assert extra_bytes == state["additional_metered_http_response_bytes"] == 174990
    assert original_bytes < state["new_saved_source_bytes_ceiling"]
    assert digest(HERE / "FOLLOW_ON_SPEC.md") == state["next_specification_sha256"]
    ast.parse((HERE / "verify_partial_relation.py").read_text(encoding="utf-8"))
    checked_json = []
    for path in HERE.glob("*.json"):
        read(path)
        checked_json.append(path.name)
    audit = {
        "status": "passed",
        "original_download_files_checked": len(checks),
        "source_integrity": checks,
        "independent_review_source_hashes_checked": True,
        "json_parsed": sorted(checked_json),
        "budget_totals_match": True,
        "follow_on_review_hash_matches": True,
        "new_target_access": False,
        "new_generator_execution": False
    }
    (HERE / "AUDIT_CHECK.json").write_text(json.dumps(audit, indent=2)+"\n", encoding="utf-8")
    names = [
        "PLAN.md", "STATE.json", "RESULTS.md", "GREINER_SCALE_AUDIT.md",
        "association_inventory.md", "association_inventory.json",
        "joint_inventory.md", "joint_inventory.json",
        "SEARCH_ROOT.json", "SEARCH_ASSOCIATIONS.json", "SEARCH_JOINT.json",
        "IDENTIFIABILITY.md", "INDEPENDENT_EVIDENCE_REVIEW.md", "INDEPENDENT_EVIDENCE_REVIEW.json",
        "FOLLOW_ON_SPEC.md", "FOLLOW_ON_REVIEW.md",
        "verify_partial_relation.py", "PARTIAL_RELATION_CHECK.json", "AUDIT_CHECK.json"
    ]
    payload = []
    prefix = "biomedical_research/virtual_cohort_system/"
    for name in names:
        path = HERE / name
        assert path.is_file() and path.suffix in {".json", ".md", ".py"}
        body = path.read_bytes()
        payload.append({"path":prefix+"reports/"+HERE.name+"/"+name,
                        "bytes":len(body), "sha256":hashlib.sha256(body).hexdigest(),
                        "git_blob_sha":hashlib.sha1(f"blob {len(body)}\0".encode()+body).hexdigest(),
                        "content_base64":base64.b64encode(body).decode()})
    focus = (PROJECT / "docs/CURRENT_RESEARCH_FOCUS.md").read_text(encoding="utf-8-sig").replace("../work/", "../reports/").encode()
    payload.append({"path":prefix+"docs/CURRENT_RESEARCH_FOCUS.md", "bytes":len(focus),
                    "sha256":hashlib.sha256(focus).hexdigest(),
                    "git_blob_sha":hashlib.sha1(f"blob {len(focus)}\0".encode()+focus).hexdigest(),
                    "content_base64":base64.b64encode(focus).decode()})
    local = HERE / "_local_only"
    local.mkdir(exist_ok=True)
    (local / "public_payload.json").write_text(json.dumps(payload), encoding="utf-8")
    manifest = [{k:v for k,v in e.items() if k!="content_base64"} for e in payload]
    (local / "public_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"audit":audit["status"],"original_files_checked":len(checks),
                      "public_files":len(payload),"public_bytes":sum(x["bytes"] for x in payload)}))

if __name__ == "__main__":
    main()
