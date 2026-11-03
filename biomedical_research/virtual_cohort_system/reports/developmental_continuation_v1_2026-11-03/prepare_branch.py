"""Commit a submitted Agent decision and prepare candidate-specific review; no draw."""
import argparse
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent / "developmental_revision_pilot_v1_2026-11-02/implementation"))
import pilot_controller_v1 as pc
from cohort_harness.__main__ import validate_bundle


def binding(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": pc.sha256(path)}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def main(author, branch):
    assert author in ("A01", "A02") and branch in ("self_review", "source_feedback")
    controller = pc.PilotController.open(WORKSPACE / "evcDC/ledger")
    bundle = WORKSPACE / "evcDC" / author
    relative = "candidates/" + branch
    directory = bundle / relative
    submission = HERE / "branch_submissions" / (author + "_" + branch)
    review = HERE / "candidate_reviews" / (author + "_" + branch)
    if review.exists():
        raise RuntimeError("Review preparation already reserved; inspect before any recovery")
    decision = pc.read_json(submission / "decision.json")
    dispatch = next(item for item in pc.read_json(HERE / "BRANCH_AUTHOR_DISPATCH.json")
                    if item["constructor"] == author and item["branch"] == branch)
    assert dispatch["packet"]["packet_sha256"] == decision["packet_sha256"]
    if decision["action"] == "stop":
        controller.record_branch_decision(author, branch, decision)
        write(review / "STOP.json", {"decision": decision, "dispatch": dispatch})
        print(json.dumps({"constructor": author, "branch": branch, "action": "stop"}))
        return
    # Metadata validation before committing a choice; never executes generator.
    validate_bundle(bundle, directory)
    sys.path.insert(0, str(HERE.parent / "qualified_author_preflight_v1_2026-11-03"))
    import qualified_author_preflight as early
    checked = early.preflight(bundle, branch)
    if checked["findings"]:
        raise RuntimeError(json.dumps(checked["findings"]))
    manifest = {path.name: pc.sha256(path) for path in directory.iterdir() if path.is_file()}
    controller.record_branch_decision(author, branch, decision)
    frozen = pc.lifecycle.freeze_candidate(bundle, relative, parent_receipt=bundle / "candidates/initial/freeze.json",
             revision={"kind": decision["action"], "reason": decision["reason"],
                       "addressed_findings": decision["addressed_findings"], "remaining_limitations": decision["remaining_limitations"]})
    write(review / "SUBMISSION.json", {"constructor": author, "branch": branch, "files": manifest,
          "author_dispatch": dispatch, "decision": decision, "freeze_sha256": pc.sha256(directory / "freeze.json"),
          "root_metadata_preflight": checked})
    runtime = pc.read_json(bundle / "context_bridge_v1/initial/intent.json")["runtime"]
    write(review / "BRIDGE_PREPARATION.json", pc.bridge.prepare(bundle, relative, runtime=runtime))
    write(review / "BINDING_REQUESTS.json", pc.bridge.binding_requests(bundle, relative))
    write(review / "SCIENCE_REQUEST.json", pc.source.science_request(bundle, relative))
    write(review / "SUPPORT_ASSESSMENT.json", pc.support_assessment(bundle, relative, controller.release))
    write(review / "AUTHOR_TRACE.json", {"recorded_utc": datetime.now(timezone.utc).isoformat(), "dispatch": dispatch,
          "decision_file": binding(submission / "decision.json"), "report_file": binding(submission / "AUTHOR_REPORT.md"),
          "submission": binding(review / "SUBMISSION.json"), "fresh_branch_context": True,
          "model_calls": None, "output_tokens": None, "scientific_opportunities": 1,
          "boundary": "Procedural packet allowlist, not OS isolation of author tools"})
    provenance = {"actor_id": dispatch["actor"].split("/")[-1], "context_id": dispatch["actor"],
                  "packet_sha256": decision["packet_sha256"], "author_turns": dispatch["observed_scientific_turns"],
                  "scientific_opportunities": 1, "model_calls": None, "output_tokens": None,
                  "schema_returns": dispatch["schema_returns"], "author_trace": binding(review / "AUTHOR_TRACE.json"),
                  "common_correction": None}
    write(review / "PROVENANCE.json", provenance)
    print(json.dumps({"constructor": author, "branch": branch, "action": decision["action"], "status": "frozen_prepared_for_independent_review", "generator_draws": 0}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("author")
    parser.add_argument("branch")
    args = parser.parse_args()
    main(args.author, args.branch)
