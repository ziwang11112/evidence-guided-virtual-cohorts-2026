"""Close this release without execution; preserve every planned slot and input."""
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "implementation"))
import pilot_controller_v1 as pilot


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def main():
    release = pilot.read_json(HERE / "RELEASE.json")
    controller = pilot.PilotController.open(release["ledger_directory"])
    before = controller.verify()
    if any(before["state"]["versions"].values()):
        raise RuntimeError("Expected wholly unregistered versions; do not repeat closure")
    results = {}
    for author in ("A01", "A02"):
        bundle = Path(release["ledger_directory"]).parent / author
        original = pilot.lifecycle.verify_candidate(bundle, "candidates/initial")
        corrected = pilot.lifecycle.verify_candidate(bundle, "candidates/initial_interface")
        for name in pilot.BASELINE_FILES - {"qualified_plan_v1.json"}:
            if pilot.sha256(bundle / "candidates/initial" / name) != pilot.sha256(bundle / "candidates/initial_interface" / name):
                raise RuntimeError("Scientific file unexpectedly changed: " + name)
        # Original bridge was only prepared, never sealed. A full bridge verify
        # correctly refuses that state; inspect absence of executions instead.
        for directory in (bundle / "context_bridge_v1").rglob("executions"):
            if any(directory.iterdir()):
                raise RuntimeError("Unexpected bridge executions")
        report = pilot.bridge.verify(bundle, "candidates/initial_interface")
        if report["attempts_consumed"] != 0:
            raise RuntimeError("Unexpected source attempts")
        requests = pilot.read_json(HERE / f"candidate_reviews/{author}_initial_interface/QUALIFIED_REQUESTS.json")
        # Use the actual prior A02 review to reproduce its failure. No approval
        # is fabricated for A01; its independent failure record remains intact.
        if author == "A02":
            reviews = pilot.read_json(HERE / "candidate_reviews/A02_initial_interface/QUALIFIED_REVIEWS.json")
            checks = {}
            for context in ("J", "B", "M"):
                child = bundle / "context_bridge_v1/initial_interface/contexts" / context / "bundle"
                try:
                    pilot.source.qualified._prepare(child, "context", requests[context]["declaration"], reviews[context])
                    checks[context] = {"status": "pass"}
                except Exception as error:
                    checks[context] = {"status": "fail", "type": type(error).__name__, "message": str(error)}
            if checks["J"].get("message") != "Unit evidence must identify the two HbA1c representations" or any(checks[c]["status"] != "pass" for c in ("B", "M")):
                raise RuntimeError("Unexpected metadata result")
            results["actual_A02_metadata_validation"] = checks
        results[author] = {"original_freeze_sha256": pilot.sha256(bundle / "candidates/initial/freeze.json"),
                           "corrected_freeze_sha256": pilot.sha256(bundle / "candidates/initial_interface/freeze.json"),
                           "original_and_corrected_verified": True, "scientific_bytes_unchanged": True,
                           "source_attempts": 0}
    # Supersession is an explicit veto, not a modified approval.
    supersession = HERE / "candidate_reviews/A02_initial_interface/QUALIFIED_REVIEW_SUPERSESSION.json"
    results["supersession_sha256"] = pilot.sha256(supersession)
    reason = ("Pre-execution metadata admission failure: J native HbA1c alias does not satisfy unit-evidence names. "
              "Two schema returns and the common initial correction were already consumed. "
              "No further correction, replacement constructor, source draw or target draw is admitted in this release. "
              "This is an interface failure, not an observed biomedical outcome.")
    for author in ("A01", "A02"):
        controller.abort_version(author, "initial", reason)
    controller.freeze_scientific_inventory()
    closed = controller.close_targets()
    verified = controller.verify()
    counts = Counter((slot["role"], slot["status"]) for slot in verified["slots"])
    if counts != Counter({("source", "aborted"): 54, ("target", "aborted"): 18}):
        raise RuntimeError("Unexpected final slot dispositions")
    if verified["state"]["authorization"] is not None:
        raise RuntimeError("Reference evaluation must remain unauthorized")
    write_new(HERE / "CLOSED_INVENTORY.json", closed)
    results.update({"schema_version": 1, "closed_utc": datetime.now(timezone.utc).isoformat(),
                    "status": "closed_admission_failure", "release_sha256": controller.release_sha256,
                    "inventory_sha256": closed["inventory_sha256"],
                    "planned_source_slots": 54, "planned_target_slots": 18,
                    "aborted_unrun_slots": 72, "source_draws": 0, "target_draws": 0,
                    "new_scientific_rows": 0, "reference_evaluation_authorized": False,
                    "new_quality_comparison_available": False})
    write_new(HERE / "ADMISSION_CLOSURE.json", results)
    print(json.dumps({key: results[key] for key in ("status", "aborted_unrun_slots", "source_draws", "target_draws", "new_quality_comparison_available")}))


if __name__ == "__main__":
    main()
