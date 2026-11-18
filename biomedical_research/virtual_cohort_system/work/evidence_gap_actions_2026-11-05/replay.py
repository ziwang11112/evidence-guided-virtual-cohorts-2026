"""Replay new action declarations against frozen source-only bundles.

Does not load generated/participant rows, feedback values or target evaluations.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import json
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
sys.path.insert(0, str(PROJECT))
from cohort_harness.evidence_actions_v1 import route_evidence_actions
from cohort_harness.lifecycle import read_json, sha256, safe_relative
from cohort_harness.contracts import require


def main():
    outputs = HERE / "replay"
    if outputs.exists():
        raise RuntimeError("Replay output already exists; preserve the receipt")
    tracked, reports, counts = {}, {}, []

    def read(path):
        tracked[str(path)] = sha256(path)
        return read_json(path)

    for author in ("C01", "C02", "E01", "E02"):
        bundle = WORKSPACE / ("evcRep" + author)
        candidate = bundle / "candidates/initial"
        task, request = read(bundle / "task.json"), read(bundle / "request.json")
        evidence, spec = read(candidate / "evidence.json"), read(candidate / "model_spec.json")
        registry = read(bundle / "registry.json")
        usage = read(bundle / "gateway/session/state.json")["usage"]
        session = PROJECT / "work/core_workflow_replication_2026-11-04/sessions" / author
        commitment = read(session / "inputs.json")
        contract = read(session / "contract.json")
        require(sha256(session / "inputs.json") == contract["inputs_sha256"], "Acquisition commitment changed")
        require(contract["author_id"] == author and Path(contract["bundle"]).resolve() == bundle.resolve(), "Session identity changed")
        freeze = read(candidate / "freeze.json")
        require(freeze["candidate"] == "candidates/initial", "Unexpected candidate receipt")
        for name in ("evidence.json", "model_spec.json"):
            require(sha256(candidate / name) == freeze["commitments"]["candidates/initial/" + name], "Frozen candidate input changed")
        if not commitment.get("acquisition_closed_utc"):
            raise RuntimeError("This development replay requires the original closed acquisition boundary")
        registered = {(r["source_id"], r["path"], r["sha256"]) for r in registry["artifacts"]
                      if r.get("screening") == "approved"}
        for source in evidence["sources"]:
            for artifact in source["artifacts"]:
                relative = artifact["path"]
                path = bundle.joinpath(*safe_relative(relative))
                digest = sha256(path)
                require((source["id"], relative, digest) in registered, "Source artifact is not registered")
                require(digest == artifact["sha256"] == commitment["files"][relative], "Source bytes changed")
                tracked[str(path)] = digest
        for relative in ("task.json", "request.json", "registry.json", "gateway/session/state.json"):
            require(sha256(bundle / relative) == commitment["files"][relative], "Closed input changed")
        manifest = read(HERE / "author" / author / "analysis_evidence.json")
        cards = read(HERE / "author" / author / "action_cards.json")
        report = route_evidence_actions(
            manifest, cards, task, evidence, spec,
            {"retrieval_phase": "closed", "queries_used": usage["queries"], "downloads_used": usage["downloads"]},
            required_analysis_ids=[a["id"] for a in request["intended_analyses"]],
        )
        reports[author] = report
        counts.append({
            "author": author, "required_analyses": len(request["intended_analyses"]),
            "additional_diagnostics": len(report["additional_declared_analysis_ids"]),
            "declared_gaps": sum(len(a["gaps"]) for a in manifest["analyses"]),
            "action_cards": len(report["routes"]),
            "action_types": dict(Counter(r["action_kind"] for r in report["routes"])),
            "dispositions": dict(Counter(r["disposition"] for r in report["routes"])),
            "query_usage": usage["queries"], "download_usage": usage["downloads"],
        })
    for path, digest in tracked.items():
        require(sha256(path) == digest, "Replay changed an input")
    outputs.mkdir()
    for author, report in reports.items():
        (outputs / f"{author}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    result = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Source-only action-policy development replay, not new generation or independent scientific confirmation.",
        "authors": counts, "retrieval_executed": False, "rows_read": False, "candidate_execution": False,
        "scientific_diagnosis_origin": "fresh_context_agents_with_procedural_source_only_instructions_not_OS_isolation",
        "source_bytes_and_registry_bindings_checked": True,
        "input_hashes_unchanged": tracked,
        "implementation_sha256": sha256(PROJECT / "cohort_harness/evidence_actions_v1.py"),
        "replay_script_sha256": sha256(Path(__file__)),
    }
    (outputs / "SUMMARY.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "completed", "authors": counts, "unchanged_input_files": len(tracked)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
