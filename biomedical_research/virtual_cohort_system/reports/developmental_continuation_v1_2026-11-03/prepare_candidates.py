"""Freeze metadata-only retained candidates and prepare unsigned review requests."""
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
PRIOR = HERE.parent / "developmental_revision_pilot_v1_2026-11-02"
sys.dont_write_bytecode = True
sys.path.insert(0, str(PRIOR / "implementation"))
import pilot_controller_v1 as pc


def binding(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": pc.sha256(path)}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def main():
    release = pc.read_json(HERE / "RELEASE_DRAFT.json")
    lineage = {"kind": "explicit_cross_release_scientific_reuse", "old_release": binding(PRIOR / "RELEASE.json"),
               "old_closure": binding(PRIOR / "ADMISSION_CLOSURE.json"), "fresh_initial_model_calls": 0,
               "fresh_initial_scientific_opportunities": 0, "automatic_repair_actor": "root",
               "mechanical_preparation_agent": "qualified_author_preflight", "authors": {}}
    for author in ("A01", "A02"):
        bundle = WORKSPACE / "evcDC" / author
        old = WORKSPACE / "evcDP" / author
        for path in (HERE / "author_inputs/input").iterdir():
            shutil.copyfile(path, bundle / "input" / path.name)
        for name in ("task.json", "registry.json"):
            assert pc.sha256(bundle / name) == pc.sha256(HERE / "author_inputs" / name)
        parent = pc.lifecycle.freeze_candidate(bundle, "candidates/reused_parent")
        child = pc.lifecycle.freeze_candidate(bundle, "candidates/initial", parent_receipt=bundle / "candidates/reused_parent/freeze.json",
                  revision={"kind": "retain", "reason": "Reuse the existing Agent scientific law; correct only native alias metadata in a separately authorized continuation.",
                            "addressed_findings": ["J measurement input alias now matches its retained unit evidence"],
                            "remaining_limitations": ["All original scientific, source and target-transfer assumptions remain; no source/target data have run"]})
        reviewdir = HERE / "candidate_reviews" / author
        runtime = pc.read_json(old / "context_bridge_v1/initial_interface/intent.json")["runtime"]
        write(reviewdir / "BRIDGE_PREPARATION.json", pc.bridge.prepare(bundle, "candidates/initial", runtime=runtime))
        write(reviewdir / "BINDING_REQUESTS.json", pc.bridge.binding_requests(bundle, "candidates/initial"))
        write(reviewdir / "SCIENCE_REQUEST.json", pc.source.science_request(bundle, "candidates/initial"))
        write(reviewdir / "SUPPORT_ASSESSMENT.json", pc.support_assessment(bundle, "candidates/initial", release))
        original_review = PRIOR / f"candidate_reviews/{author}_initial_interface"
        provenance = pc.read_json(original_review / "PROVENANCE.json")
        record = {"old_original_freeze": binding(old / "candidates/initial/freeze.json"),
                  "old_interface_freeze": binding(old / "candidates/initial_interface/freeze.json"),
                  "new_reused_freeze": binding(bundle / "candidates/reused_parent/freeze.json"),
                  "new_initial_freeze": binding(bundle / "candidates/initial/freeze.json"),
                  "delta": binding(HERE / f"staging/{author}_DELTA.json"),
                  "old_author_trace": binding(original_review / "AUTHOR_TRACE.json"),
                  "old_provenance": binding(original_review / "PROVENANCE.json")}
        lineage["authors"][author] = record
        trace = {"kind": "historical_authoring_with_automatic_metadata_reuse", "recorded_utc": datetime.now(timezone.utc).isoformat(),
                 "lineage": record, "actual_original_author_packet": binding(PRIOR / "INITIAL_PACKET.json"),
                 "current_admission_packet": binding(HERE / "INITIAL_PACKET.json"),
                 "current_packet_delivered_to_original_author": False,
                 "historical_actor": provenance["actor_id"], "historical_context": provenance["context_id"],
                 "historical_author_turns": provenance["author_turns"],
                 "historical_scientific_opportunities": provenance["scientific_opportunities"],
                 "historical_schema_returns": provenance["schema_returns"],
                 "fresh_initial_model_calls": 0, "fresh_initial_author_turns": 0, "fresh_initial_scientific_opportunities": 0,
                 "automatic_repair_actor": "root", "mechanical_preparation_agent": "qualified_author_preflight",
                 "new_alias_repair_count": 1, "new_scientific_changes": 0,
                 "repair_script": binding(HERE / "staging/stage_metadata_only.py"),
                 "scope": "Controller counters are historical carried-forward values, not fresh calls or replenished old correction allowance."}
        write(reviewdir / "AUTHOR_TRACE.json", trace)
        provenance.update(packet_sha256=pc.sha256(HERE / "INITIAL_PACKET.json"), author_trace=binding(reviewdir / "AUTHOR_TRACE.json"),
                          common_correction={"rejected_candidate": "candidates/reused_parent", "reason": "Historical scientific reuse followed by one declared automatic native-alias repair; old budgets and failures remain closed."})
        write(reviewdir / "PROVENANCE.json", provenance)
    write(HERE / "LINEAGE.json", lineage)
    print(json.dumps({"status": "frozen_prepared_unsigned", "reused_constructions": 2, "source_attempts": 0, "target_attempts": 0}))


if __name__ == "__main__":
    main()
